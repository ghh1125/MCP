# Qlib MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps key capabilities of [Microsoft Qlib](https://github.com/microsoft/qlib) for quantitative research workflows.  
It is designed for AI-agent or developer-driven automation of:

- Qlib environment initialization
- Data access (calendar, instruments, features)
- Dataset handling and preprocessing pipelines
- Model training/evaluation workflow execution
- Backtesting and experiment tracking

Core Qlib domains exposed by this service include `data`, `model`, `workflow`, `backtest`, and selected `contrib` strategies/models.

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ recommended
- OS: Linux/macOS preferred (Windows possible with extra setup)
- Sufficient disk for market data cache

### Install package
pip install pyqlib

### Install common runtime dependencies
pip install numpy pandas pyyaml mlflow ruamel.yaml requests python-dateutil

### Optional model/backtest extras
pip install lightgbm xgboost catboost torch tensorflow cvxpy plotly yfinance baostock

### If running from source
git clone https://github.com/microsoft/qlib.git  
cd qlib  
pip install -e .

---

## 3) Quick Start

### Initialize Qlib
import qlib  
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data")

### Run a workflow from config
# CLI style typically used in production automation:
qlib-run path/to/workflow_config.yaml

### Access data via provider layer
from qlib.data import D  
# Typical calls include instruments, calendar, and feature retrieval through D.*

### Backtest entry
from qlib.backtest import backtest  
# Execute strategy + executor config to get report artifacts

### Recorder / experiment tracking
from qlib.workflow import R  
# Use R for experiment lifecycle and artifact logging (MLflow-backed in common setups)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `init_environment`
  - Initialize Qlib runtime (`qlib.init`) with provider URI, region, cache options.

- `run_workflow`
  - Execute YAML-based training/evaluation task (equivalent to `qlib-run` behavior).

- `get_data_snapshot`
  - Query instruments/calendar/features through `qlib.data.D`.

- `build_dataset`
  - Construct dataset/handler pipelines (e.g., `DataHandlerLP`, `Alpha158`, `Alpha360`) and return prepared segments.

- `train_model`
  - Trigger task-oriented training via trainer/workflow integration; log metrics/artifacts.

- `run_backtest`
  - Run portfolio simulation using signal strategy + execution config; return performance reports.

- `list_experiments`
  - Read experiment/recorder metadata (MLflow/Qlib recorder).

- `run_rolling`
  - Rolling train/eval execution (maps to `python -m qlib.contrib.rolling` pattern).

- `health_check`
  - Validate dependency availability, provider path, data readability, and minimal import checks.

- `get_supported_models`
  - Return available contrib models (e.g., LightGBM, XGBoost, CatBoost, PyTorch models when installed).

---

## 5) Common Issues and Notes

- Data not found:
  - Most failures come from wrong `provider_uri`. Ensure local Qlib data exists and permissions are correct.

- Optional dependency errors:
  - Many models are optional. Install only what your workflow needs (`lightgbm`, `torch`, etc.).

- MLflow tracking issues:
  - Verify MLflow backend/store config and writable artifact location.

- Performance:
  - Large feature queries and backtests are CPU/RAM intensive; enable caching and reduce universe/date range for debugging.

- Environment consistency:
  - Pin versions for `pandas`, `numpy`, and model libraries to avoid runtime incompatibilities.

- Complexity:
  - Qlib is powerful but complex; start with benchmark configs under `examples/benchmarks/*` before custom pipelines.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/microsoft/qlib
- Main documentation entry: https://github.com/microsoft/qlib/blob/main/README.md
- Examples: `examples/` and `examples/benchmarks/`
- Scripts/data tools: `scripts/`
- Rolling workflow: `qlib.contrib.rolling`
- Core modules:
  - `qlib.data`
  - `qlib.data.dataset`
  - `qlib.model.trainer`
  - `qlib.workflow`
  - `qlib.backtest`