# Hướng Dẫn Chạy CodeJudge — Providers & Modes

Tài liệu này hướng dẫn nhanh cách chạy repo CodeJudge theo các provider (OpenAI, Gemini, Qwen, Llama/CodeLlama) và các chế độ hoạt động (local, remote/API, Kaggle, offload/disk, quantized).

## Tổng quan
- Provider: nhà cung cấp LLM (ví dụ `gpt-4`, `gemini-2.5-flash`, `qwen-turbo`, `meta-llama/Meta-Llama-3-8B-Instruct`, `codellama/...`).
- Mode: cách chạy model:
  - `local` — chạy model bằng Transformers trên GPU/CPU (Meta Llama, CodeLlama, Qwen local).
  - `api` / `remote` — gọi API cloud (OpenAI, Gemini, Qwen remote).
  - `kaggle` — chạy trong môi trường Kaggle (auto-detect, sử dụng offload/cache).
  - `offload` / `disk-based` — cho phép ghi/đọc trọng số sang đĩa khi RAM/VRAM hạn chế.
  - `quantized` — chạy với quantization (bitsandbytes 4-bit `nf4`) để giảm VRAM.

## Chọn provider
- Theo tên model trong hàm `form_filling()` hoặc `LLMFactory.create()`:
  - `gpt-4`, `gpt-3.5-turbo` → OpenAI (remote API, dùng `OPENAI_API_KEY`)
  - `gemini-2.5-flash` → Google Gemini (remote API, dùng `GOOGLE_API_KEY`)
  - `qwen-turbo`, `qwen-plus` → Qwen remote API (dùng `QWEN_API_KEY`)
  - `Qwen/...` hoặc `Qwen/Qwen2-7B` → Qwen local (HF)
  - `meta-llama/Meta-Llama-3-8B-Instruct` → Llama-3 local
  - `codellama/CodeLlama-7b-Instruct-hf` → CodeLlama local

## Cấu hình môi trường
- Copy template và điền API keys (không commit keys):
  ```bash
  cp .env.template .env
  # edit .env -> OPENAI_API_KEY, GOOGLE_API_KEY, QWEN_API_KEY, HUGGINGFACE_TOKEN
  ```
- Hoặc dùng Kaggle Secrets khi chạy trên Kaggle.
- Biến môi trường hữu ích: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `QWEN_API_KEY`, `HUGGINGFACE_TOKEN`, `HF_HOME`, `TRANSFORMERS_CACHE`.
- Lưu ý: `HUGGINGFACE_TOKEN` chỉ cần khi tải model private từ Hugging Face. Remote provider như `gemini-2.5-flash` dùng `GOOGLE_API_KEY`, không cần token HF.
- Nếu model Hugging Face private, chạy `huggingface-cli login` hoặc `hf auth login`, hoặc đặt `HUGGINGFACE_TOKEN`.

## Cách chạy (ví dụ nhanh)
- Dùng hàm `form_filling()` (áp dụng cho remote hoặc local):

```python
from code_model_score import form_filling, load_model

# Remote API (OpenAI/Gemini/Qwen remote)
prompt = [{"role":"user","content":"Đánh giá đoạn mã sau..."}]
resp = form_filling(model="gpt-4", prompt=prompt, terminators=None, pipeline=None, temperature=0.01)

# Local Llama-3
terminators, pipe = load_model("meta-llama/Meta-Llama-3-8B-Instruct")
resp = form_filling(model="meta-llama/Meta-Llama-3-8B-Instruct", prompt=prompt, terminators=terminators, pipeline=pipe, temperature=0.01)
```

- Dùng `LLMFactory` (interface thống nhất cho provider):

```python
from codejudge.core.llm_client import LLMFactory
client = LLMFactory.create(provider="gemini", model_name="gemini-2.5-flash")
print(client.generate("Viết 1 câu mô tả về LLM"))
```

## Chạy trên Kaggle (auto-config)
- Code tự phát hiện Kaggle và dùng:
  - Cache: `/kaggle/working/hf_cache`
  - Model root: `/kaggle/working/model`
  - Offload folder: `/kaggle/working/offload`
- Trên Kaggle, đặt secrets qua Notebook settings và cài phụ thuộc nếu cần:
  ```bash
  !pip install -q -r requirements.txt google-genai dashscope
  ```
