# Walkthrough notes (historical)

Primary setup and usage docs live in [README.md](README.md).

This file keeps a short record of the multi-agent migration and a thesis comparison snapshot.

## Multi-agent flow (current)

Compiler syntax → Agent 1 (factors) → Agent 2 (per-factor grades) → score + suggestions.

Implemented in:

- `codeeval/core/compiler_helper.py`
- `codeeval/core/multi_agent_assessor.py`
- `app.py`
- `evaluation/hcmus/score_with_multi_agent.py`
- `evaluation/conala/score_conala_multi_agent.py`

## Tests

```bash
conda activate codeeval
pytest codeeval/tests/ -v
```

## Live smoke (needs API key)

```bash
conda activate codeeval
python evaluation/hcmus/score_with_multi_agent.py \
  --limit 1 --provider gemini --model gemini-2.5-flash
```

## Thesis baseline note

Earlier experiments compared multi-agent against a taxonomy-based assessor on HCMUS (142 samples). Taxonomy codepaths were removed from this branch; keep metric tables in `evaluation/metrics_summary.md` / thesis writeups for reference only.
