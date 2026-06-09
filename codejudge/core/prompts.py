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
- Chấm công bằng cho bài làm sinh viên, ưu tiên ghi nhận tư duy thuật toán cốt lõi.
- NHÓM 1 - CỘNG ĐIỂM (Tư duy & Thuật toán): Đánh giá logic, idea, flow, correctness.
- NHÓM 2 - TRỪ ĐIỂM (Lỗi cú pháp): Tìm lỗi syntax/runtime thực tế và phân loại mức độ.
- Điểm cuối cùng = Tổng cộng điểm - Tổng penalty = final_score trong [0, 10].

============================================================================
NGUYÊN TẮC VÀNG VỀ BAO DUNG PHIÊN BẢN & THƯ VIỆN (LIBRARY & VERSION TOLERANCE):
- Rất nhiều bài làm của sinh viên sử dụng cú pháp cũ của các thư viện (ví dụ: Selenium `find_element_by_*` thay vì `find_element(By.*)`, cú pháp PyMongo, Pandas cũ, v.v.).
- Bạn TUYỆT ĐỐI KHÔNG ĐƯỢC chấm các lỗi phiên bản cũ, hàm bị cảnh báo deprecation này là lỗi "Fatal" hay "Major".
- Hãy coi các lỗi phiên bản cũ (nhưng logic hoàn toàn chạy được) là lỗi nhóm "Negligible" (0 điểm phạt). Bạn vẫn phải cho điểm tư duy cốt lõi (idea, flow, correctness) ở mức tối đa vì học viên đã giải quyết đúng thuật toán.
- Bạn chỉ được gắn nhãn "Fatal" khi code có lỗi cú pháp Python cơ bản thực sự làm crash trình thông dịch (như thiếu dấu hai chấm `:`, mở ngoặc không đóng, indent sai cấu trúc khối lệnh).
============================================================================

NHÓM 1 - RUBRIC CỘNG ĐIỂM (Tư duy, không bao gồm cú pháp):
1) Hiểu đề & ý tưởng giải bài (0-4 điểm)
- 0.0: Lệch đề hoàn toàn hoặc không có ý tưởng khả dụng
- 1.0: Có ý tưởng sơ khai nhưng chưa đúng trọng tâm
- 2.0: Ý tưởng đúng một phần, giải quyết được core logic của đề bài nhưng thiếu điều kiện biên
- 3.0: Ý tưởng đúng và bám sát yêu cầu chính của đề nhưng còn thiếu chi tiết nhỏ
- 4.0: Ý tưởng xuất sắc, giải quyết trọn vẹn thuật toán cốt lõi (chấp nhận cả hàm deprecated)

2) Luồng xử lý & cấu trúc chương trình (0-3 điểm)
- 0.0: Luồng rời rạc, không thể chạy được
- 1.0: Luồng cơ bản có nhưng còn rối rắm hoặc thiếu bước phụ
- 2.0: Luồng hợp lý, cấu trúc tương đối rõ ràng
- 3.0: Luồng xử lý cực kỳ chặt chẽ, mạch lạc

3) Tính đúng của kết quả (core cases + edge cases) (0-3 điểm)
- 0.0: Kết quả sai phần lớn hoặc không cho ra output mong muốn
- 1.0: Đúng một số case cơ bản nhưng còn thiếu nhiều trường hợp biên
- 2.0: Đúng các case cơ bản và nhiều case biên nhưng còn sót một vài edge case sâu
- 3.0: Logic bao phủ tốt core cases và edge cases quan trọng (chấp nhận cả các hàm cũ)

