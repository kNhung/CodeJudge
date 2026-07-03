import json
import re
import time
import torch
import hashlib
import logging
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

OPENROUTER_MODEL_ALIASES = {
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "gpt-3.5-turbo-1106": "openai/gpt-3.5-turbo",
    "gpt-4": "openai/gpt-4",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "google/gemini-2.5-flash": "google/gemini-2.5-flash",
    "Meta-Llama-3-8B-Instruct": "meta-llama/meta-llama-3-8b-instruct",
    "Meta-Llama-3-70B-Instruct": "meta-llama/meta-llama-3-70b-instruct",
}


def resolve_openrouter_model(model_name: str) -> str:
    if model_name in OPENROUTER_MODEL_ALIASES:
        return OPENROUTER_MODEL_ALIASES[model_name]
    if "/" in model_name:
        return model_name
    lower = model_name.lower()
    if "gemini" in lower:
        return f"google/{model_name}"
    return model_name


def _try_parse_json_response(text: str) -> None:
    """Raise ValueError if text does not contain parseable JSON."""
    response_clean = text.strip()
    try:
        json.loads(response_clean)
        return
    except json.JSONDecodeError:
        code_block_match = re.search(
            r"```(?:json)?\s*([\s\S]*?)\s*```", response_clean, re.IGNORECASE
        )
        if code_block_match:
            json.loads(code_block_match.group(1).strip())
            return
        greedy_match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", response_clean)
        if greedy_match:
            json.loads(greedy_match.group(1).strip())
            return
        raise ValueError("No JSON block found")


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
        # print(f"🚀 [LLMClient] Sending prompt to LLM:\n{full_prompt}\n{'-'*50}")
        # Giảm temperature xuống thấp nhất để có kết quả JSON ổn định
        response = self.generate(full_prompt, temperature=0.01)
        print(f"======Raw Response from LLMClient======\n{response}\n==========================")
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

            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
            input_length = input_ids.shape[1]

            # Lấy cấu hình max_position_embeddings từ model, nếu không tìm thấy thì fallback về 8192
            max_ctx = getattr(self.model.config, "max_position_embeddings", 8192)
            dynamic_max_new_tokens = max(512, max_ctx - input_length - 10)
            
            outputs = self.pipe(
                prompt,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                do_sample=do_sample,
                return_full_text=False,
                max_new_tokens=dynamic_max_new_tokens,
                max_length=None
            )
            return outputs[0]['generated_text'].strip()
        except Exception as e:
            logger.error(f"Qwen local generation error: {e}")
            raise

    def call(self, system_prompt, user_prompt, format_json=False):
        """Hàm call bổ trợ để TaxonomyAssessor có thể gọi được"""
        # Format gộp cả system prompt và user prompt theo chuẩn chat để Qwen sinh dữ liệu tốt nhất
        # full_prompt = f"<system_prompt>{system_prompt}</system_prompt>\n\n{user_prompt}"
        full_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        response = self.generate(full_prompt, temperature=0.01)

        print(f"======Raw Response from Qwen======\n{response}\n==========================")
        return response


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
        self.last_usage: dict = {}

    def _chat(self, messages, temperature=0.01, top_p=1.0, stop=None, format_json=False):
        extra_kwargs = {}
        if format_json:
            extra_kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            max_tokens=8192,
            **extra_kwargs,
        )
        if hasattr(resp, "usage") and resp.usage:
            self.last_usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens,
            }
        else:
            self.last_usage = {}
        content = resp.choices[0].message.content
        return content.strip() if content else ""

    def call(self, system_prompt, user_prompt, format_json=False, **kwargs):
        if self.use_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}|{format_json}".encode()
            ).hexdigest()
            if cache_key in self.request_cache:
                self.last_usage = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                }
                return self.request_cache[cache_key]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        result = self._chat(messages, format_json=format_json)
        if format_json:
            _try_parse_json_response(result)
        if self.use_cache:
            self.request_cache[cache_key] = result
        return result

    def generate(self, prompt, temperature=0.0, top_p=1.0, stop=None):
        if isinstance(prompt, list):
            return self._chat(prompt, temperature=temperature, top_p=top_p, stop=stop)
        return self.call(system_prompt="", user_prompt=str(prompt))


