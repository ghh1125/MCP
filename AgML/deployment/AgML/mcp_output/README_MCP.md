# AgML MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service provides a thin, low-intrusion MCP (Model Context Protocol) layer over the AgML Python API for agricultural ML workflows.  
It focuses on safe, practical developer operations first:

- Discover public datasets
- Inspect dataset metadata/splits/tasks
- Validate dataset names before downloads
- Instantiate loaders and inspect sample batches
- Optionally export datasets (e.g., YOLO / TensorFlow formats)
- Optionally discover model wrappers (classification/detection/segmentation)

Recommended approach: metadata-first, read-only by default, with explicit opt-in for network/filesystem writes.

---

## 2) Installation Method

### Prerequisites

- Python 3.9+ (recommended)
- pip
- Optional: CUDA-enabled PyTorch/TensorFlow if using model/inference paths

### Base dependencies (lightweight)

- numpy
- Pillow
- requests
- tqdm
- PyYAML

### Optional dependencies (feature-gated)

- torch, torchvision
- tensorflow
- opencv-python
- matplotlib
- albumentations
- ultralytics
- pytorch-lightning

### Install commands

- Install AgML from PyPI:
  pip install agml

- Or install from source:
  git clone https://github.com/Project-AgML/AgML.git  
  cd AgML  
  pip install -e .

- Optional extras should be installed only when needed for specific tools/endpoints (e.g., model inference/training/export).

---

## 3) Quick Start

### Typical service flow

1. `list_public_datasets` to discover available datasets  
2. `validate_dataset_name` before any costly operation  
3. `get_dataset_metadata` and `show_dataset_splits` for planning  
4. `instantiate_loader` for local workflow execution  
5. `sample_batch_summary` for sanity checks

### Minimal Python-side behavior the service should wrap

- Public sources and metadata:
  - `agml.data.public.public_data_sources()`
  - `agml.data.metadata.DatasetMetadata`
- Loader:
  - `agml.data.loader.AgMLDataLoader`
- Multi-dataset:
  - `agml.data.multi_loader.AgMLMultiDatasetLoader`

---

## 4) Available Tools and Endpoints List

## Phase 1 (recommended default; low risk)

- `list_public_datasets`
  - Returns dataset names and basic descriptors from AgML public registry.
- `validate_dataset_name`
  - Confirms whether a provided dataset identifier is valid.
- `get_dataset_metadata`
  - Returns normalized metadata (task type, classes, annotation style, etc.).
- `show_dataset_splits`
  - Returns split information (train/val/test where available).

## Phase 2 (controlled side effects)

- `instantiate_loader`
  - Creates an `AgMLDataLoader` for a target dataset with user options.
- `sample_batch_summary`
  - Returns shape/label/schema summaries for one or more sample batches.
- `export_dataset_format`
  - Exports data where supported (e.g., YOLO/TensorFlow exporters); requires filesystem write permission.

## Phase 3 (optional heavy runtime)

- `model_catalog_discovery`
  - Lists available model wrappers and compatibility hints.
- `lightweight_inference`
  - Runs constrained inference paths using optional ML dependencies.

---

## 5) Common Issues and Notes

- No stable packaged CLI contract
  - AgML is primarily a Python API; scripts under `scripts/` are maintenance-oriented and not a stable public CLI.
- Optional dependency failures
  - Return structured errors when `torch`/`tensorflow`/`opencv` etc. are missing.
- Network and disk safety
  - Keep metadata tools read-only by default.
  - Require explicit flags for dataset download/export/write operations.
- Performance considerations
  - Lazy-import heavy frameworks.
  - Add timeout/cancellation for downloads and synthetic generation.
- Environment complexity
  - Synthetic data and benchmarking paths are more complex than dataset metadata/loader tools; keep them opt-in.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/Project-AgML/AgML
- Main README: https://github.com/Project-AgML/AgML/blob/main/README.md
- Docs index: https://github.com/Project-AgML/AgML/tree/main/docs
- Contributing: https://github.com/Project-AgML/AgML/blob/main/CONTRIBUTING.md
- Environment file: https://github.com/Project-AgML/AgML/blob/main/environment.yml
- Requirements: https://github.com/Project-AgML/AgML/blob/main/requirements.txt

If you want, I can also generate a ready-to-use `service_manifest` section (tool schemas + input/output contracts) for this MCP (Model Context Protocol) service.