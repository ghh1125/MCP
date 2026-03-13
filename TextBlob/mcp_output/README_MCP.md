# TextBlob MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps **TextBlob** to provide practical NLP capabilities for English text processing.  
It is designed for developer workflows that need simple, callable tools for:

- Tokenization (sentence/word)
- POS tagging
- Noun phrase extraction
- Sentiment analysis
- Inflection (pluralize/singularize/lemma)
- Text classification (Naive Bayes, MaxEnt, Decision Tree)
- Optional translation/language detection
- Corpora bootstrap/download helpers

Best for lightweight NLP tasks where fast integration matters more than custom deep-learning pipelines.

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ (recommended)
- `pip`
- Internet access (for first-time corpus download and optional translation)

### Install dependencies
pip install textblob nltk

### Download required corpora
python -m textblob.download_corpora  
or lighter install:  
python -m textblob.download_corpora lite

### Optional extras
- Pattern-compatible provider for pattern-based tagging/sentiment features
- Additional NLTK datasets depending on enabled tools (e.g., `punkt`, `wordnet`, `movie_reviews`)

---

## 3) Quick Start

Basic usage flow in your MCP (Model Context Protocol) host:

1. Send text to the service endpoint/tool (e.g., `analyze_text`)
2. Choose operations you need (`tokenize`, `sentiment`, `noun_phrases`, etc.)
3. Receive structured JSON outputs for downstream automation

Typical examples:
- Sentiment: input text → polarity/subjectivity
- Tokenization: input paragraph → sentence list + word tokens
- Classification: training samples + labels → model + prediction endpoint

If your host supports direct Python calls, core objects are from `textblob.blob` (`TextBlob`, `Word`, `Sentence`) and classifiers from `textblob.classifiers`.

---

## 4) Available Tools and Endpoints

Suggested endpoint/tool mapping for this service:

- `analyze_text`
  - Unified analysis: tokens, tags, noun phrases, sentiment, n-grams
- `tokenize_sentences`
  - Sentence segmentation (`sent_tokenize`)
- `tokenize_words`
  - Word tokenization (`word_tokenize`)
- `tag_pos`
  - POS tagging via English taggers
- `extract_noun_phrases`
  - NP extraction (`ConllExtractor` / `FastNPExtractor`)
- `analyze_sentiment`
  - PatternAnalyzer or NaiveBayesAnalyzer output
- `inflect_word`
  - `pluralize`, `singularize`, `lemma`
- `classify_text`
  - Run prediction with trained classifier
- `train_classifier`
  - Train NaiveBayes / MaxEnt / DecisionTree from labeled data
- `download_corpora`
  - Trigger corpus setup (`all` or `lite`)
- `translate_text` (optional, network-dependent)
  - Translation and language detection via `Translator`

---

## 5) Common Issues and Notes

- **Missing corpora errors**: run `python -m textblob.download_corpora` first.
- **Feature variability**: some analysis paths depend on optional pattern-compatible components.
- **Classification dependencies**: NLTK resources and possibly numpy/scipy stack may be needed in some environments.
- **Translation reliability**: network-backed behavior can fail due to connectivity/rate limits/provider changes.
- **Performance**: good for small-to-medium workloads; batch requests and cache repeated preprocessing in production.
- **Determinism**: NLP outputs can vary with corpus/model versions—pin dependency versions for stable results.

---

## 6) Reference Links / Documentation

- TextBlob repository: https://github.com/sloria/TextBlob
- TextBlob docs: https://textblob.readthedocs.io/
- NLTK docs: https://www.nltk.org/
- Corpora bootstrap module: `textblob.download_corpora` (run via `python -m textblob.download_corpora`)