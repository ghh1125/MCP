# PyMC Marketing MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes practical, developer-friendly operations around the `pymc-marketing` library for:

- Marketing Mix Modeling (MMM): build, fit, evaluate, and analyze media impact
- Budget optimization: allocate spend using fitted MMM outputs
- CLV modeling: transaction frequency and monetary value models
- Customer choice modeling: multinomial, nested, and mixed logit workflows
- Config-driven model setup via YAML for low-friction integration

Core service targets in this repo map to:
- `MMM`, `MultidimensionalMMM`, `BudgetOptimizer`
- `build_mmm_from_yaml`
- `BetaGeoModel`, `GammaGammaModel`
- `MNLogitModel`, `NestedLogitModel`, `MixedLogitModel`
- `FivetranConfig`, `FivetranDataSet`

---

## 2) Installation Method

### Requirements

- Python 3.10+ recommended
- Core dependencies: `numpy`, `pandas`, `pymc`, `pytensor`, `arviz`, `scipy`, `xarray`
- Optional (feature-dependent): `matplotlib`, `seaborn`, `plotly`, `streamlit`, `mlflow`, `pydantic`, `pyyaml`

### Install

- From PyPI (library usage):
  - `pip install pymc-marketing`
- From source (service development):
  - `git clone https://github.com/pymc-labs/pymc-marketing.git`
  - `cd pymc-marketing`
  - `pip install -e .`

If you use Conda, check `environment.yml` in the repository for a reproducible environment.

---

## 3) Quick Start

### A) YAML-first MMM flow (recommended for MCP (Model Context Protocol) service integration)

1. Prepare a model YAML config (examples in `data/config_files/`).
2. Build model from config with `build_mmm_from_yaml`.
3. Fit model with your data.
4. Generate summaries and run optimization using `BudgetOptimizer`.

Typical service flow:
- `mmm.build_from_yaml` → `mmm.fit` → `mmm.summary` → `mmm.optimize_budget`

### B) Programmatic MMM flow

1. Instantiate `MMM` (or `MultidimensionalMMM` for hierarchical/multi-axis setups).
2. Fit with prepared dataframe(s).
3. Run diagnostics/evaluation and contribution analysis.
4. Optimize allocation using fitted posterior outputs.

### C) CLV flow

- Fit `BetaGeoModel` for purchase frequency/retention behavior.
- Fit `GammaGammaModel` for spend/value.
- Combine outputs for CLV-oriented decisions.

### D) Customer choice flow

- Use `MNLogitModel`, `NestedLogitModel`, or `MixedLogitModel` based on substitution structure and heterogeneity needs.
- Fit on choice-format data and extract elasticities / preference effects.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoint surface (developer-oriented):

- `mmm.build_from_yaml`
  - Build MMM object from YAML configuration (`build_mmm_from_yaml`).

- `mmm.fit`
  - Fit `MMM` or `MultidimensionalMMM` on input data.

- `mmm.evaluate`
  - Compute model quality/diagnostic metrics.

- `mmm.summary`
  - Return posterior summaries and contribution-level outputs.

- `mmm.optimize_budget`
  - Run budget allocation with `BudgetOptimizer`.

- `clv.fit_beta_geo`
  - Train `BetaGeoModel` on transaction-frequency style inputs.

- `clv.fit_gamma_gamma`
  - Train `GammaGammaModel` on monetary value inputs.

- `choice.fit_mnl`
  - Fit `MNLogitModel`.

- `choice.fit_nested_logit`
  - Fit `NestedLogitModel`.

- `choice.fit_mixed_logit`
  - Fit `MixedLogitModel`.

- `data.load_fivetran`
  - Parse/validate Fivetran-style marketing datasets (`FivetranConfig`, `FivetranDataSet`).

Note: The repository does not expose a first-class package CLI entrypoint; service orchestration should call Python APIs directly.

---

## 5) Common Issues and Notes

- Sampling cost:
  - PyMC-based Bayesian inference can be slow on large datasets; tune draws/chains and feature space.
- Environment stability:
  - Prefer pinned environments (`environment.yml`) for reproducibility.
- Optional dependency gaps:
  - Plotting/MLflow/Streamlit functions require extra packages.
- Data shape/schema:
  - Most failures come from column naming, dimensions, or time indexing mismatches.
- Complexity:
  - Multidimensional and hierarchical MMM configurations are powerful but non-trivial—start from provided YAML examples.
- Intrusiveness risk:
  - Medium; keep MCP (Model Context Protocol) service wrappers thin and configuration-driven to reduce breakage during upstream upgrades.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/pymc-labs/pymc-marketing
- Main docs index: `docs/source/index.md`
- API docs entry: `docs/source/api/index.md`
- MMM guide: `docs/source/guide/mmm/mmm_intro.md`
- CLV guide: `docs/source/guide/clv/clv_intro.md`
- Customer choice guides:
  - `docs/source/guide/customer_choice/incrementality_intro.md`
  - `docs/source/guide/customer_choice/mv_its_intro.md`
- Config examples: `data/config_files/`
- Contribution/development: `CONTRIBUTING.md`