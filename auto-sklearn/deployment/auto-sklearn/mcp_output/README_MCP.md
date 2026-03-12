# auto-sklearn MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `auto-sklearn` library as an MCP (Model Context Protocol) service for automated machine learning workflows.

Primary capabilities:
- Train classification and regression models with minimal manual tuning
- Run Bayesian/SMBO-based model and hyperparameter search
- Build ensembles from top candidate pipelines
- Support sklearn-like fit/predict/score interactions
- Configure custom metrics and resource budgets (time/memory)

Core integration targets:
- `AutoSklearnClassifier`
- `AutoSklearnRegressor`
- `AutoSklearn2Classifier` (experimental)
- Metrics via `autosklearn.metrics`

---

## 2) Installation Method

### System and Python requirements
`auto-sklearn` has compiled/runtime dependencies and is heavier than typical sklearn-only stacks.

Recommended:
- Python 3.8–3.11 (match upstream compatibility for your chosen release)
- Linux/macOS preferred for smoother dependency resolution
- Build tools available (C/C++ toolchain) for some environments

### Python dependencies (typical)
- Required: `numpy`, `scipy`, `scikit-learn`, `pandas`, `joblib`, `ConfigSpace`, `smac`, `dask`, `distributed`, `threadpoolctl`, `typing_extensions`
- Often useful/optional: `liac-arff`, `pynisher`, `pyyaml`, `matplotlib`, `openml`

### Install commands
- Install latest stable from PyPI: `pip install auto-sklearn`
- Or install from source repo root: `pip install -e .`

For reproducible environments, pin versions in your own `requirements.txt` or lockfile.

---

## 3) Quick Start

### Minimal classification flow
1. Load data (numpy/pandas)
2. Initialize `AutoSklearnClassifier` with search budget (`time_left_for_this_task`, `per_run_time_limit`)
3. Call `fit(X_train, y_train)`
4. Call `predict(X_test)` and `score(X_test, y_test)`
5. Optionally inspect ensemble/models via estimator methods

### Minimal regression flow
Same pattern, using `AutoSklearnRegressor`.

### MCP (Model Context Protocol) service usage pattern
Expose these as service operations:
- `train_classifier`
- `train_regressor`
- `predict`
- `score`
- `list_models` / `show_models`
- `get_leaderboard` (if implemented in your service layer)

Use a persistent model artifact directory so trained runs can be reused across MCP (Model Context Protocol) sessions.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints for this repo:

- `health_check`  
  Returns service status, version, and dependency readiness.

- `train_classifier`  
  Trains `AutoSklearnClassifier` with provided dataset, metric, and time limits.

- `train_regressor`  
  Trains `AutoSklearnRegressor` with provided dataset, metric, and time limits.

- `predict`  
  Runs inference using a stored trained model ID/artifact.

- `score`  
  Evaluates trained model performance on labeled data.

- `show_models`  
  Returns ensemble members / selected pipelines summary.

- `get_search_summary`  
  Returns run history, best score over time, and optimization metadata.

- `list_metrics`  
  Returns supported metrics/scorers from `autosklearn.metrics`.

- `set_resource_limits`  
  Configures task-level/per-run time and memory constraints.

Note: This repository is library-first; no stable packaged end-user CLI is the main entrypoint.

---

## 5) Common Issues and Notes

- Dependency complexity: `auto-sklearn` may fail to install if compiler/runtime prerequisites are missing.
- Runtime cost: model search can be CPU/memory intensive; start with small budgets.
- First-run latency: initial search and ensemble building can take significant time.
- Reproducibility: set random seeds and pin dependency versions.
- Parallelism: Dask/distributed setup can improve throughput but increases operational complexity.
- Data validation: mixed feature types are supported, but input schema consistency is critical.
- Environment stability: prefer containerized deployment for MCP (Model Context Protocol) services.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/automl/auto-sklearn
- Project docs (root doc config and examples in repo): `doc/` and `examples/`
- Main user-facing modules:
  - `autosklearn/estimators.py`
  - `autosklearn/automl.py`
  - `autosklearn/metrics/__init__.py`
- Contribution and setup details:
  - `CONTRIBUTING.md`
  - `pyproject.toml`
  - `requirements.txt`