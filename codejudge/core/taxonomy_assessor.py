"""
Taxonomy Assessor - Chấm điểm chi tiết (0-10)
Sử dụng phân loại lỗi: Negligible, Small, Major, Fatal
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
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
        self.additive_rubric_max = {
            "idea": 3.0,
            "flow": 2.0,
            "syntax_execution": 2.0,
            "correctness": 2.0,
            "clarity": 1.0,
        }
        self.additive_rubric_keys = [
            "idea",
            "flow",
            "syntax_execution",
            "correctness",
            "clarity",
        ]
    
    def assess(
        self,
        problem_statement: str,
        student_code: str,
        reference_code: Optional[str] = None,
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Chấm điểm chi tiết code
        
        Args:
            problem_statement: Đề bài
            student_code: Code của sinh viên
            reference_code: Code mẫu (tùy chọn, giúp xác định lỗi tốt hơn)
            language: Ngôn ngữ lập trình của bài làm
        
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
                "quality_score": 9.0,
                "reasoning": "...",
                "penalty_breakdown": {
                    "Negligible": 0,
                    "Small": 0,
                    "Major": -5,
                    "Fatal": 0
                },
                "final_score": 5.0
            }
        """
        logger.info("=== Taxonomy Assessment ===")
        logger.info(f"Problem: {problem_statement[:100]}...")
        
        # Gửi prompt yêu cầu LLM chấm điểm
        user_prompt = PromptTemplates.format_taxonomy(
            problem_statement=problem_statement,
            student_code=student_code,
            reference_code=reference_code,
            language=language,
        )
        
        # Gọi LLM
        llm_response = self.llm_client.call(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            format_json=True
        )
        llm_usage = self.llm_client.get_last_usage()
        
        # Parse response
        result = self._parse_llm_response(llm_response)

        # Normalize nested error payloads (e.g. per-submission lists)
        flat_errors = self._flatten_errors(result.get("errors", []))
        result["errors"] = flat_errors

        reasoning_text = str(result.get("reasoning", "")).strip()
        parse_failed = "could not be parsed" in reasoning_text.lower()
        
        # Ưu tiên mode cộng điểm: score_breakdown -> quality_score.
        # Chỉ fallback penalty taxonomy khi không có dữ liệu cộng điểm.
        score_breakdown, has_breakdown = self._normalize_score_breakdown(
            result.get("score_breakdown")
        )
        result["score_breakdown"] = score_breakdown

        if parse_failed:
            # Parse failure should be marked as invalid score instead of default perfect score.
            final_score = -1.0
            result["quality_score"] = -1.0
        elif has_breakdown:
            final_score = self._sum_score_breakdown(score_breakdown)
            result["quality_score"] = final_score
        else:
            fallback_score = self._coerce_score_10(result.get("quality_score"))
            if fallback_score is not None:
                final_score = fallback_score
                result["quality_score"] = fallback_score
            else:
                inferred_breakdown = self._infer_additive_breakdown_from_errors(flat_errors)
                if inferred_breakdown is not None:
                    result["score_breakdown"] = inferred_breakdown
                    final_score = self._sum_score_breakdown(inferred_breakdown)
                    result["quality_score"] = final_score
                elif self._has_typed_errors(flat_errors):
                    final_score = self._calculate_final_score(flat_errors)
                    result["quality_score"] = final_score
                else:
                    final_score = 0.0
                    result["quality_score"] = 0.0

            if result.get("reasoning") == "Parsed from list response" and result.get("score_breakdown"):
                result["reasoning"] = (
                    "LLM returned list format. Converted to additive rubric score via fallback mapping from errors."
                )

        # Nếu response có nhiều submission_* và đề có điểm tối đa từng câu,
        # tính điểm cuối cùng theo tổng điểm quy đổi từng câu.
        exam_aggregation = self._aggregate_exam_score(result, problem_statement)
        if exam_aggregation is not None:
            final_score = exam_aggregation["total_score"]
            result["quality_score"] = final_score
            result["exam_aggregation"] = exam_aggregation

        result["final_score"] = final_score
        # Keep the original model output for debugging/auditing.
        result["raw_llm_response"] = llm_response
        if llm_usage:
            result["usage"] = llm_usage
        
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

            # Gemini/smaller models sometimes return a JSON list.
            # Normalize into the expected dict schema.
            if isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    data = {
                        "errors": data,
                        "quality_score": None,
                        "reasoning": "Parsed from list response"
                    }
                else:
                    logger.warning("JSON list response is not list[dict]. Using fallback schema")
                    data = {
                        "errors": [],
                        "quality_score": None,
                        "reasoning": "LLM returned non-dict list response"
                    }

            if not isinstance(data, dict):
                logger.warning(f"Unexpected JSON type: {type(data).__name__}. Using fallback schema")
                data = {
                    "errors": [],
                    "quality_score": None,
                    "reasoning": f"LLM returned unsupported JSON type: {type(data).__name__}"
                }
            
            # Validate structure
            if "errors" not in data:
                data["errors"] = []
            
            if "quality_score" not in data:
                data["quality_score"] = None

            if "score_breakdown" not in data:
                data["score_breakdown"] = {}
            
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
                "quality_score": None,
                "score_breakdown": {},
                "reasoning": "LLM response could not be parsed",
                "raw_response": response[:500]
            }

    def _normalize_score_breakdown(self, score_breakdown: Any) -> Tuple[Dict[str, float], bool]:
        """Normalize additive score breakdown into rubric keys and bounds."""
        normalized = {key: 0.0 for key in self.additive_rubric_keys}
        if not isinstance(score_breakdown, dict):
            return normalized, False

        # Chỉ xem breakdown là hợp lệ khi có đủ 5 tiêu chí additive.
        if not all(key in score_breakdown for key in self.additive_rubric_keys):
            return normalized, False

        for key, max_score in self.additive_rubric_max.items():
            value = score_breakdown.get(key, 0)
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0
            normalized[key] = max(0.0, min(max_score, value))

        return normalized, True

    def _sum_score_breakdown(self, score_breakdown: Dict[str, float]) -> float:
        """Sum normalized additive rubric and clamp into [0, 10]."""
        total = sum(score_breakdown.values())
        return max(0.0, min(10.0, round(total, 4)))

    def _aggregate_exam_score(
        self,
        result: Dict[str, Any],
        problem_statement: str,
    ) -> Optional[Dict[str, Any]]:
        """Aggregate exam score from submission_i scores scaled to each question max."""
        submission_scores = self._extract_submission_scores(result)
        if not submission_scores:
            return None

        question_max_scores = self._extract_question_max_scores(problem_statement)
        if not question_max_scores:
            return None

        count = min(len(submission_scores), len(question_max_scores))
        if count <= 0:
            return None

        details: List[Dict[str, Any]] = []
        total_score = 0.0
        total_max = 0.0

        for i in range(count):
            submission_name, score_on_10 = submission_scores[i]
            question_max = question_max_scores[i]
            scaled_score = round((score_on_10 / 10.0) * question_max, 4)

            details.append(
                {
                    "submission": submission_name,
                    "score_on_10": score_on_10,
                    "question_max": question_max,
                    "scaled_score": scaled_score,
                }
            )
            total_score += scaled_score
            total_max += question_max

        return {
            "method": "sum_scaled_by_question_max",
            "submission_count": len(submission_scores),
            "question_count": len(question_max_scores),
            "used_count": count,
            "details": details,
            "total_score": round(total_score, 4),
            "total_max": round(total_max, 4),
        }

    def _extract_submission_scores(self, result: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Extract per-submission 0-10 scores from keys like submission_1_* in LLM JSON."""
        items: List[Tuple[int, str, float]] = []

        for key, value in result.items():
            if not isinstance(value, dict):
                continue

            m = re.match(r"submission_(\d+)(?:_.*)?$", str(key))
            if not m:
                continue

            order = int(m.group(1))
            score = self._coerce_score_10(value.get("quality_score"))

            if score is None:
                breakdown, has_breakdown = self._normalize_score_breakdown(value.get("score_breakdown"))
                if has_breakdown:
                    score = self._sum_score_breakdown(breakdown)

            if score is None:
                score = self._coerce_score_10(value.get("final_score"))

            if score is not None:
                items.append((order, key, score))

        items.sort(key=lambda x: x[0])
        return [(name, score) for _, name, score in items]

    def _extract_question_max_scores(self, problem_statement: str) -> List[float]:
        """Extract question max points from headings like 'Câu 1. (3đ)' in order."""
        if not isinstance(problem_statement, str) or not problem_statement.strip():
            return []

        scores: List[float] = []
        lines = problem_statement.splitlines()
        heading_pattern = re.compile(
            r"^\s*(?:c\S*u|b\S*i)\s*\d+.*?\((\d+(?:[\.,]\d+)?)\s*đ\)",
            flags=re.IGNORECASE,
        )

        for line in lines:
            m = heading_pattern.search(line)
            if not m:
                continue
            raw = m.group(1).replace(",", ".")
            try:
                scores.append(float(raw))
            except ValueError:
                continue

        return scores

    def _infer_additive_breakdown_from_errors(self, errors: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
        """
        Fallback cho trường hợp model không trả đúng schema additive.
        Heuristic này giữ tinh thần cộng điểm thay vì mặc định về 0.
        """
        if errors is None:
            return None

        if not errors:
            return {
                "idea": 3.0,
                "flow": 2.0,
                "syntax_execution": 2.0,
                "correctness": 2.0,
                "clarity": 1.0,
            }

        # Mặc định cho bài có lỗi nhưng vẫn có ý tưởng cơ bản.
        breakdown = {
            "idea": 2.0,
            "flow": 1.5,
            "syntax_execution": 1.5,
            "correctness": 1.5,
            "clarity": 0.5,
        }

        for error in errors:
            error_type = str(error.get("type", "")).lower()
            error_desc = str(error.get("description", "")).lower()
            text = f"{error_type} {error_desc}"

            if "fatal" in text:
                breakdown["correctness"] = 0.0
                breakdown["syntax_execution"] = min(breakdown["syntax_execution"], 0.5)

            if "logic" in text or "major" in text:
                breakdown["correctness"] -= 1.0
                breakdown["flow"] -= 0.5
                breakdown["idea"] -= 0.5

            if "edge" in text or "boundary" in text:
                breakdown["correctness"] -= 0.5

            if "syntax" in text or "runtime" in text or "compile" in text:
                breakdown["syntax_execution"] -= 1.0

            if "style" in text or "efficiency" in text or "clarity" in text:
                breakdown["clarity"] -= 0.5

        for key, max_score in self.additive_rubric_max.items():
            breakdown[key] = max(0.0, min(max_score, round(breakdown[key], 4)))

        return breakdown

    def _flatten_errors(self, errors: Any) -> List[Dict[str, Any]]:
        """Flatten nested error payloads into a list of dicts that contain `type`."""
        flattened: List[Dict[str, Any]] = []

        def walk(node: Any, submission_name: Optional[str] = None) -> None:
            if isinstance(node, list):
                for item in node:
                    walk(item, submission_name)
                return

            if not isinstance(node, dict):
                return

            current_submission = node.get("submission_name") or submission_name
            error_type = node.get("type")

            if isinstance(error_type, str):
                item = dict(node)
                if current_submission and "submission_name" not in item:
                    item["submission_name"] = current_submission
                flattened.append(item)
                return

            # Common nested schema: {submission_name, errors: [...]}.
            nested_errors = node.get("errors")
            if isinstance(nested_errors, list):
                walk(nested_errors, current_submission)

            # Best-effort recursion for other nested list/dict fields.
            for key, value in node.items():
                if key == "errors":
                    continue
                if isinstance(value, (list, dict)):
                    walk(value, current_submission)

        walk(errors)
        return flattened

    def _has_typed_errors(self, errors: List[Dict[str, Any]]) -> bool:
        """Check whether we have at least one recognized taxonomy error type."""
        for error in errors:
            if error.get("type") in self.error_taxonomy:
                return True
        return False

    def _coerce_score_10(self, value: Any) -> Optional[float]:
        """Convert an arbitrary score into [0, 10] float if possible."""
        try:
            score = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(10.0, score))
    
    def _calculate_final_score(self, errors: List[Dict]) -> float:
        """
        Tính điểm cuối cùng dựa trên lỗi
        
        Công thức:
        Điểm = Max(0, 10 - Tổng_Điểm_Phạt)
        
        Mức phạt:
        - Negligible: 0 điểm
        - Small: -0.5 điểm
        - Major: -5 điểm
        - Fatal: -10 điểm
        """
        logger.debug("Calculating final score...")
        
        total_penalty = 0.0
        penalty_breakdown = {
            "Negligible": 0.0,
            "Small": 0.0,
            "Major": 0.0,
            "Fatal": 0.0
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
        
        # Công thức: Max(0, 10 - total_penalty)
        final_score = max(0.0, 10.0 + total_penalty)  # total_penalty đã là âm
        
        logger.debug(f"Total penalty: {total_penalty}, Final score: {final_score}")
        logger.debug(f"Breakdown: {penalty_breakdown}")
        
        return final_score
    
    def get_penalty_breakdown(self, final_score: float, total_penalty: float) -> Dict:
        """
        Chi tiết cách tính penalty
        """
        return {
            "base_score": 10.0,
            "total_penalty": total_penalty,
            "final_score": final_score,
            "formula": "Max(0, 10 - TotalPenalty)"
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
