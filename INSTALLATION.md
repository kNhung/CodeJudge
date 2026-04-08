# CodeJudge - Hướng Dẫn Cài Đặt và Sử Dụng

## 📦 Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.8+
- pip hoặc conda

### Bước 1: Cài Đặt Dependencies

```bash
# Cài đặt các thư viện cơ bản
pip install -r requirements.txt

# Hoặc cài từng cái
pip install openai anthropic requests python-dotenv
```

### Bước 2: Cấu Hình LLM Provider

Bạn cần chọn một trong ba LLM providers:

#### Option A: OpenAI (GPT-4)
```bash
# Tạo file .env
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

#### Option B: Anthropic (Claude)
```bash
# Tạo file .env
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

#### Option C: Local LLM (Ollama)
```bash
# 1. Cài đặt Ollama (https://ollama.ai)
# 2. Chạy local LLM
ollama run llama2

# 3. Cấu hình
echo "LOCAL_LLM_URL=http://localhost:11434" > .env
```

### Bước 3: Kiểm Tra Cài Đặt

```bash
python -c "import codejudge; print('CodeJudge installed successfully!')"
```

---

## 🚀 Sử Dụng

### Bài 1: Binary Assessment (Đạt/Không Đạt)

```python
from codejudge import BinaryAssessor

# Khởi tạo
assessor = BinaryAssessor()

# Đề bài và code
problem = """
Viết hàm tính tổng của danh sách số
Hàm sẽ nhận vào một list các số và trả về tổng
"""

student_code = """
def sum_list(numbers):
    return sum(numbers)
"""

# Chấm điểm
result = assessor.assess(problem, student_code)

# Kết quả
print(f"Result: {result['result']}")  # "Yes" or "No"
print(f"Passed: {result['passed']}")  # True or False
print(f"Confidence: {result['confidence']}")  # 0.0 - 1.0
```

**Output:**
```python
{
    'result': 'Yes',
    'passed': True,
    'confidence': 0.95,
    'analysis': '...',
    'summary': '...'
}
```

---

### Bài 2: Taxonomy Assessment (Chấm Điểm Chi Tiết)

```python
from codejudge import TaxonomyAssessor

# Khởi tạo
assessor = TaxonomyAssessor()

# Chấm điểm
result = assessor.assess(
    problem_statement=problem,
    student_code=student_code,
    reference_code=None  # Có thể thêm code mẫu
)

# Kết quả
print(f"Final Score: {result['final_score']}")  # 0-100
print(f"Errors: {result['errors']}")  # Danh sách lỗi
```

**Output:**
```python
{
    'errors': [
        {
            'type': 'Major',
            'description': 'Sai logic',
            'code_snippet': '...',
            'fix_suggestion': '...'
        }
    ],
    'quality_score': 90,
    'final_score': 50,
    'reasoning': '...'
}
```

---

### Bài 3: Integrated Assessment (Tích Hợp)

**Đây là cách tốt nhất - sử dụng cả hai luồng**

```python
from codejudge import IntegratedAssessor

# Khởi tạo
assessor = IntegratedAssessor(run_both_assessments=True)

# Chấm điểm
result = assessor.assess(
    problem_statement=problem,
    student_code=student_code,
    reference_code=None
)

# Kết quả tích hợp
print(f"Status: {result['summary']['status']}")  # PASS or FAIL
print(f"Score: {result['summary']['score']}")  # 0-100
print(f"Grade: {result['summary']['grade_letter']}")  # A-F
print(f"Recommendation: {result['summary']['recommendation']}")  # Tùy chỉnh
```

**Output:**
```python
{
    'assessment_type': 'integrated',
    'binary': {
        'result': 'Yes',
        'passed': True,
        'confidence': 0.95,
        'analysis': '...'
    },
    'taxonomy': {
        'final_score': 75,
        'errors_count': 2,
        'error_breakdown': {
            'Negligible': 1,
            'Small': 1,
            'Major': 0,
            'Fatal': 0
        },
        'errors': [...]
    },
    'summary': {
        'status': 'PASS',
        'score': 75,
        'grade_letter': 'C',
        'recommendation': 'Khá. Cần sửa các lỗi Major.'
    }
}
```

