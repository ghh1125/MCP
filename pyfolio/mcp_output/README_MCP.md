# Pyfolio MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **pyfolio** as an MCP (Model Context Protocol) analytics backend for portfolio and strategy evaluation.

It is designed for developers who need:
- Risk/return statistics (Sharpe, drawdown, volatility, alpha/beta, VaR)
- Tear sheet generation (returns, positions, transactions, round trips, capacity)
- Plot-ready analytics for dashboards and research workflows
- Utilities for intraday detection, turnover, slippage adjustment, and factor attribution

Core modules exposed by the service:
- `timeseries` (performance metrics & drawdown analytics)
- `tears` (full and focused tear sheets)
- `plotting` (visual analytics helpers)
- `txn`, `pos`, `round_trips`, `capacity`, `perf_attrib`, `utils`

---

## 2) Installation Method

### Requirements
- Python environment compatible with pyfolio
- Required packages: `numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`, `empyrical`
- Optional: `IPython/Jupyter`, `zipline` (for extraction helpers), `scikit-learn` (some advanced paths)

### Install
- Install pyfolio from source repo or package index:
  - `pip install pyfolio`
- If using this as an MCP (Model Context Protocol) service, also install your MCP server runtime and register this service in your MCP config.

### Verify
- Import test:
  - `import pyfolio as pf`
- If import succeeds, service tool wiring can proceed.

---

## 3) Quick Start

Example workflow in your MCP (Model Context Protocol) client:
1. Load or pass `returns` (required), optionally `positions`, `transactions`, `benchmark_rets`, `factor_returns`, `factor_loadings`.
2. Call a quick summary tool (mapped to `timeseries.perf_stats`).
3. Generate a tear sheet (mapped to `tears.create_simple_tear_sheet` or `create_full_tear_sheet`).
4. Use plotting tools for targeted charts (rolling Sharpe, drawdown, turnover, sector allocation).

Typical high-value calls:
- Performance summary: `timeseries.perf_stats(returns, factor_returns, positions, transactions, turnover_denom)`
- Full report: `tears.create_full_tear_sheet(...)`
- Returns report: `tears.create_returns_tear_sheet(...)`
- Transaction analysis: `tears.create_txn_tear_sheet(...)`
- Capacity analysis: `tears.create_capacity_tear_sheet(...)`

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints (mapping suggestion):

- `analyze.perf_stats` → `timeseries.perf_stats`  
  Computes core strategy statistics.

- `analyze.drawdowns` → `timeseries.get_top_drawdowns`, `gen_drawdown_table`  
  Returns worst drawdown periods and summary tables.

- `analyze.rolling_metrics` → `timeseries.rolling_beta`, `rolling_volatility`, `rolling_sharpe`  
  Rolling risk and factor sensitivity metrics.

- `report.tear_sheet.simple` → `tears.create_simple_tear_sheet`  
  Fast all-in-one summary.

- `report.tear_sheet.full` → `tears.create_full_tear_sheet`  
  Comprehensive report with optional benchmark/factor/capacity sections.

- `report.tear_sheet.returns` → `tears.create_returns_tear_sheet`  
  Returns-focused diagnostics.

- `report.tear_sheet.positions` → `tears.create_position_tear_sheet`  
  Position concentration and exposure views.

- `report.tear_sheet.transactions` → `tears.create_txn_tear_sheet`  
  Turnover, volume, slippage-oriented insights.

- `report.tear_sheet.round_trips` → `tears.create_round_trip_tear_sheet`  
  Trade lifecycle and profitability attribution.

- `report.tear_sheet.capacity` → `tears.create_capacity_tear_sheet`  
  Liquidity and liquidation stress checks.

- `analyze.factor_attribution` → `perf_attrib.perf_attrib`, `create_perf_attrib_stats`  
  Factor exposure and contribution attribution.

---

## 5) Common Issues and Notes

- **Input format is critical**: use clean pandas Series/DataFrames with aligned datetime indexes.
- **Timezone handling**: normalize to UTC where needed (`utils.to_utc`).
- **Intraday strategies**: run intraday checks/estimation (`utils.detect_intraday`, `estimate_intraday`) before reporting.
- **Large datasets**: full tear sheets and plotting can be slow; prefer targeted endpoints in production.
- **Matplotlib backend issues** (headless servers): configure non-interactive backend (e.g., Agg).
- **Zipline-specific helpers**: `extract_rets_pos_txn_from_zipline` requires zipline-compatible objects.
- **Version compatibility**: pyfolio is mature but older; pin dependency versions in reproducible environments.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/quantopian/pyfolio
- Package docs index (repo): `docs/index.md`
- Change log: `WHATSNEW.md`
- Key source modules:
  - `pyfolio/timeseries.py`
  - `pyfolio/tears.py`
  - `pyfolio/plotting.py`
  - `pyfolio/perf_attrib.py`
  - `pyfolio/capacity.py`
  - `pyfolio/round_trips.py`
  - `pyfolio/txn.py`
  - `pyfolio/utils.py`