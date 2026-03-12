# EigenLedger MCP (Model Context Protocol) Service README

## 1) Project Introduction

EigenLedger is a portfolio analytics service focused on return/risk evaluation and performance attribution.  
This MCP (Model Context Protocol) service wraps EigenLedger’s analytics workflow and exposes practical tools for:

- Return and cumulative performance analysis
- Risk metrics (volatility, drawdown, tail risk)
- Risk-adjusted ratios (e.g., Sharpe-style metrics)
- Rolling statistics over time windows
- Factor/performance attribution

Core logic is mainly in `EigenLedger/main.py`, with analytics utilities in `EigenLedger/modules/empyrical/*`.

---

## 2) Installation Method

### Requirements
Recommended Python: 3.9+  
Core dependencies (from analysis):  
- `numpy`
- `pandas`
- `scipy`

Optional (for UI/visualization/data ingestion depending on your use case):  
- `streamlit`
- `matplotlib`
- `plotly`
- `yfinance`

### Install
1. Clone the repository:
   - `git clone https://github.com/santoshlite/EigenLedger.git`
   - `cd EigenLedger`

2. Install dependencies manually (no confirmed `requirements.txt`/`setup.py` in scan metadata):
   - `pip install numpy pandas scipy streamlit matplotlib plotly yfinance`

3. (Optional) Install as editable package:
   - `pip install -e .`

---

## 3) Quick Start

### Run via launcher
- `python -m EigenLedger.run`  
Fallback:
- `python EigenLedger/run.py`

### Import-oriented usage pattern
Use `EigenLedger.main` as the primary integration entry for custom MCP (Model Context Protocol) service handlers, and `EigenLedger.modules.empyrical` for metric-level operations.

Typical flow:
1. Load/prepare return series (Pandas Series/DataFrame).
2. Call analytics functions from main workflow or empyrical-style stats helpers.
3. Return structured JSON to MCP (Model Context Protocol) clients.

---

## 4) Available Tools and Endpoints List

Below is a practical MCP (Model Context Protocol) endpoint design based on discovered modules.

### `analyze_performance`
Compute overall performance metrics (total return, annualized return, cumulative curves).

### `analyze_risk`
Compute volatility, max drawdown, downside/tail risk, and related risk diagnostics.

### `analyze_risk_adjusted`
Compute risk-adjusted metrics (e.g., Sharpe-like and drawdown-aware ratios).

### `analyze_rolling_metrics`
Compute rolling-window statistics for trend and stability monitoring.

### `analyze_perf_attribution`
Decompose performance by factor/asset contribution (from `perf_attrib.py`).

### `health_check`
Return service runtime status, dependency readiness, and version/build metadata.

Note: Exact function names are not fully enumerated by scan metadata, so map endpoint handlers to available callable symbols in `EigenLedger/main.py` and `EigenLedger/modules/empyrical/*` during implementation.

---

## 5) Common Issues and Notes

- Packaging metadata appears minimal/incomplete in scan results; dependency pinning is recommended for production.
- Import feasibility is medium (0.58): validate module import paths in your runtime image.
- Main logic is concentrated in a large single file (`main.py`), so startup overhead and coupling may be moderate.
- If using visualization/UI libraries, separate server runtime dependencies from analytics-only runtime for lean deployments.
- Ensure input data quality (frequency consistency, NaN handling, timezone normalization) before metric computation.
- For large rolling-window workloads, prefer vectorized Pandas/Numpy operations and cache repeated computations.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/santoshlite/EigenLedger
- Main module: `EigenLedger/main.py`
- Runner: `EigenLedger/run.py`
- Analytics modules:
  - `EigenLedger/modules/empyrical/stats.py`
  - `EigenLedger/modules/empyrical/perf_attrib.py`
  - `EigenLedger/modules/empyrical/utils.py`
  - `EigenLedger/modules/empyrical/periods.py`

If you are building an MCP (Model Context Protocol) service wrapper, treat this repo as the analytics engine and expose stable, JSON-friendly endpoint contracts at your service layer.