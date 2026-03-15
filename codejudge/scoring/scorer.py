"""
Scoring Algorithm - Tính toán điểm cuối cùng

Mặc định ưu tiên rubric cộng điểm (0 -> 10).
Vẫn hỗ trợ tương thích ngược với mode penalty.
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PenaltyRule:
    """Quy tắc phạt cho một loại lỗi"""
    error_type: str
    penalty_points: float
    description: str


@dataclass
class ScoringResult:
    """Kết quả chấm điểm"""
    base_score: float
    final_score: float
    penalty_breakdown: Dict[str, float]
    total_penalty: float
    reasoning: str


# ============================================================================
# PENALTY CONFIGURATION
# ============================================================================

class PenaltyConfig:
    """Cấu hình mức phạt"""
    
    DEFAULT_PENALTIES = {
        "Negligible": {
            "penalty": 0,
            "description": "Code xấu, style, missing import - Không trừ điểm"
        },
        "Small": {
            "penalty": -0.5,
            "description": "Thiếu xử lý biên, edge case - Trừ 0.5 điểm"
        },
        "Major": {
            "penalty": -5,
            "description": "Sai logic, sai công thức - Trừ 5 điểm"
        },
        "Fatal": {
            "penalty": -10,
            "description": "Code chưa hoàn thành, undefined - Trừ hết"
        }
    }
    
    @staticmethod
    def get_penalty(error_type: str) -> float:
        """Lấy mức phạt cho một loại lỗi"""
        penalties = PenaltyConfig.DEFAULT_PENALTIES
        if error_type in penalties:
            return penalties[error_type]["penalty"]
        
        logger.warning(f"Unknown error type: {error_type}. Using Negligible (0)")
        return 0


# ============================================================================
# SCORER - HÀM TÍNH ĐIỂM
# ============================================================================

class Scorer:
    """
    Tính toán điểm từ danh sách lỗi
    
    Mặc định (additive):
    Điểm = idea + flow + syntax_execution + correctness + clarity

    Tương thích ngược (penalty):
    Điểm = Max(0, base_score + Tổng_Điểm_Phạt)
    """
    
    def __init__(self, base_score: float = 10.0):
        """
        Khởi tạo Scorer
        
        Args:
            base_score: Điểm tối đa mặc định (mặc định: 10)
        """
        self.base_score = base_score
        self.additive_rubric_max = {
            "idea": 3.0,
            "flow": 2.0,
            "syntax_execution": 2.0,
            "correctness": 2.0,
            "clarity": 1.0,
        }
    
    def calculate_score(
        self,
        errors: List[Dict[str, Any]] = None,
        score_breakdown: Dict[str, Any] = None,
    ) -> ScoringResult:
        """
        Tính điểm theo thứ tự ưu tiên:
        1) score_breakdown (additive)
        2) errors (penalty - tương thích ngược)
        
        Args:
            errors: Danh sách lỗi từ TaxonomyAssessor (legacy)
                    [
                        {
                            "type": "Major",
                            "description": "...",
                            "code_snippet": "..."
                        }
                    ]
            score_breakdown: Rubric cộng điểm
                    {
                        "idea": 2.5,
                        "flow": 1.5,
                        "syntax_execution": 2.0,
                        "correctness": 1.0,
                        "clarity": 0.5
                    }
        
        Returns:
            ScoringResult với các thông tin chi tiết
        """
        if score_breakdown is not None:
            normalized = self._normalize_additive_breakdown(score_breakdown)
            final_score = max(0.0, min(self.base_score, round(sum(normalized.values()), 4)))
            reasoning = self._generate_additive_reasoning(normalized, final_score)

            return ScoringResult(
                base_score=self.base_score,
                final_score=final_score,
                penalty_breakdown=normalized,
                total_penalty=0.0,
                reasoning=reasoning,
            )

        errors = errors or []
        logger.info(f"Calculating score for {len(errors)} errors")
        
        # Tính toán penalty
        penalty_breakdown = self._calculate_penalties(errors)
        total_penalty = sum(penalty_breakdown.values())
        
        # Công thức: Max(0, 10 - total_penalty)
        final_score = max(0.0, self.base_score + total_penalty)
        
        # Reasoning
        reasoning = self._generate_reasoning(
            penalty_breakdown,
            total_penalty,
            final_score
        )
        
        logger.info(f"Final Score: {final_score}")
        
        return ScoringResult(
            base_score=self.base_score,
            final_score=final_score,
            penalty_breakdown=penalty_breakdown,
            total_penalty=total_penalty,
            reasoning=reasoning
        )
    
    def _calculate_penalties(self, errors: List[Dict]) -> Dict[str, float]:
        """
        Tính tổng penalty cho mỗi loại lỗi
        
        Returns:
            {"Negligible": 0, "Small": -0.5, "Major": -5, ...}
        """
        penalty_breakdown = {}
        
        for error in errors:
            error_type = error.get("type", "Negligible")
            penalty = PenaltyConfig.get_penalty(error_type)
            
            if error_type not in penalty_breakdown:
                penalty_breakdown[error_type] = 0
            
            penalty_breakdown[error_type] += penalty
        
        # Ensure all types are present
        for error_type in ["Negligible", "Small", "Major", "Fatal"]:
            if error_type not in penalty_breakdown:
                penalty_breakdown[error_type] = 0
        
        logger.debug(f"Penalty breakdown: {penalty_breakdown}")
        
        return penalty_breakdown
    
    def _generate_reasoning(
        self,
        penalty_breakdown: Dict[str, float],
        total_penalty: float,
        final_score: float
    ) -> str:
        """Tạo giải thích chi tiết cho cách chấm"""
        
        parts = [
            f"Base score: {self.base_score}",
        ]
        
        # Chi tiết mỗi loại lỗi
        for error_type, penalty in penalty_breakdown.items():
            if penalty != 0:
                parts.append(f"{error_type}: {penalty}")
        
        if total_penalty != 0:
            parts.append(f"Total penalty: {total_penalty}")
        
        parts.append(f"Final score: {final_score}")
        
        return " | ".join(parts)

    def _normalize_additive_breakdown(self, score_breakdown: Dict[str, Any]) -> Dict[str, float]:
        """Normalize additive breakdown and clamp each component to rubric max."""
        normalized = {key: 0.0 for key in self.additive_rubric_max}

        for key, max_score in self.additive_rubric_max.items():
            value = score_breakdown.get(key, 0) if isinstance(score_breakdown, dict) else 0
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0
            normalized[key] = max(0.0, min(max_score, value))

        return normalized

    def _generate_additive_reasoning(
        self,
        score_breakdown: Dict[str, float],
        final_score: float,
    ) -> str:
        """Generate reasoning text for additive score mode."""
        parts = [f"Scoring mode: additive", f"Base score: {self.base_score}"]

        for key in ["idea", "flow", "syntax_execution", "correctness", "clarity"]:
            parts.append(f"{key}: {score_breakdown.get(key, 0.0)}")

        parts.append(f"Final score: {final_score}")
        return " | ".join(parts)

    def to_question_scale(self, final_score: float, question_max: float) -> float:
        """
        Chuyển điểm từ thang 0-`base_score` sang thang điểm câu hỏi (tỉ lệ).

        Công thức đơn giản: scaled = clamp(final_score / base_score * question_max, 0, question_max)
        """
        if question_max <= 0:
            logger.warning("question_max must be > 0, returning 0")
            return 0.0

        denom = self.base_score if self.base_score > 0 else 10.0
        scaled = (max(0.0, min(final_score, denom)) / denom) * question_max
        return round(scaled, 4)
    
    def set_base_score(self, base_score: float):
        """Đặt điểm gốc mới"""
        self.base_score = base_score
        logger.info(f"Base score updated to {base_score}")


# ============================================================================
# SCORE INTERPRETER - Phân tích kết quả
# ============================================================================

class ScoreInterpreter:
    """
    Giải thích kết quả chấm điểm
    """
    
    # Định nghĩa các mức điểm
    GRADE_SCALE = {
        "A": (9.0, 10.0),    # Xuất sắc
        "B": (8.0, 8.99),    # Tốt
        "C": (7.0, 7.99),    # Khá
        "D": (6.0, 6.99),    # Đủ điều kiện
        "F": (0.0, 5.99)     # Không đạt
    }
    
    # Feedback tùy theo điểm số
    FEEDBACK_TEMPLATES = {
        "A": "Xuất sắc! Code của bạn chạy đúng và không có lỗi nào.",
        "B": "Tốt! Code chạy đúng nhưng có một số vấn đề nhỏ.",
        "C": "Khá. Code có logic cơ bản đúng nhưng còn một số lỗi trung bình.",
        "D": "Chưa tốt. Code có nhiều lỗi nhưng còn cơ hội cải thiện.",
        "F": "Không đạt. Code cần được viết lại hoàn toàn."
    }
    
    @staticmethod
    def get_grade(score: float) -> str:
        """Lấy grade (A-F) từ điểm số"""
        for grade, (min_score, max_score) in ScoreInterpreter.GRADE_SCALE.items():
            if min_score <= score <= max_score:
                return grade
        return "F"
    
    @staticmethod
    def get_feedback(score: float) -> str:
        """Lấy feedback tương ứng với điểm số"""
        grade = ScoreInterpreter.get_grade(score)
        return ScoreInterpreter.FEEDBACK_TEMPLATES.get(
            grade,
            "Please review your code"
        )
    
    @staticmethod
    def get_level_description(score: float) -> str:
        """Mô tả chi tiết mức độ"""
        grade = ScoreInterpreter.get_grade(score)
        
        descriptions = {
            "A": "Code hoàn toàn chính xác, không có lỗi",
            "B": "Code chạy đúng, có một số cải thiện nhỏ",
            "C": "Code có logic cơ bản nhưng có lỗi",
            "D": "Code còn nhiều vấn đề, cần sửa chữa lớn",
            "F": "Code không thể chạy hoặc logic sai căn bản"
        }
        
        return descriptions.get(grade, "Unknown")


# ============================================================================
# RESULT FORMATTER - Format kết quả
# ============================================================================

class ResultFormatter:
    """
    Định dạng kết quả chấm điểm cho hiển thị
    """
    
    @staticmethod
    def format_full_result(
        scoring_result: ScoringResult,
        errors: List[Dict] = None,
        problem_statement: str = None
    ) -> Dict[str, Any]:
        """
        Format kết quả chấm điểm đầy đủ
        """
        grade = ScoreInterpreter.get_grade(scoring_result.final_score)
        feedback = ScoreInterpreter.get_feedback(scoring_result.final_score)
        
        result = {
            "score": {
                "final": scoring_result.final_score,
                "base": scoring_result.base_score,
                "penalty": scoring_result.total_penalty,
                "grade": grade,
                "on_10_scale": f"{scoring_result.final_score}/10"
            },
            "feedback": feedback,
            "breakdown": scoring_result.penalty_breakdown,
            "reasoning": scoring_result.reasoning
        }
        
        if errors:
            result["errors"] = {
                "count": len(errors),
                "critical": len([e for e in errors if e.get("type") in ["Major", "Fatal"]]),
                "details": errors
            }
        
        return result
    
    @staticmethod
    def format_short_result(final_score: float) -> str:
        """
        Format kết quả ngắn gọn (cho display)
        """
        grade = ScoreInterpreter.get_grade(final_score)
        return f"Score: {final_score}/10 ({grade})"
    
    @staticmethod
    def format_detailed_report(
        scoring_result: ScoringResult,
        errors: List[Dict] = None
    ) -> str:
        """
        Tạo báo cáo chi tiết (text format)
        """
        lines = [
            "=" * 60,
            "DETAILED SCORING REPORT",
            "=" * 60,
            f"Final Score: {scoring_result.final_score}/10",
            f"Base Score: {scoring_result.base_score}",
            f"Total Penalty: {scoring_result.total_penalty}",
            "",
            "PENALTY BREAKDOWN:",
        ]
        
        for error_type, penalty in scoring_result.penalty_breakdown.items():
            if penalty != 0:
                lines.append(f"  - {error_type}: {penalty}")
        
        if errors:
            lines.append("")
            lines.append("ERRORS FOUND:")
            
            error_count = {}
            for error in errors:
                error_type = error.get("type", "Unknown")
                error_count[error_type] = error_count.get(error_type, 0) + 1
            
            for error_type, count in error_count.items():
                lines.append(f"  - {error_type}: {count}")
        
        lines.append("")
        lines.append("REASONING:")
        lines.append(f"  {scoring_result.reasoning}")
        
        return "\\n".join(lines)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example errors
    errors = [
        {"type": "Small", "description": "Missing edge case handling"},
        {"type": "Major", "description": "Wrong algorithm"},
    ]
    
    # Calculate score
    scorer = Scorer(base_score=10)
    result = scorer.calculate_score(errors)
    
    print("\\n=== Scoring Result ===")
    print(f"Base Score: {result.base_score}")
    print(f"Final Score: {result.final_score}")
    print(f"Grade: {ScoreInterpreter.get_grade(result.final_score)}")
    print(f"Feedback: {ScoreInterpreter.get_feedback(result.final_score)}")
    
    # Detailed report
    print("\\n" + ResultFormatter.format_detailed_report(result, errors))
