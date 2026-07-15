"""
Extract pre_extracted_factors config from a HCMUS scoring JSONL.

When Agent 1 produces different factor names across students for the same
question, uses majority vote (most common factor list) instead of failing.

Usage:
  python evaluation/hcmus/extract_factors_config.py \\
    --jsonl evaluation/hcmus/output/gemini-parallel-noconfigs.jsonl \\
    --output evaluation/hcmus/configs/noconfig_hcmus_factors.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

QuestionKey = Tuple[str, int]


def load_factor_lists(jsonl_path: Path) -> Dict[QuestionKey, List[Tuple[str, ...]]]:
    by_key: Dict[QuestionKey, List[Tuple[str, ...]]] = defaultdict(list)
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("scoring_mode") != "per_question":
                continue
            result = data.get("result", {})
            factors = result.get("factors") or list((result.get("factor_evaluation") or {}).keys())
            if not factors:
                continue
            key = (str(data.get("problem_id", "")), int(data.get("question_index", 0)))
            by_key[key].append(tuple(factors))
    return dict(by_key)


def extract_majority_config(
    by_key: Dict[QuestionKey, List[Tuple[str, ...]]],
) -> Tuple[Dict[str, Any], List[dict]]:
    config: Dict[str, Any] = {}
    report: List[dict] = []

    for (problem_id, qidx) in sorted(by_key.keys()):
        lists = by_key[(problem_id, qidx)]
        counts = Counter(lists)
        mode, freq = counts.most_common(1)[0]
        total = len(lists)
        unique = len(counts)

        problem = config.setdefault(problem_id, {})
        problem[str(qidx)] = {"pre_extracted_factors": list(mode)}

        entry = {
            "problem_id": problem_id,
            "question_index": qidx,
            "total_records": total,
            "unique_factor_sets": unique,
            "mode_frequency": freq,
            "mode_pct": round(100.0 * freq / total, 1),
            "canonical_factors": list(mode),
        }
        if unique > 1:
            entry["alternatives"] = [
                {"count": c, "factors": list(fs)}
                for fs, c in counts.most_common()
                if fs != mode
            ]
        report.append(entry)

    return config, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract majority-vote factors config from JSONL")
    parser.add_argument("--jsonl", type=Path, required=True, help="Input JSONL from score_with_multi_agent.py")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "configs" / "noconfig_hcmus_factors.json",
        help="Output JSON config path",
    )
    parser.add_argument("--report", type=Path, default=None, help="Optional JSON report of consistency stats")
    args = parser.parse_args()

    if not args.jsonl.is_file():
        raise SystemExit(f"Input not found: {args.jsonl}")

    by_key = load_factor_lists(args.jsonl)
    if not by_key:
        raise SystemExit(f"No per_question records in {args.jsonl}")

    config, report = extract_majority_config(by_key)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"Wrote factors config: {args.output}")
    print(f"Question groups: {len(by_key)}")
    inconsistent = [r for r in report if r["unique_factor_sets"] > 1]
    print(f"Inconsistent groups (majority vote applied): {len(inconsistent)}")
    for r in report:
        flag = " *" if r["unique_factor_sets"] > 1 else ""
        print(
            f"  {r['problem_id']} Q{r['question_index']}: "
            f"{r['mode_frequency']}/{r['total_records']} ({r['mode_pct']}%) mode{flag}"
        )

    if inconsistent:
        print("\nNote: minority factor names in JSONL will NOT match this config.")
        print("For tune/rescore, re-run scoring with --config on this file, or use matching records only.")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Wrote consistency report: {args.report}")


if __name__ == "__main__":
    main()