- Ví dụ load Llama-3 trên Kaggle:
  ```python
  from code_model_score import load_model, form_filling
  terminators, pipe = load_model("meta-llama/Meta-Llama-3-8B-Instruct")
  resp = form_filling(..., terminators=terminators, pipeline=pipe)
  ```

## Offload / Disk-based setup
- Khi VRAM thiếu, dùng offload + quantization:
  - `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', ...)`
  - `from_pretrained(..., device_map='auto', offload_folder='/kaggle/working/offload', offload_state_dict=True, low_cpu_mem_usage=True)`
- `load_model()` và `LLMClient` đã hỗ trợ truyền `cache_dir` và `offload_folder`.
- Lưu ý: offload làm chậm inference nhưng cho phép chạy mô hình lớn trên GPU nhỏ.

## Quantized mode (bitsandbytes 4-bit)
- Đảm bảo cài `bitsandbytes` và `transformers` tương thích.
- Mặc định repo bật 4-bit cho mô hình local lớn để tiết kiệm VRAM.

## Tinh chỉnh runtime (ví dụ tham số)
- `cache_dir` — thư mục cache Hugging Face
- `offload_folder` — nơi lưu tạm trọng số offload
- `trust_remote_code` — đặt `False` trên Kaggle để an toàn
- `temperature`, `top_p`, `max_tokens` — tham số sinh văn bản

Ví dụ truyền tham số vào `load_model`:
```python
terminators, pipe = load_model(
    "Qwen/Qwen2-7B",
    cache_dir="/kaggle/working/hf_cache",
    offload_folder="/kaggle/working/offload"
)
```

## Lưu ý khi triển khai
- Nếu dùng remote providers, đảm bảo API key hợp lệ và có quota.
- Đặt `temperature=0.0..0.01` cho kết quả ổn định khi cần JSON/điểm số.
- Khi gặp OOM: thử model nhỏ hơn (7B), bật offload, hoặc chuyển sang API.

## Tài liệu tham khảo nhanh
- Xem `quickstart.py` để có ví dụ chạy sẵn.
- Xem `PROVIDER_SETUP.md` và `SETUP_CHECKLIST.md` để cấu hình chi tiết.

## CLI Commands (những lệnh sẵn dùng)
Dưới đây là các lệnh terminal hữu dụng để cài đặt, chạy ví dụ và kiểm tra.

### 1) Cài đặt dependencies (local venv)
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows (PowerShell)
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Tạo file `.env` từ template
```bash
cp .env.template .env    # Unix
copy .env.template .env  # Windows (cmd)
# Edit .env và thêm API keys
```

### 3) Chạy quickstart examples
```bash
# In repo root
python quickstart.py 1    # Kiểm tra môi trường
python quickstart.py 2    # OpenAI example
python quickstart.py 3    # Gemini example
python quickstart.py 4    # Qwen API example
python quickstart.py 5    # Llama local (cần tải model)
python quickstart.py 7    # LLMFactory example
```

### 4) Chạy một lệnh Python nhanh (LLMFactory)
```bash
python - <<'PY'
from codejudge.core.llm_client import LLMFactory
client = LLMFactory.create(provider='openai', model_name='gpt-4')
print(client.generate('Hello world', max_tokens=20))
PY
```

### 5) Chạy tests
```bash
# Từ thư mục repo
pytest -q
```

### 6) Kaggle-specific (chạy trong notebook cell)
```bash
!pip install -q -r requirements.txt google-genai dashscope

# Load secrets in a notebook cell
from kaggle_secrets import UserSecretsClient
import os
user_secrets = UserSecretsClient()
os.environ['OPENAI_API_KEY'] = user_secrets.get_secret('OPENAI_API_KEY')
# then run your code cells that call form_filling/load_model
```

### 7) Troubleshooting
```bash
# Nếu thiếu gói trong runtime
pip install scipy openai google-genai

# Kiểm tra Python syntax cho file đã chỉnh sửa
python -m py_compile code_model_score/utils.py code_model_score/gpt_score.py codejudge/core/llm_client.py
```

---

## Ví dụ: Chạy CoNaLa trên Kaggle với Llama (meta-llama/Meta-Llama-3-8B-Instruct)

Sau đây là các bước và câu lệnh bạn có thể copy vào Kaggle notebook để chạy đánh giá CoNaLa bằng Llama local (đã cấu hình offload/cache tự động trên Kaggle).

