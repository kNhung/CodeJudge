import torch
import hashlib
import logging
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

logger = logging.getLogger(__name__)


def is_running_on_kaggle():
    return os.path.exists('/kaggle') or os.environ.get('KAGGLE_KERNEL_RUN_TYPE') is not None

# Thử import google.generativeai nếu có
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Thử import Qwen SDK nếu có (tùy nhà cung cấp)
try:
    import qwen
    HAS_QWEN = True
except Exception:
    HAS_QWEN = False

class LLMClient:
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B-Instruct", api_key=None, use_cache=True, **kwargs):
        print(f"🚀 [CodeJudge] Đang nạp model: {model_name}")
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = {}  # Cache LLM requests
        
        # Cấu hình 4-bit để không bị văng khỏi Kaggle
        # Adjust bitsandbytes config based on environment: Kaggle often has limited memory,
        # but keep 4-bit quantization as default to reduce memory usage.
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

        # Use trust_remote_code only when not in a restrictive environment
        trust_remote = not is_running_on_kaggle()
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
        model_kwargs = {
            "quantization_config": bnb_config,
            "device_map": "auto",
            "trust_remote_code": trust_remote,
        }
        if hf_token:
            model_kwargs["token"] = hf_token
        self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate(self, prompt, temperature=0.01, top_p=0.9, stop=None):
        """Hàm generate cơ bản cho utils.py"""
        try:
            do_sample = temperature > 0
            outputs = self.pipe(
                prompt,
                temperature=temperature if do_sample else None,
                do_sample=do_sample
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            print(f"❌ Lỗi generate: {e}")
            return ""

    def call(self, system_prompt, user_prompt, format_json=False):
        """Hàm call mà Binary/Taxonomy Assessor đang yêu cầu"""

        # Tạo cache key
        if self.use_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug(f"✓ Cache hit for LLM request")
                return self.request_cache[cache_key]
        
        # Format theo Chat Template chuẩn của Llama-3
        full_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        # Giảm temperature xuống thấp nhất để có kết quả JSON ổn định
        response = self.generate(full_prompt, temperature=0.01)
        
        # Lưu vào cache
        if self.use_cache:
            self.request_cache[cache_key] = response
            logger.debug(f"Cached LLM response (cache size: {len(self.request_cache)})")
        
        return response

# Các class hỗ trợ để thỏa mãn file __init__.py
class LLMConfig: 
    def __init__(self, **kwargs):
        for k, v in kwargs.items(): setattr(self, k, v)

class GeminiClient:
    """LLM Client cho Google Gemini API"""
    def __init__(self, model_name="gemini-2.5-flash", api_key=None, use_cache=True, **kwargs):
        if not HAS_GEMINI:
            raise ImportError("google-generativeai không được cài đặt. Chạy: pip install google-generativeai")
        
        # Lấy API key từ parameter hoặc environment
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY không được tìm thấy. Set environment variable hoặc truyền api_key parameter")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = {}
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"✓ Gemini model {model_name} initialized")

    def call(self, system_prompt, user_prompt, format_json=False):
        """Gọi Gemini API"""
        if self.use_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug(f"✓ Cache hit for Gemini request")
                return self.request_cache[cache_key]
        
        try:
            # Gemini không cần format chat template đặc biệt
            full_prompt = f"<system_prompt>{system_prompt}</system_prompt>\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.01,  # Thấp để JSON ổn định
                    "top_p": 0.95
                }
            )
            
            result = response.text
            
            if self.use_cache:
                self.request_cache[cache_key] = result
                logger.debug(f"Cached Gemini response (cache size: {len(self.request_cache)})")
            
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def generate(self, prompt, temperature=0.01, top_p=0.9, stop=None):
        """Generate method cho compatibility"""
        return self.call(
            system_prompt="",
            user_prompt=prompt,
            format_json=False
        )


