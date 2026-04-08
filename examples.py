"""
CodeJudge - Ví Dụ Sử Dụng Hoàn Chỉnh
Chạy script này để test hệ thống

Trước khi chạy:
1. Tạo .env từ .env.example
2. Điền API key
3. pip install -r requirements-codejudge.txt
"""

import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Binary Assessment
# ============================================================================

def example_binary_assessment():
    """Ví dụ 1: Chấm điểm Đạt/Không Đạt"""
    
    logger.info("\\n" + "="*60)
    logger.info("EXAMPLE 1: Binary Assessment (Đạt/Không Đạt)")
    logger.info("="*60)
    
    try:
        from codejudge import BinaryAssessor
        
        # Định nghĩa bài tập
        problem = """
        Viết hàm tính tổng của danh sách số
        
        Input: Danh sách số
        Output: Tổng các số trong danh sách
        
        Ví dụ:
        - sum_list([1, 2, 3]) = 6
        - sum_list([10, 20]) = 30
        - sum_list([]) = 0
        """
        
        # Code đúng
        code_correct = """
def sum_list(numbers):
    return sum(numbers)
        """
        
        # Code sai (logic sai)
        code_wrong = """
def sum_list(numbers):
    # Quên implement
    return 0
        """
        
        # Khởi tạo assessor
        assessor = BinaryAssessor()
        
        # Test code đúng
        logger.info("\\n--- Testing CORRECT code ---")
        print("Code:", code_correct.strip())
        
        result = assessor.assess(problem, code_correct)
        logger.info(f"Result: {result['result']}")
        logger.info(f"Passed: {result['passed']}")
        logger.info(f"Confidence: {result['confidence']}")
        
        # Test code sai
        logger.info("\\n--- Testing WRONG code ---")
        print("Code:", code_wrong.strip())
        
        result = assessor.assess(problem, code_wrong)
        logger.info(f"Result: {result['result']}")
        logger.info(f"Passed: {result['passed']}")
        
    except Exception as e:
        logger.error(f"Binary Assessment example failed: {e}")
        logger.info("(Có thể do không có LLM configured)")


# ============================================================================
# EXAMPLE 2: Taxonomy Assessment
# ============================================================================

def example_taxonomy_assessment():
    """Ví dụ 2: Chấm điểm chi tiết 0-100"""
    
    logger.info("\\n" + "="*60)
    logger.info("EXAMPLE 2: Taxonomy Assessment (0-100)")
    logger.info("="*60)
    
    try:
        from codejudge import TaxonomyAssessor
        import json
        
        problem = """
        Viết hàm tìm số lớn nhất trong danh sách
        
        Input: Danh sách số nguyên
        Output: Số lớn nhất
        
        Yêu cầu:
        - Xử lý danh sách rỗng
        - Xử lý số âm
        """
        
        code_buggy = """
def find_max(numbers):
    # Quên xử lý empty list
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
        """
        
        code_reference = """
def find_max(numbers):
    if not numbers:
        raise ValueError("List is empty")
    return max(numbers)
        """
        
        # Khởi tạo assessor
        assessor = TaxonomyAssessor()
        
        # Chấm điểm
        logger.info("\\n--- Assessing code ---")
        result = assessor.assess(
            problem_statement=problem,
            student_code=code_buggy,
            reference_code=code_reference
        )
        
        # In kết quả
        logger.info(f"\\nFinal Score: {result['final_score']}/100")
        logger.info(f"Quality Score: {result.get('quality_score', 'N/A')}")
        logger.info(f"Errors found: {len(result.get('errors', []))}")
        
        # In errors chi tiết
        if result.get('errors'):
            logger.info("\\nError details:")
            for i, error in enumerate(result['errors'], 1):
                logger.info(f"  {i}. {error.get('type')}: {error.get('description')}")
        
    except Exception as e:
        logger.error(f"Taxonomy Assessment example failed: {e}")
        logger.info("(Có thể do không có LLM configured)")


# ============================================================================
# EXAMPLE 3: Integrated Assessment
# ============================================================================

def example_integrated_assessment():
    """Ví dụ 3: Integrated Assessment (Được khuyến nghị)"""
    
    logger.info("\\n" + "="*60)
    logger.info("EXAMPLE 3: Integrated Assessment (Khuyến nghị nhất)")
    logger.info("="*60)
    
    try:
        from codejudge import IntegratedAssessor
        import json
        
        problem = """
        Viết hàm tính giai thừa (factorial)
        
        Input: Số nguyên dương n
        Output: n!
        
        Ví dụ:
        - factorial(5) = 120
        - factorial(0) = 1
        """
        
        code_good = """
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
        """
        
        # Khởi tạo integrated assessor
        assessor = IntegratedAssessor(run_both_assessments=True)
        
        logger.info("\\n--- Running Integrated Assessment ---")
        result = assessor.assess(
            problem_statement=problem,
            student_code=code_good
        )
        
        # In summary
        summary = result['summary']
        logger.info(f"\\nStatus: {summary['status']}")
        logger.info(f"Score: {summary['score']}/100")
        logger.info(f"Grade: {summary['grade_letter']}")
        logger.info(f"Recommendation: {summary['recommendation']}")
        
        # In binary result
        logger.info(f"\\nBinary Assessment: {result['binary']['result']}")
        logger.info(f"Passed: {result['binary']['passed']}")
        
        # In taxonomy details
        taxonomy = result['taxonomy']
        logger.info(f"\\nErrors: {taxonomy['errors_count']}")
        breakdown = taxonomy['error_breakdown']
        for error_type, count in breakdown.items():
            if count > 0:
                logger.info(f"  {error_type}: {count}")
        
    except Exception as e:
        logger.error(f"Integrated Assessment example failed: {e}")
        logger.info("(Có thể do không có LLM configured)")


