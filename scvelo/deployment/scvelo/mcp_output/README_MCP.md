# scVelo MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core `scvelo` workflows so LLM agents and developer tools can run RNA velocity analysis on single-cell data (`AnnData`), including:

- preprocessing (`neighbors`, `moments`)
- velocity estimation (`velocity`)
- transition graph construction (`velocity_graph`)
- embedding projection (`velocity_embedding`)
- trajectory inference (`velocity_pseudotime`, `terminal_states`)
- plotting helpers for velocity visualization

Typical use case: submit an `.h5ad` dataset and receive processed analysis artifacts (updated AnnData fields, metrics, and optional figures).

---

## 2) Installation Method

### Requirements

- Python `>=3.10`
- Core libraries: `anndata`, `scanpy`, `numpy`, `scipy`, `pandas`, `matplotlib`, `scikit-learn`, `numba`, `h5py`, `joblib`
- Optional (feature-dependent): `loompy`, `igraph`, `louvain`, `leidenalg`, `pynndescent`, `umap-learn`, `dask`, `jax`, `torch`

### Install

- Install from PyPI:
  - `pip install scvelo scanpy`
- Or install from source:
  - `git clone https://github.com/theislab/scvelo.git`
  - `cd scvelo`
  - `pip install -e .`

---

## 3) Quick Start

### Minimal workflow

import scvelo as scv
import scanpy as sc

adata = sc.read_h5ad("your_data.h5ad")
scv.pp.filter_and_normalize(adata)
scv.pp.neighbors(adata)
scv.pp.moments(adata)

scv.tl.velocity(adata, mode="stochastic")   # or mode="dynamical"
scv.tl.velocity_graph(adata)
scv.tl.velocity_embedding(adata, basis="umap")
scv.tl.velocity_pseudotime(adata)
scv.tl.terminal_states(adata)

scv.pl.velocity_embedding_stream(adata, basis="umap")

### Service-oriented usage pattern

- Input: dataset path or in-memory AnnData reference + tool parameters  
- Invoke endpoint (example): `tools.velocity`  
- Output: updated AnnData keys (`layers`, `obs`, `obsm`, `uns`) and optional plot artifact paths/bytes

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `datasets.load`
  - Load built-in example datasets for testing/demo.
- `io.read`
  - Read `.h5ad`/supported formats into AnnData.
- `preprocess.neighbors`
  - Build nearest-neighbor graph used by downstream velocity analysis.
- `preprocess.moments`
  - Compute neighborhood moments required by velocity models.
- `tools.velocity`
  - Estimate RNA velocity (steady-state/stochastic/dynamical depending on config).
- `tools.velocity_graph`
  - Compute transition graph from velocity-informed similarities.
- `tools.velocity_embedding`
  - Project velocity vectors onto embedding (e.g., UMAP/PCA).
- `tools.velocity_pseudotime`
  - Infer pseudotime from velocity transition dynamics.
- `tools.terminal_states`
  - Estimate root and terminal cell states.
- `plot.velocity_embedding_stream`
  - Create stream plot for velocity field visualization.
- `plot.scatter`
  - Generic embedding scatter plotting endpoint.

---

## 5) Common Issues and Notes

- **AnnData schema assumptions**: Ensure required layers/annotations exist (spliced/unspliced, neighbors, moments) before calling later tools.
- **Pipeline order matters**: Run preprocessing (`neighbors`, `moments`) before `velocity`/`velocity_graph`.
- **Optional dependency failures**: Graph clustering/embedding features may require `igraph`, `leidenalg`, `umap-learn`, etc.
- **Performance**: `velocity_graph` and dynamical modeling can be CPU/memory intensive on large datasets; consider batching/downsampling.
- **Numerical stability**: Different preprocessing normalization/filtering settings can significantly affect inferred trajectories.
- **Reproducibility**: Set random seeds in Scanpy/scVelo-related steps for stable comparisons.
- **No native CLI detected**: Integrate via Python API-backed MCP (Model Context Protocol) service methods.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/theislab/scvelo
- scVelo docs (start from repo README and linked documentation): https://github.com/theislab/scvelo/blob/main/README.md
- Scanpy (ecosystem dependency): https://scanpy.readthedocs.io/
- AnnData: https://anndata.readthedocs.io/