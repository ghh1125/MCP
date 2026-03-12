# NLTK MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository provides an MCP (Model Context Protocol) service wrapper around **NLTK** (Natural Language Toolkit), enabling LLM agents and developer tools to access practical NLP capabilities through structured service calls.

Core capabilities include:
- Tokenization (`word_tokenize`, `sent_tokenize`)
- POS tagging (`pos_tag`)
- N-grams and text utilities
- Stemming and lemmatization
- Sentiment analysis (VADER)
- WordNet lookup and similarity
- Corpus/data download management (`nltk.downloader`)

This MCP (Model Context Protocol) service is best suited for lightweight NLP preprocessing, linguistic analysis workflows, and educational/research tasks.

---

## 2) Installation Method

### Requirements
- Python `>=3.8`
- Required packages: `click`, `joblib`, `regex`, `tqdm`
- Optional (feature-dependent): `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `twython`, `gensim`, `networkx`, `pandas`

### Install
pip install nltk click joblib regex tqdm

### Recommended: install common NLTK data
python -m nltk.downloader punkt averaged_perceptron_tagger wordnet omw-1.4 vader_lexicon

---

## 3) Quick Start

### Basic Python usage
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag

text = "NLTK is a leading platform for NLP."
tokens = word_tokenize(text)
sentences = sent_tokenize(text)
tags = pos_tag(tokens)

print(tokens)
print(sentences)
print(tags)

### Run downloader CLI
python -m nltk.downloader

### Typical MCP (Model Context Protocol) flow
1. Client calls tokenization/tagging/sentiment service.
2. Service validates input and language/resource requirements.
3. Service executes NLTK function and returns structured JSON.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `tokenize.word`
  - Split text into word tokens.
  - Backed by `nltk.tokenize.word_tokenize`.

- `tokenize.sentence`
  - Split text into sentences.
  - Backed by `nltk.tokenize.sent_tokenize`.

- `tag.pos`
  - Part-of-speech tagging for token lists.
  - Backed by `nltk.pos_tag`.

- `stem.porter`
  - Porter stemming for tokens.
  - Backed by `nltk.stem.PorterStemmer`.

- `lemma.wordnet`
  - Lemmatize words with WordNet.
  - Backed by `nltk.stem.WordNetLemmatizer`.

- `sentiment.vader`
  - Sentiment polarity scores for text.
  - Backed by `nltk.sentiment.vader.SentimentIntensityAnalyzer`.

- `wordnet.lookup`
  - Synsets, definitions, lemmas, and relation lookup.
  - Backed by `nltk.corpus.wordnet`.

- `ngrams.generate`
  - Build n-grams from token sequences.
  - Backed by `nltk.util.ngrams`.

- `data.download`
  - Download/check NLTK datasets/models.
  - Backed by `nltk.downloader.Downloader` or `python -m nltk.downloader`.

- `health.check`
  - Verify runtime + required corpora availability.

---

## 5) Common Issues and Notes

- Missing resource errors (`LookupError`) are common.
  - Fix by downloading required packages via `python -m nltk.downloader <resource>`.

- First run may be slower due to corpus/model downloads.

- Some modules require optional dependencies (e.g., `scikit-learn`, `numpy`, `matplotlib`).

- Java-dependent integrations (e.g., some parser/tagger wrappers) need local Java binaries and model paths.

- For server deployments:
  - Pre-download corpora into a shared `NLTK_DATA` path.
  - Pin package versions for reproducibility.
  - Avoid loading large corpora on every request (cache where possible).

---

## 6) Reference Links / Documentation

- NLTK Repository: https://github.com/nltk/nltk
- NLTK Official Docs: https://www.nltk.org/
- NLTK Data Guide: https://www.nltk.org/data.html
- NLTK API Reference: https://www.nltk.org/api/nltk.html
- Downloader module usage: `python -m nltk.downloader`