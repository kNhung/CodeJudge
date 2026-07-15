"""
CodeEval - Multi-agent auto-grading for programming assignments.
"""

from dotenv import load_dotenv
load_dotenv()

from codeeval.core import (
    MultiAgentAssessor,
    LLMFactory,
    LLMConfig,
    check_syntax,
    merge_folder_code,
)

__version__ = "1.0.0"
__author__ = "CodeEval Team"

__all__ = [
    "MultiAgentAssessor",
    "LLMFactory",
    "LLMConfig",
    "check_syntax",
    "merge_folder_code",
]
