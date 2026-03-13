# EigenLedger MCP (Model Context Protocol) Service README

## 1) Project Introduction

EigenLedger is a quantitative backtesting and analytics toolkit that can be exposed as an MCP (Model Context Protocol) service for LLM-driven research and automation.

This service is best suited for:
- Strategy backtest orchestration
- Backtest reporting and analysis workflows
- Portfolio performance/risk metric calculation (via vendored `empyrical` utilities)
- Performance attribution calculations

Primary callable surface:
- `EigenLedger.main` (core workflow functions such as `Backtest_Model`, `Backtest_Report`, `Backtest_Analysis`, etc.)
- `EigenLedger.modules.empyrical.stats` (risk/performance metrics)
- `EigenLedger.modules.empyrical.perf_attrib` (attribution utility)

---

## 2) Installation Method

### Requirements
- Python 3.8+
- Core libraries: `numpy`, `pandas`, `scipy`
- Optional (visualization/UI): `matplotlib`, `plotly`, `streamlit`, `seaborn`

### Install
1. Clone repository:
   - `git clone https://github.com/santoshlite/EigenLedger.git`
2. Enter project directory:
   - `cd EigenLedger`
3. Install package (editable recommended for service development):
   - `pip install -e .`
4. If optional visualization/service features are needed, install extras manually:
   - `pip install matplotlib plotly streamlit seaborn`

---

## 3) Quick Start

### A. Import and call core workflow functions
Typical main-module entry points include:
- `Backtest_Model`
- `Backtest_Report`
- `Backtest_Models`
- `Backtest_Analysis`
- `Backtest_Integration`
- `Backtest_Dataset`
- `Backtest_Transform`
- `Backtest_Visualize`
- `Backtest_Dashboard`
- `Backtest_Multiprocess`
- `Backtest_Optimize`
- `Backtest_Utility`

Use your MCP (Model Context Protocol) service layer to wrap these functions as callable tools, passing plain JSON-like parameters and returning structured results.

### B. Use analytics functions directly (stable tool candidates)
From `EigenLedger.modules.empyrical.stats`:
- `alpha`, `beta`
- `annual_return`, `annual_volatility`
- `sharpe_ratio`, `sortino_ratio`
- `max_drawdown`, `calmar_ratio`
- `omega_ratio`, `tail_ratio`
- `value_at_risk`, `conditional_value_at_risk`

From `EigenLedger.modules.empyrical.perf_attrib`:
- `perf_attrib`

### C. CLI fallback execution
If direct import behavior varies by environment, run:
- `python -m source.EigenLedger.run`
- `python -m source.EigenLedger.main`

(Use this as a fallback invocation path in your MCP (Model Context Protocol) service runtime.)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `backtest_model`  
  Wraps `Backtest_Model`; runs a strategy/model backtest pipeline.

- `backtest_report`  
  Wraps `Backtest_Report`; generates summarized backtest reports.

- `backtest_analysis`  
  Wraps `Backtest_Analysis`; computes deeper diagnostics on results.

- `backtest_optimize`  
  Wraps `Backtest_Optimize`; performs parameter/search optimization workflow.

- `backtest_dataset`  
  Wraps `Backtest_Dataset`; dataset preparation and loading helper.

- `metric_alpha_beta`  
  Wraps `alpha`/`beta`; estimates market-relative performance.

- `metric_risk_return`  
  Wraps annualized return/volatility and Sharpe/Sortino metrics.

- `metric_drawdown`  
  Wraps `max_drawdown` and `calmar_ratio`; downside risk summaries.

- `metric_tail_risk`  
  Wraps `value_at_risk`, `conditional_value_at_risk`, `tail_ratio`.

- `performance_attribution`  
  Wraps `perf_attrib`; factor/segment-level attribution output.

Implementation note: keep endpoints narrow and deterministic (single responsibility, explicit schema in/out).

---

## 5) Common Issues and Notes

- Import feasibility is moderate (estimated ~0.74).  
  If module paths differ in deployment, prefer a thin adapter layer and CLI fallback.

- Dependency gaps: no `requirements.txt` detected.  
  Use `pyproject.toml` plus manual installation of optional libraries.

- Visualization stack is optional.  
  Install plotting/UI packages only if corresponding endpoints are enabled.

- Performance considerations:
  - Backtests can be CPU/memory intensive on large datasets.
  - Consider batching, caching, and multiprocessing safeguards.
  - Add execution timeout and input-size limits in service endpoints.

- Environment consistency:
  - Pin Python and numerical package versions for reproducibility.
  - Validate data schema before running expensive computations.

- Intrusiveness risk: medium.  
  Prefer non-invasive wrappers around existing functions rather than modifying internal logic.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/santoshlite/EigenLedger
- Package root: `EigenLedger/`
- Core module: `EigenLedger/main.py`
- Runner: `EigenLedger/run.py`
- Analytics module: `EigenLedger/modules/empyrical/stats.py`
- Attribution module: `EigenLedger/modules/empyrical/perf_attrib.py`
- Existing docs:
  - `README.md`
  - `README_CN.md`