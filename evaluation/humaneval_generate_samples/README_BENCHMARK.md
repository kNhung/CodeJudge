# Benchmark CodeJudge trên HumanEval Generated Samples

Hướng dẫn chi tiết để test CodeJudge trên dataset HumanEval generated samples với Gemini hoặc LLM khác.

## 🚀 **Cách 1: Test Nhanh (Không Checkpoint)**

### Binary Mode (Đạt/Không)
```bash
cd evaluation/humaneval_generate_samples

python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 10 \
  --provider gemini \
  --model gemini-2.0-flash \
  --mode binary \
  --verbose
```

### Taxonomy Mode (Chi Tiết 0-10)
```bash
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 10 \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --verbose
```

---

## 🔄 **Cách 2: Test Đầy Đủ với Resume & Rate Limit Handling**

**Tương tự cách HCMUS test, dùng pattern này:**

### Bước 1: Đặt tên run (QUAN TRỌNG để resume)
```bash
RUN_NAME="$(date +%y%m%d_%H%M)_gemini-2.5-flash_taxonomy"
echo "$RUN_NAME"
# Output: 260322_1430_gemini-2.5-flash_taxonomy
```

### Bước 2: Chạy lần 1, dừng ở rate limit
```bash
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit \
  --verbose
```

**Output khi gặp rate limit:**
```
⚠️  Rate limit hit at sample 47!
Stopping due to rate limit. Resume with:
  python benchmark_codejudge.py --run-name 260322_1430_gemini-2.5-flash_taxonomy --resume --stop-on-rate-limit
```

### Bước 3: Đợi API key mới, cập nhật .env
```bash
nano .env
# Thay GOOGLE_API_KEY=YOUR_NEW_KEY
```

### Bước 4: Tiếp tục test với run-name cũ
```bash
python benchmark_codejudge.py \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit
```

**Lặp lại bước 3-4 cho đến khi xong dataset.**

---

## 📊 **Output Files**

Khi chạy xong, kết quả được lưu ở: `output/{RUN_NAME}/`

```
output/260322_1430_gemini-2.5-flash_taxonomy/
├── 260322_1430_gemini-2.5-flash_taxonomy.jsonl          # Tất cả kết quả
├── 260322_1430_gemini-2.5-flash_taxonomy_metrics.json   # Metrics tổng hợp
└── 260322_1430_gemini-2.5-flash_taxonomy_checkpoint.json # Checkpoint (auto-delete khi xong)
```

### Xem Metrics
```bash
cat output/260322_1430_gemini-2.5-flash_taxonomy/260322_1430_gemini-2.5-flash_taxonomy_metrics.json | python -m json.tool
```

### Tail Results (xem real-time)
```bash
tail -f output/260322_1430_gemini-2.5-flash_taxonomy/260322_1430_gemini-2.5-flash_taxonomy.jsonl
```

---

## ⚙️ **Các Tham Số**

| Tham Số | Mặc Định | Ý Nghĩa |
|---------|----------|---------|
| `--data_file` | `./data/python_test.jsonl` | JSONL data file |
| `--limit` | `None` (all) | Giới hạn số samples |
| `--provider` | `gemini` | LLM provider: gemini/openai/anthropic/local |
| `--model` | `gemini-2.0-flash` | Model name |
| `--mode` | `binary` | binary/taxonomy/integrated |
| `--run-name` | Auto | Tên run (quan trọng cho resume) |
| `--resume` | - | Tiếp tục từ checkpoint |
| `--stop-on-rate-limit` | - | Dừng ở rate limit error |
| `--verbose` | - | Chi tiết từng sample |

---

## 🎯 **Các Mode Assessment**

### Binary (Nhanh, Rẻ)
- Output: Yes/No (Passed: 1, Failed: 0)
- Score: 10 hoặc 0
- Dùng khi: Chỉ cần biết đạt hay không

### Taxonomy (Chi Tiết, Đắt)
- Output: Danh sách lỗi (Negligible, Small, Major, Fatal)
- Score: 0-10 dựa trên lỗi
- Dùng khi: Cần feedback chi tiết

### Integrated (Kết Hợp Cả 2)
- Output: Cả binary + taxonomy
- Score: 0-10
- Dùng khi: Muốn full analysis

---

## 🌐 **Các Model Gemini**

