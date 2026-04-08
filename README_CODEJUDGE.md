# CodeJudge - Hệ Thống Chấm Điểm Code Tự Động

> Biến repo này thành một ứng dụng chấm điểm code lập trình cho sinh viên với 4 giai đoạn

## 📑 Mục Lục

- [Giới Thiệu](#giới-thiệu)
- [Tính Năng](#tính-năng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Bắt Đầu Nhanh](#bắt-đầu-nhanh)
- [4 Giai Đoạn](#4-giai-đoạn)
- [Sử Dụng](#sử-dụng)
- [API](#api)
- [Ví Dụ](#ví-dụ)

---

## 🎯 Giới Thiệu

**CodeJudge** là một hệ thống chấm điểm code tự động cho bài tập lập trình, dựa trên bài báo CodeJudge và sử dụng LLM (Large Language Models) để đánh giá code.

### Tại Sao CodeJudge?

1. **Tự động hóa**: Không cần giáo viên chấm công việc lặp lại
2. **Chính xác**: Sử dụng AI để phân tích logic code chuyên sâu
3. **Chi tiết**: Không chỉ cho điểm, mà còn chỉ ra lỗi cụ thể
4. **Linh hoạt**: Hỗ trợ nhiều ngôn ngữ lập trình

---

## ✨ Tính Năng

### Giai Đoạn 1: Core Engine ✅ (Hoàn Thành)

- ✅ **Binary Assessment**: Chấm điểm Đạt/Không Đạt (Yes/No)
  - Kỹ thuật: "Analyze then Summarize"
  - Phân tích từng bước (Step-by-step)
  - Kết luận ngắn gọn

- ✅ **Taxonomy-Guided Assessment**: Chấm điểm chi tiết (0-100)
  - 4 cấp độ lỗi: Negligible, Small, Major, Fatal
  - Fault Localization
  - JSON output cho parsing

- ✅ **Integrated Assessor**: Kết hợp cả hai luồng

### Giai Đoạn 2: Scoring Algorithm ✅ (Hoàn Thành)

- ✅ Tính điểm: Công thức Max(0, 100 - Tổng_Điểm_Phạt)
- ✅ Mức phạt: Negligible (0), Small (-5), Major (-50), Fatal (-100)
- ✅ Score Interpreter: Grade A-F
- ✅ Result Formatter: Hiển thị kết quả

### Giai Đoạn 3: Internal Testing 🚧 (Trong Tiến Hành)

- ✅ Unit tests cho Core Engine
- ✅ Integration tests
- ⏳ Benchmarks với HumanEval-X
- ⏳ Benchmarks với CoNaLa

### Giai Đoạn 4: Web UI 📝 (Sắp Tới)

- 📝 Backend API (FastAPI/Flask)
- 📝 Web Interface
- 📝 Async processing
- 📝 Docker setup

---

## 📁 Cấu Trúc Dự Án

```
CodeJudge/
├── codejudge/                      # Main package ✅
│   ├── __init__.py
│   ├── core/                       # Core Engine ✅
│   │   ├── __init__.py
│   │   ├── llm_client.py          # LLM providers
│   │   ├── prompts.py             # Prompt templates
│   │   ├── binary_assessor.py     # Binary assessment
│   │   ├── taxonomy_assessor.py   # Taxonomy scoring
│   │   └── integrated_assessor.py # Integrated
│   │
│   ├── scoring/                    # Scoring Algorithm ✅
│   │   ├── __init__.py
│   │   └── scorer.py              # Score calculation
│   │
│   ├── tests/                      # Testing Suite 🚧
│   │   ├── __init__.py
│   │   ├── test_core_engine.py    # Unit tests
│   │   ├── benchmarks/            # Benchmarks
│   │   └── fixtures/              # Test data
│   │
│   ├── backend/                    # Web Backend 📝
│   │   ├── routes/
│   │   └── models/
│   │
│   └── frontend/                   # Web Frontend 📝
│       ├── js/
│       └── css/
│
├── evaluation/                     # Existing datasets
│   ├── apps/
│   ├── bigcodebench/
│   ├── conala/
│   └── humaneval/
│
├── examples.py                     # Usage examples ✅
├── ROADMAP.md                      # Development roadmap ✅
├── INSTALLATION.md                 # Installation guide ✅
├── requirements-codejudge.txt      # Python dependencies ✅
├── .env.example                    # Config template ✅
└── README.md                       # This file
```

---

## 🚀 Bắt Đầu Nhanh

### 1️⃣ Cài Đặt

```bash
# Clone / navigate
cd CodeJudge

# Cài dependencies
pip install -r requirements-codejudge.txt

# Setup config (copy từ .env.example)
cp .env.example .env
# Sửa .env và thêm API key
```

### 2️⃣ Chạy Ví Dụ

```bash
# Chạy example
python examples.py

# Hoặc test từng cái
python -c "
from codejudge import IntegratedAssessor

assessor = IntegratedAssessor()
problem = 'Tính tổng danh sách'
code = 'def sum_list(n): return sum(n)'

result = assessor.assess(problem, code)
print(f'Score: {result[\"summary\"][\"score\"]}')
"
```

### 3️⃣ Chạy Tests

```bash
# Cài pytest
pip install pytest pytest-cov

# Chạy tests
pytest codejudge/tests/ -v

# Với code coverage
pytest codejudge/tests/ --cov=codejudge/
```

---

## 4️⃣ Các Giai Đoạn

### Giai Đoạn 1: Xây Dựng Core Engine ✅

**Mục tiêu**: Implement hai luồng chấm điểm

**Chi tiết**:
- Luồng 1: Binary Assessment (Yes/No) - "Analyze then Summarize"
- Luồng 2: Taxonomy-Guided (0-100) - Phân loại 4 cấp độ lỗi

**Kết quả**:
```
codejudge/core/
├── llm_client.py       (OpenAI, Anthropic, Local LLM)
├── prompts.py          (System + user prompts)
├── binary_assessor.py  (2-step analysis)
├── taxonomy_assessor.py (Error taxonomy + scoring)
└── integrated_assessor.py (Combine both)
```

### Giai Đoạn 2: Thuật Toán Tính Điểm ✅

**Mục tiêu**: Quy đổi lỗi thành điểm

**Công thức**:
```
Điểm = Max(0, 100 - Tổng_Điểm_Phạt)

Mức Phạt:
- Negligible: 0 điểm
- Small: -5 điểm  
- Major: -50 điểm
- Fatal: -100 điểm
```

**Kết quả**:
```
codejudge/scoring/
├── scorer.py          (Calculate final score)
└── __init__.py
```

### Giai Đoạn 3: Kiểm Thử Nội Bộ 🚧

**Mục tiêu**: Validate hệ thống

**Bước 1**: Test với HumanEval-X
```python
# Đơn giản, test Binary Assessment
# Code sai → "No"
# Code đúng → "Yes"

# Mục tiêu: Accuracy > 85%
```

**Bước 2**: Test với CoNaLa
```python
# Phức tạp hơn, test Taxonomy Assessment
# So sánh điểm tự động vs điểm con người

# Mục tiêu: Correlation > 0.8
```

**Kết quả**:
```
codejudge/tests/
├── test_core_engine.py  (Unit tests)
├── benchmarks/
│   ├── humaneval_test.py
│   └── conala_test.py
└── fixtures/
```

### Giai Đoạn 4: Web UI 📝 (Sắp Tới)

**Mục tiêu**: Giao diện web cho giáo viên và sinh viên

**Backend**:
- FastAPI/Flask server
- Async job queue
- Results database

**Frontend**:
- Upload code
- Enter reference code
- View detailed feedback

**Deployment**:
- Docker
- Kubernetes (optional)

---

## 📝 Sử Dụng

### Dùng Cách 1: Binary Assessment (Đạt/Không Đạt)

```python
from codejudge import BinaryAssessor

assessor = BinaryAssessor()

result = assessor.assess(
    problem_statement="Viết hàm tính tổng danh sách",
    student_code="def sum_list(n): return sum(n)"
)

print(result['result'])    # "Yes" hoặc "No"
print(result['passed'])    # True hoặc False
```

### Dùng Cách 2: Taxonomy Assessment (Chi Tiết)

```python
from codejudge import TaxonomyAssessor

assessor = TaxonomyAssessor()

result = assessor.assess(
    problem_statement="...",
    student_code="...",
    reference_code="..."  # Optional
)

print(result['final_score'])  # 0-100
print(result['errors'])       # Danh sách lỗi
```

### Dùng Cách 3: Integrated (Khuyến Nghị) ⭐

```python
from codejudge import IntegratedAssessor

assessor = IntegratedAssessor(run_both_assessments=True)

result = assessor.assess(
    problem_statement="...",
    student_code="...",
    reference_code="..."  # Optional
)

summary = result['summary']
print(f"Status: {summary['status']}")      # PASS/FAIL
print(f"Score: {summary['score']}")        # 0-100
print(f"Grade: {summary['grade_letter']}")  # A-F
```

---

## 🔌 API

### Chính

| Class | Phương Thức | Mô Tả |
|-------|------------|-------|
| `BinaryAssessor` | `assess()` | Chấm Yes/No |
| `TaxonomyAssessor` | `assess()` | Chấm 0-100 |
| `IntegratedAssessor` | `assess()` | Kết hợp cả hai |
| `Scorer` | `calculate_score()` | Tính điểm từ lỗi |
| `ScoreInterpreter` | `get_grade()` | Lấy grade A-F |
| `ResultFormatter` | `format_full_result()` | Format output |

### LLM Providers

```python
from codejudge import LLMFactory

# OpenAI
client = LLMFactory.create("openai", model_name="gpt-4")

# Anthropic
client = LLMFactory.create("anthropic", model_name="claude-3-opus-20240229")

# Local LLM
client = LLMFactory.create("local", model_name="llama2", base_url="http://localhost:11434")
```

---

## 📚 Ví Dụ

Xem [examples.py](examples.py) để có 5 ví dụ chi tiết:

1. Binary Assessment
2. Taxonomy Assessment
3. Integrated Assessment
4. Custom LLM Provider
5. Scoring & Interpretation

Chạy:
```bash
python examples.py
```

---

## 🧪 Testing

```bash
# Tất cả tests
pytest codejudge/tests/ -v

# Specific test class
pytest codejudge/tests/test_core_engine.py::TestBinaryAssessor -v

# Với coverage
pytest codejudge/tests/ --cov=codejudge --cov-report=html
```

---

## ⚙️ Configuration

### Via .env

```bash
# Chọn provider
CODEJUDGE_DEFAULT_PROVIDER=openai  # hoặc: anthropic, local

# Model & API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LOCAL_LLM_URL=http://localhost:11434

# Settings
CODEJUDGE_TEMPERATURE=0.3      # 0.0-1.0
CODEJUDGE_TIMEOUT=120          # seconds
CODEJUDGE_LOG_LEVEL=INFO       # DEBUG, INFO, WARNING
```

### Via Code

```python
from codejudge import BinaryAssessor

assessor = BinaryAssessor()

# Custom system prompt
assessor.set_system_prompt("Custom prompt...")

# Custom taxonomy
assessor.error_taxonomy = {...}
```

---

## 💡 Tips & Tricks

### Tối Ưu Hóa Chi Phí

- Dùng GPT-3.5-turbo cho bài đơn (~$0.002/submission)
- Dùng Local LLM cho bài dễ (Free)
- Cache LLM responses

### Cải Thiện Độ Chính Xác

- Thêm **reference code** (code mẫu)
- Sử dụng **few-shot prompting**
- Chain-of-thought reasoning

### Tăng Tốc Độ

- Parallel processing
- Batch submissions
- Async backend

---

## 🚨 Troubleshooting

| Lỗi | Giải Pháp |
|-----|----------|
| "No LLM provider configured" | Tạo .env với API key |
| "openai not found" | `pip install openai` |
| "JSON decode error" | Bật DEBUG logging để xem response |
| LLM chấm chậm | Dùng local LLM hoặc GPT-3.5-turbo |

Xem [INSTALLATION.md](INSTALLATION.md) để chi tiết.

---

## 📊 Hiệu Năng

Theo bài báo:
- **Thời gian xử lý**: < 20 giây/submission
- **Accuracy**: > 85% (Binary)
- **Correlation**: > 0.8 (vs con người)

---

## 📖 Tài Liệu

- [ROADMAP.md](ROADMAP.md) - Lộ trình phát triển
- [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn chi tiết
- [examples.py](examples.py) - 5 ví dụ sử dụng
- [Paper](paper/) - Bài báo gốc
- [Tests](codejudge/tests/) - Unit tests

---

## 🤝 Đóng Góp

Các giai đoạn sắp tới:
1. ✅ Giai đoạn 1: Core Engine
2. ✅ Giai đoạn 2: Scoring
3. 🚧 Giai đoạn 3: Testing
4. 📝 Giai đoạn 4: Web UI

Để tham gia: 
- Hoàn thành Giai Đoạn 3 (benchmarks)
- Implement Giai Đoạn 4 (backend + frontend)
- Tối ưu hóa prompts

---

## 📞 Support

Có thắc mắc?
1. Xem [INSTALLATION.md](INSTALLATION.md)
2. Chạy [examples.py](examples.py)
3. Kiểm tra logs (bật DEBUG)

---

## 📄 License

[LICENSE](LICENSE)

---

## 🎉 Cảm Ơn

Dự án được xây dựng dựa trên:
- **Paper**: CodeJudge - Auto-Grading Code Assignments
- **Datasets**: HumanEval-X, CoNaLa, APPS
- **LLMs**: OpenAI, Anthropic, Meta (Llama)

---

**Built with ❤️ for automated code assessment**
