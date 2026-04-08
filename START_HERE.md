# 🎯 START HERE - Bắt Đầu CodeJudge

> Hướng dẫn chi báo bắt đầu sử dụng CodeJudge trong 5 phút

---

## ⚡ Ngay Lập Tức (5 phút)

### 1. Cài Dependencies

```bash
# Windows / Mac / Linux
pip install -r requirements-codejudge.txt
```

### 2. Cấu Hình LLM

Chọn **một** trong ba:

#### Option A: OpenAI (Khuyến Nghị)
```bash
# 1. Lấy API key từ https://platform.openai.com/api-keys

# 2. Tạo .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Test
python -c "from codejudge import LLMFactory; print('✓ OK')"
```

#### Option B: Claude (Anthropic)
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

#### Option C: Local LLM (Miễn Phí)
```bash
# 1. Cài Ollama: https://ollama.ai
# 2. Chạy: ollama run llama2
# 3. Tạo .env:
echo "LOCAL_LLM_URL=http://localhost:11434" > .env
```

### 3. Chạy Ví Dụ Đầu Tiên

```python
from codejudge import IntegratedAssessor

# Khởi tạo
assessor = IntegratedAssessor()

# Đề bài
problem = "Viết hàm tính tổng danh sách"

# Code sinh viên
code = """
def sum_list(numbers):
    return sum(numbers)
"""

# Chấm điểm
result = assessor.assess(problem, code)

# Kết quả
print(f"Status: {result['summary']['status']}")      # PASS
print(f"Score: {result['summary']['score']}/100")    # 100
print(f"Grade: {result['summary']['grade_letter']}")  # A
```

**Xong! Bạn đã có thể chấm code**

---

## 📚 Tiếp Theo (15 phút)

### Hiểu 3 Loại Assessor

#### 1. Binary Assessor - Yes/No

```python
from codejudge import BinaryAssessor

assessor = BinaryAssessor()

# "Code có đạt yêu cầu cơ bản không?"
result = assessor.assess(problem, code)

# result['result'] = "Yes" hoặc "No"
```

**Sử dụng khi**: Chỉ cần biết code có chạy đúng không

---

#### 2. Taxonomy Assessor - Điểm Chi Tiết

```python
from codejudge import TaxonomyAssessor

assessor = TaxonomyAssessor()

# "Code có lỗi gì? Trừ bao nhiêu điểm?"
result = assessor.assess(problem, code, reference_code=None)

# result['final_score'] = 0-100
# result['errors'] = [...]
```

**Sử dụng khi**: Cần điểm chi tiết và danh sách lỗi

---

#### 3. Integrated Assessor - Cả Hai ⭐ (Khuyến Nghị)

```python
from codejudge import IntegratedAssessor

assessor = IntegratedAssessor(run_both_assessments=True)

# Chạy cả Binary và Taxonomy
result = assessor.assess(problem, code, reference_code=None)

# Kết hợp:
# result['binary'] = {result, passed, confidence}
# result['taxonomy'] = {final_score, errors}
# result['summary'] = {status, score, grade, recommendation}
```

**Sử dụng khi**: Muốn đánh giá toàn diện (khuyến nghị)

---

### 4 Cấp Độ Lỗi

| Mức | Mô Tả | Trừ | Ví Dụ |
|-----|-------|-----|-------|
| 🟢 **Negligible** | Style xấu | 0 | Missing comments |
| 🟡 **Small** | Thiếu edge case | -5 | Không xử lý empty |
| 🔴 **Major** | Sai logic | -50 | Sai sort |
| ⚫ **Fatal** | Chưa xong | -100 | Undefined function |

**Công Thức**: `Điểm = Max(0, 100 - Tổng_Phạt)`

Ví dụ:
- Không lỗi: 100 - 0 = **100** (A)
- 1 lỗi Small: 100 - 5 = **95** (A)
- 1 lỗi Major: 100 - 50 = **50** (F)

---

### Grades

| Grade | Điểm | Mô Tả |
|-------|------|-------|
| **A** | 90-100 | Xuất sắc ⭐ |
| **B** | 80-89 | Tốt |
| **C** | 70-79 | Khá |
| **D** | 60-69 | Đủ |
| **F** | 0-59 | Không đạt |

---

## 🔧 Tùy Chỉnh (20 phút)

### 1. Thay Đổi LLM Model

```python
from codejudge import LLMFactory, IntegratedAssessor

# Tạo client
client = LLMFactory.create("openai", model_name="gpt-4")

# Hoặc GPT-3.5-turbo (rẻ hơn)
client = LLMFactory.create("openai", model_name="gpt-3.5-turbo")

# Hoặc Claude
client = LLMFactory.create("anthropic", model_name="claude-3-opus-20240229")

# Dùng với assessor
assessor = IntegratedAssessor(llm_client=client)
result = assessor.assess(problem, code)
```

### 2. Thêm Reference Code

Code mẫu giúp chấm chính xác hơn:

