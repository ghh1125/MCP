# sktime MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes practical time-series capabilities from [`sktime`](https://github.com/sktime/sktime) as callable developer tools.

Main goals:
- Discover available estimators dynamically
- Load built-in datasets quickly for testing
- Train and run forecasting pipelines
- Evaluate models with standard forecasting metrics
- Support split/tuning workflows for production-like experiments

Core sktime abstractions behind this service:
- `BaseForecaster`, `BaseTransformer`, `BaseClassifier`, `BaseRegressor`, `BaseClusterer`, `BaseDetector`
- Estimator registry via `all_estimators`
- Dataset loaders (`load_airline`, `load_longley`, etc.)
- Model selection (`temporal_train_test_split`, window splitters, forecasting CV search)
- Forecast metrics (`MAE`, `MSE`, `MAPE`, `MASE`)

---

## 2) Installation Method

### Requirements
- Python `>=3.9`
- Core dependencies: `numpy`, `pandas`, `scikit-learn`, `scipy`, `joblib`
- `sktime` package

### Install (minimal)
pip install -U sktime

### Optional extras (only if needed by selected estimators)
- statsmodels, pmdarima, prophet, tbats
- darts, neuralforecast
- pytorch, tensorflow
- tslearn, pyts, numba
- optuna, scikit-optimize, mlflow
- tsfresh, tsfel, temporian, transformers

Tip: keep a lean environment first, then install optional dependencies based on tool failures/warnings.

---

## 3) Quick Start

Typical MCP (Model Context Protocol) workflow:
1. Call `list_estimators` to discover compatible estimators by task (forecasting/classification/etc.)
2. Call `load_dataset` (e.g., airline) to get sample data
3. Call `train_forecaster` with estimator name + params
4. Call `predict_forecast` for horizon-based predictions
5. Call `evaluate_forecast` to compute metrics (MAE/MSE/MAPE/MASE)

Example flow (conceptual):
- `load_dataset(name="airline")`
- `temporal_split(test_size=24)`
- `train_forecaster(estimator="NaiveForecaster", params={"strategy":"last"})`
- `predict_forecast(fh=[1,2,...,24])`
- `evaluate_forecast(metrics=["mae","mape"])`

---

## 4) Available Tools and Endpoints List

- `health_check`  
  Verifies service is running and dependencies are importable.

- `list_estimators`  
  Uses sktime registry discovery (`all_estimators`) to return available estimators and metadata/tags.

- `get_estimator_info`  
  Returns constructor signature, task type, dependency hints, and capabilities for a specific estimator.

- `load_dataset`  
  Loads built-in datasets (forecasting/classification/regression) for quick experiments.

- `temporal_split`  
  Time-aware train/test split helper for forecasting datasets.

- `create_splitter`  
  Build window splitters (expanding/sliding) for backtesting.

- `train_forecaster`  
  Fit a forecasting estimator on training data.

- `predict_forecast`  
  Produce point forecasts (and optionally intervals/quantiles if supported).

- `evaluate_forecast`  
  Compute metrics such as MAE, MSE, MAPE, MASE.

- `forecasting_grid_search`  
  Hyperparameter tuning via forecasting CV.

- `forecasting_random_search`  
  Randomized hyperparameter tuning for faster exploration.

- `build_pipeline`  
  Compose transformations + estimator into a single runnable pipeline.

---

## 5) Common Issues and Notes

- Optional dependency errors are normal  
  Many sktime estimators require extra libraries. Install only what your chosen estimator needs.

- Estimator availability varies by environment  
  `list_estimators` output depends on installed optional packages.

- Data format matters  
  sktime supports multiple scientific types (series/panel/hierarchical). Use service-provided conversion/validation paths if available.

- Performance considerations  
  Some models (deep learning, large-search tuning) are compute-heavy. Start with small datasets and short horizons.

- Reproducibility  
  Pass `random_state` where possible for deterministic results.

- Version compatibility  
  Prefer recent stable versions of Python + sktime + scikit-learn to reduce API mismatch.

---

## 6) Reference Links or Documentation

- sktime repository: https://github.com/sktime/sktime  
- sktime docs: https://www.sktime.net  
- Estimator overview: `ESTIMATOR_OVERVIEW.md` (in repository)  
- Forecasting base API (`BaseForecaster`): `sktime/forecasting/base/_base.py`  
- Transformer base API (`BaseTransformer`): `sktime/transformations/base.py`  
- Registry lookup (`all_estimators`): `sktime/registry/_lookup.py`  
- Forecasting metrics: `sktime/performance_metrics/forecasting/`