---

## 🎯 Advanced Usage

### 1. Thay Đổi LLM Provider

```python
from codejudge import LLMFactory, IntegratedAssessor

# Tạo client cho GPT-4
gpt4_client = LLMFactory.create("openai", model_name="gpt-4")

# Hoặc Claude
claude_client = LLMFactory.create("anthropic", model_name="claude-3-opus-20240229")

# Hoặc Local LLM
llama_client = LLMFactory.create(
    "local",
    model_name="llama2",
    base_url="http://localhost:11434"
)

# Sử dụng với assessor
assessor = IntegratedAssessor(llm_client=gpt4_client)
result = assessor.assess(problem, code)
```

### 2. Tùy Chỉnh System Prompt

```python
from codejudge import BinaryAssessor

assessor = BinaryAssessor()

custom_prompt = """
Bạn là giáo viên đánh giá code có kinh nghiệm.
Hãy phân tích code sinh viên...
"""

assessor.set_system_prompt(custom_prompt)
result = assessor.assess(problem, code)
```

### 3. Tùy Chỉnh Error Taxonomy

```python
from codejudge import TaxonomyAssessor

custom_taxonomy = {
    "Negligible": {
        "description": "...",
        "penalty": 0,
        "examples": [...]
    },
    # ... more error types
}

assessor = TaxonomyAssessor()
assessor.set_error_taxonomy(custom_taxonomy)
result = assessor.assess(problem, code)
```

### 4. Tính Điểm Hoàn Chỉnh

```python
from codejudge import Scorer, ScoreInterpreter, ResultFormatter

# Tính điểm từ danh sách lỗi
errors = [
    {"type": "Small", "description": "..."},
    {"type": "Major", "description": "..."}
]

scorer = Scorer(base_score=100)
scoring_result = scorer.calculate_score(errors)

# Giải thích điểm
score = scoring_result.final_score
grade = ScoreInterpreter.get_grade(score)
feedback = ScoreInterpreter.get_feedback(score)

# Format kết quả
full_result = ResultFormatter.format_full_result(scoring_result, errors)

# Báo cáo chi tiết
report = ResultFormatter.format_detailed_report(scoring_result, errors)
print(report)
```

---

## 📋 Ví Dụ Hoàn Chỉnh

```python
import json
from codejudge import IntegratedAssessor

# Định nghĩa bài tập
problem = """
Viết hàm tìm số lớn nhất trong danh sách
Input: danh sách số nguyên
Output: số lớn nhất

Ví dụ:
- find_max([1, 5, 3]) = 5
- find_max([-10, 0, -5]) = 0
"""

# Code của sinh viên
student_code = """
def find_max(numbers):
    if not numbers:
        return None
    
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    
    return max_val
"""

# Code mẫu (tùy chọn)
reference_code = """
def find_max(numbers):
    return max(numbers)
"""

# Chấm điểm
assessor = IntegratedAssessor()
result = assessor.assess(
    problem_statement=problem,
    student_code=student_code,
    reference_code=reference_code
)

# In kết quả
print(json.dumps(result, indent=2, ensure_ascii=False))

# Hoặc hiển thị tóm tắt
summary = result['summary']
print(f"\\n=== KẾT QUẢ CHẤM ĐIỂM ===")
print(f"Trạng thái: {summary['status']}")
print(f"Điểm: {summary['score']}/100")
print(f"Xếp hạng: {summary['grade_letter']}")
print(f"Nhận xét: {summary['recommendation']}")
```

---

## 🛠️ Debugging

### Xem Analysis Chi Tiết

```python
# Chỉ lấy kết quả phân tích (không kết luận Yes/No)
analysis = assessor.get_analysis_only(problem, code)
print(analysis)
```

### Xem LLM Response

```python
# Kích hoạt logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Sẽ in ra tất cả prompt và response
result = assessor.assess(problem, code)
```

### Kiểm Tra LLM Connection

