import csv
import json
from pathlib import Path

from problem_utils import build_questions_payload


def load_student_code(student_dir: Path) -> str:
    files = sorted(student_dir.glob("*.cpp"), key=lambda path: path.name.lower())
    parts = []
    for file_path in files:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        parts.append(f"// --- {file_path.name} ---\n{content}")
    return "\n\n".join(parts)


def pre_process_hcmus_data():
    base = Path(__file__).parent
    csv_path = base / "hcmus_dataset.csv"
    problems_dir = base / "problems"
    data_code_dir = base / "data_code"
    out_dir = base.parent / "data" / "hcmus"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = row["id"]
            problem_id = row["problem_id"]
            problem_path = problems_dir / f"{problem_id}.txt"
            student_dir = data_code_dir / row_id

            if not problem_path.exists():
                raise FileNotFoundError(f"Missing problem file: {problem_path}")
            if not student_dir.exists():
                raise FileNotFoundError(f"Missing student code directory: {student_dir}")

            intent = problem_path.read_text(encoding="utf-8")
            submission = load_student_code(student_dir)
            if not submission.strip():
                raise ValueError(f"No C++ files found in {student_dir}")

            questions = build_questions_payload(intent, student_dir)

            out.append(
                {
                    "id": int(row_id),
                    "language": row["language"],
                    "problem_id": problem_id,
                    "student_id": row["student_id"],
                    "intent": intent,
                    "submission": submission,
                    "questions": questions,
                    "expect_grade": float(row["expect_grade"]),
                }
            )

    output_path = out_dir / "hcmus.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

    print(f"Wrote {len(out)} items to {output_path}")


if __name__ == "__main__":
    pre_process_hcmus_data()