# ============================================================================
# EXAMPLE 4: Custom LLM Provider
# ============================================================================

def example_custom_llm():
    """Ví dụ 4: Sử dụng LLM provider khác"""
    
    logger.info("\\n" + "="*60)
    logger.info("EXAMPLE 4: Custom LLM Provider")
    logger.info("="*60)
    
    try:
        from codejudge import LLMFactory, IntegratedAssessor
        
        # Option A: OpenAI GPT-4 (mặc định)
        logger.info("\\n--- Creating OpenAI client ---")
        gpt4_client = LLMFactory.create("openai", model_name="gpt-4")
        logger.info(f"Created: {gpt4_client.__class__.__name__}")
        
        # Option B: Claude (Anthropic)
        logger.info("\\n--- Creating Anthropic client ---")
        try:
            claude_client = LLMFactory.create(
                "anthropic",
                model_name="claude-3-opus-20240229"
            )
            logger.info(f"Created: {claude_client.__class__.__name__}")
        except ValueError as e:
            logger.warning(f"Anthropic not configured: {e}")
        
        # Option C: Local LLM (Ollama, vLLM)
        logger.info("\\n--- Creating Local LLM client ---")
        try:
            local_client = LLMFactory.create(
                "local",
                model_name="llama2",
                base_url="http://localhost:11434"
            )
            logger.info(f"Created: {local_client.__class__.__name__}")
        except Exception as e:
            logger.warning(f"Local LLM not available: {e}")
        
        # Sử dụng custom client
        logger.info("\\n--- Using custom client with IntegratedAssessor ---")
        assessor = IntegratedAssessor(llm_client=gpt4_client)
        logger.info("Assessor created with custom GPT-4 client")
        
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        logger.info("Make sure to install: pip install -r requirements-codejudge.txt")


# ============================================================================
# EXAMPLE 5: Scoring & Interpretation
# ============================================================================

def example_scoring():
    """Ví dụ 5: Tính toán điểm và phân tích"""
    
    logger.info("\\n" + "="*60)
    logger.info("EXAMPLE 5: Scoring & Interpretation")
    logger.info("="*60)
    
    try:
        from codejudge.scoring import Scorer, ScoreInterpreter, ResultFormatter
        
        # Giả sử có các lỗi
        errors = [
            {"type": "Negligible", "description": "Missing comments"},
            {"type": "Small", "description": "Missing edge case handling"},
            {"type": "Major", "description": "Wrong algorithm"},
        ]
        
        # Tính điểm
        logger.info("\\n--- Calculating score from errors ---")
        scorer = Scorer(base_score=100)
        scoring_result = scorer.calculate_score(errors)
        
        logger.info(f"Base Score: {scoring_result.base_score}")
        logger.info(f"Final Score: {scoring_result.final_score}")
        logger.info(f"Total Penalty: {scoring_result.total_penalty}")
        
        # Phân tích điểm
        logger.info("\\n--- Score interpretation ---")
        score = scoring_result.final_score
        grade = ScoreInterpreter.get_grade(score)
        feedback = ScoreInterpreter.get_feedback(score)
        
        logger.info(f"Grade: {grade}")
        logger.info(f"Feedback: {feedback}")
        
        # Format kết quả
        logger.info("\\n--- Formatted result ---")
        full_result = ResultFormatter.format_full_result(
            scoring_result,
            errors
        )
        logger.info("Full result:")
        print(json.dumps(full_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Scoring example failed: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Chạy tất cả các ví dụ"""
    
    logger.info("\\n" + "="*80)
    logger.info("CodeJudge - Usage Examples")
    logger.info("="*80)
    
    # Check if .env file exists
    if not Path('.env').exists() and not Path('.env.example').exists():
        logger.warning("\\n⚠️  .env file not found!")
        logger.warning("Please create .env file (copy from .env.example) with API key")
        logger.warning("Only Example 5 (Scoring) will work without LLM")
    
    # Run examples
    print("\\n\\nRunning examples...\\n")
    
    # Example 5 - không cần LLM
    example_scoring()
    
    # Examples 1-4 - cần LLM (optional)
    try:
        example_binary_assessment()
        example_taxonomy_assessment()
        example_integrated_assessment()
        example_custom_llm()
    except ImportError as e:
        logger.warning(f"\\nSkipping LLM examples: {e}")
        logger.warning("To use LLM examples:")
        logger.warning("1. pip install -r requirements-codejudge.txt")
        logger.warning("2. Create .env with API key")
    
    logger.info("\\n" + "="*80)
    logger.info("Examples completed!")
    logger.info("="*80)


if __name__ == "__main__":
    main()
