"""
CoNaLa metrics: tính Spearman / Kendall theo từng example_index,
rồi lấy trung bình cộng các hệ số r (per-sample mean correlation).

Khác với calculate_metric.py (flatten toàn bộ điểm rồi tính 1 lần).
"""

import glob
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


def extract_predicted_score_on_4(res_item: Dict[str, Any]) -> Optional[float]:
    """Lấy điểm dự đoán thang 4 từ một phần tử trong results[]."""
    res_detail = res_item.get("result", {})
    if not isinstance(res_detail, dict):
        return None

    summary = res_detail.get("summary", {})
    if isinstance(summary, dict) and summary.get("score_on_4") is not None:
        return float(summary["score_on_4"])

    scoring = res_detail.get("scoring", {})
    if isinstance(scoring, dict) and scoring.get("final_score_on_10") is not None:
        return float(scoring["final_score_on_10"]) / 10.0 * 4.0

    return None


def is_error_result(res_item: Dict[str, Any], predicted: Optional[float]) -> bool:
    if predicted is None:
        return True
    if predicted == -1.0:
        return True
    res_detail = res_item.get("result", {})
    if isinstance(res_detail, dict):
        scoring = res_detail.get("scoring", {})
        if isinstance(scoring, dict) and scoring.get("has_error"):
            return True
    return False


def load_examples_from_jsonl(file_path: str) -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
    return examples


def collect_pairs_for_example(record: Dict[str, Any]) -> Tuple[List[float], List[float], int]:
    """Trả về (actuals, predicteds, skipped_count) cho một example_index."""
    actuals: List[float] = []
    predicteds: List[float] = []
    skipped = 0

    for res_item in record.get("results", []):
        grade_ref = res_item.get("grade_reference")
        if grade_ref is None:
            skipped += 1
            continue
        try:
            actual = float(grade_ref)
        except (TypeError, ValueError):
            skipped += 1
            continue

        try:
            predicted = extract_predicted_score_on_4(res_item)
        except (TypeError, ValueError):
            skipped += 1
            continue

        if is_error_result(res_item, predicted):
            skipped += 1
            continue

        actuals.append(actual)
        predicteds.append(float(predicted))

    return actuals, predicteds, skipped


def can_compute_correlation(actuals: List[float], predicteds: List[float]) -> bool:
    if len(actuals) < 2 or len(predicteds) < 2:
        return False
    if len(set(actuals)) <= 1 or len(set(predicteds)) <= 1:
        return False
    return True


