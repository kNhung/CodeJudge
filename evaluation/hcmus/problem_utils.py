import re
from pathlib import Path

QUESTION_SPLIT = re.compile(r"(?=(?:Câu|Bài)\s+\d+)", re.IGNORECASE)
QUESTION_HEADER = re.compile(
    r"^(?:Câu|Bài)\s+(\d+)[\.\s]*\((\d+)đ\)\s*:?\s*",
    re.IGNORECASE | re.MULTILINE,
)


def parse_problem_questions(problem_text: str) -> list[dict]:
    parts = QUESTION_SPLIT.split(problem_text.strip())
    parts = [part.strip() for part in parts if part.strip()]

    questions = []
    for part in parts:
        match = QUESTION_HEADER.match(part)
        if not match:
            continue
        questions.append(
            {
                "index": int(match.group(1)),
                "weight": int(match.group(2)),
                "intent": part[match.end() :].strip(),
            }
        )
    return questions


def extract_question_number(filename: str) -> int:
    match = re.search(r"(\d+)", Path(filename).stem)
    if not match:
        raise ValueError(f"Cannot extract question number from filename: {filename}")
    return int(match.group(1))


def load_question_codes(student_dir: Path) -> dict[int, dict]:
    codes = {}
    for file_path in sorted(student_dir.glob("*.cpp"), key=lambda path: path.name.lower()):
        index = extract_question_number(file_path.name)
        codes[index] = {
            "file": file_path.name,
            "code": file_path.read_text(encoding="utf-8", errors="replace"),
        }
    return codes


def build_questions_payload(problem_text: str, student_dir: Path) -> list[dict]:
    parsed_questions = parse_problem_questions(problem_text)
    code_by_index = load_question_codes(student_dir)

    questions = []
    for question in parsed_questions:
        index = question["index"]
        code_entry = code_by_index.get(index)
        if code_entry is None:
            code_entry = {
                "file": f"missing_question_{index}.cpp",
                "code": "",
            }
        questions.append(
            {
                "index": index,
                "weight": question["weight"],
                "intent": question["intent"],
                "file": code_entry["file"],
                "code": code_entry["code"],
            }
        )
    return questions


def aggregate_question_scores(question_results: list[dict]) -> float:
    valid = [
        item
        for item in question_results
        if item.get("code_gpt_score") is not None and item["code_gpt_score"] >= 0
    ]
    if not valid:
        return -1.0

    total_weight = sum(item["weight"] for item in valid)
    weighted_sum = sum(item["code_gpt_score"] * item["weight"] for item in valid)
    return weighted_sum / total_weight