1) Cài dependencies (notebook cell):
```bash
!pip install -q -r requirements.txt
!pip install -q transformers bitsandbytes accelerate safetensors huggingface-hub
!pip install -q google-genai dashscope openai
```

2) Thêm Secrets trong Kaggle Notebook settings: `HUGGINGFACE_TOKEN` (nếu cần), `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `QWEN_API_KEY`.

3) Load secrets vào môi trường (notebook cell):
```python
from kaggle_secrets import UserSecretsClient
import os
us = UserSecretsClient()
try: os.environ['HUGGINGFACE_TOKEN'] = us.get_secret('HUGGINGFACE_TOKEN')
except: pass
try: os.environ['OPENAI_API_KEY'] = us.get_secret('OPENAI_API_KEY')
except: pass
```

4) Pre-download model vào cache/offload (khuyến nghị):
```python
from code_model_score.utils import load_model
terminators, pipeline = load_model("meta-llama/Meta-Llama-3-8B-Instruct")
print("Model cached and pipeline ready")
```

5) Chạy scoring CoNaLa (notebook cell hoặc bash):
```bash
!python evaluation/conala/score_conala.py \
  --json evaluation/conala/conala.json \
  --provider local \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --mode integrated \
  --output evaluation/conala/output/llama_conala_output.jsonl
```

Tùy chọn khi chạy:
- `--limit 100` : chỉ xử lý 100 mẫu (test nhanh)
- `--use-examples --num-examples 2` : bật few-shot calibration
- `--dry-run` : kiểm tra CLI mà không gọi LLM

6) Kiểm tra phần đầu file output:
```bash
!head -n 5 evaluation/conala/output/llama_conala_output.jsonl
```

Ghi chú:
- Nếu OOM trên Kaggle: thử model nhỏ hơn (`codellama/CodeLlama-7b-Instruct-hf`) hoặc chuyển sang remote provider (`--provider gemini`).
- Offload giúp tránh OOM nhưng làm chậm inference; đảm bảo đủ dung lượng `/kaggle/working/offload`.

---

**Lưu ý tương thích: `score_conala.py` (CLI thực tế)**

`evaluation/conala/score_conala.py` chỉ chấp nhận các tham số CLI sau (theo `argparse`):

- `--json`: Path tới file dataset (mặc định `evaluation/conala/conala.json`).
- `--source`: Trường source trong dataset để chấm (mặc định `codex`, hoặc `all`).
- `--provider`: Tên provider LLM (`local`, `openai`, `gemini`, `qwen`).
- `--model`: Tên model để dùng.
- `--api-key`: API key truyền tạm cho provider (tuỳ chọn).
- `--output`: File JSONL output (mặc định auto-gen).
- `--limit`: Giới hạn số mẫu để xử lý.
- `--start`: Bắt đầu tại index N.
- `--mode`: `integrated` hoặc `taxonomy`.
- `--use-examples`: Flag; bật calibration few-shot.
- `--num-examples`: Số ví dụ calibration.
- `--dry-run`: Flag; chỉ kiểm tra CLI và dataset, không gọi LLM.

Nếu bạn cố gắng truyền `--temperature` trực tiếp vào `score_conala.py` sẽ bị báo lỗi như sau vì tham số này không được định nghĩa trong script:
```
usage: score_conala.py [-h] [--json JSON] [--source SOURCE] [--provider PROVIDER]
                       [--model MODEL] [--api-key API_KEY] [--output OUTPUT]
                       [--limit LIMIT] [--start START] [--mode {integrated,taxonomy}]
                       [--use-examples] [--num-examples NUM_EXAMPLES] [--dry-run]
