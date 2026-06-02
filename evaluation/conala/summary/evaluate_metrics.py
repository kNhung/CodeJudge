import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


def to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_true_grade(grade_ref: Any) -> Optional[float]:
    if isinstance(grade_ref, dict):
        values = [to_float(v) for v in grade_ref.values()]
        values = [v for v in values if v is not None]
        return sum(values) / len(values) if values else None
    return to_float(grade_ref)


def get_predicted_score(result: Any) -> Optional[float]:
    if not isinstance(result, dict):
        return None
    summary = result.get("summary", {})
    if isinstance(summary, dict):
        score_on_4 = to_float(summary.get("score_on_4"))
        if score_on_4 is not None:
            return score_on_4
        score_10 = to_float(summary.get("score"))
        if score_10 is not None:
            return min(max(score_10 / 10.0 * 4.0, 0.0), 4.0)
    return None


def extract_records_from_line(data: Dict[str, Any]) -> List[Dict[str, float]]:
    records: List[Dict[str, float]] = []
    if isinstance(data.get("results"), list):
        sample_trues: List[float] = []
        sample_preds: List[float] = []
        for item in data["results"]:
            true_grade = get_true_grade(item.get("grade_reference"))
            pred_grade = get_predicted_score(item.get("result"))
            if true_grade is not None and pred_grade is not None:
                sample_trues.append(true_grade)
                sample_preds.append(pred_grade)
        if sample_trues and sample_preds:
            records.append({
                "source": "avg",
                "true": float(np.mean(sample_trues)),
                "pred": float(np.mean(sample_preds)),
            })
        return records

    true_grade = get_true_grade(data.get("grade_reference"))
    pred_grade = get_predicted_score(data.get("result"))
    if true_grade is not None and pred_grade is not None:
        records.append({"source": "avg", "true": true_grade, "pred": pred_grade})
    return records


def calculate_metrics(group_records: List[Dict[str, float]]) -> Dict[str, Any]:
    if not group_records:
        return {}

    y_true = np.array([r["true"] for r in group_records], dtype=float)
    y_pred = np.array([r["pred"] for r in group_records], dtype=float)

    n = len(y_true)
    avg_true = float(np.mean(y_true))
    avg_pred = float(np.mean(y_pred))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    exact_matches = int(np.sum(np.round(y_true, 2) == np.round(y_pred, 2)))
    exact_match_rate = float(exact_matches) / n

    if n > 1 and np.var(y_true) > 0 and np.var(y_pred) > 0:
        pearson_val = pearsonr(y_true, y_pred)[0]
        spearman_val = spearmanr(y_true, y_pred)[0]
        kendall_val = kendalltau(y_true, y_pred)[0]
    else:
        pearson_val = float("nan")
        spearman_val = float("nan")
        kendall_val = float("nan")

    return {
        "samples": n,
        "grade_scale": 4.0,
        "average_true_grade": round(avg_true, 4),
        "average_predicted_scaled": round(avg_pred, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "pearson": round(pearson_val, 4) if not np.isnan(pearson_val) else float("nan"),
        "spearman": round(spearman_val, 4) if not np.isnan(spearman_val) else float("nan"),
        "kendalltau": round(kendall_val, 4) if not np.isnan(kendall_val) else float("nan"),
        "exact_match_rate": round(exact_match_rate, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate CoNaLa scoring output JSONL against grade references by averaging per sample."
    )
    parser.add_argument("input", type=Path, help="Path to the JSONL file to evaluate")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("metrics_result.json"),
        help="Path to write the aggregated metrics JSON",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    records: List[Dict[str, float]] = []
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            records.extend(extract_records_from_line(data))

    if not records:
        raise ValueError("No valid records found in input file.")

    final_output: Dict[str, Any] = {"all": calculate_metrics(records)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out_f:
        json.dump(final_output, out_f, indent=2, ensure_ascii=False)

    print(f"Đã ghi kết quả metrics ra: {args.output}")
    print(json.dumps(final_output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
