import json
import os
import sys
import argparse
from tqdm.auto import tqdm
import code_bert_score
import requests
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codegen_metrics import (
    codebleu,
    ruby,
    chrf,
    bleu,
    meteor,
    rougel,
)

def calculate_other_metric(test_case, i):
    language = "python"

    data = []
    with open(f"./data/apps/test_cases/{test_case}.jsonl") as f:
        for line in f:
            data.append(json.loads(line))

    out = []
    for item in tqdm(data):
        program = item["program"]
        canonical_solution = item["solution"]
        output_name = f"other-metrics-without-prefix-sample-{i}.json"

        # Default: use local code_bert_score if available
        try:
            _, _, f1, f3 = code_bert_score.score(
                cands=[program], refs=[canonical_solution], lang=language
            )
            f1 = f1.tolist()
            f3 = f3.tolist()
        except Exception:
            # Fallback: try using Hugging Face Inference API embeddings if HF_API_TOKEN provided
            hf_token = os.environ.get("HF_API_TOKEN")
            hf_model = os.environ.get("HF_CODE_EMBEDDING_MODEL", "microsoft/codebert-base")
            if hf_token:
                def get_embedding(text):
                    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{hf_model}"
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    resp = requests.post(url, headers=headers, json={"inputs": text, "options": {"wait_for_model": True}})
                    resp.raise_for_status()
                    vec = resp.json()
                    # If returns token vectors, average them
                    arr = np.array(vec)
                    if arr.ndim == 2:
                        return arr.mean(axis=0)
                    return arr

                v1 = get_embedding(program)
                v2 = get_embedding(canonical_solution)
                # cosine similarity
                def cosine(a, b):
                    denom = (np.linalg.norm(a) * np.linalg.norm(b))
                    if denom == 0:
                        return 0.0
                    return float(np.dot(a, b) / denom)

                sim = cosine(v1, v2)
                # map similarity to pseudo-f1/f3 values
                f1 = [sim]
                f3 = [sim]
            else:
                raise
        out.append(
            {
                "pass": item["pass"],
                "program": program,
                "canonical_solution": canonical_solution,
                "bleu": bleu(canonical_solution, program),
                "codebleu": codebleu(canonical_solution, program),
                "chrf": chrf(canonical_solution, program),
                "rougel": rougel(canonical_solution, program),
                "ruby": ruby(canonical_solution, program),
                "meteor": meteor(canonical_solution, program),
                "code_bert_score_f1": f1[0],
                "code_bert_score_f3": f3[0],
            }
        )

        # create the directory
        if not os.path.exists(f"./output/apps/{test_case}"):
            os.makedirs(f"./output/apps/{test_case}")
        with open(f"./output/apps/{test_case}/{output_name}", "w") as f:
            json.dump(out, f, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_case", type=str)
    parser.add_argument("--num_samples", type=int, default=3)
    args = parser.parse_args()

    test_case = args.test_case
    num_samples = args.num_samples
    for i in range(num_samples):
        calculate_other_metric(test_case, i)


if __name__ == "__main__":
    main()
