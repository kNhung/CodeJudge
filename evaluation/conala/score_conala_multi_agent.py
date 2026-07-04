import argparse
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from tqdm import tqdm
from scipy import stats
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import MultiAgentAssessor, LLMFactory

CONALA_ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = CONALA_ROOT / "conala.json"
CANDIDATE_FIELDS = ["baseline", "tranx-annot", "best-tranx", "best-tranx-rerank", "codex"]

def build_default_output_path(model_name: str, source: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    safe_source = source.replace("/", "-")
    return CONALA_ROOT / "output" / f"{ts}_{safe_model}_{safe_source}_multi_agent.jsonl"

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
        for result_item in item.get("results", []):
            grade_reference = to_float(result_item.get("grade_reference"))
            result = result_item.get("result")
            predicted_score = None
            if isinstance(result, dict):
                # We extract the score_on_4 from the summary
                predicted_score = to_float(result.get("summary", {}).get("score_on_4"))
                if predicted_score is None:
                    predicted_score = to_float(result.get("scoring", {}).get("final_score_on_10"))
                    if predicted_score is not None:
                        predicted_score = predicted_score / 10.0 * 4.0 # Scale to 4
            
            if grade_reference is not None and predicted_score is not None:
                grade_refs.append(grade_reference)
                predicted_scores.append(predicted_score)
                
    if not grade_refs: return {}
    n = len(grade_refs)
    mae = sum(abs(g - p) for g, p in zip(grade_refs, predicted_scores)) / n
    
    # Calculate Pearson and Spearman correlation if enough samples
    pearson_corr = None
    spearman_corr = None
    if n >= 2:
        try:
            pearson_corr, _ = stats.pearsonr(grade_refs, predicted_scores)
            spearman_corr, _ = stats.spearmanr(grade_refs, predicted_scores)
        except Exception:
            pass
            
    res = {"samples": n, "mae": round(mae, 4)}
    if pearson_corr is not None:
        res["pearson"] = round(pearson_corr, 4)
    if spearman_corr is not None:
        res["spearman"] = round(spearman_corr, 4)
    return res

def evaluate_example(
    example: Dict[str, Any],
    assessor: Optional[MultiAgentAssessor],
    source: str,
    dry_run: bool,
    language: str = "Python",
    provider: str = "",
    model: str = "",
    pre_extracted_factors: Optional[List[str]] = None,
    factor_weights: Optional[Dict[str, float]] = None,
    syntax_penalties: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    intent = example.get("intent", "").strip()
    student_code = normalize_code(example.get(source))
    grade_reference = get_grade_reference(example, source)
    
    item = {
        "source": source, 
        "grade_reference": grade_reference,
        "provider": provider,
        "model": model
    }
    if dry_run:
        item["result"] = {
            "assessment_type": "multi_agent_mock",
            "summary": {"score": 8.0, "score_on_4": 3.2}
        }
        item["runtime_seconds"] = 0.0
        return item

    # Run assessment
    assert assessor is not None
    started_at = time.perf_counter()
    result = assessor.assess(
        question_text=intent,
        student_code=student_code,
        language=language,
        question_max=None, # We will get score on 10 by default
        pre_extracted_factors=pre_extracted_factors,
        factor_weights=factor_weights,
        syntax_penalties=syntax_penalties
    )
    item["runtime_seconds"] = round(time.perf_counter() - started_at, 6)
    
    # Map score to summary key for compute_metrics compatibility
    final_score = result.get("scoring", {}).get("final_score_on_10", 0.0)
    result["summary"] = {
        "score": final_score,
        "score_on_4": round(final_score / 10.0 * 4.0, 4)
    }
    
    item["result"] = result
    if "usage" in result:
        item["usage"] = result["usage"]
    return item

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CoNaLa dataset using Multi-Agent Assessor")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON,
                        help="Path to the CoNaLa dataset JSON file (default: evaluation/conala/conala.json)")
    parser.add_argument("--source", type=str, default="all",
                        help="Which source field to evaluate (default: all). Use 'all' to score all candidate fields.")
    parser.add_argument("--provider", type=str, default="openai",
                        help="LLM provider name")
    parser.add_argument("--model", type=str, default="gpt-4o-mini",
                        help="Model name to score with")
    parser.add_argument("--api-key", type=str, default=None,
                        help="API key for cloud providers")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output JSONL file. If omitted, auto-generate one under evaluation/conala/output")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only process first N examples")
    parser.add_argument("--start", type=int, default=0,
                        help="Start index in dataset examples")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Validate dataset and CLI without calling the LLM")
    parser.add_argument("--config", type=Path, default=None,
                        help="Path to JSON configuration file containing pre-extracted factors and weights")
    args = parser.parse_args()

    sources = CANDIDATE_FIELDS if args.source == "all" else [args.source]
    examples = load_examples(args.json)[args.start:]
    if args.limit > 0:
        examples = examples[: args.limit]

    if args.output is None:
        output_path = build_default_output_path(args.model, args.source)
    else:
        output_path = args.output

    # Load custom config if provided
    config_data = {}
    if args.config:
        if args.config.is_file():
            with args.config.open("r", encoding="utf-8") as config_f:
                config_data = json.load(config_f)
            print(f"📖 Loaded custom HITL config from: {args.config}")
        else:
            print(f"⚠️ Warning: Config file {args.config} not found.")

    # Initialize assessor
    assessor = None
    if not args.dry_run:
        llm_client = LLMFactory.create(
            provider=args.provider, 
            model_name=args.model, 
            use_cache=True,
            api_key=args.api_key
        )
        assessor = MultiAgentAssessor(llm_client=llm_client)
    
    if args.dry_run:
        print("📋 Dry run mode: no LLM calls will be made")
    else:
        print(f"📋 Mode: MULTI-AGENT (Provider: {args.provider}, Model: {args.model})")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Bắt đầu chấm điểm {len(examples)} mẫu từ {args.json}...")
    print(f"📤 Kết quả sẽ được lưu vào: {output_path}")
    start_total = time.time()
    records = []

    mode = "a" if args.start > 0 and output_path.exists() else "w"
    if mode == "a":
        print(f"🔄 Đang ghi tiếp (append) vào tệp kết quả: {output_path}")
    with output_path.open(mode, encoding="utf-8") as f:
        for idx, example in enumerate(tqdm(examples, desc="Đang chấm điểm", unit="mẫu"), start=args.start):
            example_record = {
                "example_index": idx,
                "intent": example.get("intent", "").strip(),
                "provider": args.provider,
                "model": args.model,
                "results": []
            }
            
            # Fetch config override for this example index if any
            example_config = config_data.get(str(idx), {})
            pre_factors = example_config.get("pre_extracted_factors")
            f_weights = example_config.get("factor_weights")
            s_penalties = example_config.get("syntax_penalties")
            
            for source in sources:
                if source not in example:
                    continue
                item = evaluate_example(
                    example=example,
                    assessor=assessor,
                    source=source,
                    dry_run=args.dry_run,
                    language="Python",
                    provider=args.provider,
                    model=args.model,
                    pre_extracted_factors=pre_factors,
                    factor_weights=f_weights,
                    syntax_penalties=s_penalties
                )
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
        
    # Compute metrics
    metrics = compute_metrics(records)
    if metrics:
        print(f"📊 Kết quả đánh giá CoNaLa:")
        print(f"  - Số mẫu đánh giá (grade_reference và predicted_score đầy đủ): {metrics.get('samples')}")
        print(f"  - MAE (Mean Absolute Error) trên thang điểm 4: {metrics.get('mae')}")
        if "pearson" in metrics:
            print(f"  - Pearson Correlation: {metrics.get('pearson')}")
        if "spearman" in metrics:
            print(f"  - Spearman Correlation: {metrics.get('spearman')}")

if __name__ == "__main__":
    main()
