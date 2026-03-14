# Flair MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core Flair NLP capabilities as an MCP (Model Context Protocol) service for LLM-driven workflows.

Main goals:
- Run inference for sequence labeling (NER/POS), text classification, and embedding generation
- Expose training operations (train, fine-tune, resume) in a controllable way
- Provide a low-intrusion integration point via Flair trainer services lifecycle hooks

Core Flair modules used:
- `flair.data` (Sentence/Token/Corpus/Dictionary primitives)
- `flair.models.sequence_tagger_model` (SequenceTagger)
- `flair.models.text_classification_model` (TextClassifier)
- `flair.embeddings.transformer` (Transformer embeddings)
- `flair.trainers.trainer` + `flair.trainers.services.base` (training orchestration/hooks)

---

## 2) Installation Method

Requirements (minimum):
- Python >= 3.9
- torch
- transformers
- tqdm
- numpy
- scipy
- sentencepiece
- segtok
- ftfy
- gdown
- huggingface_hub
- deprecated

Optional (feature-dependent):
- spacy, gensim, bpemb
- matplotlib, scikit-learn, tabulate
- wandb, tensorboard, clearml
- janome, langdetect, sqlitedict

Recommended setup:
1. Create a virtual environment
2. Install Flair and required runtime packages
3. Install optional packages only for features you need (logging backends, specific embeddings, language tooling)

Typical pip flow:
- `pip install flair`
- Add optional extras manually as needed (e.g., `wandb`, `tensorboard`, `clearml`)

---

## 3) Quick Start

### A. Sequence tagging inference
- Load `SequenceTagger` with `SequenceTagger.load(...)`
- Build `Sentence(...)`
- Call `predict(...)`
- Return token/span labels from `Sentence.to_dict()`

### B. Text classification inference
- Load `TextClassifier` with `TextClassifier.load(...)`
- Create `Sentence(...)` with input text
- Call `predict(...)`
- Read document labels

### C. Embedding service call
- Use `TransformerWordEmbeddings` or `TransformerDocumentEmbeddings`
- Call `embed(...)` on sentence instances
- Return embedding metadata or vectors (depending on service response policy)

### D. Training operations
- Use `ModelTrainer.train(...)`, `fine_tune(...)`, or `resume(...)`
- Attach custom trainer services through Flair’s trainer extension points for MCP (Model Context Protocol) lifecycle integration

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `health.check`
  - Validate runtime, model cache paths, and dependency readiness.

- `models.list`
  - List available local/remote model identifiers supported by the service.

- `sequence_tagger.load`
  - Load or warm a sequence tagging model.

- `sequence_tagger.predict`
  - Input: text or tokenized sentences.
  - Output: token/span labels (NER/POS/etc.), confidence if enabled.

- `text_classifier.load`
  - Load or warm a text classification model.

- `text_classifier.predict`
  - Input: sentence/document text.
  - Output: predicted class labels and scores.

- `embeddings.word`
  - Generate token-level transformer embeddings.

- `embeddings.document`
  - Generate sentence/document-level transformer embeddings.

- `training.train`
  - Start supervised training run with config.

- `training.fine_tune`
  - Fine-tune from existing checkpoint/model.

- `training.resume`
  - Resume interrupted training from checkpoint.

- `data.serialize_sentence`
  - Convert Flair Sentence to/from dict for transport-safe MCP (Model Context Protocol) payloads.

- `corpus.downsample`
  - Utility endpoint for quick dataset-size reduction in experiments.

---

## 5) Common Issues and Notes

- Version compatibility:
  - Keep `torch`, `transformers`, and Flair-compatible versions aligned.
- First-run latency:
  - Model downloads from Hugging Face can be slow; pre-warm models in production.
- Memory/performance:
  - Transformer embeddings are GPU-memory intensive; batch carefully.
- Optional dependencies:
  - Missing optional packages may disable specific features but not core inference.
- Training observability:
  - Logging integrations (W&B/TensorBoard/ClearML) require separate installation and credentials.
- Intrusiveness/risk:
  - Integration risk is low; import feasibility is high (~0.94), with medium overall complexity.

---

## 6) Reference Links / Documentation

- Flair repository: https://github.com/flairNLP/flair
- Flair docs/tutorials (in repo): `docs/tutorial/*`
- Trainer and extension points:
  - `flair.trainers.trainer`
  - `flair.trainers.services.base`
- Core model/data APIs:
  - `flair.data`
  - `flair.models.sequence_tagger_model`
  - `flair.models.text_classification_model`
  - `flair.embeddings.transformer`