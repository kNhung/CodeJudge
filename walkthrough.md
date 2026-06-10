# Walkthrough - Multi-Agent & Compiler-based Grading Flow

Chúng ta đã chuyển đổi thành công từ luồng chấm điểm cũ (sử dụng 1 prompt tích hợp) sang luồng mới sử dụng Trình biên dịch để bắt lỗi cú pháp kết hợp với Multi-Agent (Agent tách Factor và Agent chấm điểm theo Factor).

## Changes Made

### 1. Core Engine
- **[compiler_helper.py](file:///home/knhung/KLTN/CodeJudge/codejudge/core/compiler_helper.py) [NEW]**:
  - Hỗ trợ kiểm tra lỗi cú pháp thực tế cho C++ (sử dụng `g++ -fsyntax-only` chạy trên tệp tạm nằm trong workspace) và Python (sử dụng built-in `compile`).
  - Tự động chuẩn hóa, ẩn các đường dẫn tuyệt đối khỏi thông báo lỗi của trình biên dịch (thay thế bằng `student_code.cpp`).
- **[multi_agent_assessor.py](file:///home/knhung/KLTN/CodeJudge/codejudge/core/multi_agent_assessor.py) [NEW]**:
  - Triển khai lớp `MultiAgentAssessor` điều phối quy trình chấm điểm:
    1. **Agent 1 (Tách Factor)**: Trích xuất các yêu cầu logic/chức năng độc lập từ đề bài bằng LLM.
    2. **Agent 2 (Chấm điểm theo Factor)**: Dùng LLM chấm mức độ đáp ứng (từ 0.0 đến 1.0) cho từng Factor, yêu cầu LLM bỏ qua lỗi cú pháp.
    3. **Scoring Logic**: Điểm thành phần được quy đổi sang thang 10, trừ điểm phạt cú pháp (mỗi lỗi trừ 2.0 điểm, phạt tối đa 5.0 điểm), và tự động quy đổi tỉ lệ sang thang điểm tối đa của câu hỏi (`question_max`).
    4. **Suggestion Generation**: Tạo gợi ý cụ thể về logic (cho các factor đáp ứng < 100%) và cú pháp (từ output của compiler).
- **[__init__.py](file:///home/knhung/KLTN/CodeJudge/codejudge/core/__init__.py) [MODIFY]**:
  - Khai báo và export `MultiAgentAssessor` trong gói `codejudge.core`.

### 2. Evaluation Scripts
- **[score_with_multi_agent.py](file:///home/knhung/KLTN/CodeJudge/evaluation/hcmus/score_with_multi_agent.py) [NEW]**:
  - Script đánh giá hàng loạt cho dataset HCMUS sử dụng luồng mới.
  - Tách đề bài thành các câu bằng regex, tự động đối chiếu ghép cặp câu hỏi với file code tương ứng của sinh viên (ví dụ: Câu 1 tương ứng `bai01.cpp`).
  - Kết xuất JSONL chứa kết quả thành phần và báo cáo tổng hợp (exam summary) cho từng học sinh.

---

## Validation & Testing

### 1. Automated Tests
Chúng ta đã viết bộ test tự động tại `codejudge/tests/test_multi_agent.py` và chạy thành công trên môi trường conda:
```bash
conda run -n codejudge pytest codejudge/tests/test_multi_agent.py -v
```
**Kết quả test:**
```
codejudge/tests/test_multi_agent.py::TestCompilerHelper::test_python_syntax_valid PASSED
codejudge/tests/test_multi_agent.py::TestCompilerHelper::test_python_syntax_invalid PASSED
codejudge/tests/test_multi_agent.py::TestCompilerHelper::test_cpp_syntax_valid_mocked PASSED
codejudge/tests/test_multi_agent.py::TestCompilerHelper::test_cpp_syntax_invalid_mocked PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_clean_and_parse_json PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_extract_factors PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_assess_factors PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_calculate_score PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_generate_suggestions PASSED
codejudge/tests/test_multi_agent.py::TestMultiAgentAssessor::test_assess_end_to_end_mocked PASSED
======================= 10 passed in 12.08s ========================
```

---

### 2. Manual Verification (Live LLM Run)
Chạy thử nghiệm script trên dataset thực tế với model `gemini-2.5-flash`:
```bash
conda run -n codejudge 
python evaluation/hcmus/score_with_multi_agent.py --limit 1 --provider gemini --model gemini-2.5-flash
```

**Bảng phân tích kết quả chấm điểm thực tế:**

| Câu hỏi | Trạng thái biên dịch | Kết quả Factor trích xuất & Đánh giá | Điểm (Thang 10) | Điểm quy đổi | Suggestions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Câu 1** (Max 3đ) | Thành công (0 lỗi) | 1. Khởi tạo chồng đĩa: **1.0**<br>2. Thao tác rút đĩa: **0.3** (Lỗi logic hàm add)<br>3. In thứ tự đĩa: **0.0** (Gọi hàm sai size) | 4.33 | **1.3** | Gợi ý cải thiện logic chi tiết cho từng factor chưa đạt |
| **Câu 2** (Max 2đ) | Thành công (0 lỗi) | 1. Định nghĩa hàm: **1.0**<br>(Rate-limit fallback dùng điểm 10.0) | 10.0 | **2.0** | Không có (Hoàn thành tốt) |
| **Câu 3** (Max 5đ) | **Thất bại (18 lỗi)** | 1. Thực hiện đúng logic: **0.0** (Do lỗi compile) | 0.0 (Bị trừ 5đ) | **0.0** | Liệt kê chi tiết 18 lỗi cú pháp sạch của compiler |

**Báo cáo tổng hợp cuối cùng (Exam Summary):**
- **Kỳ thi:** `1_final`
- **Mã sinh viên:** `SV091214`
- **Điểm tổng dự đoán:** **`3.3 / 10.0đ`** (Câu 1: 1.3đ + Câu 2: 2.0đ + Câu 3: 0.0đ)
- **Gợi ý tổng hợp:** Gom toàn bộ gợi ý sửa lỗi logic của từng câu hỏi và hiển thị đầy đủ thông tin các lỗi cú pháp biên dịch cần sửa.
