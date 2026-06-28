import openai
from openai import OpenAI
import json
import re
import time
import os
import requests
from collections import Counter
from pathlib import Path
from transformers import AutoTokenizer
import transformers
import torch

model_cache = {}

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Short names used in sample scripts -> OpenRouter model ids
OPENROUTER_MODEL_ALIASES = {
    "gpt-3.5-turbo-1106": "openai/gpt-3.5-turbo",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "gpt-4": "openai/gpt-4",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "Gemini-2.5-flash": "google/gemini-2.5-flash",
    "Meta-Llama-3-8B-Instruct": "meta-llama/meta-llama-3-8b-instruct",
    "Meta-Llama-3-70B-Instruct": "meta-llama/meta-llama-3-70b-instruct",
    "CodeLlama-34b-Instruct": "meta-llama/codellama-34b-instruct",
    "Qwen2.5-Coder-7B-Instruct": "qwen/qwen-2.5-coder-7b-instruct",
}


def _get_openrouter_api_key():
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def resolve_openrouter_model(model):
    if model in OPENROUTER_MODEL_ALIASES:
        return OPENROUTER_MODEL_ALIASES[model]
    if "/" in model:
        return model
    return model


def should_use_openrouter(model):
    if not _get_openrouter_api_key():
        return False
    if os.environ.get("CODEJUDGE_FORCE_LOCAL", "").lower() in ("1", "true", "yes"):
        return False
    if "/" in model or model in OPENROUTER_MODEL_ALIASES:
        return True
    lower = model.lower()
    if lower.startswith("gpt-") or "gemini" in lower or lower.startswith("claude"):
        return True
    if any(tag in model for tag in ("Llama-3", "CodeLlama", "Qwen")):
        return os.environ.get("CODEJUDGE_PREFER_OPENROUTER", "1").lower() not in (
            "0",
            "false",
            "no",
        )
    return False


def _load_dotenv():
    root = Path(__file__).resolve().parents[1]
    env_file = root / ".env"
    if not env_file.exists():
        return

    # Read .env using UTF-8 and ignore invalid bytes to avoid Windows cp1252 decode errors
    for raw_line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

