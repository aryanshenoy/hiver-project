# AmazonHelp AI Support Agent — Hiver SDE Intern Take-Home

An AI support agent for AmazonHelp (built on the [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) dataset) that:
1. Classifies incoming customer messages into one of 8 intents
2. Drafts a reply grounded in how AmazonHelp has historically resolved similar issues
3. Decides whether to auto-handle or escalate to a human, with a stated reason

Full write-up: see [REPORT.md](./REPORT.md) for problem framing, results vs. baselines, failure analysis, and limitations. See [decision_log.md](./decision_log.md) for the non-obvious decisions made along the way.

## Setup

1. **Clone the repo and create a virtual environment:**
```bash
   git clone https://github.com/aryanshenoy/hiver-sde-intern-project.git
   cd hiver-sde-intern-project
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate  # Mac/Linux
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Install and run Ollama** (local LLM, used for classification, drafting, and judging):
   - Download from [ollama.com](https://ollama.com)
   - Pull the model used in this project:
```bash
     ollama pull llama3.2
```
   - Ollama runs automatically as a background service after install (no need to manually run `ollama serve` — if you see a "port already in use" message, that confirms it's already running).

4. **Data:** the raw Kaggle CSV is NOT included in this repo (too large). The pre-processed, English-filtered AmazonHelp thread data used by this project is already included at `data/amazon_english_threads.json` (~61k historical customer-reply pairs, extracted and cached from the full ~2.8M-row dataset). See `notebooks/main.ipynb` for the full data preparation pipeline (thread reconstruction, language filtering) if you want to reproduce this file from scratch.

## Reproducing the headline results (~10-15 minutes)

Run these in order:

```bash
# 1. Run the full agent pipeline on sample messages (classify → draft → decide)
python main.py

# 2. Reproduce the classifier evaluation (LLM vs. two baselines)
python evalClassify.py

# 3. Reproduce the reply-quality judge evaluation
python evalJudge.py
```

**Expected headline results:**
- Intent classifier accuracy: **~49%** (LLM) vs. ~23% (TF-IDF baseline) vs. ~9% (trivial baseline) on a 142-row held-out set
- LLM-judge vs. human agreement (on a 30-example manual check): strong on tone (73% exact match), weak on relevance/groundedness (23%/33% exact match) — see the report for what this means for trusting the judge's scores

Exact numbers may vary slightly run-to-run since `llama3.2` isn't fully deterministic even at `temperature=0`.

## Repo structure

├── main.py # Full pipeline: classify → retrieve → draft → decide
├── taxonomy.py # The 8 intent categories + definitions
├── taxonomy.md # Human-readable taxonomy doc + how it was derived
├── classify.py # LLM-based intent classifier (few-shot, Ollama)
├── baseline.py # Trivial + TF-IDF baselines
├── retrieve.py # Finds similar historical threads (TF-IDF similarity)
├── draft.py # Drafts a reply grounded in retrieved examples
├── decide.py # Auto-handle vs. escalate policy
├── judge.py # LLM-as-judge for reply quality
├── evalClassify.py # Runs classifier + baselines against golden set
├── evalJudge.py # Runs judge + saves samples for human scoring
├── data
    ├── amazon_english_threads.json # Cached, English-filtered AmazonHelp threads
├── eval
    ├── golden_set_template.csv # Intermediate scratch file — unlabeled sample before manual labeling (kept for transparency, not used by any script)
    ├── golden_set_clean.csv # Intermediate scratch file — post encoding/typo-fix 
    ├── golden_set.csv # 160 hand-labeled examples (see report for sampling method)
    ├── classification_results.csv # Per-row classifier predictions (for failure analysis)
    ├── judge_sample.csv # Judge scores + manual human scores (for agreement check)
├── notebooks
    ├── main.ipynb # Data prep: thread reconstruction, language filtering, EDA
├── decision_log.md
└── REPORT.md (or this README's Report section)


## Why AmazonHelp

Highest tweet volume in the dataset (~170k), a diverse but well-bounded set of recurring issue types (delivery, refunds, item quality, account access), and a real, documented data-quality wrinkle (multi-language support, DM-redirect resolutions) that made for an honest, non-trivial scoping exercise. Full reasoning in the decision log.

## Known limitations

- English-only scope (~75% of AmazonHelp threads)
- Single local model (`llama3.2`, ~3B params) — a frontier API model would likely score higher
- Escalation policy uses keyword matching, not full language understanding
- LLM-judge validated as reliable for tone, NOT yet reliable for relevance/groundedness

See [REPORT.md](./REPORT.md) for full problem framing, failure analysis, and what's misleading about the headline numbers.