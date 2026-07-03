import argparse
import json
import os
import re

import numpy as np
from scipy import stats

RETURN_TYPE_SCALE = {
    "helpful_score": 10.0,
    "0_to_4_score_usefulness": 2.5,
    "0_to_4_score_functional_correctness": 2.5,
    "score": 10.0,
    "inconsistency_level": 10.0,
    "error_level": 10.0,
}


def normalize_prediction(score, return_type):
    if score == -1:
        return None
    scale = RETURN_TYPE_SCALE.get(return_type, 2.5)
    return float(score) * scale


def parse_filename_meta(file_name):
    match = re.search(
        r"-1-(\d+)-([\d.]+)(?:-limit-(\d+))?(?:-perq)?-sample-(\d+)\.json$",
        file_name,
    )
    if not match:
        return {}
    return {
        "compare_prompt_index": int(match.group(1)),
        "temperature": float(match.group(2)),
        "limit": int(match.group(3)) if match.group(3) else 0,
        "per_question": "-perq" in file_name,
        "sample_index": int(match.group(4)),
    }


def describe_run(parameters, file_name):
    model = parameters.get("model", "unknown")
    meta = parse_filename_meta(file_name)
    compare_prompt = meta.get("compare_prompt_index", "?")
    per_question = parameters.get("per_question", meta.get("per_question", False))
    return_type = parameters.get("return_type", "")
    temperature = parameters.get("temperature", meta.get("temperature", 0))
    limit = parameters.get("limit", meta.get("limit", 0))

    mode = "per-question" if per_question else "whole-submission"
    return (
        f"{model} | prompt={compare_prompt} | T={temperature} | "
        f"{mode} | {return_type} | limit={limit}"
    )


def calculate_metrics(file_path, elapsed_seconds=None):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    parameters = data.get("parameters", {})
    return_type = parameters.get("return_type")
    per_question = parameters.get("per_question", False)

    references, predictions = [], []
    submission_invalid_cnt = 0
    question_invalid_cnt = 0
    question_total_cnt = 0

    for item in data["data"]:
        submission_score = item["code_gpt_score"]["submission"]
        if per_question and "questions" in submission_score:
            for question in submission_score["questions"].values():
                question_total_cnt += 1
                if float(question["code_gpt_score"]) == -1:
                    question_invalid_cnt += 1

        raw_score = float(submission_score["code_gpt_score"])
        if raw_score == -1:
            submission_invalid_cnt += 1
            continue

        prediction = normalize_prediction(raw_score, return_type)
        if prediction is None:
            submission_invalid_cnt += 1
            continue

        references.append(float(item["expect_grade"]))
        predictions.append(prediction)

    references = np.array(references, dtype=float)
    predictions = np.array(predictions, dtype=float)
    n = len(references)
    errors = predictions - references

    result = {
        "file_name": os.path.basename(file_path),
        "run": describe_run(parameters, os.path.basename(file_path)),
        "n": n,
        "total_items": len(data["data"]),
        "submission_invalid_cnt": submission_invalid_cnt,
        "kendall_tau": float("nan"),
        "spearmanr": float("nan"),
        "pearsonr": float("nan"),
        "mae": float(np.mean(np.abs(errors))) if n else float("nan"),
        "rmse": float(np.sqrt(np.mean(errors**2))) if n else float("nan"),
        "mean_bias": float(np.mean(errors)) if n else float("nan"),
        "average_time": None,
        "question_parse_rate": None,
    }

    if n >= 2:
        result["kendall_tau"] = float(stats.kendalltau(references, predictions).statistic)
        result["spearmanr"] = float(stats.spearmanr(references, predictions).statistic)
        result["pearsonr"] = float(stats.pearsonr(references, predictions).statistic)

    if elapsed_seconds is not None and n > 0:
        result["average_time"] = elapsed_seconds / n

    stored_elapsed = parameters.get("elapsed_seconds")
    if result["average_time"] is None and stored_elapsed is not None and n > 0:
        result["average_time"] = float(stored_elapsed) / n

    if question_total_cnt:
        valid_q = question_total_cnt - question_invalid_cnt
        result["question_parse_rate"] = 100.0 * valid_q / question_total_cnt

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
        "Q parse %",
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
                    format_metric(row["question_parse_rate"], digits=1),
                ]
            )
        )


def print_detail(row):
    print(f"\n{row['file_name']}")
    print(f"  run: {row['run']}")
    print(f"  n: {row['n']}/{row['total_items']} valid submissions")
    if row["submission_invalid_cnt"]:
        print(f"  submission_invalid: {row['submission_invalid_cnt']}")
    print(f"  Kendall Tau: {format_metric(row['kendall_tau'])}")
    print(f"  Spearmanr:   {format_metric(row['spearmanr'])}")
    print(f"  Pearsonr:    {format_metric(row['pearsonr'])}")
    print(f"  MAE:         {format_metric(row['mae'])}")
    print(f"  RMSE:        {format_metric(row['rmse'])}")
    print(f"  Mean Bias:   {format_metric(row['mean_bias'])}")
    print(f"  Avg time:    {format_metric(row['average_time'])} s/submission")
    if row["question_parse_rate"] is not None:
        print(f"  Q parse:     {format_metric(row['question_parse_rate'], 1)}%")


def main():
    parser = argparse.ArgumentParser(
        description="Compute HCMUS grading metrics (correlation, MAE, RMSE, bias)."
    )
    parser.add_argument(
        "--file_name",
        type=str,
        default=None,
        help="Single output JSON under output/hcmus/. Default: all JSON files.",
    )
    parser.add_argument(
        "--elapsed_seconds",
        type=float,
        default=None,
        help="Total wall-clock seconds for the run (used to compute average time).",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Print detailed metrics for each file.",
    )
    args = parser.parse_args()

    if args.file_name:
        file_list = [args.file_name]
    else:
        output_dir = "output/hcmus"
        file_list = sorted(
            name for name in os.listdir(output_dir) if name.endswith(".json")
        )

    rows = []
    for file_name in file_list:
        file_path = os.path.join("output/hcmus", file_name)
        if not os.path.exists(file_path):
            print(f"skip missing file: {file_path}")
            continue
        row = calculate_metrics(file_path, elapsed_seconds=args.elapsed_seconds)
        rows.append(row)
        if args.detail:
            print_detail(row)

    if not args.detail:
        print_table(rows)


if __name__ == "__main__":
    main()
