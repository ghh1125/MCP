# lifelines MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the `lifelines` Python library to provide survival analysis capabilities to LLM applications and developer tools.

Core capabilities:
- Fit survival models (Kaplan–Meier, Cox PH, AFT, Weibull, etc.)
- Run statistical tests (log-rank, proportional hazards checks, RMST comparisons)
- Load built-in example datasets
- Generate calibration and plotting-ready outputs
- Compute utility metrics (e.g., concordance index)

This service is best suited for data science assistants, clinical analytics workflows, and automated model comparison pipelines.

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- System packages for scientific Python stack (if needed)
- Main dependencies:
  - `numpy`
  - `scipy`
  - `pandas`
  - `matplotlib`
  - `autograd`
  - `autograd-gamma`
  - `formulaic`

### Install
pip install lifelines numpy scipy pandas matplotlib autograd autograd-gamma formulaic

### Optional (development/docs/testing)
pip install pytest sphinx jupyter nbconvert

---

## 3) Quick Start

### Basic workflow
1. Load or receive a tabular dataset with duration/event columns.
2. Call a fitter endpoint (for example, Cox or Kaplan–Meier).
3. Inspect returned coefficients/survival curves/test statistics.
4. Optionally run diagnostics (PH assumption tests, calibration).

### Example service usage flow
- `dataset.load` → `model.fit_coxph` → `statistics.logrank_test` → `utils.concordance_index`

### Minimal Python-side equivalent
from lifelines import CoxPHFitter
from lifelines.datasets import load_rossi

df = load_rossi()
cph = CoxPHFitter()
cph.fit(df, duration_col="week", event_col="arrest")
print(cph.summary)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoint groups:

### `dataset.*`
- `dataset.list` — list bundled lifelines datasets
- `dataset.load` — load a named dataset (e.g., `rossi`, `lung`, `gbsg2`)

### `model.fit_*`
- `model.fit_kaplan_meier` — non-parametric survival estimation
- `model.fit_coxph` — Cox proportional hazards regression
- `model.fit_cox_time_varying` — Cox model with time-varying covariates
- `model.fit_weibull` / `model.fit_exponential` / `model.fit_lognormal` / `model.fit_loglogistic`
- `model.fit_aft_*` — AFT regression family (Weibull/LogNormal/LogLogistic)
- `model.fit_aalen_additive` — additive hazards model

### `statistics.*`
- `statistics.logrank_test` — two-group survival comparison
- `statistics.pairwise_logrank_test` — pairwise group comparisons
- `statistics.multivariate_logrank_test` — multi-group comparison
- `statistics.proportional_hazard_test` — PH assumption diagnostics
- `statistics.rmst_difference_test` — restricted mean survival time difference

### `calibration.*`
- `calibration.survival_probability` — calibration at fixed time horizon

### `metrics.*`
- `metrics.concordance_index` — ranking/discrimination quality

### `utils.*`
- `utils.k_fold_cross_validation` — model validation
- `utils.to_long_format` / `utils.add_covariate_to_timeline` — time-varying data prep
- `utils.find_best_parametric_model` — parametric model selection helper

### `plot.*` (optional)
- `plot.survival_curve`
- `plot.loglogs`
- `plot.qq`
- `plot.rmst`
- `plot.at_risk_counts`

---

## 5) Common Issues and Notes

- **Column mapping errors**: Ensure `duration_col` and `event_col` are explicitly provided.
- **Convergence warnings**: Common in Cox/AFT models with collinearity or separability; standardize features, reduce covariates, or regularize.
- **Time-varying format**: Use long/episodic format (`start`, `stop`, `event`) for time-varying models.
- **Censoring assumptions**: Confirm right/left/interval censoring assumptions match chosen model.
- **Performance**: Large datasets and heavy diagnostics can be slow; prefer batched requests and limit plotting in production.
- **Headless environments**: For plotting endpoints on servers, configure non-interactive matplotlib backend.
- **Dependency consistency**: Pin versions in production for `numpy/scipy/pandas/lifelines`.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/CamDavidsonPilon/lifelines
- Official docs: https://lifelines.readthedocs.io/
- Examples: `examples/` directory in the repository
- Changelog: `CHANGELOG.md` in the repository

If you want, I can also generate a ready-to-use `service.json` tool schema for these MCP (Model Context Protocol) endpoints.