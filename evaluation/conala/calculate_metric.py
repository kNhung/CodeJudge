import json
import os
import sys
import glob
import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau

def analyze_model_performance(file_path):
    print(f"📊 Đang xử lý tập dữ liệu CoNaLa: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Lỗi: Không tìm thấy file tại đường dẫn này.")
        return

    actual_grades = []
    predicted_grades = []
    runtime_list = []
    skipped_rows = 0  # Dòng bị thiếu grade_reference hoặc lỗi parse JSON
    error_samples = 0 # Dòng bị lỗi trong quá trình chấm
    total_evaluations = 0 # Tổng số lượt đánh giá thành phần
    total_input_tokens = 0
    total_output_tokens = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
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
                    
                    # Thời gian chạy
                    runtime = float(res_item.get("runtime_seconds", 0.0))
                    if runtime > 0:
                        runtime_list.append(runtime)
                        
            except Exception as e:
                print(f"⚠️ Cảnh báo dòng {idx}: Không parse được JSON thô hoặc lỗi kiểu dữ liệu. Chi tiết: {e}")
                skipped_rows += 1
                continue

    # ---- TIẾN HÀNH TÍNH TOÁN METRICS ----
    num_valid_samples = len(actual_grades)
    
    if num_valid_samples == 0:
        print("❌ Không thu thập được cặp dữ liệu điểm (Thực tế - Dự đoán) nào hợp lệ.")
        return

    valid_pct = (num_valid_samples / total_evaluations) * 100 if total_evaluations > 0 else 0.0
    error_pct = (error_samples / total_evaluations) * 100 if total_evaluations > 0 else 0.0

    # Chi phí ước tính (Gemini 2.5 Flash trên OpenRouter)
    # Input: $0.075 / 1M tokens, Output: $0.30 / 1M tokens
    cost_usd = (total_input_tokens * (0.075 / 1000000)) + (total_output_tokens * (0.3 / 1000000))
    cost_vnd = cost_usd * 26320  

    cost_per_sample_usd = cost_usd / num_valid_samples if num_valid_samples > 0 else 0.0
    cost_per_sample_vnd = cost_vnd / num_valid_samples if num_valid_samples > 0 else 0.0

    # Tính toán các hệ số tương quan
    pearson_r, spearman_r, tau = 0.0, 0.0, 0.0
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        try:
            pearson_r, _ = pearsonr(actual_grades, predicted_grades)
            spearman_r, _ = spearmanr(actual_grades, predicted_grades)
            tau, _ = kendalltau(actual_grades, predicted_grades)
        except Exception as e:
            print(f"⚠️ Không tính được tương quan: {e}")

    # MAE, RMSE, Mean Bias
    actuals = np.array(actual_grades)
    predicteds = np.array(predicted_grades)
    mae = np.mean(np.abs(predicteds - actuals))
    rmse = np.sqrt(np.mean((predicteds - actuals) ** 2))
    mean_bias = np.mean(predicteds - actuals)  # > 0: chấm nới tay, < 0: chấm khắt khe

    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    # ---- IN KẾT QUẢ ĐẸP MẮT ----
    print("\n" + "="*50)
    print("🎯 BẢNG TỔNG HỢP METRICS ĐÁNH GIÁ MÔ HÌNH (CoNaLa)")
    print("="*50)
    print(f"🔹 Tổng số lượt đánh giá đọc được: {total_evaluations}")
    print(f"🔹 Số lượng mẫu hợp lệ (Valid)  : {num_valid_samples} ({valid_pct:.2f}%)")
    print(f"🔹 Số lượng mẫu lỗi (Errors -1) : {error_samples} ({error_pct:.2f}%)")
    print(f"🔹 Hệ số tương quan Pearson R   : {pearson_r:.4f}")
    print(f"🔹 Hệ số tương quan Spearman R  : {spearman_r:.4f}")
    print(f"🔹 Hệ số tương quan Kendall Tau : {tau:.4f}")
    print(f"🔹 Sai số tuyệt đối TB (MAE)    : {mae:.4f} (Thang điểm 4)")
    print(f"🔹 Căn sai số bình phương (RMSE): {rmse:.4f} (Thang điểm 4)")
    print(f"🔹 Độ lệch trung bình (Mean Bias): {mean_bias:+.4f} (Ý nghĩa: >0 chấm nới tay, <0 chấm khắt khe)")
    print(f"🔹 Tổng token tiêu thụ (Usage)  : {total_input_tokens + total_output_tokens:,} tokens")
    print(f"   + Input Tokens               : {total_input_tokens:,} tokens")
    print(f"   + Output Tokens              : {total_output_tokens:,} tokens")
    print(f"🔹 Chi phí ước tính (Est. Cost) : {cost_usd:.5f} USD (~{cost_vnd:,.0f} VNĐ)")
    print(f"   + Chi phí trung bình / mẫu   : {cost_per_sample_usd:.5f} USD (~{cost_per_sample_vnd:,.1f} VNĐ)")
    print(f"🔹 Thời gian phản hồi trung bình: {avg_time:.3f} giây / lượt đánh giá")
    if skipped_rows > 0:
        print(f"🔸 Số dòng bị bỏ qua do lỗi    : {skipped_rows}")
    print("="*50 + "\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if len(sys.argv) > 1:
        TARGET_FILE = sys.argv[1]
    else:
        # Tự động tìm file .jsonl mới nhất trong thư mục output/
        output_dir = os.path.join(current_dir, "output")
        jsonl_files = glob.glob(os.path.join(output_dir, "*.jsonl"))
        if jsonl_files:
            TARGET_FILE = max(jsonl_files, key=os.path.getmtime)
        else:
            print("❌ Không tìm thấy file .jsonl nào trong thư mục output. Vui lòng truyền đường dẫn file.")
            sys.exit(1)
            
    analyze_model_performance(TARGET_FILE)
