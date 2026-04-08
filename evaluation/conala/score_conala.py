import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import BinaryAssessor, IntegratedAssessor, LLMFactory, TaxonomyAssessor  # noqa: E402

CONALA_ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = CONALA_ROOT / "conala-aggregated-grades.json"
CANDIDATE_FIELDS = ["baseline", "tranx-annot", "best-tranx", "best-tranx-rerank", "codex", "snippet"]


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
    if not isinstance(data, list):
        raise ValueError("Conala dataset JSON must be a list of examples.")
    return data


def normalize_code(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(line).rstrip() for line in value)
    return str(value).strip()


def to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def get_grade_reference(example: Dict[str, Any], source: str) -> Optional[Any]:
    grade_field = f"grade-{source}"
    if grade_field in example:
        return example[grade_field]
    grade_data = example.get("grade")
    if isinstance(grade_data, dict):
        return grade_data.get(source)
    return None


def _safe_corr(method: str, x: List[float], y: List[float]) -> float:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return float("nan")
    if method == "kendalltau":
        return float(stats.kendalltau(x, y).statistic)
    if method == "spearmanr":
        return float(stats.spearmanr(x, y).statistic)
    if method == "pearsonr":
        return float(stats.pearsonr(x, y).statistic)
    raise ValueError(f"Unknown correlation method: {method}")


def _rmse(x: List[float], y: List[float]) -> float:
    if not x or not y or len(x) != len(y):
        return float("nan")
    mse = sum((a - b) ** 2 for a, b in zip(x, y)) / len(x)
    return math.sqrt(mse)


