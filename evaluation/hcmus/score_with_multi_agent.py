import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv()

from codejudge.core.compiler_helper import merge_folder_code


HCMUS_ROOT = Path(__file__).resolve().parent
PROBLEMS_DIR = HCMUS_ROOT / "problems"
DATA_CODE_DIR = HCMUS_ROOT / "data_code"
DEFAULT_CSV = HCMUS_ROOT / "hcmus_dataset.csv"

def build_default_output_path(model_name: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    return HCMUS_ROOT / "output" / f"{ts}_{safe_model}_multi_agent.jsonl"

def split_questions(problem_text: str) -> List[str]:
    """Split a problem file into question blocks, e.g. Cau/Bai 1,2,3."""
    parts = re.split(r"(?=^\s*(?:C\S*u|B\S*i)\s*\d+)", problem_text, flags=re.MULTILINE)
    blocks = [p.strip() for p in parts if p.strip()]
    return blocks if blocks else [problem_text.strip()]

def parse_question_max(question_text: str) -> Optional[float]:
    """Extract per-question max score from heading, e.g. '(3đ)' or '(2.5 điểm)'."""
    patterns = [
        r"\((\d+(?:[\.,]\d+)?)\s*đ\)",
        r"\((\d+(?:[\.,]\d+)?)\s*điểm\)",
        r"\b(\d+(?:[\.,]\d+)?)\s*đ\b",
        r"\b(\d+(?:[\.,]\d+)?)\s*điểm\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, question_text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).replace(",", ".")
            try:
                value = float(raw)
                if value > 0:
                    return value
            except ValueError:
                continue
    return None

def list_code_files(student_dir: Path) -> List[Path]:
    """Sort Bai01/Bai02/... files or directories in stable numeric order."""
    def key_fn(path: Path):
        m = re.search(r"(\d+)", path.name)
        return int(m.group(1)) if m else 10**9

    entries = []
    if student_dir.is_dir():
        for p in student_dir.iterdir():
            if p.is_file() and p.suffix.lower() in {".cpp", ".cc", ".cxx", ".c", ".py"}:
                entries.append(p)
            elif p.is_dir() and not p.name.startswith("."):
                entries.append(p)
                
    return sorted(entries, key=key_fn)

def get_problem_path(problem_id: str) -> Path:
    return PROBLEMS_DIR / f"{problem_id}.txt"

def load_rows(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"id", "language", "problem_id", "student_id", "expect_grade"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
        return list(reader)

def load_processed_ids(output_file: Path) -> set[str]:
    processed_ids: set[str] = set()
    if not output_file.exists():
        return processed_ids

    with output_file.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue

            item_id = item.get("id")
            if item_id is not None:
                processed_ids.add(str(item_id))
    return processed_ids

def evaluate_row(
    row: Dict[str, str],
    assessor: Optional[Any],
    dry_run: bool,
    config_data: Optional[Dict[str, Any]] = None,
    parallel_factors: bool = False,
    max_factor_workers: int = 5,
) -> List[Dict[str, object]]:
    row_id = row["id"].strip()
    problem_id = row["problem_id"].strip()
    language = row["language"].strip()

    student_dir = DATA_CODE_DIR / row_id
    problem_path = get_problem_path(problem_id)

    if not student_dir.is_dir():
        return [{"id": row_id, "problem_id": problem_id, "error": f"Missing student folder: {student_dir}"}]
    if not problem_path.is_file():
        return [{"id": row_id, "problem_id": problem_id, "error": f"Missing problem file: {problem_path}"}]

    problem_text = problem_path.read_text(encoding="utf-8", errors="ignore")
    code_files = list_code_files(student_dir)

    if not code_files:
        return [{"id": row_id, "problem_id": problem_id, "error": f"No code files found in {student_dir}"}]

    questions = split_questions(problem_text)
    results: List[Dict[str, object]] = []
    per_question_results: List[Dict[str, object]] = []

    # Get problem level config if any
    problem_config = {}
    if config_data:
        problem_config = config_data.get(problem_id, {})

    # Map each student code file (sorted numerically) to the matching split question block
    for idx, code_file in enumerate(code_files, start=1):
        if idx > len(questions):
            break
            
        if code_file.is_dir():
            code_text = merge_folder_code(code_file, language)
            source_path_val = str(code_file)
        else:
            code_text = code_file.read_text(encoding="utf-8", errors="ignore")
            source_path_val = str(code_file)
            
        question_text = questions[idx - 1]
        question_max = parse_question_max(question_text)
        if question_max is None:
            question_max = 10.0
        question_name = question_text.splitlines()[0].strip()

        item: Dict[str, object] = {
            "id": row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "question_index": idx,
            "question_name": question_name,
            "code_file": code_file.name,
            "language": language,
            "question_max": question_max,
            "scoring_mode": "per_question"
        }

        if dry_run:
            item["status"] = "dry_run"
            item["question_preview"] = question_text[:120]
            results.append(item)
            per_question_results.append(item)
            continue

        started_at = time.perf_counter()
        
        # Extract question level override parameters
        question_config = problem_config.get(str(idx), {})
        pre_factors = question_config.get("pre_extracted_factors")
        f_weights = question_config.get("factor_weights")
        s_penalties = question_config.get("syntax_penalties")

        # Run MultiAgentAssessor
        assert assessor is not None
        assessment_result = assessor.assess(
            question_text=question_text,
            student_code=code_text,
            language=language,
            question_max=question_max,
            pre_extracted_factors=pre_factors,
            factor_weights=f_weights,
            syntax_penalties=s_penalties,
            source_path=source_path_val,
            parallel_factors=parallel_factors,
            max_factor_workers=max_factor_workers,
        )
        
        item["runtime_seconds"] = round(time.perf_counter() - started_at, 6)
        item["parallel_factors"] = parallel_factors
        item["result"] = assessment_result
        
        # Compatibility root-level scores
        item["final_score"] = assessment_result.get("final_score")
        item["quality_score"] = assessment_result.get("quality_score")
        item["total_penalty"] = assessment_result.get("total_penalty")
        
        results.append(item)
        per_question_results.append(item)

    if per_question_results and not dry_run:
        total_max = 0.0
        total_predicted = 0.0
        all_suggestions = []
        total_input_tokens = 0
        total_output_tokens = 0
        any_error = False

        for q_res in per_question_results:
            qmax = q_res.get("question_max")
            if isinstance(qmax, (int, float)):
                total_max += qmax

            res = q_res.get("result", {})
            score = res.get("final_score")
            if score == -1 or score == -1.0:
                any_error = True
            elif isinstance(score, (int, float)):
                total_predicted += score

            q_suggs = res.get("suggestions", [])
            if q_suggs:
                all_suggestions.append(f"--- Gợi ý {q_res.get('question_name')}: ---")
                all_suggestions.extend(q_suggs)

            # Accumulate token usage
            q_usage = res.get("usage", {})
            if isinstance(q_usage, dict):
                total_input_tokens += q_usage.get("input_tokens", 0)
                total_output_tokens += q_usage.get("output_tokens", 0)

        summary_item: Dict[str, object] = {
            "id": row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "language": language,
            "record_type": "exam_summary",
            "questions_count": len(per_question_results),
            "max_total_score": round(total_max, 4),
            "predicted_total_score": -1.0 if any_error else round(total_predicted, 4),
            "has_error": any_error,
            "suggestions": all_suggestions,
            "runtime_seconds": round(
                sum(float(item.get("runtime_seconds", 0.0) or 0.0) for item in per_question_results),
                6,
            ),
            "usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens
            },
            "question_details": [
                {
                    "question_index": item.get("question_index"),
                    "question_max": item.get("question_max"),
                    "question_name": item.get("question_name"),
                    "score_on_10": item.get("result", {}).get("scoring", {}).get("final_score_on_10"),
                    "score_scaled": item.get("result", {}).get("scoring", {}).get("scaled_score"),
                }
                for item in per_question_results
            ]
        }
        results.append(summary_item)

    return results

def main() -> None:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout
    )
    parser = argparse.ArgumentParser(description="Score HCMUS dataset using Multi-Agent Assessor")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to hcmus_dataset.csv")
    parser.add_argument("--provider", type=str, default="openai", help="LLM provider")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model name")
    parser.add_argument("--output", type=Path, default=None, help="Output JSONL file")
    parser.add_argument("--run-name", type=str, default=None, help="Optional run name to include in output filename")
    parser.add_argument("--resume", action="store_true", help="Append to existing output and skip rows whose id already exists")
    parser.add_argument("--limit", type=int, default=0, help="Only process first N rows (0 means all)")
    parser.add_argument("--start", type=int, default=0, help="Start index in CSV rows")
    parser.add_argument("--dry-run", action="store_true", help="Do not call LLM; only run compiler and validate layout")
    parser.add_argument("--config", type=Path, default=None, help="Path to JSON configuration file containing pre-extracted factors and weights")
    parser.add_argument("--parallel-factors", action="store_true", default=False,
                        help="Grade each factor in a separate parallel LLM call")
    parser.add_argument("--max-factor-workers", type=int, default=5,
                        help="Max worker threads when --parallel-factors is set")
    parser.add_argument("--no-cache", action="store_true", default=False,
                        help="Disable LLM request cache (recommended for fair A/B timing)")

    args = parser.parse_args()
    if args.output is None:
        args.output = (HCMUS_ROOT / "output" / f"{args.run_name}.jsonl") if args.run_name else build_default_output_path(args.model)

    rows = load_rows(args.csv)

    if args.start < 0:
        raise ValueError("--start must be >= 0")

    rows = rows[args.start :]
    if args.limit > 0:
        rows = rows[: args.limit]

    processed_ids = load_processed_ids(args.output) if args.resume else set()

    # Load custom config if provided
    config_data = {}
    if args.config:
        if args.config.is_file():
            with args.config.open("r", encoding="utf-8") as config_f:
                config_data = json.load(config_f)
            print(f"Loaded custom HITL config from: {args.config}")
        else:
            print(f"Warning: Config file {args.config} not found.")

    assessor = None
    if not args.dry_run:
        from codejudge.core import MultiAgentAssessor, LLMFactory
        llm_client = LLMFactory.create(
            provider=args.provider,
            model_name=args.model,
            use_cache=not args.no_cache,
        )
        assessor = MultiAgentAssessor(llm_client=llm_client)

    mode = "PARALLEL factors" if args.parallel_factors else "BATCH factors (1 call)"
    cache_mode = "off" if args.no_cache else "on"
    print(f"Mode: MULTI-AGENT / {mode} (Provider: {args.provider}, Model: {args.model}, cache={cache_mode})")
    print(f"Scoring {len(rows)} exam rows -> {args.output}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    file_mode = "a" if args.resume and args.output.exists() else "w"
    start_total = time.perf_counter()
    
    with args.output.open(file_mode, encoding="utf-8") as f:
        for row_idx, row in enumerate(rows, start=1):
            row_id = str(row.get("id", "")).strip()
            if args.resume and row_id and row_id in processed_ids:
                continue

            print(f"[{row_idx}/{len(rows)}] Scoring exam id={row_id} ...")
            try:
                items = evaluate_row(
                    row=row,
                    assessor=assessor,
                    dry_run=args.dry_run,
                    config_data=config_data,
                    parallel_factors=args.parallel_factors,
                    max_factor_workers=args.max_factor_workers,
                )
            except Exception as e:
                print(f"Error evaluating row {row_id}: {e}")
                raise

            for item in items:
                # Add run-level metadata
                item["model"] = args.model
                item["provider"] = args.provider
                item["parallel_factors"] = args.parallel_factors
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1

            if args.resume and row_id:
                processed_ids.add(row_id)

    duration = time.perf_counter() - start_total
    print(f"Done. Wrote {written} rows to {args.output}")
    print(f"Total wall-clock: {duration:.2f}s ({duration/60:.2f} min)")
    if len(rows) > 0:
        print(f"Avg wall-clock per exam: {duration/len(rows):.2f}s")

if __name__ == "__main__":
    main()
