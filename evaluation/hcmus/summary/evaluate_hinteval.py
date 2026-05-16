import argparse
import json
import re
import sys
import types
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Sequence

from rouge_score import rouge_scorer

from hinteval.cores.dataset_core import Answer, Hint, Instance, Question
from hinteval.evaluation.convergence import Specificity
from hinteval.evaluation.familiarity import WordFrequency
from hinteval.evaluation.readability import TraditionalIndexes


SCRIPT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = SCRIPT_ROOT / "hcmus" / "output"
DEFAULT_INPUT = OUTPUT_DIR / "hcmus_from_48_taxonomy" / "hcmus_from_48_taxonomy.jsonl"
DEFAULT_OUTPUT = OUTPUT_DIR / "hint_eval_summary.json"


READABILITY_METRIC_NAME = "readability-flesch_kincaid_reading_ease-sm"
FAMILIARITY_METRIC_NAME = "familiarity-freq-exclude_stop_words-sm"
CONVERGENCE_METRIC_NAME = "convergence-specificity-bert-base"

DEFAULT_SPACY_PIPELINE = "en_core_web_sm"


PROMPT_PROBLEM_RE = re.compile(r"Đề bài:\s*(.*?)\n\s*Code sinh viên:", re.S)
PROMPT_REFERENCE_RE = re.compile(
    r"Code mẫu tham khảo.*?:\s*```(?:\w+)?\n(.*?)\n```",
    re.S,
)

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input file: {path}")
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _clean_block(text: str) -> str:
    return text.strip().strip("`").strip()


def extract_problem_statement(user_prompt: str) -> str:
    match = PROMPT_PROBLEM_RE.search(user_prompt)
    if match:
        return match.group(1).strip()
    return user_prompt.strip()


def extract_reference_code(user_prompt: str) -> str:
    match = PROMPT_REFERENCE_RE.search(user_prompt)
    if match:
        return _clean_block(match.group(1))

    fallback_markers = ["Code mẫu tham khảo", "Code tham khảo", "Reference code"]
    for marker in fallback_markers:
        if marker not in user_prompt:
            continue
        tail = user_prompt.split(marker, 1)[1]
        fence_match = re.search(r"```(?:\w+)?\n(.*?)\n```", tail, re.S)
        if fence_match:
            return _clean_block(fence_match.group(1))
    return ""


def extract_student_code(user_prompt: str) -> str:
    match = re.search(r"Code sinh viên:\s*```(?:\w+)?\n(.*?)\n```", user_prompt, re.S)
    if match:
        return _clean_block(match.group(1))
    return ""


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def extract_hints(output_parsed: Any, include_strengths: bool = False) -> List[str]:
    if not isinstance(output_parsed, dict):
        return []

    hints: List[str] = []
    improvements = output_parsed.get("improvements", [])
    if isinstance(improvements, list):
        hints.extend(str(item) for item in improvements if str(item).strip())

    errors = output_parsed.get("errors", [])
    if isinstance(errors, list):
        for error in errors:
            if not isinstance(error, dict):
                continue
            fix_suggestion = error.get("fix_suggestion")
            if fix_suggestion:
                hints.append(str(fix_suggestion))

    if include_strengths:
        strengths = output_parsed.get("strengths", [])
        if isinstance(strengths, list):
            hints.extend(str(item) for item in strengths if str(item).strip())

    return dedupe_preserve_order(hints)


def build_instances(samples: Sequence[Dict[str, Any]], include_strengths: bool = False, use_answers: bool = True):
    instances: List[Instance] = []
    metadata: List[Dict[str, Any]] = []
    for sample in samples:
        user_prompt = str(sample.get("user_prompt", ""))
        output_parsed = sample.get("output_parsed", {})
        hints = extract_hints(output_parsed, include_strengths=include_strengths)
        if not hints:
            continue

        problem_statement = extract_problem_statement(user_prompt)
        reference_code = extract_reference_code(user_prompt) if use_answers else ""
        student_code = extract_student_code(user_prompt)

        if not problem_statement:
            continue
        if use_answers and not reference_code:
            continue

        answers = [Answer(reference_code)] if (use_answers and reference_code) else []
        instance = Instance(
            question=Question(problem_statement),
            answers=answers,
            hints=[Hint(text) for text in hints],
        )
        instances.append(instance)
        metadata.append(
            {
                "row_index": sample.get("row_index"),
                "case": sample.get("case"),
                "language": sample.get("language"),
                "problem_statement": problem_statement,
                "reference_code": reference_code,
                "student_code": student_code,
                "hints": hints,
            }
        )

    return instances, metadata


