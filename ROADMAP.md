# CodeJudge - Lộ Trình Phát Triển Hệ Thống Chấm Điểm Code

## Tổng Quan
Chuyển đổi repo CodeJudge thành một ứng dụng chấm điểm code tự động cho sinh viên, dựa trên bài báo CODEJUDGE và các đề xuất kỹ thuật trong paper.

---

## 📋 Giai Đoạn 1: Xây Dựng "Bộ Não" Chấm Điểm (Core Engine)

### Mục Tiêu
Phát triển hai luồng xử lý chấm điểm:
1. **Luồng Binary Assessment** (Đạt/Không Đạt)
2. **Luồng Taxonomy-Guided** (Điểm chi tiết 0-100)

### Chi Tiết Kỹ Thuật

#### 1.1 Luồng Binary Assessment
- **Kỹ thuật**: Analyze then Summarize
- **Bước 1 (Analyze)**:
  - Gửi prompt phân tích từng bước (Step-by-step)
  - Không yêu cầu sửa code, chỉ phân tích
  - Kiểm tra code có đáp ứng yêu cầu đề bài hay không
  
- **Bước 2 (Summarize)**:
  - Gửi kết quả phân tích vào
  - Yêu cầu LLM kết luận: "Yes" hoặc "No"
  - Sử dụng Regex để bắt keyword

#### 1.2 Luồng Taxonomy-Guided
- **Mục tiêu**: Tính điểm 0-100 và chỉ ra lỗi sai
- **Kỹ thuật**: Fault Localization

**4 Cấp Độ Lỗi**:
| Cấp Độ | Định Nghĩa | Trừ Điểm | Ví Dụ |
|--------|-----------|---------|-------|
| Negligible | Code xấu, thiếu import | 0 điểm | Thiếu whitespace, style |
| Small | Thiếu xử lý biên | -5 điểm | Chưa xử lý empty input |
| Major | Sai logic thuật toán | -50 điểm | Sai sort, sai formula |
| Fatal | Code chưa hoàn thành | -100 điểm | Gọi hàm không tồn tại |

**Output Format**: JSON với danh sách lỗi
```json
{
  "binary_result": "Yes/No",
  "errors": [
    {
      "type": "Major",
      "description": "...",
      "code_snippet": "..."
    }
  ],
  "score": 100
}
```

### Cấu Trúc Thư Mục Giai Đoạn 1
```
codejudge/
├── core/                          # Core Engine
│   ├── __init__.py
│   ├── llm_client.py             # Giao tiếp với LLM
│   ├── binary_assessor.py        # Binary Assessment (Yes/No)
│   ├── taxonomy_assessor.py      # Taxonomy-Guided (0-100)
│   ├── prompts.py                # Các prompt template
│   └── error_classifier.py       # Phân loại lỗi
```

---

## 📊 Giai Đoạn 2: Viết Thuật Toán Tính Điểm (Scoring Algorithm)

### Công Thức Tính Điểm
```
Điểm = Max(0, 100 - Tổng_Điểm_Phạt)

Mức Phạt:
- Small Error: -5 điểm
- Major Error: -50 điểm
- Fatal Error: -100 điểm
```

### Cấu Trúc Thư Mục Giai Đoạn 2
```
codejudge/
├── scoring/
│   ├── __init__.py
│   ├── scorer.py                 # Hàm tính điểm chính
│   ├── penalty_rules.py          # Quy tắc phạt
│   └── result_formatter.py       # Format kết quả
```

---

## 🧪 Giai Đoạn 3: Kiểm Thử Nội Bộ (Internal Testing)

### 3.1 Kiểm Thử Với HumanEval-X
- **Mục tiêu**: Xác minh Binary Assessment
- **Yêu cầu**:
- Code sai → "No" 
  - Code đúng → "Yes"

### 3.2 Kiểm Thử Với CoNaLa
- **Mục tiêu**: Tinh chỉnh điểm chi tiết
- **Yêu cầu**: 
  - So sánh điểm chấm tự động vs điểm con người
  - Tính correlation/accuracy

