import openai
from openai import OpenAI
import json
import re
import time
import os
from collections import Counter
from transformers import AutoTokenizer
import transformers
import torch

model_cache = {}


def uses_openrouter(model, use_openrouter=None):
    if use_openrouter is not None:
        return use_openrouter
    if "/" in model:
        return True
    return bool(os.environ.get("OPENROUTER_API_KEY")) and not os.environ.get(
        "OPENAI_API_KEY"
    )


def create_api_client(use_openrouter=False):
    if use_openrouter:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise Exception("Please set the environment variable OPENROUTER_API_KEY")
        return OpenAI(
            api_key=api_key.strip(),
            base_url="https://openrouter.ai/api/v1",
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("Please set the environment variable OPENAI_API_KEY")
    return OpenAI(api_key=api_key.strip())


def is_running_on_kaggle():
    return os.path.exists('/kaggle') or os.environ.get('KAGGLE_KERNEL_RUN_TYPE') is not None


def get_kaggle_env():
    """Get environment-specific paths and settings for Kaggle/local."""
    if is_running_on_kaggle():
        return {
            "cache_dir": "/kaggle/working/hf_cache",
            "model_root": "/kaggle/working/model",
            "offload_folder": "/kaggle/working/offload",
        }
    else:
        return {
            "cache_dir": os.path.expanduser("~/.cache/huggingface"),
            "model_root": "./model",
            "offload_folder": None,
        }


def is_remote_api_model(model):
    return model.startswith("gpt") or "/" in model or "gemini" in model.lower() or "qwen" in model.lower()


def load_model(model, root_path=None, cache_dir=None, offload_folder=None):
    if model in model_cache:
        print(f"Loading {model} from cache.")
        return model_cache[model]

    # Determine environment paths
    env_paths = get_kaggle_env()
    if root_path is None:
        root_path = env_paths["model_root"]
    if cache_dir is None:
        cache_dir = env_paths["cache_dir"]
    if offload_folder is None:
        offload_folder = env_paths["offload_folder"]

    # Nhận diện tên mô hình linh hoạt
    pure_model_name = model.split('/')[-1]
    base_name = pure_model_name.replace("-hf", "")
    
    if "CodeLlama" in pure_model_name:
        repo_id = f"codellama/{pure_model_name}"
        local_subdir = f"codellama/{base_name}-hf"
    elif "Meta-Llama-3" in pure_model_name:
        repo_id = f"meta-llama/{pure_model_name}"
        local_subdir = f"llama3/{base_name}-hf"
    elif "qwen" in pure_model_name.lower():
        repo_id = model
        local_subdir = pure_model_name
    elif is_remote_api_model(model):
        model_cache[model] = (None, None)
        return None, None
    else:
        repo_id = model
        local_subdir = pure_model_name

    model_path = os.path.join(root_path, local_subdir)
    
    # Cơ chế tự tìm model trên Kaggle Input
    if not os.path.exists(model_path):
        found_in_kaggle = False
        for search_root in ['/kaggle/input', '/kaggle/working']:
            if os.path.exists(search_root):
                for r, dirs, _ in os.walk(search_root):
                    if pure_model_name in dirs:
                        model_path = os.path.join(r, pure_model_name)
                        found_in_kaggle = True
                        break
            if found_in_kaggle: break
        
        if not found_in_kaggle:
            print(f">>> 🌐 Tải {repo_id} từ Hugging Face Hub...")
            model_path = repo_id

    print(f">>> 🚀 Đang khởi tạo model từ: {model_path}")

    auth_token = os.environ.get("HUGGINGFACE_TOKEN")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            token=auth_token,
            cache_dir=cache_dir,
            trust_remote_code=False
        )
        dtype = torch.bfloat16 if "Llama-3" in pure_model_name else torch.float16
        
        # Prepare pipeline kwargs
        pipeline_kwargs = {
            "torch_dtype": dtype,
            "device_map": "auto",
            "return_full_text": False,
        }
        if auth_token:
            pipeline_kwargs["token"] = auth_token
        
        # Add offload settings for low-memory environments
        if offload_folder:
            os.makedirs(offload_folder, exist_ok=True)
            pipeline_kwargs["offload_folder"] = offload_folder
        
        pipeline = transformers.pipeline(
            "text-generation",
            model=model_path,
            **pipeline_kwargs
        )
        
        if "Llama-3" in pure_model_name:
            terminators = [
                pipeline.tokenizer.eos_token_id,
                pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
            ]
        elif "qwen" in pure_model_name.lower():
            terminators = [
                pipeline.tokenizer.eos_token_id,
                pipeline.tokenizer.convert_tokens_to_ids("<|im_end|>"),
            ]
        else:
            terminators = tokenizer.eos_token_id

        model_cache[model] = (terminators, pipeline)
        return terminators, pipeline
    except Exception as e:
        print(f"❌ Lỗi load model: {e}")
        raise e


