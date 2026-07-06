import os
import json
import argparse
import numpy as np
from scipy import stats

conala_test_cases = [
    "baseline",
    "tranx-annot",
    "best-tranx",
    "best-tranx-rerank",
    "codex",
]

def extend(array):
    return [item for sublist in array for item in sublist]

def print_correlation(file_path):
    file_name = os.path.basename(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    references, predictions = [], []
    invalid_cnt = 0
    max_pred = 0.0
    
    for d in data.get("data", []):
        example_refs = []
        example_preds = []
        for k in conala_test_cases:
            example_refs.append(float(d["grade"][k]))
            
            score_data = d.get("code_gpt_score", {}).get(k, {})
            score = float(score_data.get("code_gpt_score", -1))
            if score == -1:
                invalid_cnt += 1
                example_preds.append(0.0) # default fallback
            else:
                example_preds.append(score)
                if score > max_pred:
                    max_pred = score
        references.append(example_refs)
        predictions.append(example_preds)

    if not references:
        print(f"{file_name} | No data found")
        return

    # Calculate average correlation across all examples (rank-based)
    kt_list, pr_list, sr_list = [], [], []
    for ref, pred in zip(references, predictions):
        kt = stats.kendalltau(ref, pred).statistic
        pr = stats.pearsonr(ref, pred).statistic
        sr = stats.spearmanr(ref, pred).statistic
        
        kt_list.append(kt)
        pr_list.append(pr)
        sr_list.append(sr)

    kendalltau = np.nanmean(kt_list)
    spearmanr = np.nanmean(sr_list)
    
    # Calculate MAE, RMSE, Mean Bias on flat lists
    flat_refs = np.array(extend(references))
    flat_preds = np.array(extend(predictions))
    
    # Rescale flat_preds if they are in [0, 1] to match the [0, 4] scale of Conala grades
    if max_pred <= 1.0:
        flat_preds = flat_preds * 4.0
    
    errors = flat_preds - flat_refs
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors**2))
    bias = np.mean(errors)
    
    # Also calculate normalized versions on [0, 1] scale (for paper comparison)
    norm_refs = flat_refs / 4.0
    norm_preds = flat_preds / 4.0
    norm_errors = norm_preds - norm_refs
    norm_mae = np.mean(np.abs(norm_errors))
    norm_rmse = np.sqrt(np.mean(norm_errors**2))
    norm_bias = np.mean(norm_errors)

    # Format the display
    print(f"{file_name}")
    print(f"  n: {len(references)} examples")
    elapsed_seconds = data.get("parameters", {}).get("elapsed_seconds")
    if elapsed_seconds is not None and len(references) > 0:
        print(f"  Average time: {elapsed_seconds / len(references):.3f} s/example (total: {elapsed_seconds:.1f} s)")
    if invalid_cnt > 0:
        print(f"  invalid_cnt: {invalid_cnt}")
    print(f"  Kendall Tau: {kendalltau:.3f}" if not np.isnan(kendalltau) else "  Kendall Tau: N/A")
    print(f"  Spearmanr:   {spearmanr:.3f}" if not np.isnan(spearmanr) else "  Spearmanr:   N/A")
    print(f"  On 0-4 Grade Scale:")
    print(f"    MAE:       {mae:.3f}")
    print(f"    RMSE:      {rmse:.3f}")
    print(f"    Mean Bias: {bias:.3f}")
    print(f"  On Normalized 0-1 Scale:")
    print(f"    MAE:       {norm_mae:.3f}")
    print(f"    RMSE:      {norm_rmse:.3f}")
    print(f"    Mean Bias: {norm_bias:.3f}")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Calculate correlation metrics for Conala evaluation output.")
    parser.add_argument("--file_name", type=str, default=None, help="Name of JSON file in output/conala/")
    args = parser.parse_args()

    output_dir = "output/conala"
    
    if args.file_name:
        file_path = os.path.join(output_dir, args.file_name)
        if not os.path.exists(file_path):
            file_path = args.file_name
        if os.path.exists(file_path):
            print("-" * 50)
            print_correlation(file_path)
        else:
            print(f"File not found: {args.file_name}")
        return

    if not os.path.exists(output_dir):
        print(f"Directory {output_dir} does not exist.")
        return

    file_list = sorted(
        [
            f for f in os.listdir(output_dir)
            if f.endswith(".json") and not f.startswith("other-metrics")
        ]
    )
    
    if not file_list:
        print("No evaluation output files found in output/conala/")
        return

    print("-" * 50)
    for file_name in file_list:
        print_correlation(os.path.join(output_dir, file_name))

if __name__ == "__main__":
    main()
