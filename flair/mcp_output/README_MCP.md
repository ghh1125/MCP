# Flair MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the **Flair NLP library** as an MCP (Model Context Protocol) inference layer for practical NLP workflows.

Main capabilities:
- Named Entity Recognition (NER), POS tagging, chunking via `SequenceTagger`
- Text classification/sentiment/topic labeling via `TextClassifier`
- Few-shot/zero-shot style labeling via `TARSClassifier` / `TARSTagger`
- Sentence/document embedding generation via Flair and Transformer embedding backends
- Optional training observability hooks through Flair trainer services

This README is focused on **developer-oriented integration** for inference-first MCP (Model Context Protocol) usage.

---

## 2) Installation Method

### Requirements
- Python >= 3.8
- PyTorch
- Core libraries: `transformers`, `numpy`, `scipy`, `tqdm`, `requests`, `segtok`, `gensim`, etc.

### Install (recommended)
- `pip install flair`

### Install from source
- `git clone https://github.com/flairNLP/flair.git`
- `cd flair`
- `pip install -e .`

### Optional extras (as needed)
- `sentence-transformers`, `spacy`, `nltk`, `scikit-learn`
- Logging/experiment tools: `wandb`, `tensorboard`, `clearml`

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Start MCP (Model Context Protocol) server process exposing Flair-backed tools.
2. Client sends text input to endpoint (e.g., NER/classification/embedding).
3. Service converts text into Flair `Sentence`, runs model inference, returns structured JSON.

### Minimal usage examples (logical calls)
- `tag_entities(text, model="ner")` → entities with spans and labels
- `classify_text(text, model="sentiment")` → label + confidence
- `embed_text(text, model="transformer")` → vector output
- `tars_predict(text, labels=[...])` → zero/few-shot predictions

### Local script references
- `python -m source.examples.ner.run_ner`
- `python -m source.examples.multi_gpu.run_multi_gpu`

(These are example workflows, not a stable formal CLI.)

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) endpoint surface:

- **health**
  - Basic readiness/liveness check and model cache status.

- **tag_entities**
  - NER/POS/chunk tagging using `SequenceTagger`.
  - Input: text, model name/path, optional batch params.
  - Output: token/spans, labels, confidence.

- **classify_text**
  - Text classification with `TextClassifier`.
  - Input: text, model name/path.
  - Output: class labels + scores.

- **tars_predict**
  - Few-shot/zero-shot tagging/classification using TARS models.
  - Input: text, candidate labels, task type.
  - Output: ranked labels and scores.

- **embed_text**
  - Sentence/document embedding generation.
  - Input: text, embedding backend.
  - Output: dense vector(s), optional metadata.

- **batch_infer**
  - Batched wrapper over tagging/classification/embedding for throughput.

- **model_info**
  - Loaded model metadata, device info, supported tasks.

- **trainer_events** (optional)
  - Training-time telemetry via Flair trainer services hooks.

---

## 5) Common Issues and Notes

- **Model download latency**: First run may be slow due to checkpoint download.
- **GPU/CPU mismatch**: Ensure PyTorch CUDA build matches your environment.
- **Memory pressure**: Transformer embeddings are heavy; use batching and max-length limits.
- **Tokenization differences**: Outputs vary by tokenizer/model; keep model versions pinned.
- **Optional dependencies**: Some features fail silently without extras (e.g., sentence-transformers, logging backends).
- **Production tip**: Preload models at startup and reuse instances to reduce per-request latency.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/flairNLP/flair
- Main docs/tutorials: `docs/tutorial/`
- Core API areas:
  - `flair/data.py` (Sentence/Token/Corpus/Dictionary)
  - `flair/models/sequence_tagger_model.py`
  - `flair/models/text_classification_model.py`
  - `flair/models/tars_model.py`
  - `flair/embeddings/token.py`, `flair/embeddings/document.py`
- Examples:
  - `examples/ner/README.md`
  - `examples/multi_gpu/README.md`