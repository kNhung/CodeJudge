"""
Binary Assessor - Chấm điểm Đạt/Không Đạt
Sử dụng kỹ thuật "Analyze then Summarize"
"""

import re
import logging
from typing import Dict, Any, Tuple
from .llm_client import LLMClient, LLMFactory
from .prompts import PromptTemplates, SYSTEM_PROMPT_BINARY_ASSESSMENT

logger = logging.getLogger(__name__)


class BinaryAssessor:
    """
    Chấm điểm Binary (Yes/No - Đạt/Không Đạt)
    
    Kỹ thuật: Analyze then Summarize
    - Bước 1: Gửi prompt yêu cầu LLM phân tích chi tiết từng bước
    - Bước 2: Gửi kết quả phân tích, yêu cầu kết luận "Yes" hoặc "No"
    - Bước 3: Dùng Regex bắt từ khóa "Yes"/"No"
    """
    
    def __init__(
        self,
        llm_client: LLMClient = None,
        system_prompt: str = SYSTEM_PROMPT_BINARY_ASSESSMENT
    ):
        """
        Khởi tạo Binary Assessor
        
        Args:
            llm_client: LLM client instance (nếu None, dùng default)
            system_prompt: Custom system prompt
        """
        self.llm_client = llm_client or LLMFactory.create()
        self.system_prompt = system_prompt
    
    def assess(
        self,
        problem_statement: str,
        student_code: str,
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Chấm điểm binary cho code
        
        Args:
            problem_statement: Đề bài
            student_code: Code của sinh viên
            language: Ngôn ngữ lập trình của bài làm
        
        Returns:
            {
                "result": "Yes" | "No",
                "analysis": "<kết quả phân tích>",
                "passed": True | False,
                "confidence": 0.0-1.0
            }
        """
        logger.info(f"=== Binary Assessment ===")
        logger.info(f"Problem: {problem_statement[:100]}...")
        
        # Bước 1: Phân tích (Analyze)
        analysis = self._analyze_step(problem_statement, student_code, language)
        logger.info(f"Analysis completed")
        
        # Bước 2: Tóm tắt (Summarize)
        result = self._summarize_step(analysis)
        logger.info(f"Result: {result}")
        
        return result
    
    def _analyze_step(
        self,
        problem_statement: str,
        student_code: str,
        language: str = "Python"
    ) -> str:
        """
        Bước 1: Phân tích code chi tiết từng bước
        Không yêu cầu sửa code, chỉ phân tích
        """
        logger.debug("Step 1: Analyzing code...")
        
        # Format prompt
        user_prompt = PromptTemplates.format_binary_analyze(
            problem_statement=problem_statement,
            student_code=student_code,
            language=language,
        )
        
        # Gọi LLM
        analysis = self.llm_client.call(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            format_json=False
        )
        
        return analysis
    
    def _summarize_step(self, analysis: str) -> Dict[str, Any]:
        """
        Bước 2: Tóm tắt kết quả phân tích thành "Yes" hoặc "No"
        """
        logger.debug("Step 2: Summarizing analysis...")
        
        # Format prompt tóm tắt
        user_prompt = PromptTemplates.format_binary_summarize(analysis)
        
        # Gọi LLM
        summary = self.llm_client.call(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            format_json=False
        )
        
        # Bước 3: Bắt "Yes" hoặc "No"
        result = self._extract_binary_result(summary, analysis)
        
        return result
    
    def _extract_binary_result(
        self,
        summary: str,
        full_analysis: str
    ) -> Dict[str, Any]:
        """
        Trích xuất "Yes" hoặc "No" từ summary
        Sử dụng Regex để tìm từ khóa "Yes"/"No"
        """
        logger.debug("Extracting binary result from summary...")
        
        # Normalize text
        text = summary.upper().strip()
        
        # Patterns để bắt Yes/No
        yes_patterns = [
            r'\bYES\b',
            r'✓\s*YES',
            r'PASSED?',
            r'CORRECT',
            r'ĐẠTT?',  # Vietnamese: Đạt
        ]
        
        no_patterns = [
            r'\bNO\b',
            r'✗\s*NO',
            r'FAILED?',
            r'INCORRECT',
            r'KHÔNG\s*ĐẠT',  # Vietnamese: Không Đạt
        ]
        
        # Check Yes patterns
        for pattern in yes_patterns:
            if re.search(pattern, text):
                logger.info(f"Detected 'Yes' pattern: {pattern}")
                return {
                    "result": "Yes",
                    "passed": True,
                    "analysis": full_analysis,
                    "summary": summary,
                    "confidence": 0.95
                }
        
        # Check No patterns
        for pattern in no_patterns:
            if re.search(pattern, text):
                logger.info(f"Detected 'No' pattern: {pattern}")
                return {
                    "result": "No",
                    "passed": False,
                    "analysis": full_analysis,
                    "summary": summary,
                    "confidence": 0.95
                }
        
        # Nếu không tìm thấy rõ ràng, dùng heuristics
        logger.warning(f"No clear Yes/No detected. Using heuristics...")
        
        # Heuristic: Nếu có nhiều "Good", "Correct", "Pass" → Yes
        positive_words = ["good", "correct", "pass", "đúng", "đạt", "hoàn thành"]
        negative_words = ["error", "wrong", "fail", "bug", "sai", "không", "lỗi"]
        
        text_lower = summary.lower()
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        if positive_count > negative_count:
            return {
                "result": "Yes",
                "passed": True,
                "analysis": full_analysis,
                "summary": summary,
                "confidence": 0.7  # Lower confidence
            }
        else:
            return {
                "result": "No",
                "passed": False,
                "analysis": full_analysis,
                "summary": summary,
                "confidence": 0.7
            }
    
    def set_system_prompt(self, custom_prompt: str):
        """Thiết lập custom system prompt"""
        self.system_prompt = custom_prompt
        logger.info("System prompt updated")
    
    def get_analysis_only(
        self,
        problem_statement: str,
        student_code: str
    ) -> str:
        """
        Lấy chỉ kết quả phân tích (Analyze step)
        Hữu ích cho debugging
        """
        return self._analyze_step(problem_statement, student_code)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example problem and code
    problem = """
    Viết hàm tính tổng của danh sách số
    Hàm sẽ nhận vào một list các số và trả về tổng của chúng.
    """
    
    correct_code = """
def sum_list(numbers):
    return sum(numbers)
    """
    
    wrong_code = """
def sum_list(numbers):
    return 0  # Luôn trả về 0, sai logic
    """
    
    # Khởi tạo assessor (sẽ dùng default LLM)
    assessor = BinaryAssessor()
    
    # Test code đúng
    print("\\n=== Testing correct code ===")
    try:
        result = assessor.assess(problem, correct_code)
        print(f"Result: {result['result']}")
        print(f"Passed: {result['passed']}")
    except Exception as e:
        print(f"Skipped (no LLM configured): {e}")
    
    # Test code sai
    print("\\n=== Testing wrong code ===")
    try:
        result = assessor.assess(problem, wrong_code)
        print(f"Result: {result['result']}")
        print(f"Passed: {result['passed']}")
    except Exception as e:
        print(f"Skipped (no LLM configured): {e}")
