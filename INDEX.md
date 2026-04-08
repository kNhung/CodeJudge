# 📑 CodeJudge - Documentation Index

> Hướng dẫn nhanh để tìm những gì bạn cần

---

## 🎯 I'm New to CodeJudge

**Hãy bắt đầu từ đây!**

1. **[START_HERE.md](START_HERE.md)** ⭐ 
   - Quick start: 5 phút để setup
   - 3 loại assessor được giải thích
   - Debug tips

2. **[SUMMARY.md](SUMMARY.md)**
   - Những gì đã hoàn thành
   - API overview
   - Next steps

3. **[examples.py](examples.py)**
   - 5 ví dụ chạy được
   - Test trên máy của bạn

---

## 📖 I Want to Understand the System

**Tài liệu chi tiết:**

### Architecture
- **[ROADMAP.md](ROADMAP.md)** - 4 giai đoạn phát triển
- **[README_CODEJUDGE.md](README_CODEJUDGE.md)** - Full documentation

### Components
- **Core Engine** → `codejudge/core/`
  - `llm_client.py` - LLM providers
  - `binary_assessor.py` - Yes/No scoring
  - `taxonomy_assessor.py` - 0-100 scoring
  - `prompts.py` - Prompt templates

- **Scoring** → `codejudge/scoring/`
  - `scorer.py` - Score calculation
  - Grade interpretation

### Data Structures
- Error Taxonomy (4 levels)
- Grade Scale (A-F)
- Scoring Formula

---

## 💻 I Want to Use CodeJudge

### Installation
1. **[INSTALLATION.md](INSTALLATION.md)** (15-30 phút)
   - Step-by-step setup
   - LLM provider options
   - Configuration

### Usage
2. **[README_CODEJUDGE.md](README_CODEJUDGE.md) - Usage Section**
   - 3 ways to assess code
   - LLM switching
   - Custom prompts

3. **[examples.py](examples.py)**
   - Run examples: `python examples.py`
   - Copy-paste ready code

### API Reference
4. **[README_CODEJUDGE.md](README_CODEJUDGE.md) - API Section**
   - All classes and methods
   - Parameters and returns

---

## 🧪 I Want to Test the System

### Run Tests
```bash
pytest codejudge/tests/ -v
```

### Run Examples
```bash
python examples.py
```

### Read Test Code
- **[codejudge/tests/test_core_engine.py](codejudge/tests/test_core_engine.py)**
  - 26 unit tests
  - Test all modules

---

## 🔧 I Want to Develop/Extend

### Project Structure
**[ROADMAP.md](ROADMAP.md)** - Complete structure:
```
codejudge/
├── core/           (Assessors, LLM client)
├── scoring/        (Score calculation)
├── tests/          (Unit tests)
├── backend/        (API - pending)
└── frontend/       (Web UI - pending)
```

### Development Guides
1. **Core Engine** - [README_CODEJUDGE.md](README_CODEJUDGE.md)
2. **Scoring** - [README_CODEJUDGE.md](README_CODEJUDGE.md)
3. **Testing** - [PROGRESS.md](PROGRESS.md)
4. **Web UI** - [ROADMAP.md](ROADMAP.md)

### Code Examples
- **Custom LLM**: [examples.py](examples.py) Example 4
- **Custom Prompts**: [examples.py](examples.py) + docs
- **Custom Scoring**: [codejudge/scoring/scorer.py](codejudge/scoring/scorer.py)

---

## 📊 I Want to Know Project Status

### Progress
- **[PROGRESS.md](PROGRESS.md)** ✅
  - What's done (Giai Đoạn 1-2)
  - What's pending (Giai Đoạn 3)
  - What's planned (Giai Đoạn 4)

### Summary
- **[SUMMARY.md](SUMMARY.md)** ✅
  - Completed work
  - How to use
  - Next steps

---

## 🆘 Troubleshooting & FAQs

### Setup Issues
→ **[INSTALLATION.md](INSTALLATION.md) - Troubleshooting**

### Usage Questions
→ **[START_HERE.md](START_HERE.md) - Q&A**

### API Questions
→ **[README_CODEJUDGE.md](README_CODEJUDGE.md) - API Section**

### Debug Help
→ **[INSTALLATION.md](INSTALLATION.md) - Debug Section**

---

## 📚 Full Documentation Map

```
Documentation/
├── START_HERE.md ⭐ (Quick start)
├── INSTALLATION.md (Setup & config)
├── SUMMARY.md (What's done)
├── README_CODEJUDGE.md (Full API docs)
├── ROADMAP.md (4 giai đoạn)
├── PROGRESS.md (Current status)
├── INDEX.md (This file)
│
└── Code/
    ├── codejudge/core/ (Assessors)
    ├── codejudge/scoring/ (Score calc)
    ├── codejudge/tests/ (Unit tests)
    └── examples.py (5 examples)
```

---

## 🎯 Quick Navigation by Use Case

