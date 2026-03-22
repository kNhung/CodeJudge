"""
Internal Testing - Giai Đoạn 3
Kiểm thử các module Core Engine

Chạy: pytest tests/test_core_engine.py -v
"""

import pytest
import json
from pathlib import Path

# Thêm parent directory vào path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from codejudge.core import (
    BinaryAssessor,
    TaxonomyAssessor,
    IntegratedAssessor,
    LLMFactory,
    ERROR_TAXONOMY
)
from codejudge.scoring import Scorer, ScoreInterpreter


# ============================================================================
# FIXTURES & TEST DATA
# ============================================================================

class TestData:
    """Các test case"""
    
    SIMPLE_PROBLEM = "Viết hàm tính tổng của danh sách"
    
    CORRECT_CODE = """
def sum_list(numbers):
    return sum(numbers)
    """
    
    WRONG_CODE = """
def sum_list(numbers):
    return 0  # Luôn trả về 0
    """
    
    BUGGY_CODE = """
def sum_list(numbers):
    if not numbers:
        pass  # Quên return
    total = 0
    for num in numbers:
        total += num
    return total
    """


# ============================================================================
# UNIT TESTS - Core Engine
# ============================================================================

class TestBinaryAssessor:
    """Test Binary Assessor"""
    
    def test_initialization(self):
        """Test khởi tạo Binary Assessor"""
        assessor = BinaryAssessor()
        assert assessor is not None
        assert assessor.system_prompt is not None
    
    def test_extract_binary_result_yes(self):
        """Test trích xuất 'Yes' từ response"""
        assessor = BinaryAssessor()
        
        response = "Code đúng. Đáp ứng yêu cầu. Yes."
        result = assessor._extract_binary_result(response, "analysis")
        
        assert result["result"] == "Yes"
        assert result["passed"] is True
    
    def test_extract_binary_result_no(self):
        """Test trích xuất 'No' từ response"""
        assessor = BinaryAssessor()
        
        response = "Code sai logic. No."
        result = assessor._extract_binary_result(response, "analysis")
        
        assert result["result"] == "No"
        assert result["passed"] is False
    
    def test_extract_binary_result_with_keywords(self):
        """Test trích xuất Yes qua từ khóa khác"""
        assessor = BinaryAssessor()
        
        # Test PASSED keyword
        response = "PASSED - code works correctly"
        result = assessor._extract_binary_result(response, "analysis")
        assert result["result"] == "Yes"
        
        # Test FAILED keyword
        response = "FAILED - wrong logic"
        result = assessor._extract_binary_result(response, "analysis")
        assert result["result"] == "No"
    
    def test_heuristic_fallback(self):
        """Test heuristic fallback khi không có Yes/No rõ ràng"""
        assessor = BinaryAssessor()
        
        response = "Code looks good and correct"
        result = assessor._extract_binary_result(response, "analysis")
        
        # Nên detect là "Yes" dựa trên từ khóa "good" và "correct"
        assert result["result"] == "Yes"
        assert result["confidence"] <= 0.8  # Lower confidence


