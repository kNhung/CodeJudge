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
# Ép dùng đường dẫn tuyệt đối cho dataset trên Kaggle
DEFAULT_JSON = Path("/kaggle/working/CodeJudge/evaluation/conala/conala-aggregated-grades.json")
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
    item = {"source": source, "intent": intent, "grade_reference": grade_reference}
    if dry_run: return item
    result = assessor.assess(problem_statement=intent, student_code=student_code, reference_code=None, language=language)
    # Normalize kết quả taxonomy
    if mode == "taxonomy":
        result = {
            "taxonomy": result,
            "summary": {"score": result.get("final_score", 0), "score_on_4": round(result.get("final_score", 0) / 10 * 4, 4)}
        }
    item["result"] = result
    return item

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--source", type=str, default="codex")
    parser.add_argument("--provider", type=str, default="local")
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--mode", type=str, default="taxonomy")
    args = parser.parse_args()

    sources = CANDIDATE_FIELDS if args.source == "all" else [args.source]
    examples = load_examples(args.json)[args.start:]
    if args.limit > 0: examples = examples[:args.limit]

    # Khởi tạo assessor
    llm_client = LLMFactory.create(provider=args.provider, model_name=args.model)
    assessor = TaxonomyAssessor(llm_client=llm_client)

    output_path = build_default_output_path(args.model, args.source)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Bắt đầu chấm điểm {len(examples)} mẫu trên nhánh stage04...")
    start_total = time.time() # Lưu thời gian bắt đầu
    records = []

    # Thêm thanh tiến trình tqdm ở đây
    with output_path.open("w", encoding="utf-8") as f:
        for idx, example in enumerate(tqdm(examples, desc="Đang chấm điểm", unit="mẫu"), start=args.start):
            for source in sources:
                if source not in example: continue
                item = evaluate_example(example, assessor, source, False, "Python", args.mode)
                item["example_index"] = idx
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                records.append(item)

    end_total = time.time()
    duration = end_total - start_total
    print(f"\n✅ Hoàn thành! Đã lưu {len(records)} hàng vào {output_path}")
    print(f"⏱️ Tổng thời gian chạy: {duration:.2f} giây ({duration/60:.2f} phút)")
    if len(records) > 0:
        print(f"📊 Trung bình: {duration/len(records):.2f} giây/mẫu")

if __name__ == "__main__":
    main()