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