"""
CodeJudge - Auto-Grading System for Programming Assignments
Hệ thống chấm điểm code tự động cho bài tập lập trình

Dựa trên paper: CodeJudge - Auto-Grading Code Assignments
"""

from codejudge.core import (
    IntegratedAssessor,
    BinaryAssessor,
    TaxonomyAssessor,
    LLMFactory,
    LLMConfig,
)

from codejudge.scoring import (
    Scorer,
    ScoreInterpreter,
    ResultFormatter,
)

__version__ = "1.0.0"
__author__ = "CodeJudge Team"

__all__ = [
    "IntegratedAssessor",
    "BinaryAssessor",
    "TaxonomyAssessor",
    "LLMFactory",
    "LLMConfig",
    "Scorer",
    "ScoreInterpreter",
    "ResultFormatter",
]
