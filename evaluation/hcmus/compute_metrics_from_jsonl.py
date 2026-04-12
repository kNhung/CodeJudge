import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from scipy import stats
except Exception:  # pragma: no cover
    stats = None


PARSE_FAIL_TEXT = "llm response could not be parsed"
LIST_FALLBACK_TEXT = "llm returned list format. converted to additive rubric score via fallback mapping from errors."


def _safe_corr(method: str, x: List[float], y: List[float]) -> float:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return float("nan")

    if stats is None:
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


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def _is_error_record(
    record: Dict[str, Any],
    parse_fail_text: str = PARSE_FAIL_TEXT,
    list_fallback_text: str = LIST_FALLBACK_TEXT,
) -> Tuple[bool, str]:
    result = record.get("result", {})
    reasoning = ""
    if isinstance(result, dict):
        reasoning = str(result.get("reasoning", "") or "").strip().lower()

    score = _to_float(record.get("predicted_score_10"))
    if score is not None and score < 0:
        return True, "negative_score"
    if parse_fail_text in reasoning:
        return True, "parse_fail"
    if list_fallback_text in reasoning:
        return True, "list_fallback"
    return False, ""


def compute_metrics_from_jsonl(
    jsonl_path: Path,
    mode: str = "taxonomy",
    pass_threshold: float = 5.0,
    exclude_error_records: bool = False,
) -> Dict[str, Any]:
    """Compute metrics from HCMUS-style JSONL output.

    Args:
        jsonl_path: Path to the JSONL file.
        mode: Output mode label for metrics.
        pass_threshold: Threshold on 10-point score to infer pass/fail when missing.
        exclude_error_records: If True, exclude records that are parse-fail,
            list-fallback, or predicted_score_10 < 0 from metric calculations.

    Returns:
        Metrics dictionary.
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"JSONL not found: {jsonl_path}")

    total = 0
    invalid_cnt = 0
    processed_ids = set()
    correct_cnt = 0

    pass_refs: List[float] = []
    pass_preds: List[float] = []
    grade_pairs: List[Tuple[float, float]] = []

    excluded_cnt = 0
    excluded_by_reason = {"negative_score": 0, "parse_fail": 0, "list_fallback": 0}

    with jsonl_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total += 1
            try:
                record = json.loads(line)
            except Exception:
                invalid_cnt += 1
                continue

            row_id = record.get("id")
            if row_id is not None:
                processed_ids.add(str(row_id))

            is_error, reason = _is_error_record(record)
            if exclude_error_records and is_error:
                excluded_cnt += 1
                excluded_by_reason[reason] += 1
                continue

            expected = bool(record.get("expected_pass", False))
            predicted_pass_raw = record.get("predicted_pass", None)
            predicted_score = _to_float(record.get("predicted_score_10"))

            if isinstance(predicted_pass_raw, bool):
                predicted_pass = predicted_pass_raw
            elif predicted_score is not None:
                predicted_pass = predicted_score >= pass_threshold
            else:
                predicted_pass = False

            if predicted_score is not None:
                correct_cnt += int(predicted_pass == expected)
                pass_refs.append(1.0 if expected else 0.0)
                pass_preds.append(1.0 if predicted_pass else 0.0)

                expected_score_10 = _to_float(record.get("expect_grade"))
                if expected_score_10 is not None:
                    grade_pairs.append((predicted_score, expected_score_10))

    metrics: Dict[str, Any] = {
        "mode": mode,
        "samples": total,
        "output_file": str(jsonl_path),
        "invalid_cnt": invalid_cnt,
        "total_cnt": total,
        "processed_unique_ids": len(processed_ids),
        "rate_limit_hit": False,
        "exclude_error_records": exclude_error_records,
        "excluded_cnt": excluded_cnt,
        "excluded_by_reason": excluded_by_reason,
    }

    valid_cnt = len(pass_refs)
    metrics["valid_metric_records"] = valid_cnt
    metrics["correct_cnt"] = correct_cnt
    if valid_cnt > 0:
        metrics["accuracy"] = correct_cnt / valid_cnt
        metrics["kendalltau"] = round(_safe_corr("kendalltau", pass_refs, pass_preds), 3)
        metrics["spearmanr"] = round(_safe_corr("spearmanr", pass_refs, pass_preds), 3)

    if grade_pairs:
        preds = [p for p, _ in grade_pairs]
        exps = [e for _, e in grade_pairs]
        mae = sum(abs(p - e) for p, e in grade_pairs) / len(grade_pairs)
        metrics["mae_on_10"] = round(mae, 3)
        metrics["rmse_on_10"] = round(_rmse(preds, exps), 3)
        metrics["pearson_grade"] = round(_safe_corr("pearsonr", preds, exps), 3)

    if stats is None:
        metrics["warning"] = "scipy is unavailable, correlation metrics may be NaN"

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute metrics from HCMUS JSONL output")
    parser.add_argument("--jsonl", type=Path, required=True, help="Path to output JSONL file")
    parser.add_argument("--mode", type=str, default="taxonomy")
    parser.add_argument("--pass-threshold", type=float, default=5.0)
    parser.add_argument(
        "--exclude-error-records",
        action="store_true",
        help="Exclude parse-fail/list-fallback/negative-score records from metric calculations",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional output JSON path to save metrics",
    )
    args = parser.parse_args()

    metrics = compute_metrics_from_jsonl(
        jsonl_path=args.jsonl,
        mode=args.mode,
        pass_threshold=args.pass_threshold,
        exclude_error_records=args.exclude_error_records,
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))

    if args.save is not None:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
