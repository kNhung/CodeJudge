"""
CodeJudge Core Engine
Multi-agent code grading: compiler syntax check + factor extract/grade.
"""

from .llm_client import (
    LLMClient,
    OpenAIClient,
    GeminiClient,
    QwenClient,
    LLMFactory,
    LLMConfig,
)

from .multi_agent_assessor import MultiAgentAssessor

from .compiler_helper import check_syntax, merge_folder_code

__all__ = [
    "LLMClient",
    "OpenAIClient",
    "GeminiClient",
    "QwenClient",
    "LLMFactory",
    "LLMConfig",
    "MultiAgentAssessor",
    "check_syntax",
    "merge_folder_code",
]

__version__ = "1.0.0"
