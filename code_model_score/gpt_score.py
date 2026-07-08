import copy

from .utils import openai_request


def code_llama_prompt(message):
    if len(message) == 1:
        # only user prompt
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
        prompt = (
            f"<s>[INST] <<SYS>>\\n{system}\\n<</SYS>>\\n\\n{user}[/INST] {assistant}"
        )
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
        print(message)
        raise Exception("Invalid message length")
    return prompt


def llama3_prompt(message):
    prompt = "<|begin_of_text|>"
    for sentence in message:
        prompt += f"<|start_header_id|>{sentence['role']}<|end_header_id|>\n{sentence['content']}<|eot_id|>"
    prompt += "<|start_header_id|>assistant<|end_header_id|>"
    return prompt


def qwen_prompt(message):
    prompt = ""
    for sentence in message:
        role = sentence['role']
        content = sentence['content']
        prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"
    return prompt


def form_filling(
    model,
    prompt,
    terminators,
    pipeline,
    temperature,
    info=None,
    max_tokens=2000,
    use_openrouter=None,
):
    message = copy.deepcopy(prompt)
    if info is not None:
        for item in message:
            for place_holder in info:
                text = info[place_holder]
                place_holder = "{{" + place_holder + "}}"
                if place_holder in item["content"]:
                    item["content"] = item["content"].replace(place_holder, text).strip()

    # 1. If local pipeline is loaded, run it locally
    if pipeline is not None:
        do_sample = temperature > 0
        if "CodeLlama" in model:
            formatted_prompt = code_llama_prompt(message)
        elif "Meta-Llama-3" in model:
            formatted_prompt = llama3_prompt(message)
        elif "qwen" in model.lower():
            formatted_prompt = qwen_prompt(message)
        else:
            try:
                formatted_prompt = pipeline.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
            except Exception:
                formatted_prompt = str(message)
        return pipeline(
            formatted_prompt,
            do_sample=do_sample,
            temperature=temperature if do_sample else None,
            top_p=0.9 if do_sample else None,
            num_return_sequences=1,
            eos_token_id=terminators,
            max_new_tokens=max_tokens,
            pad_token_id=pipeline.tokenizer.eos_token_id,
        )[0]["generated_text"].strip()

    # 2. Otherwise call remote APIs
    if model.startswith("gpt-4") or model.startswith("gpt-3.5-turbo") or "/" in model:
        return openai_request(
            message=message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            use_openrouter=use_openrouter,
        )
    else:
        raise Exception("Invalid model")
