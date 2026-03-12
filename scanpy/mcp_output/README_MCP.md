# Scanpy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core **Scanpy** single-cell analysis workflows into MCP (Model Context Protocol)-friendly tools so LLM agents and developer clients can run common RNA-seq tasks programmatically.

Main capabilities:
- AnnData I/O (`read`, `read_h5ad`, `write`)
- Preprocessing (filtering, normalization, log transform, scaling, HVG selection, PCA)
- Graph and embedding workflows (neighbors, UMAP)
- Clustering (Leiden)
- Marker ranking (`rank_genes_groups`)
- Data extraction helpers (`obs_df`, `var_df`, `rank_genes_groups_df`)
- Built-in dataset loaders for smoke tests (`pbmc3k`, `pbmc68k_reduced`, `visium_sge`)

---

## 2) Installation Method

### Requirements
Core dependencies:
- anndata
- numpy
- scipy
- pandas
- matplotlib
- scikit-learn

Common optional dependencies (feature-dependent):
- umap-learn
- igraph + leidenalg (or louvain)
- h5py
- numba
- dask
- bbknn, harmonypy, scanorama, magic-impute, phate, phenograph

### Install
- Install Scanpy:
  - `pip install scanpy`
- Recommended clustering stack:
  - `pip install "scanpy[leiden]"`
- Optional ecosystem tools: install only what your endpoints expose.

---

## 3) Quick Start

### Typical workflow in service logic
1. Load dataset (`scanpy.datasets.pbmc3k()` or `scanpy.read_h5ad(...)`)
2. Preprocess:
   - `filter_cells`, `filter_genes`
   - `normalize_per_cell`, `log1p`
   - `highly_variable_genes`
   - `pca`
3. Build graph and embedding:
   - `neighbors`
   - `umap`
4. Cluster and markers:
   - `leiden`
   - `rank_genes_groups`
5. Return tabular outputs:
   - `obs_df`, `var_df`, `rank_genes_groups_df`

### Minimal invocation path
- Import-first strategy is recommended (`import scanpy as sc`)
- CLI fallback is available:
  - `scanpy ...`
  - `python -m scanpy ...`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `io.read`
  - Read AnnData from path/URL.
- `io.read_h5ad`
  - Read `.h5ad` specifically.
- `io.write`
  - Persist AnnData/results.

- `datasets.pbmc3k`
  - Load canonical PBMC tutorial dataset (fast smoke test).
- `datasets.pbmc68k_reduced`
  - Reduced PBMC dataset for quicker iteration.
- `datasets.visium_sge`
  - Spatial example dataset.

- `pp.filter_cells`
  - Filter low-quality cells by counts/genes.
- `pp.filter_genes`
  - Filter low-information genes.
- `pp.normalize_per_cell`
  - Library-size normalization.
- `pp.log1p`
  - Log transform.
- `pp.highly_variable_genes`
  - HVG selection.
- `pp.pca`
  - PCA embedding.

- `neighbors.compute`
  - KNN graph computation (`scanpy.neighbors.neighbors`).

- `tl.umap`
  - UMAP embedding from neighbor graph.
- `tl.leiden`
  - Leiden clustering.
- `tl.rank_genes_groups`
  - Differential ranking by cluster/group.
- `tl.filter_rank_genes_groups`
  - Post-filter ranked markers.

- `get.obs_df`
  - Extract obs-aligned tabular data.
- `get.var_df`
  - Extract var-aligned tabular data.
- `get.rank_genes_groups_df`
  - Extract marker table as DataFrame-like output.

---

## 5) Common Issues and Notes

- **Leiden errors**: usually missing `igraph`/`leidenalg`.
- **UMAP unavailable**: install `umap-learn`.
- **Large-memory runs**: PCA/neighbors on big datasets can be heavy; use subset/HVG and incremental strategies.
- **Version mismatch**: keep `scanpy`, `anndata`, and `numpy/scipy` compatible.
- **Headless environments**: configure matplotlib backend if plotting endpoints are enabled.
- **Runtime profile**: import feasibility is high; operational complexity is medium.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/scverse/scanpy
- Scanpy docs index: `docs/index.md` (in repo)
- API docs sections:
  - `docs/api/preprocessing.md`
  - `docs/api/tools.md`
  - `docs/api/plotting.md`
  - `docs/api/io.md`
  - `docs/api/datasets.md`
- Development/testing references:
  - `docs/dev/getting-set-up.md`
  - `docs/dev/testing.md`
  - `tests/` for behavior examples