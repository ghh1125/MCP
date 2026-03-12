# Backtrader MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical interface to the `backtrader` engine for strategy backtesting, optimization, and analysis.

Core capabilities:
- Run backtests with `Cerebro`
- Load market data from CSV/Pandas and supported connectors
- Execute strategies based on `Strategy`
- Simulate execution with `BackBroker`
- Collect performance metrics via analyzers (Sharpe, Drawdown, Returns, TradeAnalyzer, etc.)
- Optional plotting/reporting integrations

Repository: https://github.com/mementum/backtrader

---

## 2) Installation Method

### Requirements
- Python 3.x
- `setuptools` (for package install)

### Optional dependencies (feature-based)
- `matplotlib` for plotting
- `pandas` for DataFrame feeds
- `numpy` for analytics paths
- `TA-Lib` for `backtrader.talib`
- Interactive Brokers stack for IB integration
- OANDA stack for OANDA integration
- `pyfolio` for pyfolio analyzer workflows
- InfluxDB client for influx feed utilities

### Install
- From PyPI:
  - `pip install backtrader`
- From source:
  - `git clone https://github.com/mementum/backtrader.git`
  - `cd backtrader`
  - `pip install .`

---

## 3) Quick Start

### Minimal programmatic flow
1. Create `Cerebro()`
2. Add a data feed (`bt.feeds.*`)
3. Add a strategy (`bt.Strategy` subclass)
4. Optionally add analyzers/observers
5. Call `cerebro.run()`
6. Optionally call `cerebro.plot()`

### Minimal usage example
import backtrader as bt

class MyStrategy(bt.Strategy):
    def next(self):
        if not self.position:
            self.buy(size=1)

cerebro = bt.Cerebro()
data = bt.feeds.YahooFinanceCSVData(dataname='datas/orcl-2014.txt')
cerebro.adddata(data)
cerebro.addstrategy(MyStrategy)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
results = cerebro.run()
print(results[0].analyzers.sharpe.get_analysis())

### CLI quick run
- Main CLI: `btrun`
- Utility wrapper: `tools/bt-run.py`
- Data utility: `tools/yahoodownload.py`
- Data rewrite utility: `tools/rewrite-data.py`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints mapped to repository capabilities:

- `run_backtest`
  - Execute a strategy with given data, broker settings, and runtime parameters.
- `optimize_strategy`
  - Run parameter sweeps/optimization through `Cerebro` optimization mode.
- `list_analyzers`
  - Return available analyzers (e.g., Sharpe, DrawDown, Returns, SQN, TradeAnalyzer).
- `run_analyzers`
  - Attach selected analyzers and return computed metrics.
- `list_data_feeds`
  - Show supported feed adapters (CSV, Pandas, Yahoo CSV, IB/OANDA where configured).
- `validate_data_source`
  - Validate feed format/path and date/time alignment before execution.
- `plot_results`
  - Generate plots when plotting dependencies are installed.
- `run_cli_btrun`
  - Execute backtesting via `btrun` argument model for batch/legacy compatibility.
- `download_yahoo_data`
  - Wrapper around `tools/yahoodownload.py`.
- `rewrite_data`
  - Wrapper around `tools/rewrite-data.py`.

---

## 5) Common Issues and Notes

- No modern lockfile/pyproject metadata in analyzed output: use source install and explicit dependency pinning in your own environment.
- Plotting failures usually mean missing `matplotlib`.
- Pandas feed usage requires `pandas`.
- TA-Lib features require native TA-Lib installation plus Python bindings.
- Broker/store integrations (IB/OANDA) need separate credentials and vendor SDK dependencies.
- Large optimizations can be CPU/memory heavy; start with narrow parameter grids.
- Timeframe mixing/resampling/replay can produce alignment surprises; validate with sample scripts in `samples/`.
- Prefer deterministic test datasets (see `datas/`) for CI and reproducible MCP (Model Context Protocol) responses.

---

## 6) Reference Links or Documentation

- Upstream repository: https://github.com/mementum/backtrader
- Core engine: `backtrader/cerebro.py`
- Strategy base: `backtrader/strategy.py`
- Data feed base: `backtrader/feed.py`
- Broker base/default broker: `backtrader/broker.py`, `backtrader/brokers/bbroker.py`
- Analyzer base and implementations: `backtrader/analyzer.py`, `backtrader/analyzers/`
- CLI runner: `backtrader/btrun/btrun.py`
- Practical examples: `samples/`
- Tests for behavior reference: `tests/`