import argparse
import json
import sys
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core.prompts import (
    PromptTemplates,
    SYSTEM_PROMPT_BINARY_ASSESSMENT,
    SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
)
from codejudge.core import LLMFactory, TaxonomyAssessor
from score_with_codejudge import (
    DEFAULT_CSV,
    DATA_CODE_DIR,
    get_problem_path,
    list_code_files,
    load_rows,
    parse_question_max,
    split_questions,
)


@dataclass
class CallUsage:
    call_name: str
    input_tokens: int
    output_tokens_est: int


@dataclass
class SampleUsage:
    sample_id: str
    question_index: Optional[int]
    call_usages: List[CallUsage]
    runtime_seconds: Optional[float] = None

    @property
    def input_tokens(self) -> int:
        return sum(c.input_tokens for c in self.call_usages)

    @property
    def output_tokens_est(self) -> int:
        return sum(c.output_tokens_est for c in self.call_usages)

    @property
    def total_tokens_est(self) -> int:
        return self.input_tokens + self.output_tokens_est


def get_encoding(model_name: str, fallback_encoding: str):
    try:
        import tiktoken
    except ImportError as e:
        raise ImportError(
            "tiktoken is required for --usage-source estimate. Install with: pip install tiktoken"
        ) from e

    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding(fallback_encoding)


def count_chat_tokens(encoding, system_prompt: str, user_prompt: str) -> int:
    # Approximation based on OpenAI chat format framing.
    tokens_per_message = 3
    reply_priming_tokens = 3

    total = 0
    total += tokens_per_message + len(encoding.encode("system")) + len(encoding.encode(system_prompt))
    total += tokens_per_message + len(encoding.encode("user")) + len(encoding.encode(user_prompt))
    total += reply_priming_tokens
    return total


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


def estimate_sample_usage(
    encoding,
    sample_id: str,
    language: str,
    problem_statement: str,
    student_code: str,
    mode: str,
    run_both_assessments: bool,
    assumed_binary_analysis_output_tokens: int,
    binary_analysis_output_tokens_est: int,
    binary_summary_output_tokens_est: int,
    taxonomy_output_tokens_est: int,
    question_index: Optional[int] = None,
) -> SampleUsage:
    call_usages: List[CallUsage] = []

    if mode in {"binary", "integrated"}:
        analyze_prompt = PromptTemplates.format_binary_analyze(
            problem_statement=problem_statement,
            student_code=student_code,
            language=language,
        )
        analyze_input_tokens = count_chat_tokens(
            encoding,
            SYSTEM_PROMPT_BINARY_ASSESSMENT,
            analyze_prompt,
        )
        call_usages.append(
            CallUsage(
                call_name="binary_analyze",
                input_tokens=analyze_input_tokens,
                output_tokens_est=binary_analysis_output_tokens_est,
            )
        )

        summarize_base_prompt = PromptTemplates.format_binary_summarize(analysis_result="")
        summarize_base_input_tokens = count_chat_tokens(
            encoding,
            SYSTEM_PROMPT_BINARY_ASSESSMENT,
            summarize_base_prompt,
        )
        summarize_input_tokens = summarize_base_input_tokens + max(0, assumed_binary_analysis_output_tokens)
        call_usages.append(
            CallUsage(
                call_name="binary_summarize",
                input_tokens=summarize_input_tokens,
                output_tokens_est=binary_summary_output_tokens_est,
            )
        )

    if mode in {"taxonomy", "integrated"}:
        if mode == "taxonomy" or run_both_assessments:
            taxonomy_prompt = PromptTemplates.format_taxonomy(
                problem_statement=problem_statement,
                student_code=student_code,
                reference_code=None,
                language=language,
            )
            taxonomy_input_tokens = count_chat_tokens(
                encoding,
                SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
                taxonomy_prompt,
            )
            call_usages.append(
                CallUsage(
                    call_name="taxonomy",
                    input_tokens=taxonomy_input_tokens,
                    output_tokens_est=taxonomy_output_tokens_est,
                )
            )

    return SampleUsage(
        sample_id=sample_id,
        question_index=question_index,
        call_usages=call_usages,
    )


