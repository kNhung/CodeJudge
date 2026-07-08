import json
import os
import numpy as np
from scipy.stats import kendalltau, spearmanr

def analyze_model_performance(file_path):
    print(f"📊 Đang xử lý tập dữ liệu: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Lỗi: Không tìm thấy file tại đường dẫn này.")
        return

    actual_grades = []
    predicted_grades = []
    runtime_list = []
    skipped_rows = 0  # Dòng bị thiếu expect_grade hoặc lỗi parse JSON
    error_samples = 0 # Dòng bị lỗi trong quá trình chấm (predicted == -1.0)
    total_samples = 0 # Tổng số bài thi (dòng summary) đọc được
    total_input_tokens = 0
    total_output_tokens = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
                # Bỏ qua dòng chấm chi tiết từng câu (chỉ giữ lại dòng exam_summary hoặc dòng whole_exam)
                if data.get("scoring_mode") == "per_question":
                    continue
                
                total_samples += 1
                
                # Tích lũy số token tiêu thụ từ dòng summary
                usage = data.get("usage", {})
                if isinstance(usage, dict):
                    total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                    total_output_tokens += int(usage.get("output_tokens", 0) or 0)
                
                # 1. Bóc tách điểm thực tế (expect_grade)
                if "expect_grade" in data and data["expect_grade"] is not None:
                    actual = float(data["expect_grade"])
                else:
                    skipped_rows += 1
                    continue
                
                # 2. Cơ chế bóc điểm dự đoán ĐỘNG (Xử lý việc lệch cấu trúc giữa các mô hình)
                predicted = None
                keys = ["predicted_total_score", "exam_total_predicted_score", "final_score", "quality_score"]
                
                # Kiểm tra ngoài root level trước
                for k in keys:
                    if k in data and data[k] is not None:
                        predicted = float(data[k])
                        break
                
                # Nếu không thấy, kiểm tra bên trong dict result
                if predicted is None:
                    res = data.get("result", {})
                    if isinstance(res, dict):
                        for k in keys:
                            if k in res and res[k] is not None:
                                predicted = float(res[k])
                                break
                
                # Nếu quét hết các tầng vẫn không thấy điểm, gán mặc định bằng 0.0
                if predicted is None:
                    predicted = 0.0
                
                # Nếu mẫu bị lỗi chấm điểm (-1.0), bỏ qua không đưa vào tính toán metric
                if predicted == -1.0:
                    error_samples += 1
                    continue
                
                actual_grades.append(actual)
                predicted_grades.append(predicted)
                
                # 3. Bóc tách thời gian chạy (runtime_seconds)
                runtime = float(data.get("runtime_seconds", 0.0))
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

    # Tính toán phần trăm
    valid_pct = (num_valid_samples / total_samples) * 100 if total_samples > 0 else 0.0
    error_pct = (error_samples / total_samples) * 100 if total_samples > 0 else 0.0

    # Tính toán chi phí (Gemini 2.5 Flash trên OpenRouter)
    # Input: $0.075 / 1M tokens, Output: $0.30 / 1M tokens
    cost_usd = (total_input_tokens * (0.3 / 1000000)) + (total_output_tokens * (2.5 / 1000000))
    cost_vnd = cost_usd * 26320  

    # Tính toán chi phí trung bình trên mỗi mẫu
    cost_per_sample_usd = cost_usd / total_samples if total_samples > 0 else 0.0
    cost_per_sample_vnd = cost_vnd / total_samples if total_samples > 0 else 0.0

    # Tính toán Kendall's Tau và Spearman's R
    # Kiểm tra tránh trường hợp tất cả các điểm dự đoán bị bằng nhau (hệ số biến thiên bằng 0 gây lỗi NaN)
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        tau, _ = kendalltau(actual_grades, predicted_grades)
        spearman_r, _ = spearmanr(actual_grades, predicted_grades)
    else:
        tau, spearman_r = 0.0, 0.0

    # Tính toán các chỉ số MAE, RMSE, Mean Bias
    actuals = np.array(actual_grades)
    predicteds = np.array(predicted_grades)
    mae = np.mean(np.abs(predicteds - actuals))
    rmse = np.sqrt(np.mean((predicteds - actuals) ** 2))
    mean_bias = np.mean(predicteds - actuals)  # > 0: chấm nới tay, < 0: chấm khắt khe

    # Tính toán thời gian chạy trung bình (Avg Time)
    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    # ---- IN KẾT QUẢ ĐẸP MẮT ----
    print("\n" + "="*50)
    print("🎯 BẢNG TỔNG HỢP METRICS ĐÁNH GIÁ MÔ HÌNH")
    print("="*50)
    print(f"🔹 Tổng số bài thi đọc được     : {total_samples}")
    print(f"🔹 Số lượng mẫu hợp lệ (Valid)  : {num_valid_samples} ({valid_pct:.2f}%)")
    print(f"🔹 Số lượng mẫu lỗi (Errors -1) : {error_samples} ({error_pct:.2f}%)")
    print(f"🔹 Hệ số tương quan Kendall Tau : {tau:.4f}")
    print(f"🔹 Hệ số tương quan SpearmanR  : {spearman_r:.4f}")
    print(f"🔹 Sai số tuyệt đối TB (MAE)    : {mae:.4f}")
    print(f"🔹 Căn sai số bình phương (RMSE): {rmse:.4f}")
    print(f"🔹 Độ lệch trung bình (Mean Bias): {mean_bias:+.4f} (Ý nghĩa: >0 chấm nới tay, <0 chấm khắt khe)")
    print(f"🔹 Tổng token tiêu thụ (Usage)  : {total_input_tokens + total_output_tokens:,} tokens")
    print(f"   + Input Tokens               : {total_input_tokens:,} tokens")
    print(f"   + Output Tokens              : {total_output_tokens:,} tokens")
    print(f"🔹 Chi phí ước tính (Est. Cost) : {cost_usd:.5f} USD (~{cost_vnd:,.0f} VNĐ)")
    print(f"   + Chi phí trung bình / mẫu   : {cost_per_sample_usd:.5f} USD (~{cost_per_sample_vnd:,.1f} VNĐ)")
    print(f"🔹 Thời gian phản hồi trung bình: {avg_time:.3f} giây / bài thi")
    if skipped_rows > 0:
        print(f"🔸 Số dòng bị bỏ qua do lỗi    : {skipped_rows}")
    print("="*50 + "\n")

if __name__ == "__main__":
    import sys
    import glob

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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
            TARGET_FILE = os.path.join(output_dir,"report_11", "qwen-2.5-7b-instruct_hcmus_multi_agent_tuned.jsonl")
            
    analyze_model_performance(TARGET_FILE)