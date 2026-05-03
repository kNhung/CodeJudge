"""
Prompt Templates cho System Prompting
Sử dụng cho Binary Assessment và Taxonomy-Guided Scoring
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SYSTEM PROMPTS - Định nghĩa vai trò và context cho LLM
# ============================================================================

SYSTEM_PROMPT_BINARY_ASSESSMENT = """Bạn là một chuyên gia đánh giá code chất lượng cao.

Nhiệm vụ của bạn là phân tích code của sinh viên từng bước theo yêu cầu đề bài.

QUAN TRỌNG:
- Chỉ phân tích, KHÔNG sửa code
- Chỉ kiểm tra xem code có đáp ứng yêu cầu cơ bản hay không
- Đầu ra cuối cùng PHẢI là "Yes" (code đạt) hoặc "No" (code không đạt)

Lưu ý: Chỉ trả lời "Yes" nếu logic cơ bản hoàn toàn đúng theo đề bài."""

SYSTEM_PROMPT_TAXONOMY_ASSESSMENT = """Bạn là giảng viên chấm code theo hướng khuyến khích: bắt đầu từ 0 và cộng điểm dần theo phần làm đúng.

MỤC TIÊU:
- Chấm công bằng cho bài làm sinh viên, ưu tiên ghi nhận phần đúng.
- Không dùng tư duy "cho 10 rồi trừ".
- Điểm cuối cùng nằm trong [0, 10].

RUBRIC CỘNG ĐIỂM (THANG 10):
1) Hiểu đề & ý tưởng giải bài (0-3 điểm)
- 0.0: Lệch đề hoàn toàn hoặc không có ý tưởng khả dụng
- 1.0: Có ý tưởng sơ khai nhưng chưa đúng trọng tâm
- 2.0: Ý tưởng đúng một phần, có thể giải được một số trường hợp
- 3.0: Ý tưởng đúng và bám sát yêu cầu chính của đề

2) Luồng xử lý & cấu trúc chương trình (0-2 điểm)
- 0.0: Luồng rời rạc, thiếu bước quan trọng
- 1.0: Luồng cơ bản có nhưng còn thiếu/chưa chặt chẽ
- 2.0: Luồng rõ ràng, thứ tự xử lý hợp lý

3) Cú pháp, khả năng chạy, dùng API/ngôn ngữ (0-2 điểm)
- 0.0: Lỗi cú pháp/runtime nghiêm trọng, khó chạy
- 1.0: Chạy được một phần hoặc còn lỗi nhỏ
- 2.0: Cú pháp ổn, có thể chạy đúng ở mức mong đợi

4) Tính đúng của kết quả (core cases + edge cases) (0-2 điểm)
- 0.0: Kết quả sai phần lớn
- 1.0: Đúng các case cơ bản nhưng hụt một số case biên
- 2.0: Kết quả đúng ổn định cho cả case cơ bản và biên quan trọng

5) Trình bày và độ rõ ràng (0-1 điểm)
- 0.0: Khó đọc, biến/hàm gây khó hiểu
- 0.5: Tạm đọc được nhưng còn rối
- 1.0: Dễ đọc, đặt tên hợp lý, thể hiện tư duy rõ

QUY TẮC CHẤM:
- Nếu có phần đúng thì phải cộng điểm cho phần đó.
- Không bắt sinh viên đạt chuẩn production mới được điểm.
- Không phạt nặng style/comment nếu không ảnh hưởng tính đúng.
- Khi chưa chắc, chọn mức điểm bảo toàn công sức của sinh viên.
- BẮT BUỘC: Top-level JSON phải là object, KHÔNG được là array/list.
- BẮT BUỘC: score_breakdown phải có đủ 5 khóa: idea, flow, syntax_execution, correctness, clarity.