def format_money(value: float) -> str:
    return f"${value:.6f}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate token usage for HCMUS CodeJudge prompts without calling API."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to hcmus_dataset.csv")
    parser.add_argument("--start", type=int, default=0, help="Start index in CSV rows")
    parser.add_argument("--limit", type=int, default=10, help="Number of rows to estimate")
    parser.add_argument(
        "--mode",
        type=str,
        default="integrated",
        choices=["binary", "taxonomy", "integrated"],
        help="Assessment mode",
    )
    parser.add_argument(
        "--scoring-mode",
        type=str,
        default="whole_exam",
        choices=["whole_exam", "per_question"],
        help="whole_exam or per_question",
    )
    parser.add_argument(
        "--run-both-assessments",
        action="store_true",
        help="For integrated mode: include taxonomy call even if binary may fail",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="Tokenizer model name for tiktoken encoding_for_model",
    )
    parser.add_argument(
        "--fallback-encoding",
        type=str,
        default="cl100k_base",
        help="Fallback tiktoken encoding when model is unknown",
    )

    parser.add_argument(
        "--assumed-binary-analysis-output-tokens",
        type=int,
        default=450,
        help="Estimated tokens of output from binary analyze step (used as input to summarize step)",
    )
    parser.add_argument(
        "--est-binary-analysis-output-tokens",
        type=int,
        default=450,
        help="Estimated completion tokens billed for binary analyze response",
    )
    parser.add_argument(
        "--est-binary-summary-output-tokens",
        type=int,
        default=8,
        help="Estimated completion tokens billed for binary summarize response",
    )
    parser.add_argument(
        "--est-taxonomy-output-tokens",
        type=int,
        default=280,
        help="Estimated completion tokens billed for taxonomy response",
    )

    parser.add_argument(
        "--price-input-per-1m",
        type=float,
        default=0.0,
        help="Input token price per 1M tokens (USD)",
    )
    parser.add_argument(
        "--price-output-per-1m",
        type=float,
        default=0.0,
        help="Output token price per 1M tokens (USD)",
    )

    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional path to save detailed token report as JSON",
    )
    parser.add_argument(
        "--append-jsonl",
        type=Path,
        default=None,
        help="Optional path to append one-line JSON summary for each run",
    )
    parser.add_argument(
        "--token-io-jsonl",
        type=Path,
        default=None,
        help="Optional path to append detailed input/output token logs for verification",
    )
    parser.add_argument(
        "--io-text-jsonl",
        type=Path,
        default=None,
        help="Optional path to append readable prompt input/output text logs",
    )
    parser.add_argument(
        "--usage-source",
        type=str,
        default="estimate",
        choices=["estimate", "real"],
        help="estimate: local token estimation; real: call API and use response usage",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "anthropic", "local", "gemini"],
        help="Provider for --usage-source real",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for local provider in --usage-source real",
    )

    args = parser.parse_args()

    if args.start < 0:
        raise ValueError("--start must be >= 0")
    if args.limit <= 0:
        raise ValueError("--limit must be > 0")

    if args.usage_source == "real" and (args.mode != "taxonomy" or args.scoring_mode != "whole_exam"):
        raise ValueError("--usage-source real currently supports only --mode taxonomy --scoring-mode whole_exam")

    encoding = None
    if args.usage_source == "estimate":
        encoding = get_encoding(args.model, args.fallback_encoding)

    rows = load_rows(args.csv)
    rows = rows[args.start :]
    rows = rows[: args.limit]

    sample_usages: List[SampleUsage] = []
    skipped: List[Dict[str, str]] = []
    io_text_samples: List[Dict[str, object]] = []

    llm_client = None
    taxonomy_assessor = None
    if args.usage_source == "real":
        kwargs = {}
        if args.provider == "local" and args.base_url:
            kwargs["base_url"] = args.base_url
        llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, **kwargs)
        taxonomy_assessor = TaxonomyAssessor(llm_client=llm_client)

    run_started_at = time.perf_counter()

    for row in rows:
        row_id = row["id"].strip()
        problem_id = row["problem_id"].strip()
        sample_started_at = time.perf_counter()

        try:
            if args.scoring_mode == "whole_exam":
                language, problem_statement, student_code = build_whole_exam_inputs(row)
                if args.usage_source == "real":
                    assert taxonomy_assessor is not None
                    assert llm_client is not None
                    taxonomy_prompt = PromptTemplates.format_taxonomy(
                        problem_statement=problem_statement,
                        student_code=student_code,
                        reference_code=None,
                        language=language,
                    )
                    result = taxonomy_assessor.assess(
                        problem_statement=problem_statement,
                        student_code=student_code,
                        reference_code=None,
                        language=language,
                    )
                    usage_obj = {}
                    if isinstance(result, dict) and isinstance(result.get("usage"), dict):
                        usage_obj = result.get("usage") or {}
                    if not usage_obj:
                        usage_obj = llm_client.get_last_usage() or {}
                    input_tokens = int(usage_obj.get("input_tokens") or 0)
                    output_tokens = int(usage_obj.get("output_tokens") or 0)
                    if input_tokens == 0 and output_tokens == 0:
                        skipped.append(
                            {
                                "id": row_id,
                                "problem_id": problem_id,
                                "error": "No usage metadata returned by provider for this sample",
                            }
                        )
                    usage = SampleUsage(
                        sample_id=row_id,
                        question_index=None,
                        call_usages=[
                            CallUsage(
                                call_name="taxonomy_real",
                                input_tokens=input_tokens,
                                output_tokens_est=output_tokens,
                            )
                        ],
                    )
                    io_text_samples.append(
                        {
                            "id": row_id,
                            "question_index": None,
                            "language": language,
                            "system_prompt": SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
                            "user_prompt": taxonomy_prompt,
                            "output_raw": result.get("raw_llm_response", "") if isinstance(result, dict) else "",
                            "output_parsed": result if isinstance(result, dict) else {},
                        }
                    )
                else:
                    assert encoding is not None
                    usage = estimate_sample_usage(
                        encoding=encoding,
                        sample_id=row_id,
                        language=language,
                        problem_statement=problem_statement,
                        student_code=student_code,
                        mode=args.mode,
                        run_both_assessments=args.run_both_assessments,
                        assumed_binary_analysis_output_tokens=args.assumed_binary_analysis_output_tokens,
                        binary_analysis_output_tokens_est=args.est_binary_analysis_output_tokens,
                        binary_summary_output_tokens_est=args.est_binary_summary_output_tokens,
                        taxonomy_output_tokens_est=args.est_taxonomy_output_tokens,
                    )
                usage.runtime_seconds = time.perf_counter() - sample_started_at
                sample_usages.append(usage)
            else:
                language = row.get("language", "").strip() or "C++"
                student_dir = DATA_CODE_DIR / row_id
                problem_path = get_problem_path(problem_id)

                if not student_dir.is_dir():
                    raise FileNotFoundError(f"Missing student folder: {student_dir}")
                if not problem_path.is_file():
                    raise FileNotFoundError(f"Missing problem file: {problem_path}")

                problem_text = problem_path.read_text(encoding="utf-8", errors="ignore")
                questions = split_questions(problem_text)
                code_files = list_code_files(student_dir)

                if not code_files:
                    raise FileNotFoundError(f"No code files found in {student_dir}")

                for idx, code_file in enumerate(code_files, start=1):
                    if idx > len(questions):
                        break
                    code_text = code_file.read_text(encoding="utf-8", errors="ignore")
                    question_text = questions[idx - 1]
                    _ = parse_question_max(question_text)

                    usage = estimate_sample_usage(
                        encoding=encoding,
                        sample_id=row_id,
                        language=language,
                        problem_statement=question_text,
                        student_code=code_text,
                        mode=args.mode,
                        run_both_assessments=args.run_both_assessments,
                        assumed_binary_analysis_output_tokens=args.assumed_binary_analysis_output_tokens,
                        binary_analysis_output_tokens_est=args.est_binary_analysis_output_tokens,
                        binary_summary_output_tokens_est=args.est_binary_summary_output_tokens,
                        taxonomy_output_tokens_est=args.est_taxonomy_output_tokens,
                        question_index=idx,
                    )
                    usage.runtime_seconds = time.perf_counter() - sample_started_at
                    sample_usages.append(usage)

        except Exception as e:
            skipped.append({"id": row_id, "problem_id": problem_id, "error": str(e)})

    if not sample_usages:
        raise RuntimeError("No valid samples to estimate. Check input paths and arguments.")

    run_elapsed_seconds = time.perf_counter() - run_started_at

    total_input_tokens = sum(s.input_tokens for s in sample_usages)
    total_output_tokens_est = sum(s.output_tokens_est for s in sample_usages)
    total_tokens_est = total_input_tokens + total_output_tokens_est

    avg_input_tokens = total_input_tokens / len(sample_usages)
    avg_output_tokens_est = total_output_tokens_est / len(sample_usages)
    avg_total_tokens_est = total_tokens_est / len(sample_usages)

    runtime_values = [s.runtime_seconds for s in sample_usages if isinstance(s.runtime_seconds, (int, float))]
    total_runtime_seconds = sum(runtime_values)
    avg_runtime_seconds = (total_runtime_seconds / len(runtime_values)) if runtime_values else 0.0

    call_breakdown: Dict[str, Dict[str, float]] = {}
    for sample in sample_usages:
        for call in sample.call_usages:
            if call.call_name not in call_breakdown:
                call_breakdown[call.call_name] = {
                    "count": 0,
                    "input_tokens": 0,
                    "output_tokens_est": 0,
                }
            call_breakdown[call.call_name]["count"] += 1
            call_breakdown[call.call_name]["input_tokens"] += call.input_tokens
            call_breakdown[call.call_name]["output_tokens_est"] += call.output_tokens_est

    for call_name, stats in call_breakdown.items():
        stats["avg_input_tokens"] = stats["input_tokens"] / stats["count"]
        stats["avg_output_tokens_est"] = stats["output_tokens_est"] / stats["count"]

    input_cost = (total_input_tokens / 1_000_000.0) * max(0.0, args.price_input_per_1m)
    output_cost = (total_output_tokens_est / 1_000_000.0) * max(0.0, args.price_output_per_1m)
    total_cost = input_cost + output_cost

    report = {
        "config": {
            "csv": str(args.csv),
            "start": args.start,
            "limit": args.limit,
            "mode": args.mode,
            "scoring_mode": args.scoring_mode,
            "run_both_assessments": args.run_both_assessments,
            "model": args.model,
            "fallback_encoding": args.fallback_encoding,
            "assumed_binary_analysis_output_tokens": args.assumed_binary_analysis_output_tokens,
            "est_binary_analysis_output_tokens": args.est_binary_analysis_output_tokens,
            "est_binary_summary_output_tokens": args.est_binary_summary_output_tokens,
            "est_taxonomy_output_tokens": args.est_taxonomy_output_tokens,
            "price_input_per_1m": args.price_input_per_1m,
            "price_output_per_1m": args.price_output_per_1m,
            "usage_source": args.usage_source,
            "provider": args.provider,
        },
        "summary": {
            "valid_samples": len(sample_usages),
            "skipped_samples": len(skipped),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens_est": total_output_tokens_est,
            "total_tokens_est": total_tokens_est,
            "avg_input_tokens_per_sample": avg_input_tokens,
            "avg_output_tokens_est_per_sample": avg_output_tokens_est,
            "avg_total_tokens_est_per_sample": avg_total_tokens_est,
            "total_runtime_seconds": total_runtime_seconds,
            "avg_runtime_seconds_per_sample": avg_runtime_seconds,
            "run_elapsed_seconds": run_elapsed_seconds,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
        },
        "call_breakdown": call_breakdown,
        "samples": [
            {
                "id": s.sample_id,
                "question_index": s.question_index,
                "input_tokens": s.input_tokens,
                "output_tokens_est": s.output_tokens_est,
                "total_tokens_est": s.total_tokens_est,
                "runtime_seconds": s.runtime_seconds,
                "calls": [
                    {
                        "name": c.call_name,
                        "input_tokens": c.input_tokens,
                        "output_tokens_est": c.output_tokens_est,
                    }
                    for c in s.call_usages
                ],
            }
            for s in sample_usages
        ],
        "skipped": skipped,
    }

    print("=== Token Estimation Summary ===")
    print(f"Valid samples: {len(sample_usages)}")
    print(f"Skipped samples: {len(skipped)}")
    print(f"Total input tokens: {total_input_tokens}")
    print(f"Total output tokens (est): {total_output_tokens_est}")
    print(f"Total tokens (est): {total_tokens_est}")
    print(f"Avg input tokens/sample: {avg_input_tokens:.2f}")
    print(f"Avg output tokens/sample (est): {avg_output_tokens_est:.2f}")
    print(f"Avg total tokens/sample (est): {avg_total_tokens_est:.2f}")
    print(f"Total runtime (s): {total_runtime_seconds:.2f}")
    print(f"Avg runtime/sample (s): {avg_runtime_seconds:.2f}")
    print(f"Run elapsed (s): {run_elapsed_seconds:.2f}")

    if args.price_input_per_1m > 0 or args.price_output_per_1m > 0:
        print("--- Cost Estimation (USD) ---")
        print(f"Input cost: {format_money(input_cost)}")
        print(f"Output cost: {format_money(output_cost)}")
        print(f"Total cost: {format_money(total_cost)}")

    print("--- Call Breakdown ---")
    for call_name, stats in sorted(call_breakdown.items()):
        print(
            f"{call_name}: count={int(stats['count'])}, "
            f"avg_input={stats['avg_input_tokens']:.2f}, "
            f"avg_output_est={stats['avg_output_tokens_est']:.2f}"
        )

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Detailed report written to: {args.json_output}")

    if args.append_jsonl:
        args.append_jsonl.parent.mkdir(parents=True, exist_ok=True)
        append_record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "config": report["config"],
            "summary": report["summary"],
            "call_breakdown": report["call_breakdown"],
            "sample_ids": [s.sample_id for s in sample_usages],
            "skipped": report["skipped"],
        }
        with args.append_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(append_record, ensure_ascii=False) + "\n")
        print(f"Appended run summary to: {args.append_jsonl}")

    if args.token_io_jsonl:
        args.token_io_jsonl.parent.mkdir(parents=True, exist_ok=True)
        token_io_record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "token_source": "provider_usage" if args.usage_source == "real" else "estimated",
            "usage_source": args.usage_source,
            "provider": args.provider,
            "model": args.model,
            "start": args.start,
            "limit": args.limit,
            "totals": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens_est,
                "total_tokens": total_tokens_est,
                "runtime_seconds": total_runtime_seconds,
                "total_cost_usd": total_cost,
            },
            "samples": [
                {
                    "id": s.sample_id,
                    "question_index": s.question_index,
                    "input_tokens": s.input_tokens,
                    "output_tokens": s.output_tokens_est,
                    "total_tokens": s.total_tokens_est,
                    "runtime_seconds": s.runtime_seconds,
                }
                for s in sample_usages
            ],
            "skipped": skipped,
        }
        with args.token_io_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(token_io_record, ensure_ascii=False) + "\n")
        print(f"Appended token input/output log to: {args.token_io_jsonl}")

    if args.io_text_jsonl:
        args.io_text_jsonl.parent.mkdir(parents=True, exist_ok=True)
        io_record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "usage_source": args.usage_source,
            "provider": args.provider,
            "model": args.model,
            "start": args.start,
            "limit": args.limit,
            "samples": io_text_samples,
        }
        with args.io_text_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(io_record, ensure_ascii=False) + "\n")
        print(f"Appended readable input/output log to: {args.io_text_jsonl}")


if __name__ == "__main__":
    main()
