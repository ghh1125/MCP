# tsfresh MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **tsfresh** capabilities so developers can extract and select time-series features in automation or agent workflows.

Main capabilities:
- **Feature extraction** from long/wide time-series tables
- **Relevant feature extraction** (extract + statistical selection in one step)
- **Feature selection** against a target (`y`)
- **Forecasting frame utilities** (rolling windows, supervised framing)
- **Scikit-learn compatible transformers**
- **Optional distributed execution** (multiprocessing / Dask-style workflows)

Repository: https://github.com/blue-yonder/tsfresh

---

## 2) Installation Method

### Python requirements
Core dependencies typically include:
- numpy
- pandas
- scipy
- statsmodels
- scikit-learn
- tqdm
- requests
- stumpy
- cloudpickle
- distributed (for some distributed modes)

Optional:
- dask[dataframe]
- matplotlib
- notebook stack (for notebook/example scenarios)

### Install commands
- Install from PyPI:
  pip install tsfresh

- With optional Dask support:
  pip install "dask[dataframe]" distributed

- If building an MCP (Model Context Protocol) service wrapper, also install your MCP server runtime per your stack (for example, FastMCP/SDK-specific package).

---

## 3) Quick Start

### Basic feature extraction
Use `extract_features(...)` with key columns:
- `column_id`: entity/series id
- `column_sort`: time index
- `column_kind`: signal type (optional if single signal)
- `column_value`: numeric value column

Typical flow:
1. Load pandas DataFrame
2. Call `tsfresh.feature_extraction.extraction.extract_features`
3. Impute missing/infinite values if needed
4. Train downstream model

### Extract only relevant features
Use:
- `tsfresh.convenience.relevant_extraction.extract_relevant_features(...)`

This runs extraction + statistical relevance filtering against target `y`.

### Feature selection on existing feature table
Use:
- `tsfresh.feature_selection.selection.select_features(X, y, ...)`

### Helpful utilities
- `make_forecasting_frame(...)` for forecasting datasets
- `roll_time_series(...)` for rolling windows
- Transformers:
  - `FeatureAugmenter`
  - `RelevantFeatureAugmenter`
  - `FeatureSelector`
  - `PerColumnImputer`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (developer-oriented mapping):

- `extract_features`
  - Wraps `tsfresh.feature_extraction.extraction.extract_features`
  - Input: time-series container + column mappings + extraction settings
  - Output: extracted feature matrix

- `extract_relevant_features`
  - Wraps `tsfresh.convenience.relevant_extraction.extract_relevant_features`
  - Input: time-series container + target `y` (+ optional baseline `X`)
  - Output: relevance-filtered feature matrix

- `select_features`
  - Wraps `tsfresh.feature_selection.selection.select_features`
  - Input: feature matrix `X`, target `y`, statistical test config
  - Output: selected feature subset

- `calculate_relevance_table`
  - Wraps `tsfresh.feature_selection.relevance.calculate_relevance_table`
  - Input: `X`, `y`, ML task settings
  - Output: per-feature relevance statistics

- `make_forecasting_frame`
  - Wraps `tsfresh.utilities.dataframe_functions.make_forecasting_frame`
  - Input: univariate series + shift settings
  - Output: supervised forecasting frame

- `roll_time_series`
  - Wraps `tsfresh.utilities.dataframe_functions.roll_time_series`
  - Input: dataframe/dict + rolling parameters
  - Output: rolled/segmented time-series data

- `run_tsfresh_cli` (optional service passthrough)
  - Wraps script behavior from `tsfresh.scripts.run_tsfresh`
  - Useful for batch-style extraction jobs

---

## 5) Common Issues and Notes

- **Data format is the #1 failure point**: verify `column_id`, `column_sort`, `column_kind`, `column_value`.
- **NaN/Inf handling**: run tsfresh imputation utilities before modeling.
- **Performance tuning**:
  - Start with smaller feature parameter sets (`MinimalFCParameters` / `EfficientFCParameters`)
  - Tune `n_jobs` and `chunksize`
  - Disable progress bars in service mode
- **Distributed execution**: ensure Dask/distributed dependencies and runtime are correctly installed.
- **Statistical selection**:
  - Correctly set `ml_task` (classification vs regression)
  - Tune `fdr_level` based on false discovery tolerance
- **Large datasets**: memory usage can grow quickly during extraction; process in chunks and monitor worker memory.

---

## 6) Reference Links / Documentation

- GitHub: https://github.com/blue-yonder/tsfresh
- Official docs: https://tsfresh.readthedocs.io/
- Main APIs:
  - Feature extraction: `tsfresh.feature_extraction.extraction.extract_features`
  - Relevant extraction: `tsfresh.convenience.relevant_extraction.extract_relevant_features`
  - Feature selection: `tsfresh.feature_selection.selection.select_features`
- Examples in repository:
  - `tsfresh/examples/robot_execution_failures.py`
  - `tsfresh/examples/har_dataset.py`
  - `tsfresh/examples/driftbif_simulation.py`