def safe_correlation(
    actuals: List[float],
    predicteds: List[float],
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Tính Pearson, Spearman, Kendall cho một example. Trả về None nếu không tính được."""
    if not can_compute_correlation(actuals, predicteds):
        return None, None, None
    try:
        pearson_r, _ = pearsonr(actuals, predicteds)
        spearman_r, _ = spearmanr(actuals, predicteds)
        kendall_r, _ = kendalltau(actuals, predicteds)
        if np.isnan(pearson_r) or np.isnan(spearman_r) or np.isnan(kendall_r):
            return None, None, None
        return float(pearson_r), float(spearman_r), float(kendall_r)
    except Exception:
        return None, None, None


def mean_or_none(values: List[float]) -> Optional[float]:
    return float(np.mean(values)) if values else None


def compute_per_example_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    pearson_per_example: List[float] = []
    spearman_per_example: List[float] = []
    kendall_per_example: List[float] = []
    mae_per_example: List[float] = []

    skipped_examples = 0
    skipped_pairs = 0
    total_examples = len(records)

    # Flatten lists để so sánh với cách cũ
    flat_actuals: List[float] = []
    flat_predicteds: List[float] = []

    for record in records:
        actuals, predicteds, skipped = collect_pairs_for_example(record)
        skipped_pairs += skipped
        flat_actuals.extend(actuals)
        flat_predicteds.extend(predicteds)

        if not actuals:
            skipped_examples += 1
            continue

        mae_per_example.append(float(np.mean(np.abs(np.array(predicteds) - np.array(actuals)))))

        pearson_r, spearman_r, kendall_r = safe_correlation(actuals, predicteds)
        if pearson_r is None:
            skipped_examples += 1
            continue

        pearson_per_example.append(pearson_r)
        spearman_per_example.append(spearman_r)
        kendall_per_example.append(kendall_r)

    # Global flatten (cách calculate_metric.py)
    global_pearson = global_spearman = global_kendall = None
    if can_compute_correlation(flat_actuals, flat_predicteds):
        global_pearson, global_spearman, global_kendall = safe_correlation(flat_actuals, flat_predicteds)

    global_mae = None
    if flat_actuals:
        global_mae = float(np.mean(np.abs(np.array(flat_predicteds) - np.array(flat_actuals))))

    return {
        "total_examples": total_examples,
        "examples_used_for_correlation": len(spearman_per_example),
        "examples_skipped_for_correlation": skipped_examples,
        "total_pairs": len(flat_actuals),
        "pairs_skipped": skipped_pairs,
        "mae_per_example_mean": mean_or_none(mae_per_example),
        "pearson_per_example_mean": mean_or_none(pearson_per_example),
        "spearman_per_example_mean": mean_or_none(spearman_per_example),
        "kendall_per_example_mean": mean_or_none(kendall_per_example),
        "global_mae_flatten": global_mae,
        "global_pearson_flatten": global_pearson,
        "global_spearman_flatten": global_spearman,
        "global_kendall_flatten": global_kendall,
    }


def print_report(file_path: str, metrics: Dict[str, Any]) -> None:
    print(f"\nFile: {file_path}")
    print("=" * 58)
    print("METRICS THEO TUNG MAU (mean of per-example r)")
    print("=" * 58)
    print(f"- Tong so example_index          : {metrics['total_examples']}")
    print(f"- Example dung tinh correlation  : {metrics['examples_used_for_correlation']}")
    print(f"- Example bo qua (khong du diem) : {metrics['examples_skipped_for_correlation']}")
    print(f"- Tong cap (actual, predicted)   : {metrics['total_pairs']}")
    print(f"- Cap bo qua                     : {metrics['pairs_skipped']}")
    print()
    print("--- Per-example mean ---")
    if metrics["spearman_per_example_mean"] is not None:
        print(f"- Spearman R (mean per example)  : {metrics['spearman_per_example_mean']:.4f}")
        print(f"- Kendall Tau (mean per example) : {metrics['kendall_per_example_mean']:.4f}")
        print(f"- Pearson R (mean per example)   : {metrics['pearson_per_example_mean']:.4f}")
    else:
        print("- Khong tinh duoc correlation per-example (khong du mau hop le).")
    if metrics["mae_per_example_mean"] is not None:
        print(f"- MAE (mean per example)         : {metrics['mae_per_example_mean']:.4f} (thang 4)")
    print()
    print("--- Global flatten (tham chieu) ---")
    if metrics["global_spearman_flatten"] is not None:
        print(f"* Spearman R (flatten)           : {metrics['global_spearman_flatten']:.4f}")
        print(f"* Kendall Tau (flatten)          : {metrics['global_kendall_flatten']:.4f}")
        print(f"* Pearson R (flatten)            : {metrics['global_pearson_flatten']:.4f}")
    if metrics["global_mae_flatten"] is not None:
        print(f"* MAE (flatten)                  : {metrics['global_mae_flatten']:.4f} (thang 4)")
    print("=" * 58 + "\n")


def resolve_target_file(argv: List[str]) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if len(argv) > 1:
        return argv[1]
    output_dir = os.path.join(current_dir, "output")
    jsonl_files = glob.glob(os.path.join(output_dir, "*.jsonl"))
    if not jsonl_files:
        print("Khong tim thay file .jsonl trong evaluation/conala/output/")
        sys.exit(1)
    return max(jsonl_files, key=os.path.getmtime)


def main() -> None:
    target_file = resolve_target_file(sys.argv)
    if not os.path.exists(target_file):
        print(f"Khong tim thay file: {target_file}")
        sys.exit(1)

    records = load_examples_from_jsonl(target_file)
    if not records:
        print("File JSONL rong.")
        sys.exit(1)

    metrics = compute_per_example_metrics(records)
    print_report(target_file, metrics)


if __name__ == "__main__":
    main()
