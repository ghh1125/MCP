# BPt MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the **BPt** library to provide programmatic, reproducible machine-learning workflows for tabular/scientific data.

Core capabilities:
- Dataset handling with roles/scopes (`Dataset`)
- Experiment configuration (`ProblemSpec`, `Pipeline`, `ModelPipeline`)
- Model evaluation and CV (`evaluate`, `cross_val_score`, `cross_validate`, `CV`, `CVStrategy`)
- Experiment comparison/statistics (`Compare`, `CompareDict`, `CompareSubset`)
- Hyperparameter search backend support (`BPtSearchCV` via high-level APIs)

Repository: https://github.com/sahahn/BPt

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Required libs: `numpy`, `pandas`, `scikit-learn`, `scipy`, `joblib`
- Optional libs (feature-dependent): `matplotlib`, `seaborn`, `lightgbm`, `nevergrad`, `nilearn`, `xgboost`

### Install
- `pip install BPt`
- Or from source:
  - `git clone https://github.com/sahahn/BPt.git`
  - `cd BPt`
  - `pip install -e .`

For optional features, install corresponding extras manually (e.g., `pip install lightgbm nevergrad`).

---

## 3) Quick Start

### Minimal workflow
import BPt as bp
from sklearn.datasets import load_breast_cancer

raw = load_breast_cancer(as_frame=True)
df = raw.frame
df["target"] = raw.target

data = bp.Dataset(df).set_target("target")
results = bp.evaluate(data=data)

print(results.mean_scores)

### Cross-validation helpers
scores = bp.cross_val_score(data=data)
cv_out = bp.cross_validate(data=data)

### Compare experiments
# compare_obj = bp.Compare({...})
# compare_results = bp.evaluate(data=data, problem_spec=..., pipeline=..., compare=compare_obj)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `evaluate`
  - Run end-to-end training/evaluation with BPt configuration objects.
- `cross_val_score`
  - Return CV scores for quick benchmark checks.
- `cross_validate`
  - Return richer fold-level CV outputs (scores/timing/metadata).
- `get_estimator`
  - Build/resolve estimator objects from BPt configuration.
- `compare_dict_from_existing`
  - Build comparison-ready structures from existing evaluation outputs.
- `dataset_ops` (service wrapper around `Dataset`)
  - Create dataset, set target, manage roles/scopes, filtering/validation.
- `cv_config` (service wrapper around `CV`, `CVStrategy`)
  - Configure folds/splitting strategy.
- `results_ops` (service wrapper around `EvalResults`)
  - Extract means/std, predictions, feature importances, and subsets.

---

## 5) Common Issues and Notes

- Missing optional dependency errors:
  - Install only what your pipeline needs (`lightgbm`, `xgboost`, `nevergrad`, etc.).
- Data schema issues:
  - Ensure target is explicitly set (`set_target`) and columns are clean.
- Reproducibility:
  - Set random states consistently in problem/pipeline/CV configs.
- Performance:
  - Large CV + search spaces can be expensive; start with small folds/search first.
- Environment:
  - Use a virtual environment to avoid sklearn/numpy version conflicts.

---

## 6) Reference Links / Documentation

- GitHub: https://github.com/sahahn/BPt
- Main package entry: `BPt/__init__.py`
- Key modules:
  - `BPt/main/eval.py`
  - `BPt/dataset/dataset.py`
  - `BPt/main/input.py`
  - `BPt/main/compare.py`
  - `BPt/main/CV.py`
- Docs (repo-built): `docs/` and `doc/source/` in the project tree