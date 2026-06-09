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
    skipped_rows = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                
                # 1. Bóc tách điểm thực tế (expect_grade)
                if "expect_grade" in data and data["expect_grade"] is not None:
                    actual = float(data["expect_grade"])
                else:
                    skipped_rows += 1
                    continue
                
                # 2. Cơ chế bóc điểm dự đoán ĐỘNG
                res = data.get("result", {})
                predicted = None
                
                if isinstance(res, dict):
                    predicted = res.get("exam_total_predicted_score") or res.get("final_score") or res.get("quality_score")
                
                if predicted is None:
                    predicted = data.get("exam_total_predicted_score") or data.get("final_score") or data.get("quality_score")
                
                if predicted is None:
                    predicted = 0.0
                
                actual_grades.append(actual)
                predicted_grades.append(float(predicted))
                
                # 3. Bóc tách thời gian chạy (runtime_seconds)
                runtime = float(data.get("runtime_seconds", 0.0))
                if runtime > 0:
                    runtime_list.append(runtime)

            except Exception as e:
                print(f"⚠️ Cảnh báo dòng {idx}: Không parse được JSON thô hoặc lỗi kiểu dữ liệu. Chi tiết: {e}")
                continue

    # ---- TIẾN HÀNH TÍNH TOÁN METRICS ----
    num_samples = len(actual_grades)
    
    if num_samples == 0:
        print("❌ Không thu thập được cặp dữ liệu điểm (Thực tế - Dự đoán) nào hợp lệ.")
        return

    # Mảng numpy để tính toán toán học
    act_arr = np.array(actual_grades)
    pred_arr = np.array(predicted_grades)

    # A. Tính toán các chỉ số tương quan (Correlation)
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        tau, _ = kendalltau(actual_grades, predicted_grades)
        score_spearman_r, _ = spearmanr(actual_grades, predicted_grades)
    else:
        tau, score_spearman_r = 0.0, 0.0

    # 🎯 B. TÍNH TOÁN CÁC CHỈ SỐ ĐỘ LỆCH (DEVIATION METRICS)
    errors = pred_arr - act_arr                     # Độ lệch từng bài (Dự đoán - Thực tế)
    mae = np.mean(np.abs(errors))                    # Mean Absolute Error
    rmse = np.sqrt(np.mean(errors ** 2))             # Root Mean Squared Error
    mean_bias = np.mean(errors)                      # Mean Bias Error (Sai số hệ thống)

    # C. Tính toán thời gian chạy trung bình (Avg Time)
    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    # ---- IN KẾT QUẢ CHUYÊN NGHIỆP CHO KHÓA LUẬN ----
    print("\n" + "="*55)
    print("🎯 BẢNG TỔNG HỢP METRICS ĐÁNH GIÁ TOÀN DIỆN MÔ HÌNH")
    print("="*55)
    print(f"🔹 Số lượng mẫu (Samples)         : {num_samples} bài thi")
    print(f"🔹 Hệ số tương quan Kendall Tau   : {tau:.4f}")
    print(f"🔹 Hệ số tương quan SpearmanR    : {score_spearman_r:.4f}")
    print(f"🔹 Sai số tuyệt đối TB (MAE)       : {mae:.4f} (thang điểm 10)")
    print(f"🔹 Sai số bình phương TB (RMSE)   : {rmse:.4f}")
    print(f"🔹 Độ lệch hệ thống (Mean Bias)   : {mean_bias:.4f} " + ("🔴 (Chấm quá khắt khe)" if mean_bias < 0 else "🟢 (Chấm quá lỏng tay)"))
    print(f"🔹 Thời gian phản hồi trung bình  : {avg_time:.3f} giây / bài thi")
    if skipped_rows > 0:
        print(f"🔸 Số dòng dữ liệu bị bỏ qua     : {skipped_rows}")
    print("="*55 + "\n")

if __name__ == "__main__":
    # 1. Định vị chính xác thư mục output/report_8/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(current_dir, "output", "report_8")
    
    print(f"📂 Bắt đầu quét và tính toán tự động trong thư mục: {report_folder}\n")
    
    # 2. Tìm tất cả các file có đuôi .jsonl trong thư mục report_8
    import glob
    search_pattern = os.path.join(report_folder, "*.jsonl")
    jsonl_files = glob.glob(search_pattern)
    
    if not jsonl_files:
        print(f"❌ Cảnh báo: Không tìm thấy file dữ liệu .jsonl nào trong thư mục report_8.")
    else:
        # Sắp xếp tên file theo thứ tự abc cho đẹp
        jsonl_files.sort()
        
        # 3. Chạy vòng lặp tính metrics cho từng file
        for file_path in jsonl_files:
            analyze_model_performance(file_path)