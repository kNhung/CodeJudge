# CodeJudge Multi-Provider Refactoring - Summary

## Overview

CodeJudge has been refactored to support **multiple LLM providers** on both **local machines** and **Kaggle notebooks**, with intelligent auto-detection of the environment.

### Supported Providers

| Provider | Type | Cost | Speed | Use Case |
|----------|------|------|-------|----------|
| **OpenAI (GPT-4)** | Cloud API | $$ | Fast | Production, high quality |
| **Google Gemini** | Cloud API | $ | Fast | Budget-friendly, good quality |
| **Alibaba Qwen** | Cloud/Local | $ | Fast | Asia-based, efficient |
| **Meta Llama-3** | Local (GPU) | Free | Fastest | On-device, no API keys |
| **CodeLlama** | Local (GPU) | Free | Fast | Code-specific tasks |

---

## What Changed

### 1. **Core Code Refactoring**

#### `code_model_score/gpt_score.py`
- Refactored `form_filling()` to dispatch API models through unified `llm_request()` dispatcher
- Supports: `gpt-*`, `gemini-*`, `qwen-*`, `llama-*`, `codellama-*`
- Local models still use pipeline execution; remote models go through API adapters

#### `code_model_score/utils.py`
- Added `llm_request()` - unified dispatcher for OpenAI/Gemini/Qwen
- Added `qwen_request()` - Qwen API adapter
- Made `openai` import lazy to avoid runtime failures
- Enhanced `load_model()` with cache/offload folder support
- Added `get_kaggle_env()` - auto-detect and configure paths for Kaggle vs local

#### `codejudge/core/llm_client.py`
- Enhanced `LLMClient` with Kaggle-specific optimizations:
  - Offload folder support for low-memory systems
  - Cache directory customization
  - Auto-detection of `trust_remote_code` based on environment
- Added `QwenClient` - supports both remote API and local Qwen models
- Added `OpenAIClient` - thin wrapper around OpenAI SDK
- Enhanced `LLMFactory.create()` to support: `"local"`, `"openai"`, `"gemini"`, `"qwen"`

### 2. **Environment Detection**

**Automatic Kaggle Detection:**

```python
# Kaggle auto-paths (no setup needed):
HF_CACHE = "/kaggle/working/hf_cache"
MODEL_ROOT = "/kaggle/working/model"
OFFLOAD_FOLDER = "/kaggle/working/offload"

# Local auto-paths:
HF_CACHE = ~/.cache/huggingface
MODEL_ROOT = ./model
OFFLOAD_FOLDER = None (uses temp)
```

### 3. **Kaggle Optimizations**

Applied for low-memory Kaggle GPUs (T4 with 15GB VRAM):

| Feature | Benefit |
|---------|---------|
| 4-bit quantization (nf4) | Reduces model size by ~4x |
| Offload to disk | Allows models larger than VRAM |
| Low CPU memory mode | Reduces intermediate tensors |
| Offload state dict | Spills weights to disk as needed |

---

## How to Use

### **Option 1: Local Machine (with API Keys)**

```bash
# 1. Copy template and configure
cp .env.template .env
# Edit .env, add: OPENAI_API_KEY, GOOGLE_API_KEY, QWEN_API_KEY

# 2. Use any provider
python quickstart.py 2      # OpenAI
python quickstart.py 3      # Gemini
python quickstart.py 4      # Qwen
python quickstart.py 5      # Llama
```

### **Option 2: Kaggle Notebook**

```python
# 1. Add secrets in notebook settings:
#    OPENAI_API_KEY, GOOGLE_API_KEY, QWEN_API_KEY

# 2. In first cell:
from kaggle_secrets import UserSecretsClient
import os

user_secrets = UserSecretsClient()
os.environ["OPENAI_API_KEY"] = user_secrets.get_secret("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"] = user_secrets.get_secret("GOOGLE_API_KEY")

# 3. Use any provider (paths auto-adjust):
from code_model_score import form_filling

response = form_filling(
    model="gpt-4",              # or gemini-2.5-flash, qwen-turbo, etc.
    prompt=[{"role": "user", "content": "..."}],
    terminators=None,
    pipeline=None,
    temperature=0.1
)
```

### **Option 3: Using LLMFactory (Recommended)**

```python
from codejudge.core.llm_client import LLMFactory

# Create any client with one line
client = LLMFactory.create(provider="gemini", model_name="gemini-2.5-flash")

# All clients have compatible interface
response = client.generate(prompt="...", max_tokens=100)
```

---

## Files Added

| File | Purpose |
|------|---------|
| `PROVIDER_SETUP.md` | Complete setup guide with examples |
| `.env.template` | Configuration template |
| `quickstart.py` | Quick reference examples |
| `REFACTORING_SUMMARY.md` | This file |

