import os
import json
import argparse

from scipy import stats

hcmus_test_cases = ["submission"]

RETURN_TYPE_SCALE = {
    "helpful_score": 10.0,
    "0_to_4_score_usefulness": 2.5,
    "0_to_4_score_functional_correctness": 2.5,
    "score": 10.0,
    "inconsistency_level": 10.0,
    "error_level": 10.0,
}


def normalize_prediction(score, return_type):
    if score == -1:
        return None
    scale = RETURN_TYPE_SCALE.get(return_type, 2.5)
    return float(score) * scale


def print_number(kendalltau, pearsonr, spearmanr, length=None):
    print("{:.3f}".format(round(kendalltau, 3)), end=" | ")
    print("{:.3f}".format(round(pearsonr, 3)), end=" | ")
    print("{:.3f}".format(round(spearmanr, 3)), end=" | ")
    if length:
        print(length, end=" | ")
    print("")


def print_correlation(file_name, return_type=None):
    print(file_name.split("/")[-1], end=" | ")
    references, predictions = [], []
    invalid_cnt = 0
    question_invalid_cnt = 0
    question_total_cnt = 0

    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    if return_type is None:
        return_type = data.get("parameters", {}).get("return_type")
    per_question = data.get("parameters", {}).get("per_question", False)

    for item in data["data"]:
        submission_score = item["code_gpt_score"]["submission"]
        if per_question and "questions" in submission_score:
            for question in submission_score["questions"].values():
                question_total_cnt += 1
                if float(question["code_gpt_score"]) == -1:
                    question_invalid_cnt += 1

        raw_score = float(submission_score["code_gpt_score"])
        if raw_score == -1:
            invalid_cnt += 1
            continue

        references.append(float(item["expect_grade"]))
        if return_type:
            prediction = normalize_prediction(raw_score, return_type)
            if prediction is None:
                invalid_cnt += 1
                continue
            predictions.append(prediction)
        else:
            predictions.append(raw_score)

    length = len(references)
    if length < 2:
        print_number(float("nan"), float("nan"), float("nan"), length)
        print("note: correlation requires at least 2 valid samples")
    else:
        kendalltau = stats.kendalltau(references, predictions).statistic
        pearsonr = stats.pearsonr(references, predictions).statistic
        spearmanr = stats.spearmanr(references, predictions).statistic
        print_number(kendalltau, pearsonr, spearmanr, length)
    if invalid_cnt:
        print(f"invalid_cnt: {invalid_cnt}/{len(data['data'])}")
    if per_question and question_total_cnt:
        valid_q = question_total_cnt - question_invalid_cnt
        print(
            f"question_parse_rate: {valid_q}/{question_total_cnt} "
            f"({100 * valid_q / question_total_cnt:.1f}%)"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", type=str, default=None)
    parser.add_argument(
        "--return_type",
        type=str,
        default=None,
        help="Used to rescale model scores to the 0-10 HCMUS grade scale.",
    )
    args = parser.parse_args()

    if args.file_name:
        print_correlation(f"output/hcmus/{args.file_name}", args.return_type)
        return

    file_list = []
    for file_name in os.listdir("output/hcmus"):
        if file_name.endswith(".json"):
            file_list.append(file_name)

    file_list.sort()
    for file_name in file_list:
        print_correlation(f"output/hcmus/{file_name}", args.return_type)


if __name__ == "__main__":
    main()
