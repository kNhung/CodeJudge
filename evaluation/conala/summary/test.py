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

def evaluate_json_file(file_path):
    """Đánh giá file JSON (không phải JSONL)"""
    print(f"Đang đánh giá file JSON: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return
    
    data_list = data.get("data", [])
    if not data_list:
        print("Lỗi: Không tìm thấy 'data' trong file JSON!")
        return
    
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
        kendalltau_vals = [stats.kendalltau(ref, pred).statistic for ref, pred in zip(references, predictions)]
        pearsonr_vals = [stats.pearsonr(ref, pred).statistic for ref, pred in zip(references, predictions)]
        spearmanr_vals = [stats.spearmanr(ref, pred).statistic for ref, pred in zip(references, predictions)]
        
        kendalltau = nanmean(kendalltau_vals)
        pearsonr = nanmean(pearsonr_vals)
        spearmanr = nanmean(spearmanr_vals)

    print("\n" + "="*80)
    print("KẾT QUẢ ĐÁNH GIÁ PERFORMANCE")
    print("="*80)
    print(f"Số lượng mẫu đánh giá: {len(references)}")
    print(f"\nKendall Tau    | Pearson r  | Spearman r")
    print_number(kendalltau, pearsonr, spearmanr)
    print("\n" + "-"*80)
    print("CHI TIẾT THỐNG KÊ:")
    print("-"*80)
    print(f"Kendall Tau:   {kendalltau:.6f} (min: {min(kendalltau_vals):.6f}, max: {max(kendalltau_vals):.6f})")
    print(f"Pearson r:     {pearsonr:.6f} (min: {min(pearsonr_vals):.6f}, max: {max(pearsonr_vals):.6f})")
    print(f"Spearman r:    {spearmanr:.6f} (min: {min(spearmanr_vals):.6f}, max: {max(spearmanr_vals):.6f})")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Đánh giá file JSON
    json_file = r"C:\Users\ADMIN\Downloads\CodeJudge\evaluation\conala\summary\260531_0951_Qwen-Qwen2.5-Coder-7B-Instruct_all.jsonl"
    evaluate_json_file(json_file)
    
    print("\n" + "#"*80)
    print("# Để đánh giá file JSONL, bạn có thể dùng lệnh bên dưới:")
    print("#"*80)
    # Hoặc đánh giá file JSONL
    # jsonl_file = r"C:\Users\ADMIN\Downloads\CodeJudge\evaluation\conala\output\260511_1850_meta-llama-Meta-Llama-3-8B-Instruct_all.jsonl"
    # evaluate_jsonl_file(jsonl_file)