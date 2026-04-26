import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core import LLMFactory, TaxonomyAssessor
from codejudge.core.prompts import PromptTemplates, SYSTEM_PROMPT_TAXONOMY_ASSESSMENT

DEFAULT_DATA = REPO_ROOT / "evaluation" / "data" / "conala" / "conala.json"
DEFAULT_CASES = ["baseline", "tranx-annot", "best-tranx", "best-tranx-rerank", "codex"]


def parse_cases(raw: str) -> List[str]:
    cases = [x.strip() for x in raw.split(",") if x.strip()]
    return cases if cases else DEFAULT_CASES


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate token/time for Conala using taxonomy assessor")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to conala.json")
    parser.add_argument("--start", type=int, default=0, help="Start index in dataset")
    parser.add_argument("--limit", type=int, default=10, help="Number of examples to process")
    parser.add_argument(
        "--cases",
        type=str,
        default=",".join(DEFAULT_CASES),
        help="Comma-separated prediction fields to evaluate",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="gemini",
        choices=["openai", "anthropic", "local", "gemini"],
        help="LLM provider",
    )
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="Model name")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL for local provider")
    parser.add_argument("--price-input-per-1m", type=float, default=0.0, help="Input token price per 1M")
    parser.add_argument("--price-output-per-1m", type=float, default=0.0, help="Output token price per 1M")
    parser.add_argument("--json-output", type=Path, default=None, help="Write full report as JSON")
    parser.add_argument("--append-jsonl", type=Path, default=None, help="Append run summary as JSONL")
    parser.add_argument(
        "--token-io-jsonl",
        type=Path,
        default=None,
        help="Append token input/output log as JSONL",
    )
    parser.add_argument(
        "--io-text-jsonl",
        type=Path,
        default=None,
        help="Append readable prompt input/output text logs as JSONL",
    )

    args = parser.parse_args()

    if args.start < 0:
        raise ValueError("--start must be >= 0")
    if args.limit <= 0:
        raise ValueError("--limit must be > 0")

    if not args.data.is_file():
        raise FileNotFoundError(f"Missing data file: {args.data}")

    cases = parse_cases(args.cases)

    with args.data.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data[args.start : args.start + args.limit]
    if not rows:
        raise RuntimeError("No rows selected. Check --start/--limit")

    kwargs = {}
    if args.provider == "local" and args.base_url:
        kwargs["base_url"] = args.base_url

    llm_client = LLMFactory.create(provider=args.provider, model_name=args.model, **kwargs)
    assessor = TaxonomyAssessor(llm_client=llm_client)

    run_start = time.perf_counter()
    per_call_records: List[Dict[str, object]] = []
    skipped: List[Dict[str, object]] = []
    io_text_samples: List[Dict[str, object]] = []

    for offset, row in enumerate(rows):
        row_index = args.start + offset
        intent = str(row.get("intent", ""))
        reference = str(row.get("snippet", ""))

        for case in cases:
            student_code = row.get(case)
            if not isinstance(student_code, str):
                skipped.append({"row_index": row_index, "case": case, "error": f"Missing prediction field: {case}"})
                continue

            taxonomy_prompt = PromptTemplates.format_taxonomy(
                problem_statement=intent,
                student_code=student_code,
                reference_code=reference,
                language="Python",
            )

            call_start = time.perf_counter()
            try:
                result = assessor.assess(
                    problem_statement=intent,
                    student_code=student_code,
                    reference_code=reference,
                    language="Python",
                )
                usage = result.get("usage", {}) if isinstance(result, dict) else {}
                if not usage:
                    usage = llm_client.get_last_usage() or {}
                input_tokens = int(usage.get("input_tokens") or 0)
                output_tokens = int(usage.get("output_tokens") or 0)

                io_text_samples.append(
                    {
                        "row_index": row_index,
                        "case": case,
                        "language": "Python",
                        "system_prompt": SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
                        "user_prompt": taxonomy_prompt,
                        "output_raw": result.get("raw_llm_response", "") if isinstance(result, dict) else "",
                        "output_parsed": result if isinstance(result, dict) else {},
                    }
                )
            except Exception as e:
                skipped.append({"row_index": row_index, "case": case, "error": str(e)})
                input_tokens = 0
                output_tokens = 0

            runtime_seconds = time.perf_counter() - call_start

            per_call_records.append(
                {
                    "row_index": row_index,
                    "case": case,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "runtime_seconds": runtime_seconds,
                }
            )

    run_elapsed = time.perf_counter() - run_start

    valid_calls = [r for r in per_call_records if (r["input_tokens"] > 0 or r["output_tokens"] > 0)]
    total_input = sum(r["input_tokens"] for r in valid_calls)
    total_output = sum(r["output_tokens"] for r in valid_calls)
    total_tokens = total_input + total_output
    total_runtime = sum(float(r["runtime_seconds"]) for r in per_call_records)

    calls_count = len(per_call_records)
    valid_count = len(valid_calls)

    avg_input = total_input / valid_count if valid_count else 0.0
    avg_output = total_output / valid_count if valid_count else 0.0
    avg_total = total_tokens / valid_count if valid_count else 0.0
    avg_runtime = total_runtime / calls_count if calls_count else 0.0

    input_cost = (total_input / 1_000_000.0) * max(0.0, args.price_input_per_1m)
    output_cost = (total_output / 1_000_000.0) * max(0.0, args.price_output_per_1m)
    total_cost = input_cost + output_cost

    report = {
        "config": {
            "data": str(args.data),
            "start": args.start,
            "limit": args.limit,
            "cases": cases,
            "provider": args.provider,
            "model": args.model,
            "price_input_per_1m": args.price_input_per_1m,
            "price_output_per_1m": args.price_output_per_1m,
        },
        "summary": {
            "rows_selected": len(rows),
            "calls_total": calls_count,
            "calls_valid_usage": valid_count,
            "calls_skipped": len(skipped),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "avg_input_tokens_per_call": avg_input,
            "avg_output_tokens_per_call": avg_output,
            "avg_total_tokens_per_call": avg_total,
            "total_runtime_seconds": total_runtime,
            "avg_runtime_seconds_per_call": avg_runtime,
            "run_elapsed_seconds": run_elapsed,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
        },
        "calls": per_call_records,
        "skipped": skipped,
    }

    print("=== Conala Token/Time Summary ===")
    print(f"Rows selected: {len(rows)}")
    print(f"Calls total: {calls_count}")
    print(f"Calls with usage: {valid_count}")
    print(f"Calls skipped: {len(skipped)}")
    print(f"Total input tokens: {total_input}")
    print(f"Total output tokens: {total_output}")
    print(f"Total tokens: {total_tokens}")
    print(f"Avg input/call: {avg_input:.2f}")
    print(f"Avg output/call: {avg_output:.2f}")
    print(f"Avg total/call: {avg_total:.2f}")
    print(f"Total runtime (s): {total_runtime:.2f}")
    print(f"Avg runtime/call (s): {avg_runtime:.2f}")
    print(f"Run elapsed (s): {run_elapsed:.2f}")

    if args.price_input_per_1m > 0 or args.price_output_per_1m > 0:
        print("--- Cost (USD) ---")
        print(f"Input: ${input_cost:.6f}")
        print(f"Output: ${output_cost:.6f}")
        print(f"Total: ${total_cost:.6f}")

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote JSON report: {args.json_output}")

    if args.append_jsonl:
        args.append_jsonl.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "config": report["config"],
            "summary": report["summary"],
            "skipped": skipped,
        }
        with args.append_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Appended summary JSONL: {args.append_jsonl}")

    if args.token_io_jsonl:
        args.token_io_jsonl.parent.mkdir(parents=True, exist_ok=True)
        token_io_record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "token_source": "provider_usage",
            "provider": args.provider,
            "model": args.model,
            "start": args.start,
            "limit": args.limit,
            "cases": cases,
            "totals": {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_tokens,
                "runtime_seconds": total_runtime,
                "total_cost_usd": total_cost,
            },
            "calls": per_call_records,
            "skipped": skipped,
        }
        with args.token_io_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(token_io_record, ensure_ascii=False) + "\n")
        print(f"Appended token input/output log: {args.token_io_jsonl}")

    if args.io_text_jsonl:
        args.io_text_jsonl.parent.mkdir(parents=True, exist_ok=True)
        io_record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "provider": args.provider,
            "model": args.model,
            "start": args.start,
            "limit": args.limit,
            "cases": cases,
            "samples": io_text_samples,
        }
        with args.io_text_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(io_record, ensure_ascii=False) + "\n")
        print(f"Appended readable input/output log: {args.io_text_jsonl}")


if __name__ == "__main__":
    main()
