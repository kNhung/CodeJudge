# HintEval Answer-Agnostic Mode

## Overview

The updated `evaluate_hinteval.py` script now supports **Answer-Agnostic** mode from the HintEval paper (arXiv 2025). This allows evaluating code improvement hints without requiring ground-truth reference code.

## Modes

### 1. Relevance Mode (Original)
Evaluates hints by comparing them to reference code using ROUGE metrics.
- **Requires**: Reference code (answers)
- **Metrics**: ROUGE-L/1/2 (Relevance)
- **Use case**: When you have ground-truth answers

```bash
python evaluate_hinteval.py --mode relevance --rouge-model rougeL
```

### 2. Answer-Agnostic Mode (NEW)
Evaluates hints independently without requiring reference code.
- **Metrics**:
  - **Readability**: Heuristic complexity assessment (0=easy, 1=hard)
  - **Familiarity**: Percentage of common/frequent words (0=unfamiliar, 1=familiar)
- **Use case**: When evaluating system suggestions without ground-truth

```bash
python evaluate_hinteval.py --mode agnostic
```

## Usage

### Basic Answer-Agnostic Evaluation
```bash
python evaluate_hinteval.py --mode agnostic
```

Output: `evaluation/conala/output/hint_eval_agnostic.json`

### With Custom Input/Output
```bash
python evaluate_hinteval.py \
  --mode agnostic \
  --input custom_runs.jsonl \
  --output my_evaluation.json
```

By default, the script now reads the flat Conala summary file:
`evaluation/conala/summary/260409_0841_gemini-2.5-flash_all.jsonl`

### Include Strengths as Hints
```bash
python evaluate_hinteval.py \
  --mode agnostic \
  --include-strengths
```

### Relevance Mode (with answers)
```bash
python evaluate_hinteval.py \
  --mode relevance \
  --rouge-model rougeL
```

## Output Format

### Summary Section
```json
{
  "samples": 30,
  "total_hints": 143,
  "metrics": {
    "readability": {
      "mean": 0.904833,
      "max": 1.0,
      "min": 0.15,
      "count": 143
    },
    "familiarity": {
      "mean": 0.909825,
      "max": 1.0,
      "min": 0.6,
      "count": 143
    }
  }
}
```

### Sample Details
Each sample includes individual hint scores:
```json
{
  "row_index": 0,
  "case": "...",
  "language": "python",
  "hints": ["improvement 1", "fix 1", ...],
  "hints_with_scores": [
    {
      "text": "improvement 1",
      "readability": 0.85,
      "familiarity": 0.92
    },
    ...
  ]
}
```

## Metrics Explanation

### Readability
- **Formula**: Based on average word length and sentence length
- **Range**: 0 (easy, beginner-friendly) to 1 (hard, advanced)
- **Higher value** = More complex, advanced language
- **Lower value** = Simple, beginner-friendly

### Familiarity
- **Formula**: Percentage of common/frequent English words
- **Range**: 0 (unfamiliar) to 1 (very familiar)
- **Higher value** = More common words used
- **Lower value** = More technical/specialized vocabulary

## Common Workflows

### Evaluate System Suggestions (No Ground Truth)
```bash
python evaluate_hinteval.py --mode agnostic --include-strengths
```

### Compare with Reference Code
```bash
python evaluate_hinteval.py --mode relevance
```

### Combine Both Evaluations
```bash
# Run both modes
python evaluate_hinteval.py --mode agnostic --output results_agnostic.json
python evaluate_hinteval.py --mode relevance --output results_relevance.json

# Compare results
```

## Requirements

- `rouge_score`: For relevance metrics
- `hinteval` (optional): Core classes only, no heavy dependencies

Install:
```bash
pip install rouge_score
pip install hinteval --no-deps
```

## Data Format

Input JSONL format:
```json
{
  "source": "baseline",
  "intent": "send a signal `signal.SIGUSR1` to the current process",
  "code_preview": "os.kill(os.getpid(), signal.SIGUSR1)",
  "language": "Python",
  "grade_reference": 0,
  "result": {
    "taxonomy": {
      "quality_score": 1.0,
      "score_breakdown": {
        "idea": 1.0,
        "flow": 0.0,
        "syntax_execution": 0.0,
        "correctness": 0.0,
        "clarity": 0.0
      },
      "strengths": [],
      "improvements": ["Thiếu ý tưởng giải bài"],
      "errors": []
    },
    "summary": {
      "score": 1.0,
      "score_on_4": 0.4
    }
  },
  "example_index": 0
}
```
