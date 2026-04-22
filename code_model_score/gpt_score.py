import copy
import re
from .utils import openai_request, gemini_request

def code_llama_prompt(message):
    if len(message) == 1:
        user = message[0]["content"].strip()
        prompt = f"<s>[INST] {user} [/INST]"
    elif len(message) == 2:
        if message[1]["role"] == "user":
            system = message[0]["content"].strip()
            user = message[1]["content"].strip()
            prompt = f"<s>[INST] <<SYS>>\\n{system}\\n<</SYS>>\\n\\n{user}[/INST]"
        elif message[1]["role"] == "assistant":
            user = message[0]["content"].strip()
            assistant = message[1]["content"].strip()
            prompt = f"<s>[INST] {user} [/INST] {assistant}"
    elif len(message) == 3:
        system = message[0]["content"].strip()
        user = message[1]["content"].strip()
        assistant = message[2]["content"].strip()
        prompt = (f"<s>[INST] <<SYS>>\\n{system}\\n<</SYS>>\\n\\n{user}[/INST] {assistant}")
    elif len(message) == 4:
        system = message[0]["content"].strip()
        user_1 = message[1]["content"].strip()
        answer_1 = message[2]["content"].strip()
        user_2 = message[3]["content"].strip()
        prompt = f"<<SYS>>\\n{system}\\n<</SYS>>\\n\\n{user_1}"
        prompt += f"<s>[INST] {prompt} [/INST] {answer_1} </s>"
        prompt += f"<s>[INST] {user_2} [/INST]"
    elif len(message) == 6:
        system = message[0]["content"].strip()
        user_1 = message[1]["content"].strip()
        answer_1 = message[2]["content"].strip()
        user_2 = message[3]["content"].strip()
        answer_2 = message[4]["content"].strip()
        user_3 = message[5]["content"].strip()
        prompt = f"<<SYS>>\\n{system}\\n<</SYS>>\\n\\n{user_1}"
        prompt += f"<s>[INST] {prompt} [/INST] {answer_1} </s>"
        prompt += f"<s>[INST] {user_2} [/INST] {answer_2} </s>"
        prompt += f"<s>[INST] {user_3} [/INST]"
    else:
        raise Exception("Invalid message length")
    return prompt

def llama3_prompt(message):
    prompt = "<|begin_of_text|>"
    for sentence in message:
        prompt += f"<|start_header_id|>{sentence['role']}<|end_header_id|>\n{sentence['content']}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
    return prompt

def form_filling(
    model,
    prompt,
    terminators,
    pipeline,
    temperature,
    info=None,
    max_tokens=2000,
):
    message = copy.deepcopy(prompt)
    if info is not None:
        for item in message:
            for place_holder in info:
                text = info[place_holder]
                placeholder_tag = "{{" + place_holder + "}}"
                if placeholder_tag in item["content"]:
                    item["content"] = item["content"].replace(placeholder_tag, str(text)).strip()

    # 1. Xử lý mô hình API
    if model.startswith("gpt-4") or model.startswith("gpt-3.5-turbo"):
        return openai_request(message=message, model=model, temperature=temperature, max_tokens=max_tokens)
    elif "gemini" in model.lower():
        return gemini_request(message=message, model=model, temperature=temperature, max_tokens=max_tokens)

    # 2. Xử lý mô hình Local (CodeLlama hoặc Llama 3)
    # Tự động điều chỉnh do_sample để tránh lỗi khi temperature = 0
    do_sample = temperature > 0 #
    
    # Kiểm tra tên model linh hoạt hơn (dùng 'in' thay vì 'startswith')
    if "CodeLlama" in model: #
        formatted_prompt = code_llama_prompt(message)
    elif "Meta-Llama-3" in model: #
        formatted_prompt = llama3_prompt(message)
    else:
        raise Exception(f"Invalid model name: {model}")

    return pipeline(
        formatted_prompt,
        do_sample=do_sample, #
        temperature=temperature if do_sample else None, #
        top_p=0.9 if do_sample else None,
        num_return_sequences=1,
        eos_token_id=terminators,
        max_new_tokens=max_tokens,
        pad_token_id=pipeline.tokenizer.eos_token_id,
    )[0]["generated_text"].strip()