class QwenClient:
    """Adapter for Qwen and Qwen-like providers (e.g., DashScope API).
    Supports both local Qwen models via transformers and remote Qwen API via dashscope SDK.
    
    For remote API: set QWEN_API_KEY environment variable and use model names like 'qwen-turbo'.
    For local models: use HF model names like 'Qwen/Qwen2-7B' and ensure transformers+bitsandbytes installed.
    """
    def __init__(self, model_name="Qwen/Qwen2-7B", api_key=None, use_cache=True, cache_dir=None, offload_folder=None, **kwargs):
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = {}
        self.is_remote = "qwen-turbo" in model_name.lower() or "qwen-plus" in model_name.lower()
        
        if self.is_remote:
            # Remote Qwen API (via DashScope or similar)
            self._init_remote_api(api_key)
        else:
            # Local Qwen model via transformers
            self._init_local_model(model_name, cache_dir, offload_folder)
    
    def _init_remote_api(self, api_key):
        """Initialize remote Qwen API client."""
        try:
            import dashscope
            HAS_DASHSCOPE = True
        except Exception:
            HAS_DASHSCOPE = False
        
        if not HAS_DASHSCOPE:
            raise ImportError(
                "dashscope SDK not installed for remote Qwen API. "
                "Install with: pip install dashscope\n"
                "Or use local Qwen models (e.g., 'Qwen/Qwen2-7B') with transformers instead."
            )
        
        api_key = api_key or os.getenv("QWEN_API_KEY")
        if not api_key:
            raise ValueError(
                "QWEN_API_KEY not found. Set environment variable or pass api_key. "
                "Get key from: https://dashscope.aliyun.com/"
            )
        
        dashscope.api_key = api_key
        self.client = dashscope.Generation
        logger.info(f"✓ Qwen remote API ({self.model_name}) initialized")
    
    def _init_local_model(self, model_name, cache_dir, offload_folder):
        """Initialize local Qwen model via transformers."""
        # if cache_dir is None or offload_folder is None:
        #     cache_dir, offload_folder = get_kaggle_paths()

        if cache_dir is None:
            cache_dir = "/kaggle/working/hf_cache"
        if offload_folder is None:
            offload_folder = "/kaggle/working/offload"
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        trust_remote = not is_running_on_kaggle()
        
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,  # Qwen models often use custom code
            cache_dir=cache_dir,
            token=hf_token
        )
        
        model_kwargs = {
            "token": hf_token,
            "quantization_config": bnb_config,
            "device_map": "auto",
            "trust_remote_code": True,
            "cache_dir": cache_dir,
            "low_cpu_mem_usage": True,
            "offload_state_dict": True,
        }
        if offload_folder:
            model_kwargs["offload_folder"] = offload_folder
            os.makedirs(offload_folder, exist_ok=True)
        
        self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        self.client = None
        logger.info(f"✓ Qwen local model ({model_name}) initialized")

    def generate(self, prompt, temperature=0.01, top_p=0.9, stop=None):
        """Generate text via remote API or local model."""
        if self.is_remote:
            return self._generate_remote(prompt, temperature, top_p, stop)
        else:
            return self._generate_local(prompt, temperature, top_p, stop)
    
    def _generate_remote(self, prompt, temperature, top_p, stop):
        """Generate via DashScope API."""
        if self.client is None:
            raise RuntimeError("Qwen remote client not initialized")
        try:
            response = self.client.call(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p
            )
            # DashScope response structure
            if hasattr(response, 'output') and hasattr(response.output, 'text'):
                return response.output.text
            return str(response)
        except Exception as e:
            logger.error(f"Qwen remote API error: {e}")
            raise
    
    def _generate_local(self, prompt, temperature, top_p, stop):
        """Generate via local Qwen model."""
        if not hasattr(self, 'pipe'):
            raise RuntimeError("Qwen local model not initialized")
        try:
            do_sample = temperature > 0
            outputs = self.pipe(
                prompt,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                do_sample=do_sample,
                return_full_text=False,
                max_new_tokens=None,
                max_length=None
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            logger.error(f"Qwen local generation error: {e}")
            raise

    def call(self, system_prompt, user_prompt, format_json=False):
        """Hàm call bổ trợ để TaxonomyAssessor có thể gọi được"""
        # Format gộp cả system prompt và user prompt theo chuẩn chat để Qwen sinh dữ liệu tốt nhất
        full_prompt = f"<system_prompt>{system_prompt}</system_prompt>\n\n{user_prompt}"
        return self.generate(full_prompt, temperature=0.01)


class OpenAIClient:
    """Thin wrapper around OpenAI-compatible client using the official OpenAI SDK (openai).
    Uses environment variable OPENAI_API_KEY if api_key not supplied.
    """
    def __init__(self, model_name="gpt-4", api_key=None, use_cache=True, **kwargs):
        try:
            from openai import OpenAI
        except Exception:
            raise ImportError("openai SDK not installed. pip install openai >= 3.0.0")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Set environment variable or pass api_key")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = {}

    def generate(self, prompt, temperature=0.0, top_p=1.0, stop=None):
        # Accept either chat-format messages (list of dicts) or a single string prompt
        try:
            if isinstance(prompt, list):
                resp = self.client.chat.completions.create(model=self.model_name, messages=prompt, temperature=temperature, top_p=top_p, stop=stop)
                return resp.choices[0].message.content
            else:
                # Fallback: use completions endpoint
                resp = self.client.responses.create(model=self.model_name, input=prompt)
                # SDK response shapes differ; try common access
                if hasattr(resp, 'output'):
                    # Newer SDK
                    return "\n".join([o.get('content', '') for o in resp.output if isinstance(o, dict)]) or str(resp)
                return str(resp)
        except Exception as e:
            logger.error(f"OpenAIClient generate error: {e}")
            raise

class LLMFactory:
    @staticmethod
    def create(provider="local", model_name="meta-llama/Meta-Llama-3-8B-Instruct", use_cache=True, api_key=None, **kwargs):
        """
        Tạo LLM client dựa trên provider
        
        Args:
            provider: "local", "gemini", "openai", etc.
            model_name: Tên model
            use_cache: Có dùng cache không
            api_key: API key (nếu cần)
        """
        p = provider.lower()
        model_lower = model_name.lower()

        # If the user accidentally passes local provider with a remote API model name,
        # route to the proper remote client automatically.
        if p == "local":
            if "gemini" in model_lower:
                p = "gemini"
                logger.warning(
                    "Provider 'local' overridden to 'gemini' because model '%s' is a Gemini remote model.",
                    model_name,
                )
            elif model_lower.startswith("qwen-") and not model_lower.startswith("qwen/"):
                p = "qwen"
                logger.warning(
                    "Provider 'local' overridden to 'qwen' because model '%s' is a Qwen remote model.",
                    model_name,
                )
            elif model_lower.startswith("gpt-") or model_lower.startswith("gpt4") or model_lower.startswith("gpt3"):
                p = "openai"
                logger.warning(
                    "Provider 'local' overridden to 'openai' because model '%s' is an OpenAI remote model.",
                    model_name,
                )

        if p == "gemini":
            return GeminiClient(model_name=model_name, api_key=api_key, use_cache=use_cache, **kwargs)
        if p == "qwen":
            return QwenClient(model_name=model_name, api_key=api_key, use_cache=use_cache, **kwargs)
        if p in ("openai", "gpt", "gpt-api"):
            # Provide a thin OpenAI client wrapper
            return OpenAIClient(model_name=model_name, api_key=api_key, use_cache=use_cache, **kwargs)
        # Default: local model
        return LLMClient(model_name=model_name, use_cache=use_cache, **kwargs)

# Thiết lập các Alias (Bí danh)
AnthropicClient = LLMClient
LocalLLMClient = LLMClient