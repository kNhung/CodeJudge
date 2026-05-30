import json
import warnings
from scipy import stats
from numpy import nanmean

# Danh sách các mô hình cần đánh giá tương ứng với keys trong file
conala_test_cases = [
    "baseline",
    "tranx-annot",
    "best-tranx",
    "best-tranx-rerank",
    "codex",
]

def print_number(kendalltau, pearsonr, spearmanr, length=None):
    """In kết quả ra console theo format chuẩn"""
    print("{:.3f}".format(round(kendalltau, 3)), end=" | ")
    print("{:.3f}".format(round(pearsonr, 3)), end=" | ")
    print("{:.3f}".format(round(spearmanr, 3)), end=" | ")
    if length is not None:
        print(length, end=" | ")
    print("")

def evaluate_jsonl_file(file_path):
    print(f"Đang đánh giá file JSONL: {file_path}")
    data_list = []

    # Đọc file JSONL theo từng dòng
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Lấy dữ liệu từ mảng "data" của mỗi dòng
                if "data" in obj:
                    data_list.extend(obj["data"])
                else:
                    data_list.append(obj)
            except json.JSONDecodeError as e:
                print(f"Bỏ qua lỗi parse ở dòng {line_num}: {e}")

    references = []
    predictions = []

    # Xử lý tính toán dựa trên dữ liệu thu thập được
    for item in data_list:
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
                    pass
            
        # Đảm bảo list hợp lệ trước khi đưa vào tính toán
        if ref_row and pred_row and len(ref_row) == len(pred_row):
            references.append(ref_row)
            predictions.append(pred_row)

    if not references:
        print("Lỗi: Không tìm thấy dữ liệu đánh giá hợp lệ trong file!")
        return

    # Tính toán các chỉ số thống kê
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kendalltau = nanmean([stats.kendalltau(ref, pred).statistic for ref, pred in zip(references, predictions)])
        pearsonr = nanmean([stats.pearsonr(ref, pred).statistic for ref, pred in zip(references, predictions)])
        spearmanr = nanmean([stats.spearmanr(ref, pred).statistic for ref, pred in zip(references, predictions)])

    print("Kendall | Pearson | Spearman | Length")
    print_number(kendalltau, pearsonr, spearmanr, len(references))

if __name__ == "__main__":
    # Điền đường dẫn tới file jsonl bạn vừa đưa
    # Nếu chạy script cùng thư mục với file, bạn chỉ cần để tên file như bên dưới
    file_name = r"C:\Users\ADMIN\Downloads\CodeJudge\evaluation\conala\output\260511_1850_meta-llama-Meta-Llama-3-8B-Instruct_all.jsonl"
    evaluate_jsonl_file(file_name)