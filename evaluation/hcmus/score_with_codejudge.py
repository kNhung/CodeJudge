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
# defer importing prompts (codejudge.core imports heavy deps like torch)


def build_default_output_path(model_name: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    return HCMUS_ROOT / "output" / f"{ts}_{safe_model}.jsonl"


HCMUS_ROOT = Path(__file__).resolve().parent
PROBLEMS_DIR = HCMUS_ROOT / "problems"
DATA_CODE_DIR = HCMUS_ROOT / "data_code"
DEFAULT_CSV = HCMUS_ROOT / "hcmus_dataset.csv"


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


def _sum_usage_dicts(usages: List[Optional[Dict[str, Any]]]) -> Dict[str, int]:
    total_input = 0
    total_output = 0
    has_any = False

    for usage in usages:
        if not isinstance(usage, dict):
            continue
        in_tok = usage.get("input_tokens")
        out_tok = usage.get("output_tokens")
        if isinstance(in_tok, int):
            total_input += in_tok
            has_any = True
        if isinstance(out_tok, int):
            total_output += out_tok
            has_any = True

    if not has_any:
        return {}

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "total_tokens": total_input + total_output,
    }


def extract_usage_totals(result: Dict[str, Any]) -> Dict[str, int]:
    usage = result.get("usage")
    if not isinstance(usage, dict):
        return {}

    # Integrated output: usage.binary.total + usage.taxonomy
    if isinstance(usage.get("binary"), dict) or isinstance(usage.get("taxonomy"), dict):
        parts: List[Optional[Dict[str, Any]]] = []
        binary = usage.get("binary")
        if isinstance(binary, dict):
            parts.append(binary.get("total") if isinstance(binary.get("total"), dict) else binary)
        taxonomy = usage.get("taxonomy")
        if isinstance(taxonomy, dict):
            parts.append(taxonomy)
        return _sum_usage_dicts(parts)

    # Binary-only output: usage.total.
    if isinstance(usage.get("total"), dict):
        return _sum_usage_dicts([usage.get("total")])

    # Taxonomy-only or flat provider usage.
    return _sum_usage_dicts([usage])


def determine_usage_source(result: Dict[str, Any]) -> Optional[str]:
    """Determine provenance of usage metadata: hf_response, estimated, unavailable, or mixed."""
    usage = result.get("usage")
    if not isinstance(usage, dict):
        return None

    # Integrated outputs may contain nested parts
    sources = set()

    def inspect(u: Any):
        if not isinstance(u, dict):
            return
        raw = u.get("raw_usage") if isinstance(u.get("raw_usage"), dict) else u
        src = raw.get("source") if isinstance(raw, dict) else None
        if src:
            sources.add(str(src))

    # top-level usage
    inspect(usage)

    # nested fields commonly used: binary, taxonomy, total
    for key in ("binary", "taxonomy", "total"):
        part = usage.get(key)
        if isinstance(part, dict):
            inspect(part)

    if not sources:
        return None
    if len(sources) == 1:
        return next(iter(sources))
    return "mixed"


def attach_metadata(item: Dict[str, object], result: Dict[str, Any]) -> None:
    totals = extract_usage_totals(result)
    if totals:
        item["input_tokens"] = totals.get("input_tokens")
        item["output_tokens"] = totals.get("output_tokens")
        item["total_tokens"] = totals.get("total_tokens")

    # Add a clear usage_source field so JSONL consumers know where tokens came from.
    src = determine_usage_source(result)
    if src:
        item["usage_source"] = src

    # Keep the existing runtime_seconds field as the shared metadata entry.
    runtime_seconds = item.get("runtime_seconds")
    if isinstance(runtime_seconds, (int, float)):
        item["runtime_seconds"] = round(float(runtime_seconds), 6)


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


