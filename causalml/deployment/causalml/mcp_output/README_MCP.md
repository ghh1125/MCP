# causalml MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key capabilities from [uber/causalml](https://github.com/uber/causalml) so MCP (Model Context Protocol) clients can run practical causal inference workflows:

- Estimate heterogeneous treatment effects (CATE/ITE)
- Train meta-learners (S/T/X/R/DR learners)
- Use causal trees and causal forests
- Estimate and calibrate propensity scores
- Run matching for observational data
- Evaluate uplift models (Qini/gain/lift)
- Generate synthetic datasets for testing
- Optimize treatment policy decisions

It is intended for experimentation, model comparison, and production-oriented decision support.

---

## 2) Installation Method

### Python and core dependencies
Recommended: Python 3.9+ with scientific stack.

Core dependencies:
- numpy
- pandas
- scikit-learn
- scipy
- statsmodels
- matplotlib

Optional (feature-dependent):
- xgboost
- lightgbm
- shap
- seaborn
- tensorflow
- torch
- pyro-ppl

### Install causalml
pip install causalml

### Install common optional extras (as needed)
pip install xgboost lightgbm shap seaborn tensorflow torch pyro-ppl

### Verify install
python -c "import causalml; print('causalml OK')"

---

## 3) Quick Start

### A. Generate synthetic data + train a T-learner
from causalml.dataset.synthetic import synthetic_data
from causalml.inference.meta import BaseTRegressor
from xgboost import XGBRegressor

y, X, treatment, tau, b, e = synthetic_data(mode=1, n=2000, p=10, sigma=1.0)

learner = BaseTRegressor(learner=XGBRegressor())
learner.fit(X=X, treatment=treatment, y=y)
te_pred = learner.predict(X)

print(te_pred[:5])

### B. Propensity scoring + trimming
from causalml.propensity import compute_propensity_score, trim_by_propensity_score

p = compute_propensity_score(X, treatment)
X_trim, t_trim, y_trim = trim_by_propensity_score(X, treatment, y, p, cutoff=0.01)

### C. Matching
from causalml.match import nearest_neighbor_match

matched = nearest_neighbor_match(
    data=None,  # replace with your DataFrame pipeline
    treatment_col="treatment",
    score_cols=["propensity_score"]
)

### D. Uplift evaluation plots
from causalml.metrics.visualize import plot_qini, plot_gain, plot_lift

# plot_qini(y_true, uplift_score, treatment)
# plot_gain(y_true, uplift_score, treatment)
# plot_lift(y_true, uplift_score, treatment)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints (mapped to causalml modules):

- estimate_s_learner  
  Train/predict with S-learner (`BaseSRegressor`, `BaseSClassifier`)

- estimate_t_learner  
  Train/predict with T-learner (`BaseTRegressor`, `BaseTClassifier`)

- estimate_x_learner  
  Train/predict with X-learner (`BaseXRegressor`, `BaseXClassifier`)

- estimate_r_learner  
  Train/predict with R-learner (`BaseRRegressor`, `BaseRClassifier`)

- estimate_dr_learner  
  Train/predict with doubly robust learners (`BaseDRRegressor`, `BaseDRClassifier`)

- estimate_driv  
  IV-based doubly robust estimation (`BaseDRIVLearner`)

- train_causal_tree  
  Interpretable segmentation (`CausalTreeRegressor`)

- train_causal_forest  
  Tree ensemble CATE estimation (`CausalRandomForestRegressor`)

- compute_propensity  
  Propensity estimation/calibration/trimming (`compute_propensity_score`, `calibrate`, `trim_by_propensity_score`, `get_importance_weights`)

- run_matching  
  Covariate balance and nearest-neighbor matching (`create_table_one`, `nearest_neighbor_match`)

- evaluate_uplift  
  Uplift metrics/plots (`plot_qini`, `plot_gain`, `plot_lift`)

- generate_synthetic_data  
  Simulation helpers (`synthetic_data`, `simulate_randomized_trial`, etc.)

- optimize_policy  
  Policy optimization (`PolicyLearner`)

---

## 5) Common Issues and Notes

- Optional ML backends not installed  
  Some learners require extra packages (e.g., xgboost, tensorflow, torch). Install only what you need.

- Binary treatment expectations  
  Many workflows assume treatment is binary; verify encoding and input schema.

- Propensity extremes  
  Very small/large propensity scores can destabilize estimators. Use trimming and calibration.

- Small sample sizes  
  Meta-learners can overfit easily. Use cross-validation and simpler base learners first.

- Performance  
  Tree ensembles and deep models can be slow. Start with smaller datasets and tune incrementally.

- Reproducibility  
  Set random seeds consistently across NumPy, sklearn, and model backends.

- Visualization in headless environments  
  Configure matplotlib backend (e.g., Agg) if running on servers/containers.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/uber/causalml
- Main README: https://github.com/uber/causalml/blob/master/README.md
- Package source tree: `causalml/`
- Tests/examples reference: `tests/`
- Project metadata: `pyproject.toml`, `setup.py`, `setup.cfg`