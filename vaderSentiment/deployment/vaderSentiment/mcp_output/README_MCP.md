# vaderSentiment MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **VADER Sentiment** for fast, rule-based sentiment scoring of short text (social posts, comments, messages, headlines, etc.).  
It provides a lightweight MCP (Model Context Protocol) service interface around the core `SentimentIntensityAnalyzer` so clients can submit text and receive polarity scores:

- `neg` (negative)
- `neu` (neutral)
- `pos` (positive)
- `compound` (normalized overall sentiment, `-1` to `1`)

Best fit: real-time sentiment enrichment, moderation pipelines, analytics preprocessing, and simple text scoring without heavy ML dependencies.

---

## 2) Installation Method

### Requirements
- Python 3.8+ recommended
- No external runtime dependencies required (stdlib-based core)

### Install from source
1. Clone repository:
   - `git clone https://github.com/cjhutto/vaderSentiment.git`
2. Install:
   - `pip install .`
   - or editable mode: `pip install -e .`

### Verify import
- `from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer`

---

## 3) Quick Start

### Basic sentiment scoring flow
1. Initialize analyzer once.
2. Call polarity scoring for each input text.
3. Return JSON-like MCP (Model Context Protocol) response payload.

Example usage logic:
- Create `SentimentIntensityAnalyzer()`
- Run `polarity_scores("VADER is very smart, handsome, and funny.")`
- Return scores to caller

Expected output shape:
- `{"neg": 0.xx, "neu": 0.xx, "pos": 0.xx, "compound": 0.xx}`

### Typical service behavior
- Input: raw text string
- Output: sentiment score object
- Optional: batch handling by iterating over an array of texts and returning per-item results

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service tools/endpoints for this repository:

- `analyze_sentiment`
  - Purpose: score one text input
  - Input: `text: string`
  - Output: `neg, neu, pos, compound`

- `analyze_sentiment_batch`
  - Purpose: score multiple texts in one request
  - Input: `texts: string[]`
  - Output: array of sentiment score objects in input order

- `health_check`
  - Purpose: service readiness/liveness check
  - Input: none
  - Output: status and version info

- `service_info`
  - Purpose: expose analyzer/service metadata
  - Input: none
  - Output: model name (`VADER`), lexicon presence, runtime version

Notes:
- Repository has no built-in CLI entry points discovered.
- Core implementation is in `vaderSentiment/vaderSentiment.py`.
- Lexicons used:
  - `vaderSentiment/vader_lexicon.txt`
  - `vaderSentiment/emoji_utf8_lexicon.txt`

---

## 5) Common Issues and Notes

- **Lexicon files must be packaged correctly**  
  Ensure both lexicon files are available in runtime environment; missing files will break analyzer initialization.

- **Text domain limitations**  
  VADER is optimized for social/media-style English text and may underperform on domain-specific jargon or multilingual input.

- **Throughput tips**  
  Reuse a single `SentimentIntensityAnalyzer` instance instead of recreating per request.

- **Interpretation caution**  
  `compound` is useful as a single score, but thresholding should be tuned for your application.

- **Environment/setup**  
  This project provides `setup.py` and `setup.cfg`; no `requirements.txt` or `pyproject.toml` detected.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/cjhutto/vaderSentiment
- License: `LICENSE.txt` in repository root
- Core module: `vaderSentiment/vaderSentiment.py`
- Packaging config: `setup.py`, `setup.cfg`
- Lexicons:
  - `vaderSentiment/vader_lexicon.txt`
  - `vaderSentiment/emoji_utf8_lexicon.txt`