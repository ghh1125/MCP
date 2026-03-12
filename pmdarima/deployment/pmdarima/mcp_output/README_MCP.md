# pmdarima MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the core capabilities of [`pmdarima`](https://github.com/alkaline-ml/pmdarima) to provide practical time-series forecasting workflows for LLM-driven or API-based systems.

Main capabilities:
- Automatic ARIMA/SARIMA model selection (`auto_arima`)
- ARIMA model training and forecasting (`ARIMA`, `AutoARIMA`)
- Time-series cross-validation (`RollingForecastCV`, `SlidingWindowForecastCV`, `cross_val_score`, `cross_val_predict`)
- Preprocessing pipelines for endogenous/exogenous features (`Pipeline`, Box-Cox/log transforms, date/fourier featurizers)
- Diagnostics and utilities (stationarity tests, differencing helpers, sMAPE metric)
- Built-in sample datasets for smoke tests and demos

---

## 2) Installation Method

### Requirements
Core dependencies:
- numpy
- scipy
- scikit-learn
- pandas
- statsmodels
- joblib
- Cython

Optional:
- matplotlib (visualization)
- pytest (testing)

### Install
Recommended:
- `pip install pmdarima`

If building from source in your MCP (Model Context Protocol) service environment:
- Ensure C/C++ build tooling is available
- Then run: `pip install .`

---

## 3) Quick Start

### Minimal flow
1. Load a time series
2. Run `auto_arima` to identify orders
3. Forecast future periods
4. (Optional) Validate with time-series CV
5. (Optional) Add preprocessing pipeline

Example workflow (conceptual):
- Dataset: `load_airpassengers()`
- Fit: `auto_arima(y, seasonal=True, m=12)`
- Predict: `model.predict(n_periods=12)`
- Evaluate: `smape(y_true, y_pred)`

With exogenous features:
- Build date/fourier features (`DateFeaturizer`, `FourierFeaturizer`)
- Use `Pipeline([... , AutoARIMA(...)])`
- Fit and predict with exogenous matrix aligned to forecast horizon

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `forecast.auto_arima`
  - Auto-select ARIMA/SARIMA orders and fit model.
- `forecast.fit_arima`
  - Fit explicit ARIMA configuration.
- `forecast.predict`
  - Generate out-of-sample forecasts (with optional confidence intervals).
- `forecast.update`
  - Append new observations and refresh model state.
- `validation.cross_val_score`
  - Time-series cross-validation scoring.
- `validation.cross_val_predict`
  - Fold-wise predictions for backtesting.
- `validation.split.rolling`
  - Rolling-origin splitter (`RollingForecastCV`).
- `validation.split.sliding`
  - Sliding-window splitter (`SlidingWindowForecastCV`).
- `preprocess.endog.boxcox`
  - Box-Cox transform/inverse-transform for target series.
- `preprocess.endog.log`
  - Log transform/inverse-transform for target series.
- `preprocess.exog.date_features`
  - Calendar/date feature generation.
- `preprocess.exog.fourier_features`
  - Fourier seasonal feature generation.
- `diagnostics.stationarity`
  - ADF/KPSS/PP stationarity checks.
- `utils.differencing`
  - `ndiffs`/`nsdiffs` suggestions and differencing helpers.
- `metrics.smape`
  - Forecast error metric.
- `datasets.load`
  - Load built-in sample datasets for testing.

---

## 5) Common Issues and Notes

- Binary/build issues:
  - `pmdarima` may require compiled extensions; ensure compiler toolchain and compatible Python version.
- Seasonal configuration:
  - Set `m` correctly (e.g., 12 monthly, 7 daily-weekly cycle) or auto-selection quality may degrade.
- Exogenous regressors:
  - Training and forecasting exogenous features must have consistent columns and ordering.
- Data quality:
  - Handle missing timestamps/values before fitting.
- Performance:
  - `auto_arima` can be expensive on large grids; prefer stepwise mode for production latency.
- Reproducibility:
  - Pin dependency versions and set deterministic options where possible.
- Environment:
  - Use isolated virtual environments and lock files for MCP (Model Context Protocol) deployments.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/alkaline-ml/pmdarima
- Official README: https://github.com/alkaline-ml/pmdarima/blob/master/README.md
- API Docs: https://alkaline-ml.com/pmdarima/
- Examples: `examples/` directory in repository
- Build/config reference: `pyproject.toml` in repository

If you are integrating this as an MCP (Model Context Protocol) service, start by exposing `auto_arima`, `predict`, CV utilities, and preprocessing endpoints first; these cover most production forecasting use cases.