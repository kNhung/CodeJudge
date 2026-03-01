"""
CodeJudge Core Engine
Các module chính cho chấm điểm code tự động
"""

from .llm_client import (
    LLMClient,
    OpenAIClient,
    AnthropicClient,
    LocalLLMClient,
    LLMFactory,
    LLMConfig
)

from .prompts import (
    PromptTemplates,
    ERROR_TAXONOMY,
    SYSTEM_PROMPT_BINARY_ASSESSMENT,
    SYSTEM_PROMPT_TAXONOMY_ASSESSMENT
)

from .binary_assessor import BinaryAssessor

from .taxonomy_assessor import (
    TaxonomyAssessor,
    ErrorClassifier
)

from .integrated_assessor import IntegratedAssessor

__all__ = [
    # LLM Clients
    "LLMClient",
    "OpenAIClient",
    "AnthropicClient",
    "LocalLLMClient",
    "LLMFactory",
    "LLMConfig",
    
    # Prompts
    "PromptTemplates",
    "ERROR_TAXONOMY",
    "SYSTEM_PROMPT_BINARY_ASSESSMENT",
    "SYSTEM_PROMPT_TAXONOMY_ASSESSMENT",
    
    # Assessors
    "BinaryAssessor",
    "TaxonomyAssessor",
    "ErrorClassifier",
    "IntegratedAssessor",
]

__version__ = "1.0.0"
