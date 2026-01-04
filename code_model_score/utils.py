
import openai
from openai import OpenAI
import json
import re
import time
import os
from collections import Counter
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import transformers
import torch

try:
    import ollama
except ImportError:
    ollama = None

model_cache = {}

# --- HÀM 1: OPENAI REQUEST (ĐÃ ĐƯỢC THÊM LẠI) ---
def openai_request(message, model, temperature=0, top_p=1, max_tokens=2000, stop=None):
    if os.environ.get("OPENAI_API_KEY") is None:
        # Nếu không có key thì báo warning thay vì lỗi để code vẫn chạy được các phần khác
        print("Warning: OPENAI_API_KEY not set.")
    
    # Khởi tạo client an toàn
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except:
        client = None

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
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(time_out_delay)
            
    raise Exception("Failed to get a response after multiple retries.")

# --- HÀM 2: LOAD MODEL (ĐÃ TỐI ƯU CHO KAGGLE) ---
def load_model(model, root_path="./model"):
    if model in model_cache:
        print(f"Loading {model} from cache.")
        return model_cache[model]

    # Map tên ngắn sang Hugging Face ID
    model_map = {
        "CodeLlama-7b-Instruct": "codellama/CodeLlama-7b-Instruct-hf",
        "CodeLlama-13b-Instruct": "codellama/CodeLlama-13b-Instruct-hf",
        "CodeLlama-34b-Instruct": "codellama/CodeLlama-34b-Instruct-hf",
    }
    
    if model in model_map:
        model_path = model_map[model]
    elif model.startswith("CodeLlama"):
        model_path = f"codellama/{model}-hf"
    else:
        model_path = None

    print(f"--> Đang tải model: {model_path}")

    if model_path:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Cấu hình 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )

        pipeline = transformers.pipeline(
            "text-generation",
            model=model_path,
            model_kwargs={"quantization_config": bnb_config},
            device_map="auto",
            return_full_text=False,
            tokenizer=tokenizer
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token  
        terminators = tokenizer.eos_token_id
        
    else:
        # Xử lý các trường hợp khác (ollama, gpt...)
        terminators = None
        pipeline = None

    model_cache[model] = (terminators, pipeline)
    return terminators, pipeline

# --- HÀM 3: LLAMA3 PROMPT ---
def llama3_prompt(message):
    prompt = "<|begin_of_text|>"
    for sentence in message:
        prompt += f"<|start_header_id|>{sentence['role']}<|end_header_id|>\n{sentence['content']}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>"
    return prompt

# --- HÀM 4: CÁC HÀM XỬ LÝ KẾT QUẢ ---
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
    if len(set(ans)) != 1:
        if "N/A" in content: return 0
    if len(ans) == 0:
        try: return float(content)
        except: return -1
    return int(ans[0])

def answer_to_score(answer, return_type):
    # Logic tối giản để tránh lỗi, bạn có thể copy logic đầy đủ nếu cần
    if return_type == "helpful_score":
        try:
            answer = str(answer).replace("(0-4)", "")
            numbers = re.findall(r"\d+", answer)
            if numbers: return int(numbers[0]) / 100
        except: pass
        return -1
    return -1
