import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from code_model_score import answer_to_score, form_filling, load_model  # noqa: E402
from evaluation.apps.prompts import single_step_prompt  # noqa: E402

HCMUS_DATA_ROOT = REPO_ROOT / "evaluation" / "data" / "hcmus"
PROBLEMS_DIR = HCMUS_DATA_ROOT / "problems"
DATA_CODE_DIR = HCMUS_DATA_ROOT / "data_code"
DEFAULT_CSV = HCMUS_DATA_ROOT / "hcmus_dataset.csv"
OUTPUT_ROOT = REPO_ROOT / "evaluation" / "hcmus" / "output"


def build_default_output_path(model_name: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    return OUTPUT_ROOT / f"{ts}_{safe_model}_author-baseline.jsonl"


def split_questions(problem_text: str) -> List[str]:
    parts = re.split(r"(?=^\s*(?:C\S*u|B\S*i)\s*\d+)", problem_text, flags=re.MULTILINE)
    blocks = [p.strip() for p in parts if p.strip()]
    return blocks if blocks else [problem_text.strip()]


def list_code_files(student_dir: Path) -> List[Path]:
    def key_fn(path: Path) -> int:
        m = re.search(r"(\d+)", path.stem)
        return int(m.group(1)) if m else 10**9

    cpp_files = [
        p
        for p in student_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".cpp", ".cc", ".cxx", ".c"}
    ]
    return sorted(cpp_files, key=key_fn)


def parse_rows(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"id", "language", "problem_id", "student_id", "expect_grade"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
        return list(reader)


def expected_pass(expect_grade: str) -> bool:
    try:
        return float(expect_grade) >= 5.0
    except Exception:
        return False


def run_one_question(
    model: str,
    terminators,
    pipeline,
    problem_statement: str,
    student_code: str,
    temperature: float,
):
    # Author baseline binary prompt (no reference code)
    binary_answer = form_filling(
        model,
        single_step_prompt[0],
        terminators,
        pipeline,
        temperature,
        info={"PROBLEM": problem_statement, "CODE1": student_code},
    )
    binary_score = answer_to_score(binary_answer, "bool")

    # Author baseline taxonomy prompt (no reference code)
    taxonomy_answer = form_filling(
        model,
        single_step_prompt[4],
        terminators,
        pipeline,
        temperature,
        info={"PROBLEM": problem_statement, "CODE1": student_code},
    )
    taxonomy_score = answer_to_score(taxonomy_answer, "inconsistency_level")

    # Author baseline 0-4 functional score prompt (no reference code)
    functional_answer = form_filling(
        model,
        single_step_prompt[2],
        terminators,
        pipeline,
        temperature,
        info={"PROBLEM": problem_statement, "CODE1": student_code},
    )
    functional_raw = answer_to_score(functional_answer, "0_to_4_score_functional_correctness")

    score_10 = -1.0
    if isinstance(functional_raw, (int, float)) and functional_raw >= 0:
        score_10 = min(10.0, max(0.0, float(functional_raw) * 2.5))
    elif isinstance(taxonomy_score, (int, float)) and taxonomy_score >= 0:
        score_10 = 10.0 if float(taxonomy_score) >= 1.0 else 0.0
    elif isinstance(binary_score, bool):
        score_10 = 10.0 if binary_score else 0.0

    return {
        "binary": {
            "result": "Yes" if binary_score is True else ("No" if binary_score is False else "Unknown"),
            "passed": bool(binary_score) if isinstance(binary_score, bool) else False,
            "raw_response": binary_answer,
        },
        "taxonomy": {
            "passed": bool(taxonomy_score) if isinstance(taxonomy_score, (int, float)) else False,
            "raw_response": taxonomy_answer,
            "raw_score": taxonomy_score,
        },
        "functional": {
            "score_0_to_4": functional_raw,
            "raw_response": functional_answer,
        },
        "summary": {
            "score": score_10,
            "status": "PASS" if score_10 >= 5.0 else "FAIL",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HCMUS with author-baseline prompting logic")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--model", type=str, default="gemini-2.5-flash")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--scoring-mode", choices=["whole_exam", "per_question"], default="per_question")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.output is None:
        args.output = build_default_output_path(args.model)

    rows = parse_rows(args.csv)
    rows = rows[max(0, args.start) :]
    if args.limit > 0:
        rows = rows[: args.limit]

    terminators = None
    pipeline = None
    if not args.dry_run:
        terminators, pipeline = load_model(args.model)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as fout:
        for row in rows:
            row_id = row["id"].strip()
            problem_id = row["problem_id"].strip()
            student_dir = DATA_CODE_DIR / row_id
            problem_file = PROBLEMS_DIR / f"{problem_id}.txt"

            if not student_dir.is_dir() or not problem_file.is_file():
                record = {
                    "id": row_id,
                    "student_id": row.get("student_id", ""),
                    "problem_id": problem_id,
                    "expect_grade": row.get("expect_grade", ""),
                    "error": "missing student folder or problem file",
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            problem_text = problem_file.read_text(encoding="utf-8", errors="ignore")
            code_files = list_code_files(student_dir)
            questions = split_questions(problem_text)

            if args.scoring_mode == "whole_exam":
                code_blocks = []
                for idx, p in enumerate(code_files, start=1):
                    code_text = p.read_text(encoding="utf-8", errors="ignore")
                    code_blocks.append(f"[Submission {idx} - {p.name}]\n```cpp\n{code_text}\n```")
                all_code = "\n\n".join(code_blocks)

                if args.dry_run:
                    result = {"status": "dry_run", "num_code_files": len(code_files)}
                else:
                    result = run_one_question(
                        model=args.model,
                        terminators=terminators,
                        pipeline=pipeline,
                        problem_statement=problem_text,
                        student_code=all_code,
                        temperature=args.temperature,
                    )

                predicted = result.get("summary", {}).get("score", -1)
                record = {
                    "mode": "author_baseline",
                    "id": row_id,
                    "student_id": row.get("student_id", ""),
                    "problem_id": problem_id,
                    "expect_grade": row.get("expect_grade", ""),
                    "expected_pass": expected_pass(row.get("expect_grade", "")),
                    "predicted_pass": predicted >= 5.0 if isinstance(predicted, (int, float)) else False,
                    "predicted_score_10": predicted,
                    "result": result,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            for idx, code_file in enumerate(code_files, start=1):
                if idx > len(questions):
                    break
                code_text = code_file.read_text(encoding="utf-8", errors="ignore")
                question_text = questions[idx - 1]

                if args.dry_run:
                    result = {"status": "dry_run", "question_preview": question_text[:120]}
                else:
                    result = run_one_question(
                        model=args.model,
                        terminators=terminators,
                        pipeline=pipeline,
                        problem_statement=question_text,
                        student_code=code_text,
                        temperature=args.temperature,
                    )

                predicted = result.get("summary", {}).get("score", -1)
                record = {
                    "mode": "author_baseline",
                    "id": row_id,
                    "student_id": row.get("student_id", ""),
                    "problem_id": problem_id,
                    "question_index": idx,
                    "code_file": code_file.name,
                    "expect_grade": row.get("expect_grade", ""),
                    "expected_pass": expected_pass(row.get("expect_grade", "")),
                    "predicted_pass": predicted >= 5.0 if isinstance(predicted, (int, float)) else False,
                    "predicted_score_10": predicted,
                    "result": result,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Done. Wrote output to {args.output}")
    print("Note: this script uses author-baseline prompts/parsers from evaluation/apps/prompts.py and code_model_score.")


if __name__ == "__main__":
    main()
