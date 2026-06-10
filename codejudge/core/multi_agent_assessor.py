import json
import re
import logging
from typing import List, Dict, Any, Optional
from .llm_client import LLMClient, LLMFactory
from .compiler_helper import check_syntax

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_FACTOR_EXTRACTOR = """Bạn là chuyên gia phân tích nghiệp vụ đề bài lập trình.
Nhiệm vụ của bạn là đọc kỹ đề bài (hoặc câu hỏi) và phân tích tách nhỏ thành các yêu cầu logic/chức năng chính (Factors) phục vụ cho việc chấm điểm.

YÊU CẦU:
1. Mỗi Factor đại diện cho một chức năng, cấu trúc dữ liệu, hoặc yêu cầu thuật toán cụ thể (Ví dụ: "Định nghĩa cấu trúc struct phù hợp", "Hàm đọc dữ liệu từ file đúng chuẩn", "Xử lý tìm kiếm chính xác", "Xử lý trường hợp biên/rỗng").
2. Bỏ qua hoàn toàn các yêu cầu về cú pháp (syntax) hay định dạng biên dịch vì lỗi cú pháp sẽ được compiler chấm riêng.
3. Số lượng các Factor nên dao động từ 2 đến 5 tùy độ phức tạp của câu hỏi.
4. Trả về kết quả DƯỚI DẠNG MỘT JSON ARRAY chứa các chuỗi factor. KHÔNG được thêm giải thích ngoài JSON.
5. Các Factor phải tập trung vào kết quả logic/chức năng đầu ra của bài toán. Tuyệt đối KHÔNG áp đặt một phương pháp giải cụ thể (ví dụ: không bắt buộc dùng stack, mảng phụ, đệ quy...) trừ khi đề bài yêu cầu rõ ràng điều đó.

VÍ DỤ OUTPUT CHUẨN:
[
  "Định nghĩa struct Pokemon với đầy đủ thuộc tính id, name, speed",
  "Hàm đọc file ReadFile lưu dữ liệu đúng định dạng",
  "Hàm tìm kiếm Search trả về kết quả chính xác theo hệ"
]
"""

SYSTEM_PROMPT_FACTOR_GRADER = """Bạn là trợ giảng chấm điểm code lập trình chuyên nghiệp và công bằng.
Nhiệm vụ của bạn là đánh giá mức độ đáp ứng (%) của code sinh viên đối với từng Factor (yêu cầu logic) được đưa ra.

YÊU CẦU:
1. Với mỗi Factor (được đánh số thứ tự từ 1), hãy xác định xem sinh viên đã viết logic/chức năng tương ứng hay chưa, và chạy đúng khoảng bao nhiêu % (từ 0.0 đến 1.0, tương ứng 0% đến 100%).
2. QUAN TRỌNG: Hãy bỏ qua hoàn toàn các lỗi cú pháp (syntax error) làm code không compile được (do lỗi cú pháp đã được chấm riêng bởi compiler). Đánh giá dựa trên tư duy, thuật toán và cấu trúc code mà sinh viên đã viết. Nếu sinh viên có ý tưởng đúng và cấu trúc đúng cho factor đó, hãy cho điểm cao dù code có thể thiếu dấu chấm phẩy hoặc sai cú pháp nhỏ.
3. Trả về kết quả DƯỚI DẠNG MỘT JSON OBJECT duy nhất. Mỗi key là INDEX (dưới dạng chuỗi, ví dụ: "1", "2") của Factor tương ứng theo đúng thứ tự trong danh sách được cung cấp. Value là một object chứa "compliance" (số thực từ 0.0 đến 1.0) và "reasoning" (giải thích ngắn gọn lý do cho điểm bằng tiếng Việt). KHÔNG thêm bất kì văn bản nào ngoài JSON.

VÍ DỤ INPUT:
Danh sách các Factor:
[
  "Định nghĩa struct Pokemon với đầy đủ thuộc tính id, name, speed",
  "Hàm đọc file ReadFile lưu dữ liệu đúng định dạng"
]

VÍ DỤ OUTPUT CHUẨN:
{
  "1": {
    "compliance": 1.0,
    "reasoning": "Sinh viên đã định nghĩa struct Pokemon đầy đủ các thuộc tính theo yêu cầu."
  },
  "2": {
    "compliance": 0.5,
    "reasoning": "Sinh viên có viết hàm ReadFile nhưng chưa xử lý chuyển đổi kiểu dữ liệu cho thuộc tính speed."
  }
}
"""

