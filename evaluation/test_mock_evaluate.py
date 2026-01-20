import os
import json
import argparse
import importlib.util
from pathlib import Path

# Load evaluate_student.py as a module by file path (avoid package import issues)
module_path = Path(__file__).parent / "evaluate_student.py"
spec = importlib.util.spec_from_file_location("evaluate_student", str(module_path))
evaluate_student = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluate_student)


def test_mock_evaluate_creates_output(tmp_path):
    # Use the example student file included in the repo
    example_file = Path(__file__).parent / "example_student.py"

    args = argparse.Namespace(
        problem_id=None,
        problem_text="Return the sum of a list of numbers",
        student_code_file=str(example_file),
        student_code_text=None,
        language="python",
        model="gpt-3.5-turbo",
        step=1,
        compare_prompt=0,
        analyze_prompt=0,
        temperature=0.0,
        return_type="bool",
        with_prefix=False,
        mock=True,
        max_tokens=1024,
        analyze_max_tokens=64,
    )

    # Ensure output directory exists and is empty for the test
    out_dir = Path("./output/humaneval/student_evals")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run the mock evaluation
    evaluate_student.evaluate_single(args)

    # Find the most recent file in the student_evals directory
    files = sorted(out_dir.glob("eval-*.json"))
    assert files, "No evaluation output files created"
    latest = files[-1]

    with latest.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Basic assertions about the mock output
    assert data.get("model") == "MOCK"
    assert "score" in data
    assert data.get("code") is not None

    # Cleanup (optional): remove the test file created
    try:
        latest.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    test_mock_evaluate_creates_output(Path.cwd())
