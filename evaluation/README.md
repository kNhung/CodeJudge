# HumanEval — Student evaluation helper

This folder contains scripts and prompts to evaluate single student code submissions using the existing HumanEval dataset prompts and LLM adapters.

Main additions:
- `evaluate_student.py` — CLI to evaluate one student submission and save a JSON result.

Quick usage examples

1) Evaluate a student file using a dataset question id (step 1 — direct compare):

```bash
python evaluation/humaneval/evaluate_student.py \
  --problem_id 4 \
  --language python \
  --student_code_file path/to/student.py \
  --model gpt-3.5-turbo \
  --step 1 \
  --return_type bool
```

2) Evaluate inline code text (step 2 — dual step):

```bash
python evaluation/humaneval/evaluate_student.py \
  --problem_text "Return sum of list of numbers" \
  --student_code_text "def f(a): return sum(a)" \
  --model CodeLlama-34b-Instruct \
  --step 2 \
  --compare_prompt 0 \
  --analyze_prompt 0 \
  --return_type bool
```

Notes
- `evaluate_student.py` uses `OPENAI_API_KEY` when running OpenAI models (gpt-3.5/gpt-4). Set it in the environment.
- For local models (CodeLlama / Llama-3) ensure the model weights are available under `./model/` as expected by `code_model_score.load_model()`.
- Results are saved to `./output/humaneval/student_evals/` as JSON.

If you want, I can add a PowerShell example that runs a dry evaluation using a mocked model (no API calls). Want that next? 

PowerShell and mock example

```powershell
# Mock (dry-run) evaluation using the example student file
python evaluation/humaneval/evaluate_student.py \
  --problem_text "Return the sum of a list of numbers" \
  --student_code_file evaluation/humaneval/example_student.py \
  --mock \
  --step 1 \
  --return_type bool
```

Use `--mock` when you don't have `OPENAI_API_KEY` set or local model weights.

New input format: JSON record file

You can provide a single student record as a JSON file with the following fields:

- `language`: (string) programming language, e.g. `python` or `cpp`
- `intent`: (string) the problem statement / prompt
- `snippet`: (string) the student submission code to be graded
- `ground_truth`: (string, optional) reference solution
- `barem`: (object/list, optional) rubric or scoring breakdown
- `grade`: (number, optional) instructor grade

Example (JSONL file): `evaluation/humaneval/sample_student_dataset.jsonl` (two sample records included).

Command using a record file:

```bash
python evaluation/humaneval/evaluate_student.py \
  --record_file evaluation/humaneval/sample_student_dataset.jsonl \
  --mock \
  --step 1 \
  --return_type bool
```

Note: when `--record_file` is provided the script reads a single JSON object. If you have a JSONL file, pass the path to a single-line record or extract a line to a temporary file.
