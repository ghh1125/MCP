# Statsmodels MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `statsmodels` Python library as an MCP (Model Context Protocol) service so LLM agents and developer tools can run statistical modeling and diagnostics through stable, tool-style endpoints.

Primary capabilities:
- Linear regression (OLS/WLS/GLS)
- Generalized Linear Models (GLM)
- Discrete models (Logit/Probit/Poisson/NegativeBinomial)
- Time-series modeling (ARIMA/SARIMAX and related forecasting workflows)
- Statistical tests and diagnostics
- Built-in dataset loading for reproducible examples
- Environment/version health checks

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Core dependencies:
  - `numpy`
  - `scipy`
  - `pandas`
  - `patsy`
  - `packaging`

Optional:
- `matplotlib` (plots)
- `cvxopt` (some optimization paths)
- `joblib` (parallel helpers)
- External `x13as` binary (for `statsmodels.tsa.x13` workflows)

### Install
pip install statsmodels pandas numpy scipy patsy packaging

(Optional extras)
pip install matplotlib joblib cvxopt

Health check:
python -m statsmodels.tools.print_version

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Call a dataset endpoint (or pass your own tabular/time-series data).
2. Call a model-fit endpoint (e.g., OLS/GLM/Logit/ARIMA).
3. Call predict/forecast endpoint.
4. Call diagnostics endpoint.

### Example service usage (conceptual)
- `dataset.load(name="longley")`
- `regression.ols_fit(y="TOTEMP", X=["GNPDEFL","GNP","UNEMP","ARMED","POP","YEAR"])`
- `regression.predict(rows=[...])`
- `stats.diagnostic_tests(model_id="...")`

For formula-based workflows:
- `formula.fit(model="ols", formula="y ~ x1 + x2", data=...)`

For time series:
- `tsa.arima_fit(order=[1,1,1], y=...)`
- `tsa.forecast(steps=12)`

---

## 4) Available Tools and Endpoints List

Recommended endpoint set for this repository:

- `health.version`
  - Returns runtime/version info using `statsmodels.tools.print_version`.
- `dataset.load`
  - Loads built-in datasets from `statsmodels.datasets`.
- `regression.ols_fit`
  - Fits OLS via `statsmodels.regression.linear_model.OLS`.
- `regression.wls_fit`
  - Fits weighted least squares (WLS).
- `regression.gls_fit`
  - Fits generalized least squares (GLS).
- `glm.fit`
  - Fits generalized linear model via `statsmodels.genmod.generalized_linear_model.GLM`.
- `discrete.logit_fit`
  - Binary logistic regression via `Logit`.
- `discrete.probit_fit`
  - Binary probit regression via `Probit`.
- `discrete.poisson_fit`
  - Count model via `Poisson`.
- `discrete.negbin_fit`
  - Count model via `NegativeBinomial`.
- `formula.fit`
  - Formula interface through `statsmodels.formula.api`.
- `tsa.arima_fit`
  - Univariate ARIMA via `statsmodels.tsa.arima.model.ARIMA`.
- `tsa.sarimax_fit`
  - Seasonal/exogenous ARIMA via `statsmodels.tsa.statespace.sarimax.SARIMAX`.
- `model.predict`
  - Generic in-sample/out-of-sample prediction.
- `model.summary`
  - Returns compact model summary/statistics.
- `stats.tests`
  - Common statistical tests via `statsmodels.stats.api`.

---

## 5) Common Issues and Notes

- Data shape issues:
  - Most failures come from mismatched `X/y` lengths, missing values, or non-numeric columns.
- Constant/intercept handling:
  - Add a constant where required (`sm.add_constant`) unless formula API handles it.
- Convergence:
  - GLM/discrete/state-space models may need solver/maxiter tuning.
- Time index quality:
  - For forecasting, use a clean monotonic datetime index with fixed frequency.
- Performance:
  - Large state-space and high-dimensional models can be expensive; consider smaller batches and cached fitted models.
- Optional binary dependency:
  - `x13as` must be installed separately for X13 seasonal adjustment endpoints.
- Reproducibility:
  - Pin `statsmodels`, `numpy`, `scipy`, and `pandas` versions in production.

---

## 6) Reference Links or Documentation

- Statsmodels repository: https://github.com/statsmodels/statsmodels
- Statsmodels user docs: https://www.statsmodels.org/
- API entrypoint: `statsmodels/api.py`
- Formula API: `statsmodels/formula/api.py`
- Time-series API: `statsmodels/tsa/api.py`
- Stats API: `statsmodels/stats/api.py`
- Version diagnostics: `python -m statsmodels.tools.print_version`