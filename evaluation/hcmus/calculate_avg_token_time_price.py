import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute average token, time, and price from token_time_runs.jsonl")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("evaluation/hcmus/output/token_time_runs.jsonl"),
        help="Path to JSONL run log",
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
        raise RuntimeError("No valid JSON records found")

    def avg(key: str, default: float = 0.0) -> float:
        values = []
        for r in rows:
            summary = r.get("summary", {})
            val = summary.get(key, default)
            if isinstance(val, (int, float)):
                values.append(float(val))
        return sum(values) / len(values) if values else 0.0

    avg_input_tokens = avg("total_input_tokens")
    avg_output_tokens = avg("total_output_tokens_est")
    avg_total_tokens = avg("total_tokens_est")
    avg_runtime_seconds = avg("total_runtime_seconds")
    avg_total_cost_usd = avg("total_cost_usd")

    print(f"Records: {len(rows)}")
    print(f"Avg input tokens: {avg_input_tokens:.2f}")
    print(f"Avg output tokens: {avg_output_tokens:.2f}")
    print(f"Avg total tokens: {avg_total_tokens:.2f}")
    print(f"Avg time (seconds): {avg_runtime_seconds:.2f}")
    print(f"Avg price (USD): {avg_total_cost_usd:.6f}")


if __name__ == "__main__":
    main()