```python
reference_code = """
def sum_list(numbers):
    return sum(numbers)
"""

result = assessor.assess(
    problem_statement=problem,
    student_code=code,
    reference_code=reference_code  # ← Thêm này
)

# Kết quả sẽ chính xác hơn!
```

### 3. Custom Prompt

```python
from codejudge import BinaryAssessor

assessor = BinaryAssessor()

custom_prompt = """
Bạn là giáo viên đánh giá code Python chuyên sâu.
Hãy phân tích code sinh viên...
"""

assessor.set_system_prompt(custom_prompt)
result = assessor.assess(problem, code)
```

### 4. Debug & Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Bây giờ sẽ thấy tất cả prompts và responses
result = assessor.assess(problem, code)
```

---

## 🧪 Test Hệ Thống (30 phút)

### Chạy Unit Tests

```bash
# Cài pytest
pip install pytest pytest-cov

# Chạy
pytest codejudge/tests/ -v

# Coverage
pytest codejudge/tests/ --cov=codejudge
```

### 5 Ví Dụ Sẵn

```bash
python examples.py
```

Sẽ chạy:
1. Binary Assessment
2. Taxonomy Assessment
3. Integrated Assessment
4. Custom LLM Provider
5. Scoring & Interpretation

---

## 📁 Cấu Trúc Thư Mục

```
CodeJudge/
├── codejudge/
│   ├── core/              ← Chấm điểm
│   ├── scoring/           ← Tính điểm
│   └── tests/             ← Unit tests
│
├── examples.py            ← 5 ví dụ
├── INSTALLATION.md        ← Chi tiết setup
├── ROADMAP.md             ← Lộ trình 4 giai đoạn
└── README_CODEJUDGE.md    ← Tài liệu đầy đủ
```

---

## 📖 Tài Liệu

| File | Mục Đích |
|------|----------|
| `START_HERE.md` | Bạn đang đọc 👈 |
| `INSTALLATION.md` | Setup chi tiết |
| `README_CODEJUDGE.md` | API & features |
| `ROADMAP.md` | 4 giai đoạn phát triển |
| `examples.py` | 5 ví dụ chạy được |

---

## ❓ Yêu Cầu & Giải Quyết

### Q: Tôi không có API key?
**A**: Dùng Local LLM (Ollama, free) hoặc dùng trial key

### Q: Code chấm chậm?
**A**: Dùng GPT-3.5-turbo (nhanh hơn) hoặc local LLM

### Q: Độ chính xác thấp?
**A**: Thêm reference code, bật few-shot prompting

### Q: Test trên đâu?
**A**: `pytest codejudge/tests/` hoặc chạy `examples.py`

### Q: Tiếp tục ở đâu?
**A**: Xem [ROADMAP.md](ROADMAP.md) - 4 giai đoạn

---

## 🎯 Mục Tiêu Tiếp Theo

### Công Việc Hiện Tại
- ✅ **Giai Đoạn 1**: Core Engine (Binary + Taxonomy)
- ✅ **Giai Đoạn 2**: Scoring Algorithm
- 🚧 **Giai Đoạn 3**: Testing (Unit tests hoàn, cần benchmarks)
- 📝 **Giai Đoạn 4**: Web UI (sắp tới)

### Tiếp Theo Làm Gì?

1. **Chạy Examples**
   ```bash
   python examples.py
   ```

2. **Chạy Tests**
   ```bash
   pytest codejudge/tests/ -v
   ```

3. **Viết Code Của Bạn**
   ```python
   from codejudge import IntegratedAssessor
   assessor = IntegratedAssessor()
   # ...
   ```

4. **Hoàn Thành Giai Đoạn 3**
   - Benchmark với HumanEval-X
   - Benchmark với CoNaLa
   - Fine-tune prompts

5. **Bắt Tay Giai Đoạn 4**
   - Web Backend (FastAPI)
   - Web Frontend
   - Docker

---

## 💬 Một Số Command Hữu Ích

```bash
# Test connection
python -c "from codejudge import LLMFactory; print('✓')"

# Chạy examples
python examples.py

# Run tests
pytest codejudge/tests/ -v --tb=short

# Code coverage
pytest codejudge/tests/ --cov=codejudge --cov-report=html

# Debug mode
CODEJUDGE_LOG_LEVEL=DEBUG python examples.py
```

---

## 📞 Hỗ Trợ

- 📖 [INSTALLATION.md](INSTALLATION.md) - Chi tiết
- 🎓 [examples.py](examples.py) - Ví dụ
- 🧪 [tests](codejudge/tests/) - Unit tests
- 📋 [ROADMAP.md](ROADMAP.md) - Lộ trình

---

## 🚀 Bắt Đầu Ngay!

```bash
# 1. Cài
pip install -r requirements-codejudge.txt

# 2. Setup
cp .env.example .env
# Sửa .env thêm API key

# 3. Chạy
python examples.py

# 🎉 Xong!
```

---

**Chúc bạn thành công!** 🎉

Bất kỳ vấn đề? Xem [INSTALLATION.md](INSTALLATION.md) hoặc chạy `pytest codejudge/tests/`.