ĐỊNH DẠNG OUTPUT (BẮT BUỘC JSON):
{
    "quality_score": 6.5,
    "score_breakdown": {
        "idea": 2.0,
        "flow": 1.5,
        "syntax_execution": 1.0,
        "correctness": 1.5,
        "clarity": 0.5
    },
    "strengths": [
        "Có ý tưởng đúng cho trường hợp cơ bản"
    ],
    "improvements": [
        "Thiếu xử lý một số edge case"
    ],
    "errors": [
        {
            "type": "Improvement",
            "description": "Mô tả ngắn gọn điểm cần cải thiện",
            "code_snippet": "đoạn liên quan",
            "fix_suggestion": "hướng cải thiện"
        }
    ],
    "reasoning": "Giải thích ngắn gọn cách cộng điểm theo từng mục"
}"""

# ============================================================================
# BINARY ASSESSMENT - Phân tích từng bước
# ============================================================================

BINARY_ASSESSMENT_ANALYZE_PROMPT = """Ngôn ngữ code: {language}

Đề bài: 
{problem_statement}

Code sinh viên:
```
{student_code}
```

Yêu cầu: Phân tích từng bước xem code này có:
1. ✓ Đạt yêu cầu cơ bản của đề bài không?
2. ✓ Logic chính có đúng không?
3. ✓ Xử lý input/output có chính xác không?
4. ✓ Không có lỗi cú pháp hay runtime không?

Hãy phân tích chi tiết, giải thích từng bước, nhưng KHÔNG sửa code.
Chỉ đưa ra nhận xét và điểm yếu (nếu có)."""

BINARY_ASSESSMENT_SUMMARIZE_PROMPT = """Dựa trên phân tích ở trên:

{analysis_result}

Hãy kết luận NGẮN GỌN:
- Nếu logic cơ bản HOÀN TOÀN ĐÚng theo đề bài → trả lời: Yes
- Nếu có lỗi hoặc sai logic → trả lời: No

Chỉ trả lời: "Yes" hoặc "No" (không thêm giải thích)"""

# ============================================================================
# TAXONOMY-GUIDED - Chấm điểm chi tiết
# ============================================================================

TAXONOMY_ASSESSMENT_PROMPT = """Ngôn ngữ code: {language}

Đề bài:
{problem_statement}

Code sinh viên:
```
{student_code}
```

{reference_code_section}

Hãy chấm theo rubric cộng điểm từ 0 đến 10:
- Bước 1: Chấm từng tiêu chí trong score_breakdown
- Bước 2: Cộng các mục để ra quality_score
- Bước 3: quality_score phải nằm trong [0, 10]
- Bước 4: Trả về top-level JSON object, không trả về list
- Bước 5: score_breakdown phải có đủ 5 trường rubric

Trả về JSON đúng định dạng yêu cầu."""

REFERENCE_CODE_TEMPLATE = """Code mẫu tham khảo (để giúp xác định lỗi):
```
{reference_code}
```"""

# ============================================================================
# UTILITY PROMPTS
# ============================================================================

ERROR_SUMMARY_PROMPT = """Dựa trên phân tích sau:

{errors_json}

Hãy tính toán điểm cuối cùng (0-10) theo hướng cộng điểm:
Điểm = idea + flow + syntax_execution + correctness + clarity
Sau đó chặn trong [0, 10].

Rubric:
- idea: 0-3
- flow: 0-2
- syntax_execution: 0-2
- correctness: 0-2
- clarity: 0-1

