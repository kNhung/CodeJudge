"""
CodeJudge Scoring Module
Tính toán điểm và phân tích kết quả
"""

from .scorer import (
    Scorer,
    ScoreInterpreter,
    ResultFormatter,
    PenaltyConfig,
    PenaltyRule,
    ScoringResult
)

__all__ = [
    "Scorer",
    "ScoreInterpreter",
    "ResultFormatter",
    "PenaltyConfig",
    "PenaltyRule",
    "ScoringResult"
]

__version__ = "1.0.0"