def score_relevance(instances: Sequence[Instance], rouge_model: str) -> List[List[float]]:
    scorer = rouge_scorer.RougeScorer([rouge_model], use_stemmer=True)
    scores: List[List[float]] = []
    for instance in instances:
        question_text = instance.question.question
        hint_scores = []
        for hint in instance.hints:
            score = scorer.score(question_text, hint.hint)[rouge_model].fmeasure
            hint_scores.append(float(score))
        scores.append(hint_scores)
    return scores


def evaluate_answer_agnostic(instances: Sequence[Instance]) -> Dict[str, Any]:
    readability_metric = TraditionalIndexes(
        method="flesch_kincaid_reading_ease",
        spacy_pipeline=DEFAULT_SPACY_PIPELINE,
        checkpoint=False,
        enable_tqdm=False,
    )
    familiarity_metric = WordFrequency(
        method="exclude_stop_words",
        spacy_pipeline=DEFAULT_SPACY_PIPELINE,
        checkpoint=False,
        enable_tqdm=False,
    )
    convergence_metric = Specificity(
        model_name="bert-base",
        batch_size=32,
        checkpoint=False,
        enable_tqdm=False,
    )

    flattened_hints: List[Hint] = [hint for instance in instances for hint in instance.hints]
    readability_scores = readability_metric.evaluate(flattened_hints)
    familiarity_scores = familiarity_metric.evaluate(flattened_hints)
    convergence_scores = convergence_metric.evaluate(list(instances))

    return {
        "readability_scores": readability_scores,
        "familiarity_scores": familiarity_scores,
        "convergence_scores": convergence_scores,
    }


def summarize_relevance(metadata: Sequence[Dict[str, Any]], scores: Sequence[Sequence[float]], instances: Sequence[Instance], rouge_model: str):
    sample_rows = []
    all_scores: List[float] = []

    for item, instance, hint_scores in zip(metadata, instances, scores):
        scores_list = [float(score) for score in hint_scores]
        all_scores.extend(scores_list)
        sample_rows.append(
            {
                **item,
                "rouge_model": rouge_model,
                "relevance_scores": scores_list,
                "hint_count": len(scores_list),
                "hints_with_scores": [
                    {"text": hint.hint, f"relevance_{rouge_model}": float(score)}
                    for hint, score in zip(instance.hints, scores_list)
                ],
                "mean_relevance": round(mean(scores_list), 6) if scores_list else None,
                "max_relevance": round(max(scores_list), 6) if scores_list else None,
                "min_relevance": round(min(scores_list), 6) if scores_list else None,
            }
        )

    summary = {
        "samples": len(sample_rows),
        "total_hints": len(all_scores),
        "rouge_model": rouge_model,
        "mean_relevance": round(mean(all_scores), 6) if all_scores else None,
        "max_relevance": round(max(all_scores), 6) if all_scores else None,
        "min_relevance": round(min(all_scores), 6) if all_scores else None,
    }
    return summary, sample_rows


def summarize_answer_agnostic(metadata: Sequence[Dict[str, Any]], instances: Sequence[Instance], metric_outputs: Dict[str, Any]):
    sample_rows = []
    readability_scores = metric_outputs["readability_scores"]
    familiarity_scores = metric_outputs["familiarity_scores"]
    convergence_scores = metric_outputs["convergence_scores"]

    metric_values = {
        READABILITY_METRIC_NAME: [],
        FAMILIARITY_METRIC_NAME: [],
        CONVERGENCE_METRIC_NAME: [],
    }

    hint_offset = 0
    for item, instance, convergence_row in zip(metadata, instances, convergence_scores):
        sample_obj = {**item, "hints_with_scores": [], "hint_count": len(instance.hints)}

        for local_idx, hint in enumerate(instance.hints):
            global_idx = hint_offset + local_idx
            readability_value = float(readability_scores[global_idx])
            familiarity_value = float(familiarity_scores[global_idx])
            convergence_value = float(convergence_row[local_idx])
            sample_obj["hints_with_scores"].append(
                {
                    "text": hint.hint,
                    READABILITY_METRIC_NAME: readability_value,
                    FAMILIARITY_METRIC_NAME: familiarity_value,
                    CONVERGENCE_METRIC_NAME: convergence_value,
                }
            )
            metric_values[READABILITY_METRIC_NAME].append(readability_value)
            metric_values[FAMILIARITY_METRIC_NAME].append(familiarity_value)
            metric_values[CONVERGENCE_METRIC_NAME].append(convergence_value)

        hint_offset += len(instance.hints)
        sample_rows.append(sample_obj)

    summary = {
        "samples": len(sample_rows),
        "total_hints": len(readability_scores),
        "metrics": {}
    }

    for metric_name, values in metric_values.items():
        if values:
            summary["metrics"][metric_name] = {
                "mean": round(mean(values), 6),
                "max": round(max(values), 6),
                "min": round(min(values), 6),
                "count": len(values)
            }

    return summary, sample_rows