# This function adopted from https://github.com/terryyz/ice-score/blob/main/llm_code_eval/evaluator.py#L24-L59
def process_raw_content(content, aspect):
    """
    Processes the raw content to extract the answer.

    Args:
        content (str): The raw content from GPT response.
        aspect (str): The evaluation aspect.

    Returns:
        int: The extracted answer as an integer.
    """
    # Normalize content: lowercase, remove parentheses, and split into lines
    splits = content.lower().replace("(", "").replace(")", "").split("\n")

    # Extract lines containing "score", remove dots, and replace "out of" and "/4"
    ls = [
        ll.strip(".").replace("out of ", "/").replace("/4", "")
        for l in splits
        for ll in l.lstrip("0123456789. ").split(". ")
        if any(item in ll for item in ["score"] + aspect.split())
    ]

    # Extract all numeric characters in each line and store them in a list
    ans = [ll for l in ls for ll in l.split() if ll.isnumeric()]

    # If there are multiple answers, return the most common one
    if len(set(ans)) != 1 and len(ans) > 1:
        return int(Counter(ans).most_common(1)[0][0])

    # Handle special cases where there are no answers or multiple non-numeric answers
    if len(set(ans)) != 1:
        if "N/A" in content:
            return 0

    # Statement added here to avoid `ans` is empty
    if len(ans) == 0:
        try:
            return float(content)
        except:
            return -1

    # Return the single numeric answer
    return int(ans[0])