Trả về JSON:
{
  "final_score": <số điểm>,
    "score_breakdown": {
        "idea": <0-3>,
        "flow": <0-2>,
        "syntax_execution": <0-2>,
        "correctness": <0-2>,
        "clarity": <0-1>
    },
  "reasoning": "<giải thích>"
}"""

# ============================================================================
# PROMPT TEMPLATES - Để dễ custom
# ============================================================================

class PromptTemplates:
    """Các template prompt có thể tùy chỉnh"""
    
    # Binary Assessment
    BINARY_ANALYZE = BINARY_ASSESSMENT_ANALYZE_PROMPT
    BINARY_SUMMARIZE = BINARY_ASSESSMENT_SUMMARIZE_PROMPT
    
    # Taxonomy Assessment  
    TAXONOMY = TAXONOMY_ASSESSMENT_PROMPT
    REFERENCE_CODE = REFERENCE_CODE_TEMPLATE
    
    # Error Summary
    ERROR_SUMMARY = ERROR_SUMMARY_PROMPT
    
    @staticmethod
    def format_binary_analyze(
        problem_statement: str,
        student_code: str,
        language: str = "Python"
    ) -> str:
        """Format prompt phân tích (Step 1)"""
        return BINARY_ASSESSMENT_ANALYZE_PROMPT.format(
            language=language,
            problem_statement=problem_statement,
            student_code=student_code
        )
    
    @staticmethod
    def format_binary_summarize(analysis_result: str) -> str:
        """Format prompt tóm tắt (Step 2)"""
        return BINARY_ASSESSMENT_SUMMARIZE_PROMPT.format(
            analysis_result=analysis_result
        )
    
    @staticmethod
    def format_taxonomy(
        problem_statement: str, 
        student_code: str,
        reference_code: str = None,
        language: str = "Python"
    ) -> str:
        """Format prompt chấm điểm chi tiết"""
        reference_section = ""
        if reference_code:
            reference_section = REFERENCE_CODE_TEMPLATE.format(
                reference_code=reference_code
            )
        
        return TAXONOMY_ASSESSMENT_PROMPT.format(
            language=language,
            problem_statement=problem_statement,
            student_code=student_code,
            reference_code_section=reference_section
        )
    
    @staticmethod
    def format_error_summary(errors_json: str) -> str:
        """Format prompt tính toán điểm cuối"""
        return ERROR_SUMMARY_PROMPT.format(errors_json=errors_json)
    
    @staticmethod
    def format_taxonomy_with_examples(
        problem_statement: str,
        student_code: str,
        reference_code: str = None,
        language: str = "Python",
        include_examples: bool = True,
        num_examples: int = 3
    ) -> str:
        """
        Format prompt chấm điểm với ví dụ calibration (few-shot learning)
        
        Args:
            problem_statement: Đề bài
            student_code: Code sinh viên
            reference_code: Code mẫu (tùy chọn)
            language: Ngôn ngữ lập trình
            include_examples: Có thêm examples không?
            num_examples: Số lượng ví dụ (nên ≤ 3 để không quá dài)
        
        Returns:
            Prompt đầy đủ với examples
        """
        try:
            from .examples_library import format_examples_for_prompt
        except ImportError:
            logger.warning("Could not import examples_library, skipping examples")
            include_examples = False
        
        # Format base taxonomy prompt
        base_prompt = PromptTemplates.format_taxonomy(
            problem_statement=problem_statement,
            student_code=student_code,
            reference_code=reference_code,
            language=language
        )
        
        # Thêm examples nếu có
        if include_examples:
            try:
                # Tạo key từ problem statement (hash đơn giản)
                problem_key = "all_elements_same"  # Default
                
                examples_section = format_examples_for_prompt(
                    problem_key=problem_key,
                    num_examples=num_examples
                )
                
                base_prompt = examples_section + "\n" + base_prompt
                logger.debug(f"Added {num_examples} calibration examples to prompt")
            except Exception as e:
                logger.warning(f"Failed to add examples: {e}")
        
        return base_prompt


# ============================================================================
# ERROR TAXONOMY - Định nghĩa các cấp độ lỗi
# ============================================================================

ERROR_TAXONOMY = {
    "Negligible": {
        "description": "Code xấu, thiếu import, style sai",
        "penalty": 0,
        "examples": [
            "Thiếu type hints",
            "Sai whitespace/indentation",
            "Comments không rõ ràng",
            "Thiếu docstring"
        ]
    },
    "Small": {
        "description": "Thiếu xử lý biên, edge case",
        "penalty": -0.5,
        "examples": [
            "Không xử lý empty list",
            "Không check None values",
            "Thiếu boundary checks",
            "Không validate input"
        ]
    },
    "Major": {
        "description": "Sai logic thuật toán, công thức",
        "penalty": -5,
        "examples": [
            "Sort sai thứ tự",
            "Loop condition sai",
            "Math formula sai",
            "Logic control flow sai"
        ]
    },
    "Fatal": {
        "description": "Code chưa hoàn thành, hàm undefined",
        "penalty": -10,
        "examples": [
            "Gọi undefined function",
            "Return missing",
            "Syntax error (không compile)",
            "Logic chính chưa được implement"
        ]
    }
}
