import json
import os
import sys
import glob
import numpy as np
from scipy.stats import kendalltau, spearmanr

def calculate_metrics_for_file(file_path):
    actual_grades = []
    predicted_grades = []
    runtime_list = []
    skipped_rows = 0
    error_samples = 0
    total_samples = 0
    total_input_tokens = 0
    total_output_tokens = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
                if data.get("scoring_mode") == "per_question":
                    continue
                
                total_samples += 1
                
                usage = data.get("usage", {})
                if isinstance(usage, dict):
                    total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                    total_output_tokens += int(usage.get("output_tokens", 0) or 0)
                
                if "expect_grade" in data and data["expect_grade"] is not None:
                    actual = float(data["expect_grade"])
                else:
                    skipped_rows += 1
                    continue
                
                predicted = None
                keys = ["predicted_total_score", "exam_total_predicted_score", "final_score", "quality_score"]
                
                for k in keys:
                    if k in data and data[k] is not None:
                        predicted = float(data[k])
                        break
                
                if predicted is None:
                    res = data.get("result", {})
                    if isinstance(res, dict):
                        for k in keys:
                            if k in res and res[k] is not None:
                                predicted = float(res[k])
                                break
                
                if predicted is None:
                    predicted = 0.0
                
                if predicted == -1.0:
                    error_samples += 1
                    continue
                
                actual_grades.append(actual)
                predicted_grades.append(predicted)
                
                runtime = float(data.get("runtime_seconds", 0.0))
                if runtime > 0:
                    runtime_list.append(runtime)

            except Exception as e:
                skipped_rows += 1
                continue

    num_valid_samples = len(actual_grades)
    if num_valid_samples == 0:
        return None

    cost_usd = (total_input_tokens * (0.3 / 1000000)) + (total_output_tokens * (2.5 / 1000000))
    cost_vnd = cost_usd * 26320  

    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        try:
            tau, _ = kendalltau(actual_grades, predicted_grades)
            spearman_r, _ = spearmanr(actual_grades, predicted_grades)
        except:
            tau, spearman_r = 0.0, 0.0
    else:
        tau, spearman_r = 0.0, 0.0

    actuals = np.array(actual_grades)
    predicteds = np.array(predicted_grades)
    mae = np.mean(np.abs(predicteds - actuals))
    rmse = np.sqrt(np.mean((predicteds - actuals) ** 2))
    mean_bias = np.mean(predicteds - actuals)
    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    return {
        "file_name": os.path.basename(file_path),
        "valid_samples": num_valid_samples,
        "total_samples": total_samples,
        "tau": tau,
        "spearman_r": spearman_r,
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
        os.path.join(os.path.dirname(current_dir), "output", "hcmus")
    ]
    
    jsonl_files = []
    for s_dir in scan_dirs:
        if os.path.exists(s_dir):
            jsonl_files.extend(glob.glob(os.path.join(s_dir, "**/*.jsonl"), recursive=True))

    jsonl_files = list(set([os.path.abspath(f) for f in jsonl_files]))
    
    if not jsonl_files:
        print("❌ Không tìm thấy file .jsonl nào trong các thư mục kết quả của HCMUS.")
        return

    print(f"🔍 Tìm thấy {len(jsonl_files)} file kết quả HCMUS. Đang tiến hành tính toán...")
    
    results = []
    for fp in sorted(jsonl_files):
        metrics = calculate_metrics_for_file(fp)
        if metrics:
            results.append(metrics)

    if not results:
        print("❌ Không có file nào chứa dữ liệu hợp lệ.")
        return

    headers = [
        "File Name", "Valid", "Kendall Tau", "Spearman R", "MAE", "RMSE", "Bias", "Time(s)", "Cost(đ)"
    ]
    print("\n" + "="*115)
    print("🏆 BẢNG TỔNG HỢP SO SÁNH METRICS CÁC MÔ HÌNH (HCMUS)")
    print("="*115)
    print(f"{headers[0]:<40} | {headers[1]:<5} | {headers[2]:<11} | {headers[3]:<10} | {headers[4]:<6} | {headers[5]:<6} | {headers[6]:<6} | {headers[7]:<7} | {headers[8]:<7}")
    print("-"*115)
    for r in results:
        name = r["file_name"]
        if len(name) > 38:
            name = name[:35] + "..."
        print(f"{name:<40} | {r['valid_samples']:<5} | {r['tau']:.4f}      | {r['spearman_r']:.4f}     | {r['mae']:.4f} | {r['rmse']:.4f} | {r['mean_bias']:+.4f} | {r['avg_time']:.1f}s | {r['cost_vnd']:,.0f}đ")
    print("="*115 + "\n")

if __name__ == "__main__":
    main()