### "I have 5 minutes"
→ [START_HERE.md](START_HERE.md)

### "I want to use it now"
→ [INSTALLATION.md](INSTALLATION.md) + [examples.py](examples.py)

### "I want to understand it"
→ [README_CODEJUDGE.md](README_CODEJUDGE.md) + [ROADMAP.md](ROADMAP.md)

### "I want to extend it"
→ [ROADMAP.md](ROADMAP.md) + [README_CODEJUDGE.md](README_CODEJUDGE.md)

### "What's done?"
→ [SUMMARY.md](SUMMARY.md) + [PROGRESS.md](PROGRESS.md)

### "I'm confused"
→ [INSTALLATION.md](INSTALLATION.md) Troubleshooting section

---

## 📋 File Descriptions

| File | Purpose | Length | For |
|------|---------|--------|-----|
| **START_HERE.md** | Quick start guide | 10 min read | Everyone |
| **INSTALLATION.md** | Setup & configuration | 20 min read | Users |
| **README_CODEJUDGE.md** | Full documentation | 30 min read | Developers |
| **ROADMAP.md** | Project roadmap | 15 min read | Planners |
| **PROGRESS.md** | Current status | 10 min read | Managers |
| **SUMMARY.md** | What's completed | 5 min read | Quick overview |
| **examples.py** | Code examples | Runnable | Learners |

---

## 🔗 External Resources

- **OpenAI API**: https://platform.openai.com/api-keys
- **Anthropic API**: https://console.anthropic.com/
- **Ollama**: https://ollama.ai
- **HumanEval-X**: In `evaluation/humaneval/`
- **CoNaLa**: In `evaluation/conala/`

---

## 💡 Tips

### First Time Users
1. Read [START_HERE.md](START_HERE.md) (10 min)
2. Setup .env from .env.example
3. Run `python examples.py`
4. Read [INSTALLATION.md](INSTALLATION.md) for details

### Developers
1. Read [ROADMAP.md](ROADMAP.md) for architecture
2. Read [README_CODEJUDGE.md](README_CODEJUDGE.md) for API
3. Check [codejudge/tests/](codejudge/tests/) for examples
4. Run `pytest` to verify setup

### Contributors
1. Check [PROGRESS.md](PROGRESS.md) for status
2. See Giai Đoạn 3-4 in [ROADMAP.md](ROADMAP.md)
3. Pick a task and start coding

---

## ⏱️ Time Investment Chart

```
Activity              Time    Document
─────────────────────────────────────────
Setup & install       5 min   INSTALLATION.md
First example         5 min   examples.py
Understand basics     15 min  START_HERE.md
Full API docs         30 min  README_CODEJUDGE.md
Architecture deep dive 20 min ROADMAP.md
─────────────────────────────────────────
Total                 75 min  All docs
```

---

## 🎓 Learning Path

### Path 1: User (Want to use CodeJudge)
```
START_HERE.md (5 min)
    ↓
INSTALLATION.md (15 min)
    ↓
examples.py (10 min)
    ↓
README_CODEJUDGE.md - Usage (10 min)
    ↓
Ready to use! 🚀
```

### Path 2: Developer (Want to understand/extend)
```
START_HERE.md (5 min)
    ↓
ROADMAP.md (15 min)
    ↓
README_CODEJUDGE.md (30 min)
    ↓
examples.py + code (20 min)
    ↓
Ready to develop! 💻
```

### Path 3: Contributor (Want to contribute)
```
All above paths (75 min)
    ↓
PROGRESS.md (10 min)
    ↓
ROADMAP.md - Giai Đoạn 3-4 (15 min)
    ↓
Pick a task and start! 💪
```

---

## 🚀 Quick Commands

```bash
# Setup
pip install -r requirements-codejudge.txt
cp .env.example .env
# Edit .env with API key

# Run examples
python examples.py

# Run tests
pytest codejudge/tests/ -v

# Debug
CODEJUDGE_LOG_LEVEL=DEBUG python examples.py

# Check installation
python -c "from codejudge import *; print('✓ OK')"
```

---

## 📞 Still Need Help?

1. **Can't install?** → [INSTALLATION.md](INSTALLATION.md) - Setup section
2. **Confused about usage?** → [START_HERE.md](START_HERE.md) - Examples
3. **API questions?** → [README_CODEJUDGE.md](README_CODEJUDGE.md) - API section
4. **Want to contribute?** → [PROGRESS.md](PROGRESS.md) - Next steps

---

## 🎉 Ready to Start?

**Choose your path:**

- 👤 New user? → [START_HERE.md](START_HERE.md)
- 💻 Developer? → [INSTALLATION.md](INSTALLATION.md)
- 📚 Learner? → [README_CODEJUDGE.md](README_CODEJUDGE.md)
- 🤝 Contributor? → [PROGRESS.md](PROGRESS.md)

---

**Last Updated**: February 19, 2026
**Version**: 1.0 (Giai Đoạn 1-2 Complete)