def answer_to_score(answer, return_type):
    lines = answer.split("\n")
    if return_type == "bool":
        last_line = lines[-1].strip()
        first_line = lines[0].strip()
        if "yes" in last_line.lower() or "yes" in first_line.lower():
            return True
        elif "no" in last_line.lower() or "no" in first_line.lower():
            return False
        else:
            print(f"Invalid answer: {answer}")
            return -1.0
    elif return_type == "score":
        for line in lines:
            try:
                return float(line) / 100
            except:
                match_sentences = [
                    r"score of (\d+)",
                    r"score is (\d+)",
                    r"score for this code snippet is (\d+)",
                    r"score for the code snippet is (\d+)",
                    r"score for the code snippet provided is (\d+)",
                    r"score for correctness is (\d+)",
                    r"Score: (\d+)",
                    r"Score\(0-100 only\): (\d+)",
                    r"Score \(0-100\): (\d+)",
                    r"Answer: (\d+)",
                    r"Correctness: (\d+)",
                    r"would be (\d+)",
                    r"would be around (\d+)",
                    r"should be (\d+)",
                    r"should be scored as (\d+)",
                    r"Score\s?\(0-100 only\):\s?(\d+)",
                    r"code snippet as (\d+)",
                    r"(\d+)/100",
                    r"(\d+) out of 100",
                ]
                for match_sentence in match_sentences:
                    match = re.search(match_sentence, line)
                    if match:
                        return float(match.group(1)) / 100
        print(f"Invalid answer: {answer}")
        return -1
    elif return_type == "error_level":
        def parse_json_list(s: str) -> list:
            json_list_match = re.search(r"\[\s*?\{.*?\}\s*?\]", s, re.DOTALL)
            if json_list_match:
                json_list_str = json_list_match.group(0)
                return json.loads(json_list_str)
            raise ValueError("Invalid JSON string")

        def parse_json_dict(s: str) -> dict:
            json_list_match = re.search(r"\{.*?\}", s, re.DOTALL)
            if json_list_match:
                json_list_str = json_list_match.group(0)
                return json.loads(json_list_str)
            raise ValueError("Invalid JSON string")

        try:
            json_list = parse_json_list(answer)
        except:
            try:
                json_list = [parse_json_dict(answer)]
            except:
                print(f"Invalid answer: {answer}")
                return -1

        score = 100
        for item in json_list:
            try:
                if item["severity"].lower() == "fatal":
                    score -= 100
                elif item["severity"].lower() == "major":
                    score -= 50
                elif item["severity"].lower() == "minor":
                    score -= 5
                elif (
                    item["mistake"].lower() == "none"
                    or item["severity"].lower() == "none"
                    or item["severity"] == ""
                ):
                    pass
                else:
                    raise ValueError("Invalid severity")
            except Exception:
                print(f"Invalid answer: {answer}")
                return -1
        return max(score, 0) / 100
    elif return_type == "inconsistency_level":
        inconsistency_type_map = {
            "Different methods or algorithms": "negligible",
            "Missing dependency declarations": "negligible",
            "No error messages for unexpected input cases": "negligible",
            "Inefficiency, unnecessary statements": "negligible",
            "Edge case not handled": "small",
            "Logic error": "major",
            "Function or variable not defined": "fatal",
            "Code not completed": "fatal",
        }
        def parse_json_list(s: str) -> list:
            json_list_match = re.search(r"\[\s*?\{.*?\}\s*?\]", s, re.DOTALL)
            if json_list_match:
                json_list_str = json_list_match.group(0)
                return json.loads(json_list_str)
            raise ValueError("Invalid JSON string")

        def parse_json_dict(s: str) -> dict:
            json_list_match = re.search(r"\{.*?\}", s, re.DOTALL)
            if json_list_match:
                json_list_str = json_list_match.group(0)
                return json.loads(json_list_str)
            raise ValueError("Invalid JSON string")

        try:
            json_list = parse_json_list(answer)
        except:
            try:
                json_list = [parse_json_dict(answer)]
            except:
                print(f"Invalid answer: {answer}")
                return -1

        score = 100
        for item in json_list:
            try:
                if "severity" in item:
                    if item["severity"].lower() == "fatal":
                        score -= 100
                    elif item["severity"].lower() == "major":
                        score -= 50
                    elif item["severity"].lower() == "small":
                        score -= 5
                    elif (
                        item["inconsistency"].lower() == "none"
                        or item["severity"].lower() == "negligible"
                        or item["severity"] == ""
                    ):
                        pass
                else:
                    flag = False
                    for inconsistency in inconsistency_type_map:
                        if inconsistency.lower() in item["inconsistency"].lower():
                            if inconsistency_type_map[inconsistency] == "fatal":
                                score -= 100
                            elif inconsistency_type_map[inconsistency] == "major":
                                score -= 50
                            elif inconsistency_type_map[inconsistency] == "small":
                                score -= 5
                            elif inconsistency_type_map[inconsistency] == "negligible":
                                pass
                            else:
                                raise ValueError("Invalid severity")
                            flag = True
                            break
                    if not flag:
                        raise ValueError("Invalid severity")
            except Exception:
                print(f"Invalid answer: {answer}")
                return -1
        return max(score, 0) / 100
    elif return_type == "0_to_4_score_functional_correctness":
        return process_raw_content(answer, "functional correctness")
    elif return_type == "0_to_4_score_usefulness":
        return process_raw_content(answer, "usefulness")
    elif return_type == "helpful_score":
        answer = answer.replace("(0-4)", "")
        numbers = re.findall(r"\d+", answer)
        if numbers:
            extracted_number = int(numbers[0])
        else:
            print(answer)
            return -1
        return extracted_number / 4
    elif return_type == "classification":
        def extract_answer(text: str) -> str:
            pattern = r"\[ANSWER\](.*?)\[/ANSWER\]"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return ""
        answer = extract_answer(answer)
        if "incorrect" in answer.lower():
            return 0
        elif "correct" in answer.lower():
            return 1
        else:
            print(f"Invalid answer: {answer}")
            return -1


def openai_request(
    message,
    model,
    temperature=0,
    top_p=1,
    max_tokens=2000,
    stop=None,
    use_openrouter=None,
):
    client = create_api_client(uses_openrouter(model, use_openrouter))
    # print(message[0]["content"])
    # print(message[1]["content"])
    # print(message[2]["content"])
    retries = 5
    time_out_delay = 1
    rate_limit_delay = 60
    for i in range(retries):
        try:
            if model == "davinci-002":
                response = client.completions.create(
                    model=model,
                    prompt=message,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop,
                ).choices[0].text
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=message,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    stop=stop,
                ).choices[0].message.content
            return response
        except openai.APITimeoutError:
            print(f">>> Timeout, retrying attempt {i + 1} of {retries}...")
            time.sleep(time_out_delay)
        except openai.RateLimitError as e:
            print(openai.api_key)
            print(e)
            time.sleep(rate_limit_delay)
            print(f">>> Rate limit exceeded, retrying attempt {i + 1} of {retries}...")
        except openai.APIConnectionError as e:
            print(e)
            time.sleep(time_out_delay)
            print(f">>> API connection error, retrying attempt {i + 1} of {retries}...")

    raise Exception("Failed to get a response after multiple retries.")