| Model | Tốc độ | Chính Xác | Chi Phí | Khuyến Cáo |
|-------|--------|----------|--------|-----------|
| `gemini-2.0-flash` | ⚡⚡⚡ | 90% | 💰 | ✅ Tốt nhất |
| `gemini-2.5-flash` | ⚡⚡ | 92% | 💰💰 | Tốt |
| `gemini-1.5-pro` | 🚶 | 95% | 💰💰💰 | Nếu budget có |
| `gemini-1.5-flash` | ⚡ | 85% | 💰 | Rẻ nhất |

**Khuyến cáo:** Dùng `gemini-2.0-flash` cho cân bằng tốc độ/chi phí.

---

## 🔑 **Setup API Keys**

### Gemini
```bash
# 1. Lấy key từ https://aistudio.google.com/app/apikey
# 2. Thêm vào .env
echo "GOOGLE_API_KEY=YOUR_KEY" >> .env
```

### OpenAI
```bash
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Anthropic Claude
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

---

## 📋 **Ví Dụ Chạy**

### Test 20 samples với Gemini
```bash
RUN="test_gemini_20"
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 20 \
  --model gemini-2.0-flash \
  --mode binary \
  --run-name "$RUN"
```

### Test toàn bộ dataset với resume capability
```bash
RUN="full_test_$(date +%y%m%d_%H%M)"
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --run-name "$RUN" \
  --resume \
  --stop-on-rate-limit
```

### So sánh 2 model
```bash
# Model 1: Gemini Flash
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 50 \
  --model gemini-2.0-flash \
  --run-name "compare_gemini"

# Model 2: GPT-3.5
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 50 \
  --provider openai \
  --model gpt-3.5-turbo \
  --run-name "compare_gpt35"
```

---

## 🐛 **Troubleshooting**

### Lỗi: "GOOGLE_API_KEY not found"
```bash
# Kiểm tra .env
cat .env | grep GOOGLE_API_KEY

# Hoặc set trực tiếp
GOOGLE_API_KEY=your-key python benchmark_codejudge.py ...
```

### Lỗi: "requests not installed"
```bash
pip install requests
```

### Checkpoint bị xóa không thụng?
```bash
# Checkpoint auto-delete khi xong. Nếu muốn giữ lại:
cp output/{RUN_NAME}/{RUN_NAME}_checkpoint.json output/{RUN_NAME}/{RUN_NAME}_checkpoint.bak.json
```

### Muốn reset và test lại từ đầu?
```bash
# Xóa output folder
rm -rf output/{RUN_NAME}

# Hoặc đặt RUN_NAME mới
RUN_NAME="new_test_$(date +%s)"
```

---

## 📈 **Metrics Giải Thích**

File `*_metrics.json`:
```json
{
  "total_samples": 100,
  "processed": 100,
  "valid": 100,
  "errors": 0,
  "avg_score": 7.45,
  "std_score": 2.38,
  "pass_rate": 0.7456,
  "grade_distribution": {
    "A": 55,
    "B": 12,
    "C": 8,
    "D": 5,
    "F": 20
  }
}
```

- **avg_score**: Điểm trung bình (0-10)
- **std_score**: Độ lệch chuẩn
- **pass_rate**: Tỷ lệ passing (Grade A, B, C)
- **grade_distribution**: Phân bố từng grade

---

## 🎓 **So Sánh với HCMUS Benchmark**

| Loại | HCMUS | HumanEval Generated |
|------|-------|-------------------|
| **Script** | `evaluation/hcmus/test_modes.py` | `benchmark_codejudge.py` (này) |
| **Dataset** | HCMUS student submissions | Generated code samples |
| **Format** | CSV + Student Folders | JSONL |
| **Resume** | ✅ Yes | ✅ Yes |
| **Rate Limit Handling** | ✅ Yes | ✅ Yes |
| **Output** | JSONL + Metrics | JSONL + Metrics |

Cách dùng **gần giống nhau**, chỉ khác là dataset format.

---

## 📞 **Liên Hệ Hỗ Trợ**

Nếu có vấn đề:
1. Check `.env` có GOOGLE_API_KEY không
2. Test model: `python -c "from codejudge import LLMFactory; LLMFactory.create('gemini', 'gemini-2.0-flash')"`
3. Check dataset file: `head -1 ./data/python_test.jsonl`

---

**Happy Benchmarking! 🎉**
