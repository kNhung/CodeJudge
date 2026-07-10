import os
import json
import glob
import numpy as np
from scipy.stats import kendalltau, spearmanr, pearsonr
from collections import defaultdict

def calculate_tokens_cost(total_in, total_out, model_name="", filename="", provider=""):
    # Only calculate cost for openrouter provider
    if str(provider).lower() != "openrouter":
        return "x"
        
    if total_in <= 0 and total_out <= 0:
        return "x"
        
    key = ""
    if model_name:
        key = str(model_name).lower()
    elif filename:
        key = str(filename).lower()
        
    if "gemini" in key:
        in_rate = 0.30 / 1000000
        out_rate = 2.50 / 1000000
    elif "llama" in key:
        in_rate = 0.14 / 1000000
        out_rate = 0.14 / 1000000
    elif "qwen" in key:
        in_rate = 0.04 / 1000000
        out_rate = 0.10 / 1000000
    else:
        in_rate = 0.0
        out_rate = 0.0
        
    if in_rate == 0.0 and out_rate == 0.0:
        return "x"
        
    cost_usd = (total_in * in_rate) + (total_out * out_rate)
    return f"${cost_usd:.3f}"

def calculate_conala_json_metrics(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    data = content.get("data", [])
    parameters = content.get("parameters", {})
    elapsed_seconds = parameters.get("elapsed_seconds", 0.0)
    detected_model = parameters.get("model", "")
    detected_provider = parameters.get("provider", "")
    
    sources = ["baseline", "tranx-annot", "best-tranx", "best-tranx-rerank", "codex"]
    
    # AP (average per example)
    per_example_tau = []
    per_example_spearman = []
    per_example_mae = []
    per_example_rmse = []
    per_example_bias = []
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    for item in data:
        grade = item.get("grade", {})
        gpt_score = item.get("code_gpt_score", {})
        
        ex_actuals = []
        ex_preds = []
        
        for src in sources:
            if src in grade and src in gpt_score:
                actual = float(grade[src])
                pred_dict = gpt_score[src]
                pred_val = pred_dict.get("code_gpt_score")
                if pred_val is not None:
                    # In json files, code_gpt_score is out of 1.0, scale to 4.0
                    pred = float(pred_val) * 4.0
                    if pred >= 0:
                        ex_actuals.append(actual)
                        ex_preds.append(pred)
                
                total_input_tokens += int(pred_dict.get("input_tokens", 0) or 0)
                total_output_tokens += int(pred_dict.get("output_tokens", 0) or 0)
        
        if len(ex_actuals) >= 2 and len(set(ex_actuals)) > 1 and len(set(ex_preds)) > 1:
            try:
                tau, _ = kendalltau(ex_actuals, ex_preds)
                spearman, _ = spearmanr(ex_actuals, ex_preds)
                if not np.isnan(tau) and not np.isnan(spearman):
                    per_example_tau.append(tau)
                    per_example_spearman.append(spearman)
            except:
                pass
        
        if len(ex_actuals) > 0:
            ex_actuals = np.array(ex_actuals)
            ex_preds = np.array(ex_preds)
            per_example_mae.append(np.mean(np.abs(ex_preds - ex_actuals)))
            per_example_rmse.append(np.sqrt(np.mean((ex_preds - ex_actuals) ** 2)))
            per_example_bias.append(np.mean(ex_preds - ex_actuals))
            
    n_samples = len(data)
    
    ap_tau = np.mean(per_example_tau) if per_example_tau else 0.0
    ap_spearman = np.mean(per_example_spearman) if per_example_spearman else 0.0
    ap_mae = np.mean(per_example_mae) if per_example_mae else 0.0
    ap_rmse = np.mean(per_example_rmse) if per_example_rmse else 0.0
    ap_bias = np.mean(per_example_bias) if per_example_bias else 0.0
    
    avg_time = elapsed_seconds / n_samples if n_samples > 0 else 0.0
    
    filename = os.path.basename(file_path)
    cost_val = calculate_tokens_cost(total_input_tokens, total_output_tokens, model_name=detected_model, filename=filename, provider=detected_provider)
    
    return {
        "n": n_samples,
        "AP": {"Kendall": ap_tau, "Spearman": ap_spearman, "MAE": ap_mae, "RMSE": ap_rmse, "Bias": ap_bias},
        "avg_time": avg_time,
        "cost": cost_val
    }

def calculate_conala_jsonl_metrics(file_path):
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    per_example_tau = []
    per_example_spearman = []
    per_example_mae = []
    per_example_rmse = []
    per_example_bias = []
    
    runtime_list = []
    total_input_tokens = 0
    total_output_tokens = 0
    detected_model = ""
    detected_provider = ""
    
    for record in records:
        results = record.get("results", [])
        ex_actuals = []
        ex_preds = []
        
        for res_item in results:
            grade_ref = res_item.get("grade_reference")
            if grade_ref is None:
                continue
            
            # extract prediction
            predicted = None
            res_detail = res_item.get("result", {})
            if isinstance(res_detail, dict):
                summary = res_detail.get("summary", {})
                if isinstance(summary, dict) and summary.get("score_on_4") is not None:
                    predicted = float(summary["score_on_4"])
                else:
                    scoring = res_detail.get("scoring", {})
                    if isinstance(scoring, dict) and scoring.get("final_score_on_10") is not None:
                        predicted = float(scoring["final_score_on_10"]) / 10.0 * 4.0
            
            # error filter
            if predicted is None or predicted == -1.0:
                continue
            if isinstance(res_detail, dict) and res_detail.get("scoring", {}).get("has_error"):
                continue
                
            actual = float(grade_ref)
            ex_actuals.append(actual)
            ex_preds.append(predicted)
            
            # runtime and tokens
            runtime = float(res_item.get("runtime_seconds", 0.0))
            if runtime > 0:
                runtime_list.append(runtime)
            usage = res_item.get("usage", {})
            if isinstance(usage, dict):
                total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                total_output_tokens += int(usage.get("output_tokens", 0) or 0)
            
            if not detected_model and record.get("model"):
                detected_model = record.get("model")
            if not detected_provider and record.get("provider"):
                detected_provider = record.get("provider")
                
        if len(ex_actuals) >= 2 and len(set(ex_actuals)) > 1 and len(set(ex_preds)) > 1:
            try:
                tau, _ = kendalltau(ex_actuals, ex_preds)
                spearman, _ = spearmanr(ex_actuals, ex_preds)
                if not np.isnan(tau) and not np.isnan(spearman):
                    per_example_tau.append(tau)
                    per_example_spearman.append(spearman)
            except:
                pass
                
        if len(ex_actuals) > 0:
            ex_actuals = np.array(ex_actuals)
            ex_preds = np.array(ex_preds)
            per_example_mae.append(np.mean(np.abs(ex_preds - ex_actuals)))
            per_example_rmse.append(np.sqrt(np.mean((ex_preds - ex_actuals) ** 2)))
            per_example_bias.append(np.mean(ex_preds - ex_actuals))
            
    n_samples = len(records)
    
    ap_tau = np.mean(per_example_tau) if per_example_tau else 0.0
    ap_spearman = np.mean(per_example_spearman) if per_example_spearman else 0.0
    ap_mae = np.mean(per_example_mae) if per_example_mae else 0.0
    ap_rmse = np.mean(per_example_rmse) if per_example_rmse else 0.0
    ap_bias = np.mean(per_example_bias) if per_example_bias else 0.0
    
    avg_time = np.mean(runtime_list) if runtime_list else 0.0
    
    filename = os.path.basename(file_path)
    cost_val = calculate_tokens_cost(total_input_tokens, total_output_tokens, model_name=detected_model, filename=filename, provider=detected_provider)
    
    return {
        "n": n_samples,
        "AP": {"Kendall": ap_tau, "Spearman": ap_spearman, "MAE": ap_mae, "RMSE": ap_rmse, "Bias": ap_bias},
        "avg_time": avg_time,
        "cost": cost_val
    }

def calculate_hcmus_json_metrics_ap(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
        
    data = content.get("data", [])
    parameters = content.get("parameters", {})
    elapsed_seconds = parameters.get("elapsed_seconds", 0.0)
    detected_model = parameters.get("model", "")
    detected_provider = parameters.get("provider", "")
    
    actuals = []
    preds = []
    total_input_tokens = 0
    total_output_tokens = 0
    for item in data:
        if "expect_grade" in item and "code_gpt_score" in item:
            actual = float(item["expect_grade"])
            gpt_score_dict = item["code_gpt_score"]
            if isinstance(gpt_score_dict, dict) and "submission" in gpt_score_dict:
                submission = gpt_score_dict["submission"]
                if "questions" in submission:
                    total_pred_score = 0.0
                    for q_idx, q_val in submission["questions"].items():
                        q_weight = float(q_val.get("weight", 0.0))
                        q_score = float(q_val.get("code_gpt_score", 0.0))
                        if q_score < 0:
                            q_score = 0.0
                        total_pred_score += q_score * q_weight
                        
                        total_input_tokens += int(q_val.get("input_tokens", 0) or 0)
                        total_output_tokens += int(q_val.get("output_tokens", 0) or 0)
                    actuals.append(actual)
                    preds.append(total_pred_score)
                    
    actuals = np.array(actuals)
    preds = np.array(preds)
    
    if len(actuals) > 0:
        tau, _ = kendalltau(actuals, preds)
        spearman, _ = spearmanr(actuals, preds)
        mae = np.mean(np.abs(preds - actuals))
        rmse = np.sqrt(np.mean((preds - actuals) ** 2))
        bias = np.mean(preds - actuals)
        ap_metrics = {"Kendall": tau, "Spearman": spearman, "MAE": mae, "RMSE": rmse, "Bias": bias}
    else:
        ap_metrics = {"Kendall": 0.0, "Spearman": 0.0, "MAE": 0.0, "RMSE": 0.0, "Bias": 0.0}
        
    avg_time = elapsed_seconds / len(data) if len(data) > 0 else 0.0
    
    filename = os.path.basename(file_path)
    cost_val = calculate_tokens_cost(total_input_tokens, total_output_tokens, model_name=detected_model, filename=filename, provider=detected_provider)
    
    return {
        "n": len(data),
        "AP": ap_metrics,
        "avg_time": avg_time,
        "cost": cost_val
    }

def calculate_hcmus_jsonl_metrics_ap(file_path):
    records_by_id = defaultdict(list)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                records_by_id[data["id"]].append(data)
                
    actual_grades = []
    predicted_grades = []
    runtime_list = []
    total_input_tokens = 0
    total_output_tokens = 0
    detected_model = ""
    detected_provider = ""
    
    for student_id, lines in records_by_id.items():
        expect_grade = None
        for d in lines:
            if "expect_grade" in d and d["expect_grade"] is not None:
                expect_grade = float(d["expect_grade"])
                break
        if expect_grade is None:
            continue
            
        total_pred_score = 0.0
        has_questions = False
        
        for d in lines:
            if d.get("scoring_mode") == "per_question":
                has_questions = True
                res = d.get("result", {})
                if isinstance(res, dict):
                    scoring = res.get("scoring", {})
                    if isinstance(scoring, dict):
                        scaled_score = scoring.get("scaled_score")
                        if scaled_score is not None:
                            total_pred_score += float(scaled_score)
            else:
                runtime = float(d.get("runtime_seconds", 0.0))
                if runtime > 0:
                    runtime_list.append(runtime)
                usage = d.get("usage", {})
                if isinstance(usage, dict):
                    total_input_tokens += int(usage.get("input_tokens", 0) or 0)
                    total_output_tokens += int(usage.get("output_tokens", 0) or 0)
                    
            if not detected_model and d.get("model"):
                detected_model = d.get("model")
            if not detected_provider and d.get("provider"):
                detected_provider = d.get("provider")
                    
        if not has_questions:
            # Fallback to summary score
            for d in lines:
                if d.get("scoring_mode") != "per_question":
                    predicted = None
                    keys = ["predicted_total_score", "exam_total_predicted_score", "final_score", "quality_score"]
                    for k in keys:
                        if k in d and d[k] is not None:
                            predicted = float(d[k])
                            break
                    if predicted is None:
                        res = d.get("result", {})
                        if isinstance(res, dict):
                            for k in keys:
                                if k in res and res[k] is not None:
                                    predicted = float(res[k])
                                    break
                    if predicted is not None and predicted != -1.0:
                        total_pred_score = predicted
                        break
                        
        actual_grades.append(expect_grade)
        predicted_grades.append(total_pred_score)
        
    actual_grades = np.array(actual_grades)
    predicted_grades = np.array(predicted_grades)
    
    if len(actual_grades) > 0:
        tau, _ = kendalltau(actual_grades, predicted_grades)
        spearman, _ = spearmanr(actual_grades, predicted_grades)
        mae = np.mean(np.abs(predicted_grades - actual_grades))
        rmse = np.sqrt(np.mean((predicted_grades - actual_grades) ** 2))
        bias = np.mean(predicted_grades - actual_grades)
        ap_metrics = {"Kendall": tau, "Spearman": spearman, "MAE": mae, "RMSE": rmse, "Bias": bias}
    else:
        ap_metrics = {"Kendall": 0.0, "Spearman": 0.0, "MAE": 0.0, "RMSE": 0.0, "Bias": 0.0}
        
    avg_time = np.mean(runtime_list) if runtime_list else 0.0
    
    filename = os.path.basename(file_path)
    cost_val = calculate_tokens_cost(total_input_tokens, total_output_tokens, model_name=detected_model, filename=filename, provider=detected_provider)
        
    return {
        "n": len(actual_grades),
        "AP": ap_metrics,
        "avg_time": avg_time,
        "cost": cost_val
    }

def print_result_row(file_name, n, metrics, avg_time, cost, lines_list, scale=4):
    mae_str = f"{metrics['MAE']:.3f}"
    rmse_str = f"{metrics['RMSE']:.3f}"
    bias_str = f"{metrics['Bias']:+.3f}"
    if scale == 4:
        row = f"| {file_name:<40} | {n:<3} | {metrics['Kendall']:.3f}  | {metrics['Spearman']:.3f}  | {mae_str:<13} | {rmse_str:<14} | {bias_str:<14} | {avg_time:6.2f}s | {cost:<8} |"
    else:
        row = f"| {file_name:<40} | {n:<3} | {metrics['Kendall']:.3f}  | {metrics['Spearman']:.3f}  | {mae_str:<14} | {rmse_str:<15} | {bias_str:<15} | {avg_time:6.2f}s | {cost:<8} |"
    print(row)
    lines_list.append(row)

def main():
    conala_dir = "/home/knhung/KLTN/CodeJudge/evaluation/output/conala"
    hcmus_dir = "/home/knhung/KLTN/CodeJudge/evaluation/output/hcmus"
    
    out_lines = []
    def log(msg=""):
        print(msg)
        out_lines.append(msg)
        
    log("\n" + "="*132)
    log("📋 CONALA DATASET METRICS")
    log("="*132)
    log(f"| {'File Name':<40} | {'n':<3} | {'Kendall':<8} | {'Spearman':<8} | {'MAE (thang 4)':<13} | {'RMSE (thang 4)':<14} | {'Bias (thang 4)':<14} | {'Time':<7} | {'Cost':<8} |")
    log("|" + "-"*42 + "|" + "-"*5 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*15 + "|" + "-"*16 + "|" + "-"*16 + "|" + "-"*9 + "|" + "-"*10 + "|")
    
    conala_files = sorted(glob.glob(os.path.join(conala_dir, "*")))
    for fp in conala_files:
        if fp.endswith(".Zone.Identifier"):
            continue
        try:
            if fp.endswith(".json"):
                res = calculate_conala_json_metrics(fp)
            elif fp.endswith(".jsonl"):
                res = calculate_conala_jsonl_metrics(fp)
            else:
                continue
                
            fname = os.path.basename(fp)
            print_result_row(fname, res["n"], res["AP"], res["avg_time"], res["cost"], out_lines, scale=4)
        except Exception as e:
            log(f"Error processing {fp}: {e}")
            
    log("\n" + "="*135)
    log("📋 HCMUS DATASET METRICS")
    log("="*135)
    log(f"| {'File Name':<40} | {'n':<3} | {'Kendall':<8} | {'Spearman':<8} | {'MAE (thang 10)':<14} | {'RMSE (thang 10)':<15} | {'Bias (thang 10)':<15} | {'Time':<7} | {'Cost':<8} |")
    log("|" + "-"*42 + "|" + "-"*5 + "|" + "-"*10 + "|" + "-"*10 + "|" + "-"*16 + "|" + "-"*17 + "|" + "-"*17 + "|" + "-"*9 + "|" + "-"*10 + "|")
    
    hcmus_files = sorted(glob.glob(os.path.join(hcmus_dir, "*")))
    for fp in hcmus_files:
        if fp.endswith(".Zone.Identifier"):
            continue
        try:
            if fp.endswith(".json"):
                res = calculate_hcmus_json_metrics_ap(fp)
            elif fp.endswith(".jsonl"):
                res = calculate_hcmus_jsonl_metrics_ap(fp)
            else:
                continue
                
            fname = os.path.basename(fp)
            print_result_row(fname, res["n"], res["AP"], res["avg_time"], res["cost"], out_lines, scale=10)
        except Exception as e:
            log(f"Error processing {fp}: {e}")
            
    # Write to file
    summary_path = "/home/knhung/KLTN/CodeJudge/evaluation/metrics_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(out_lines))
    print(f"\n💾 Saved summary to: {summary_path}")

if __name__ == "__main__":
    main()
