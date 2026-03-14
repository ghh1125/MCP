# DeepChem MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core DeepChem capabilities for molecular ML workflows, including:

- Dataset loading and preprocessing (CSV/SDF/JSON/image/biological sequence)
- Featurization (ECFP, graph, SMILES/token, protein/complex features)
- Model training/inference (Torch, TensorFlow, JAX, sklearn, XGBoost)
- Benchmarking via MolNet loaders and benchmark runners
- Evaluation, metrics, splitting, transforms, and utility workflows

Repository: https://github.com/deepchem/deepchem

---

## 2) Installation

### Base requirements
- Python 3.8+ (recommended 3.10/3.11)
- Core libs: `numpy scipy pandas scikit-learn joblib tqdm`

Install core package:
- `pip install deepchem`

Install optional stacks as needed:
- Chemistry: `rdkit`
- Deep learning: `torch` or `tensorflow` or `jax`
- Extras: `pytorch-lightning transformers dgl torch-geometric xgboost lightgbm pyscf`

Practical setup pattern:
1. Create a fresh virtual environment
2. Install `deepchem`
3. Add only the backend/features you need (Torch/TensorFlow/JAX + RDKit)

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Load dataset from MolNet (e.g., Tox21, Delaney, QM9)
2. Apply featurizer and split strategy
3. Train selected model
4. Evaluate with DeepChem metrics
5. Return scores/predictions via MCP (Model Context Protocol) response

### Example task patterns
- Classification benchmark: use `deepchem.molnet.run_benchmark`
- Low-data benchmark: use `deepchem.molnet.run_benchmark_low_data`
- Programmatic loading: use `deepchem.molnet.load_function.*`
- Data ingest: `deepchem.data.*` loaders
- Feature extraction: `deepchem.feat.*`
- Training APIs: `deepchem.models.*` / `deepchem.models.torch_models.*`
- Evaluation: `deepchem.metrics.*`, `deepchem.utils.evaluate`

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints:

- `health_check`
  - Verify runtime, backend availability, and import status.

- `list_capabilities`
  - Return installed backends/features (Torch/TF/JAX/RDKit, etc.).

- `load_dataset`
  - Load datasets via MolNet (`load_tox21`, `load_delaney`, `load_qm9`, etc.) or file loaders.

- `featurize_data`
  - Apply selected featurizer (ECFP, graph conv, SMILES tokenizer, protein/complex, material).

- `split_dataset`
  - Apply splitters (random, scaffold, stratified, time/PDBBind, task-based).

- `train_model`
  - Train model families (GraphConv, MPNN, GCN/GAT, multitask MLP, sklearn, GBDT).

- `predict`
  - Run inference on prepared datasets.

- `evaluate_model`
  - Compute metrics (ROC-AUC, PRC-AUC, RMSE, MAE, Pearson R², etc.).

- `run_benchmark`
  - Execute MolNet benchmark workflow using selected model/split/featurizer.

- `run_low_data_benchmark`
  - Execute low-data benchmark variants.

- `export_results`
  - Save predictions, scores, and metadata to disk/artifact storage.

---

## 5) Common Issues and Notes

- Dependency complexity is medium/high; install only required optional stacks.
- RDKit is essential for many molecule features and loaders.
- Torch/TF/JAX features are backend-specific; missing backend causes import/runtime failures.
- Some benchmark datasets require downloading large files; expect longer setup times.
- GPU acceleration depends on correct CUDA/backend build compatibility.
- DGL/PyG-based models need matching versions with your PyTorch installation.
- For reproducibility, set random seeds and pin package versions.

---

## 6) References

- DeepChem repository: https://github.com/deepchem/deepchem
- Main package docs (in repo): `README.md`, `docs/`
- Examples: `examples/`
- MolNet loaders: `deepchem/molnet/load_function/`
- Benchmarks:  
  - `python -m deepchem.molnet.run_benchmark`  
  - `python -m deepchem.molnet.run_benchmark_low_data`
- Contribution guide: `CONTRIBUTING.md`