### Cấu Trúc Thư Mục Giai Đoạn 3
```
codejudge/
├── tests/
│   ├── __init__.py
│   ├── test_binary_assessor.py
│   ├── test_taxonomy_assessor.py
│   ├── test_scorer.py
│   ├── benchmarks/
│   │   ├── humaneval_x_test.py
│   │   └── conala_test.py
│   └── fixtures/
│       └── sample_submissions.py
```

---

## 🌐 Giai Đoạn 4: Xây Dựng Web & UX (Web Application)

### 4.1 Yêu Cầu Thiết Kế
1. **Xử Lý Độ Trễ**:
   - Async processing (Không để người dùng chờ)
   - Background job queue
   - Real-time notifications

2. **Giao Diện Giáo Viên**:
   - Upload file code hoặc copy-paste
   - Nhập Code Mẫu (Reference Code) cho bài khó
   - Xem kết quả chấm chi tiết

3. **Giao Diện Sinh Viên**:
   - Nộp bài
   - Xem điểm và lỗi
   - So sánh với code mẫu (nếu có)

### Cấu Trúc Thư Mục Giai Đoạn 4
```
codejudge/
├── backend/                       # Backend API
│   ├── app.py                    # Flask/FastAPI app
│   ├── routes/
│   │   ├── submission.py
│   │   ├── evaluation.py
│   │   └── results.py
│   └── models/
│       ├── submission_model.py
│       └── result_model.py
│
├── frontend/                      # Frontend Web
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── components/
│
└── docker/                        # Docker setup
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🎯 Thời Gian Dự Kiến

| Giai Đoạn | Nhiệm Vụ | Thời Gian |
|-----------|---------|----------|
| 1 | Core Engine | 2-3 tuần |
| 2 | Scoring Algorithm | 1 tuần |
| 3 | Internal Testing | 1-2 tuần |
| 4 | Web & UX | 2-3 tuần |

**Tổng Cộng**: ~6-9 tuần

---

## 📌 Các Lưu Ý Kỹ Thuật

1. **Dependency LLM**:
   - Hỗ trợ OpenAI (GPT-4), Anthropic (Claude), Local LLM (Llama-3)
   - Abstraction layer để dễ thay đổi provider

2. **Error Handling**:
   - Retry logic cho LLM calls (network failure)
   - Fallback mechanism cho API timeout

3. **Performance**:
   - Cache prompt engineering results
   - Parallel processing cho multiple submissions

4. **Prompt Engineering Tips**:
   - Sử dụng few-shot examples
   - Chain-of-thought prompting cho accuracy cao hơn
   - Nhập Code Mẫu nếu có để improve accuracy trên bài khó

5. **Tránh Lỗi Chấm Sai**:
   - Không bắt lỗi try-catch nếu đề bài không yêu cầu
   - Không trừ điểm style code nếu logic đúng

---

## 📚 Tài Liệu Tham Khảo

- Paper: CodeJudge - Auto-Grading Code Assignments
- Dataset:
  - HumanEval-X: Diverse programming benchmarks
- CoNaLa: Code + Natural Language pairs
  - APPS: Harder algorithmic challenges
- LLM Models: GPT-4, Llama-3, Code Llama

---

## ✅ Checklist

### Giai Đoạn 1
- [ ] Implement LLM Client
- [ ] Implement Binary Assessor
- [ ] Implement Taxonomy Assessor
- [ ] Define Error Taxonomy
- [ ] Write Prompt Templates
- [ ] Unit tests

### Giai Đoạn 2
- [ ] Implement Scoring Algorithm
- [ ] Define Penalty Rules
- [ ] Result Formatter
- [ ] Unit tests

### Giai Đoạn 3
- [ ] Prepare Test Data (HumanEval-X)
- [ ] Prepare Test Data (CoNaLa)
- [ ] Run Benchmarks
- [ ] Analyze Results
- [ ] Fine-tune Prompts

### Giai Đoạn 4
- [ ] Design API Endpoints
- [ ] Implement Backend
- [ ] Design UI/UX
- [ ] Implement Frontend
- [ ] Setup Docker
- [ ] Deploy & Test