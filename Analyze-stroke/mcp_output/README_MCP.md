# Analyze-stroke MCP (Model Context Protocol) Service README

## 1) Project Introduction

Analyze-stroke is a Python-based analysis pipeline for stroke-related data, focused on:

- Data loading and preprocessing
- Feature selection
- Dimensionality reduction
- Model training/evaluation
- Causal effect analysis
- Result visualization (including chart export)

This repository can be wrapped as an MCP (Model Context Protocol) service to expose analysis steps as callable developer tools for local automation or agent workflows.

Core modules:

- `data_loader.py` → `DataLoader`
- `feature_selection.py` → `FeatureSelectionAnalyzer`
- `dim_reduction.py` → `DimensionAnalyzer`
- `models.py` → `ModelManager`
- `causal_module.py` → `CausalAnalyzer`
- `plot_utils.py` → plotting utilities

---

## 2) Installation Method

### Prerequisites

- Python 3.9+ (recommended)
- Conda (recommended, because `environment.yml` is provided)

### Option A: Conda (recommended)

1. Create environment from `environment.yml`
2. Activate it
3. Validate runtime

Typical commands:

- `conda env create -f environment.yml`
- `conda activate <env-name>`
- `python test_env.py`

### Option B: pip (minimal)

Install core dependencies manually:

- `pip install numpy pandas scikit-learn matplotlib seaborn`

If causal analysis features fail, install additional causal-related packages referenced in `environment.yml` / `causal_module.py`.

---

## 3) Quick Start

### Run full pipeline

- `python main.py`

### Run causal batch workflow (with charts)

- `python run_all_causal.py`

### Run causal workflow without drawing (headless/CI)

- `python run_all_causal_wo_draw.py`

### Environment check

- `python test_env.py`

### Programmatic usage (import style)

Use module classes directly in your service layer:

- `DataLoader` for dataset input
- `FeatureSelectionAnalyzer` for feature filtering/ranking
- `DimensionAnalyzer` for dimensionality reduction
- `ModelManager` for model lifecycle
- `CausalAnalyzer` for causal analysis
- `plot_utils.plot_from_excel(...)` for chart generation from result files

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `health_check`
  - Runs environment/dependency diagnostics (maps to `test_env.check_environment`)

- `run_main_pipeline`
  - Executes end-to-end analysis (maps to `main.main`)

- `run_causal_batch`
  - Executes multi-run causal analysis with visualization (maps to `run_all_causal.run_batch_analysis`)

- `run_causal_batch_no_draw`
  - Executes causal analysis in non-plot mode (maps to `run_all_causal_wo_draw.py` flow)

- `plot_results_from_excel`
  - Generates effect/p-value charts from Excel outputs (maps to `plot_utils.plot_from_excel`)

- `draw_effect_chart`
  - Draws effect chart for a dataframe (maps to `plot_utils.draw_effect_chart`)

- `draw_pvalue_chart`
  - Draws p-value chart for a dataframe (maps to `plot_utils.draw_pvalue_chart`)

- `parse_causal_log_output`
  - Parses causal log text for summaries/metrics (maps to `run_all_causal.parse_log_output`)

---

## 5) Common Issues and Notes

- Dependency mismatches:
  - Prefer `environment.yml` to avoid version conflicts.
- Headless environments:
  - Use no-draw workflow (`run_all_causal_wo_draw.py`) when display backends are unavailable.
- Import feasibility:
  - Repository structure is script-oriented; for MCP (Model Context Protocol) service use, add a thin adapter layer around existing classes/functions.
- Performance:
  - Causal workflows can be slower on large datasets; consider batching and reduced plotting for automation runs.
- Output handling:
  - Ensure write permissions for logs, figures, and exported result files.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/ghh1125/Analyze-stroke
- Main entry scripts:
  - `main.py`
  - `run_all_causal.py`
  - `run_all_causal_wo_draw.py`
  - `test_env.py`
- Core analysis modules:
  - `data_loader.py`
  - `feature_selection.py`
  - `dim_reduction.py`
  - `models.py`
  - `causal_module.py`
  - `plot_utils.py`