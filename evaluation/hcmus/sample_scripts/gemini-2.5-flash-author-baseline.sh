#!/usr/bin/env bash
set -euo pipefail

# Activate codejudge environment
if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate codejudge
else
  echo "[WARN] conda not found. Please activate the 'codejudge' environment manually."
fi

# Use Gemini via OpenAI-compatible endpoint.
# Option A: direct Gemini compatibility endpoint
# export OPENAI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
# export OPENAI_API_KEY="${GEMINI_API_KEY}"

# Option B: OpenRouter
# export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
# export OPENAI_API_KEY="<OPENROUTER_API_KEY>"

python evaluation/hcmus/run_author_baseline_hcmus.py \
  --model gemini-2.5-flash \
  --scoring-mode per_question
