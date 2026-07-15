# CodeEval / CodeJudge

Multi-agent auto-grading for programming assignments: **compiler syntax check** → **Agent 1 (factor extract)** → **Agent 2 (factor grade)** → score + suggestions.

Python package name remains `codejudge`. Conda environment name: **`codeeval`**.

## Pipeline

1. **Compiler helper** — real syntax check (Python `compile`, C/C++ `g++ -fsyntax-only`, multi-file folders via temp dir).
2. **Agent 1** — extract independent functional factors from the problem statement (LLM).
3. **Agent 2** — grade each factor 0.0–1.0 (ignores syntax; scored separately).
4. **Scoring** — convert to /10, apply syntax penalties, optionally scale to `question_max`; generate fix suggestions.

## Requirements

- Python >= 3.10
- For local HF models: CUDA-capable GPU recommended; `torch` + `bitsandbytes`
- For C/C++ syntax checks: `g++` on `PATH`

## Setup

```bash
git clone <repo-url>
cd CodeJudge
conda create -n codeeval python=3.10 -y
conda activate codeeval
pip install -r requirements.txt
cp .env_template .env   # fill API keys for providers you use
```

## Providers

`LLMFactory.create(provider=..., model_name=..., api_key=...)` supports:

| Provider | SDK / backend | Env key | Notes |
|---|---|---|---|
| `openrouter` | OpenAI-compatible | `OPENROUTER_API_KEY` | Default UI presets in `app.py` |
| `openai` | OpenAI | `OPENAI_API_KEY` | Also aliases `gpt` / `gpt-api` |
| `gemini` | `google.generativeai` | `GOOGLE_API_KEY` | |
| `qwen` | DashScope (remote) or HF local | `QWEN_API_KEY` / `HUGGINGFACE_TOKEN` | Remote if name contains `qwen-turbo` / `qwen-plus` |
| `ollama` | OpenAI-compatible | — | Default `http://localhost:11434/v1` |
| `vllm` | OpenAI-compatible | — | Default `http://localhost:8000/v1` |
| `local` | transformers + 4-bit | `HUGGINGFACE_TOKEN` | Auto Kaggle path / HF cache |

Example:

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
# or
export GOOGLE_API_KEY=...
```

## Web UI

```bash
conda activate codeeval
python app.py
```

Supports text paste, single file, or folder submission for student code; problem statement from text / `.txt` / `.md` / `.pdf` / `.docx` (optional `pypdf`, `python-docx`).

## Batch scoring

### HCMUS

```bash
python evaluation/hcmus/score_with_multi_agent.py \
  --provider openrouter \
  --model google/gemini-2.5-flash \
  --limit 1
```

Useful flags: `--config <weights.json>`, `--parallel-factors`, `--max-factor-workers`, `--resume`, `--start`, `--output`.

### CoNaLa

```bash
python evaluation/conala/score_conala_multi_agent.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --limit 5
```

Useful flags: `--config`, `--parallel-factors`, `--source`, `--no-cache`, `--output`.

## HITL (HCMUS weights / factors)

1. Extract factor config from a scored JSONL:

```bash
python evaluation/hcmus/extract_factors_config.py --help
```

2. Tune weights offline:

```bash
python evaluation/hcmus/tune_weights.py --help
```

Configs live under `evaluation/hcmus/configs/` (e.g. `1_final.json`, `noconfig_*`).

## Metrics

```bash
# Single file
python evaluation/hcmus/calculate_metric.py <path-to.jsonl>
python evaluation/conala/calculate_metric.py <path-to.jsonl>

# Batch / table (+ optional OpenRouter token cost)
python evaluation/hcmus/calculate_all_metrics.py
python evaluation/conala/calculate_all_metrics.py
python evaluation/calculate_table_metrics.py
```

## Tests

```bash
conda activate codeeval
pytest codejudge/tests/ -v
```

Covers compiler helper, `MultiAgentAssessor` (mocked LLM), HITL weights, and cache policy.

## Package layout (runtime)

```
app.py
codejudge/
  core/
    multi_agent_assessor.py
    compiler_helper.py
    llm_client.py
  tests/
evaluation/
  hcmus/          # score_with_multi_agent, HITL, metrics
  conala/         # score_conala_multi_agent, metrics
requirements.txt
.env_template
```

Archive folders such as `paper/` and `code_model_score/` are thesis/reference only and are not part of the multi-agent runtime path.
