# Scanpy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core **Scanpy** single-cell analysis capabilities through an MCP (Model Context Protocol) interface.  
It is designed for developer workflows that need structured, callable tools for:

- AnnData I/O (`read`, `read_10x_h5`, `read_10x_mtx`, `read_visium`, `write`)
- Preprocessing (`filter_cells`, `filter_genes`, `normalize_total`, `log1p`, `highly_variable_genes`, `scale`, `pca`, `neighbors`)
- Analysis (`umap`, `tsne`, `leiden`, `louvain`, `rank_genes_groups`, `paga`, `dpt`, `score_genes`)
- Plotting (selected non-interactive plotting functions)
- Demo datasets (`pbmc3k`, `pbmc68k_reduced`, `visium_sge`, etc.)

Recommended execution strategy:
- Primary: direct Python import/calls
- Fallback: `scanpy` CLI for limited cases

---

## 2) Installation Method

### Runtime requirements
Required core stack:
- Python
- numpy, scipy, pandas
- anndata, h5py
- matplotlib
- scikit-learn, numba, networkx

Optional (feature-dependent):
- umap-learn, igraph, leidenalg, louvain, pynndescent
- dask, zarr
- bbknn, harmonypy, scanorama, magic-impute, phate, phenograph, palantir, sam-algorithm, wishbone

### Install (minimal)
pip install scanpy

### Install (common analysis extras)
pip install "scanpy[leiden]" umap-learn igraph leidenalg

### Service integration
Install your MCP (Model Context Protocol) host/runtime, then register this service as a Python-backed service that imports `scanpy` and exposes the tool functions listed below.

---

## 3) Quick Start

### Typical workflow (service-side logic)
1. Load data via `scanpy.read*`  
2. Preprocess via `scanpy.pp.*`  
3. Compute embeddings/clusters via `scanpy.tl.*`  
4. Return structured results (obs/var stats, embeddings, cluster labels)  
5. Optionally generate saved plots via `scanpy.pl.*` (file output only)

### Example call sequence
- `read("data.h5ad")`
- `pp.filter_cells(...)`
- `pp.filter_genes(...)`
- `pp.normalize_total(...)`
- `pp.log1p(...)`
- `pp.highly_variable_genes(...)`
- `pp.pca(...)`
- `pp.neighbors(...)`
- `tl.umap(...)`
- `tl.leiden(...)`
- `tl.rank_genes_groups(...)`

### Recommended response pattern
For each endpoint, return:
- `status`
- `inputs`
- `summary_metrics`
- `artifacts` (paths, tables, plot file names)
- `warnings` (missing optional dependencies, large-memory operations)

---

## 4) Available Tools and Endpoints List

### I/O endpoints
- `read` — Load AnnData-compatible files.
- `read_10x_h5` — Load 10x HDF5 matrices.
- `read_10x_mtx` — Load 10x MTX directories.
- `read_visium` — Load Visium spatial datasets.
- `write` — Save AnnData to disk.

### Preprocessing endpoints
- `filter_cells` — Filter low-quality cells.
- `filter_genes` — Filter low-information genes.
- `normalize_total` — Library size normalization.
- `log1p` — Log transform counts.
- `highly_variable_genes` — Select variable genes.
- `scale` — Standardize features.
- `pca` — Dimensionality reduction.
- `neighbors` — Compute neighborhood graph.

### Analysis endpoints
- `umap` — 2D/3D manifold embedding.
- `tsne` — t-SNE embedding.
- `leiden` — Graph-based clustering (requires leiden deps).
- `louvain` — Louvain clustering (optional deps).
- `rank_genes_groups` — Differential expression per group.
- `paga` — Coarse-grained connectivity graph.
- `dpt` — Diffusion pseudotime.
- `score_genes` — Gene set scoring.

### Plotting endpoints (selective)
- `pl.umap`, `pl.tsne`, `pl.pca`
- `pl.violin`, `pl.dotplot`, `pl.matrixplot`
- `pl.rank_genes_groups`

### Dataset endpoints
- `datasets.pbmc3k`
- `datasets.pbmc68k_reduced`
- `datasets.visium_sge`
- `datasets.krumsiek11`
- `datasets.toggleswitch`

---

## 5) Common Issues and Notes

- **Optional dependency errors**: many advanced tools (Leiden, UMAP, external methods) need extra packages.
- **Headless environments**: use non-interactive matplotlib backend; save plots to files.
- **Memory/performance**: large `.h5ad` and dense conversions can be expensive; prefer sparse-safe operations.
- **Path safety**: enforce strict sandboxing for read/write endpoints.
- **Reproducibility**: set random seeds for neighbors/UMAP/clustering.
- **Stability**: expose a curated subset of plotting and external methods to reduce operational risk.

---

## 6) Reference Links / Documentation

- Scanpy repository: https://github.com/scverse/scanpy
- Scanpy docs index: https://scanpy.readthedocs.io/
- API docs: https://scanpy.readthedocs.io/en/stable/api.html
- Installation guide: https://scanpy.readthedocs.io/en/stable/installation.html
- AnnData docs: https://anndata.readthedocs.io/

If you want, I can also provide a ready-to-use MCP (Model Context Protocol) service manifest/template with this endpoint set and suggested input/output schemas.