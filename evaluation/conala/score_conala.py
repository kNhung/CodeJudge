import argparse
import json
import math
import sys
import time # Thêm thư viện thời gian
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from tqdm import tqdm # Thêm thanh tiến trình
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import BinaryAssessor, IntegratedAssessor, LLMFactory, TaxonomyAssessor

CONALA_ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = CONALA_ROOT / "conala.json"
CANDIDATE_FIELDS = ["baseline", "tranx-annot", "best-tranx", "best-tranx-rerank", "codex", "snippet"]

# ... (Các hàm build_default_output_path, load_examples, normalize_code giữ nguyên)
def build_default_output_path(model_name: str, source: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    safe_source = source.replace("/", "-")
    return CONALA_ROOT / "output" / f"{ts}_{safe_model}_{safe_source}.jsonl"

def load_examples(json_path: Path) -> List[Dict[str, Any]]:
    if not json_path.is_file():
        raise FileNotFoundError(f"Missing dataset JSON file: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def normalize_code(value: Any) -> str:
    if value is None: return ""
    if isinstance(value, list): return "\n".join(str(line).rstrip() for line in value)
    return str(value).strip()

def to_float(value: Any) -> Optional[float]:
    try: return float(value)
    except: return None

def get_grade_reference(example: Dict[str, Any], source: str) -> Optional[Any]:
    grade_field = f"grade-{source}"
    if grade_field in example: return example[grade_field]
    grade_data = example.get("grade")
    if isinstance(grade_data, dict): return grade_data.get(source)
    return None

def compute_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grade_refs, predicted_scores = [], []
    for item in records:
        grade_reference = to_float(item.get("grade_reference"))
        result = item.get("result")
        predicted_score = None
        if isinstance(result, dict):
            predicted_score = to_float(result.get("summary", {}).get("score_on_4"))
            if predicted_score is None: predicted_score = to_float(result.get("summary", {}).get("score"))
        if grade_reference is not None and predicted_score is not None:
            grade_refs.append(grade_reference)
            predicted_scores.append(predicted_score)
    if not grade_refs: return {}
    grade_scale = 4.0
    predicted_scaled = [p / 10.0 * grade_scale for p in predicted_scores]
    n = len(grade_refs)
    mae = sum(abs(g - p) for g, p in zip(grade_refs, predicted_scaled)) / n
    return {"samples": n, "mae": round(mae, 4)}

def evaluate_example(example: Dict[str, Any], assessor, source: str, dry_run: bool, language: str, mode: str) -> Dict[str, Any]:
    intent = example.get("intent", "").strip()
    student_code = normalize_code(example.get(source))
    grade_reference = get_grade_reference(example, source)
    item = {"source": source, "grade_reference": grade_reference}
    if dry_run: return item
    result = assessor.assess(problem_statement=intent, student_code=student_code, reference_code=None, language=language)
    
    # Normalize kết quả tùy theo mode
    if mode == "integrated":
        # IntegratedAssessor format
        final_score = result.get("summary", {}).get("score", 
                                 result.get("taxonomy", {}).get("final_score", 0))
        result = {
            "assessment_type": "integrated",
            "binary": result.get("binary", {}),
            "taxonomy": result.get("taxonomy", {}),
            "summary": {"score": final_score, "score_on_4": round(final_score / 10 * 4, 4)}
        }
    else:  # mode == "taxonomy"
        # TaxonomyAssessor format (legacy)
        result = {
            "assessment_type": "taxonomy",
            "taxonomy": result,
            "summary": {"score": result.get("final_score", 0), "score_on_4": round(result.get("final_score", 0) / 10 * 4, 4)}
        }
    item["result"] = result
    return item

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON,
                        help="Path to the CoNaLa dataset JSON file (default: evaluation/conala/conala.json)")
    parser.add_argument("--source", type=str, default="codex",
                        help="Which source field to evaluate (default: codex). Use 'all' to score all candidate fields.")
    parser.add_argument("--provider", type=str, default="local",
                        help="LLM provider name")
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct",
                        help="Model name to score with")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output JSONL file. If omitted, auto-generate one under evaluation/conala/output")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only process first N examples")
    parser.add_argument("--start", type=int, default=0,
                        help="Start index in dataset examples")
    parser.add_argument("--mode", type=str, default="integrated", 
                        choices=["integrated", "taxonomy"],
                        help="integrated: Binary + Taxonomy (recommended), taxonomy: detailed legacy output")
    parser.add_argument("--use-examples", action="store_true", default=False,
                        help="Use calibration examples (few-shot) when scoring")
    parser.add_argument("--num-examples", type=int, default=2,
                        help="Number of calibration examples per prompt (recommended ≤ 3)")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Validate dataset and CLI without calling the LLM")
    args = parser.parse_args()

    sources = CANDIDATE_FIELDS if args.source == "all" else [args.source]
    examples = load_examples(args.json)[args.start:]
    if args.limit > 0:
        examples = examples[: args.limit]

    if args.output is None:
        output_path = build_default_output_path(args.model, args.source)
    else:
        output_path = args.output

    # Khởi tạo assessor
    assessor = None
    llm_client = None
    if not args.dry_run:
        llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, use_cache=True)
    
    if args.dry_run:
        print("📋 Dry run mode: no LLM calls will be made")
    elif args.mode == "integrated":
        print("📋 Mode: INTEGRATED (Binary + Taxonomy)")
        assessor = IntegratedAssessor(llm_client=llm_client, run_both_assessments=True)
    else:
        print("📋 Mode: TAXONOMY (Chi tiết)")
        assessor = TaxonomyAssessor(
            llm_client=llm_client,
            use_examples=args.use_examples,
            num_examples=args.num_examples
        )
    
    if args.use_examples:
        print(f"📚 Sử dụng calibration examples ({args.num_examples} examples/prompt)")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Bắt đầu chấm điểm {len(examples)} mẫu từ {args.json}...")
    print(f"📤 Kết quả sẽ được lưu vào: {output_path}")
    start_total = time.time() # Lưu thời gian bắt đầu
    records = []

    # Thêm thanh tiến trình tqdm ở đây
    with output_path.open("w", encoding="utf-8") as f:
        for idx, example in enumerate(tqdm(examples, desc="Đang chấm điểm", unit="mẫu"), start=args.start):
            example_record = {
                "example_index": idx,
                "intent": example.get("intent", "").strip(),
                "results": []
            }
            for source in sources:
                if source not in example:
                    continue
                item = evaluate_example(example, assessor, source, False, "Python", args.mode)
                example_record["results"].append(item)
            if not example_record["results"]:
                continue
            f.write(json.dumps(example_record, ensure_ascii=False) + "\n")
            records.append(example_record)

    end_total = time.time()
    duration = end_total - start_total
    print(f"\n✅ Hoàn thành! Đã lưu {len(records)} mẫu vào {output_path}")
    print(f"⏱️ Tổng thời gian chạy: {duration:.2f} giây ({duration/60:.2f} phút)")
    if len(records) > 0:
        print(f"📊 Trung bình: {duration/len(records):.2f} giây/mẫu")

if __name__ == "__main__":
    main()