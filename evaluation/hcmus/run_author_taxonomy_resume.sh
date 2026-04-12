#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
  # Optional: auto-activate conda env if available
  # Set CONDA_ENV_NAME to override, default is codejudge
  # Example: CONDA_ENV_NAME=base ./evaluation/hcmus/run_author_taxonomy_resume.sh
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
  conda activate "${CONDA_ENV_NAME:-codejudge}" || true
fi

python evaluation/hcmus/test_modes.py \
  --mode taxonomy \
  --taxonomy-system-prompt author \
  --provider "${PROVIDER:-gemini}" \
  --model "${MODEL_NAME:-gemini-2.5-flash}" \
  --start "${START_INDEX:-120}" \
  --run-name "${RUN_NAME:-hcmus_author_from_id48}" \
  --resume \
  --stop-on-rate-limit \
  --metrics-scope file \
  "$@"
