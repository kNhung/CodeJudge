import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import BinaryAssessor, IntegratedAssessor, LLMFactory, TaxonomyAssessor
from scipy import stats

from score_with_codejudge import DEFAULT_CSV, DATA_CODE_DIR, get_problem_path, list_code_files, load_rows


HCMUS_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = HCMUS_ROOT / "output"


AUTHOR_TAXONOMY_SYSTEM_PROMPT = """You will be provided with a problem statement, a code snippet that supposedly addresses the problem,
and a catalog of code inconsistencies.
Evaluation Steps:
1. Read the problem statement carefully to identify the functionalities required for the
implementation.
2. Read the code snippet and compare it to the problem statement. Check if the code snippet covers
the required functionalities.
3. Output your answer in a JSON format list.
a) If the code snippet is correct, output: [{"inconsistency": "None", "severity": "Negligible"}].
b) If the code snippet is incorrect, output the identified inconsistencies and their severity
according to the catalog of code inconsistencies. For example: [{"inconsistency": "<inconsistency1>",
"severity": "<severity1>"}, {"inconsistency": "<inconsistency2>", "severity": "<severity2>"}, ...]
Problem: {PROBLEM}
Code Snippet: {CODE}
Taxonomy of Common Inconsistencies:
1. Missing dependency declarations: Negligible
2. No error messages for unexpected input cases: Negligible
3. Inefficiency, unnecessary statements: Negligible
4. Edge case not handled: Small
5. Logic error: Major
6. Function or variable not defined: Fatal
7. Code not completed: Fatal
Evaluation Form:
JSON output (a JSON list only):
[{"inconsistency": "None", "severity": "Negligible"}]"""


def build_whole_exam_inputs(row: Dict[str, str]) -> Tuple[str, str, str]:
    row_id = row["id"].strip()
    language = row.get("language", "").strip() or "C++"
    problem_id = row["problem_id"].strip()

    student_dir = DATA_CODE_DIR / row_id
    problem_path = get_problem_path(problem_id)

    if not student_dir.is_dir():
        raise FileNotFoundError(f"Missing student folder: {student_dir}")
    if not problem_path.is_file():
        raise FileNotFoundError(f"Missing problem file: {problem_path}")

    problem_text = problem_path.read_text(encoding="utf-8", errors="ignore")

    code_files = list_code_files(student_dir)
    if not code_files:
        raise FileNotFoundError(f"No code files found in {student_dir}")

    code_parts: List[str] = []
    for idx, code_file in enumerate(code_files, start=1):
        code_text = code_file.read_text(encoding="utf-8", errors="ignore")
        code_parts.append(f"[Submission {idx} - {code_file.name}]\n```cpp\n{code_text}\n```")

    student_code = "\n\n".join(code_parts)
    return language, problem_text, student_code


def expected_pass(expect_grade: str) -> bool:
    try:
        return float(expect_grade) >= 5.0
    except Exception:
        return False


def _safe_corr(method: str, x: List[float], y: List[float]) -> float:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return float("nan")

    if method == "kendalltau":
        return float(stats.kendalltau(x, y).statistic)
    if method == "spearmanr":
        return float(stats.spearmanr(x, y).statistic)
    if method == "pearsonr":
        return float(stats.pearsonr(x, y).statistic)
    raise ValueError(f"Unknown correlation method: {method}")


def _rmse(x: List[float], y: List[float]) -> float:
    if not x or not y or len(x) != len(y):
        return float("nan")
    mse = sum((a - b) ** 2 for a, b in zip(x, y)) / len(x)
    return math.sqrt(mse)


