# causalml MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core capabilities from [uber/causalml](https://github.com/uber/causalml) to provide practical causal inference workflows through MCP (Model Context Protocol).  
It is designed for developers who need to:

- Generate synthetic uplift/treatment-effect datasets
- Estimate treatment effects (CATE/ATE) with meta-learners (S/T/X/R/DR)
- Train causal trees/forests
- Estimate propensity scores and run matching
- Evaluate uplift models with Qini/Gain/Lift metrics
- Optimize treatment policy decisions

Typical use cases include personalized treatment assignment, campaign uplift modeling, and observational study analysis.

---

## 2) Installation Method

### Recommended environment

- Python 3.9+
- `pip` latest version
- Optional virtual environment (`venv` or `conda`)

### Core dependencies

- numpy
- pandas
- scipy
- scikit-learn
- statsmodels
- matplotlib

### Optional dependencies (feature-dependent)

- xgboost
- lightgbm
- shap
- tensorflow
- torch
- pydotplus
- seaborn

### Install commands

pip install causalml

For fuller functionality:

pip install "causalml[xgboost]"  
pip install xgboost lightgbm shap tensorflow torch seaborn pydotplus

If you are building an MCP (Model Context Protocol) wrapper service, also install your MCP runtime/SDK in the same environment.

---

## 3) Quick Start

### A. Generate synthetic data

Use dataset utilities (for example `make_uplift_classification` or `synthetic_data`) to create treatment/control samples with known uplift.

### B. Train a learner

Use a meta-learner such as:

- `BaseSRegressor`/`BaseSLearner` style
- `BaseTRegressor`
- `BaseXRegressor`
- `BaseRRegressor`
- `BaseDRRegressor`

Then fit on features, treatment labels, and outcomes; predict treatment effects per unit.

### C. Evaluate uplift

Use plotting utilities:

- `plot_qini`
- `plot_gain`
- `plot_lift`

to compare ranking quality across models.

### D. Propensity + matching workflow

- Estimate propensity: `compute_propensity_score`
- Match cohorts: `nearest_neighbor_match`
- Summarize covariate balance: `create_table_one`

### E. Policy optimization

Use `PolicyLearner` to convert estimated treatment effects into recommended treatment actions under constraints.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints (developer-oriented mapping):

- `dataset.make_uplift_classification`  
  Generate synthetic classification uplift data.

- `dataset.make_uplift_classification_logistic`  
  Logistic uplift data generation variant.

- `dataset.simulate_randomized_trial`  
  Simulate RCT-like data.

- `dataset.synthetic_data`  
  Regression-style synthetic causal data.

- `inference.meta.s_learner`  
  S-learner CATE estimation.

- `inference.meta.t_learner`  
  T-learner with separate treatment/control models.

- `inference.meta.x_learner`  
  X-learner for imbalanced treatment groups.

- `inference.meta.r_learner`  
  Orthogonalized R-learner estimation.

- `inference.meta.dr_learner`  
  Doubly robust treatment-effect estimation.

- `inference.tree.causal_tree`  
  `CausalTreeRegressor` for interpretable partitioning.

- `inference.tree.causal_forest`  
  `CausalRandomForestRegressor` for non-linear heterogeneous effects.

- `propensity.compute`  
  Propensity score estimation/calibration.

- `match.nearest_neighbor`  
  Nearest-neighbor matching for observational data.

- `metrics.plot_qini` / `metrics.plot_gain` / `metrics.plot_lift`  
  Uplift evaluation charts.

- `optimize.policy_learner`  
  Learn deployment policy from treatment effects.

---

## 5) Common Issues and Notes

- Optional packages missing  
  Some learners/features silently require extras (e.g., XGBoost, TensorFlow, Torch). Install only what your endpoints need.

- Version compatibility  
  Pin `numpy/scipy/scikit-learn` in production. Validate against your deployment Python version.

- Data assumptions  
  Treatment coding, outcome type (binary vs regression), and confounding assumptions must match learner choice.

- Performance  
  Tree/forest and deep-learning models can be expensive. Use sampling, feature selection, and parallel training where possible.

- Reproducibility  
  Set random seeds for data generation and model training.

- Observational data caution  
  Propensity and matching reduce bias but do not guarantee causal identification without strong assumptions.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/uber/causalml
- Main README: https://github.com/uber/causalml/blob/master/README.md
- Package source tree: `causalml/dataset`, `causalml/inference`, `causalml/metrics`, `causalml/optimize`
- Tests/examples reference: `tests/` directory for practical usage patterns

If you are exposing this as an MCP (Model Context Protocol) service, keep endpoint names stable and version your service contract as you add new learners.