import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Average token/time/price from Conala run JSONL")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("evaluation/conala/output/token_time_runs.jsonl"),
        help="Path to JSONL created by estimate_token_time.py --append-jsonl",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    rows = []
    with args.input.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not rows:
        raise RuntimeError("No valid JSON rows found")

    def avg(summary_key: str) -> float:
        vals = []
        for row in rows:
            summary = row.get("summary", {})
            val = summary.get(summary_key)
            if isinstance(val, (int, float)):
                vals.append(float(val))
        return sum(vals) / len(vals) if vals else 0.0

    print(f"Records: {len(rows)}")
    print(f"Avg input tokens/call: {avg('avg_input_tokens_per_call'):.2f}")
    print(f"Avg output tokens/call: {avg('avg_output_tokens_per_call'):.2f}")
    print(f"Avg total tokens/call: {avg('avg_total_tokens_per_call'):.2f}")
    print(f"Avg runtime/call (s): {avg('avg_runtime_seconds_per_call'):.2f}")
    print(f"Avg total cost/run (USD): {avg('total_cost_usd'):.6f}")


if __name__ == "__main__":
    main()
