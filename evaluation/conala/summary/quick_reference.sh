#!/bin/bash
# Quick reference: HintEval Answer-Agnostic Mode Usage

# Activate environment
source /home/knhung/miniconda3/etc/profile.d/conda.sh
conda activate codejudge

cd /home/knhung/KLTN/CodeJudge

# ============================================================================
# 1. EVALUATE WITH ANSWER-AGNOSTIC MODE (Recommended for system suggestions)
# ============================================================================
# This mode evaluates hints WITHOUT requiring ground-truth answers
# Metrics: Readability (0=easy, 1=hard) + Familiarity (0=uncommon, 1=common)

python evaluation/conala/summary/evaluate_hinteval.py \
  --mode agnostic \
  --output evaluation/conala/output/hint_eval_agnostic.json

# Result: Readability (mean) + Familiarity (mean) for all 143 hints


# ============================================================================
# 2. EVALUATE WITH RELEVANCE MODE (Original - requires reference code)
# ============================================================================
# This mode evaluates hints by comparing them to reference code
# Metric: ROUGE-L (relevance to reference implementation)

python evaluation/conala/summary/evaluate_hinteval.py \
  --mode relevance \
  --rouge-model rougeL \
  --output evaluation/conala/output/hint_eval_relevance.json

# Result: ROUGE-L scores for each hint


# ============================================================================
# 3. INCLUDE STRENGTHS (Optional)
# ============================================================================
# Treats both improvements AND strengths as hints

python evaluation/conala/summary/evaluate_hinteval.py \
  --mode agnostic \
  --include-strengths \
  --output evaluation/conala/output/hint_eval_with_strengths.json


# ============================================================================
# 4. VIEW RESULTS
# ============================================================================

echo "=== Answer-Agnostic Results ==="
cat evaluation/conala/output/hint_eval_agnostic.json | python -m json.tool | head -50

echo -e "\n=== Relevance Results ==="
cat evaluation/conala/output/hint_eval_relevance.json | python -m json.tool | head -50
