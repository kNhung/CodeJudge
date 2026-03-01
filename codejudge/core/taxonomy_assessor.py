"""
Taxonomy Assessor - Chấm điểm chi tiết (0-100)
Sử dụng phân loại lỗi: Negligible, Small, Major, Fatal
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional
from .llm_client import LLMClient, LLMFactory
from .prompts import PromptTemplates, SYSTEM_PROMPT_TAXONOMY_ASSESSMENT, ERROR_TAXONOMY

logger = logging.getLogger(__name__)


class TaxonomyAssessor:
    """
    Chấm điểm chi tiết và phân loại lỗi
    
    Kỹ thuật: Fault Localization with Error Taxonomy
    - Phân tích code
    - Xác định lỗi theo 4 cấp độ
    - Tính điểm dựa trên mức phạt
    """
    
    def __init__(
        self,
        llm_client: LLMClient = None,
        system_prompt: str = SYSTEM_PROMPT_TAXONOMY_ASSESSMENT,
        error_taxonomy: Dict = None
    ):
        """
        Khởi tạo Taxonomy Assessor
        
        Args:
            llm_client: LLM client instance
            system_prompt: Custom system prompt
            error_taxonomy: Custom error taxonomy (nếu None, dùng default)
        """
        self.llm_client = llm_client or LLMFactory.create()
        self.system_prompt = system_prompt
        self.error_taxonomy = error_taxonomy or ERROR_TAXONOMY
    
    def assess(
        self,
        problem_statement: str,
        student_code: str,
        reference_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chấm điểm chi tiết code
        
        Args:
            problem_statement: Đề bài
            student_code: Code của sinh viên
            reference_code: Code mẫu (tùy chọn, giúp xác định lỗi tốt hơn)
        
        Returns:
            {
                "errors": [
                    {
                        "type": "Major",
                        "description": "...",
                        "code_snippet": "...",
                        "fix_suggestion": "..."
                    }
                ],
                "quality_score": 90,
                "reasoning": "...",
                "penalty_breakdown": {
                    "Negligible": 0,
                    "Small": 0,
                    "Major": -50,
                    "Fatal": 0
                },
                "final_score": 50
            }
        """
        logger.info("=== Taxonomy Assessment ===")
        logger.info(f"Problem: {problem_statement[:100]}...")
        
        # Gửi prompt yêu cầu LLM chấm điểm
        user_prompt = PromptTemplates.format_taxonomy(
            problem_statement=problem_statement,
            student_code=student_code,
            reference_code=reference_code
        )
        
        # Gọi LLM
        llm_response = self.llm_client.call(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            format_json=True
        )
        
        # Parse response
        result = self._parse_llm_response(llm_response)
        
        # Tính toán final score
        final_score = self._calculate_final_score(result["errors"])
        result["final_score"] = final_score
        
        logger.info(f"Final Score: {final_score}")
        
        return result
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response từ LLM
        """
        logger.debug("Parsing LLM response...")
        
        try:
            # Thử parse JSON trực tiếp
            data = json.loads(response)
            
            # Validate structure
            if "errors" not in data:
                data["errors"] = []
            
            if "quality_score" not in data:
                data["quality_score"] = 100
            
            if "reasoning" not in data:
                data["reasoning"] = ""
            
            return data
        
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON. Trying extraction...")
            
            # Thử trích xuất JSON từ text
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, response)
            
            if matches:
                json_str = max(matches, key=len)
                try:
                    data = json.loads(json_str)
                    return self._parse_llm_response(json.dumps(data))
                except json.JSONDecodeError:
                    logger.error(f"Could not parse extracted JSON")
            
            # Fallback: No errors found
            logger.warning("Using fallback: No errors detected")
            return {
                "errors": [],
                "quality_score": 100,
                "reasoning": "LLM response could not be parsed",
                "raw_response": response[:500]
            }
    
    def _calculate_final_score(self, errors: List[Dict]) -> int:
        """
        Tính điểm cuối cùng dựa trên lỗi
        
        Công thức:
        Điểm = Max(0, 100 - Tổng_Điểm_Phạt)
        
        Mức phạt:
        - Negligible: 0 điểm
        - Small: -5 điểm
        - Major: -50 điểm
        - Fatal: -100 điểm
        """
        logger.debug("Calculating final score...")
        
        total_penalty = 0
        penalty_breakdown = {
            "Negligible": 0,
            "Small": 0,
            "Major": 0,
            "Fatal": 0
        }
        
        for error in errors:
            error_type = error.get("type", "Negligible")
            
            # Validate error type
            if error_type not in self.error_taxonomy:
                logger.warning(f"Unknown error type: {error_type}")
                error_type = "Negligible"
            
            # Lấy penalty
            penalty = self.error_taxonomy[error_type]["penalty"]
            total_penalty += penalty
            penalty_breakdown[error_type] += penalty
            
            logger.debug(f"Error: {error_type}, Penalty: {penalty}")
        
        # Công thức: Max(0, 100 - total_penalty)
        final_score = max(0, 100 + total_penalty)  # total_penalty đã là âm
        
        logger.debug(f"Total penalty: {total_penalty}, Final score: {final_score}")
        logger.debug(f"Breakdown: {penalty_breakdown}")
        
        return final_score
    
    def get_penalty_breakdown(self, final_score: int, total_penalty: int) -> Dict:
        """
        Chi tiết cách tính penalty
        """
        return {
            "base_score": 100,
            "total_penalty": total_penalty,
            "final_score": final_score,
            "formula": "Max(0, 100 - TotalPenalty)"
        }
    
    def set_system_prompt(self, custom_prompt: str):
        """Thiết lập custom system prompt"""
        self.system_prompt = custom_prompt
        logger.info("System prompt updated")
    
    def set_error_taxonomy(self, custom_taxonomy: Dict):
        """Thiết lập custom error taxonomy"""
        self.error_taxonomy = custom_taxonomy
        logger.info("Error taxonomy updated")
    
    def get_error_taxonomy_info(self) -> Dict:
        """Lấy thông tin error taxonomy"""
        return self.error_taxonomy


class ErrorClassifier:
    """
    Phân loại lỗi từ response
    """
    
    @staticmethod
    def classify_errors(errors: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Phân loại lỗi theo type
        """
        classified = {
            "Negligible": [],
            "Small": [],
            "Major": [],
            "Fatal": []
        }
        
        for error in errors:
            error_type = error.get("type", "Negligible")
            if error_type in classified:
                classified[error_type].append(error)
            else:
                classified["Negligible"].append(error)
        
        return classified
    
    @staticmethod
    def get_critical_errors(errors: List[Dict]) -> List[Dict]:
        """
        Lấy các lỗi nghiêm trọng (Major, Fatal)
        """
        return [e for e in errors if e.get("type") in ["Major", "Fatal"]]
    
    @staticmethod
    def get_error_summary(errors: List[Dict]) -> str:
        """
        Tạo summary của các lỗi
        """
        if not errors:
            return "No errors found - code is correct!"
        
        classified = ErrorClassifier.classify_errors(errors)
        
        summary_parts = []
        for error_type, error_list in classified.items():
            if error_list:
                summary_parts.append(f"{error_type}: {len(error_list)} errors")
        
        return " | ".join(summary_parts)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    problem = """
    Viết hàm tìm giá trị lớn nhất trong danh sách
    """
    
    buggy_code = """
def find_max(numbers):
    if not numbers:
        # Missing return statement
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
    """
    
    assessor = TaxonomyAssessor()
    
    print("\\n=== Testing Taxonomy Assessment ===")
    try:
        result = assessor.assess(problem, buggy_code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Skipped (no LLM configured): {e}")
