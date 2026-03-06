"""
LLM Client - Giao tiếp với các mô hình LLM
Hỗ trợ: OpenAI (GPT-4), Anthropic (Claude), Local LLM
"""

import os
import json
import re
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class LLMClient(ABC):
    """Abstract base class cho tất cả LLM clients"""
    
    def __init__(self, model_name: str, temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = 3
        self.retry_count = 0
    
    @abstractmethod
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        format_json: bool = False
    ) -> str:
        """
        Gọi LLM và lấy response
        
        Args:
            system_prompt: System prompt (vai trò, hướng dẫn)
            user_prompt: User prompt (câu hỏi/yêu cầu)
            format_json: Yêu cầu output JSON
        
        Returns:
            Response text từ LLM
        """
        pass
    
    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Trích xuất JSON từ response
        (xử lý khi LLM trả về text bao quanh JSON)
        """
        try:
            # Thử parse trực tiếp
            return json.loads(response)
        except json.JSONDecodeError:
            # Tìm JSON object trong text
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, response)
            
            if matches:
                # Lấy match dài nhất (likely là JSON object chính)
                json_str = max(matches, key=len)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning(f"Không thể parse JSON từ response: {json_str}")
                    return None
            
            logger.warning(f"Không tìm thấy JSON trong response")
            return None


# ============================================================================
# OPENAI CLIENT
# ============================================================================

class OpenAIClient(LLMClient):
    """Client cho OpenAI (GPT-4, GPT-3.5-turbo)"""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        format_json: bool = False
    ) -> str:
        """Gọi OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"Retrying... ({self.retry_count}/{self.max_retries})")
                return self.call(system_prompt, user_prompt, format_json)
            raise


# ============================================================================
# ANTHROPIC CLIENT
# ============================================================================

class AnthropicClient(LLMClient):
    """Client cho Anthropic (Claude)"""
    
    def __init__(self, model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        format_json: bool = False
    ) -> str:
        """Gọi Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"Retrying... ({self.retry_count}/{self.max_retries})")
                return self.call(system_prompt, user_prompt, format_json)
            raise


# ============================================================================
# LOCAL LLM CLIENT
# ============================================================================

class LocalLLMClient(LLMClient):
    """Client cho Local LLM (Ollama, vllm, etc.)"""
    
    def __init__(
        self,
        model_name: str = "llama2",
        base_url: str = "http://localhost:11434"
    ):
        super().__init__(model_name)
        self.base_url = base_url
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package not installed. Run: pip install requests")
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        format_json: bool = False
    ) -> str:
        """Gọi Local LLM through API"""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "temperature": self.temperature
        }
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            return response.json().get("response", "")
        
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"Retrying... ({self.retry_count}/{self.max_retries})")
                return self.call(system_prompt, user_prompt, format_json)
            raise


# ============================================================================
# LLM FACTORY
# ============================================================================

class LLMFactory:
    """Factory để tạo LLM clients"""
    
    _providers = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "local": LocalLLMClient
    }
    
    @staticmethod
    def create(
        provider: str = "openai",
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLMClient:
        """
        Tạo LLM client dựa trên provider
        
        Args:
            provider: "openai", "anthropic", hoặc "local"
            model_name: Tên mô hình (mặc định trong mỗi client)
            **kwargs: Các argument khác (api_key, base_url, etc.)
        
        Returns:
            LLM client instance
        
        Example:
            # OpenAI
            client = LLMFactory.create("openai", model_name="gpt-4")
            
            # Local
            client = LLMFactory.create("local", model_name="llama2")
        """
        if provider not in LLMFactory._providers:
            raise ValueError(f"Unknown provider: {provider}. Supported: {list(LLMFactory._providers.keys())}")
        
        ClientClass = LLMFactory._providers[provider]
        
        if model_name:
            return ClientClass(model_name=model_name, **kwargs)
        else:
            return ClientClass(**kwargs)
    
    @staticmethod
    def register_provider(name: str, client_class: type):
        """Đăng ký custom provider"""
        if not issubclass(client_class, LLMClient):
            raise TypeError("Client class must inherit from LLMClient")
        LLMFactory._providers[name] = client_class


# ============================================================================
# CONFIG & UTILITY
# ============================================================================

class LLMConfig:
    """Configuration cho LLM"""
    
    # Default models
    DEFAULT_OPENAI_MODEL = "gpt-4"
    DEFAULT_ANTHROPIC_MODEL = "claude-3-opus-20240229"
    DEFAULT_LOCAL_MODEL = "llama2"
    
    # Temperature settings
    TEMPERATURE_CHAT = 0.5  # Chuyển hóa tự nhiên
    TEMPERATURE_ANALYSIS = 0.3  # Phân tích chặt chẽ
    TEMPERATURE_CREATIVE = 0.8  # Creative tasks
    
    @staticmethod
    def get_default_client(temperature: float = 0.3) -> LLMClient:
        """Tạo client mặc định dựa trên env vars"""
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIClient(
                model_name=LLMConfig.DEFAULT_OPENAI_MODEL
            )
        elif os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicClient(
                model_name=LLMConfig.DEFAULT_ANTHROPIC_MODEL
            )
        elif os.getenv("LOCAL_LLM_URL"):
            return LocalLLMClient(
                base_url=os.getenv("LOCAL_LLM_URL"),
                model_name=LLMConfig.DEFAULT_LOCAL_MODEL
            )
        else:
            raise RuntimeError(
                "No LLM provider configured. Set one of: "
                "OPENAI_API_KEY, ANTHROPIC_API_KEY, or LOCAL_LLM_URL"
            )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Example: OpenAI
    try:
        client = LLMFactory.create("openai", model_name="gpt-4")
        
        response = client.call(
            system_prompt="Bạn là một chuyên gia Python.",
            user_prompt="Viết một hàm tính tổng của danh sách.",
            format_json=False
        )
        print("OpenAI Response:", response)
    except Exception as e:
        print(f"OpenAI test skipped: {e}")
    
    # Example: Local LLM
    try:
        client = LLMFactory.create(
            "local",
            model_name="llama2",
            base_url="http://localhost:11434"
        )
        
        response = client.call(
            system_prompt="You are a helpful assistant.",
            user_prompt="What is 2+2?"
        )
        print("Local LLM Response:", response)
    except Exception as e:
        print(f"Local LLM test skipped: {e}")
