import json
import os

def fix_and_minus_penalty(file_path, output_path):
    print(f"🛠️ Đang quét và cấn trừ điểm phạt trực tiếp trên file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Lỗi: Không tìm thấy file nguồn.")
        return

    fixed_lines = []
    count_fixed = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                res = data.get("result", {})
                
                # Chỉ xử lý nếu trường result là một Dictionary và có chứa danh sách errors
                if isinstance(res, dict) and "errors" in res:
                    errors_list = res.get("errors", [])
                    
                    # 1. Tính toán tổng điểm phạt từ mảng errors thực tế của Qwen
                    total_penalty = 0.0
                    for err in errors_list:
                        if isinstance(err, dict):
                            err_type = err.get("type", "")
                            if err_type == "Fatal":
                                total_penalty += 10.0
                            elif err_type == "Major":
                                total_penalty += 5.0
                            elif err_type == "Small":
                                total_penalty += 0.5
                            elif err_type == "Negligible":
                                total_penalty += 0.0
                    
                    # 2. Nếu có dính điểm phạt, tiến hành ép cấu trúc trừ điểm
                    if total_penalty < 0:
                        # Điểm chuẩn = Trần 10.0 trừ đi điểm phạt, chặn dưới ở mức 0.0
                        corrected_score = max(0.0, 10.0 - total_penalty)
                        
                        # Chỉ gán lại nếu điểm hiện tại đang bị sai (bằng 10 hoặc bằng 8 mà nhận xét trừ sạch)
                        raw_quality = float(res.get("quality_score", 10.0))
                        if raw_quality != corrected_score:
                            res["quality_score"] = corrected_score
                            res["final_score"] = corrected_score
                            res["exam_total_predicted_score"] = corrected_score
                            data["result"] = res
                            count_fixed += 1
                            print(f"   ✓ Dòng {idx} (ID: {data.get('id')}): Đã ép trừ điểm phạt {total_penalty} -> Điểm mới: {corrected_score}")
                
                fixed_lines.append(json.dumps(data, ensure_ascii=False))
            except Exception as e:
                print(f"⚠️ Lỗi xử lý tại dòng {idx}: {e}")
                fixed_lines.append(line)

    # 3. Ghi đè lại kết quả sạch sẽ vào file mới hoặc ghi đè file cũ
    with open(output_path, 'w', encoding='utf-8') as f_out:
        for fl in fixed_lines:
            f_out.write(fl + "\n")
            
    print(f"\n✅ Đã hoàn thành! Đã sửa lỗi điểm cho {count_fixed} dòng dữ liệu.")
    print(f"💾 File kết quả mới sạch lỗi đã được lưu tại: {output_path}")

if __name__ == "__main__":
    # Lấy thư mục cha của file compute_metric.py (chính là thư mục hcmus)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Nối với thư mục output/kaggle/
    INPUT = os.path.join(current_dir, "output", "kaggle", "260603_taxonomy_qwen_2.5_coder_7b_instruct.jsonl")
    OUTPUT = os.path.join(current_dir, "output", "kaggle", "260603_taxonomy_qwen_2.5_coder_7b_instruct_FIXED.jsonl")
    
    fix_and_minus_penalty(INPUT, OUTPUT)