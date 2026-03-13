# Statsmodels MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a developer-friendly interface to core `statsmodels` capabilities for statistical modeling, inference, and forecasting.

Main functions:
- Run classical regression (OLS/WLS/GLS), GLM, and discrete models (Logit/Probit/Poisson)
- Execute time-series workflows (ARIMA, SARIMAX, decomposition, forecasting)
- Access statistical tests and diagnostics
- Load built-in datasets for rapid experimentation
- Return structured model summaries, parameters, predictions, and diagnostics

Repository: https://github.com/statsmodels/statsmodels

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Core dependencies:
  - `numpy`
  - `scipy`
  - `pandas`
  - `patsy`
  - `packaging`
- Optional (feature-dependent):
  - `matplotlib` (plots)
  - `cvxopt` (some optimization paths)
  - `joblib` (parallel helpers)
  - `x13as` external binary (for X13 seasonal adjustment workflows)

### Install
pip install statsmodels numpy scipy pandas patsy packaging

Optional extras:
pip install matplotlib joblib cvxopt

Environment check:
python -m statsmodels.tools.print_version

---

## 3) Quick Start

### Basic import path
Use high-level APIs:
- `statsmodels.api` (general models/stats)
- `statsmodels.tsa.api` (time-series)
- `statsmodels.stats.api` (tests/inference)
- `statsmodels.formula.api` (formula syntax)

### Typical service flow
1. Load/receive dataset
2. Choose model family (`OLS`, `GLM`, `Logit`, `ARIMA`, `SARIMAX`, etc.)
3. Fit model
4. Return:
   - coefficients
   - confidence intervals
   - p-values
   - model diagnostics
   - predictions/forecasts

### Example call patterns (conceptual)
- Regression: fit OLS and return summary + residual diagnostics
- Classification/count: fit Logit/Poisson and return marginal effects
- Forecasting: fit ARIMA/SARIMAX and return horizon forecasts with intervals

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `health_check`
  - Verifies runtime, package availability, and version metadata.

- `get_version_info`
  - Returns Python/statsmodels/dependency versions (similar to `print_version`).

- `list_datasets`
  - Lists built-in datasets available from `statsmodels.datasets`.

- `load_dataset`
  - Loads a selected built-in dataset and returns schema/sample rows.

- `fit_ols`
  - Fits OLS/WLS/GLS/GLSAR models; returns coefficients and inference statistics.

- `fit_glm`
  - Fits GLM with configurable family/link; returns fit metrics and inference.

- `fit_discrete_model`
  - Fits `Logit`, `Probit`, `MNLogit`, `Poisson`, `NegativeBinomial`.

- `fit_arima`
  - Fits ARIMA models for univariate time series.

- `fit_sarimax`
  - Fits SARIMAX (seasonality + exogenous regressors + state space engine).

- `forecast`
  - Produces out-of-sample predictions/forecast intervals for fitted time-series models.

- `run_stat_tests`
  - Executes common tests (normality, heteroskedasticity, autocorrelation, proportions/power, etc.).

- `model_summary`
  - Standardized textual/structured summary extraction from fitted results objects.

- `predict`
  - In-sample or out-of-sample prediction for regression/discrete/GLM models.

---

## 5) Common Issues and Notes

- Binary/scientific stack issues:
  - Use a clean virtual environment.
  - Upgrade `pip`, `setuptools`, and `wheel` if installation fails.

- Formula models:
  - `patsy` is required for formula APIs.

- Time-series advanced features:
  - Some workflows (e.g., X13) require external binaries not installed by pip.

- Performance:
  - Large state-space or high-dimensional models can be expensive.
  - Prefer smaller parameter grids and constrained iteration settings in service contexts.

- Numerical convergence:
  - Non-convergence can occur for complex models.
  - Expose optimizer options (maxiter, method, tolerance) in endpoint inputs.

- Reproducibility:
  - Set random seeds where simulation/resampling is involved.
  - Return model config + versions in every response payload.

---

## 6) Reference Links / Documentation

- Statsmodels repository: https://github.com/statsmodels/statsmodels
- Official docs: https://www.statsmodels.org/
- API reference (entry point): https://www.statsmodels.org/stable/api.html
- Time series docs: https://www.statsmodels.org/stable/tsa.html
- Installation notes: https://www.statsmodels.org/stable/install.html
- Developer docs directory in repo: `docs/`