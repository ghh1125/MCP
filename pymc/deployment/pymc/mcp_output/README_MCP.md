# PyMC MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes **PyMC** as a developer-friendly probabilistic modeling backend.  
It is designed for LLM/agent workflows that need to:

- Define Bayesian models
- Run posterior inference (primarily MCMC/NUTS)
- Generate prior/posterior predictive samples
- Export results to ArviZ `InferenceData` for diagnostics and analysis

Core capabilities come from `pymc.model`, `pymc.distributions`, `pymc.sampling`, `pymc.variational`, and `pymc.backends.arviz`.

---

## 2) Installation Method

### Requirements
- Python 3.10+ (recommended)
- Core deps: `numpy`, `scipy`, `pytensor`, `arviz`, `pandas`, `xarray`, `cloudpickle`, `rich`, `typing-extensions`
- Optional acceleration/features: `jax`, `jaxlib`, `numba`, `zarr`, `matplotlib`, `graphviz`, `pydot`

### Install
- From PyPI:
  - `pip install pymc`
- Optional extras (as needed):
  - `pip install jax jaxlib`
  - `pip install zarr matplotlib graphviz pydot`

For MCP (Model Context Protocol) integration, register this service in your MCP host config and point tool handlers to the functions listed below.

---

## 3) Quick Start

### Typical workflow
1. Create a model context (`pymc.Model`)
2. Add priors/likelihood using distributions (e.g., `Normal`, `Bernoulli`, `Poisson`)
3. Run `sample()` for posterior draws
4. Run predictive sampling (`sample_prior_predictive`, `sample_posterior_predictive`)
5. Convert/export with `to_inference_data`

### Minimal service call flow (conceptual)
- `create_model` → `add_distribution_nodes` → `sample_mcmc` → `sample_posterior_predictive` → `to_inference_data`

Main API entrypoints:
- `pymc.sampling.mcmc.sample`
- `pymc.sampling.mcmc.init_nuts`
- `pymc.sampling.forward.sample_prior_predictive`
- `pymc.sampling.forward.sample_posterior_predictive`
- `pymc.variational.inference.fit`
- `pymc.backends.arviz.to_inference_data`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `model.create`
  - Create/initialize a `pymc.Model` context.
- `distribution.add_continuous`
  - Add continuous RVs (`Normal`, `HalfNormal`, `Gamma`, `Beta`, etc.).
- `distribution.add_discrete`
  - Add discrete RVs (`Bernoulli`, `Poisson`, `Categorical`, `Binomial`, etc.).
- `sampling.mcmc.sample`
  - Run posterior MCMC sampling (default continuous-model path: NUTS).
- `sampling.mcmc.init_nuts`
  - Initialize NUTS settings for tuned sampling starts.
- `sampling.forward.prior_predictive`
  - Draw prior predictive samples.
- `sampling.forward.posterior_predictive`
  - Draw posterior predictive samples.
- `variational.fit`
  - Run VI (`ADVI`, `FullRankADVI`) for faster approximate inference.
- `backends.to_inference_data`
  - Convert traces/predictive outputs to ArviZ `InferenceData`.
- `gp.create` (optional)
  - Gaussian Process workflows (`Latent`, `Marginal`, `MarginalSparse`).

Note: PyMC is library-first; no stable end-user CLI is the primary interface.

---

## 5) Common Issues and Notes

- **Compilation/startup cost:** First model compile can be slow (PyTensor graph build/compile).
- **Numerical stability:** Poor priors/scales can cause divergences; inspect diagnostics in ArviZ.
- **Performance tuning:** Use fewer chains/draws for iteration, then scale up for final runs.
- **JAX backend:** Optional and environment-sensitive; version mismatches are common.
- **Large traces:** Prefer chunked/backed storage (e.g., Zarr) for memory-heavy workloads.
- **Graphviz-dependent visuals:** Require system Graphviz binary in addition to Python package.
- **No first-class packaged CLI:** Use Python API-driven MCP service handlers.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pymc-devs/pymc
- PyMC docs: https://www.pymc.io
- ArviZ docs: https://python.arviz.org
- Contributor/developer docs in repo:
  - `ARCHITECTURE.md`
  - `docs/source/contributing/developer_guide.md`
  - `docs/source/contributing/running_the_test_suite.md`