# dedupe MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `dedupe` Python library as an MCP (Model Context Protocol) service for entity resolution tasks:

- **Deduplication**: find duplicate records within one dataset
- **Record linkage**: match records across two datasets
- **Gazetteer matching**: match messy input records against a canonical reference set

Core runtime API is based on `dedupe.api` classes:

- `Dedupe`, `StaticDedupe`
- `RecordLink`, `StaticRecordLink`
- `Gazetteer`, `StaticGazetteer`

Typical workflow: define fields → sample/label training pairs → train model → persist settings → run match/link queries.

---

## 2) Installation Method

### Requirements

- Python (modern 3.x environment recommended)
- Native/scientific dependencies required by `dedupe`

Key runtime dependencies (from repository analysis):

- `affinegap`
- `categorical-distance`
- `doublemetaphone`
- `highered`
- `numpy`
- `simplecosine`
- `haversine`
- `BTrees`
- `zope.index`
- `dedupe-Levenshtein-search`

### Install

- `pip install dedupe`
- or for local development: clone repo, then `pip install -e .`

If installation fails, upgrade build tooling first:

- `pip install --upgrade pip setuptools wheel`

---

## 3) Quick Start

### Minimal service flow

1. Prepare records as `{record_id: {field_name: value, ...}}`
2. Define variable schema (for example `String`, `Exact`, `Exists`, etc.)
3. Create `Dedupe` (or `RecordLink`/`Gazetteer`) instance
4. Run sampling + labeling
5. Train model
6. Save settings/training with serializer helpers
7. Use `Static*` classes for fast production inference

### Example (conceptual)

- Initialize model with fields from `dedupe.variables`
- Call training-data helpers from `dedupe.convenience` if needed
- Persist artifacts via:
  - `write_training` / `read_training`
  - `write_settings` / `read_settings`
- In production, load `StaticDedupe` or `StaticRecordLink` from saved settings and run matching calls

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- **`health_check`**  
  Returns service status and dependency readiness.

- **`create_model`**  
  Input: mode (`dedupe` | `record_link` | `gazetteer`), field definitions.  
  Output: model/session identifier.

- **`prepare_training_data`**  
  Input: records (single or paired datasets), optional strategy.  
  Output: candidate pairs for labeling.

- **`label_pairs`**  
  Input: labeled match/distinct examples.  
  Output: updated training state.

- **`train_model`**  
  Trains current model state.  
  Output: training summary and model-ready flag.

- **`save_artifacts`**  
  Persists settings/training data (serializer-backed).  
  Output: artifact paths/IDs.

- **`load_static_model`**  
  Loads saved settings into `StaticDedupe` / `StaticRecordLink` / `StaticGazetteer`.  
  Output: inference handle.

- **`match_records`**  
  For deduplication within one dataset.  
  Output: clusters/pairs with confidence scores.

- **`link_records`**  
  For cross-dataset record linkage.  
  Output: matched pairs with scores.

- **`gazetteer_search`**  
  Matches incoming records to canonical reference entries.  
  Output: ranked candidates.

- **`explain_model_config`**  
  Returns active variable schema and persisted model metadata.

---

## 5) Common Issues and Notes

- **No built-in CLI detected**: this repo is primarily a Python library; MCP (Model Context Protocol) service should expose its own endpoints.
- **Dependency friction**: some packages may need system build tools; use clean virtual environments.
- **State persistence is important**: store settings/training artifacts to avoid retraining every startup.
- **Performance**:
  - blocking/indexing helps scale; use high-level API rather than internal modules
  - large datasets may require batch processing and memory-aware deployment
- **Schema quality matters**: choosing correct variable types (`String`, `Set`, `Price`, `LatLong`, etc.) strongly impacts match quality.
- **Interactive labeling**: useful for quality, but for automation you may pre-generate labeled examples and feed them programmatically.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/dedupeio/dedupe
- Main README: https://github.com/dedupeio/dedupe/blob/master/README.md
- Changelog: https://github.com/dedupeio/dedupe/blob/master/CHANGELOG.md
- Package modules of interest:
  - `dedupe.api`
  - `dedupe.convenience`
  - `dedupe.serializer`
  - `dedupe.variables`
- Docs config present in repo (`docs/`), plus ReadTheDocs configuration (`.readthedocs.yml`) for extended documentation builds.