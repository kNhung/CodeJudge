"""Compare runtime/token/quality metrics between two CoNaLa multi-agent JSONL runs."""
import argparse
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

from scipy import stats


def to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_items(path: Path) -> List[Dict[str, Any]]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for result_item in rec.get("results", []):
                items.append(result_item)
    return items


def summarize(path: Path) -> Dict[str, Any]:
    items = load_items(path)
    runtimes = [float(i["runtime_seconds"]) for i in items if i.get("runtime_seconds") is not None]
    tokens = []
    grade_refs = []
    preds = []
    errors = 0

    for item in items:
        usage = item.get("usage") or (item.get("result") or {}).get("usage") or {}
        total = usage.get("total_tokens")
        if total is not None:
            tokens.append(float(total))

        result = item.get("result") or {}
        scoring = result.get("scoring") or {}
        if scoring.get("has_error"):
            errors += 1

        grade_ref = to_float(item.get("grade_reference"))
        pred = to_float((result.get("summary") or {}).get("score_on_4"))
        if pred is None:
            final_10 = to_float(scoring.get("final_score_on_10"))
            if final_10 is not None and final_10 >= 0:
                pred = final_10 / 10.0 * 4.0
        if grade_ref is not None and pred is not None and pred >= 0:
            grade_refs.append(grade_ref)
            preds.append(pred)

    summary: Dict[str, Any] = {
        "path": str(path),
        "n": len(items),
        "errors": errors,
        "avg_runtime_s": round(statistics.mean(runtimes), 3) if runtimes else None,
        "median_runtime_s": round(statistics.median(runtimes), 3) if runtimes else None,
        "total_runtime_s": round(sum(runtimes), 2) if runtimes else None,
        "avg_tokens": round(statistics.mean(tokens), 1) if tokens else None,
        "total_tokens": int(sum(tokens)) if tokens else None,
    }
    if grade_refs:
        n = len(grade_refs)
        mae = sum(abs(g - p) for g, p in zip(grade_refs, preds)) / n
        summary["metric_samples"] = n
        summary["mae"] = round(mae, 4)
        if n >= 2:
            spearman, _ = stats.spearmanr(grade_refs, preds)
            summary["spearman"] = round(float(spearman), 4) if spearman == spearman else None
    return summary


def print_summary(label: str, summary: Dict[str, Any]) -> None:
    print(f"\n=== {label} ===")
    for key in (
        "path", "n", "errors", "avg_runtime_s", "median_runtime_s", "total_runtime_s",
        "avg_tokens", "total_tokens", "metric_samples", "mae", "spearman",
    ):
        if key in summary and summary[key] is not None:
            print(f"  {key}: {summary[key]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare A/B CoNaLa multi-agent runs")
    parser.add_argument("baseline", type=Path, help="Baseline JSONL (batch factors)")
    parser.add_argument("parallel", type=Path, help="Parallel JSONL")
    args = parser.parse_args()

    baseline = summarize(args.baseline)
    parallel = summarize(args.parallel)
    print_summary("BASELINE (1 call / all factors)", baseline)
    print_summary("PARALLEL (1 call / factor)", parallel)

    if baseline.get("avg_runtime_s") and parallel.get("avg_runtime_s"):
        delta = parallel["avg_runtime_s"] - baseline["avg_runtime_s"]
        pct = delta / baseline["avg_runtime_s"] * 100
        print(f"\nRuntime delta (parallel - baseline): {delta:+.3f}s/sample ({pct:+.1f}%)")
    if baseline.get("avg_tokens") and parallel.get("avg_tokens"):
        delta_t = parallel["avg_tokens"] - baseline["avg_tokens"]
        pct_t = delta_t / baseline["avg_tokens"] * 100
        print(f"Token delta (parallel - baseline): {delta_t:+.1f}/sample ({pct_t:+.1f}%)")
    if baseline.get("mae") is not None and parallel.get("mae") is not None:
        print(f"MAE delta (parallel - baseline): {parallel['mae'] - baseline['mae']:+.4f}")
    if baseline.get("spearman") is not None and parallel.get("spearman") is not None:
        print(f"Spearman delta (parallel - baseline): {parallel['spearman'] - baseline['spearman']:+.4f}")


if __name__ == "__main__":
    main()
