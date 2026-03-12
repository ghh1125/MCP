# TextBlob MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps **TextBlob** to provide practical NLP capabilities over text input, including:

- Tokenization (words/sentences)
- POS tagging
- Noun phrase extraction
- Sentiment analysis
- Spelling correction and inflection helpers
- N-grams
- Text classification (NLTK-backed)
- Optional language detection/translation (network-dependent)

It is designed for lightweight, developer-friendly NLP workflows with a simple Python integration path.

---

## 2) Installation Method

### Requirements

- Python 3.x
- `textblob`
- `nltk` (required backend resources)
- Optional: pattern-compatible runtime for some sentiment behavior
- Internet access (for corpora download and translation/detection features)

### Install

pip install textblob nltk

Download required corpora (recommended):

python -m textblob.download_corpora

Lite download (smaller footprint, fewer resources):

python -c "from textblob.download_corpora import download_lite; download_lite()"

---

## 3) Quick Start

Create a basic analysis flow in your MCP (Model Context Protocol) service handler:

from textblob import TextBlob

text = "TextBlob is easy to use. It gives useful NLP features quickly."
blob = TextBlob(text)

# Core NLP
words = blob.words
sentences = blob.sentences
tags = blob.tags
noun_phrases = blob.noun_phrases
sentiment = blob.sentiment

# Extras
ngrams = blob.ngrams(2)
corrected = blob.correct()

For classification:

from textblob.classifiers import NaiveBayesClassifier

train = [
    ("I love this product", "pos"),
    ("This is terrible", "neg"),
]
cl = NaiveBayesClassifier(train)
label = cl.classify("I love it")

For translation/detection (network-dependent):

from textblob import TextBlob
b = TextBlob("Bonjour tout le monde")
lang = b.detect_language()
en_text = b.translate(to="en")

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `analyze_text`
  - Input: raw text
  - Output: tokens, sentences, tags, noun phrases, sentiment, n-grams

- `sentiment_analyze`
  - Input: text, analyzer type (`pattern` or `naive_bayes`)
  - Output: polarity/subjectivity or classifier sentiment result

- `tokenize`
  - Input: text, mode (`word`/`sentence`)
  - Output: token list

- `pos_tag`
  - Input: text
  - Output: `(token, tag)` pairs

- `extract_noun_phrases`
  - Input: text, extractor (`fast`/`conll`)
  - Output: noun phrase list

- `classify_text`
  - Input: text, model id
  - Output: predicted label (+ optional confidence/probability)

- `train_classifier`
  - Input: labeled samples, classifier type (`naive_bayes`, `maxent`, `decision_tree`, etc.)
  - Output: model id / training summary

- `correct_spelling`
  - Input: text
  - Output: corrected text suggestion

- `translate_text`
  - Input: text, target language
  - Output: translated text (requires network)

- `detect_language`
  - Input: text
  - Output: language code (requires network)

- `download_corpora`
  - Input: mode (`lite`/`all`)
  - Output: download status

---

## 5) Common Issues and Notes

- Missing corpora errors (`LookupError`): run `python -m textblob.download_corpora`.
- First-run latency: corpus download and model initialization can be slow.
- Translation/detection reliability depends on external network/services.
- Classifier quality depends heavily on training data balance and size.
- Pattern-related behavior may vary by environment/runtime compatibility.
- For production MCP (Model Context Protocol) services:
  - Cache loaded models/resources.
  - Validate/limit input size.
  - Add timeouts for network-dependent operations.
  - Return structured errors for missing corpora or unsupported languages.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/sloria/TextBlob
- TextBlob docs: https://textblob.readthedocs.io/
- Corpora downloader module: `textblob.download_corpora`
- NLTK docs: https://www.nltk.org/