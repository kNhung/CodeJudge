# HCMUS Run Guide

This document describes the current command-line flags for `evaluation/hcmus/score_with_codejudge.py` and how to run the HCMUS dataset with different scoring modes and prompts.

## 1. Activate the environment

```bash
source /home/knhung/miniconda3/bin/activate codejudge
```

## 2. Load environment variables

If your provider needs an API key, load it before running the script:

```bash
set -a && source .env && set +a
```

## 3. Main runner

Use `evaluation/hcmus/score_with_codejudge.py` as the single entry point.

### Common flags

- `--csv`: input CSV file, default is `evaluation/hcmus/hcmus_dataset.csv`
- `--provider`: LLM provider, for example `openai`, `anthropic`, `local`, `gemini`, or `huggingface`
- `--model`: model name to use with the selected provider
- `--output`: output JSONL file
- `--run-name`: output name without extension, used when `--output` is not provided
- `--mode`: scoring mode, one of `binary`, `taxonomy`, or `intergrated`
- `--taxonomy-prompt`: taxonomy prompt template, one of `mine` or `author`
- `--save-metadata`: store token/runtime metadata in the main JSONL output
- `--resume`: append to an existing output file and skip already processed rows
- `--limit`: process only the first N rows
- `--start`: start from a CSV row offset
- `--scoring-mode`: `whole_exam` or `per_question`
- `--dry-run`: validate mapping without calling the LLM
- `--base-url`: backend URL for the `local` provider

## 4. Example commands

### A. Taxonomy mode with the author prompt

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --taxonomy-prompt author \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name 20260527_taxonomy_author_gemini-2.5-flash \
  --resume \
  --start 48 \
  --limit 1
```

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider huggingface \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --mode taxonomy \
  --taxonomy-prompt author \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name 20260527_taxonomy_author_llama-3-8b-instruct \
  --resume \
  --start 48 
```

### B. Taxonomy mode with the default prompt

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --taxonomy-prompt mine \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name 20260527_taxonomy_mine_gemini-2.5-flash \
  --resume \
  --start 48 \
  --limit 1
```

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider huggingface \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --mode taxonomy \
  --taxonomy-prompt mine \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name 20260527_taxonomy_mine_llama-3-8b-instruct \
  --resume \
  --start 48 \
  --limit 1
```

### C. Binary mode

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode binary \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name hcmus_binary
```

### D. Integrated mode

```bash
python evaluation/hcmus/score_with_codejudge.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode intergrated \
  --taxonomy-prompt author \
  --scoring-mode whole_exam \
  --save-metadata \
  --run-name hcmus_integrated
```

## 5. Resume workflow for long runs

When you expect rate limits or want to continue a previous run, keep the same `--run-name` and add `--resume`.

```bash
RUN_NAME="$(date +%y%m%d_%H%M)_gemini-2.5-flash_taxonomy"

python evaluation/hcmus/score_with_codejudge.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --taxonomy-prompt author \
  --scoring-mode whole_exam \
  --run-name "$RUN_NAME" \
  --resume \
  --save-metadata
```

If the run stops and you want to continue later, run the same command again with the same `RUN_NAME`.

## 6. Output location

If you do not pass `--output`, the script writes to:

```bash
evaluation/hcmus/output/<run-name>.jsonl
```

If `--run-name` is also omitted, the file name is generated automatically from the model name and timestamp.

## 7. Notes

- `--taxonomy-prompt author` selects the author prompt.
- `--taxonomy-prompt mine` selects the repository prompt and is the default.
- `--mode taxonomy` is the default scoring mode.
- The flag spelling in the code is currently `intergrated`, so use that exact value when calling integrated mode.