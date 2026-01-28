import pandas as pd
import json
# Print out columns of dataset
import pandas as pd
import json
import os

# Print out columns of dataset
def get_columns(dataset):
    return dataset.columns.tolist()


def load_json_flex(path):
    # Try pandas read_json with lines (for jsonl), then without lines (for array json),
    # then fallback to manual line-by-line parse.
    try:
        return pd.read_json(path, lines=True)
    except ValueError:
        try:
            return pd.read_json(path)
        except ValueError:
            # fallback: try manual JSON lines parsing
            data = []
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        # skip lines that are not valid JSON on their own
                        continue
            if data:
                return pd.DataFrame(data)
            # last attempt: try loading entire file as a single JSON value
            with open(path, 'r') as f:
                obj = json.load(f)
                if isinstance(obj, dict):
                    return pd.DataFrame([obj])
                return pd.DataFrame(obj)


if __name__ == "__main__":
    links = [
        "/home/knhung/KLTN/CodeJudge/evaluation/data/apps/test_cases/gpt.jsonl",
        "/home/knhung/KLTN/CodeJudge/evaluation/data/bigcodebench/test_cases/codellama--CodeLlama-13b-Instruct-hf.jsonl",
        "/home/knhung/KLTN/CodeJudge/evaluation/data/conala/conala-aggregated-grades.json",
        "/home/knhung/KLTN/CodeJudge/evaluation/data/humaneval/dataset/python.json",
    ]

    for json_file_path in links:
        if not os.path.exists(json_file_path):
            print(f"File not found: {json_file_path}")
            continue

        try:
            df = load_json_flex(json_file_path)
        except Exception as e:
            print(f"Failed to parse {json_file_path}: {e}")
            continue

        columns = get_columns(df)
        print(json_file_path, "->", columns)