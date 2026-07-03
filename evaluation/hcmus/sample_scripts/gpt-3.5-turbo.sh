# Run from evaluation/ directory:
#   bash ./hcmus/sample_scripts/gpt-3.5-turbo.sh
#
# Prompts 0, 2, 4, 5 do not require a reference solution (HCMUS has none).
# Prompts 1, 3, 6, 7 need CODE2 and are skipped here.

python ./hcmus/pre_process.py

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 1 \
--compare_prompt 0 \
--temperature 0 \
--return_type "helpful_score" \
--num_samples 1

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 1 \
--compare_prompt 2 \
--temperature 0 \
--return_type "0_to_4_score_usefulness" \
--num_samples 1

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 1 \
--compare_prompt 4 \
--temperature 0 \
--return_type "inconsistency_level" \
--num_samples 1

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 1 \
--compare_prompt 5 \
--temperature 0 \
--return_type "inconsistency_level" \
--num_samples 1

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 2 \
--compare_prompt 0 \
--analyze_prompt 0 \
--temperature 0 \
--return_type helpful_score \
--num_samples 1

python ./hcmus/code_score.py \
--model gpt-3.5-turbo-1106 \
--step 2 \
--compare_prompt 2 \
--analyze_prompt 0 \
--temperature 0 \
--return_type helpful_score \
--num_samples 1

python ./hcmus/calculate_correlation.py