def compute_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grade_refs: List[float] = []
    predicted_scores: List[float] = []
    for item in records:
        grade_reference = to_float(item.get("grade_reference"))
        result = item.get("result")
        predicted_score = None
        if isinstance(result, dict):
            predicted_score = to_float(result.get("summary", {}).get("score_on_4"))
            if predicted_score is None:
                predicted_score = to_float(result.get("summary", {}).get("score"))
        if grade_reference is not None and predicted_score is not None:
            grade_refs.append(grade_reference)
            predicted_scores.append(predicted_score)

    if not grade_refs:
        return {}

    grade_scale = 4.0
    predicted_scaled = [p / 10.0 * grade_scale for p in predicted_scores]

    n = len(grade_refs)
    mae = sum(abs(g - p) for g, p in zip(grade_refs, predicted_scaled)) / n
    rmse = _rmse(grade_refs, predicted_scaled)
    exact_match = sum(int(round(g) == round(p)) for g, p in zip(grade_refs, predicted_scaled)) / n

    return {
        "samples": n,
        "grade_scale": grade_scale,
        "average_true_grade": round(sum(grade_refs) / n, 4),
        "average_predicted_scaled": round(sum(predicted_scaled) / n, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "pearson": round(_safe_corr("pearsonr", grade_refs, predicted_scaled), 4),
        "spearman": round(_safe_corr("spearmanr", grade_refs, predicted_scaled), 4),
        "kendalltau": round(_safe_corr("kendalltau", grade_refs, predicted_scaled), 4),
        "exact_match_rate": round(exact_match, 4),
    }


def evaluate_example(
    example: Dict[str, Any],
    assessor: Optional[BinaryAssessor | TaxonomyAssessor | IntegratedAssessor],
    source: str,
    dry_run: bool,
    language: str,
    mode: str,
) -> Dict[str, Any]:
    intent = example.get("intent", "").strip()
    student_code = normalize_code(example.get(source))
    grade_reference = get_grade_reference(example, source)

    item: Dict[str, Any] = {
        "example_index": example.get("id") or example.get("index") or None,
        "source": source,
        "intent": intent,
        "code_preview": student_code[:200],
        "language": language,
        "grade_reference": grade_reference,
    }

    if dry_run:
        item["status"] = "dry_run"
        item["problem_preview"] = intent[:200]
        return item

    assert assessor is not None
    if mode == "binary":
        result = assessor.assess(
            problem_statement=intent,
            student_code=student_code,
            language=language,
        )
        # Normalize binary result to match integrated format
        result = {
            "assessment_type": "binary",
            "binary": {
                "result": result["result"],
                "passed": result["passed"],
                "confidence": result.get("confidence", 0.9),
                "analysis": result.get("analysis", ""),
                "analysis_preview": result.get("analysis", "")[:200] + "...",
            },
            "taxonomy": {
                "final_score": 10.0 if result["passed"] else 0.0,
                "errors_count": 0,
                "error_breakdown": {},
                "quality_score": 0,
                "errors": [],
                "reasoning": "Binary mode: no taxonomy"
            },
            "summary": {
                "status": "PASS" if result["passed"] else "FAIL",
                "score": 10.0 if result["passed"] else 0.0,
                "grade_letter": "A" if result["passed"] else "F",
                "recommendation": "Binary assessment only"
            }
        }
    elif mode == "taxonomy":
        result = assessor.assess(
            problem_statement=intent,
            student_code=student_code,
            reference_code=None,
            language=language,
        )
        # Normalize taxonomy result to match integrated format
        result = {
            "assessment_type": "taxonomy",
            "binary": {
                "result": "Yes" if result["final_score"] >= 5.0 else "No",
                "passed": result["final_score"] >= 5.0,
                "confidence": 0.9,
                "analysis": "Taxonomy mode: no binary analysis",
                "analysis_preview": "Taxonomy mode: no binary analysis",
            },
            "taxonomy": {
                "final_score": result["final_score"],
                "errors_count": len(result.get("errors", [])),
                "error_breakdown": {},
                "quality_score": result.get("quality_score", 0),
                "errors": result.get("errors", []),
                "reasoning": result.get("reasoning", "")
            },
            "summary": {
                "status": "PASS" if result["final_score"] >= 5.0 else "FAIL",
                "score": result["final_score"],
                "score_on_4": round(result["final_score"] / 10.0 * 4.0, 4),
                "grade_letter": "A" if result["final_score"] >= 9.0 else "B" if result["final_score"] >= 8.0 else "C" if result["final_score"] >= 7.0 else "D" if result["final_score"] >= 6.0 else "F",
                "recommendation": "Taxonomy assessment only"
            }
        }
    else:  # integrated
        result = assessor.assess(
            problem_statement=intent,
            student_code=student_code,
            reference_code=None,
            language=language,
        )
        if isinstance(result, dict):
            result_summary = result.get("summary", {})
            if result_summary.get("score") is not None:
                result_summary["score_on_4"] = round(float(result_summary["score"]) / 10.0 * 4.0, 4)
                result["summary"] = result_summary
    item["result"] = result
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Conala examples using CodeJudge IntegratedAssessor")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON, help="Path to Conala JSON dataset")
    parser.add_argument(
        "--source",
        type=str,
        default="codex",
        choices=CANDIDATE_FIELDS + ["all"],
        help="Which code field to evaluate (default: codex)",
    )
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "anthropic", "local", "gemini"], help="LLM provider")
    parser.add_argument("--model", type=str, default="gpt-4", help="Model name")
    parser.add_argument("--output", type=Path, default=None, help="Output JSONL file path")
    parser.add_argument("--limit", type=int, default=0, help="Only process first N examples (0 means all)")
    parser.add_argument("--start", type=int, default=0, help="Start index in example list")
    parser.add_argument("--run-both-assessments", action="store_true", help="Always run both binary and taxonomy assessments")
    parser.add_argument("--dry-run", action="store_true", help="Do not call LLM; only validate dataset and emit metadata")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL for local provider")
    parser.add_argument("--language", type=str, default="Python", help="Programming language for Conala examples")
    parser.add_argument(
        "--mode",
        type=str,
        default="integrated",
        choices=["binary", "taxonomy", "integrated"],
        help="Assessment mode (default: integrated)",
    )
    parser.add_argument("--metrics-output", type=Path, default=None, help="Metrics JSON output path")
    args = parser.parse_args()

    if args.start < 0:
        raise ValueError("--start must be >= 0")

    sources = CANDIDATE_FIELDS if args.source == "all" else [args.source]
    examples = load_examples(args.json)
    examples = examples[args.start :]
    if args.limit > 0:
        examples = examples[: args.limit]

    assessor: Optional[BinaryAssessor | TaxonomyAssessor | IntegratedAssessor] = None
    if not args.dry_run:
        kwargs = {}
        if args.provider == "local" and args.base_url:
            kwargs["base_url"] = args.base_url
        llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, **kwargs)
        if args.mode == "binary":
            assessor = BinaryAssessor(llm_client=llm_client)
        elif args.mode == "taxonomy":
            assessor = TaxonomyAssessor(llm_client=llm_client)
        else:  # integrated
            assessor = IntegratedAssessor(llm_client=llm_client, run_both_assessments=args.run_both_assessments)

    if args.output is None:
        args.output = build_default_output_path(args.model, args.source)
    if args.metrics_output is None:
        args.metrics_output = args.output.parent / f"{args.output.stem}_metrics.json"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    records: List[Dict[str, Any]] = []
    with args.output.open("w", encoding="utf-8") as f:
        for idx, example in enumerate(examples, start=args.start):
            for source in sources:
                if source not in example:
                    continue
                item = evaluate_example(
                    example=example,
                    assessor=assessor,
                    source=source,
                    dry_run=args.dry_run,
                    language=args.language,
                    mode=args.mode,
                )
                item["example_index"] = idx
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                records.append(item)
                written += 1

    print(f"Done. wrote {written} rows to {args.output}")

    if not args.dry_run:
        metrics: Dict[str, Any] = {}
        all_sources = sorted(set(item["source"] for item in records))
        for source in all_sources:
            source_records = [item for item in records if item["source"] == source]
            metrics[source] = compute_metrics(source_records)
        metrics["all"] = compute_metrics(records)

        with args.metrics_output.open("w", encoding="utf-8") as mf:
            json.dump(metrics, mf, ensure_ascii=False, indent=2)

        print(f"Saved metrics to {args.metrics_output}")
        print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
