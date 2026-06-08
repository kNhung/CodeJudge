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
    data_list = []

    # Thử đọc file
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            # Cách 1: Thử parse toàn bộ file như một file JSON chuẩn
            json_content = json.load(f)
            
            # Xử lý nếu format có dạng {"parameters": ..., "data": [...]}
            if isinstance(json_content, dict) and "data" in json_content:
                data_list = json_content["data"]
            # Xử lý nếu format là một list JSON trực tiếp: [...]
            elif isinstance(json_content, list):
                data_list = json_content
            else:
                # Trường hợp file chỉ là 1 object độc lập (ít gặp)
                data_list = [json_content]

        except json.JSONDecodeError:
            print("Phát hiện định dạng JSON Lines (.jsonl). Đang đọc từng dòng...")
            # Cách 2: Nếu thất bại do có nhiều object không được bọc trong list, thử đọc từng dòng
            f.seek(0) # Quay lại đầu file
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    # Tương tự như trên, kiểm tra cấu trúc của object
                    if "data" in obj:
                        data_list.extend(obj["data"])
                    else:
                        data_list.append(obj)
                except json.JSONDecodeError as e:
                    print(f"Lỗi parse ở dòng {line_num}: {e}")

    # Tiến hành trích xuất dữ liệu
    references = []
    predictions = []

    for item in data_list:
        # Bỏ qua nếu cấu trúc không có trường 'grade' hoặc 'code_gpt_score'
        if not isinstance(item, dict) or "grade" not in item or "code_gpt_score" not in item:
            continue
            
        ref_row = []
        pred_row = []
        
        for case in conala_test_cases:
            if case in item["grade"] and case in item["code_gpt_score"]:
                try:
                    ref_val = float(item["grade"][case])
                    pred_val = float(item["code_gpt_score"][case]["code_gpt_score"])
                    ref_row.append(ref_val)
                    pred_row.append(pred_val)
                except (ValueError, TypeError, KeyError):
                    # Bỏ qua nếu dữ liệu không phải dạng số hoặc bị thiếu
                    pass
            
        # Chỉ thêm vào list nếu có đủ dữ liệu cho test case này
        if ref_row and pred_row and len(ref_row) == len(pred_row):
            references.append(ref_row)
            predictions.append(pred_row)

    if not references:
        print("Lỗi: Không tìm thấy dữ liệu hợp lệ (thiếu 'grade' hoặc 'code_gpt_score') trong file!")
        return

    # Tính toán
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

    print("Kendall | Pearson | Spearman | Length")
    print_number(kendalltau, pearsonr, spearmanr, len(references))

if __name__ == "__main__":
    # Thay thế bằng đường dẫn tuyệt đối tới file JSON của bạn
    file_name = r"C:\Users\ADMIN\Downloads\CodeJudge\evaluation\conala\summary\Qwen2.5-Coder-7B-Instruct-1-4-0.0-sample-0.json"
    evaluate_file(file_name)