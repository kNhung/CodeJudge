import json
import numpy as np
from scipy import stats

# Load the JSON file
with open('C:\\Users\\ADMIN\\Downloads\\CodeJudge\\evaluation\\output\\conala\\Meta-Llama-3-8B-Instruct-1-4-0.01-sample-0.json', 'r') as f:
    data = json.load(f)

conala_test_cases = [
    "baseline",
    "tranx-annot",
    "best-tranx",
    "best-tranx-rerank",
    "codex",
]

references = []
predictions = []

for item in data['data'][:60]:  # Limit to first 60 samples
    example_references = []
    example_predictions = []
    for case in conala_test_cases:
        example_references.append(float(item['grade'][case]))
        code_gpt_score = item['code_gpt_score'][case]['code_gpt_score']
        if code_gpt_score == -1:
            example_predictions.append(0)  # or handle invalid
        else:
            example_predictions.append(float(code_gpt_score))
    references.append(example_references)
    predictions.append(example_predictions)

# Calculate correlations
kendalltau_values = []
spearmanr_values = []

for ref, pred in zip(references, predictions):
    kendalltau_values.append(stats.kendalltau(ref, pred).statistic)
    spearmanr_values.append(stats.spearmanr(ref, pred).statistic)

# Average
avg_kendalltau = np.nanmean(kendalltau_values)
avg_spearmanr = np.nanmean(spearmanr_values)

print(f"Average Kendall Tau: {avg_kendalltau:.3f}")
print(f"Average Spearman: {avg_spearmanr:.3f}")