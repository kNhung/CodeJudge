#!/usr/bin/env python3
import argparse

def humaneval_command(args):
    from evaluation.humaneval import code_score as hv

    hv.router(
        args.test_case,
        args.model,
        args.step,
        args.temperature,
        args.with_prefix,
        args.return_type,
        args.num_samples,
        args.overwrite,
        analyze_prompt=None if args.analyze_prompt is None else args.analyze_prompt,
        compare_prompt=None if args.compare_prompt is None else args.compare_prompt,
        file_name=None,
    )


def conala_command(args):
    from evaluation.conala import code_score as cs

    cs.router(
        args.model,
        args.step,
        args.analyze_prompt,
        args.compare_prompt,
        args.temperature,
        args.return_type,
        args.num_samples,
        args.start_index,
    )


def main():
    parser = argparse.ArgumentParser(description="Unified evaluator for datasets")
    subparsers = parser.add_subparsers(dest="dataset", required=True)

    # HumanEval
    p_h = subparsers.add_parser("humaneval")
    p_h.add_argument("--test_case", type=str, required=True)
    p_h.add_argument("--model", type=str, default="gpt-3.5-turbo")
    p_h.add_argument("--step", type=int, default=1)
    p_h.add_argument("--analyze_prompt", type=int, default=None)
    p_h.add_argument("--compare_prompt", type=int, default=0)
    p_h.add_argument("--temperature", type=float, default=0)
    p_h.add_argument("--with_prefix", action="store_true")
    p_h.add_argument("--return_type", type=str, default="bool")
    p_h.add_argument("--num_samples", type=int, default=1)
    p_h.add_argument("--overwrite", action="store_true")
    p_h.set_defaults(func=humaneval_command)

    # CoNaLa
    p_c = subparsers.add_parser("conala")
    p_c.add_argument("--model", type=str, default="gpt-3.5-turbo")
    p_c.add_argument("--step", type=int, default=1)
    p_c.add_argument("--analyze_prompt", type=int, default=0)
    p_c.add_argument("--compare_prompt", type=int, default=0)
    p_c.add_argument("--temperature", type=float, default=0)
    p_c.add_argument("--return_type", type=str, default="bool")
    p_c.add_argument("--num_samples", type=int, default=1)
    p_c.add_argument("--start_index", type=int, default=0)
    p_c.set_defaults(func=conala_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
