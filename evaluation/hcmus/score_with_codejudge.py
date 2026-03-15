import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import IntegratedAssessor, LLMFactory  # noqa: E402


HCMUS_ROOT = Path(__file__).resolve().parent
PROBLEMS_DIR = HCMUS_ROOT / "problems"
DATA_CODE_DIR = HCMUS_ROOT / "data_code"
DEFAULT_CSV = HCMUS_ROOT / "hcmus_dataset.csv"


def build_default_output_path(model_name: str) -> Path:
    """Build default output path with format: YYMMDD_HH:MM_model-name.jsonl"""
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    return HCMUS_ROOT / "output" / f"{ts}_{safe_model}.jsonl"


def split_questions(problem_text: str) -> List[str]:
    """Split a problem file into question blocks, e.g. Cau/Bai 1,2,3."""
    # Supports both accented and unaccented Vietnamese headings.
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
    """Sort Bai01/Bai02/... files in stable numeric order."""

    def key_fn(path: Path):
        m = re.search(r"(\d+)", path.stem)
        return int(m.group(1)) if m else 10**9

    cpp_files = [p for p in student_dir.iterdir() if p.is_file() and p.suffix.lower() in {".cpp", ".cc", ".cxx", ".c"}]
    return sorted(cpp_files, key=key_fn)


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


def evaluate_row(
    row: Dict[str, str],
    assessor: Optional[IntegratedAssessor],
    run_both_assessments: bool,
    dry_run: bool,
    scoring_mode: str,
) -> List[Dict[str, object]]:
    row_id = row["id"].strip()
    problem_id = row["problem_id"].strip()
    language = row["language"].strip() or "C++"

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

    results: List[Dict[str, object]] = []

    if scoring_mode == "whole_exam":
        full_problem_statement = problem_text

        code_parts = []
        for idx, code_file in enumerate(code_files, start=1):
            code_text = code_file.read_text(encoding="utf-8", errors="ignore")
            code_parts.append(
                f"[Submission {idx} - {code_file.name}]\n```cpp\n{code_text}\n```"
            )

        full_student_code = "\n\n".join(code_parts)

        item: Dict[str, object] = {
            "id": row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "language": language,
            "run_both_assessments": run_both_assessments,
            "scoring_mode": scoring_mode,
            "num_code_files": len(code_files),
            "code_files": [p.name for p in code_files],
        }

        if dry_run:
            item["status"] = "dry_run"
            item["problem_preview"] = problem_text[:180]
            results.append(item)
            return results

        assert assessor is not None
        integrated = assessor.assess(
            problem_statement=full_problem_statement,
            student_code=full_student_code,
            reference_code=None,
            language=language,
        )
        item["result"] = integrated
        results.append(item)
        return results

    questions = split_questions(problem_text)
    per_question_results: List[Dict[str, object]] = []

    for idx, code_file in enumerate(code_files, start=1):
        if idx > len(questions):
            break
        code_text = code_file.read_text(encoding="utf-8", errors="ignore")
        question_text = questions[idx - 1]
        question_max = parse_question_max(question_text)

        item: Dict[str, object] = {
            "id": row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "question_index": idx,
            "code_file": code_file.name,
            "language": language,
            "question_max": question_max,
            "run_both_assessments": run_both_assessments,
            "scoring_mode": scoring_mode,
        }

        if dry_run:
            item["status"] = "dry_run"
            item["question_preview"] = question_text[:120]
            results.append(item)
            per_question_results.append(item)
            continue

        assert assessor is not None
        problem_statement = question_text
        integrated = assessor.assess(
            problem_statement=problem_statement,
            student_code=code_text,
            reference_code=None,
            language=language,
            question_max=question_max,
        )
        item["result"] = integrated
        results.append(item)
        per_question_results.append(item)

    # Add one summary line for full exam score when scoring per question.
    if per_question_results:
        total_max = 0.0
        total_scaled = 0.0
        has_scaled = False

        for item in per_question_results:
            qmax = item.get("question_max")
            if isinstance(qmax, (int, float)):
                total_max += float(qmax)

            res = item.get("result")
            if isinstance(res, dict):
                summary = res.get("summary", {}) if isinstance(res.get("summary"), dict) else {}
                scaled = summary.get("score_scaled")
                raw_score = summary.get("score")
                if isinstance(scaled, (int, float)):
                    total_scaled += float(scaled)
                    has_scaled = True
                elif isinstance(raw_score, (int, float)) and isinstance(qmax, (int, float)):
                    total_scaled += float(raw_score) / 10.0 * float(qmax)
                    has_scaled = True

        summary_item: Dict[str, object] = {
            "id": row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "language": language,
            "scoring_mode": scoring_mode,
            "record_type": "exam_summary",
            "questions_count": len(per_question_results),
            "max_total_score": round(total_max, 4),
        }

        if has_scaled:
            summary_item["predicted_total_score"] = round(total_scaled, 4)
            if total_max > 0:
                summary_item["predicted_total_score_ratio"] = round(total_scaled / total_max, 4)

        if not dry_run:
            summary_item["question_details"] = [
                {
                    "question_index": item.get("question_index"),
                    "question_max": item.get("question_max"),
                    "score_on_10": (
                        item.get("result", {}).get("summary", {}).get("score")
                        if isinstance(item.get("result"), dict)
                        else None
                    ),
                    "score_scaled": (
                        item.get("result", {}).get("summary", {}).get("score_scaled")
                        if isinstance(item.get("result"), dict)
                        else None
                    ),
                }
                for item in per_question_results
            ]

        results.append(summary_item)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Score HCMUS dataset using codejudge IntegratedAssessor")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to hcmus_dataset.csv")
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "anthropic", "local", "gemini"],
        help="LLM provider",
    )
    parser.add_argument("--model", type=str, default="gpt-4", help="Model name")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL file. If omitted, auto-generate as YYMMDD_HH:MM_model-name.jsonl in evaluation/hcmus/output",
    )
    parser.add_argument("--limit", type=int, default=0, help="Only process first N rows (0 means all)")
    parser.add_argument("--start", type=int, default=0, help="Start index in CSV rows")
    parser.add_argument("--run-both-assessments", action="store_true", help="Always run both binary and taxonomy")
    parser.add_argument(
        "--scoring-mode",
        type=str,
        default="whole_exam",
        choices=["whole_exam", "per_question"],
        help="whole_exam: one prompt for whole exam; per_question: split by Cau/Bai headings",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not call LLM; only validate mapping and emit metadata")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL for local provider")

    args = parser.parse_args()
    if args.output is None:
        args.output = build_default_output_path(args.model)

    rows = load_rows(args.csv)

    if args.start < 0:
        raise ValueError("--start must be >= 0")

    rows = rows[args.start :]
    if args.limit > 0:
        rows = rows[: args.limit]

    assessor: Optional[IntegratedAssessor] = None
    if not args.dry_run:
        kwargs = {}
        if args.provider == "local" and args.base_url:
            kwargs["base_url"] = args.base_url
        llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, **kwargs)
        assessor = IntegratedAssessor(
            llm_client=llm_client,
            run_both_assessments=args.run_both_assessments,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.output.open("w", encoding="utf-8") as f:
        for row in rows:
            items = evaluate_row(
                row=row,
                assessor=assessor,
                run_both_assessments=args.run_both_assessments,
                dry_run=args.dry_run,
                scoring_mode=args.scoring_mode,
            )
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1

    print(f"Done. wrote {written} rows to {args.output}")


if __name__ == "__main__":
    main()
