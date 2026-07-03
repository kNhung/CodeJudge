# Run from evaluation/ directory:
#   bash ./hcmus/sample_scripts/openrouter-gemini.sh
#
# Per-question scoring: one API call per exam question, then weighted aggregate.
# Output files include "-perq" in the filename.

LIMIT=5
MODEL="google/gemini-2.5-flash"

python ./hcmus/pre_process.py

python ./hcmus/code_score.py \
  --model "$MODEL" \
  --step 1 \
  --compare_prompt 0 \
  --temperature 0 \
  --return_type "0_to_4_score_usefulness" \
  --limit "$LIMIT" \
  --per_question \
  --use_openrouter \
  --num_samples 1

python ./hcmus/calculate_correlation.py
python ./hcmus/calculate_table.py --detail
