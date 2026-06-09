import json
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def extract_errors_from_file(file_path):
    """Hàm bóc tách điểm thực tế và điểm dự đoán để tính độ lệch (Predicted - Actual)"""
    actual_grades = []
    predicted_grades = []

    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "expect_grade" not in data or data["expect_grade"] is None:
                    continue
                
                actual = float(data["expect_grade"])
                
                # Cơ chế bóc điểm dự đoán động
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
            except Exception:
                continue

    if not actual_grades:
        return None

    # Trả về mảng sai số thô: Dự đoán - Thực tế (để thấy được hướng âm/dương của Bias)
    return np.array(predicted_grades) - np.array(actual_grades)

def plot_distributions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(current_dir, "output", "report_8")
    
    # 1. Cấu hình đường dẫn chính xác đến 3 file mô hình của Nhóm
    # Nhung hãy chỉnh sửa lại tên file cho khớp chính xác với tên file trong folder của bạn
    file_map = {
        "Qwen-2.5-Coder-7B": os.path.join(report_folder, "260603_taxonomy_qwen_2.5_coder_7b_instruct.jsonl"), 
        "Gemini-2.5-Flash": os.path.join(report_folder, "260604_taxonomy_gemini_2.5_flash.jsonl"),
        "Llama-3-8B": os.path.join(report_folder, "260604_taxonomy_llama_3_8b.jsonl") 
        # "Qwen-2.5-Coder-7B": os.path.join(report_folder, "260605_author_taxonomy_qwen_2.5_coder_7b_instruct.jsonl"), 
        # "Gemini-2.5-Flash": os.path.join(report_folder, "260605_author_taxonomy_gemini_2.5_flash.jsonl"),
        # "Llama-3-8B": os.path.join(report_folder, "260605_author_taxonomy_llama_3_8b_instruct.jsonl") 
    }

    # Gom dữ liệu để đưa vào DataFrame của Pandas
    all_data = []

    for model_name, file_path in file_map.items():
        errors = extract_errors_from_file(file_path)
        if errors is not None:
            print(f"✅ Đã trích xuất thành công {len(errors)} mẫu từ {model_name}")
            for err in errors:
                all_data.append({"Model": model_name, "Error": err})
        else:
            print(f"⚠️ Cảnh báo: Không tìm thấy hoặc lỗi dữ liệu tại file của {model_name}")

    if not all_data:
        print("❌ Không có dữ liệu hợp lệ để vẽ biểu đồ.")
        return

    df = pd.DataFrame(all_data)

    # 2. Khởi tạo không gian vẽ biểu đồ
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Vẽ biểu đồ mật độ phân phối KDE (Kernel Density Estimate)
    # Bổ sung fill=True để đổ màu dưới đường cong cho trực quan
    sns.kdeplot(
        data=df, 
        x="Error", 
        hue="Model", 
        fill=True, 
        common_norm=False, 
        palette="Set1", 
        alpha=0.25, 
        linewidth=2.5
    )

    # Vẽ đường thẳng đứng nét đứt tại vị trí Error = 0 (Vị trí chấm chuẩn xác tuyệt đối so với thầy cô)
    plt.axvline(x=0.0, color='black', linestyle='--', linewidth=1.5, label='Chấm chuẩn xác (Error = 0)')

    # 3. Định dạng nhãn và tiêu đề (Chuẩn hóa tiếng Anh/tiếng Việt để đưa vào khóa luận)
    plt.title("Phân phối Sai số Điểm số giữa Các Mô hình", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Sai số (Điểm Dự đoán - Điểm Giảng viên)", fontsize=12)
    plt.ylabel("Mật độ phân bổ (Density)", fontsize=12)
    
    # Giới hạn trục X từ -6 đến 4 điểm để tập trung vào vùng phân phối chính
    plt.xlim(-6.0, 4.0)

    plt.tight_layout()
    
    # 4. Lưu biểu đồ thành file ảnh chất lượng cao PNG để chèn vào Word/Slide
    output_image_path = os.path.join(current_dir, "error_distribution_report8.png")
    plt.savefig(output_image_path, dpi=300)
    print(f"\n🏆 Đã vẽ xong! Biểu đồ đã được lưu thành công tại: {output_image_path}")
    plt.show()

if __name__ == "__main__":
    plot_distributions()