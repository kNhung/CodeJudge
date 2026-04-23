import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

class LLMClient:
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B-Instruct", api_key=None, **kwargs):
        print(f"🚀 [CodeJudge] Đang nạp model: {model_name}")
        self.model_name = model_name
        
        # Cấu hình 4-bit để không bị văng khỏi Kaggle
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            token=True,
            trust_remote_code=True
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate(self, prompt, max_tokens=2000, temperature=0.01, top_p=0.9, stop=None):
        """Hàm generate cơ bản cho utils.py"""
        try:
            do_sample = temperature > 0
            outputs = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature if do_sample else None,
                do_sample=do_sample,
                return_full_text=False 
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            print(f"❌ Lỗi generate: {e}")
            return ""

    def call(self, system_prompt, user_prompt, format_json=False):
        """Hàm call mà Binary/Taxonomy Assessor đang yêu cầu"""
        # Format theo Chat Template chuẩn của Llama-3
        full_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        # Giảm temperature xuống thấp nhất để có kết quả JSON ổn định
        return self.generate(full_prompt, temperature=0.01)

# Các class hỗ trợ để thỏa mãn file __init__.py
class LLMConfig: 
    def __init__(self, **kwargs):
        for k, v in kwargs.items(): setattr(self, k, v)

class LLMFactory:
    @staticmethod
    def create(provider="local", model_name="meta-llama/Meta-Llama-3-8B-Instruct", **kwargs):
        return LLMClient(model_name=model_name, **kwargs)

# Thiết lập các Alias (Bí danh)
OpenAIClient = LLMClient
AnthropicClient = LLMClient
LocalLLMClient = LLMClient
GeminiClient = LLMClient