score_conala.py: error: unrecognized arguments: --temperature 0.0
```

**Model / Runtime options**

Thay vì truyền các tham số runtime/model như `--cache-dir`, `--offload-folder`, `--device`, `--quantize`, `--temperature` vào `score_conala.py`, hãy quản lý chúng bằng một trong các cách sau:

- Preload model trong một notebook hoặc script bằng `load_model(...)` (ví dụ trong `code_model_score.utils`) và truyền `terminators`/`pipeline` vào `form_filling()` khi gọi trực tiếp.
- Thiết lập biến môi trường trước khi chạy script (ví dụ `TRANSFORMERS_CACHE`, `HF_HOME`, `OPENAI_API_KEY`).
- Nếu cần, sửa `evaluation/conala/score_conala.py` để thêm argparse flags tùy biến (tôi có thể hỗ trợ nếu muốn).

Ví dụ workflow thay thế (Kaggle notebook):

1) Pre-download và cấu hình model (notebook cell):
```python
from code_model_score.utils import load_model
terminators, pipeline = load_model(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    cache_dir="/kaggle/working/hf_cache",
    offload_folder="/kaggle/working/offload"
)
```

2) Chạy `score_conala.py` (sử dụng provider/model phù hợp) — lưu ý không truyền `--temperature`:
```bash
python evaluation/conala/score_conala.py \
  --json evaluation/conala/conala.json \
  --provider local \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --mode integrated \
  --output evaluation/conala/output/llama_conala_output.jsonl \
  --limit 100 \
  --use-examples --num-examples 2
```

3) Nếu bạn cần điều chỉnh `temperature` hoặc các tham số generation khác, có hai lựa chọn:
- Chạy một script Python nhỏ sử dụng `LLMFactory.create(...)` / `form_filling(...)` trực tiếp và truyền tham số `temperature` vào đó.
- Yêu cầu tôi thêm flag `--temperature` và các tuỳ chọn khác vào `score_conala.py` — tôi có thể cập nhật script để chấp nhận và chuyển các giá trị này xuống `LLMFactory`/`form_filling`.

---

**CLI Options (Bảng biến số tổng quát)**

(Bên dưới là các biến số chung mà repo hỗ trợ theo các module khác; một số trong đó KHÔNG phải là flags trực tiếp của `score_conala.py`.)

- **`--json`**: Path tới file dataset input (JSON hoặc JSONL). Ví dụ: `evaluation/conala/conala.json`.
- **`--provider`**: Nhà cung cấp LLM: `local`, `openai`, `gemini`, `qwen`.
- **`--model`**: Tên model (HF ID hoặc provider model name). Ví dụ: `meta-llama/Meta-Llama-3-8B-Instruct`.
- **`--cache-dir`**: Thư mục cache HF (nơi lưu model đã tải). (Sử dụng `load_model` hoặc `TRANSFORMERS_CACHE`.)
- **`--offload-folder`**: Thư mục offload cho checkpoints/state (dùng trên máy VRAM thấp). (Sử dụng `load_model`.)
- **`--mode`**: Chế độ đánh giá/assessor (`integrated`, `taxonomy`).
- **`--output`**: Path tới file JSONL output chứa kết quả scoring.
- **`--limit`**: Số nguyên; giới hạn số mẫu để xử lý (test nhanh).
- **`--use-examples`**: Flag; bật few-shot examples (không có giá trị đi kèm).
- **`--num-examples`**: Số nguyên; số ví dụ few-shot để kèm vào prompt.
- **`--temperature`**: Float; nhiệt độ sampling cho generation — *không phải flag của `score_conala.py`*. Truyền khi gọi `form_filling()` trực tiếp hoặc thêm flag vào script.
- **`--device`**: Thiết bị mục tiêu: `cpu`, `cuda`, hoặc `cuda:0` (thiết lập qua code hoặc biến môi trường).
- **`--quantize`**: Cài đặt quantization local (`4bit`, `8bit`, `none`) — thiết lập khi dùng `load_model`.
- **`--dry-run`**: Flag; kiểm tra inputs và hiển thị các lệnh sẽ gọi mà không gọi LLM.

Ví dụ CLI copyable (khớp `score_conala.py`):
```bash
python evaluation/conala/score_conala.py \
  --json evaluation/conala/conala.json \
  --provider local \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --mode integrated \
  --output evaluation/conala/output/llama_conala_output.jsonl \
  --limit 100 \
  --use-examples --num-examples 2
```

Ghi chú ngắn:
- Trên Kaggle, preload model với `load_model(..., cache_dir=..., offload_folder=...)` nếu muốn kiểm soát cache/offload.
- Với provider remote (OpenAI/Gemini/Qwen) bạn cần export API key hoặc đặt trong Secrets của nền tảng.
- Sử dụng `--dry-run` để kiểm tra cấu hình trước khi thực hiện calls.

File này nằm ở: [RUN_PROVIDERS_MODES.md](RUN_PROVIDERS_MODES.md)