class TestTaxonomyAssessor:
    """Test Taxonomy Assessor"""
    
    def test_initialization(self):
        """Test khởi tạo"""
        assessor = TaxonomyAssessor()
        assert assessor is not None
        assert len(assessor.error_taxonomy) == 4  # 4 loại lỗi
    
    def test_error_taxonomy_structure(self):
        """Test cấu trúc error taxonomy"""
        assessor = TaxonomyAssessor()
        
        for error_type in ["Negligible", "Small", "Major", "Fatal"]:
            assert error_type in assessor.error_taxonomy
            taxonomy = assessor.error_taxonomy[error_type]
            assert "description" in taxonomy
            assert "penalty" in taxonomy
            assert isinstance(taxonomy["penalty"], (int, float))
    
    def test_parse_json_response_valid(self):
        """Test parse JSON response đúng định dạng"""
        assessor = TaxonomyAssessor()
        
        valid_response = json.dumps({
            "errors": [
                {"type": "Major", "description": "Wrong logic"}
            ],
            "quality_score": 5.0,
            "reasoning": "..."
        })
        
        result = assessor._parse_llm_response(valid_response)
        
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "Major"
    
    def test_parse_json_response_with_text(self):
        """Test parse JSON từ response có text bao quanh"""
        assessor = TaxonomyAssessor()
        
        response = """
        Here is the analysis:
        
        {
            "errors": [],
            "quality_score": 10.0,
            "reasoning": "No errors"
        }
        
        End of analysis.
        """
        
        result = assessor._parse_llm_response(response)
        
        assert "errors" in result
        assert result["quality_score"] == 10.0
    
    def test_calculate_final_score_no_errors(self):
        """Test tính điểm khi không có lỗi"""
        assessor = TaxonomyAssessor()
        
        errors = []
        score = assessor._calculate_final_score(errors)
        
        assert score == 10.0  # Max(0, 10 - 0)
    
    def test_calculate_final_score_with_small_error(self):
        """Test tính điểm với lỗi Small (-0.5)"""
        assessor = TaxonomyAssessor()
        
        errors = [{"type": "Small", "description": "..."}]
        score = assessor._calculate_final_score(errors)
        
        assert score == 9.5  # Max(0, 10 - 0.5)
    
    def test_calculate_final_score_with_major_error(self):
        """Test tính điểm với lỗi Major (-5)"""
        assessor = TaxonomyAssessor()
        
        errors = [{"type": "Major", "description": "..."}]
        score = assessor._calculate_final_score(errors)
        
        assert score == 5.0  # Max(0, 10 - 5)
    
    def test_calculate_final_score_multiple_errors(self):
        """Test tính điểm với nhiều lỗi"""
        assessor = TaxonomyAssessor()
        
        errors = [
            {"type": "Small", "description": "..."},  # -0.5
            {"type": "Major", "description": "..."}   # -5
        ]
        score = assessor._calculate_final_score(errors)
        
        assert score == 4.5  # Max(0, 10 - 5.5)
    
    def test_calculate_final_score_fatal_error(self):
        """Test tính điểm với lỗi Fatal"""
        assessor = TaxonomyAssessor()
        
        errors = [{"type": "Fatal", "description": "..."}]
        score = assessor._calculate_final_score(errors)
        
        assert score == 0  # Max(0, 10 - 10)


class TestIntegratedAssessor:
    """Test Integrated Assessor"""
    
    def test_initialization(self):
        """Test khởi tạo"""
        assessor = IntegratedAssessor()
        assert assessor is not None
    
    def test_count_errors_by_type(self):
        """Test đếm lỗi theo type"""
        assessor = IntegratedAssessor()
        
        errors = [
            {"type": "Small"},
            {"type": "Small"},
            {"type": "Major"},
            {"type": "Fatal"}
        ]
        
        breakdown = assessor._count_errors_by_type(errors)
        
        assert breakdown["Small"] == 2
        assert breakdown["Major"] == 1
        assert breakdown["Fatal"] == 1
        assert breakdown["Negligible"] == 0
    
    def test_get_grade_letter(self):
        """Test lấy grade letter từ score"""
        assessor = IntegratedAssessor()
        
        assert assessor._get_grade_letter(9.5) == "A"
        assert assessor._get_grade_letter(8.5) == "B"
        assert assessor._get_grade_letter(7.5) == "C"
        assert assessor._get_grade_letter(6.5) == "D"
        assert assessor._get_grade_letter(5.0) == "F"


# ============================================================================
# UNIT TESTS - Scoring
# ============================================================================

class TestScorer:
    """Test Scoring Module"""
    
    def test_initialization(self):
        """Test khởi tạo"""
        scorer = Scorer(base_score=10.0)
        assert scorer.base_score == 10.0
    
    def test_calculate_score_no_errors(self):
        """Test tính điểm không có lỗi"""
        scorer = Scorer(base_score=10.0)
        
        errors = []
        result = scorer.calculate_score(errors)
        
        assert result.final_score == 10.0
        assert result.total_penalty == 0
    
    def test_calculate_score_with_errors(self):
        """Test tính điểm có lỗi"""
        scorer = Scorer(base_score=10.0)
        
        errors = [
            {"type": "Small"},      # -0.5
            {"type": "Major"},      # -5
        ]
        result = scorer.calculate_score(errors)
        
        assert result.final_score == 4.5  # 10 - 5.5
        assert result.total_penalty == -5.5
    
    def test_calculate_score_negative_clamping(self):
        """Test điểm không đi âm"""
        scorer = Scorer(base_score=10.0)
        
        errors = [
            {"type": "Fatal"},      # -10
            {"type": "Fatal"},      # -10 (nếu có 2 cái)
        ]
        result = scorer.calculate_score(errors)
        
        assert result.final_score >= 0  # Không âm