def run_mode(
    mode: str,
    rows: List[Dict[str, str]],
    output_file: Path,
    llm_client: Any,
    run_both_assessments: bool,
    resume: bool,
    stop_on_rate_limit: bool,
    taxonomy_system_prompt: str,
) -> Dict[str, Any]:
    if mode == "binary":
        assessor = BinaryAssessor(llm_client=llm_client)
    elif mode == "taxonomy":
        if taxonomy_system_prompt:
            assessor = TaxonomyAssessor(llm_client=llm_client, system_prompt=taxonomy_system_prompt)
        else:
            assessor = TaxonomyAssessor(llm_client=llm_client)
    elif mode == "integrated":
        assessor = IntegratedAssessor(
            llm_client=llm_client,
            run_both_assessments=run_both_assessments,
        )
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    processed_ids = set()
    if resume and output_file.exists():
        with output_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    if item.get("id") is not None:
                        processed_ids.add(str(item.get("id")))
                except Exception:
                    continue

    total = 0
    invalid_cnt = 0
    correct_cnt = 0
    rate_limit_hit = False
    # Dataset-style references/predictions (binary pass labels)
    pass_refs: List[float] = []
    pass_preds: List[float] = []
    # Optional grade-level analysis on 10-point scale
    grade_pairs: List[Tuple[float, float]] = []

    file_mode = "a" if resume and output_file.exists() else "w"
    with output_file.open(file_mode, encoding="utf-8") as f:
        for row in rows:
            row_id = str(row.get("id", "")).strip()
            if row_id and row_id in processed_ids:
                continue

            total += 1
            language, problem_statement, student_code = build_whole_exam_inputs(row)
            expected = expected_pass(row.get("expect_grade", ""))

            predicted_pass = False
            predicted_score = None
            result: Dict[str, Any]

            try:
                if mode == "binary":
                    result = assessor.assess(
                        problem_statement=problem_statement,
                        student_code=student_code,
                        language=language,
                    )
                    predicted_pass = bool(result.get("passed", False))
                    predicted_score = 10.0 if predicted_pass else 0.0
                elif mode == "taxonomy":
                    result = assessor.assess(
                        problem_statement=problem_statement,
                        student_code=student_code,
                        reference_code=None,
                        language=language,
                    )
                    predicted_score = float(result.get("final_score", 0))
                    predicted_pass = predicted_score >= 5.0
                else:
                    result = assessor.assess(
                        problem_statement=problem_statement,
                        student_code=student_code,
                        reference_code=None,
                        language=language,
                    )
                    predicted_score = float(result.get("summary", {}).get("score", 0))
                    predicted_pass = predicted_score >= 5.0
            except Exception as e:
                if stop_on_rate_limit and "429" in str(e):
                    rate_limit_hit = True
                    print("Rate limit detected (HTTP 429). Stopping run to allow resume later.")
                    break
                invalid_cnt += 1
                result = {"error": str(e)}

            if predicted_score is not None:
                pass_refs.append(1.0 if expected else 0.0)
                pass_preds.append(1.0 if predicted_pass else 0.0)
                correct_cnt += int(predicted_pass == expected)

            try:
                expected_score_10 = float(row.get("expect_grade", 0))
                if predicted_score is not None:
                    grade_pairs.append((predicted_score, expected_score_10))
            except Exception:
                pass

            record = {
                "mode": mode,
                "id": row.get("id"),
                "student_id": row.get("student_id"),
                "problem_id": row.get("problem_id"),
                "expect_grade": row.get("expect_grade"),
                "expected_pass": expected,
                "predicted_pass": predicted_pass,
                "predicted_score_10": predicted_score,
                "result": result,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            if row_id:
                processed_ids.add(row_id)

    metrics: Dict[str, Any] = {
        "mode": mode,
        "samples": total,
        "output_file": str(output_file),
        "invalid_cnt": invalid_cnt,
        "total_cnt": total,
        "correct_cnt": correct_cnt,
        "processed_unique_ids": len(processed_ids),
        "rate_limit_hit": rate_limit_hit,
    }

    valid_cnt = len(pass_refs)
    if valid_cnt > 0:
        metrics["accuracy"] = correct_cnt / valid_cnt
        metrics["kendalltau"] = round(_safe_corr("kendalltau", pass_refs, pass_preds), 3)
        metrics["spearmanr"] = round(_safe_corr("spearmanr", pass_refs, pass_preds), 3)

    if grade_pairs:
        preds = [p for p, _ in grade_pairs]
        exps = [e for _, e in grade_pairs]
        mae = sum(abs(p - e) for p, e in grade_pairs) / len(grade_pairs)
        metrics["mae_on_10"] = round(mae, 3)
        metrics["rmse_on_10"] = round(_rmse(preds, exps), 3)
        metrics["pearson_grade"] = round(_safe_corr("pearsonr", preds, exps), 3)

    return metrics


def recompute_metrics_from_output(mode: str, output_file: Path) -> Dict[str, Any]:
    """Recompute metrics from the whole JSONL output file."""
    if not output_file.exists():
        return {
            "mode": mode,
            "samples": 0,
            "output_file": str(output_file),
            "invalid_cnt": 0,
            "total_cnt": 0,
            "correct_cnt": 0,
            "processed_unique_ids": 0,
            "rate_limit_hit": False,
        }

    total = 0
    invalid_cnt = 0
    correct_cnt = 0
    processed_ids = set()
    pass_refs: List[float] = []
    pass_preds: List[float] = []
    grade_pairs: List[Tuple[float, float]] = []

    with output_file.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total += 1
            try:
                record = json.loads(line)
            except Exception:
                invalid_cnt += 1
                continue

            row_id = record.get("id")
            if row_id is not None:
                processed_ids.add(str(row_id))

            expected = bool(record.get("expected_pass", False))
            predicted_pass_raw = record.get("predicted_pass", None)
            predicted_score_raw = record.get("predicted_score_10", None)

            try:
                predicted_score = float(predicted_score_raw) if predicted_score_raw is not None else None
            except Exception:
                predicted_score = None

            if isinstance(predicted_pass_raw, bool):
                predicted_pass = predicted_pass_raw
            elif predicted_score is not None:
                predicted_pass = predicted_score >= 5.0
            else:
                predicted_pass = False

            if predicted_score is not None:
                correct_cnt += int(predicted_pass == expected)
                pass_refs.append(1.0 if expected else 0.0)
                pass_preds.append(1.0 if predicted_pass else 0.0)

                try:
                    expected_score_10 = float(record.get("expect_grade", 0))
                    grade_pairs.append((predicted_score, expected_score_10))
                except Exception:
                    pass

    metrics: Dict[str, Any] = {
        "mode": mode,
        "samples": total,
        "output_file": str(output_file),
        "invalid_cnt": invalid_cnt,
        "total_cnt": total,
        "correct_cnt": correct_cnt,
        "processed_unique_ids": len(processed_ids),
        "rate_limit_hit": False,
    }

    valid_cnt = len(pass_refs)
    if valid_cnt > 0:
        metrics["accuracy"] = correct_cnt / valid_cnt
        metrics["kendalltau"] = round(_safe_corr("kendalltau", pass_refs, pass_preds), 3)
        metrics["spearmanr"] = round(_safe_corr("spearmanr", pass_refs, pass_preds), 3)

    if grade_pairs:
        preds = [p for p, _ in grade_pairs]
        exps = [e for _, e in grade_pairs]
        mae = sum(abs(p - e) for p, e in grade_pairs) / len(grade_pairs)
        metrics["mae_on_10"] = round(mae, 3)
        metrics["rmse_on_10"] = round(_rmse(preds, exps), 3)
        metrics["pearson_grade"] = round(_safe_corr("pearsonr", preds, exps), 3)

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HCMUS benchmarking for binary/taxonomy/integrated modes")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--provider", type=str, default="gemini", choices=["openai", "anthropic", "local", "gemini"])
    parser.add_argument("--model", type=str, default="gemini-2.5-flash")
    parser.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=["all", "binary", "taxonomy", "integrated"],
        help="Run one mode or all modes",
    )
    parser.add_argument("--limit", type=int, default=0, help="0 means run full dataset")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--run-both-assessments", action="store_true")
    parser.add_argument("--base-url", type=str, default=None)
    parser.add_argument("--run-name", type=str, default=None, help="Reuse a fixed run folder name for resume")
    parser.add_argument("--resume", action="store_true", help="Append to existing output and skip already processed ids")
    parser.add_argument(
        "--stop-on-rate-limit",
        action="store_true",
        help="Stop run immediately when HTTP 429 is detected (recommended with --resume)",
    )
    parser.add_argument(
        "--metrics-scope",
        type=str,
        default="batch",
        choices=["batch", "file"],
        help="batch: metrics for current run only, file: recompute metrics from full output JSONL",
    )
    parser.add_argument(
        "--taxonomy-system-prompt",
        type=str,
        default="improved",
        choices=["improved", "author"],
        help="Prompt used by taxonomy mode: improved (current core prompt) or author (paper prompt)",
    )
    args = parser.parse_args()

    rows = load_rows(args.csv)
    rows = rows[args.start :]
    if args.limit > 0:
        rows = rows[: args.limit]

    kwargs: Dict[str, Any] = {}
    if args.provider == "local" and args.base_url:
        kwargs["base_url"] = args.base_url

    llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, **kwargs)

    taxonomy_system_prompt = (
        AUTHOR_TAXONOMY_SYSTEM_PROMPT
        if args.taxonomy_system_prompt == "author"
        else None
    )

    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = args.model.replace("/", "-").replace(" ", "-")
    selected_modes = [args.mode] if args.mode != "all" else ["binary", "taxonomy", "integrated"]

    metrics_all: List[Dict[str, Any]] = []
    for mode in selected_modes:
        run_name = args.run_name if args.run_name else f"{ts}_{safe_model}_{mode}"
        run_dir = OUTPUT_ROOT / run_name
        run_dir.mkdir(parents=True, exist_ok=True)

        output_file = run_dir / f"{run_name}.jsonl"
        batch_metrics = run_mode(
            mode=mode,
            rows=rows,
            output_file=output_file,
            llm_client=llm_client,
            run_both_assessments=args.run_both_assessments,
            resume=args.resume,
            stop_on_rate_limit=args.stop_on_rate_limit,
            taxonomy_system_prompt=taxonomy_system_prompt,
        )
        if args.metrics_scope == "file":
            metrics = recompute_metrics_from_output(mode=mode, output_file=output_file)
            metrics["metric_scope"] = "file"
            metrics["last_batch_samples"] = batch_metrics.get("samples", 0)
            metrics["last_batch_rate_limit_hit"] = batch_metrics.get("rate_limit_hit", False)
        else:
            metrics = batch_metrics
            metrics["metric_scope"] = "batch"

        metrics_all.append(metrics)
        print(json.dumps(metrics, ensure_ascii=False))

        # Save per-run metric file for easy tracking
        metric_file = run_dir / f"{run_name}_metrics.json"
        with metric_file.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"Saved metrics: {metric_file}")

    if len(metrics_all) > 1:
        summary_file = OUTPUT_ROOT / f"{ts}_{safe_model}_all_metrics.json"
        with summary_file.open("w", encoding="utf-8") as f:
            json.dump(metrics_all, f, ensure_ascii=False, indent=2)
        print(f"Saved summary: {summary_file}")


if __name__ == "__main__":
    main()
