import json
import os
from hinteval.cores import Hint
# Import chính xác 2 mô hình theo ví dụ Nhung cung cấp
from hinteval.evaluation.readability import MachineLearningBased
from hinteval.evaluation.familiarity import Wikipedia

def run_hinteval_two_metrics(jsonl_path: str):
    print(f"=== Khởi chạy HintEval (Readability & Familiarity) cho: {os.path.basename(jsonl_path)} ===")
    
    # Mảng lưu trữ các object Hint của những câu sinh viên dính lỗi thực tế
    hint_sentences = []
    
    total_samples_count = 0     # Biến đếm tổng số mẫu (khớp với con số 94 trên bảng)
    perfect_responses_count = 0 # Số mẫu sinh viên làm đúng (None) để gán điểm sàn tối đa

    # 1. Đọc file JSONL và bóc tách dữ liệu
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                result_block = data.get("result", {})
                errors_list = result_block.get("errors", [])
                
                for err in errors_list:
                    if isinstance(err, dict):
                        total_samples_count += 1
                        
                        description = err.get("description", "").strip()
                        severity_type = err.get("type", "Negligible")
                        
                        # Phân loại: Bài làm đúng (None) hoặc lỗi không đáng kể (Negligible)
                        if (not description 
                            or description.lower() == "none" 
                            or severity_type == "Negligible"):
                            perfect_responses_count += 1
                        else:
                            # Đóng gói chuỗi phân tích lỗi vào thực thể Hint của hệ thống
                            hint_sentences.append(Hint(description))
                            
            except Exception as e:
                print(f"⚠️ Lỗi đọc dữ liệu tại dòng {idx}: {e}")

    if total_samples_count == 0:
        print("❌ Không tìm thấy dữ liệu mẫu nào.")
        return

    print(f"📊 Thống kê quy mô tập mẫu:")
    print(f"   - Tổng số mẫu thực nghiệm (N)       : {total_samples_count}")
    print(f"   - Số nhận xét lỗi cần chạy mô hình : {len(hint_sentences)}")
    print(f"   - Số nhận xét đúng (Mặc định Max)   : {perfect_responses_count}")

    # Khởi tạo tổng điểm tích lũy cho 2 tiêu chí
    accumulated_readability = 0.0
    accumulated_familiarity = 0.0

    # 2. Thực thi đánh giá bằng HintEval API mẫu
    if hint_sentences:
        print("⏳ Đang khởi tạo các Pipeline NLP và tính toán điểm số...")
        
        # 🔹 A. Chấm điểm Readability (Sử dụng XGBoost giống ví dụ mẫu)
        readability_scorer = MachineLearningBased(method='xgboost')
        readability_scorer.evaluate(hint_sentences)
        
        # 🔹 B. Chấm điểm Familiarity (Sử dụng mô hình Wikipedia Transformer)
        # Sử dụng en_core_web_trf cho các nhận xét bằng tiếng Anh của Gemini
        familiarity_scorer = Wikipedia(spacy_pipeline='en_core_web_trf')
        familiarity_scorer.evaluate(hint_sentences)

        # 3. Trích xuất giá trị từ thuộc tính metrics của từng object Hint
        for sent in hint_sentences:
            # Thu hoạch điểm Readability (Quy đổi lớp: 0 đại diện cho beginner/dễ đọc nhất)
            r_score = 1.0  
            for k, v in sent.metrics.items():
                if 'readability' in k:
                    # Gán điểm tỉ lệ tuyến tính dựa trên class phân loại lớp
                    r_score = 1.0 if v.value == 0 else (0.5 if v.value == 1 else 0.0)
                    break
            accumulated_readability += r_score

            # Thu hoạch điểm Familiarity (Bốc trực tiếp giá trị float từ Wikipedia)
            f_score = 0.0
            for k, v in sent.metrics.items():
                if 'familiarity' in k:
                    f_score = float(v.value)
                    break
            accumulated_familiarity += f_score

    # ============================================================================
    # 4. ÁP DỤNG ĐIỂM SÀN TỐI ĐA (1.0) CHO CÂU ĐÚNG VÀ CHIA TRUNG BÌNH TOÀN BỘ SỐ MẪU
    # ============================================================================
    # Các câu sinh viên viết đúng (None) mặc định đạt 1.0 điểm chất lượng phản hồi
    final_readability = (accumulated_readability + (perfect_responses_count * 1.0)) / total_samples_count
    final_familiarity = (accumulated_familiarity + (perfect_responses_count * 1.0)) / total_samples_count

    print("\n" + "="*45)
    print("🏆 KẾT QUẢ ĐẦY ĐỦ SỐ MẪU (HINTEVAL BENCHMARK) 🏆")
    print("="*45)
    print(f"🔹 Số mẫu thực nghiệm (N)         : {total_samples_count}")
    print(f"🔹 Readability (Độ dễ đọc)        : {round(final_readability, 4)}")
    print(f"🔹 Familiarity (Độ quen thuộc)   : {round(final_familiarity, 4)}")
    print("="*45)

if __name__ == "__main__":
    # Nhung trỏ đúng về file output mới nhất của bạn để chạy nghiệm thu nhé
    TARGET_FILE = "/home/knhung/KLTN/CodeJudge/evaluation/hcmus/output/report_8/260605_author_taxonomy_gemini_2.5_flash.jsonl"
    if os.path.exists(TARGET_FILE):
        run_hinteval_two_metrics(TARGET_FILE)
    else:
        print(f"❌ Không tìm thấy file kết quả mục tiêu tại: {TARGET_FILE}")