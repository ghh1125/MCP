# Stanza MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps Stanford **Stanza** to provide production-friendly NLP capabilities over a service interface.

Main functions:
- Multilingual NLP pipelines (tokenization, POS, lemma, dependency parse, NER, sentiment, constituency, coref depending on models/language)
- Model/resource download and management
- Optional CoreNLP-backed server features (Semgrex / Ssurgeon / Tsurgeon / TokensRegex workflows)

This service is ideal when you want LLM tools to call robust NLP processing as reusable MCP (Model Context Protocol) services.

---

## 2) Installation Method

### Requirements
- Python >= 3.8
- Core deps: `torch`, `numpy`, `requests`, `tqdm`, `protobuf`
- Optional deps (feature-based): `transformers`, `sentencepiece`, `peft`, `spacy`, `jieba`, `pythainlp`, `sudachipy`, `matplotlib`, `streamlit`

### Install
- `pip install stanza`
- If building from source repo:
  - `pip install -e .`

### Download language models
- In Python: `stanza.download('en')` (replace `en` as needed)

---

## 3) Quick Start

### Basic pipeline usage
- Create a pipeline with processors (example: tokenize + POS + lemma + depparse + NER)
- Run text through pipeline
- Return structured document output (sentences, tokens, entities, dependencies)

Typical flow:
1. Initialize once at service startup
2. Reuse pipeline instances per language for performance
3. Expose MCP (Model Context Protocol) tools that accept text + language + processor options

### Optional server mode
- Launch server module: `python -m stanza.server.main`
- Use when integrating Java/CoreNLP-related annotation workflows

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `pipeline.annotate`
  - Run configurable Stanza pipeline on input text
  - Inputs: `text`, `lang`, `processors`, optional `package/model_dir`
  - Output: token/sentence/linguistic annotations

- `pipeline.multilingual_annotate`
  - Auto-handle mixed-language or language-routing workflows
  - Useful when upstream language is unknown

- `resources.download`
  - Download required models/resources for language and processors
  - Wraps Stanza resource management functions

- `resources.list_languages`
  - List available languages/resources from local cache or remote index

- `server.annotate` (optional)
  - Bridge to `stanza.server` features when CoreNLP-compatible behavior is needed

- `server.semgrex` / `server.ssurgeon` / `server.tsurgeon` (optional advanced)
  - Dependency/tree pattern search and rewrite operations for expert workflows

- `health.check`
  - Runtime health, model cache readiness, dependency checks

---

## 5) Common Issues and Notes

- **First-run latency**: model download can be large; pre-download in deployment image.
- **PyTorch/CUDA**: ensure Torch build matches your CUDA/CPU environment.
- **Language coverage differs by processor**: not all processors are available for all languages/packages.
- **Memory usage**: constituency/coref/transformer pipelines can be heavy; prefer pooled, reused pipeline objects.
- **Optional tokenizer integrations** (`jieba`, `pythainlp`, `sudachipy`, `spacy`) require extra installs.
- **Java-dependent server utilities** may require proper Java/classpath setup.
- **No requirements.txt in repo root**: rely on `setup.py` metadata and feature-based extras in your service deployment config.

---

## 6) Reference Links / Documentation

- Stanza repository: https://github.com/stanfordnlp/stanza
- Stanza main README/docs: https://github.com/stanfordnlp/stanza/blob/main/README.md
- Stanford NLP site: https://stanfordnlp.github.io/stanza/
- CoreNLP (if using server-side Java features): https://stanfordnlp.github.io/CoreNLP/