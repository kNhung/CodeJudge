import argparse
import json
import os
import re
import numpy as np
from scipy import stats
from sklearn.metrics import root_mean_squared_error

conala_test_cases = [
    "baseline",
    "tranx-annot",
    "best-tranx",
    "best-tranx-rerank",
    "codex",
]

def extend(array):
    return [item for sublist in array for item in sublist]

def calculate_metrics(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    parameters = data.get("parameters", {})
    return_type = parameters.get("return_type", "bool")

    references, predictions = [], []
    invalid_cnt = 0
    total_cnt = 0
    max_pred = 0

    for d in data["data"]:
        example_references = []
        example_predictions = []
        for k in conala_test_cases:
            total_cnt += 1
            example_references.append(float(d["grade"][k]))
            raw_score = float(d["code_gpt_score"][k]["code_gpt_score"])
            if raw_score == -1:
                invalid_cnt += 1
                example_predictions.append(0.0)
            else:
                example_predictions.append(raw_score)
                max_pred = max(max_pred, raw_score)
        references.append(example_references)
        predictions.append(example_predictions)

    ref = extend(references)
    pred = extend(predictions)
    
    # Scale model predictions (0-1 range) to the 0-4 human grade scale
    ref_scale = np.array(ref, dtype=float)
    pred_scale = np.array(pred, dtype=float) * 4.0

    n = len(ref_scale)
    errors = pred_scale - ref_scale

    # Calculate average correlations per example
    kendalltau = []
    spearmanr = []
    pearsonr = []
    for r_item, p_item in zip(references, predictions):
        p_item_norm = [x / 4 for x in p_item] if max_pred > 1 else p_item
        r_item_norm = [x / 4 for x in r_item]
        kendalltau.append(stats.kendalltau(r_item_norm, p_item_norm).statistic)
        spearmanr.append(stats.spearmanr(r_item_norm, p_item_norm).statistic)
        pearsonr.append(stats.pearsonr(r_item_norm, p_item_norm).statistic)

    result = {
        "file_name": os.path.basename(file_path),
        "n": len(data["data"]),
        "total_items": len(data["data"]),
        "invalid_cnt": invalid_cnt,
        "total_cnt": total_cnt,
        "kendall_tau": float(np.nanmean(kendalltau)),
        "spearmanr": float(np.nanmean(spearmanr)),
        "pearsonr": float(np.nanmean(pearsonr)),
        "mae": float(np.mean(np.abs(errors))) if n else float("nan"),
        "rmse": float(np.sqrt(np.mean(errors**2))) if n else float("nan"),
        "mean_bias": float(np.mean(errors)) if n else float("nan"),
        "average_time": None,
    }

    stored_elapsed = parameters.get("elapsed_seconds")
    if stored_elapsed is not None and len(data["data"]) > 0:
        result["average_time"] = float(stored_elapsed) / len(data["data"])

    return result

def format_metric(value, digits=3):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)

def print_table(rows):
    headers = [
        "file",
        "n",
        "Kendall Tau",
        "Spearmanr",
        "MAE",
        "RMSE",
        "Mean Bias",
        "Avg time (s)",
    ]
    print("\t".join(headers))
    for row in rows:
        print(
            "\t".join(
                [
                    row["file_name"],
                    str(row["n"]),
                    format_metric(row["kendall_tau"]),
                    format_metric(row["spearmanr"]),
                    format_metric(row["mae"]),
                    format_metric(row["rmse"]),
                    format_metric(row["mean_bias"]),
                    format_metric(row["average_time"]),
                ]
            )
        )

def print_detail(row):
    print(f"\n{row['file_name']}")
    print(f"  n: {row['n']}/{row['total_items']} valid items")
    if row["invalid_cnt"]:
        print(f"  invalid_cnt: {row['invalid_cnt']}/{row['total_cnt']}")
    print(f"  Kendall Tau: {format_metric(row['kendall_tau'])}")
    print(f"  Spearmanr:   {format_metric(row['spearmanr'])}")
    print(f"  Pearsonr:    {format_metric(row['pearsonr'])}")
    print(f"  MAE:         {format_metric(row['mae'])}")
    print(f"  RMSE:        {format_metric(row['rmse'])}")
    print(f"  Mean Bias:   {format_metric(row['mean_bias'])}")
    if row["average_time"] is not None:
        print(f"  Avg time:    {format_metric(row['average_time'])} s/item")

def main():
    parser = argparse.ArgumentParser(
        description="Compute Conala grading metrics (correlation, MAE, RMSE, bias) in HCMUS style."
    )
    parser.add_argument(
        "--file_name",
        type=str,
        default=None,
        help="Single output JSON under output/conala/. Default: all JSON files in output/conala/.",
    )
    args = parser.parse_args()

    output_dir = "output/conala"
    if args.file_name:
        if os.path.exists(args.file_name):
            file_paths = [args.file_name]
        else:
            file_paths = [os.path.join(output_dir, args.file_name)]
    else:
        if not os.path.exists(output_dir):
            print(f"Output directory {output_dir} does not exist.")
            return
        file_paths = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith(".json") and not f.startswith("other-metrics")
        ]

    rows = []
    for fp in file_paths:
        if not os.path.exists(fp):
            print(f"File not found: {fp}")
            continue
        try:
            row = calculate_metrics(fp)
            rows.append(row)
        except Exception as e:
            print(f"Error processing {fp}: {e}")

    if not rows:
        print("No valid JSON files processed.")
        return

    if len(rows) > 1:
        print_table(rows)
    else:
        print_detail(rows[0])

if __name__ == "__main__":
    main()
