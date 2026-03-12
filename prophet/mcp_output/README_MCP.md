# Prophet MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core capabilities from **Facebook Prophet** for time-series forecasting and evaluation, exposed through MCP (Model Context Protocol)-friendly service endpoints.

Main capabilities:
- Train forecasting models (`Prophet`)
- Generate future forecasts and components
- Run backtesting / cross-validation diagnostics
- Compute performance metrics (RMSE, MAE, MAPE, coverage, etc.)
- Handle country holiday calendars
- Serialize / deserialize trained models for reuse

Repository analyzed: https://github.com/facebook/prophet

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ (recommended)
- `pip`
- Build tools needed by Prophet backend (CmdStan / compiler toolchain depending on OS)

### Install Prophet
- `pip install prophet`

If your environment has backend build issues, ensure compiler toolchain and CmdStan dependencies are available (common on minimal containers/CI).

### Optional visualization dependencies
- Matplotlib and Plotly are commonly used by Prophet plotting functions.

---

## 3) Quick Start

### Minimal forecasting flow
- Create a dataframe with:
  - `ds`: datetime column
  - `y`: target value
- Initialize and fit `Prophet`
- Create future dataframe
- Predict forecast
- (Optional) evaluate with diagnostics cross-validation and metrics

Typical Python call pattern:
- `from prophet import Prophet`
- `m = Prophet(...)`
- `m.fit(df)`
- `future = m.make_future_dataframe(periods=...)`
- `fcst = m.predict(future)`

### Diagnostics flow
- `from prophet.diagnostics import cross_validation, performance_metrics`
- `df_cv = cross_validation(model=m, horizon='30 days', ...)`
- `df_perf = performance_metrics(df_cv, metrics=['rmse','mae','mape','coverage'])`

### Serialization flow
- `from prophet.serialize import model_to_json, model_from_json`
- Save trained model JSON, then reload for inference without retraining

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) services to expose:

1. **train_forecast_model**
   - Train a Prophet model from historical time-series data.
   - Input: rows with `ds`, `y`, model options.
   - Output: model handle / serialized model.

2. **predict_forecast**
   - Generate forecast for future periods from a trained model.
   - Input: model handle, forecast horizon or future dataframe config.
   - Output: forecast dataframe (`yhat`, intervals, trend/seasonality components).

3. **run_cross_validation**
   - Time-series backtesting with rolling cutoffs.
   - Input: model handle, `horizon`, optional `initial`, `period`, `cutoffs`.
   - Output: cross-validation prediction results.

4. **compute_performance_metrics**
   - Compute evaluation metrics from CV output.
   - Input: CV dataframe, selected metrics, rolling window options.
   - Output: metric summary dataframe.

5. **generate_holidays**
   - Build holiday dataframe by country/region and years.
   - Input: `country`, `year_list`, optional `province`/`state`.
   - Output: holidays dataframe for model regressors.

6. **serialize_model / deserialize_model**
   - Persist and reload Prophet model state.
   - Input/Output: JSON model payload.

7. **get_regressor_coefficients** (optional advanced)
   - Return fitted regressor effects for interpretability.

---

## 5) Common Issues and Notes

- **Backend/toolchain setup**: Prophet may require local compilation/runtime backend support. If install fails, verify compiler + CmdStan-related prerequisites.
- **Data format is strict**: `ds` must be parseable datetime; `y` must be numeric and clean (handle NaN/outliers upstream).
- **Frequency consistency**: Use consistent historical cadence (daily/hourly/etc.) for stable forecasts.
- **Cross-validation cost**: Diagnostics can be expensive on large datasets; tune `period`, `horizon`, and parallel settings.
- **Timezone handling**: Normalize timezone strategy before training (e.g., UTC) to avoid alignment issues.
- **Model portability**: Prefer JSON serialization endpoints for deployment and reproducibility.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/facebook/prophet
- Top-level docs: `README.md` (repo root)
- Python package docs: `python/README.md`
- Core modules:
  - `python/prophet/forecaster.py` (`Prophet`)
  - `python/prophet/diagnostics.py`
  - `python/prophet/serialize.py`
  - `python/prophet/make_holidays.py`
  - `python/prophet/utilities.py`
  - `python/prophet/plot.py`

If you are implementing this as an MCP (Model Context Protocol) service, start with `train_forecast_model`, `predict_forecast`, `run_cross_validation`, and `compute_performance_metrics` as the core production endpoints.