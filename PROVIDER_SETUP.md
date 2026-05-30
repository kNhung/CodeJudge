# CodeJudge LLM Provider Setup Guide

This document explains how to configure and use different LLM providers (OpenAI, Gemini, Qwen, Llama) on both local machines and Kaggle.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Machine Setup](#local-machine-setup)
3. [Kaggle Notebook Setup](#kaggle-notebook-setup)
4. [Provider Configurations](#provider-configurations)
5. [Environment Variables](#environment-variables)
6. [Usage Examples](#usage-examples)

---

## Quick Start

### Installation

Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

For specific providers:

```bash
# OpenAI
pip install openai>=1.0.0

# Google Gemini
pip install google-genai>=0.1.0

# Qwen (Remote API)
pip install dashscope

# Local model support
pip install transformers bitsandbytes accelerate
```

---

## Local Machine Setup

### 1. Directory Structure

After installation, the code will auto-create these directories:

```
./model/               # Local Llama/CodeLlama models
~/.cache/huggingface/  # Hugging Face model cache
./offload/ (optional)  # Offload folder for low-memory systems
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Google Gemini
GOOGLE_API_KEY=AIzaSy...

# Qwen (DashScope)
QWEN_API_KEY=sk-...

# Optional: Customize cache directories
HF_HOME=~/.cache/huggingface
TRANSFORMERS_CACHE=~/.cache/huggingface
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Running with Different Providers

**OpenAI (GPT-4/GPT-3.5):**

```python
from code_model_score import form_filling, load_model

prompt = [{"role": "user", "content": "Rate this code..."}]
response = form_filling(
    model="gpt-4",
    prompt=prompt,
    terminators=None,
    pipeline=None,
    temperature=0.1
)
```

**Google Gemini:**

```python
response = form_filling(
    model="gemini-2.5-flash",
    prompt=prompt,
    terminators=None,
    pipeline=None,
    temperature=0.1
)
```

**Qwen (Remote):**

```python
response = form_filling(
    model="qwen-turbo",  # or qwen-plus
    prompt=prompt,
    terminators=None,
    pipeline=None,
    temperature=0.1
)
```

**Llama-3 / CodeLlama (Local):**

```python
# First time: load and cache the model
terminators, pipeline = load_model(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    root_path="./model"
)

response = form_filling(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    prompt=prompt,
    terminators=terminators,
    pipeline=pipeline,
    temperature=0.1
)
```

---

## Kaggle Notebook Setup

### 1. Auto-Detection

CodeJudge automatically detects Kaggle environment and adjusts paths:

```python
# Kaggle paths (auto-detected):
# - Models: /kaggle/working/model
# - Cache: /kaggle/working/hf_cache
# - Offload: /kaggle/working/offload
```

### 2. Add Secrets to Kaggle

1. Go to your Kaggle notebook settings.
2. Enable "Internet" (for API calls).
3. In "Secrets", add:

| Name | Value |
|------|-------|
| OPENAI_API_KEY | sk-... |
| GOOGLE_API_KEY | AIzaSy... |
| QWEN_API_KEY | sk-... |
| HUGGINGFACE_TOKEN | hf_... |

Load secrets in your notebook:

```python
import os
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
os.environ["OPENAI_API_KEY"] = user_secrets.get_secret("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"] = user_secrets.get_secret("GOOGLE_API_KEY")
os.environ["QWEN_API_KEY"] = user_secrets.get_secret("QWEN_API_KEY")
```

### 3. Install Dependencies in Kaggle

```bash
!pip install -q -r requirements.txt
!pip install -q google-genai dashscope
```

### 4. Kaggle-Specific Optimizations

For memory-limited Kaggle GPUs, the code auto-enables:

- **4-bit quantization** (bitsandbytes)
- **Offload to disk** (models can spill to `/kaggle/working/offload`)
- **CPU offloading** for large models
- **Caching** to avoid re-downloading

This allows running 7B/13B models even on T4 GPUs (15GB VRAM).

### 5. Full Kaggle Example

```python
# Setup secrets and paths
import os
import sys
sys.path.insert(0, '/kaggle/working')

from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()

os.environ["OPENAI_API_KEY"] = user_secrets.get_secret("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"] = user_secrets.get_secret("GOOGLE_API_KEY")

# Import CodeJudge
from code_model_score import form_filling

# Use any provider - paths auto-adjust for Kaggle
prompt = [{"role": "user", "content": "Evaluate code..."}]

# Option 1: OpenAI (cloud)
response = form_filling(model="gpt-4", prompt=prompt, terminators=None, pipeline=None, temperature=0.1)

# Option 2: Gemini (cloud)
response = form_filling(model="gemini-2.5-flash", prompt=prompt, terminators=None, pipeline=None, temperature=0.1)

# Option 3: Llama-3 (local GPU)
from code_model_score import load_model
terminators, pipeline = load_model("meta-llama/Meta-Llama-3-8B-Instruct")
response = form_filling(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    prompt=prompt,
    terminators=terminators,
    pipeline=pipeline,
    temperature=0.1
)
```

---

## Provider Configurations

### OpenAI

**Supported Models:**
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Setup:**
```python
from code_model_score.utils import openai_request

response = openai_request(
    message=[{"role": "user", "content": "Your prompt"}],
    model="gpt-4",
    temperature=0.1,
    max_tokens=2000
)
```

**Cost:** ~$0.03-0.06 per 1K input tokens

---

### Google Gemini

**Supported Models:**
- `gemini-2.5-flash` (recommended, fast + cheap)
- `gemini-2.0-flash`
- `gemini-pro`

**Setup:**
```python
from code_model_score.utils import gemini_request

response = gemini_request(
    message=[{"role": "user", "content": "Your prompt"}],
    model="gemini-2.5-flash",
    temperature=0.1,
    max_tokens=2000
)
```

**Cost:** Free tier available; paid plans start ~$0.00075 per 1K input tokens

---

### Qwen (阿里云)

**Remote Models (API):**
- `qwen-turbo` (balance of speed/quality)
- `qwen-plus` (higher quality)
- `qwen-max` (highest quality, slower)

**Local Models (HF):**
- `Qwen/Qwen2-7B`
- `Qwen/Qwen2-14B` (requires more VRAM)
- `Qwen/Qwen1.5-7B`

**Remote Setup:**
```python
from code_model_score.utils import qwen_request

response = qwen_request(
    message=[{"role": "user", "content": "Your prompt"}],
    model="qwen-turbo",
    temperature=0.1,
    max_tokens=2000
)
```

**Local Setup:**
```python
from codejudge.core.llm_client import QwenClient

client = QwenClient(model_name="Qwen/Qwen2-7B")
response = client.generate(prompt="Your prompt", max_tokens=2000)
```

**Cost:** Remote API ~¥0.0002 per 1K tokens (~$0.00003)

---

### Meta Llama (Local)

**Supported Models:**
- `meta-llama/Meta-Llama-3-8B-Instruct` (8B, recommended for Kaggle)
- `meta-llama/Meta-Llama-3-70B-Instruct` (70B, requires multi-GPU)
- `codellama/CodeLlama-7b-Instruct-hf` (code-specific, 7B)
- `codellama/CodeLlama-34b-Instruct-hf` (34B)

**Setup:**
```python
from code_model_score import load_model, form_filling

# Load once, cache automatically
terminators, pipeline = load_model(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    root_path="./model"  # Auto-detects Kaggle vs local
)

response = form_filling(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    prompt=prompt,
    terminators=terminators,
    pipeline=pipeline,
    temperature=0.01
)
```

**Cost:** Free (runs locally on your hardware)

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication | `sk-...` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `QWEN_API_KEY` | Alibaba Qwen API key | `sk-...` |
| `HF_HOME` | Hugging Face cache directory | `/kaggle/working/hf_cache` |
| `TRANSFORMERS_CACHE` | Transformers library cache | `/kaggle/working/hf_cache` |
| `KAGGLE_KERNEL_RUN_TYPE` | Auto-set by Kaggle (no need to set) | - |

### Load from .env file:

```python
from dotenv import load_dotenv
import os

load_dotenv(".env")
print(os.getenv("OPENAI_API_KEY"))
```

---

## Usage Examples

### Example 1: Using `form_filling` with different models

```python
from code_model_score import form_filling, load_model

prompt = [
    {"role": "system", "content": "You are a code reviewer."},
    {"role": "user", "content": "Review this code: def add(a, b): return a + b"}
]

# Try each provider
models = [
    "gpt-4",
    "gemini-2.5-flash",
    "qwen-turbo",
    "meta-llama/Meta-Llama-3-8B-Instruct"
]

for model_name in models:
    print(f"\n[{model_name}]")
    try:
        if model_name.startswith("meta-llama") or model_name.startswith("codellama"):
            # Local model
            terminators, pipeline = load_model(model_name)
            response = form_filling(model_name, prompt, terminators, pipeline, temperature=0.01)
        else:
            # Remote/API model
            response = form_filling(model_name, prompt, None, None, temperature=0.01)
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
```

### Example 2: Using `LLMFactory` for provider abstraction

```python
from codejudge.core.llm_client import LLMFactory

# Create clients for different providers
clients = {
    "local": LLMFactory.create(provider="local", model_name="meta-llama/Meta-Llama-3-8B-Instruct"),
    "openai": LLMFactory.create(provider="openai", model_name="gpt-4"),
    "gemini": LLMFactory.create(provider="gemini", model_name="gemini-2.5-flash"),
    "qwen": LLMFactory.create(provider="qwen", model_name="qwen-turbo"),
}

# All clients have compatible .generate() method
for provider, client in clients.items():
    try:
        result = client.generate("Explain this code: x = [1,2,3]", max_tokens=100)
        print(f"{provider}: {result[:100]}")
    except Exception as e:
        print(f"{provider} failed: {e}")
```

### Example 3: Running assessment with Binary Assessor

```python
from codejudge.core.integrated_assessor import IntegratedAssessor
from codejudge.core.llm_client import LLMFactory

# Create assessor with Gemini (cloud-based)
client = LLMFactory.create(provider="gemini", model_name="gemini-2.5-flash")

assessor = IntegratedAssessor(llm_client=client)

code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

result = assessor.assess(code=code, problem_statement="Implement fibonacci")
print(result)
```

---

## Troubleshooting

### Out of Memory (OOM) on Kaggle

Solution: The code auto-enables:
- 4-bit quantization
- Offloading to disk (`/kaggle/working/offload`)
- CPU fallback

If still OOM, try:
```python
# Manually set smaller model
from code_model_score import load_model

terminators, pipeline = load_model(
    "codellama/CodeLlama-7b-Instruct-hf",  # Smaller than Llama-3-8B
    offload_folder="/kaggle/working/offload"
)
```

### API Key Not Found

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Debug
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
```

### Model Download Stuck

Models are cached in `HF_HOME` after first download. If stuck:

```python
# Resume with custom cache
from code_model_score import load_model

load_model(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    cache_dir="/kaggle/working/hf_cache"
)
```

---

## Best Practices

### 1. **Cost Optimization (for Kaggle)**

Use **Gemini 2.5-flash** (cheapest) for initial testing, then switch to local Llama-3 for batch processing (free after download).

### 2. **Memory Optimization (for Kaggle)**

- Use 7B/8B models (fit in T4 GPU with quantization)
- Enable offload for 13B+ models
- Batch requests to reduce model loads

### 3. **Latency Optimization**

- **Local models**: Fastest (GPU inference), free
- **API models**: Medium (network latency), cheap
- **Remote Qwen**: Fastest API (China-based), cheapest

### 4. **Production Setup**

```python
# Use environment detection for auto-configuration
from code_model_score.utils import get_kaggle_env

env = get_kaggle_env()
print(f"Running on: {'Kaggle' if env['model_root'] == '/kaggle/working/model' else 'Local'}")
```

---

## Support

For issues or questions:
1. Check the [repository README](README.md)
2. Review [test files](codejudge/tests/) for examples
3. Open an issue on GitHub

---

Last updated: 2024-05-30
