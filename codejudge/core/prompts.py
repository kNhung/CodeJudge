"""
Prompt Templates cho System Prompting
Sử dụng cho Binary Assessment và Taxonomy-Guided Scoring
"""

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

SYSTEM_PROMPT_TAXONOMY_ASSESSMENT = """Bạn là một chuyên gia chấm điểm code với tiêu chuẩn rõ ràng.

Nhiệm vụ của bạn là:
1. Phân tích code sinh viên
2. Xác định lỗi (nếu có) theo 4 cấp độ sau:

ĐỊNH NGHĨA 4 CẤP ĐỘ LỖI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Cấp Độ     | Định Nghĩa                              | Mức Phạt | Ví Dụ                    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Negligible | Code xấu, thiếu import, style sai      | 0 điểm   | Thiếu comments, format  |
| Small      | Thiếu xử lý biên, edge case không đủ  | -0.5 điểm| Không xử lý empty input |
| Major      | Sai logic thuật toán, sai công thức    | -5 điểm  | Sai sort, sai condition |
| Fatal      | Code chưa viết xong, hàm không tồn tại| -10 điểm | Gọi undefined function  |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HƯỚNG DẪN CHẤM ĐIỂM:
• Không trừ điểm try-catch nếu đề bài không yêu cầu
• Cấp độ lỗi cao nhất = lỗi nghiêm trọng nhất trong code
• Nếu không có lỗi, trả về danh sách rỗng

ĐỊNH DẠNG OUTPUT (BẮTBUỘC JSON):
{
  "errors": [
    {
      "type": "Major",
      "description": "Mô tả lỗi chi tiết",
      "code_snippet": "đoạn code sai",
      "fix_suggestion": "gợi ý sửa"
    }
  ],
    "quality_score": 9.0,
  "reasoning": "Giải thích cách chấm"
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

Hãy chấm điểm code này theo tiêu chuẩn đã nêu, trả về JSON theo định dạng yêu cầu."""

REFERENCE_CODE_TEMPLATE = """Code mẫu tham khảo (để giúp xác định lỗi):
```
{reference_code}
```"""

# ============================================================================
# UTILITY PROMPTS
# ============================================================================

ERROR_SUMMARY_PROMPT = """Dựa trên danh sách lỗi sau:

{errors_json}

Hãy tính toán điểm cuối cùng (0-10) dựa trên công thức:
Điểm = Max(0, 10 - Tổng_Điểm_Phạt)

Với mức phạt:
- Negligible: 0 điểm
- Small: -0.5 điểm
- Major: -5 điểm
- Fatal: -10 điểm

Trả về JSON:
{
  "final_score": <số điểm>,
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
