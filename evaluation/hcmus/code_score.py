import os
import json
import sys
import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from code_model_score import form_filling, answer_to_score, load_model
from prompts import single_step_prompt, dual_step_prompt
from problem_utils import aggregate_question_scores

from tqdm import tqdm


hcmus_test_cases = ["submission"]


def read_data(
    model,
    temperature,
    file_name,
    return_type,
    limit=0,
    per_question=False,
    compare_prompt=None,
    analyze_prompt=None,
):
    with open("./data/hcmus/hcmus.json", encoding="utf-8") as f:
        data = json.load(f)

    if limit > 0:
        data = data[:limit]

    if os.path.exists(f"./output/hcmus/{file_name}"):
        with open(f"./output/hcmus/{file_name}", encoding="utf-8") as f:
            out = json.load(f)
    else:
        parameters = {
            "model": model,
            "temperature": temperature,
            "return_type": return_type,
            "limit": limit,
            "per_question": per_question,
        }
        if analyze_prompt is not None:
            parameters["analyze_prompt"] = analyze_prompt
            parameters["compare_prompt"] = compare_prompt
        else:
            parameters["compare_prompt"] = compare_prompt
        out = {"parameters": parameters, "data": []}

    return data, out


def build_form_info(problem_text, code, language="C++", reference="", include_language=False):
    info = {
        "CODE1": code,
        "CODE2": reference,
        "PROBLEM": problem_text,
    }
    if include_language:
        info["LANGUAGE"] = language
        info["EXAMPLE"] = ""
    return info


def format_question_problem(question: dict) -> str:
    return f"Câu {question['index']} ({question['weight']}đ):\n{question['intent']}"


def score_single_question(
    model,
    compare_prompt,
    terminators,
    pipeline,
    temperature,
    question,
    language,
    return_type,
    use_openrouter,
):
    problem_text = format_question_problem(question)
    code_gpt_answer = form_filling(
        model,
        compare_prompt,
        terminators,
        pipeline,
        temperature,
        info=build_form_info(problem_text, question["code"], language=language),
        use_openrouter=use_openrouter,
    )
    return {
        "index": question["index"],
        "weight": question["weight"],
        "file": question["file"],
        "code_gpt_score": float(answer_to_score(code_gpt_answer, return_type)),
        "comparison": code_gpt_answer,
    }


def find_existing_item(out_data, item_id):
    for existing in out_data:
        if existing["id"] == item_id:
            return existing
    return None


def resume_single_step_per_question_workflow(
    model,
    compare_prompt,
    temperature,
    file_name,
    return_type,
    limit,
    use_openrouter,
):
    data, out = read_data(
        model,
        temperature,
        file_name,
        return_type,
        limit=limit,
        per_question=True,
        compare_prompt=compare_prompt,
    )

    terminators, pipeline = load_model(model)

    for item in tqdm(data):
        existing = find_existing_item(out["data"], item["id"])
        if existing is None:
            existing = {
                "id": item["id"],
                "problem_id": item["problem_id"],
                "student_id": item["student_id"],
                "intent": item["intent"],
                "submission": item["submission"],
                "expect_grade": item["expect_grade"],
                "code_gpt_score": {"submission": {"questions": {}}},
            }
            out["data"].append(existing)

        questions_dict = existing["code_gpt_score"]["submission"]["questions"]
        expected_keys = {str(question["index"]) for question in item["questions"]}
        if expected_keys.issubset(questions_dict.keys()):
            continue

        for question in item["questions"]:
            key = str(question["index"])
            if key in questions_dict:
                continue

            result = score_single_question(
                model,
                compare_prompt,
                terminators,
                pipeline,
                temperature,
                question,
                item.get("language", "C++"),
                return_type,
                use_openrouter,
            )
            questions_dict[key] = result

            question_results = list(questions_dict.values())
            existing["code_gpt_score"]["submission"]["code_gpt_score"] = float(
                aggregate_question_scores(question_results)
            )
            existing["code_gpt_score"]["submission"]["comparison"] = question_results

            os.makedirs("./output/hcmus/", exist_ok=True)
            with open("./output/hcmus/" + file_name, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=4, ensure_ascii=False)


def single_step_workflow(
    model,
    compare_prompt,
    temperature,
    file_name,
    return_type,
    limit,
    use_openrouter,
):
    data, out = read_data(
        model,
        temperature,
        file_name,
        return_type,
        limit=limit,
        per_question=False,
        compare_prompt=compare_prompt,
    )
    if len(out["data"]) == len(data):
        return

    terminators, pipeline = load_model(model)
    for item in tqdm(data[len(out["data"]) :]):
        output_item = {
            "id": item["id"],
            "problem_id": item["problem_id"],
            "student_id": item["student_id"],
            "intent": item["intent"],
            "submission": item["submission"],
            "expect_grade": item["expect_grade"],
            "code_gpt_score": {},
        }

        code_gpt_answer = form_filling(
            model,
            compare_prompt,
            terminators,
            pipeline,
            temperature,
            info=build_form_info(item["intent"], item["submission"]),
            use_openrouter=use_openrouter,
        )

        output_item["code_gpt_score"]["submission"] = {
            "code_gpt_score": float(answer_to_score(code_gpt_answer, return_type)),
            "comparison": code_gpt_answer,
        }

        out["data"].append(output_item)
        os.makedirs("./output/hcmus/", exist_ok=True)
        with open("./output/hcmus/" + file_name, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=4, ensure_ascii=False)


