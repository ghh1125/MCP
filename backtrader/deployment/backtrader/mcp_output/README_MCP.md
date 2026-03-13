# Backtrader MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes the core capabilities of the `backtrader` engine for strategy research and backtesting through callable service endpoints.

Main functions:
- Run backtests with `Cerebro`
- Load market data (CSV, Pandas, Yahoo/Quandl-style feeds, and others)
- Execute strategies, brokers, sizers, analyzers, and observers
- Return structured performance outputs (returns, drawdown, Sharpe, trade stats, etc.)
- Support optional plotting and integration-oriented workflows

Repository analyzed: https://github.com/mementum/backtrader

---

## 2) Installation Method

### Requirements
- Python runtime
- Required: `matplotlib`
- Common optional deps: `pandas`, `numpy`, `python-dateutil`, `pytz`
- Integration-specific optional deps:
  - IB stack (`ibpy`/`ib_insync` ecosystem) for IB-related store/broker/data
  - Oanda client libs for Oanda store/broker/data
  - `TA-Lib` for `backtrader.talib`
  - `pyfolio` for PyFolio analyzer workflows

### Install
- Install backtrader:
  pip install backtrader

- Minimal plotting dependency:
  pip install matplotlib

- Recommended data stack:
  pip install pandas numpy python-dateutil pytz

---

## 3) Quick Start

### Minimal service workflow
1. Create a backtest run request
2. Provide data source (e.g., CSV or Pandas)
3. Select strategy and parameters
4. Attach analyzers (Sharpe, DrawDown, Returns, TradeAnalyzer, etc.)
5. Execute and fetch normalized results

### Typical Python usage pattern behind the service
import backtrader as bt

class SmaCross(bt.Strategy):
    params = dict(fast=10, slow=30)
    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.fast)
        sma2 = bt.ind.SMA(period=self.p.slow)
        self.crossover = bt.ind.CrossOver(sma1, sma2)
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)
data = bt.feeds.GenericCSVData(dataname="datas/2006-day-001.txt")
cerebro.adddata(data)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
cerebro.run()

In the MCP (Model Context Protocol) service, this is wrapped into endpoint calls (see below).

---

## 4) Available Tools and Endpoints List

Recommended service endpoints (developer-oriented mapping to backtrader modules):

- `health`
  - Basic readiness/liveness check.

- `list_capabilities`
  - Returns supported feeds, analyzers, observers, sizers, and integration availability.

- `run_backtest`
  - Core endpoint. Runs a backtest with:
    - strategy class/name + params
    - data config (feed type, path, timeframe/compression)
    - broker/cash/commission/slippage
    - analyzers/observers/sizers
  - Returns metrics, trades, and optional artifacts metadata.

- `optimize_strategy`
  - Runs parameter sweeps/optimization over strategy params.
  - Returns ranked result set and top configurations.

- `load_data_preview`
  - Validates data config and previews parsed bars/date range before execution.

- `list_analyzers`
  - Lists available analyzers (e.g., `SharpeRatio`, `DrawDown`, `Returns`, `TradeAnalyzer`, `TimeReturn`, `SQN`, `VWR`).

- `list_feeds`
  - Lists supported feed adapters (CSV generic/backtrader CSV, Pandas, Yahoo/Quandl-style, IB/Oanda/VC when enabled).

- `run_btrun_cli` (optional bridge)
  - Wraps `backtrader.btrun.btrun` style execution for CLI-compatible scenarios.

---

## 5) Common Issues and Notes

- Dependency gaps:
  - Core backtesting works with minimal deps, but many feeds/integrations need extra packages.
- TA-Lib and PyFolio:
  - Optional; endpoint should gracefully report “not installed” capability.
- Broker/store integrations:
  - IB/Oanda/VC modules require external vendor/client ecosystems and credentials.
- Data alignment/timeframes:
  - Multi-timeframe and replay/resample logic can be sensitive to feed configuration.
- Plotting in server environments:
  - Prefer non-interactive backends or disable plotting in headless deployments.
- Performance:
  - Strategy optimization can be CPU-heavy; use bounded parameter grids and job limits.
- Stability:
  - Import feasibility is high and intrusiveness risk is low per analysis, but integration modules vary by environment.

---

## 6) Reference Links / Documentation

- Upstream repository: https://github.com/mementum/backtrader
- Package entry points of interest:
  - `backtrader.cerebro.Cerebro`
  - `backtrader.strategy.Strategy`
  - `backtrader.feed` / `backtrader.feeds.*`
  - `backtrader.analyzers.*`
  - `backtrader.observers.*`
  - `backtrader.btrun.btrun`
- Samples directory (practical patterns):
  - `samples/` in repository root
- Tests directory (behavior references):
  - `tests/` in repository root

If you want, I can also generate a concrete endpoint I/O schema (JSON request/response shapes) for each MCP (Model Context Protocol) service endpoint.