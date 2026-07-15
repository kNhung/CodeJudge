import json
import os
import sys
import glob
import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau

def analyze_model_performance(file_path):
    # Windows console may default to cp1252, which breaks on emoji.
    # Force UTF-8 if possible, and avoid printing emoji.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(f"INFO: Dang xu ly tap du lieu CoNaLa: {file_path}")
    
    if not os.path.exists(file_path):
        print("ERROR: Khong tim thay file tai duong dan nay.")
        return

    actual_grades = []
    predicted_grades = []
    runtime_list = []
    skipped_rows = 0  # Dòng bị thiếu grade_reference hoặc lỗi parse JSON
    error_samples = 0 # Dòng bị lỗi trong quá trình chấm
    total_evaluations = 0 # Tổng số lượt đánh giá thành phần
    total_input_tokens = 0
    total_output_tokens = 0
    example_groups = {} # Group refs and preds by example_index to compute per-example correlation

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
                    
                    # Tích lũy token usage
                    usage = res_item.get("usage", {})
                    if isinstance(usage, dict):
                        total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                        total_output_tokens += int(usage.get("output_tokens", 0) or 0)
                        
                    # Lấy grade_reference (thang điểm 4)
                    actual = res_item.get("grade_reference")
                    if actual is None:
                        skipped_rows += 1
                        continue
                    try:
                        actual = float(actual)
                    except ValueError:
                        skipped_rows += 1
                        continue
                        
                    # Lấy predicted_score (quy đổi ra thang điểm 4)
                    predicted = None
                    res_detail = res_item.get("result", {})
                    if isinstance(res_detail, dict):
                        summary = res_detail.get("summary", {})
                        if isinstance(summary, dict) and "score_on_4" in summary:
                            predicted = summary.get("score_on_4")
                        else:
                            # Thử lấy từ scoring và quy đổi
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
                        
                    # Nếu mẫu bị lỗi chấm điểm (-1.0 hoặc lỗi hệ thống)
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
                    
                    # Thời gian chạy
                    runtime = float(res_item.get("runtime_seconds", 0.0))
                    if runtime > 0:
                        runtime_list.append(runtime)
                
                if len(ex_refs) >= 2:
                    example_groups[example_index] = (ex_refs, ex_preds)
                        
            except Exception as e:
                print(f"WARNING: Canh bao dong {idx}: Khong parse duoc JSON tho hoac loi kieu du lieu. Chi tiet: {e}")
                skipped_rows += 1
                continue

    # ---- TIẾN HÀNH TÍNH TOÁN METRICS ----
    num_valid_samples = len(actual_grades)
    
    if num_valid_samples == 0:
        print("ERROR: Khong thu thap duoc cap du lieu diem (Thuc te - Du doan) nao hop le.")
        return

    valid_pct = (num_valid_samples / total_evaluations) * 100 if total_evaluations > 0 else 0.0
    error_pct = (error_samples / total_evaluations) * 100 if total_evaluations > 0 else 0.0

    # Chi phí ước tính (Gemini 2.5 Flash trên OpenRouter)
    # Input: $0.075 / 1M tokens, Output: $0.30 / 1M tokens
    cost_usd = (total_input_tokens * (0.075 / 1000000)) + (total_output_tokens * (0.3 / 1000000))
    cost_vnd = cost_usd * 26320  

    cost_per_sample_usd = cost_usd / num_valid_samples if num_valid_samples > 0 else 0.0
    cost_per_sample_vnd = cost_vnd / num_valid_samples if num_valid_samples > 0 else 0.0

    # Tính toán các hệ số tương quan toàn cục
    g_pearson, g_spearman, g_tau = 0.0, 0.0, 0.0
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        try:
            g_pearson, _ = pearsonr(actual_grades, predicted_grades)
            g_spearman, _ = spearmanr(actual_grades, predicted_grades)
            g_tau, _ = kendalltau(actual_grades, predicted_grades)
        except Exception as e:
            print(f"WARNING: Khong tinh duoc tuong quan toan cuc: {e}")

    # Tính toán các hệ số tương quan trung bình theo từng bài toán (Per-example Average Correlation - Khớp với Paper)
    k_list, s_list, p_list = [], [], []
    for ex_index, (r, p) in example_groups.items():
        if len(set(r)) > 1 and len(set(p)) > 1:
            try:
                p_list.append(pearsonr(r, p)[0])
                s_list.append(spearmanr(r, p)[0])
                k_list.append(kendalltau(r, p)[0])
            except Exception:
                pass
    avg_pearson = np.nanmean(p_list) if p_list else 0.0
    avg_spearman = np.nanmean(s_list) if s_list else 0.0
    avg_kendall = np.nanmean(k_list) if k_list else 0.0

    # MAE, RMSE, Mean Bias
    actuals = np.array(actual_grades)
    predicteds = np.array(predicted_grades)
    mae = np.mean(np.abs(predicteds - actuals))
    rmse = np.sqrt(np.mean((predicteds - actuals) ** 2))
    mean_bias = np.mean(predicteds - actuals)  # > 0: chấm nới tay, < 0: chấm khắt khe

    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    # ---- IN KẾT QUẢ ----
    print("\n" + "="*60)
    print("BANG TONG HOP METRICS DANH GIA MO HINH (CoNaLa)")
    print("="*60)
    print(f"TOTAL evaluations read: {total_evaluations}")
    print(f"VALID samples         : {num_valid_samples} ({valid_pct:.2f}%)")
    print(f"ERROR samples (-1)    : {error_samples} ({error_pct:.2f}%)")
    print("\n[Cach 1] Tuong quan trung binh theo bai toan (khop Paper):")
    print(f"  Pearson R           : {avg_pearson:.4f}")
    print(f"  Spearman R          : {avg_spearman:.4f}")
    print(f"  Kendall Tau         : {avg_kendall:.4f}")
    print("\n[Cach 2] Tuong quan toan cuc (Global Flattened):")
    print(f"  Pearson R           : {g_pearson:.4f}")
    print(f"  Spearman R          : {g_spearman:.4f}")
    print(f"  Kendall Tau         : {g_tau:.4f}")
    print("\nSai so (thang diem 4):")
    print(f"  MAE                 : {mae:.4f}")
    print(f"  RMSE                : {rmse:.4f}")
    print(f"  Mean Bias           : {mean_bias:+.4f} (>0: noi tay, <0: khat khe)")
    print(f"\nTotal tokens consumed : {total_input_tokens + total_output_tokens:,} tokens")
    print(f"  + Input tokens      : {total_input_tokens:,} tokens")
    print(f"  + Output tokens     : {total_output_tokens:,} tokens")
    print(f"Est. cost             : {cost_usd:.5f} USD (~{cost_vnd:,.0f} VND)")
    print(f"Avg cost/sample       : {cost_per_sample_usd:.5f} USD (~{cost_per_sample_vnd:,.1f} VND)")
    print(f"Avg runtime           : {avg_time:.3f} giay / luot danh gia")
    if skipped_rows > 0:
        print(f"SKIPPED lines due to parse/error: {skipped_rows}")
    print("="*60 + "\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if len(sys.argv) > 1:
        TARGET_FILE = sys.argv[1]
    else:
        # Tự động tìm file .jsonl mới nhất trong thư mục output/
        output_dir = os.path.join(current_dir, "output_to_share")
        jsonl_files = glob.glob(os.path.join(output_dir, "*.jsonl"))
        if jsonl_files:
            TARGET_FILE = max(jsonl_files, key=os.path.getmtime)
        else:
            print("ERROR: Khong tim thay file .jsonl trong output. Vui long truyen duong dan file.")
            sys.exit(1)
            
    analyze_model_performance(TARGET_FILE)
