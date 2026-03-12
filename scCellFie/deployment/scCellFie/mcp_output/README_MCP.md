# scCellFie MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the core capabilities of **scCellFie** for single-cell metabolic analysis on `AnnData` objects.  
It is designed for developers who want programmable access to:

- End-to-end scCellFie pipeline execution
- Gene score, reaction activity, and metabolic task scoring
- Preprocessing utilities (GPR handling, normalization, database preparation)
- Spatial analysis and communication scoring
- Differential statistics and reporting
- Plot-ready outputs and data export/load helpers

Primary package: `sccellfie`  
Repository: https://github.com/earmingol/scCellFie

---

## 2) Installation Method

### Requirements

Core Python dependencies include:

- numpy
- pandas
- scipy
- anndata
- scanpy
- networkx
- matplotlib
- seaborn
- statsmodels

Optional (feature-dependent): `squidpy`, `scikit-learn`, `umap-learn`, `plotly`.

### Install

- From source:
  - `git clone https://github.com/earmingol/scCellFie.git`
  - `cd scCellFie`
  - `pip install -r requirements.txt`
  - `pip install .`

- For MCP (Model Context Protocol) service deployment, add this package to your service runtime image/environment and expose the tool endpoints listed below.

---

## 3) Quick Start

Minimal developer flow:

1. Load or prepare an `AnnData`.
2. Run scCellFie pipeline.
3. Access results in `adata` fields/layers.
4. Optionally run reporting/statistics/plotting services.

Example usage (Python-level backend logic):

import scanpy as sc
from sccellfie.sccellfie_pipeline import run_sccellfie_pipeline
from sccellfie.datasets.database import load_sccellfie_database

adata = sc.read_h5ad("input.h5ad")
db = load_sccellfie_database(organism="homo_sapiens")

adata = run_sccellfie_pipeline(
    adata=adata,
    organism="homo_sapiens",
    sccellfie_db=db,
    smooth_cells=True,
    alpha=0.3,
    n_neighbors=15,
    verbose=True
)

Common direct scoring calls:

- `compute_gene_scores(...)` in `sccellfie.gene_score`
- `compute_reaction_activity(...)` in `sccellfie.reaction_activity`
- `compute_mt_score(...)` in `sccellfie.metabolic_task`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints mapped from core modules:

- `run_sccellfie_pipeline`
  - Full workflow orchestration (neighbors, smoothing, scoring, task activity).
- `load_sccellfie_database`
  - Load organism-specific metabolic task/reaction resources.
- `preprocess_inputs`
  - Align expression + database resources and filter unusable mappings.
- `compute_gene_scores`
  - Compute per-gene activity scores from expression and thresholds.
- `compute_reaction_activity`
  - Evaluate reaction-level activity using GPR rules.
- `compute_mt_score`
  - Compute metabolic task scores from reaction activity.
- `thresholds_*` (global/local mean/percentile/trimean/manual)
  - Generate threshold strategies for gene scoring.
- `smooth_expression_knn`
  - KNN-based expression smoothing for noisy single-cell data.
- `compute_communication_scores`
  - Ligand-receptor style communication scoring by group.
- `compute_local_colocalization_scores`
  - Spatial colocalization communication metric.
- `create_knn_network` / `compute_assortativity` / `compute_hotspots`
  - Spatial network, assortativity, and hotspot services.
- `pairwise_differential_analysis` / `scanpy_differential_analysis` / `fit_gam_model`
  - Differential and trajectory-like statistical analysis.
- `generate_report_from_adata`
  - Summarize metrics by tissue/group/cell type.
- `save_adata` / `load_adata` / `save_result_summary`
  - I/O services for reproducible persistence.
- Plot services (`plot_spatial`, `create_volcano_plot`, `create_radial_plot`, etc.)
  - Ready-to-render data visualizations.

---

## 5) Common Issues and Notes

- **AnnData schema**: Ensure expected `obs`, `var`, and optional `layers/raw` fields are present before calling scoring services.
- **Species resources**: Built-in data targets human and mouse task folders; verify `organism` and DB files match your input gene IDs.
- **Gene ID mapping**: Use preprocessing/gpr utilities if your matrix uses symbols vs Ensembl IDs inconsistently.
- **Performance**: Large datasets may require chunking (`chunk_size`) and disabling expensive plotting in pipeline runs.
- **Spatial features**: Spatial services require valid coordinates (commonly `obsm["spatial"]`) and neighbor graph configuration.
- **Optional deps**: Some advanced/statistical/spatial paths may require optional libraries not present in minimal installs.

---

## 6) Reference Links or Documentation

- GitHub repository: https://github.com/earmingol/scCellFie
- Package source tree: `sccellfie/` modules (pipeline, preprocessing, expression, stats, spatial, plotting)
- Test suite (recommended behavior reference): `sccellfie/**/tests/`
- Docs config: `docs/source/` (Sphinx-based structure present)