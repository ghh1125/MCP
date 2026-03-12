# vaderSentiment MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the `vaderSentiment` library to provide fast, rule-based sentiment analysis for short to medium English text (e.g., chat, social posts, reviews).

Main capabilities:
- Polarity scoring: `positive`, `neutral`, `negative`, and `compound`
- Handles emphasis patterns (ALL CAPS, punctuation like `!!!`, `??`)
- Includes slang/idiom and emoji-aware lexicon behavior from VADER resources

Core runtime module: `vaderSentiment/vaderSentiment.py`  
Primary class: `SentimentIntensityAnalyzer`

---

## 2) Installation Method

### Requirements
- Python 3.8+ recommended
- No external runtime dependencies beyond Python standard library

### Install from PyPI
pip install vaderSentiment

### Install from source
1. Clone repository:
   `https://github.com/cjhutto/vaderSentiment`
2. Install:
   `pip install .`

### MCP (Model Context Protocol) service integration
In your MCP (Model Context Protocol) host, register this service as an import-based Python service that initializes one shared `SentimentIntensityAnalyzer` instance for request handling.

---

## 3) Quick Start

### Basic usage flow
1. Create analyzer instance
2. Call polarity scoring on input text
3. Return JSON-like score object

Example call pattern:
- Input: `"VADER is smart, handsome, and funny!"`
- Output fields:
  - `neg`: negative ratio
  - `neu`: neutral ratio
  - `pos`: positive ratio
  - `compound`: normalized aggregate score in `[-1, 1]`

Suggested interpretation:
- `compound >= 0.05` → positive
- `compound <= -0.05` → negative
- otherwise → neutral

For MCP (Model Context Protocol), expose this as a simple text-in / score-out endpoint.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `analyze_sentiment`
  - Purpose: Score one text string with VADER
  - Input: `text` (string)
  - Output: `{neg, neu, pos, compound}`

- `analyze_batch`
  - Purpose: Score multiple texts in one request
  - Input: `texts` (string array)
  - Output: list of `{neg, neu, pos, compound}` in input order

- `health_check`
  - Purpose: Verify service readiness
  - Output: status + analyzer initialization state

- `service_info`
  - Purpose: Return version and model metadata
  - Output: library version, lexicon availability, runtime info

---

## 5) Common Issues and Notes

- English-focused heuristics: results may degrade on non-English text.
- Lexicon files required at runtime:
  - `vader_lexicon.txt`
  - `emoji_utf8_lexicon.txt`
- Packaging note: analysis detected setup metadata files in repo; ensure your deployment includes resource files.
- Performance: lightweight and fast for real-time calls; reuse analyzer instance instead of recreating per request.
- Input limits: for very large documents, chunking is recommended.
- Determinism: rule-based engine (non-LLM), outputs are stable for identical input.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/cjhutto/vaderSentiment
- Core implementation: `vaderSentiment/vaderSentiment.py`
- License: `LICENSE.txt`
- Original package name: `vaderSentiment`