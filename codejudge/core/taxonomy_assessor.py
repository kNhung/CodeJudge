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
        error_taxonomy: Dict = None,
        use_examples: bool = False,
        num_examples: int = 2
    ):
        """
        Khởi tạo Taxonomy Assessor
        
        Args:
            llm_client: LLM client instance
            system_prompt: Custom system prompt
            error_taxonomy: Custom error taxonomy (nếu None, dùng default)
            use_examples: Sử dụng calibration examples (few-shot learning)?
            num_examples: Số lượng ví dụ (nên ≤ 3 để không quá dài)
        """
        self.llm_client = llm_client or LLMFactory.create()
        self.system_prompt = system_prompt
        self.error_taxonomy = error_taxonomy or ERROR_TAXONOMY
        self.use_examples = use_examples
        self.num_examples = num_examples
        # NHÓM 1: Cộng điểm (Tư duy, không bao gồm cú pháp)
        self.additive_rubric_max = {
            "idea": 4.0,
            "flow": 3.0,
            "correctness": 3.0,
        }
        self.additive_rubric_keys = [
            "idea",
            "flow",
            "correctness",
        ]
        
        # NHÓM 2: Trừ điểm (Dựa trên lỗi phát hiện)
        self.penalty_map = {
            "Negligible": 0.0,    # Không trừ
            "Small": -0.5,        # Lỗi logic bộ phận
            "Major": -5.0,        # Lỗi logic phần lớn
            "Fatal": -10.0,       # Lỗi cú pháp/crash
        }
    
    def assess(
        self,
        problem_statement: str,
        student_code: str,
        reference_code: Optional[str] = None,
        language: str = "Python"
    ) -> Dict[str, Any]:
        logger.info("=== Taxonomy Assessment ===")
        
        if self.use_examples:
            user_prompt = PromptTemplates.format_taxonomy_with_examples(
                problem_statement=problem_statement,
                student_code=student_code,
                reference_code=reference_code,
                language=language,
                include_examples=True,
                num_examples=self.num_examples
            )
        else:
            user_prompt = PromptTemplates.format_taxonomy(
                problem_statement=problem_statement,
                student_code=student_code,
                reference_code=reference_code,
                language=language,
            )
        
        llm_response = self.llm_client.call(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            format_json=True
        )
        
        result = self._parse_llm_response(llm_response)

        # 1. Đưa toàn bộ cấu trúc lỗi về dạng phẳng sớm để xử lý
        flat_errors = self._flatten_errors(result.get("errors", []))
        if not flat_errors and isinstance(result.get("taxonomy"), dict):
            flat_errors = self._flatten_errors(result["taxonomy"].get("errors", []))
        
        # 2. THỰC HIỆN HẠ CẤP BẢO DUNG LỖI VẶT NGAY TẠI ĐÂY
        flat_errors = self._reclassify_trivial_errors(flat_errors)
        result["errors"] = flat_errors
        
        # 3. Trích xuất và chuẩn hóa score_breakdown
        # Kiểm tra cả trong trường hợp LLM lồng cụm này vào trong object "taxonomy"
        llm_breakdown = result.get("score_breakdown")
        if not llm_breakdown and isinstance(result.get("taxonomy"), dict):
            llm_breakdown = result["taxonomy"].get("score_breakdown")
            
        score_breakdown, has_breakdown = self._normalize_score_breakdown(llm_breakdown)
        result["score_breakdown"] = score_breakdown

        # 4. TÍNH TOÁN ĐIỂM SỐ DỰA TRÊN KẾT QUẢ ĐÃ LÀM SẠCH
        if has_breakdown:
            base_score = self._sum_score_breakdown(score_breakdown)
            
            # Tính toán tổng điểm phạt sau khi đã loại bỏ lỗi định dạng vặt
            total_penalty = 0.0
            for err in flat_errors:
                err_type = err.get("type", "Negligible")
                if err_type in self.penalty_map:
                    total_penalty += self.penalty_map[err_type]
                elif err_type in self.error_taxonomy:
                    total_penalty += self.error_taxonomy[err_type].get("penalty", 0.0)
            
            # Điểm cuối cùng bằng điểm thuật toán cơ sở trừ đi penalty (chặn dưới bằng 0)
            final_score = round(max(0.0, base_score + total_penalty), 4)
            
            result["quality_score"] = base_score
            result["total_penalty"] = total_penalty
        else:
            # Luồng Fallback phòng khi LLM không trả về breakdown đúng chuẩn
            fallback_score = self._coerce_score_10(result.get("quality_score"))
            if fallback_score is not None:
                final_score = fallback_score
            else:
                inferred_breakdown = self._infer_additive_breakdown_from_errors(flat_errors)
                if inferred_breakdown is not None:
                    result["score_breakdown"] = inferred_breakdown
                    final_score = self._sum_score_breakdown(inferred_breakdown)
                else:
                    final_score = 0.0

        # Tích hợp xử lý điểm thi nếu có câu hỏi lớn
        exam_aggregation = self._aggregate_exam_score(result, problem_statement)
        if exam_aggregation is not None:
            final_score = exam_aggregation["total_score"]
            result["exam_aggregation"] = exam_aggregation

        result["final_score"] = final_score
        logger.info(f"Final Score: {final_score}")
        
        return result
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response từ LLM (Đã nâng cấp cơ chế tự vá lỗi truncated JSON)
        """
        logger.debug("Parsing LLM response...")
        
        if not response or not isinstance(response, str):
            return {
                "errors": [{"type": "Major", "description": "LLM response rỗng hoặc sai định dạng chuỗi.", "code_snippet": ""}],
                "quality_score": 0.0,
                "score_breakdown": {"idea": 0.0, "flow": 0.0, "correctness": 0.0},
                "reasoning": "LLM returned empty or invalid string."
            }

        # ==========================================
        # BƯỚC KHỬ ĐỘT BIẾN: VÁ CHUỖI JSON BỊ CẮT CỤM (TRUNCATED)
        # ==========================================
        stripped_resp = response.strip()
        
        # Nếu chuỗi có dấu hiệu bị cắt cụm do hết token (chứa dấu mở nhưng không có dấu đóng ngoặc ở cuối)
        if (
            ("{" in stripped_resp and not stripped_resp.endswith("}")) or 
            ("score_breakdown" in stripped_resp and not stripped_resp.endswith("}"))
        ):
            logger.warning("⚠️ Phát hiện chuỗi JSON từ LLM bị cắt cụm (Truncated). Tiến hành vá cấu trúc...")
            
            # 1. Dọn dẹp các ký tự lửng lơ ở cuối chuỗi bị cắt
            if stripped_resp.endswith(",") or stripped_resp.endswith(":") or stripped_resp.endswith('"'):
                stripped_resp = stripped_resp.rstrip(',:" ')
            
            # 2. Đếm và tự động bù ngoặc vuông `]` cho mảng "errors" hoặc "strengths" bị hở
            open_brackets = stripped_resp.count("[")
            close_brackets = stripped_resp.count("]")
            if open_brackets > close_brackets:
                # Nếu phần tử cuối cùng trong list chưa được đóng ngoặc nhọn, đóng nó trước
                if stripped_resp.strip().endswith("{") or stripped_resp.strip().endswith('"') or re.search(r'"[^"]+$', stripped_resp):
                    open_braces_in_list = stripped_resp.split("[")[-1].count("{")
                    close_braces_in_list = stripped_resp.split("[")[-1].count("}")
                    if open_braces_in_list > close_braces_in_list:
                        stripped_resp += "}"
                stripped_resp += "]"
            
            # 3. Đếm và tự động bù ngoặc nhọn `}` cho Object cha
            open_braces = stripped_resp.count("{")
            close_braces = stripped_resp.count("}")
            if open_braces > close_braces:
                stripped_resp += "}" * (open_braces - close_braces)
                
            response = stripped_resp

        # ==========================================
        # TIẾN HÀNH PARSE JSON
        # ==========================================
        try:
            # Thử parse JSON trực tiếp sau khi đã vá chuỗi
            data = json.loads(response)

            # Đồng bộ hóa list response về dạng dict như cũ (Hỗ trợ Gemini/Smaler models)
            if isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    data = {
                        "errors": data,
                        "quality_score": None,
                        "reasoning": "Parsed from list response"
                    }
                else:
                    logger.warning("JSON list response is not list[dict]. Using fallback schema")
                    data = {"errors": [], "quality_score": None, "reasoning": "LLM returned non-dict list response"}

            if not isinstance(data, dict):
                logger.warning(f"Unexpected JSON type: {type(data).__name__}. Using fallback schema")
                data = {"errors": [], "quality_score": None, "reasoning": f"LLM returned unsupported JSON type: {type(data).__name__}"}
            
            # Validate các trường cấu trúc bắt buộc
            if "errors" not in data: data["errors"] = []
            if "quality_score" not in data: data["quality_score"] = None
            if "score_breakdown" not in data: data["score_breakdown"] = {}
            if "reasoning" not in data: data["reasoning"] = ""
            
            return data
        
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON directly. Trying extraction from markdown/code blocks...")

            extracted = None
            # Thử trích xuất JSON từ markdown code block ```json ... ```
            code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, flags=re.S | re.I)
            if code_block_match:
                extracted = code_block_match.group(1).strip()
            else:
                # Fallback: tìm khối JSON cân bằng đầu tiên trong chuỗi
                start = response.find("{")
                if start != -1:
                    brace_level = 0
                    for i, ch in enumerate(response[start:], start):
                        if ch == "{":
                            brace_level += 1
                        elif ch == "}":
                            brace_level -= 1
                            if brace_level == 0:
                                extracted = response[start:i + 1].strip()
                                break

            if extracted:
                try:
                    data = json.loads(extracted)
                except json.JSONDecodeError:
                    extracted = None

            if extracted is None:
                logger.error("Unable to recover valid JSON from LLM response. Returning safe fallback.")
                return {
                    "errors": [{
                        "type": "Major",
                        "description": "LLM returned invalid or truncated JSON that could not be parsed.",
                        "code_snippet": response[:512]
                    }],
                    "quality_score": 0.0,
                    "score_breakdown": {"idea": 0.0, "flow": 0.0, "correctness": 0.0},
                    "reasoning": "Failed to parse or recover JSON from LLM response."
                }

            if isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    data = {
                        "errors": data,
                        "quality_score": None,
                        "reasoning": "Parsed from list response"
                    }
                else:
                    logger.warning("JSON list response is not list[dict]. Using fallback schema")
                    data = {"errors": [], "quality_score": None, "reasoning": "LLM returned non-dict list response"}

            if not isinstance(data, dict):
                logger.warning(f"Unexpected JSON type: {type(data).__name__}. Using fallback schema")
                data = {"errors": [], "quality_score": None, "reasoning": f"LLM returned unsupported JSON type: {type(data).__name__}"}

            if "errors" not in data: data["errors"] = []
            if "quality_score" not in data: data["quality_score"] = None
            if "score_breakdown" not in data: data["score_breakdown"] = {}
            if "reasoning" not in data: data["reasoning"] = ""
            return data

    def _normalize_score_breakdown(self, score_breakdown: Any) -> Tuple[Dict[str, float], bool]:
        """Normalize additive score breakdown into rubric keys and bounds."""
        normalized = {key: 0.0 for key in self.additive_rubric_keys}
        if not isinstance(score_breakdown, dict):
            return normalized, False

        # Chỉ xem breakdown là hợp lệ khi có đủ 3 tiêu chí additive.
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
                "idea": 4.0,
                "flow": 3.0,
                "correctness": 3.0,
            }

        # Mặc định cho bài có lỗi nhưng vẫn có ý tưởng cơ bản.
        breakdown = {
            "idea": 3.0,
            "flow": 2.0,
            "correctness": 2.0,
        }

        for error in errors:
            error_type = str(error.get("type", "")).lower()
            error_desc = str(error.get("description", "")).lower()
            text = f"{error_type} {error_desc}"

            if "fatal" in text:
                breakdown["correctness"] = 0.0

            if "logic" in text or "major" in text:
                breakdown["correctness"] -= 1.0
                breakdown["flow"] -= 0.5
                breakdown["idea"] -= 0.5

            if "edge" in text or "boundary" in text:
                breakdown["correctness"] -= 0.5

            if "syntax" in text or "runtime" in text or "compile" in text:
                breakdown["correctness"] -= 1.0

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
    def _reclassify_trivial_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reclassify các lỗi nhỏ từ "Fatal" thành "Small" hoặc "Negligible".
        """
        reclassified = []
        
        for error in errors:
            err_type = error.get("type", "Negligible")
            description = (error.get("description") or "").lower()
            code_snippet = (error.get("code_snippet") or "").lower()
            full_text = f"{description} {code_snippet}"
            
            # --- PATTERN 1: Lỗi toán tử so sánh vs toán tử gán (=, = =, == =) ---
            is_assignment_typo = (
                "= =" in full_text or 
                "sử dụng = thay vì ==" in description or
                "toán tử gán" in description or
                ("comparison" in description and "assignment" in description)
            )
            if err_type == "Fatal" and (is_assignment_typo or re.search(r"\b(if|while|elif|for)\b[\s\S]*?=\s*[^=]", code_snippet)):
                error_copy = dict(error)
                error_copy["type"] = "Negligible"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Trivial syntax issue: assignment operator used instead of comparison"
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Đã hạ cấp lỗi gán '=' nhầm thành '==': {description[:100]}...")
                continue
            
            # --- PATTERN 2: Dấu Backtick "`" thay vì dấu nháy chuỗi ---
            if err_type == "Fatal" and ("`" in full_text or any(kw in description for kw in ["backtick", "dấu nháy", "quote"])):
                error_copy = dict(error)
                error_copy["type"] = "Negligible"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Trivial syntax issue: backtick used instead of string quote"
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Đã hạ cấp lỗi dấu backtick ` thành lỗi không trừ điểm.")
                continue
            
            # --- PATTERN 3: Lỗi báo biến / Tên biến không khớp (NameError / Mismatch) ---
            is_variable_error = any(kw in description for kw in [
                "variable", "biến", "declare", "khai báo", "undefined", "undeclared", 
                "not defined", "nameerror", "báo biến", "chưa định nghĩa",
                "thay", "đổi thành"
            ])
            if err_type == "Fatal" and is_variable_error:
                error_copy = dict(error)
                error_copy["type"] = "Small"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Downgraded variable name mismatch/undefined to Small penalty"
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Hạ cấp lỗi sai tên biến từ Fatal xuống Small: {description[:100]}...")
                continue

            # --- PATTERN 4: Bỏ qua lỗi khoảng trắng trong Regex/Token/Lambda ---
            has_spacing_issue = (
                "khoảng trắng" in description or "space" in description or "whitespace" in description or
                re.search(r"\w+\s+\[\s*\d+\s*\]", code_snippet) or
                ("lambda" in full_text and ("[" in code_snippet or "]" in code_snippet)) or
                any(pattern in code_snippet.replace(" ", "") for pattern in ["(?=", "\\b", "\\d", "\\w"])
            )
            
            if err_type == "Fatal" and has_spacing_issue:
                error_copy = dict(error)
                error_copy["type"] = "Negligible"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Ignored whitespace fragmentation."
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Xóa bỏ hình phạt khoảng trắng: {code_snippet.strip()}")
                continue

            # --- PATTERN 5: Cứu các cấu trúc Generator Expression / Dict Comprehension hợp lệ ---
            is_generator_syntax = (
                ("dict(" in code_snippet and "for" in code_snippet) or
                "comprehension" in description
            )
            if err_type == "Fatal" and is_generator_syntax:
                error_copy = dict(error)
                error_copy["type"] = "Negligible"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Valid Python generator expression/comprehension incorrectly flagged as Fatal."
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Khôi phục cấu trúc generator hợp lệ: {code_snippet.strip()}")
                continue

            # --- PATTERN 6: Chuyển đổi lỗi Runtime/ValueError về đúng bản chất ---
            is_runtime_value_error = (
                "valueerror" in description or "invalid literal" in description or
                ("int(" in code_snippet and any(kw in description for kw in ["ép kiểu", "chuyển đổi", "tham số", "base"]))
            )
            if err_type == "Fatal" and is_runtime_value_error:
                error_copy = dict(error)
                error_copy["type"] = "Small"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Downgraded runtime ValueError to Small."
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Hạ cấp lỗi ép kiểu Runtime về lỗi Small.")
                continue

            # --- PATTERN 7: Cứu các hàm lồng ghép Built-in như list(map(...)) ---
            is_nested_builtin = any(kw in code_snippet for kw in ["map(int", "list(map", "join(map"])
            if err_type == "Fatal" and is_nested_builtin:
                error_copy = dict(error)
                error_copy["type"] = "Small"
                error_copy["original_type"] = "Fatal"
                error_copy["ignored_reason"] = "Nested built-in function expressions are syntax-valid. Downgraded to Small."
                reclassified.append(error_copy)
                logger.info(f"⚡ [Bao dung] Cứu hàm lồng nhau hợp lệ: {code_snippet.strip()}")
                continue

            # Giữ nguyên nếu không khớp
            reclassified.append(error)
        
        return reclassified
        
    def _coerce_score_10(self, value: Any) -> Optional[float]:
        """Convert an arbitrary score into [0, 10] float if possible."""
        try:
            score = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(10.0, score))
    
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
