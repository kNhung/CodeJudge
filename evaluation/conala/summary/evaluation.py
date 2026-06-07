import csv
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
    per_item_metrics = []

    print("Sample | Item ID | Kendall | Pearson | Spearman | Length")

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
            
            if not ref_row or not pred_row or len(ref_row) != len(pred_row):
                continue

            item_id = item.get("id") or item.get("example_id") or item.get("problem_id") or f"line_{line_idx}"
            length = len(ref_row)

            references.append(ref_row)
            predictions.append(pred_row)

            if length >= 2:
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
                    "length": length,
                })
                print_number(kendalltau, pearsonr, spearmanr, f"{item_id} ({length})")
            else:
                print(f"{line_idx+1} | {item_id} | insufficient data (only {length} matched models)")

    if not per_item_metrics:
        print("Lỗi: Không tìm thấy mẫu nào đủ dữ liệu để tính Kendall/Spearman.")
        return

    # Tính toán các chỉ số tương quan trung bình cho toàn bộ bộ dữ liệu
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kendalltau_mean = nanmean([m["kendall"] for m in per_item_metrics])
        pearsonr_mean = nanmean([m["pearson"] for m in per_item_metrics])
        spearmanr_mean = nanmean([m["spearman"] for m in per_item_metrics])

    print("\nTổng hợp cuối cùng:")
    print("Kendall | Pearson | Spearman | Num samples")
    print_number(kendalltau_mean, pearsonr_mean, spearmanr_mean, len(per_item_metrics))

    # Ghi kết quả per-sample ra file CSV
    if file_path.lower().endswith(".jsonl"):
        csv_path = file_path[:-6] + "_per_sample_metrics.csv"
    else:
        csv_path = file_path + "_per_sample_metrics.csv"

    with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["item_id", "kendall", "pearson", "spearman", "length"])
        for metrics in per_item_metrics:
            writer.writerow([
                metrics["item_id"],
                "{:.6f}".format(metrics["kendall"]),
                "{:.6f}".format(metrics["pearson"]),
                "{:.6f}".format(metrics["spearman"]),
                metrics["length"],
            ])
        writer.writerow([])
        writer.writerow(["SUMMARY", "{:.6f}".format(kendalltau_mean), "{:.6f}".format(pearsonr_mean), "{:.6f}".format(spearmanr_mean), len(per_item_metrics)])

    print(f"Kết quả đã ghi vào file CSV: {csv_path}")

if __name__ == "__main__":
    # Điền tên file JSONL cần đánh giá vào đây
    file_name = "260530_1313_meta-llama-Meta-Llama-3-8B-Instruct_all.jsonl"
    evaluate_jsonl_file(file_name)