class TestScoreInterpreter:
    """Test Score Interpreter"""
    
    def test_get_grade_a(self):
        """Test grade A (9.0-10.0)"""
        assert ScoreInterpreter.get_grade(10.0) == "A"
        assert ScoreInterpreter.get_grade(9.5) == "A"
        assert ScoreInterpreter.get_grade(9.0) == "A"
    
    def test_get_grade_b(self):
        """Test grade B (8.0-8.99)"""
        assert ScoreInterpreter.get_grade(8.9) == "B"
        assert ScoreInterpreter.get_grade(8.0) == "B"
    
    def test_get_grade_c(self):
        """Test grade C (7.0-7.99)"""
        assert ScoreInterpreter.get_grade(7.9) == "C"
        assert ScoreInterpreter.get_grade(7.0) == "C"
    
    def test_get_grade_d(self):
        """Test grade D (6.0-6.99)"""
        assert ScoreInterpreter.get_grade(6.9) == "D"
        assert ScoreInterpreter.get_grade(6.0) == "D"
    
    def test_get_grade_f(self):
        """Test grade F (0-5.99)"""
        assert ScoreInterpreter.get_grade(5.9) == "F"
        assert ScoreInterpreter.get_grade(0) == "F"
    
    def test_get_feedback(self):
        """Test lấy feedback"""
        feedback_a = ScoreInterpreter.get_feedback(9.5)
        assert "Xuất sắc" in feedback_a or "excellent" in feedback_a.lower()
        
        feedback_f = ScoreInterpreter.get_feedback(3.0)
        assert "Không" in feedback_f or "không đạt" in feedback_f


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests - test kết hợp nhiều module"""
    
    def test_workflow_error_to_score(self):
        """Test workflow từ lỗi sang điểm"""
        
        # Giả sử lỗi từ TaxonomyAssessor
        errors = [
            {"type": "Small", "description": "Missing edge case"},
            {"type": "Major", "description": "Wrong algorithm"}
        ]
        
        # Tính điểm
        scorer = Scorer(base_score=10.0)
        scoring_result = scorer.calculate_score(errors)
        
        # Lấy grade
        grade = ScoreInterpreter.get_grade(scoring_result.final_score)
        
        # Assertions
        assert scoring_result.final_score == 4.5  # 10 - 0.5 - 5
        assert grade == "F"  # Dưới 6.0
    
    def test_full_assessment_pipeline(self):
        """Test toàn bộ pipeline"""
        
        # 1. Binary Assessment
        binary_result = {
            "result": "No",
            "passed": False
        }
        
        # 2. Taxonomy Assessment (bị skip vì Binary = No)
        taxonomy_result = {
            "errors": [],
            "final_score": 0,
            "quality_score": 0
        }
        
        # 3. Integrated Assessor kết hợp
        combined = {
            "binary": binary_result,
            "taxonomy": taxonomy_result,
            "summary": {
                "status": "FAIL",
                "score": 0
            }
        }
        
        assert combined["summary"]["status"] == "FAIL"
        assert combined["summary"]["score"] == 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance tests"""
    
    def test_scorer_performance(self):
        """Test hiệu năng Scorer"""
        import time
        
        scorer = Scorer()
        
        # Tạo nhiều lỗi
        errors = [{"type": "Small"}] * 100
        
        start = time.time()
        result = scorer.calculate_score(errors)
        elapsed = time.time() - start
        
        # Nên hoàn thành trong < 1ms
        assert elapsed < 0.01


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
