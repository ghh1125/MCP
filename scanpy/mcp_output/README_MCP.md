# Scanpy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core **Scanpy** single-cell analysis capabilities through an MCP (Model Context Protocol) interface.  
It is designed for developer workflows that need programmatic access to:

- Data I/O for AnnData and 10x formats
- Preprocessing (QC, normalization, HVG selection, PCA, neighbor graph)
- Analysis tools (Leiden/Louvain clustering, UMAP/t-SNE, PAGA, marker ranking)
- Plotting helpers (UMAP/scatter, dotplot, matrixplot, violin, etc.)
- Dataset loading and tabular extraction utilities

Repository: https://github.com/scverse/scanpy

---

## 2) Installation Method

### Requirements
Core runtime dependencies typically include:

- anndata, numpy, scipy, pandas
- matplotlib, scikit-learn, h5py
- numba, networkx, packaging

Common optional dependencies (feature-dependent):

- umap-learn
- igraph / python-igraph, leidenalg, louvain
- dask, zarr
- statsmodels, seaborn
- harmonypy, bbknn, scanorama, magic-impute, palantir, phate, phenograph

### Install
- Install Scanpy:
  - `pip install scanpy`
- For richer workflows, also install optional ecosystem packages as needed.
- If deploying as an MCP (Model Context Protocol) service, include Scanpy and your MCP runtime in the same environment.

---

## 3) Quick Start

Typical service flow:

1. Load data (`read_h5ad`, `read_10x_h5`, `read_10x_mtx`, or dataset loaders such as `pbmc3k`)
2. Run preprocessing (`filter_cells`, `filter_genes`, `calculate_qc_metrics`, `normalize_total`, `log1p`, `highly_variable_genes`, `pca`, `neighbors`)
3. Run analysis (`leiden`/`louvain`, `umap`, `rank_genes_groups`, `paga`)
4. Return tabular results (`obs_df`, `var_df`, `rank_genes_groups_df`) and/or plotting artifacts

Example pipeline sequence:
- read → qc/filter → normalize/log1p → hvg → pca → neighbors → leiden → umap → marker ranking

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (grouped by module):

### I/O
- `read`, `read_h5ad`, `read_csv`, `read_loom` — Load AnnData-compatible files
- `read_10x_h5`, `read_10x_mtx` — Read 10x Genomics data
- `write` — Persist processed AnnData objects

### Datasets
- `pbmc3k`, `pbmc68k_reduced`, `blobs`, `krumsiek11`, `toggleswitch`, `ebi_expression_atlas` — Quick demo/test datasets

### Preprocessing (`pp`)
- `calculate_qc_metrics` — Per-cell/per-gene QC metrics
- `filter_cells`, `filter_genes` — Basic filtering
- `normalize_total`, `log1p` — Library-size normalization and transform
- `highly_variable_genes` — Feature selection
- `scale`, `regress_out` — Feature scaling and regression
- `pca`, `neighbors` — Dimensionality reduction and graph construction
- `scrublet`, `subsample` — Doublet detection and sampling helpers

### Tools (`tl`)
- `leiden`, `louvain` — Graph clustering
- `umap`, `tsne`, `diffmap`, `draw_graph` — Embedding
- `paga`, `dendrogram`, `embedding_density`, `ingest` — Graph/trajectory and transfer utilities
- `rank_genes_groups`, `score_genes`, `marker_gene_overlap` — Marker and scoring analysis

### Plotting (`pl`)
- `umap`, `scatter`, `spatial` — Embedding/spatial visualization
- `dotplot`, `matrixplot`, `stacked_violin`, `violin`, `heatmap` — Expression summary plots
- `paga`, `rank_genes_groups` — Result-oriented visual outputs

### Get/Tabular Accessors
- `obs_df`, `var_df`, `rank_genes_groups_df` — Dataframe outputs for downstream systems

### Metrics
- `morans_i`, `gearys_c` — Spatial/autocorrelation metrics

### External Integrations (`external`)
- `bbknn`, `harmony_integrate`, `scanorama_integrate`, `magic`, `mnn_correct` — Optional integrations requiring extra packages

### CLI
- `scanpy`
- `python -m scanpy`

---

## 5) Common Issues and Notes

- **Missing optional dependencies**: many advanced endpoints require extra installs (e.g., `leidenalg`, `igraph`, `umap-learn`).
- **Version compatibility**: keep `scanpy`, `anndata`, and numeric stack versions aligned.
- **Memory/performance**: large datasets can be expensive for PCA/neighbors/UMAP; consider subsampling, sparse matrices, and staged processing.
- **Headless environments**: plotting may require non-interactive matplotlib backend.
- **External methods**: wrappers in `scanpy.external` fail gracefully only if dependency checks are handled in service code.
- **Data format assumptions**: most endpoints expect valid AnnData structure (`.obs`, `.var`, `.X`, optional `.raw`, `.obsm`, `.uns`).

---

## 6) Reference Links and Documentation

- Scanpy repository: https://github.com/scverse/scanpy
- Scanpy docs index: `docs/index.md` in repository
- API docs sections:
  - `docs/api/preprocessing.md`
  - `docs/api/tools.md`
  - `docs/api/plotting.md`
  - `docs/api/io.md`
  - `docs/api/datasets.md`
  - `docs/api/get.md`
  - `docs/api/metrics.md`
- Developer docs:
  - `docs/dev/getting-set-up.md`
  - `docs/dev/testing.md`
  - `docs/dev/documentation.md`