def run_assessment(
    assessor: object,
    mode: str,
    problem_statement: str,
    student_code: str,
    language: str,
    question_max: Optional[float] = None,
) -> Dict[str, Any]:
    assess_kwargs: Dict[str, Any] = {
        "problem_statement": problem_statement,
        "student_code": student_code,
        "language": language,
    }

    if mode in {"taxonomy", "intergrated"}:
        assess_kwargs["reference_code"] = None
    if mode == "intergrated":
        assess_kwargs["question_max"] = question_max

    return assessor.assess(**assess_kwargs)


def evaluate_row(
    row: Dict[str, str],
    assessor: Optional[object],
    mode: str,
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
        # collect question headings so outputs can map scores/comments to question names
        questions = split_questions(problem_text)
        question_names = [q.splitlines()[0].strip() for q in questions]
        code_parts = []
        for idx, code_file in enumerate(code_files, start=1):
            code_text = code_file.read_text(encoding="utf-8", errors="ignore")
            code_parts.append(
                f"[Submission {idx} - {code_file.name}]\n```cpp\n{code_text}\n```"
            )

        full_student_code = "\n\n".join(code_parts)

        item: Dict[str, object] = {
            "id": row_id,
            "example_index": int(row_id) if str(row_id).isdigit() else row_id,
            "student_id": row.get("student_id", ""),
            "problem_id": problem_id,
            "expect_grade": row.get("expect_grade", ""),
            "language": language,
            "mode": mode,
            "scoring_mode": scoring_mode,
            "num_code_files": len(code_files),
            "code_files": [p.name for p in code_files],
            "results": [],
            "question_names": question_names,
        }

        if dry_run:
            item["status"] = "dry_run"
            item["problem_preview"] = problem_text[:180]
            results.append(item)
            return results

        assert assessor is not None
        started_at = time.perf_counter()
        assessment_result = run_assessment(
            assessor=assessor,
            mode=mode,
            problem_statement=full_problem_statement,
            student_code=full_student_code,
            language=language,
        )
        item["runtime_seconds"] = round(time.perf_counter() - started_at, 6)
        item["result"] = assessment_result
        item["results"] = [
            {
                "source": "whole_exam",
                "grade_reference": row.get("expect_grade", ""),
                "result": assessment_result,
            }
        ]
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
        # human-friendly short question name (heading first line)
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
            "mode": mode,
            "scoring_mode": scoring_mode,
        }

        if dry_run:
            item["status"] = "dry_run"
            item["question_preview"] = question_text[:120]
            item["question_name"] = question_name
            results.append(item)
            per_question_results.append(item)
            continue

        assert assessor is not None
        problem_statement = question_text
        started_at = time.perf_counter()
        assessment_result = run_assessment(
            assessor=assessor,
            mode=mode,
            problem_statement=problem_statement,
            student_code=code_text,
            language=language,
            question_max=question_max,
        )
        item["runtime_seconds"] = round(time.perf_counter() - started_at, 6)
        item["result"] = assessment_result
        item["question_name"] = question_name
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
            "mode": mode,
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
            summary_item["runtime_seconds"] = round(
                sum(float(item.get("runtime_seconds", 0.0) or 0.0) for item in per_question_results),
                6,
            )

        if not dry_run:
            summary_item["question_details"] = [
                {
                    "question_index": item.get("question_index"),
                    "question_max": item.get("question_max"),
                    "question_name": item.get("question_name"),
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
    parser.add_argument("--provider", type=str, default="openai", help="LLM provider")
    parser.add_argument("--model", type=str, default="gpt-4", help="Model name")
    parser.add_argument("--api-key", type=str, default=None, help="API key for cloud providers")
    parser.add_argument("--output", type=Path, default=None, help="Output JSONL file")
    parser.add_argument("--run-name", type=str, default=None, help="Optional run name to include in output filename")
    parser.add_argument(
        "--mode",
        type=str,
        default="taxonomy",
        choices=["binary", "taxonomy", "intergrated"],
        help="Choose the scoring mode",
    )
    parser.add_argument(
        "--taxonomy-prompt",
        type=str,
        default="mine",
        choices=["mine", "author"],
        help="Choose taxonomy prompt template: mine or author",
    )
    parser.add_argument(
        "--save-metadata",
        action="store_true",
        help="Write token/runtime metadata into the main JSONL output file",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Append to existing output and skip rows whose id already exists there",
    )
    parser.add_argument("--limit", type=int, default=0, help="Only process first N rows (0 means all)")
    parser.add_argument("--start", type=int, default=0, help="Start index in CSV rows")
    parser.add_argument(
        "--scoring-mode",
        type=str,
        default="whole_exam",
        choices=["whole_exam", "per_question"],
        help="whole_exam: one prompt for whole exam; per_question: split by Cau/Bai headings",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not call LLM; only validate mapping and emit metadata")

    args = parser.parse_args()
    if args.output is None:
        args.output = (HCMUS_ROOT / "output" / f"{args.run_name}.jsonl") if args.run_name else build_default_output_path(args.model)

    rows = load_rows(args.csv)

    # Resolve taxonomy system prompt early if possible (deferred import)
    taxonomy_system_prompt = None
    try:
        from codejudge.core.prompts import (
            AUTHOR_SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
            SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
        )
        taxonomy_system_prompt = (
            AUTHOR_SYSTEM_PROMPT_TAXONOMY_ASSESSMENT if args.taxonomy_prompt == "author" else SYSTEM_PROMPT_TAXONOMY_ASSESSMENT
        )
    except Exception:
        taxonomy_system_prompt = None

    if args.start < 0:
        raise ValueError("--start must be >= 0")

    rows = rows[args.start :]
    if args.limit > 0:
        rows = rows[: args.limit]

    processed_ids = load_processed_ids(args.output) if args.resume else set()

    assessor: Optional[IntegratedAssessor] = None
    if not args.dry_run:
        # Import assessors lazily to avoid heavy ML deps during dry-run
        from codejudge.core import BinaryAssessor, IntegratedAssessor, LLMFactory, TaxonomyAssessor  # noqa: E402
        llm_client = LLMFactory.create(provider=args.provider, model_name=args.model)
        # taxonomy_system_prompt already resolved above
        if args.mode == "binary":
            assessor = BinaryAssessor(llm_client=llm_client)
        elif args.mode == "taxonomy":
            assessor = TaxonomyAssessor(llm_client=llm_client, system_prompt=taxonomy_system_prompt)
        else:
            assessor = IntegratedAssessor(
                llm_client=llm_client,
                run_both_assessments=True,
            )
            # adapt to current IntegratedAssessor API by setting taxonomy prompt on the instance
            try:
                assessor.taxonomy_assessor.system_prompt = taxonomy_system_prompt
            except Exception:
                pass

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    file_mode = "a" if args.resume and args.output.exists() else "w"
    with args.output.open(file_mode, encoding="utf-8") as f:
        for row in rows:
            row_id = str(row.get("id", "")).strip()
            if args.resume and row_id and row_id in processed_ids:
                continue

            try:
                items = evaluate_row(
                    row=row,
                    assessor=assessor,
                    mode=args.mode,
                    dry_run=args.dry_run,
                    scoring_mode=args.scoring_mode,
                )
            except RuntimeError as e:
                message = str(e)
                if args.provider == "huggingface" and (
                    "402 Payment Required" in message
                    or "depleted your monthly included credits" in message
                    or "Payment Required" in message
                ):
                    print("Hugging Face quota exhausted. Stopping cleanly so you can resume later.")
                    print(f"Last row id={row_id}")
                    print(f"Error: {message}")
                    break
                raise

            for item in items:
                # Add run-level metadata
                item["model"] = args.model
                item["provider"] = args.provider
                item["taxonomy_prompt"] = args.taxonomy_prompt
                # include a small preview of the system prompt for auditing
                item["system_prompt_preview"] = (
                    taxonomy_system_prompt[:500] if isinstance(taxonomy_system_prompt, str) else None
                )

                if args.save_metadata and "result" in item and isinstance(item["result"], dict):
                    attach_metadata(item, item["result"])

                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1

                if args.resume and row_id:
                    processed_ids.add(row_id)

    print(f"Done. wrote {written} rows to {args.output}")


if __name__ == "__main__":
    main()