def load_model(model, root_path="./model"):
    if model in model_cache:
        print(f">>> Loading {model} from cache.")
        return model_cache[model]

    if should_use_openrouter(model):
        openrouter_model = resolve_openrouter_model(model)
        print(f">>> Using OpenRouter model: {openrouter_model}")
        model_cache[model] = (None, None)
        return None, None

    # Nhận diện tên mô hình linh hoạt
    pure_model_name = model.split('/')[-1]
    base_name = pure_model_name.replace("-hf", "")
    
    if "CodeLlama" in pure_model_name:
        repo_id = f"codellama/{pure_model_name}"
        local_subdir = f"codellama/{base_name}-hf"
    elif "Meta-Llama-3" in pure_model_name or pure_model_name.startswith("Llama-3"):
        repo_id = f"meta-llama/{pure_model_name}"
        local_subdir = f"llama3/{base_name}-hf"
    else:
        repo_id = model
        local_subdir = pure_model_name

    model_path = os.path.join(root_path, local_subdir)
    is_gemini = "gemini" in pure_model_name.lower()

    # Cơ chế tự tìm model trên Kaggle Input
    if not os.path.exists(model_path):
        if is_gemini:
            print(f">>> Gemini local model '{pure_model_name}' không tìm thấy; sử dụng Gemini client thay thế.")
            model_cache[model] = (None, None)
            return None, None

        found_in_kaggle = False
        for search_root in ['/kaggle/input', '/kaggle/working']:
            for r, dirs, _ in os.walk(search_root):
                if pure_model_name in dirs:
                    model_path = os.path.join(r, pure_model_name)
                    found_in_kaggle = True
                    break
            if found_in_kaggle:
                break

        if not found_in_kaggle:
            print(f">>> 🌐 Tải {repo_id} từ Hugging Face Hub...")
            model_path = repo_id

    print(f">>> 🚀 Đang khởi tạo model từ: {model_path}")
    auth_token = os.environ.get("HUGGINGFACE_TOKEN")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_auth_token=auth_token)
        dtype = torch.bfloat16 if "Llama-3" in pure_model_name else torch.float16
        
        pipeline = transformers.pipeline(
            "text-generation",
            model=model_path,
            torch_dtype=dtype,
            device_map="auto",
            return_full_text=False,
            use_auth_token=auth_token,
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
    helpfulness_match = re.search(
        r"helpfulness\s*\(0-4\)\s*:\s*(\d+)", content, re.IGNORECASE
    )
    if helpfulness_match:
        return int(helpfulness_match.group(1))

    stripped = content.strip()
    if stripped.isdigit():
        return int(stripped)

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

def openai_request(message, model, temperature=0, top_p=1, max_tokens=2000, stop=None):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    for i in range(5):
        try:
            return client.chat.completions.create(model=model, messages=message, max_tokens=max_tokens, temperature=temperature, top_p=top_p, stop=stop).choices[0].message.content
        except: time.sleep(1)
    return ""


def openrouter_request(message, model, temperature=0, top_p=1, max_tokens=2000, stop=None):
    api_key = _get_openrouter_api_key()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")

    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    openrouter_model = resolve_openrouter_model(model)
    extra_headers = {
        "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "https://github.com/VichyTong/CodeJudge"),
        "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "CodeJudge"),
    }
    max_retries = int(os.environ.get("CODEJUDGE_MAX_RETRIES", "5"))

    for i in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=openrouter_model,
                messages=message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                extra_headers=extra_headers,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except Exception as e:
            print(f">>> OpenRouter request failed ({i + 1}/{max_retries}): {e}")
            time.sleep(min(2 ** i, 8))
    return ""


def api_request(message, model, temperature=0, top_p=1, max_tokens=2000, stop=None):
    if should_use_openrouter(model):
        return openrouter_request(
            message=message,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )

    lower_model = model.lower()
    if lower_model.startswith("gpt-4") or lower_model.startswith("gpt-3.5-turbo"):
        return openai_request(
            message=message,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )
    if "gemini" in lower_model:
        return gemini_request(
            message=message,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
        )
    raise ValueError(
        f"No API provider configured for model '{model}'. "
        "Set OPENROUTER_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY."
    )

import os
import google.generativeai as genai

def google_gemini_request(message, model, temperature=0, top_p=1, max_tokens=256, stop=None):
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY không được cấu hình cho Gemini API")

    # 1. Cấu hình API Key cho thư viện cũ
    genai.configure(api_key=google_api_key)

    # 2. Chuyển đổi định dạng message sang cấu trúc tin nhắn của thư viện cũ
    # Thư viện này dùng 'user' và 'model'
    formatted_contents = []
    if isinstance(message, list):
        for m in message:
            role = "model" if m['role'] in ['model', 'assistant'] else "user"
            formatted_contents.append({
                "role": role,
                "parts": [m['content']]
            })
    else:
        formatted_contents = message  # Nếu là chuỗi text thuần túy thì giữ nguyên

    # 3. Tạo cấu hình config
    generation_config = genai.GenerationConfig(
        temperature=float(temperature),
        top_p=float(top_p),
        max_output_tokens=int(max_tokens),
        stop_sequences=stop if isinstance(stop, list) else ([stop] if stop else None)
    )

    # 4. Khởi tạo model và gọi API
    try:
        model_client = genai.GenerativeModel(model_name=model)
        
        # Thư viện cũ tự động xử lý endpoint v1/v1beta dựa trên tên model bạn truyền vào
        response = model_client.generate_content(
            contents=formatted_contents,
            generation_config=generation_config
        )
        
        if response.text:
            return response.text.strip()
        else:
            raise ValueError(f"Không nhận được văn bản phản hồi: {response}")
            
    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi thư viện google-generativeai: {e}")


def gemini_request(message, model, temperature=0, top_p=1, max_tokens=2000, stop=None):
    if os.environ.get("GOOGLE_API_KEY"):
        return google_gemini_request(message=message, model=model, temperature=temperature, top_p=top_p, max_tokens=max_tokens, stop=stop)

    from codejudge.core.llm_client import GeminiClient
    client = GeminiClient(model_name=model)
    prompt = "".join([f"{m['role']}: {m['content']}\n" for m in message]) if isinstance(message, list) else message
    return client.generate(prompt, max_tokens=max_tokens, temperature=temperature, top_p=top_p, stop=stop)