class MultiAgentAssessor:
    """
    Multi-Agent grading engine that combines compiler syntax checks
    and LLM agent steps (Factor Extraction, Factor Grading) for code assessment.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMFactory.create()

    def _clean_and_parse_json(self, response: str) -> Any:
        """Helper to extract and parse JSON block from LLM response string."""
        response = response.strip()
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback extraction: search for json code block first
            code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.IGNORECASE)
            if code_block_match:
                try:
                    return json.loads(code_block_match.group(1).strip())
                except json.JSONDecodeError:
                    pass
            
            # Simple greedy match for array or object
            greedy_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response)
            if greedy_match:
                try:
                    return json.loads(greedy_match.group(1).strip())
                except json.JSONDecodeError:
                    pass
                    
            logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError("LLM response did not contain valid JSON.")

    def extract_factors(self, question_text: str) -> List[str]:
        """Agent 1: Extract core grading factors from question text."""
        logger.info("Agent 1: Extracting factors from problem description...")
        
        user_prompt = f"Hãy phân tích và tách các Factor (yêu cầu logic) cho đề bài sau:\n\n{question_text}"
        response = self.llm_client.call(
            system_prompt=SYSTEM_PROMPT_FACTOR_EXTRACTOR,
            user_prompt=user_prompt,
            format_json=True
        )
        
        factors = self._clean_and_parse_json(response)
        if isinstance(factors, dict):
            # Try to find a list within the dictionary values
            for k, v in factors.items():
                if isinstance(v, list) and len(v) > 0:
                    factors = v
                    break
            else:
                # If no list is found, keys might be the factors
                factors = list(factors.keys())
                
        if not isinstance(factors, list):
            raise ValueError(f"Expected list of factors, got {type(factors).__name__}")
        
        # Ensure all items are strings
        return [str(f) for f in factors]

    def assess_factors(self, student_code: str, factors: List[str], language: str) -> Dict[str, Dict[str, Any]]:
        """Agent 2: Assess student code compliance against factors, ignoring syntax errors."""
        logger.info("Agent 2: Scoring student code against factors...")
        
        # Format factors with index numbers
        formatted_factors = [f"{i+1}. {factor}" for i, factor in enumerate(factors)]
        
        user_prompt = (
            f"Ngôn ngữ lập trình: {language}\n\n"
            f"Danh sách các Factor cần chấm (theo đúng thứ tự):\n"
            f"{json.dumps(formatted_factors, ensure_ascii=False, indent=2)}\n\n"
            f"Code của sinh viên:\n"
            f"```\n{student_code}\n```"
        )
        
        response = self.llm_client.call(
            system_prompt=SYSTEM_PROMPT_FACTOR_GRADER,
            user_prompt=user_prompt,
            format_json=True
        )
        
        evaluation = self._clean_and_parse_json(response)
        
        # If it returns a list, try to clean it first (fallback)
        if isinstance(evaluation, list):
            new_eval = {}
            for item in evaluation:
                if isinstance(item, dict):
                    idx_key = item.get("factor") or item.get("name") or item.get("key") or item.get("index")
                    if idx_key:
                        new_eval[str(idx_key)] = {
                            "compliance": item.get("compliance", 0.0),
                            "reasoning": item.get("reasoning", "")
                        }
            evaluation = new_eval
            
        if not isinstance(evaluation, dict):
            raise ValueError(f"Expected dict of factor grading, got {type(evaluation).__name__}")
            
        # Map the index keys back to the original factor strings
        final_eval = {}
        for key, value in evaluation.items():
            if not isinstance(value, dict):
                continue
            try:
                # Key can be "1", "factor_1", "Factor 1", etc. Extract numbers using regex.
                match = re.search(r'\d+', str(key))
                if match:
                    idx = int(match.group(0)) - 1
                    if 0 <= idx < len(factors):
                        factor_name = factors[idx]
                        final_eval[factor_name] = {
                            "compliance": float(value.get("compliance", 0.0)),
                            "reasoning": str(value.get("reasoning", ""))
                        }
            except Exception as e:
                logger.error(f"Error parsing index-based factor key '{key}': {e}")
                
        # Fill in any missing factors as fallback to avoid KeyError down the line
        for factor in factors:
            if factor not in final_eval:
                final_eval[factor] = {
                    "compliance": 0.0,
                    "reasoning": "Không thể đánh giá hoặc thiếu phản hồi từ model."
                }
                
        return final_eval

    def _classify_syntax_error(self, error_msg: str) -> float:
        err_lower = error_msg.lower()
        
        # Category 1: Warnings (Penalty: 0.25)
        if "warning:" in err_lower or "unused variable" in err_lower or "unused parameter" in err_lower:
            return 0.25
            
        # Category 2: Typos (Penalty: 0.5)
        typo_keywords = [
            "expected ';'", "expected '}'", "expected ')'", "expected ']'", 
            "suggest brackets", "return-statement with a value, in function returning 'void'"
        ]
        if any(k in err_lower for k in typo_keywords):
            return 0.5
            
        # Category 3: Major/Conceptual (Penalty: 1.5)
        return 1.5

    def calculate_score(
        self,
        factor_eval: Dict[str, Dict[str, Any]],
        syntax_errors: List[str],
        question_max: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate final score based on factors and syntax errors.
        
        Formula:
        - Factor score = average(compliance) * 10.0
        - Syntax penalty = sum(classified penalties) (capped at 5.0 points on 10-scale)
        - Final score on 10 = max(0.0, Factor score - Syntax penalty)
        - Scaled score = (Final score on 10 / 10.0) * question_max
        """
        compliance_scores = []
        for factor, details in factor_eval.items():
            if isinstance(details, dict) and "compliance" in details:
                try:
                    val = float(details["compliance"])
                    # Clamp compliance to range [0.0, 1.0]
                    val = max(0.0, min(1.0, val))
                    compliance_scores.append(val)
                except (TypeError, ValueError):
                    pass
        
        if compliance_scores:
            avg_compliance = sum(compliance_scores) / len(compliance_scores)
        else:
            avg_compliance = 0.0
            
        factor_score_on_10 = avg_compliance * 10.0
        
        # Calculate syntax error penalties based on classification
        total_penalty = 0.0
        for err in syntax_errors:
            total_penalty += self._classify_syntax_error(err)
        syntax_penalty = min(5.0, total_penalty)
        
        final_score_on_10 = max(0.0, factor_score_on_10 - syntax_penalty)
        
        result = {
            "factor_score_on_10": round(factor_score_on_10, 2),
            "syntax_penalty_on_10": round(syntax_penalty, 2),
            "final_score_on_10": round(final_score_on_10, 2),
            "compliance_average": round(avg_compliance, 4)
        }
        
        if question_max is not None:
            scaled_score = (final_score_on_10 / 10.0) * question_max
            result["scaled_score"] = round(scaled_score, 2)
            result["question_max"] = question_max
            
        return result

    def generate_suggestions(
        self,
        factor_eval: Dict[str, Dict[str, Any]],
        syntax_errors: List[str]
    ) -> List[str]:
        """Generate specific suggestions based on unsatisfied factors and compiler errors."""
        suggestions = []
        
        # Syntax suggestions first as they block compilation
        if syntax_errors:
            suggestions.append("Cần sửa đổi các lỗi cú pháp biên dịch sau:")
            for err in syntax_errors:
                suggestions.append(f"- {err}")
                
        # Factor suggestions
        unsat_factors = []
        for factor, details in factor_eval.items():
            compliance = details.get("compliance", 1.0)
            if compliance < 1.0:
                unsat_factors.append((factor, compliance, details.get("reasoning", "")))
                
        if unsat_factors:
            if syntax_errors:
                suggestions.append("") # space separator
            suggestions.append("Gợi ý cải thiện logic chương trình:")
            for factor, compliance, reasoning in unsat_factors:
                percent = int(compliance * 100)
                suggestions.append(f"- Yêu cầu '{factor}' (Đáp ứng {percent}%): {reasoning}")
                
        if not suggestions:
            suggestions.append("Tuyệt vời! Code của bạn hoàn thành tốt tất cả các yêu cầu và không có lỗi cú pháp.")
            
        return suggestions

    def assess(
        self,
        question_text: str,
        student_code: str,
        language: str = "cpp",
        question_max: Optional[float] = None
    ) -> Dict[str, Any]:
        """Run the complete Multi-Agent grading flow for a question-code pair."""
        logger.info("--- Starting Multi-Agent Assessment ---")
        
        # Reset last_usage on client
        if hasattr(self.llm_client, 'last_usage'):
            self.llm_client.last_usage = {}
            
        total_input_tokens = 0
        total_output_tokens = 0
        llm_error = False
        error_msg = ""
        
        # Step 1: Compiler syntax check
        logger.info("Step 1: Running compiler syntax check...")
        syntax_errors = check_syntax(student_code, language)
        logger.info(f"Compiler check complete. Found {len(syntax_errors)} errors.")
        
        # Step 2: Factor extraction (Agent 1)
        try:
            factors = self.extract_factors(question_text)
            if hasattr(self.llm_client, 'last_usage') and self.llm_client.last_usage:
                total_input_tokens += self.llm_client.last_usage.get("input_tokens", 0)
                total_output_tokens += self.llm_client.last_usage.get("output_tokens", 0)
        except Exception as e:
            logger.error(f"Error extracting factors: {e}")
            llm_error = True
            error_msg = f"Lỗi Agent 1 (Factor Extractor): {str(e)}"
            factors = ["Thực hiện đúng logic của câu hỏi"]
            
        # Step 3: Factor grading (Agent 2)
        if not llm_error:
            try:
                if hasattr(self.llm_client, 'last_usage'):
                    self.llm_client.last_usage = {}
                factor_eval = self.assess_factors(student_code, factors, language)
                if hasattr(self.llm_client, 'last_usage') and self.llm_client.last_usage:
                    total_input_tokens += self.llm_client.last_usage.get("input_tokens", 0)
                    total_output_tokens += self.llm_client.last_usage.get("output_tokens", 0)
            except Exception as e:
                logger.error(f"Error assessing factors: {e}")
                llm_error = True
                error_msg = f"Lỗi Agent 2 (Factor Grader): {str(e)}"
                
        if llm_error:
            # Fallback assessment indicating error
            factor_eval = {
                f: {
                    "compliance": -1.0,
                    "reasoning": f"Gặp lỗi khi gọi tác vụ chấm điểm LLM: {error_msg}"
                } for f in factors
            }
            
        # Step 4: Calculate final score
        if llm_error:
            scoring_details = {
                "factor_score_on_10": -1.0,
                "syntax_penalty_on_10": -1.0,
                "final_score_on_10": -1.0,
                "compliance_average": -1.0,
                "has_error": True,
                "error_message": error_msg
            }
            if question_max is not None:
                scoring_details["scaled_score"] = -1.0
                scoring_details["question_max"] = question_max
        else:
            scoring_details = self.calculate_score(factor_eval, syntax_errors, question_max)
        
        # Step 5: Generate suggestions
        if llm_error:
            suggestions = [f"Không thể tạo gợi ý do lỗi LLM: {error_msg}"]
            if syntax_errors:
                suggestions.append("Cần sửa đổi các lỗi cú pháp biên dịch sau:")
                for err in syntax_errors:
                    suggestions.append(f"- {err}")
        else:
            suggestions = self.generate_suggestions(factor_eval, syntax_errors)
        
        # Combine everything into final JSON output
        result = {
            "assessment_type": "multi_agent",
            "syntax_errors": syntax_errors,
            "factors": factors,
            "factor_evaluation": factor_eval,
            "scoring": scoring_details,
            "suggestions": suggestions,
            "usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens
            }
        }
        
        # Root-level metrics for compatibility
        result["final_score"] = scoring_details.get("scaled_score") if question_max is not None else scoring_details.get("final_score_on_10")
        result["quality_score"] = scoring_details.get("factor_score_on_10")
        result["total_penalty"] = scoring_details.get("syntax_penalty_on_10")
        
        return result