def dual_step_workflow(
    model,
    analyze_prompt,
    compare_prompt,
    temperature,
    file_name,
    return_type,
    compare_prompt_index,
    limit,
    use_openrouter,
):
    data, out = read_data(
        model,
        temperature,
        file_name,
        return_type,
        limit=limit,
        per_question=False,
        analyze_prompt=analyze_prompt,
        compare_prompt=compare_prompt,
    )
    if len(out["data"]) == len(data):
        return

    include_language = compare_prompt_index >= 2
    terminators, pipeline = load_model(model)
    for item in tqdm(data[len(out["data"]) :]):
        output_item = {
            "id": item["id"],
            "problem_id": item["problem_id"],
            "student_id": item["student_id"],
            "intent": item["intent"],
            "submission": item["submission"],
            "expect_grade": item["expect_grade"],
            "code_gpt_score": {},
        }

        nl_mistakes = form_filling(
            model,
            compare_prompt,
            terminators,
            pipeline,
            temperature,
            info=build_form_info(
                item["intent"],
                item["submission"],
                language=item.get("language", "C++"),
                include_language=include_language,
            ),
            use_openrouter=use_openrouter,
        )
        code_gpt_answer = form_filling(
            model,
            analyze_prompt,
            terminators,
            pipeline,
            temperature,
            info={"MISTAKES": nl_mistakes},
            max_tokens=10,
            use_openrouter=use_openrouter,
        )

        output_item["code_gpt_score"]["submission"] = {
            "code_gpt_score": float(answer_to_score(code_gpt_answer, return_type)),
            "comparison": nl_mistakes,
            "parsed_comparison": code_gpt_answer,
        }

        out["data"].append(output_item)
        os.makedirs("./output/hcmus/", exist_ok=True)
        with open("./output/hcmus/" + file_name, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=4, ensure_ascii=False)


def sanitize_model_name(model):
    return model.replace("/", "-").replace(":", "-")


def build_file_name(
    model,
    step,
    analyze_prompt_index,
    compare_prompt_index,
    temperature,
    limit,
    index,
    per_question=False,
):
    safe_model = sanitize_model_name(model)
    limit_suffix = f"-limit-{limit}" if limit > 0 else ""
    perq_suffix = "-perq" if per_question else ""
    if step == 1:
        return (
            f"{safe_model}-1-{compare_prompt_index}-{temperature}"
            f"{limit_suffix}{perq_suffix}-sample-{index}.json"
        )
    return (
        f"{safe_model}-2-{analyze_prompt_index}-{compare_prompt_index}-"
        f"{temperature}{limit_suffix}{perq_suffix}-sample-{index}.json"
    )


def router(
    model,
    step,
    analyze_prompt_index,
    compare_prompt_index,
    temperature,
    return_type,
    num_samples,
    start_index,
    limit,
    use_openrouter,
    per_question,
):
    for index in range(start_index, start_index + num_samples):
        if step == 1:
            compare_prompt = single_step_prompt[compare_prompt_index]
            file_name = build_file_name(
                model,
                step,
                analyze_prompt_index,
                compare_prompt_index,
                temperature,
                limit,
                index,
                per_question=per_question,
            )
            print(file_name)
            if per_question:
                resume_single_step_per_question_workflow(
                    model,
                    compare_prompt,
                    temperature,
                    file_name,
                    return_type,
                    limit,
                    use_openrouter,
                )
            else:
                single_step_workflow(
                    model,
                    compare_prompt,
                    temperature,
                    file_name,
                    return_type,
                    limit,
                    use_openrouter,
                )
        elif step == 2:
            if per_question:
                raise SystemExit("Per-question scoring currently supports --step 1 only.")
            analyze_prompt = dual_step_prompt["analyze_prompt"][analyze_prompt_index]
            compare_prompt = dual_step_prompt["compare_prompt"][compare_prompt_index]
            file_name = build_file_name(
                model,
                step,
                analyze_prompt_index,
                compare_prompt_index,
                temperature,
                limit,
                index,
                per_question=per_question,
            )
            print(file_name)
            dual_step_workflow(
                model,
                analyze_prompt,
                compare_prompt,
                temperature,
                file_name,
                return_type,
                compare_prompt_index,
                limit,
                use_openrouter,
            )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, default="google/gemini-2.5-flash")
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--analyze_prompt", type=int, default=0)
    parser.add_argument("--compare_prompt", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--return_type", type=str, default="0_to_4_score_usefulness")
    parser.add_argument("--num_samples", type=int, default=1)
    parser.add_argument("--start_index", type=int, default=0)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of HCMUS items to score (0 = all).",
    )
    parser.add_argument(
        "--per_question",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Score each exam question separately and aggregate by weights.",
    )
    parser.add_argument(
        "--use_openrouter",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use OPENROUTER_API_KEY with OpenRouter endpoint.",
    )

    args = parser.parse_args()

    if args.use_openrouter and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is not set in environment/.env")

    router(
        args.model,
        args.step,
        args.analyze_prompt,
        args.compare_prompt,
        args.temperature,
        args.return_type,
        args.num_samples,
        args.start_index,
        args.limit,
        args.use_openrouter,
        args.per_question,
    )


if __name__ == "__main__":
    main()
