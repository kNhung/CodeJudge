"""
Integrated Assessment Engine
Kết hợp Binary Assessment và Taxonomy-Guided Assessment
"""

import logging
from typing import Dict, Any, Optional
from .llm_client import LLMClient, LLMFactory
from .binary_assessor import BinaryAssessor
from .taxonomy_assessor import TaxonomyAssessor
from ..scoring.scorer import Scorer

logger = logging.getLogger(__name__)


class IntegratedAssessor:
    """
    Chấm điểm tích hợp - dùng cả hai luồng
    
    Quy trình:
    1. Binary Assessment: Kiểm tra code có đạt yêu cầu cơ bản không (Yes/No)
    2. Taxonomy Assessment: Nếu May (hoặc luôn), tính điểm chi tiết 0-10
    """
    
    def __init__(
        self,
        llm_client: LLMClient = None,
        run_both_assessments: bool = True
    ):
        """
        Khởi tạo Integrated Assessor
        
        Args:
            llm_client: LLM client instance
            run_both_assessments: Chạy cả Binary và Taxonomy
                                 (True = luôn chạy cả hai)
                                 (False = nếu Binary là No, bỏ Taxonomy)
        """
        self.llm_client = llm_client or LLMFactory.create()
        self.run_both_assessments = run_both_assessments
        
        self.binary_assessor = BinaryAssessor(self.llm_client)
        self.taxonomy_assessor = TaxonomyAssessor(self.llm_client)
    
    def assess(
        self,
        problem_statement: str,
        student_code: str,
        reference_code: Optional[str] = None,
        language: str = "Python",
        question_max: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Chấm điểm tích hợp
        
        Args:
            problem_statement: Đề bài
            student_code: Code của sinh viên
            reference_code: Code mẫu (tùy chọn)
            language: Ngôn ngữ lập trình của bài làm
            question_max: Điểm tối đa của câu (nếu cần quy đổi từ thang 10)
        
        Returns:
            Kết quả chấm điểm tích hợp với cả Binary và Taxonomy scores
        """
        logger.info("=== INTEGRATED ASSESSMENT ===")
        
        # Bước 1: Binary Assessment
        binary_result = self.binary_assessor.assess(
            problem_statement,
            student_code,
            language=language,
        )
        
        logger.info(f"Binary Result: {binary_result['result']}")
        
        # Bước 2: Taxonomy Assessment
        # (chạy nếu run_both_assessments = True hoặc Binary = Yes)
        if self.run_both_assessments or binary_result["passed"]:
            logger.info("Running Taxonomy Assessment...")
            
            taxonomy_result = self.taxonomy_assessor.assess(
                problem_statement,
                student_code,
                reference_code,
                language=language,
            )
        else:
            logger.info("Skipping Taxonomy Assessment (Binary = No)")
            taxonomy_result = {
                "errors": [],
                "quality_score": 0,
                "final_score": 0,
                "reasoning": "Code does not meet basic requirements"
            }
        
        # Kết hợp kết quả
        integrated_result = self._combine_results(
            binary_result,
            taxonomy_result,
            question_max,
        )
        
        return integrated_result
    
    def _combine_results(
        self,
        binary_result: Dict[str, Any],
        taxonomy_result: Dict[str, Any],
        question_max: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Kết hợp kết quả từ hai luồng
        """
        logger.debug("Combining assessment results...")
        
        result = {
            "assessment_type": "integrated",
            "binary": {
                "result": binary_result["result"],
                "passed": binary_result["passed"],
                "confidence": binary_result.get("confidence", 0.9),
                "analysis": binary_result.get("analysis", ""),
                "analysis_preview": binary_result.get("analysis", "")[:200] + "...",
            },
            "taxonomy": {
                "final_score": taxonomy_result["final_score"],
                "errors_count": len(taxonomy_result.get("errors", [])),
                "error_breakdown": self._count_errors_by_type(
                    taxonomy_result.get("errors", [])
                ),
                "quality_score": taxonomy_result.get("quality_score", 0),
                "errors": taxonomy_result.get("errors", []),
                "reasoning": taxonomy_result.get("reasoning", "")
            },
            "summary": {
                "status": "PASS" if binary_result["passed"] else "FAIL",
                "score": taxonomy_result["final_score"],
                "grade_letter": self._get_grade_letter(
                    taxonomy_result["final_score"]
                ),
                "recommendation": self._get_recommendation(
                    binary_result["passed"],
                    taxonomy_result["final_score"]
                )
            }
        }

        if question_max is not None:
            score_on_10 = float(taxonomy_result["final_score"])
            scaled_score = Scorer(base_score=10.0).to_question_scale(score_on_10, question_max)

            result["summary"]["question_max"] = question_max
            result["summary"]["score_on_10"] = score_on_10
            result["summary"]["score_scaled"] = scaled_score
            result["taxonomy"]["score_scaled"] = scaled_score

        return result
    
    def _count_errors_by_type(self, errors: list) -> Dict[str, int]:
        """Đếm lỗi theo type"""
        breakdown = {
            "Negligible": 0,
            "Small": 0,
            "Major": 0,
            "Fatal": 0,
            "Improvement": 0,
            "Other": 0,
        }
        
        for error in errors:
            error_type = error.get("type", "Negligible")
            if error_type in breakdown:
                breakdown[error_type] += 1
            else:
                breakdown["Other"] += 1
        
        return breakdown
    
    def _get_grade_letter(self, score: float) -> str:
        """Lấy điểm chữ từ điểm số"""
        if score >= 9.0:
            return "A"
        elif score >= 8.0:
            return "B"
        elif score >= 7.0:
            return "C"
        elif score >= 6.0:
            return "D"
        else:
            return "F"
    
    def _get_recommendation(
        self,
        passed_binary: bool,
        final_score: float
    ) -> str:
        """Gợi ý dựa trên kết quả"""
        if not passed_binary:
            return "Code không đạt yêu cầu cơ bản. Cần viết lại."
        
        if final_score >= 9.0:
            return "Xuất sắc! Không cần sửa."
        elif final_score >= 8.0:
            return "Tốt! Có thể cải thiện một số điểm."
        elif final_score >= 7.0:
            return "Khá. Cần sửa các lỗi Major."
        elif final_score >= 6.0:
            return "Chưa tốt. Cần sửa nhiều lỗi."
        else:
            return "Không đạt. Cần sửa các lỗi Fatal."
    
    def get_llm_client(self) -> LLMClient:
        """Lấy LLM client hiện tại"""
        return self.llm_client
    
    def set_llm_client(self, llm_client: LLMClient):
        """Thay đổi LLM client"""
        self.llm_client = llm_client
        self.binary_assessor = BinaryAssessor(llm_client)
        self.taxonomy_assessor = TaxonomyAssessor(llm_client)
        logger.info("LLM client updated")


# ============================================================================
# EXAMPLE USAGE  
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    problem = """
    Viết hàm tính giai thừa (factorial) của một số nguyên dương n.
    Hàm sẽ nhận vào n và trả về n!
    """
    
    correct_code = """
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
    """
    
    wrong_code = """
def factorial(n):
    return n * (n - 1)  # Sai logic!
    """
    
    # Khởi tạo
    assessor = IntegratedAssessor(run_both_assessments=True)
    
    print("\\n=== Testing correct code ===")
    try:
        import json
        result = assessor.assess(problem, correct_code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Skipped: {e}")
    
    print("\\n=== Testing wrong code ===")
    try:
        result = assessor.assess(problem, wrong_code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Skipped: {e}")
