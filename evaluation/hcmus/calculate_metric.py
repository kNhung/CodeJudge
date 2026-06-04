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
                
                # 2. Cơ chế bóc điểm dự đoán ĐỘNG (Xử lý việc lệch cấu trúc giữa các mô hình)
                res = data.get("result", {})
                predicted = None
                
                if isinstance(res, dict):
                    # Thứ tự ưu tiên bóc điểm: Điểm Aggregation > Điểm Final > Điểm Quality
                    predicted = res.get("exam_total_predicted_score") or res.get("final_score") or res.get("quality_score")
                
                # Nếu cấu trúc nằm phẳng ở ngoài (tùy thuộc vào model khác)
                if predicted is None:
                    predicted = data.get("exam_total_predicted_score") or data.get("final_score") or data.get("quality_score")
                
                # Nếu quét hết các tầng vẫn không thấy điểm, gán mặc định bằng 0.0 hoặc bỏ qua
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

    # Tính toán Kendall's Tau và Spearman's R
    # Kiểm tra tránh trường hợp tất cả các điểm dự đoán bị bằng nhau (hệ số biến thiên bằng 0 gây lỗi NaN)
    if len(set(actual_grades)) > 1 and len(set(predicted_grades)) > 1:
        tau, _ = kendalltau(actual_grades, predicted_grades)
        spearman_r, _ = spearmanr(actual_grades, predicted_grades)
    else:
        tau, spearman_r = 0.0, 0.0

    # Tính toán thời gian chạy trung bình (Avg Time)
    avg_time = np.mean(runtime_list) if runtime_list else 0.0

    # ---- IN KẾT QUẢ ĐẸP MẮT ----
    print("\n" + "="*50)
    print("🎯 BẢNG TỔNG HỢP METRICS ĐÁNH GIÁ MÔ HÌNH")
    print("="*50)
    print(f"🔹 Số lượng mẫu (Samples)       : {num_samples} bài thi")
    print(f"🔹 Hệ số tương quan Kendall Tau : {tau:.4f}")
    print(f"🔹 Hệ số tương quan SpearmanR  : {spearman_r:.4f}")
    print(f"🔹 Thời gian phản hồi trung bình: {avg_time:.3f} giây / bài thi")
    if skipped_rows > 0:
        print(f"🔸 Số dòng summary bị bỏ qua   : {skipped_rows}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Lấy thư mục cha của file compute_metric.py (chính là thư mục hcmus)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Nối với thư mục output/kaggle/
    # TARGET_FILE = os.path.join(current_dir, "output", "report_8", "260604_taxonomy_gemini_2.5_flash.jsonl")
    TARGET_FILE = os.path.join(current_dir, "output", "260604_taxonomy_gemini_2.5_flash.jsonl")
    analyze_model_performance(TARGET_FILE)