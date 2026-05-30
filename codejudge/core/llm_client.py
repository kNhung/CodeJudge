import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

class GeminiClient:
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B-Instruct", api_key=None):
        print(f"🚀 Khởi tạo model: {model_name}")
        self.model_name = model_name
        
        # Nén 4-bit để tối ưu GPU Kaggle
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )

        auth_token = os.environ.get("HUGGINGFACE_TOKEN")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=auth_token)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
            use_auth_token=auth_token,
        )
        
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate(self, prompt, max_tokens=2000, temperature=0.01, top_p=0.9, stop=None):
        try:
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                return_full_text=False 
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return ""