```python
from codejudge import LLMFactory

# Tạo client
client = LLMFactory.create("openai")

# Test gọi
response = client.call(
    system_prompt="Bạn là trợ lý hữu ích",
    user_prompt="Tất cả bao nhiêu ngón tay?"
)

print(response)  # Nên in "10" hoặc tương tự
```

---

## 📊 Error Taxonomy

### 4 Cấp Độ Lỗi

| Cấp Độ | Định Nghĩa | Mức Phạt | Ví Dụ |
|--------|-----------|---------|-------|
| **Negligible** | Code xấu, style sai | 0 điểm | Thiếu comments, whitespace |
| **Small** | Thiếu edge case | -5 điểm | Không xử lý empty input |
| **Major** | Sai logic | -50 điểm | Sai sort, sai condition |
| **Fatal** | Chưa hoàn thành | -100 điểm | Undefined function |

### Công Thức Tính Điểm
```
Điểm = Max(0, 100 - Tổng_Điểm_Phạt)

Ví dụ:
- Không lỗi: 100 - 0 = 100 (A)
- 1 lỗi Small: 100 - 5 = 95 (A)
- 1 lỗi Major: 100 - 50 = 50 (F)
- 1 lỗi Fatal: 100 - 100 = 0 (F)
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **Độ Trễ (Latency)**:
   - Mỗi assessment mất ~10-20 giây (phụ thuộc LLM)
   - Dùng async/background job cho production

2. **Chi Phí API**:
   - OpenAI: ~0.01-0.05 USD per submission
   - Anthropic: ~0.002-0.01 USD per submission
   - Local LLM: Free nhưng cần GPU

3. **Prompt Engineering**:
   - Thêm code mẫu (reference_code) để chấm chính xác hơn
   - Đặc biệt quan trọng với bài khó (bài APPS)

4. **Tránh Lỗi Chấm Sai**:
   - Không trừ try-catch nếu đề không yêu cầu
   - Không trừ type hints nếu không bắt buộc

---

## 🚨 Troubleshooting

### Lỗi: "No LLM provider configured"
```python
# Fix: Tạo file .env và thêm một trong các API keys
echo "OPENAI_API_KEY=sk-..." > .env
```

### Lỗi: "Failed to import openai"
```bash
# Fix: Cài đặt openai package
pip install openai
```

### Lỗi: "JSON decode error"
```python
# Đôi khi LLM không trả về JSON chuẩn
# Solution: Bật DEBUG logging để xem response
import logging
logging.basicConfig(level=logging.DEBUG)
```

### LLM chấm chậm
```python
# Sử dụng local LLM nếu có GPU
client = LLMFactory.create("local", model_name="llama2")
```

---

## 📚 Các Dataset Để Test

Repo này cung cấp sẵn các dataset:

- **HumanEval-X**: Đơn giản, Python/Java/C++
- **BigCodeBench**: Vừa phải, production code
- **CoNaLa**: Code + Natural Language
- **APPS**: Khó, algorithmic challenges

Xem chi tiết ở `evaluation/` folder.

---

## 📖 Tài Liệu Thêm

- [ROADMAP.md](../ROADMAP.md) - Lộ trình development
- [Paper](../paper/) - Tài liệu gốc về CodeJudge
- [Giai đoạn 3: Testing](../codejudge/tests/) - Kiểm thử

---

## 💡 Tips & Tricks

1. **Tối ưu hóa Chi Phí**:
   - Dùng GPT-3.5-turbo thay GPT-4 cho bài đơn
   - Dùng local LLM cho bài dễ

2. **Cải Thiện Accuracy**:
   - Thêm code mẫu
   - Sử dụng few-shot prompting
   - Chain-of-thought reasoning

3. **Tăng Tốc Độ**:
   - Cache LLM responses
   - Parallel processing
   - Batch submission

---

## 📞 Hỗ Trợ

Các vấn đề? Kiểm tra:
1. Logs (bật DEBUG)
2. API key
3. Network connection
4. LLM provider status

---

Chúc bạn thành công! 🎉
