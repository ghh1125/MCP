# spaCy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core spaCy capabilities as MCP (Model Context Protocol) tools so LLM clients can run NLP tasks programmatically.

Main capabilities:
- Load/initialize pipelines (`spacy.load`, `spacy.blank`)
- Text processing with `Doc`, `Token`, `Span`
- Rule-based matching (`Matcher`, `PhraseMatcher`, `DependencyMatcher`)
- Training/evaluation utilities (config, train, evaluate, convert)
- Environment/model diagnostics (info, validate, debug-* commands)

Repository: https://github.com/explosion/spaCy

---

## 2) Installation Method

### Requirements
- Python >= 3.8
- Core deps include: `numpy`, `thinc`, `pydantic`, `cymem`, `preshed`, `murmurhash`, `srsly`, `wasabi`, `catalogue`, `typer`, `tqdm`, `requests`, `jinja2`, `packaging`, `langcodes`

### Install
- `pip install -U spacy`
- Optional GPU: install CuPy variant compatible with your CUDA setup, then use spaCy GPU selection APIs
- Optional language/model extras as needed (e.g., Japanese, Russian/Ukrainian lemmatization ecosystems)

### Install a model
- `python -m spacy download en_core_web_sm`

---

## 3) Quick Start

### Basic NLP flow
- Load model with `spacy.load("en_core_web_sm")`
- Process text: `doc = nlp("Apple is looking at buying a startup in the UK.")`
- Access entities/tokens/sentences from `doc`

### Minimal service-facing operations
- `load_pipeline(model_name)` → initializes `Language`
- `process_text(text)` → returns tokens, lemmas, POS, entities, dependencies (depending on pipeline)
- `match_patterns(text, patterns)` → rule-based extraction
- `pipeline_info()` → version/model/environment metadata

### Training lifecycle (service orchestration)
- `init_config` → generate starter config
- `convert` → convert data format
- `train` → fit pipeline
- `evaluate` → score trained pipeline
- `package` → build distributable model package

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `nlp.load`
  - Load a spaCy pipeline or create blank language pipeline.
- `nlp.process`
  - Run full pipeline over text and return structured annotations.
- `nlp.explain`
  - Explain tag/label abbreviations via spaCy glossary.
- `nlp.match`
  - Run token-based/phrase/dependency matchers.
- `nlp.info`
  - Return spaCy version, installed pipelines, runtime details.
- `nlp.validate`
  - Check installed model/package compatibility.
- `train.init_config`
  - Generate baseline training config.
- `train.convert`
  - Convert external annotation files to spaCy-friendly formats.
- `train.run`
  - Train model from config.
- `train.evaluate`
  - Evaluate model against dev/test data.
- `train.debug_data`
  - Detect label/data quality issues.
- `train.debug_config`
  - Inspect resolved config and overrides.
- `train.debug_model`
  - Inspect architecture behavior.
- `model.package`
  - Build installable Python package for trained pipeline.
- `runtime.prefer_gpu` / `runtime.require_gpu`
  - Configure GPU usage behavior.

---

## 5) Common Issues and Notes

- Model not found:
  - Install language model separately (e.g., `python -m spacy download en_core_web_sm`).
- Version mismatch:
  - Run validate endpoint; align spaCy and model versions.
- GPU problems:
  - Ensure CUDA/CuPy compatibility; fallback to CPU if unavailable.
- Language-specific tokenization:
  - Some languages require extra tokenizer packages/dictionaries.
- Performance:
  - Reuse loaded `nlp` object (avoid reloading per request).
  - Use batch processing for high throughput.
  - Disable unused pipeline components for speed.
- Training quality:
  - Use `debug-data` early; many failures come from annotation inconsistencies.

---

## 6) Reference Links and Documentation

- spaCy repository: https://github.com/explosion/spaCy
- spaCy documentation: https://spacy.io/usage
- API reference: https://spacy.io/api
- CLI reference: https://spacy.io/api/cli
- Training guide: https://spacy.io/usage/training
- Models overview: https://spacy.io/models