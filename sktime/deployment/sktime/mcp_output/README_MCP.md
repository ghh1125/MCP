# sktime MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the `sktime` ecosystem to provide practical time-series capabilities through standardized tools/endpoints.

Main functions:
- Forecasting (fit/predict/update, intervals, quantiles, probabilistic outputs)
- Transformation pipelines (fit/transform/inverse_transform)
- Classification, regression, clustering for time series
- Detection (anomaly/changepoint/segmentation)
- Dataset loading for demos/tests
- Estimator discovery via registry (no hard-coded model lists)
- Evaluation with forecasting metrics and temporal splitters

---

## 2) Installation Method

### Requirements
- Python >= 3.10
- Core: `numpy`, `pandas`, `scikit-learn`, `scipy`, `packaging`
- Optional (feature-dependent): `statsmodels`, `pmdarima`, `prophet`, `darts`, `neuralforecast`, `pytorch-forecasting`, `torch`, `tensorflow`, `tslearn`, `pyts`, `numba`, `mlflow`, `polars`, `dask`, `gluonts`, `tbats`, `arch`, `skopt`, `optuna`, `hyperactive`

### Install
- `pip install sktime`
- If your MCP (Model Context Protocol) service has extras, install those per your deployment profile (forecasting DL, probabilistic, optimization, etc.).

---

## 3) Quick Start

Typical MCP (Model Context Protocol) workflow:
1. List available estimators with registry lookup (`all_estimators`)
2. Load a built-in dataset (e.g., `load_airline`, `load_longley`, `load_gunpoint`)
3. Create estimator instance (forecaster/transformer/classifier/etc.)
4. Run lifecycle methods:
   - Forecasting: `fit`, `predict`, `update`, `predict_interval`, `predict_quantiles`, `predict_proba`, `score`
   - Transformation: `fit`, `transform`, `fit_transform`, `inverse_transform`, `update`
   - Classification/Regression/Clustering/Detection: standard `fit/predict/...`
5. Evaluate with metrics (e.g., MAE/MSE/MAPE/MASE) and temporal splitters (`temporal_train_test_split`, sliding/expanding windows)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) endpoints for this service:

- `list_estimators`
  - Uses `sktime.registry.all_estimators`
  - Returns estimators filtered by task/scitype/tags

- `load_dataset`
  - Built-in loaders from `sktime.datasets`
  - Examples: airline, lynx, shampoo_sales, basic_motions, gunpoint, tecator

- `forecast_fit_predict`
  - Fits a `BaseForecaster`-compatible model and returns forecasts

- `forecast_predict_interval`
  - Returns prediction intervals for fitted forecasters

- `forecast_predict_quantiles`
  - Returns quantile forecasts

- `forecast_predict_proba`
  - Returns probabilistic forecast outputs (distribution-like predictions)

- `transform_fit_transform`
  - Applies `BaseTransformer` pipeline to input data

- `transform_inverse`
  - Runs inverse transformations where supported

- `classify_fit_predict`
  - Time-series classification via `BaseClassifier`

- `regress_fit_predict`
  - Time-series regression via `BaseRegressor`

- `cluster_fit_predict`
  - Time-series clustering via `BaseClusterer`

- `detect_fit_predict`
  - Detection tasks via `BaseDetector` (anomaly/changepoint/segmentation)

- `split_temporal`
  - Time-aware train/test split and CV splitter generation

- `evaluate_forecast`
  - Forecast metric computation (MAE, MSE, MAPE, MASE, etc.)

---

## 5) Common Issues and Notes

- Optional dependency errors are expected for some estimators.
  - Fix by installing task-specific packages (e.g., `torch`, `statsmodels`, `tslearn`).
- No first-class end-user CLI is exposed by default.
  - `build_tools/*` scripts are maintainer utilities, not runtime MCP (Model Context Protocol) endpoints.
- Performance:
  - Large panel/hierarchical data can be expensive; prefer windowed evaluation and lightweight models first.
  - Enable `numba`-accelerated paths when available.
- Data shape/type mismatches are common.
  - Use `sktime`-compatible series/panel/hierarchical formats and validate before inference.
- Reproducibility:
  - Set random seeds in estimator params where available.
- Environment:
  - Python 3.10+ strongly recommended to avoid compatibility issues.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/sktime/sktime
- Main docs and usage guidance (from repo README/docs): `README.md`, `docs/source/*`
- Estimator discovery: `sktime/registry/_lookup.py` (`all_estimators`)
- Core APIs:
  - Forecasting base: `sktime/forecasting/base/_base.py`
  - Transformer base: `sktime/transformations/base.py`
  - Classifier base: `sktime/classification/base.py`
  - Regressor base: `sktime/regression/base.py`
  - Clusterer base: `sktime/clustering/base.py`
  - Detector base: `sktime/detection/base/_base.py`
- Datasets: `sktime/datasets/__init__.py`
- Forecast metrics: `sktime/performance_metrics/forecasting/__init__.py`
- Temporal splitting: `sktime/split/__init__.py`