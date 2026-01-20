#!/usr/bin/env python3
"""
Lightweight CLI to evaluate a single student's code submission.

Usage examples:
python evaluation/humaneval/evaluate_student.py --problem_text "Return sum" --student_code_text "def f(a): return sum(a)" --model Qwen2.5 --step 2 --barem "{\"style\": 1}"
"""
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_dataset_entry(language, question_id):
    ds_path = f"./data/humaneval/dataset/{language}.json"
    if not os.path.exists(ds_path):
        raise FileNotFoundError(f"Dataset not found: {ds_path}")
    with open(ds_path, "r") as f:
        dataset = json.load(f)
    if str(question_id) not in dataset:
        raise KeyError(f"Question id {question_id} not in dataset for {language}")
    return dataset[str(question_id)]


def read_student_code(args):
    if args.student_code_file:
        with open(args.student_code_file, "r", encoding="utf-8") as f:
            return f.read()
    if args.student_code_text:
        return args.student_code_text
    raise ValueError("Provide either --student_code_file or --student_code_text")


def evaluate_single(args):
    # --- 1. PREPARE INPUTS ---
    student_code = None
    record = None
    
    # Defaults
    problem_text = args.problem_text
    code2 = args.reference_code_text # Reference/Ground Truth from CLI
    barem = None
    grade = args.expected_grade

    # Handle Barem from CLI (JSON String parsing)
    if args.barem:
        try:
            barem = json.loads(args.barem)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Invalid JSON in --barem. Using raw string.")
            barem = args.barem

    # Case A: Load from Record File
    if getattr(args, "record_file", None):
        with open(args.record_file, "r", encoding="utf-8") as f:
            record = json.load(f)
        
        args.language = record.get("language", args.language)
        problem_text = record.get("intent", problem_text)
        student_code = record.get("snippet", None)
        
        # Override CLI args if record has them, otherwise keep CLI
        code2 = record.get("ground_truth", code2)
        barem = record.get("barem", barem)
        grade = record.get("grade", grade)

        if student_code is None:
            raise ValueError("record_file must contain 'snippet' field")
        
        if args.with_prefix and record.get("declaration"):
            code1 = record.get("declaration") + student_code
            if code2:
                code2 = record.get("declaration") + code2
        else:
            code1 = student_code

    # Case B: Load from CLI / Dataset ID
    else:
        student_code = read_student_code(args)
        
        if args.problem_id is not None:
            entry = load_dataset_entry(args.language, args.problem_id)
            problem_text = entry.get("prompt") or entry.get("docstring") or entry.get("description") or entry.get("problem", "")
            canonical = entry.get("canonical_solution", "")
            declaration = entry.get("declaration", "")
            
            if args.with_prefix:
                code2 = declaration + canonical
                code1 = declaration + student_code
            else:
                code2 = canonical
                code1 = student_code
        else:
            # Fully manual CLI mode
            problem_text = problem_text or ""
            code1 = student_code
            # code2 is already set from args.reference_code_text

    # --- 2. MOCK MODE ---
    if args.mock:
        raw = "[MOCK] generated evaluation"
        has_return = ("return" in code1) or ("def " in code1)
        if args.return_type == "bool":
            score = True if has_return else False
        else:
            score = 1.0 if has_return else 0.0

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": "MOCK",
            "step": args.step,
            "return_type": args.return_type,
            "score": score,
            "raw": raw,
            "code": code1,
            "reference": code2,
            "problem": problem_text,
            "barem": barem,
            "grade": grade,
        }

    # --- 3. AI EVALUATION MODE ---
    else:
        # Lazy imports
        from code_model_score import form_filling, answer_to_score, load_model
        from humaneval.prompts import single_step_prompt, dual_step_prompt

        terminators, pipeline = load_model(args.model)

        # Prepare formatting info for Prompt Templates
        # Note: We inject BAREM into the info dict so updated prompts can use it.
        barem_str = json.dumps(barem, indent=2) if isinstance(barem, dict) else str(barem)
        
        common_info = {
            "CODE1": code1,
            "CODE2": code2 if code2 is not None else "",
            "PROBLEM": problem_text,
            "EXAMPLE": "",
            "LANGUAGE": args.language,
            "BAREM": barem_str if barem else "", # New field available for prompts
        }

        if args.step == 1:
            compare_prompt = single_step_prompt[args.compare_prompt]
            
            raw = form_filling(
                args.model,
                compare_prompt,
                terminators,
                pipeline,
                args.temperature,
                info=common_info,
                max_tokens=args.max_tokens,
            )
            score = answer_to_score(raw, args.return_type)
            
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "model": args.model,
                "step": 1,
                "return_type": args.return_type,
                "score": score,
                "raw": raw,
                "code": code1,
                "reference": code2,
                "problem": problem_text,
                "barem": barem,   # Include in output
                "grade": grade    # Include in output
            }

        elif args.step == 2:
            compare_prompt = dual_step_prompt["compare_prompt"][args.compare_prompt]
            analyze_prompt = dual_step_prompt["analyze_prompt"][args.analyze_prompt]

            # Phase 1: Comparison / Mistake Finding
            nl_mistakes = form_filling(
                args.model,
                compare_prompt,
                terminators,
                pipeline,
                args.temperature,
                info=common_info,
                max_tokens=args.max_tokens,
            )

            # Phase 2: Analysis / Scoring
            info_anl = {
                "MISTAKES": nl_mistakes,
                "PROBLEM": problem_text,
                "EXAMPLE": "",
                "BAREM": barem_str if barem else "",
            }

            raw = form_filling(
                args.model,
                analyze_prompt,
                terminators,
                pipeline,
                args.temperature,
                info=info_anl,
                max_tokens=args.analyze_max_tokens,
            )

            score = answer_to_score(raw, args.return_type)
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "model": args.model,
                "step": 2,
                "return_type": args.return_type,
                "score": score,
                "comparison": nl_mistakes,
                "parsed_comparison": raw,
                "code": code1,
                "reference": code2,
                "problem": problem_text,
                "barem": barem,   # Include in output
                "grade": grade    # Include in output
            }

        else:
            raise ValueError("Unsupported step; use 1 or 2")

    # --- 4. OUTPUT ---
    out_dir = f"./output/humaneval/student_evals/"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"eval-{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved to {out_file}")


