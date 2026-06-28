# CoNaLa via OpenRouter (requires OPENROUTER_API_KEY in repo-root .env)
# Run from evaluation/: bash conala/sample_scripts/openrouter-gemini.sh

python ./conala/code_score.py \
--model google/gemini-2.5-flash \
--step 1 \
--compare_prompt 0 \
--temperature 0 \
--return_type "0_to_4_score_usefulness" \
--num_samples 1

python ./conala/code_score.py \
--model google/gemini-2.5-flash \
--step 1 \
--compare_prompt 2 \
--temperature 0 \
--return_type "0_to_4_score_usefulness" \
--num_samples 1
