import json
import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau

def get_true_grade(grade_ref):
    # Nếu grade_reference là dict (nhiều người chấm), lấy trung bình
    if isinstance(grade_ref, dict):
        return sum(grade_ref.values()) / len(grade_ref)
    # Nếu là số hoặc chuỗi có thể ép kiểu
    return float(grade_ref)

def calculate_metrics(group_records):
    if not group_records:
        return {}
    
    y_true = np.array([r['true'] for r in group_records])
    y_pred = np.array([r['pred'] for r in group_records])
    
    n = len(y_true)
    avg_true = np.mean(y_true)
    avg_pred = np.mean(y_pred)
    
    # Tính MAE và RMSE
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    
    # Exact Match Rate (Làm tròn để tránh lỗi số học dấu phẩy động)
    exact_matches = np.sum(np.round(y_true, 2) == np.round(y_pred, 2))
    exact_match_rate = exact_matches / n
    
    # Tính toán hệ số tương quan (Chỉ tính được khi có >1 sample và phương sai > 0)
    if n > 1 and np.var(y_true) > 0 and np.var(y_pred) > 0:
        pearson_val = pearsonr(y_true, y_pred)[0]
        spearman_val = spearmanr(y_true, y_pred)[0]
        kendall_val = kendalltau(y_true, y_pred)[0]
    else:
        pearson_val = float('nan')
        spearman_val = float('nan')
        kendall_val = float('nan')
        
    return {
        "samples": n,
        "grade_scale": 4.0,
        "average_true_grade": round(float(avg_true), 4),
        "average_predicted_scaled": round(float(avg_pred), 4),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "pearson": round(float(pearson_val), 4) if not np.isnan(pearson_val) else float('nan'),
        "spearman": round(float(spearman_val), 4) if not np.isnan(spearman_val) else float('nan'),
        "kendalltau": round(float(kendall_val), 4) if not np.isnan(kendall_val) else float('nan'),
        "exact_match_rate": round(float(exact_match_rate), 4)
    }

def main():
    file_path = r'C:\Users\ADMIN\Downloads\CodeJudge\evaluation\conala\summary\260409_0841_gemini-2.5-flash_all.jsonl'
    output_path = 'metrics_result.json'  # Tên file đầu ra bạn muốn lưu
    records = []
    
    # Đọc file JSONL
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            
            # Lưu ý: Code này giả định bạn truyền file JSONL chuẩn, không chứa các tag bị lẫn vào trong nội dung.
            data = json.loads(line)
            
            source = data.get('source', 'unknown')
            true_grade = get_true_grade(data.get('grade_reference', 0))
            
            # Lấy điểm mô hình chấm trên thang 4
            pred_grade = data.get('result', {}).get('summary', {}).get('score_on_4', 0)
            
            records.append({
                'source': source,
                'true': true_grade,
                'pred': pred_grade
            })
            
    # Gom nhóm theo 'source'
    sources = set(r['source'] for r in records)
    final_output = {}
    
    for src in sources:
        group = [r for r in records if r['source'] == src]
        final_output[src] = calculate_metrics(group)
        
    # Thêm nhóm 'all' (tổng hợp tất cả)
    final_output['all'] = calculate_metrics(records)
    
    # Ghi kết quả ra file JSON
    with open(output_path, 'w', encoding='utf-8') as out_f:
        json.dump(final_output, out_f, indent=2)
        
    print(f"Đã ghi kết quả thành công ra file: {output_path}")

if __name__ == "__main__":
    main()