class OpenRouterClient:
    """OpenAI-compatible client for OpenRouter (https://openrouter.ai)."""

    def __init__(self, model_name="google/gemini-2.5-flash", api_key=None, use_cache=True, **kwargs):
        try:
            from openai import OpenAI
        except Exception:
            raise ImportError("openai SDK not installed. pip install openai >= 3.0.0")

        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Set it in .env or pass api_key."
            )

        self.client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
        self.model_name = resolve_openrouter_model(model_name)
        self.use_cache = use_cache
        self.request_cache = {}
        self.last_usage: dict = {}
        self.extra_headers = {
            "HTTP-Referer": os.getenv(
                "OPENROUTER_HTTP_REFERER", "https://github.com/VichyTong/CodeJudge"
            ),
            "X-Title": os.getenv("OPENROUTER_APP_TITLE", "CodeJudge"),
        }
        logger.info("OpenRouter client initialized with model %s", self.model_name)

    def call(self, system_prompt, user_prompt, format_json=False, **kwargs):
        use_cache = kwargs.get("use_cache", self.use_cache)
        cache_key = None
        if use_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}|{format_json}".encode()
            ).hexdigest()
            if cache_key in self.request_cache:
                self.last_usage = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                }
                return self.request_cache[cache_key]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        extra_kwargs = {"max_tokens": 8192}
        if format_json:
            extra_kwargs["response_format"] = {"type": "json_object"}

        max_retries = int(os.getenv("CODEJUDGE_MAX_RETRIES", "5"))
        backoff_factor = 2.0
        last_error = None

        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.01,
                    timeout=120.0,
                    extra_headers=self.extra_headers,
                    **extra_kwargs,
                )
                result = resp.choices[0].message.content or ""

                if hasattr(resp, "usage") and resp.usage:
                    self.last_usage = {
                        "input_tokens": resp.usage.prompt_tokens,
                        "output_tokens": resp.usage.completion_tokens,
                        "total_tokens": resp.usage.total_tokens,
                    }
                else:
                    self.last_usage = {}

                if format_json:
                    try:
                        _try_parse_json_response(result)
                    except Exception as json_err:
                        if attempt < max_retries - 1:
                            raise ValueError(f"Invalid JSON returned: {json_err}")
                        logger.warning(
                            "OpenRouter returned non-strict JSON on final attempt; passing raw text to assessor: %s",
                            json_err,
                        )

                result = result.strip()
                if use_cache and cache_key is not None:
                    self.request_cache[cache_key] = result
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** (attempt + 1)
                    logger.warning(
                        "OpenRouter request failed: %s. Retrying in %ss...",
                        e,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                else:
                    self.last_usage = {}
                    logger.error(
                        "OpenRouter call error after %s attempts: %s",
                        max_retries,
                        e,
                    )
                    raise last_error

        raise RuntimeError("OpenRouter request failed without a captured error")

    def generate(self, prompt, temperature=0.01, top_p=0.9, stop=None):
        if isinstance(prompt, list):
            user_prompt = "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}" for m in prompt
            )
            return self.call(system_prompt="", user_prompt=user_prompt)
        return self.call(system_prompt="", user_prompt=str(prompt))


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
            return OpenAIClient(model_name=model_name, api_key=api_key, use_cache=use_cache, **kwargs)
        if p in ("openrouter", "open-router"):
            return OpenRouterClient(model_name=model_name, api_key=api_key, use_cache=use_cache, **kwargs)
        # Default: local model
        return LLMClient(model_name=model_name, use_cache=use_cache, **kwargs)

# Thiết lập các Alias (Bí danh)
AnthropicClient = LLMClient
LocalLLMClient = LLMClient