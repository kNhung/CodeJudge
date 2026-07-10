import json
import os
import sys
import glob
import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau

def calculate_metrics_for_file(file_path):
    actual_grades = []
    predicted_grades = []
    runtime_list = []
    skipped_rows = 0
    error_samples = 0
    total_evaluations = 0
    total_input_tokens = 0
    total_output_tokens = 0
    example_groups = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                example_index = data.get("example_index", idx)
                ex_refs = []
                ex_preds = []
                
                results = data.get("results", [])
                for res_item in results:
                    total_evaluations += 1
                    
                    usage = res_item.get("usage", {})
                    if isinstance(usage, dict):
                        total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                        total_output_tokens += int(usage.get("output_tokens", 0) or 0)
                        
                    actual = res_item.get("grade_reference")
                    if actual is None:
                        skipped_rows += 1
                        continue
                    try:
                        actual = float(actual)
                    except ValueError:
                        skipped_rows += 1
                        continue
                        
                    predicted = None
                    res_detail = res_item.get("result", {})
                    if isinstance(res_detail, dict):
                        summary = res_detail.get("summary", {})
                        if isinstance(summary, dict) and "score_on_4" in summary:
                            predicted = summary.get("score_on_4")
                        else:
                            scoring = res_detail.get("scoring", {})
                            if isinstance(scoring, dict):
                                final_score_10 = scoring.get("final_score_on_10")
                                if final_score_10 is not None:
                                    if float(final_score_10) == -1.0:
                                        predicted = -1.0
                                    else:
                                        predicted = float(final_score_10) / 10.0 * 4.0
                    
                    if predicted is None:
                        predicted = 0.0
                        
                    if predicted == -1.0 or (isinstance(res_detail, dict) and res_detail.get("scoring", {}).get("has_error")):
                        error_samples += 1
                        continue
                        
                    try:
                        predicted = float(predicted)
                    except ValueError:
                        error_samples += 1
                        continue
                        
                    actual_grades.append(actual)
                    predicted_grades.append(predicted)
                    ex_refs.append(actual)
                    ex_preds.append(predicted)
                    
                    runtime = float(res_item.get("runtime_seconds", 0.0))
                    if runtime > 0:
                        runtime_list.append(runtime)
                
                if len(ex_refs) >= 2:
                    example_groups[example_index] = (ex_refs, ex_preds)
                        
            except Exception as e:
                skipped_rows += 1
                continue

    num_valid_samples = len(actual_grades)
    if num_valid_samples == 0:
        return None

    # Correlations (Global)
    g_pearson, g_spearman, g_tau = 0.0, 0.0, 0.0
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        try:
            g_pearson, _ = pearsonr(actual_grades, predicted_grades)
            g_spearman, _ = spearmanr(actual_grades, predicted_grades)
            g_tau, _ = kendalltau(actual_grades, predicted_grades)
        except:
            pass

    # Correlations (Per-example average)
    k_list, s_list, p_list = [], [], []
    for ex_index, (r, p) in example_groups.items():
        if len(set(r)) > 1 and len(set(p)) > 1:
            try:
                p_list.append(pearsonr(r, p)[0])
                s_list.append(spearmanr(r, p)[0])
                k_list.append(kendalltau(r, p)[0])
            except:
                pass
    avg_pearson = np.nanmean(p_list) if p_list else 0.0
    avg_spearman = np.nanmean(s_list) if s_list else 0.0
    avg_kendall = np.nanmean(k_list) if k_list else 0.0

    actuals = np.array(actual_grades)
    predicteds = np.array(predicted_grades)
    mae = np.mean(np.abs(predicteds - actuals))
    rmse = np.sqrt(np.mean((predicteds - actuals) ** 2))
    mean_bias = np.mean(predicteds - actuals)
    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    cost_usd = (total_input_tokens * (0.075 / 1000000)) + (total_output_tokens * (0.3 / 1000000))
    cost_vnd = cost_usd * 26320

    return {
        "file_name": os.path.basename(file_path),
        "valid_samples": num_valid_samples,
        "total_evaluations": total_evaluations,
        "avg_pearson": avg_pearson,
        "avg_spearman": avg_spearman,
        "avg_kendall": avg_kendall,
        "g_pearson": g_pearson,
        "g_spearman": g_spearman,
        "g_tau": g_tau,
        "mae": mae,
        "rmse": rmse,
        "mean_bias": mean_bias,
        "avg_time": avg_time,
        "cost_vnd": cost_vnd
    }

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scan_dirs = [
        os.path.join(current_dir, "output"),
        os.path.join(current_dir, "output_to_share"),
        os.path.join(os.path.dirname(current_dir), "output", "conala")
    ]
    
    jsonl_files = []
    for s_dir in scan_dirs:
        if os.path.exists(s_dir):
            jsonl_files.extend(glob.glob(os.path.join(s_dir, "**/*.jsonl"), recursive=True))

    jsonl_files = list(set([os.path.abspath(f) for f in jsonl_files]))
    
    if not jsonl_files:
        print("❌ Không tìm thấy file .jsonl nào trong các thư mục kết quả của CoNaLa.")
        return

    print(f"🔍 Tìm thấy {len(jsonl_files)} file kết quả CoNaLa. Đang tiến hành tính toán...")
    
    results = []
    for fp in sorted(jsonl_files):
        metrics = calculate_metrics_for_file(fp)
        if metrics:
            results.append(metrics)

    if not results:
        print("❌ Không có file nào chứa dữ liệu hợp lệ.")
        return

    headers = [
        "File Name", "Valid", "P_avg", "S_avg", "K_avg", "P_glob", "S_glob", "MAE", "RMSE", "Bias", "Time(s)", "Cost(đ)"
    ]
    print("\n" + "="*125)
    print("🏆 BẢNG TỔNG HỢP SO SÁNH METRICS CÁC MÔ HÌNH (CoNaLa)")
    print("="*125)
    print(f"{headers[0]:<40} | {headers[1]:<5} | {headers[2]:<6} | {headers[3]:<6} | {headers[4]:<6} | {headers[5]:<6} | {headers[6]:<6} | {headers[7]:<6} | {headers[8]:<6} | {headers[9]:<6} | {headers[10]:<7} | {headers[11]:<7}")
    print("-"*125)
    for r in results:
        name = r["file_name"]
        if len(name) > 38:
            name = name[:35] + "..."
        print(f"{name:<40} | {r['valid_samples']:<5} | {r['avg_pearson']:.4f} | {r['avg_spearman']:.4f} | {r['avg_kendall']:.4f} | {r['g_pearson']:.4f} | {r['g_spearman']:.4f} | {r['mae']:.4f} | {r['rmse']:.4f} | {r['mean_bias']:+.4f} | {r['avg_time']:.1f}s | {r['cost_vnd']:,.0f}đ")
    print("="*125 + "\n")

if __name__ == "__main__":
    main()
