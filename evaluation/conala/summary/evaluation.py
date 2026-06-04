import json
import numpy as np
from scipy import stats
from numpy import nanmean
import warnings

# Danh sách các mô hình cần đánh giá tương ứng với trường "source" trong file JSONL
conala_test_cases = [
    "baseline",
    "tranx-annot",
    "best-tranx",
    "best-tranx-rerank",
    "codex",
]

def print_number(kendalltau, pearsonr, spearmanr, length=None):
    """Hàm in kết quả format ra bảng console"""
    print("{:.3f}".format(round(kendalltau, 3)), end=" | ")
    print("{:.3f}".format(round(pearsonr, 3)), end=" | ")
    print("{:.3f}".format(round(spearmanr, 3)), end=" | ")
    if length is not None:
        print(length, end=" | ")
    print("")

def evaluate_jsonl_file(file_path):
    print(f"Đang đánh giá file JSONL: {file_path}")
    
    references = []  # Lưu điểm nhãn gốc (grade_reference)
    predictions = [] # Lưu điểm dự đoán từ hệ thống (score_on_4)

    # Đọc file theo từng dòng (đặc trưng của định dạng .jsonl)
    with open(file_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
                
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Cảnh báo: Bỏ qua dòng {line_idx} do lỗi định dạng JSON: {e}")
                continue

            # Kiểm tra xem có danh sách kết quả chấm "results" không
            if "results" not in item:
                continue

            # Chuyển đổi list kết quả thành dictionary để dễ tra cứu theo mô hình (source)
            row_scores = {res["source"]: res for res in item["results"] if "source" in res}
            
            ref_row = []
            pred_row = []
            
            for model in conala_test_cases:
                if model in row_scores:
                    res_obj = row_scores[model]
                    
                    # Lấy điểm nhãn gốc (Ground Truth)
                    ref_val = res_obj.get("grade_reference")
                    
                    # Lấy điểm dự đoán của mô hình chấm tự động (mặc định lấy trường score_on_4)
                    pred_val = None
                    if "result" in res_obj and "summary" in res_obj["result"]:
                        pred_val = res_obj["result"]["summary"].get("score_on_4")
                    
                    if ref_val is not None and pred_val is not None:
                        try:
                            ref_row.append(float(ref_val))
                            pred_row.append(float(pred_val))
                        except (ValueError, TypeError):
                            continue
            
            # Chỉ thêm cặp dữ liệu đối sánh nếu thu thập đủ số lượng mô hình của dòng đó
            if ref_row and pred_row and len(ref_row) == len(pred_row):
                references.append(ref_row)
                predictions.append(pred_row)

    if not references:
        print("Lỗi: Không tìm thấy dữ liệu đối sánh hợp lệ ('grade_reference' & 'score_on_4') trong file!")
        return

    # Tính toán các chỉ số tương quan (Correlation Metrics)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        kendalltau = nanmean([
            stats.kendalltau(ref, pred).statistic 
            for ref, pred in zip(references, predictions)
        ])
        pearsonr = nanmean([
            stats.pearsonr(ref, pred).statistic 
            for ref, pred in zip(references, predictions)
        ])
        spearmanr = nanmean([
            stats.spearmanr(ref, pred).statistic 
            for ref, pred in zip(references, predictions)
        ])

    # In kết quả định dạng bảng trực quan
    print("Kendall | Pearson | Spearman | Length")
    print_number(kendalltau, pearsonr, spearmanr, len(references))

if __name__ == "__main__":
    # Điền tên file JSONL cần đánh giá vào đây
    file_name = "260602_1839_Qwen-Qwen2.5-Coder-7B-Instruct_all.jsonl"
    evaluate_jsonl_file(file_name)