---

## Files Modified

| File | Changes |
|------|---------|
| `code_model_score/gpt_score.py` | Added `llm_request()` dispatcher |
| `code_model_score/utils.py` | Added Kaggle detection, cache/offload support |
| `codejudge/core/llm_client.py` | Added QwenClient, OpenAIClient, Kaggle optimizations |
| `requirements.txt` | Updated (google-generativeai → google-genai) |

---

## Key Features

### 🌍 **Multi-Provider Support**
- Seamlessly switch between OpenAI, Gemini, Qwen, and local Llama models
- Single codebase for all providers

### 📍 **Auto-Environment Detection**
- Automatically detects Kaggle vs local machine
- Adjusts paths, quantization, and API behavior accordingly
- No manual configuration needed for Kaggle

### 💾 **Smart Caching**
- Models cached after first download
- API responses cached to reduce costs
- Configurable cache directories

### ⚡ **Kaggle Optimizations**
- 4-bit quantization for memory efficiency
- Disk offloading for models larger than VRAM
- Works on T4 GPU (15GB VRAM) with 7B/8B models
- Can extend to 13B+ with offloading

### 🔐 **Flexible Configuration**
- Environment variables, .env files, or programmatic configuration
- Kaggle Secrets for secure key management
- Optional parameters for fine-tuning

---

## Quick Reference

### Initialize a Client

```python
# Option A: Direct API
from code_model_score import form_filling
response = form_filling(model="gpt-4", prompt=prompt, ...)

# Option B: Factory
from codejudge.core.llm_client import LLMFactory
client = LLMFactory.create(provider="openai", model_name="gpt-4")
response = client.generate(prompt="...", max_tokens=100)
```

### Configure Paths

```python
# All auto-configured, but you can override:
from code_model_score import load_model

terminators, pipeline = load_model(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    cache_dir="/custom/cache",
    offload_folder="/custom/offload"
)
```

### Check Environment

```python
from code_model_score.utils import get_kaggle_env, is_running_on_kaggle

print(f"Kaggle: {is_running_on_kaggle()}")
print(f"Paths: {get_kaggle_env()}")
```

---

## Cost Estimation

For 1000 requests of 100 tokens each:

| Provider | Cost |
|----------|------|
| OpenAI (GPT-4) | ~$6 |
| Gemini (2.5-flash) | ~$0.08 |
| Qwen (API) | ~$0.01 |
| Llama-3 (local) | $0 (after model download) |

**Recommendation:** Use Gemini for testing, Llama-3 for batch processing.

---

## Troubleshooting

### Q: Model downloads slowly on Kaggle
**A:** Models are cached in `/kaggle/working/hf_cache`. Subsequent runs use cache.

### Q: Out of memory on Kaggle T4
**A:** Already handled with 4-bit quantization and offloading. If still failing:
- Switch to smaller model: `CodeLlama-7b` instead of `Llama-3-8b`
- Or use cloud API: Gemini (no GPU needed)

### Q: API key not recognized on Kaggle
**A:** Use Kaggle "Secrets" in notebook settings, then load:
```python
from kaggle_secrets import UserSecretsClient
os.environ["OPENAI_API_KEY"] = UserSecretsClient().get_secret("OPENAI_API_KEY")
```

### Q: How to use custom model?
**A:** Pass to `load_model()` or `LLMFactory.create()`:
```python
from code_model_score import load_model
terminators, pipeline = load_model("microsoft/Phi-2")
```

---

## Next Steps

1. **Try locally first:**
   ```bash
   cp .env.template .env
   # Edit .env with API keys
   python quickstart.py 7  # LLMFactory example
   ```

2. **Deploy to Kaggle:**
   - Create notebook
   - Add secrets
   - Copy code from `quickstart.py` examples

3. **Production deployment:**
   - Use `get_kaggle_env()` for path management
   - Implement request logging with `logging` module
   - Cache results to reduce API calls

---

## Documentation

- **Complete Setup Guide:** [PROVIDER_SETUP.md](PROVIDER_SETUP.md)
- **Quick Examples:** `python quickstart.py`
- **API Reference:** Check docstrings in modified files

---

## Version

- CodeJudge Multi-Provider: v1.0
- Tested on: Python 3.10+, transformers 4.36+, torch 2.0+
- Last updated: May 30, 2024

---

## Credits

Refactored to support multiple LLM providers for maximum flexibility in research and production use.

If you have issues or suggestions, please check:
1. `.env` configuration
2. API keys are set (locally or Kaggle Secrets)
3. Internet connection enabled (for API calls)
4. Sufficient disk space for model cache (20-30GB recommended)