def main():
    parser = argparse.ArgumentParser()
    
    # Source Group: Defines where the Problem comes from
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--problem_id", type=int, help="Question id from HumanEval dataset")
    group.add_argument("--problem_text", type=str, help="Problem text")
    group.add_argument("--record_file", type=str, help="Path to JSON record file")

    # Code Group: Defines where the Student Code comes from
    code_group = parser.add_mutually_exclusive_group(required=True)
    code_group.add_argument("--student_code_file", type=str, help="Path to student code file")
    code_group.add_argument("--student_code_text", type=str, help="Student code as string")

    # --- NEW ARGUMENTS ---
    parser.add_argument("--reference_code_text", type=str, default=None, help="Reference/Ground Truth code")
    parser.add_argument("--barem", type=str, default=None, help="JSON string representing grading rubric")
    parser.add_argument("--expected_grade", type=float, default=None, help="Human grade for comparison")
    # ---------------------

    parser.add_argument("--language", type=str, default="python")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    parser.add_argument("--step", type=int, default=1, choices=[1, 2])
    parser.add_argument("--compare_prompt", type=int, default=0)
    parser.add_argument("--analyze_prompt", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--return_type", type=str, default="bool")
    parser.add_argument("--with_prefix", action="store_true")
    parser.add_argument("--mock", action="store_true", help="Run in mock/dry-run mode")
    parser.add_argument("--max_tokens", type=int, default=1024)
    parser.add_argument("--analyze_max_tokens", type=int, default=64)

    args = parser.parse_args()
    evaluate_single(args)


if __name__ == "__main__":
    main()