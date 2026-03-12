# Flair MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core Flair NLP capabilities for model-assisted workflows, including:

- Sequence labeling (NER, POS, chunking) via `SequenceTagger`
- Text/document classification via `TextClassifier`
- Embedding generation (word, Flair, transformer, stacked embeddings)
- Dataset loading for sequence labeling (e.g., `ColumnCorpus`)
- Training orchestration via `ModelTrainer`
- Extensible training hooks via trainer services (renamed from plugins)

It is designed for developers who want a practical interface to run inference, training, and embedding operations through an MCP (Model Context Protocol)-style service layer.

---

## 2) Installation Method

### Requirements

Core runtime dependencies include:

- `torch`
- `transformers`
- `tqdm`
- `numpy`
- `scikit-learn`
- `deprecated`
- `segtok`
- `matplotlib`
- `janome`
- `langdetect`
- `lxml`
- `gdown`
- `sqlitedict`
- `mpld3`

Optional (feature-specific): `sentencepiece`, `sacremoses`, `ftfy`, `boto3`, `gensim`, `bpemb`, `wandb`, `tensorboard`, `clearml`.

### Install

- Install Flair from source repository or PyPI (recommended for stable usage).
- Then install optional extras only if needed (e.g., experiment tracking or specific tokenizers).

Typical flow:
- create virtual environment
- install PyTorch matching your CUDA/CPU setup
- install Flair
- install optional packages as needed

---

## 3) Quick Start

### Basic inference flow

1. Create `Sentence` objects (`flair.data.Sentence`)
2. Load a pretrained model (`SequenceTagger` or `TextClassifier`)
3. Run prediction
4. Read labels/spans/tokens from the enriched sentence/document objects

### Typical training flow

1. Load corpus (e.g., `ColumnCorpus` for sequence labeling data)
2. Define embeddings (`WordEmbeddings`, `FlairEmbeddings`, or transformer embeddings)
3. Build model (`SequenceTagger` / `TextClassifier`)
4. Train with `ModelTrainer`
5. Optionally attach trainer services for logging/checkpoint/scheduling behaviors

### Example scripts in repository

- `examples/ner/run_ner.py` (NER workflow)
- `examples/multi_gpu/run_multi_gpu.py` (multi-GPU training workflow)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoints for this service:

- `health`
  - Service health/status check.

- `models.list`
  - List available/registered Flair model families and pretrained aliases.

- `models.load`
  - Load a model into memory (e.g., sequence tagger, text classifier).

- `inference.sequence_tag`
  - Run token-level tagging (NER/POS/chunking) using `SequenceTagger`.

- `inference.classify_text`
  - Run text/document classification using `TextClassifier`.

- `embeddings.encode_tokens`
  - Generate token embeddings (word/flair/transformer).

- `embeddings.encode_document`
  - Generate document embeddings (transformer document embeddings, etc.).

- `datasets.load_column_corpus`
  - Load custom sequence-labeling datasets from column format.

- `training.start`
  - Start model training via `ModelTrainer`.

- `training.status`
  - Retrieve training progress/metrics.

- `training.stop`
  - Gracefully stop training job.

- `training.services.configure`
  - Configure trainer services (logging, scheduler, checkpoints, tracking).

- `artifacts.list`
  - List produced artifacts (models, logs, checkpoints).

- `artifacts.get`
  - Retrieve specific artifact metadata/path/reference.

---

## 5) Common Issues and Notes

- PyTorch compatibility:
  - Always match Torch build with your CUDA runtime; many runtime failures come from mismatch.

- Transformer-heavy pipelines:
  - Expect high memory usage. Use smaller models, shorter max sequence length, or batch-size tuning.

- Tokenization differences:
  - Prediction quality can vary if inference tokenization differs from training setup.

- Optional dependency gaps:
  - Missing optional libraries may disable specific embedding/model features.

- Multi-GPU:
  - Use provided example as baseline; confirm distributed environment variables and NCCL setup.

- Reproducibility:
  - Pin library versions and random seeds; behavior may vary across transformer/torch versions.

- Service extensibility:
  - Prefer trainer services for customization instead of editing core training loops.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/flairNLP/flair
- Main docs/tutorials: `docs/tutorial/`
- Core modules:
  - `flair.data`
  - `flair.models.sequence_tagger_model`
  - `flair.models.text_classification_model`
  - `flair.embeddings.token`
  - `flair.embeddings.transformer`
  - `flair.trainers.trainer`
  - `flair.trainers.services.base` (conceptual rename from plugin base)
  - `flair.datasets.sequence_labeling`
- Example workflows:
  - `examples/ner/run_ner.py`
  - `examples/multi_gpu/run_multi_gpu.py`

If you want, I can also provide a ready-to-use MCP (Model Context Protocol) service contract (JSON schema-style endpoint I/O) for these endpoints.