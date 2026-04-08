## HCMUS Test Flow: Chay den rate limit, doi key, roi chay tiep

Buoc 1: vao env
```bash
source /home/knhung/miniconda3/bin/activate codejudge
```

Buoc 2: dat ten run co dinh (quan trong de resume dung file)
```bash
RUN_NAME="$(date +%y%m%d_%H%M)_gemini-2.5-flash_taxonomy"
echo "$RUN_NAME"
```

Buoc 3: chay lan 1, dung ngay khi gap 429
```bash
set -a && source .env && set +a
python evaluation/hcmus/test_modes.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit
```

Buoc 4: doi API key trong `.env`
```bash
nano .env
```

Cap nhat:
```env
GOOGLE_API_KEY=YOUR_NEW_KEY
```

Buoc 5: nap lai env va chay tiep dung run-name cu
```bash
set -a && source .env && set +a
python evaluation/hcmus/test_modes.py \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit
```

Ghi chu:
- KQ jsonl: `evaluation/hcmus/output/$RUN_NAME/$RUN_NAME.jsonl`
- Metrics: `evaluation/hcmus/output/$RUN_NAME/${RUN_NAME}_metrics.json`
- Co the lap lai Buoc 4-5 nhieu lan cho den khi xong dataset.


Test trên dataset
```bash
cd /home/knhung/KLTN/CodeJudge && source /home/knhung/miniconda3/bin/activate base && conda activate codejudge && python evaluation/hcmus/test_modes.py --provider gemini --model gemini-2.5-flash --mode taxonomy --start 67 --run-name hcmus_from_48_taxonomy --resume --stop-on-rate-limit
```
Tính điểm
```bash
cd /home/knhung/KLTN/CodeJudge && source /home/knhung/miniconda3/bin/activate base && conda activate codejudge && python test_modes.py --provider gemini --model gemini-2.5-flash --mode taxonomy --start 999999 --run-name hcmus_from_48_taxonomy --resume --metrics-scope file
```

---

## HumanEval Generated Samples Test Flow

Cách test tương tự HCMUS nhưng trên dataset HumanEval generated samples.

### Bước 1: Vào env
```bash
source /home/knhung/miniconda3/bin/activate codejudge
cd /home/knhung/KLTN/CodeJudge/evaluation/humaneval_generate_samples
```

### Bước 2: Đặt tên run
```bash
RUN_NAME="$(date +%y%m%d_%H%M)_gemini-2.5-flash_taxonomy"
echo "$RUN_NAME"
```

### Bước 3: Chạy lan 1, dừng ở rate limit
```bash
set -a && source ../../.env && set +a
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --provider gemini \
  --model gemini-2.5-flash \
  --mode taxonomy \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit
```

### Bước 4: Đợi API key mới, cập nhật .env
```bash
nano ../../.env
# Cập nhật: GOOGLE_API_KEY=YOUR_NEW_KEY
```

### Bước 5: Nạp lại env và chạy tiếp
```bash
set -a && source ../../.env && set +a
python benchmark_codejudge.py \
  --run-name "$RUN_NAME" \
  --resume \
  --stop-on-rate-limit
```

Ghi chú:
- KQ jsonl: `output/$RUN_NAME/$RUN_NAME.jsonl`
- Metrics: `output/$RUN_NAME/${RUN_NAME}_metrics.json`
- Lặp lại Bước 4-5 cho đến khi xong dataset

### Quick test (10 samples)
```bash
python benchmark_codejudge.py \
  --data_file ./data/python_test.jsonl \
  --limit 10 \
  --model gemini-2.0-flash \
  --mode binary \
  --verbose
```