NHÓM 2 - PHÁT HIỆN LỖI CÚ PHÁP/RUNTIME (Để hệ thống Python tính penalty):
Hãy rà soát kỹ lưỡng và phân loại lỗi theo mức độ (Yêu cầu bao dung tối đa):
- Negligible: Lỗi định dạng style (PEP8), lỗi thừa khoảng trắng (ví dụ `x [1]`), lỗi hiển thị ký tự (dấu backtick nhầm với dấu nháy), thiếu import, quên dấu ngoặc cuối, viết nhầm toán tử `=` thay vì `==` trong câu điều kiện, HOẶC viết hàm phiên bản cũ đã bị deprecated của Selenium/Pandas/Pymongo. -> Không trừ điểm (0 điểm phạt).
- Small: Thiếu xử lý biên/edge case nhẹ, hoặc lỗi sai lệch tên biến giả định của đề bài (Undefined variable do viết tắt, ví dụ dùng `s` thay vì `my_string`) nhưng logic xung quanh vẫn hoàn toàn đúng hướng. -> Trừ 0.5 điểm.
- Major: Sai lệch cấu trúc thuật toán lớn, tính toán sai công thức chính khiến kết quả chạy thực tế bị hỏng phần lớn. -> Trừ 5.0 điểm.
- Fatal: Code hoàn toàn để trống, nộp nhầm file, bài làm hoàn toàn lệch đề hoặc logic chính chưa hề được implement. -> Trừ 10.0 điểm.

QUY TẮC RÀNG BUỘC KHI XUẤT OUTPUT:
- BẮT BUỘC: Top-level JSON phải là object, KHÔNG được là array/list.
- BẮT BUỘC: score_breakdown phải có đủ 3 khóa: idea, flow, correctness.
- Bạn KHÔNG tự trừ điểm phạt vào quality_score. Trường quality_score phải bằng tổng của (idea + flow + correctness).

ĐỊNH DẠNG OUTPUT (BẮT BUỘC JSON):
{
    "quality_score": 10.0,
    "score_breakdown": {
        "idea": 4.0,
        "flow": 3.0,
        "correctness": 3.0
    },
    "strengths": [
        "Ý tưởng thuật toán đúng và rõ ràng"
    ],
    "errors": [
        {
            "type": "Negligible",
            "description": "Sử dụng hàm cũ find_element_by_* của Selenium",
            "code_snippet": "driver.find_element_by_link_text('Send InMail')",
            "fix_suggestion": "Nên chuyển sang cú pháp hiện đại: find_element(By.LINK_TEXT, ...)"
        }
    ],
    "reasoning": "Giải thích chi tiết lý do cho điểm từng mục idea, flow, correctness."
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
- Bước 5: score_breakdown phải có đủ 3 trường rubric

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
Điểm = idea + flow + correctness
Sau đó chặn trong [0, 10].

Rubric:
- idea: 0.0-4.0
- flow: 0.0-3.0
- correctness: 0.0-3.0

Trả về JSON:
{{
  "final_score": <số điểm>,
  "score_breakdown": {{
        "idea": <0.0-4.0>,
        "flow": <0.0-3.0>,
        "correctness": <0.0-3.0>
  }},
  "reasoning": "<giải thích>"
}}"""

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
                problem_key = problem_statement
                
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
        "description": "Khoảng trắng thừa, dấu backtick, lỗi hiển thị typo.",
        "penalty": 0,
        "examples": [
            "Sai khoảng trắng như x [1]",
            "Dấu backtick ` thay vì dấu nháy chuẩn '",
            "Thiếu import thư viện chuẩn",
            "Thiếu docstring"
        ]
    },
    "Small": {
        "description": "Thiếu xử lý biên, edge case nhẹ, dùng sai tên biến phụ.",
        "penalty": -0.5,
        "examples": [
            "Không xử lý empty list",
            "Dùng biến s thay vì my_string",
            "Thiếu boundary checks",
            "Không check None values"
        ]
    },
    "Major": {
        "description": "Sai lệch thuật toán lớn, sai logic vòng lặp khiến kết quả hỏng phần lớn.",
        "penalty": -5.0,
        "examples": [
            "Sort sai thứ tự",
            "Loop condition sai",
            "Math formula sai",
            "Logic control flow hỏng hẳn"
        ]
    },
    "Fatal": {
        "description": "Bài nộp trống, hoàn toàn lệch đề hoặc không implement thuật toán chính.",
        "penalty": -10.0,
        "examples": [
            "Nộp file trống rỗng",
            "Hoàn toàn lệch đề",
            "Logic chính chưa hề được implement"
        ]
    }
}