def evaluate_file(input_path: Path, mode: str = "agnostic", include_strengths: bool = False, rouge_model: str = "rougeL"):
    """Evaluate hints using specified mode.

    Args:
        input_path: Path to input JSONL
        mode: 'relevance' (with answers), 'agnostic' (paper-like answer-agnostic metrics)
        include_strengths: Include strengths as hints
        rouge_model: ROUGE variant to use
    """
    records = load_jsonl(input_path)
    all_samples: List[Dict[str, Any]] = []
    for record in records:
        # Existing JSONL format (conala-style): top-level 'samples' list
        if isinstance(record, dict) and "samples" in record:
            samples = record.get("samples")
            if isinstance(samples, list):
                all_samples.extend(sample for sample in samples if isinstance(sample, dict))
            continue

        # Taxonomy-style records: top-level 'result' contains evaluation fields
        # Convert to the internal sample shape expected by build_instances
        if isinstance(record, dict) and "result" in record and isinstance(record["result"], dict):
            sample: Dict[str, Any] = {
                # Use problem_id or problem identifier as the prompt/question text
                "user_prompt": str(record.get("problem_id", record.get("id", ""))),
                # Place the taxonomy result under output_parsed so extract_hints can work
                "output_parsed": record.get("result", {}),
                "row_index": record.get("id"),
                "case": None,
                "language": None,
            }
            all_samples.append(sample)

    use_answers = (mode == "relevance")
    instances, metadata = build_instances(all_samples, include_strengths=include_strengths, use_answers=use_answers)
    if not instances:
        raise ValueError("No evaluable samples found in the input JSONL.")

    if mode == "relevance":
        scores = score_relevance(instances, rouge_model=rouge_model)
        summary, sample_rows = summarize_relevance(metadata, scores, instances, rouge_model)
        return {
            "input_file": str(input_path),
            "mode": mode,
            "include_strengths": include_strengths,
            "metrics": [f"relevance_{rouge_model}"],
            "summary": summary,
            "samples": sample_rows,
        }

    metric_outputs = evaluate_answer_agnostic(instances)
    summary, sample_rows = summarize_answer_agnostic(metadata, instances, metric_outputs)

    return {
        "input_file": str(input_path),
        "mode": mode,
        "include_strengths": include_strengths,
        "metrics": [READABILITY_METRIC_NAME, FAMILIARITY_METRIC_NAME, CONVERGENCE_METRIC_NAME],
        "summary": summary,
        "samples": sample_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate system suggestions with HintEval-compatible metrics.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSONL file with system outputs")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to write the summary JSON")
    parser.add_argument(
        "--mode",
        type=str,
        default="agnostic",
        choices=["relevance", "agnostic"],
        help="Evaluation mode: 'relevance' (with answers), 'agnostic' (paper-like answer-agnostic metrics)",
    )
    parser.add_argument(
        "--rouge-model",
        type=str,
        default="rougeL",
        choices=["rouge1", "rouge2", "rougeL"],
        help="ROUGE variant to use for relevance scoring (only in relevance mode)",
    )
    parser.add_argument(
        "--include-strengths",
        action="store_true",
        help="Also treat strengths as hints",
    )
    args = parser.parse_args()

    result = evaluate_file(
        args.input,
        mode=args.mode,
        include_strengths=args.include_strengths,
        rouge_model=args.rouge_model,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print(f"Wrote HintEval summary to {args.output}")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
