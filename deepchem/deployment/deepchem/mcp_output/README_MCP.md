# DeepChem MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical interface over the DeepChem repository for molecular ML workflows, including:

- Data ingestion (`CSV`, `SDF`, `JSON`, FASTA, images)
- Featurization (molecular, graph, sequence, material, complex)
- Dataset preparation and splitting (random, scaffold, stratified, index)
- Model training/inference (PyTorch, TensorFlow/Keras, optional JAX)
- Transforms and metrics for evaluation
- MolNet benchmark execution

It is designed for developer-facing automation agents and toolchains that need structured access to DeepChem capabilities.

---

## 2) Installation Method

### Prerequisites
- Python 3.9+ recommended
- Core: `numpy`, `scipy`, `pandas`, `scikit-learn`
- Optional by use case: `rdkit`, `torch`, `tensorflow`, `jax`, `pytorch-lightning`, `transformers`, `dgl`, `xgboost`, `lightgbm`, `pyscf`

### Install DeepChem
- Minimal:
  - `pip install deepchem`
- With PyTorch workflows:
  - Install `torch` first (matching your CPU/GPU setup), then `pip install deepchem`
- With TensorFlow workflows:
  - Install `tensorflow`, then `pip install deepchem`
- Chemistry-heavy workflows:
  - Ensure `rdkit` is installed in your environment before running molecular featurizers/loaders

### Verify
- Run: `python -c "import deepchem as dc; print(dc.__version__)"`

---

## 3) Quick Start

### Typical workflow in MCP (Model Context Protocol)
1. Load data with a DeepChem loader (e.g., `CSVLoader`, `SDFLoader`)
2. Featurize into a `Dataset` (`NumpyDataset`/`DiskDataset`)
3. Split (`RandomSplitter` or `ScaffoldSplitter`)
4. Apply transformers (normalization/balancing if needed)
5. Train model (`TorchModel` or `KerasModel`)
6. Evaluate using `Metric`

### Minimal example flow
- Load a CSV of molecules + labels
- Apply a molecular featurizer (e.g., circular fingerprint or graph featurizer)
- Train a classifier/regressor
- Return predictions and ROC-AUC/RMSE metrics

### Benchmark entry points
- `python -m deepchem.molnet.run_benchmark`
- `python -m deepchem.molnet.run_benchmark_low_data`
- `python -m deepchem.molnet.run_benchmark_models`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) services for this repo:

- `health_check`
  - Validate Python runtime and key package availability.
- `list_capabilities`
  - Return installed backends (RDKit/Torch/TF/JAX) and enabled features.
- `load_dataset`
  - Ingest raw files via DeepChem loaders into dataset objects.
- `featurize_data`
  - Apply selected featurizer to molecules/sequences/materials/complexes.
- `split_dataset`
  - Run random/scaffold/stratified/index splitting.
- `apply_transformers`
  - Run normalization, balancing, clipping, log transforms.
- `train_model`
  - Train DeepChem model wrappers (`TorchModel`, `KerasModel`, etc.).
- `predict`
  - Batch inference on new samples.
- `evaluate_model`
  - Compute metrics via DeepChem `Metric`.
- `run_molnet_benchmark`
  - Launch MolNet benchmarking scripts and return summary results.
- `list_models` / `list_featurizers` / `list_splitters`
  - Discover available classes in current environment.

---

## 5) Common Issues and Notes

- Backend mismatch:
  - Many features are optional; missing `rdkit`/`torch`/`tensorflow` causes import/runtime errors for specific tasks.
- Environment complexity:
  - DeepChem is large and multi-framework; prefer isolated virtual environments.
- Performance:
  - Use `DiskDataset` for larger-than-memory workloads.
  - For GPU workflows, verify CUDA-compatible framework versions.
- Reproducibility:
  - Set random seeds and splitter configs explicitly.
- Intrusiveness/complexity:
  - Service integration risk is medium due to broad dependency surface; start with minimal endpoints and progressively enable advanced features.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/deepchem/deepchem
- Main docs (project): check `README.md` and `docs/` in repo
- Examples: `examples/`
- Core benchmark modules:
  - `deepchem/molnet/run_benchmark.py`
  - `deepchem/molnet/run_benchmark_low_data.py`
  - `deepchem/molnet/run_benchmark_models.py`
- Key implementation modules:
  - `deepchem/data/datasets.py`
  - `deepchem/data/data_loader.py`
  - `deepchem/feat/base_classes.py`
  - `deepchem/models/torch_models/torch_model.py`
  - `deepchem/models/keras_model.py`
  - `deepchem/splits/splitters.py`
  - `deepchem/trans/transformers.py`
  - `deepchem/metrics/metric.py`