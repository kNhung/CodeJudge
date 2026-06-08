import csv
import json
import numpy as np
from scipy import stats
from numpy import nanmean
import warnings

# Danh sách các mô hình cần đánh giá tương ứng với keys trong file JSON
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

def evaluate_file(file_path):
    print(f"Đang đánh giá file: {file_path}")
    
    # Đọc file JSON dữ liệu kết quả chấm của GPT
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            json_content = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Lỗi: Không thể parse file JSON. Chi tiết: {e}")
            return

    # Lấy danh sách data (hỗ trợ cả cấu trúc bọc trong key "data" hoặc danh sách gốc)
    if isinstance(json_content, dict) and "data" in json_content:
        data_entries = json_content["data"]
    elif isinstance(json_content, list):
        data_entries = json_content
    else:
        print("Lỗi: Định dạng file JSON không hợp lệ (Phải là List hoặc Dict chứa key 'data')")
        return

    # Khởi tạo ma trận chứa điểm của nhãn gốc (ground truth) và điểm dự đoán của GPT
    references = []  # Lưu điểm từ trường 'grade'
    predictions = [] # Lưu điểm trích xuất từ 'parsed_comparison' bên trong 'code_gpt_score'
    per_item_metrics = []

    print("Sample | Item ID | Kendall | Pearson | Spearman | Length")

    for idx, item in enumerate(data_entries):
        # Kiểm tra sự tồn tại của các trường dữ liệu chấm điểm bắt buộc
        if "grade" not in item or "code_gpt_score" not in item:
            continue
            
        ref_row = []
        pred_row = []
        
        for model in conala_test_cases:
            # Lấy điểm nhãn gốc (Ground Truth)
            if model in item["grade"]:
                ref_val = item["grade"][model]
            else:
                continue
                
            # Lấy điểm dự đoán được GPT phân tách (Parsed GPT Score)
            if model in item["code_gpt_score"] and "parsed_comparison" in item["code_gpt_score"][model]:
                try:
                    # Chuyển đổi giá trị parsed_comparison dạng chuỗi thành số thực/số nguyên
                    raw_score = item["code_gpt_score"][model]["parsed_comparison"]
                    pred_val = float(raw_score)
                    
                    # Nếu thang điểm GPT trả về là 0-100, chuẩn hóa về thang điểm 0-4 tương ứng với nhãn gốc
                    # (Ví dụ: 100 -> 4.0, 60 -> 2.4, 0 -> 0.0)
                    if pred_val > 4.0:
                        pred_val = (pred_val / 100.0) * 4.0
                        
                except (ValueError, TypeError):
                    # Bỏ qua nếu dữ liệu điểm parsed_comparison bị lỗi định dạng không quy đổi được
                    continue
            else:
                continue
                
            ref_row.append(ref_val)
            pred_row.append(pred_val)
            
        # Chỉ tiến hành thêm vào tập tính toán nếu test case này có đầy đủ điểm đối sánh cho các mô hình
        if ref_row and pred_row and len(ref_row) == len(pred_row):
            references.append(ref_row)
            predictions.append(pred_row)

            # Tạo item_id thuận tiện để xuất báo cáo từng mẫu
            item_id = item.get("id") or item.get("example_id") or item.get("problem_id") or f"item_{idx}"
            if len(ref_row) >= 2:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    kendalltau = stats.kendalltau(ref_row, pred_row).statistic
                    pearsonr = stats.pearsonr(ref_row, pred_row).statistic
                    spearmanr = stats.spearmanr(ref_row, pred_row).statistic

                per_item_metrics.append({
                    "item_id": item_id,
                    "kendall": kendalltau,
                    "pearson": pearsonr,
                    "spearman": spearmanr,
                    "length": len(ref_row),
                })
                print_number(kendalltau, pearsonr, spearmanr, f"{item_id} ({len(ref_row)})")
            else:
                print(f"{idx+1} | {item_id} | insufficient data (only {len(ref_row)} matched models)")

    if not references:
        print("Lỗi: Không tìm thấy cặp dữ liệu đối sánh hợp lệ ('grade' & 'parsed_comparison') trong file!")
        return

    # Tính toán các chỉ số tương quan (Correlation Metrics)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Tính trung bình chỉ số tương quan trên từng dòng (từng câu test case)
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

    # In kết quả ra màn hình dạng bảng giống test2.py
    print("Kendall | Pearson | Spearman | Length")
    print_number(kendalltau, pearsonr, spearmanr, len(references))

    # Ghi kết quả per-sample ra file CSV nếu có ít nhất một mẫu hợp lệ
    if per_item_metrics:
        if file_path.lower().endswith('.jsonl'):
            csv_path = file_path[:-6] + '_per_sample_metrics.csv'
        else:
            csv_path = file_path + '_per_sample_metrics.csv'

        with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['item_id', 'kendall', 'pearson', 'spearman', 'length'])
            for metrics in per_item_metrics:
                writer.writerow([
                    metrics['item_id'],
                    '{:.6f}'.format(metrics['kendall']),
                    '{:.6f}'.format(metrics['pearson']),
                    '{:.6f}'.format(metrics['spearman']),
                    metrics['length'],
                ])
            writer.writerow([])
            writer.writerow(['SUMMARY', '{:.6f}'.format(kendalltau), '{:.6f}'.format(pearsonr), '{:.6f}'.format(spearmanr), len(per_item_metrics)])

        print(f"Kết quả per-sample đã ghi vào file CSV: {csv_path}")
    else:
        print("Chú ý: Không có mẫu nào đủ dữ liệu để ghi per-sample CSV.")

if __name__ == "__main__":
    # Điền đường dẫn file JSON của bạn vào đây để chạy kiểm tra
    file_name = "Qwen2.5-Coder-7B-Instruct-2-0-2-0.0-sample-0.json"
    evaluate_file(file_name)