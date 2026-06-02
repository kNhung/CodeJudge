import json
import re
import time
import os
from collections import Counter
from transformers import AutoTokenizer
import transformers
import torch


def is_running_on_kaggle():
    return os.path.exists('/kaggle') or os.environ.get('KAGGLE_KERNEL_RUN_TYPE') is not None

model_cache = {}

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


def load_model(model, root_path=None, cache_dir=None, offload_folder=None):
    if model in model_cache:
        print(f">>> Loading {model} from cache.")
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
    elif pure_model_name.startswith("gpt") or pure_model_name.startswith("gemini"):
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
            use_auth_token=auth_token,
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
            pipeline_kwargs["use_auth_token"] = auth_token
        
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
        else:
            terminators = tokenizer.eos_token_id

        model_cache[model] = (terminators, pipeline)
        return terminators, pipeline
    except Exception as e:
        print(f"❌ Lỗi load model: {e}")
        raise e

def process_raw_content(content, aspect):
    splits = content.lower().replace("(", "").replace(")", "").split("\n")
    ls = [
        ll.strip(".").replace("out of ", "/").replace("/4", "")
        for l in splits
        for ll in l.lstrip("0123456789. ").split(". ")
        if any(item in ll for item in ["score"] + aspect.split())
    ]
    ans = [ll for l in ls for ll in l.split() if ll.isnumeric()]
    if len(set(ans)) != 1 and len(ans) > 1:
        return int(Counter(ans).most_common(1)[0][0])
    if len(set(ans)) != 1 and "N/A" in content: return 0
    if len(ans) == 0:
        try: return float(content)
        except: return -1
    return int(ans[0])

def answer_to_score(answer, return_type):
    lines = answer.split("\n")
    if return_type == "bool":
        text = answer.lower()
        if "yes" in text: return True
        if "no" in text: return False
        return -1.0
    elif return_type == "score":
        patterns = [r"score is (\d+)", r"Score: (\d+)", r"(\d+)/100"]
        for line in lines:
            for p in patterns:
                m = re.search(p, line, re.IGNORECASE)
                if m: return float(m.group(1)) / 100
        return -1
    elif return_type in ["error_level", "inconsistency_level"]:
        try:
            json_match = re.search(r"\[\s*?\{.*?\}\s*?\]|\{.*?\}", answer, re.DOTALL)
            if not json_match: return -1
            data = json.loads(json_match.group(0))
            if isinstance(data, dict): data = [data]
            score = 100
            for item in data:
                sev = item.get("severity", "").lower()
                if sev == "fatal": score -= 100
                elif sev == "major": score -= 50
                elif sev in ["minor", "small"]: score -= 5
            return (1.0 if score == 100 else 0.0) if return_type == "inconsistency_level" else max(score, 0) / 100
        except: return -1
    elif "0_to_4_score" in return_type:
        aspect = "functional correctness" if "correctness" in return_type else "usefulness"
        return process_raw_content(answer, aspect)
    return -1

def openai_request(message, model, temperature=0, top_p=1, stop=None):
    try:
        from openai import OpenAI
    except Exception:
        raise ImportError("openai SDK not installed. Install with: pip install openai")

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    for i in range(5):
        try:
            return client.chat.completions.create(model=model, messages=message, temperature=temperature, top_p=top_p, stop=stop).choices[0].message.content
        except Exception:
            time.sleep(1)
    return ""

def gemini_request(message, model, temperature=0, top_p=1, stop=None):
    from codejudge.core.llm_client import GeminiClient
    client = GeminiClient(model_name=model)
    prompt = "".join([f"{m['role']}: {m['content']}\n" for m in message]) if isinstance(message, list) else message
    return client.generate(prompt, temperature=temperature, top_p=top_p, stop=stop)


def qwen_request(message, model, temperature=0, top_p=1, stop=None):
    """Adapter for Qwen-like providers. Requires an optional QwenClient in codejudge.core.llm_client.
    Falls back to raising ImportError with guidance if SDK not installed."""
    try:
        from codejudge.core.llm_client import QwenClient
    except Exception as e:
        raise ImportError("Qwen client not available. Install Qwen SDK or add QwenClient to codejudge.core.llm_client")

    client = QwenClient(model_name=model)
    prompt = "".join([f"{m['role']}: {m['content']}\n" for m in message]) if isinstance(message, list) else message
    return client.generate(prompt, temperature=temperature, top_p=top_p, stop=stop)


def llm_request(message, model, temperature=0, top_p=1, stop=None):
    """Unified entrypoint for remote/chat LLMs (OpenAI, Gemini, Qwen).
    Keeps existing openai_request and gemini_request behavior and dispatches to qwen_request when model name indicates Qwen.
    """
    lower = model.lower()
    if "gemini" in lower:
        return gemini_request(message=message, model=model, temperature=temperature, top_p=top_p, stop=stop)
    if "qwen" in lower:
        return qwen_request(message=message, model=model, temperature=temperature, top_p=top_p, stop=stop)
    # Default: assume OpenAI-compatible
    return openai_request(message=message, model=model, temperature=temperature, top_p=top_p, stop=stop)
