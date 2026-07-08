import json
import torch
import hashlib
import logging
import os
import threading
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)

CACHE_FILE = ".codejudge_cache.json"

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save persistent cache: {e}")


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
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B-Instruct", api_key=None, use_cache=True, cache_dir=None, offload_folder=None, **kwargs):
        print(f"🚀 [CodeJudge] Đang nạp model: {model_name}")
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = load_cache() if use_cache else {}  # Cache LLM requests
        
        # Determine environment paths
        if is_running_on_kaggle():
            if cache_dir is None:
                cache_dir = "/kaggle/working/hf_cache"
            if offload_folder is None:
                offload_folder = "/kaggle/working/offload"
        
        # Cấu hình 4-bit để không bị văng khỏi Kaggle
        # Adjust bitsandbytes config based on environment: Kaggle often has limited memory,
        # but keep 4-bit quantization as default to reduce memory usage.
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

        # Allow trust_remote_code to be True by default for flexibility (needed by Qwen, etc.)
        trust_remote = kwargs.get("trust_remote_code", True)
        hf_token = os.environ.get("HUGGINGFACE_TOKEN")
        
        tokenizer_kwargs = {
            "token": hf_token,
            "trust_remote_code": trust_remote
        }
        if cache_dir:
            tokenizer_kwargs["cache_dir"] = cache_dir
            
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
        
        model_kwargs = {
            "quantization_config": bnb_config,
            "device_map": "auto",
            "trust_remote_code": trust_remote,
            "low_cpu_mem_usage": True,
        }
        if hf_token:
            model_kwargs["token"] = hf_token
        if cache_dir:
            model_kwargs["cache_dir"] = cache_dir
        if offload_folder:
            model_kwargs["offload_folder"] = offload_folder
            model_kwargs["offload_state_dict"] = True
            os.makedirs(offload_folder, exist_ok=True)
            
        self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        self.last_usage = {}

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

    def call(self, system_prompt, user_prompt, format_json=False, use_cache=None):
        """Call local LLM model using Llama-3 Chat Template and retry/format_json validation similar to openrouter."""
        active_cache = use_cache if use_cache is not None else self.use_cache

        # Create cache key
        if active_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug(f"✓ Cache hit for local LLM request")
                self.last_usage = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                }
                return self.request_cache[cache_key]

        # Format theo Chat Template chuẩn của Llama-3
        full_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        import time
        max_retries = 5
        backoff_factor = 2.0

        for attempt in range(max_retries):
            try:
                response = self.generate(full_prompt, temperature=0.01)
                
                # If generation failed completely (e.g. empty response due to pipeline error), raise error to trigger retry.
                if not response:
                    raise RuntimeError("Local LLM generated an empty response")
                
                # print(f"======Raw Response from LLMClient======\n{response}\n==========================")

                # Validate JSON if format_json is True
                if format_json:
                    try:
                        import re
                        response_clean = response.strip()
                        try:
                            json.loads(response_clean)
                        except json.JSONDecodeError:
                            code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_clean, re.IGNORECASE)
                            if code_block_match:
                                json.loads(code_block_match.group(1).strip())
                            else:
                                greedy_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response_clean)
                                if greedy_match:
                                    json.loads(greedy_match.group(1).strip())
                                else:
                                    raise ValueError("No JSON block found")
                    except Exception as json_err:
                        raise ValueError(f"Invalid JSON returned: {json_err}")

                # Save token usage metadata
                try:
                    # Estimate tokens using the tokenizer
                    input_tokens = len(self.tokenizer.encode(full_prompt))
                    output_tokens = len(self.tokenizer.encode(response))
                    self.last_usage = {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    }
                except Exception as token_err:
                    logger.warning(f"Failed to calculate local token usage: {token_err}")
                    self.last_usage = {}

                # Save to cache
                if active_cache:
                    self.request_cache[cache_key] = response
                    save_cache(self.request_cache)
                    logger.debug(f"Cached local LLM response (cache size: {len(self.request_cache)})")

                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** (attempt + 1)
                    logger.warning(f"Local LLM request failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    self.last_usage = {}
                    logger.error(f"LLMClient call error after {max_retries} attempts: {e}")
                    raise

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
        if api_key:
            api_key = api_key.strip()
            
        if not api_key:
            raise ValueError("GOOGLE_API_KEY không được tìm thấy. Set environment variable hoặc truyền api_key parameter")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = load_cache() if use_cache else {}
        self.last_usage = {}
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"✓ Gemini model {model_name} initialized")

    def call(self, system_prompt, user_prompt, format_json=False, use_cache=None):
        """Gọi Gemini API"""
        active_cache = use_cache if use_cache is not None else self.use_cache

        if active_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug(f"✓ Cache hit for Gemini request")
                self.last_usage = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                }
                return self.request_cache[cache_key]
        
        import time
        max_retries = 5
        backoff_factor = 2.0
        
        for attempt in range(max_retries):
            try:
                # Gemini không cần format chat template đặc biệt
                full_prompt = f"<system_prompt>{system_prompt}</system_prompt>\n\n{user_prompt}"
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.01,  # Thấp để JSON ổn định
                        "top_p": 0.95,
                        "max_output_tokens": 8192
                    }
                )
                
                result = response.text
                
                # Save token usage metadata
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    self.last_usage = {
                        "input_tokens": response.usage_metadata.prompt_token_count,
                        "output_tokens": response.usage_metadata.candidates_token_count,
                        "total_tokens": response.usage_metadata.total_token_count
                    }
                else:
                    self.last_usage = {}
                
                # Validate JSON if format_json is True
                if format_json:
                    try:
                        import re
                        response_clean = result.strip()
                        try:
                            json.loads(response_clean)
                        except json.JSONDecodeError:
                            code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_clean, re.IGNORECASE)
                            if code_block_match:
                                json.loads(code_block_match.group(1).strip())
                            else:
                                greedy_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response_clean)
                                if greedy_match:
                                    json.loads(greedy_match.group(1).strip())
                                else:
                                    raise ValueError("No JSON block found")
                    except Exception as json_err:
                        raise ValueError(f"Invalid JSON returned: {json_err}")
                
                if active_cache:
                    self.request_cache[cache_key] = result
                    save_cache(self.request_cache)
                    logger.debug(f"Cached Gemini response (cache size: {len(self.request_cache)})")
                
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** (attempt + 1)
                    logger.warning(f"Gemini request failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    self.last_usage = {}
                    logger.error(f"Gemini API error after {max_retries} attempts: {e}")
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
        self.request_cache = load_cache() if use_cache else {}
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

    def call(self, system_prompt, user_prompt, format_json=False, use_cache=None):
        """Hàm call bổ trợ để TaxonomyAssessor có thể gọi được"""
        active_cache = use_cache if use_cache is not None else self.use_cache

        if active_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug(f"✓ Cache hit for Qwen request")
                return self.request_cache[cache_key]

        # Format gộp cả system prompt và user prompt theo chuẩn chat để Qwen sinh dữ liệu tốt nhất
        # full_prompt = f"<system_prompt>{system_prompt}</system_prompt>\n\n{user_prompt}"
        full_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        response = self.generate(full_prompt, temperature=0.01)

        # print(f"======Raw Response from Qwen======\n{response}\n==========================")
        if active_cache:
            self.request_cache[cache_key] = response
            save_cache(self.request_cache)
        return response


class OpenAIClient:
    """Thin wrapper around OpenAI-compatible client using the official OpenAI SDK (openai).
    Supports OpenAI-compatible endpoints like OpenRouter.
    """
    def __init__(self, model_name="gpt-4", api_key=None, use_cache=True, base_url=None, **kwargs):
        try:
            from openai import OpenAI
        except Exception:
            raise ImportError("openai SDK not installed. pip install openai >= 3.0.0")
        
        # Determine API key based on base_url or defaults
        is_local_api = base_url and any(h in base_url for h in ("localhost", "127.0.0.1", "0.0.0.0"))
        if is_local_api:
            api_key = api_key or os.getenv("OPENAI_API_KEY") or "local"
        elif base_url and "openrouter.ai" in base_url:
            api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        else:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            
        if api_key:
            api_key = api_key.strip()
            
        if not api_key:
            raise ValueError("API Key not found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY.")
            
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = OpenAI(**client_kwargs)
        self.model_name = model_name
        self.use_cache = use_cache
        self.request_cache = load_cache() if use_cache else {}
        self.last_usage = {}
        self._tls = threading.local()

    def _set_usage(self, usage: dict):
        self.last_usage = usage
        self._tls.last_usage = usage

    def get_last_usage(self) -> dict:
        """Thread-safe usage snapshot for the current thread."""
        return getattr(self._tls, "last_usage", None) or self.last_usage or {}

    def generate(self, prompt, temperature=0.0, top_p=1.0, stop=None):
        # Accept either chat-format messages (list of dicts) or a single string prompt
        try:
            if isinstance(prompt, list):
                resp = self.client.chat.completions.create(model=self.model_name, messages=prompt, temperature=temperature, top_p=top_p, stop=stop, timeout=45.0)
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

    def call(self, system_prompt, user_prompt, format_json=False, use_cache=None):
        """Call OpenAI/OpenRouter chat completion endpoint."""
        active_cache = use_cache if use_cache is not None else self.use_cache

        # Create cache key
        if active_cache:
            cache_key = hashlib.md5(
                f"{system_prompt}|{user_prompt}".encode()
            ).hexdigest()
            
            if cache_key in self.request_cache:
                logger.debug("✓ Cache hit for OpenAI/OpenRouter request")
                self._set_usage({
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                })
                return self.request_cache[cache_key]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        extra_kwargs = {}
        if format_json:
            # Both OpenAI and OpenRouter support json response format
            extra_kwargs["response_format"] = {"type": "json_object"}
        
        # Set a large max_tokens to prevent OpenRouter/OpenAI default truncation (usually 150-256 tokens)
        extra_kwargs["max_tokens"] = 8192

        import time
        max_retries = 5
        backoff_factor = 2.0
        
        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.01,
                    timeout=45.0,
                    **extra_kwargs
                )
                result = resp.choices[0].message.content
                
                # Save token usage metadata (thread-local for parallel grading)
                if hasattr(resp, 'usage') and resp.usage:
                    self._set_usage({
                        "input_tokens": resp.usage.prompt_tokens,
                        "output_tokens": resp.usage.completion_tokens,
                        "total_tokens": resp.usage.total_tokens
                    })
                else:
                    self._set_usage({})
                
                # Validate JSON if format_json is True
                if format_json:
                    try:
                        import re
                        response_clean = result.strip()
                        try:
                            json.loads(response_clean)
                        except json.JSONDecodeError:
                            code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_clean, re.IGNORECASE)
                            if code_block_match:
                                json.loads(code_block_match.group(1).strip())
                            else:
                                greedy_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response_clean)
                                if greedy_match:
                                    json.loads(greedy_match.group(1).strip())
                                else:
                                    raise ValueError("No JSON block found")
                    except Exception as json_err:
                        raise ValueError(f"Invalid JSON returned: {json_err}")
                
                if active_cache:
                    self.request_cache[cache_key] = result
                    save_cache(self.request_cache)
                    
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** (attempt + 1)
                    logger.warning(f"OpenAI/OpenRouter request failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    self._set_usage({})
                    logger.error(f"OpenAIClient call error after {max_retries} attempts: {e}")
                    raise


class LLMFactory:
    @staticmethod
    def create(provider="local", model_name="meta-llama/Meta-Llama-3-8B-Instruct", use_cache=True, api_key=None, **kwargs):
        """
        Tạo LLM client dựa trên provider
        
        Args:
            provider: "local", "gemini", "openai", "openrouter", etc.
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
        if p == "openrouter":
            # API key defaults to environment variable OPENROUTER_API_KEY
            api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            return OpenAIClient(
                model_name=model_name,
                api_key=api_key,
                use_cache=use_cache,
                base_url="https://openrouter.ai/api/v1",
                **kwargs
            )
        if p == "ollama":
            api_key = api_key or "ollama"
            base_url = kwargs.get("base_url") or "http://localhost:11434/v1"
            return OpenAIClient(
                model_name=model_name,
                api_key=api_key,
                use_cache=use_cache,
                base_url=base_url,
                **kwargs
            )
        if p == "vllm":
            api_key = api_key or "vllm"
            base_url = kwargs.get("base_url") or "http://localhost:8000/v1"
            return OpenAIClient(
                model_name=model_name,
                api_key=api_key,
                use_cache=use_cache,
                base_url=base_url,
                **kwargs
            )
        # Default: local model
        return LLMClient(model_name=model_name, use_cache=use_cache, **kwargs)

# Thiết lập các Alias (Bí danh)
AnthropicClient = LLMClient
LocalLLMClient = LLMClient