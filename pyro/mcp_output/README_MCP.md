# Pyro MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the [Pyro](https://github.com/pyro-ppl/pyro) probabilistic programming library for developer-facing model workflows.  
It is designed for programmatic use (no built-in CLI), and focuses on:

- Defining probabilistic models (`sample`, `param`, `plate`, etc.)
- Running inference with SVI and MCMC (HMC/NUTS)
- Generating posterior predictive samples
- Inspecting and transforming model execution with effect handlers (poutine)

Best for teams building Bayesian modeling, uncertainty estimation, and probabilistic ML services on top of PyTorch.

---

## 2) Installation Method

### Requirements

Core dependencies (from analysis):

- torch
- numpy
- opt_einsum
- tqdm

Common optional dependencies:

- scipy, pandas, matplotlib
- graphviz
- funsor
- horovod

### Install (typical)

- Install PyTorch first (matching your CUDA/CPU target)
- Then install Pyro:
  - `pip install pyro-ppl`
- For development/service packaging from source repo:
  - `pip install -e .`

---

## 3) Quick Start

Minimal service flow:

1. Define a Pyro model with primitives (`pyro.sample`, `pyro.param`, `pyro.plate`)
2. Choose inference backend:
   - Variational: `pyro.infer.SVI`
   - Sampling: `pyro.infer.MCMC` + `pyro.infer.NUTS` or `HMC`
3. Run training/sampling loop
4. Produce predictions using `pyro.infer.Predictive`
5. Use poutine handlers (`trace`, `condition`, `replay`, etc.) for debugging/transforms

Typical import surface:

- `import pyro`
- `import pyro.distributions as dist`
- `from pyro.infer import SVI, Trace_ELBO, Predictive`
- `from pyro.infer.mcmc import MCMC, NUTS`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints (library-first mapping):

- `model/primitives`
  - Exposes core model operations: `sample`, `param`, `deterministic`, `factor`, `plate`, `subsample`
- `infer/svi/run`
  - Runs stochastic variational inference via `SVI`
- `infer/mcmc/run`
  - Runs MCMC with configurable kernels (`HMC`, `NUTS`)
- `infer/predictive/run`
  - Posterior predictive sampling via `Predictive`
- `poutine/trace`
  - Captures execution traces for debugging/inspection
- `poutine/transform`
  - Applies handlers like `condition`, `replay`, `mask`, `scale`, `block`, `reparam`
- `params/store`
  - Manage global parameter state (`ParamStoreDict`, clear/get helpers)
- `nn/pyromodule`
  - Integrates `PyroModule`, `PyroParam`, `PyroSample` for PyTorch module-based models

Note: The upstream project does not expose a stable first-class CLI; implement these as MCP (Model Context Protocol) service operations in your host runtime.

---

## 5) Common Issues and Notes

- **Environment mismatch**: PyTorch/CUDA version mismatch is the most common setup failure.
- **Global param store**: Pyro uses a global parameter store; clear/reset between isolated runs/tests.
- **Inference cost**: NUTS/HMC can be expensive; tune warmup, number of samples, and model complexity.
- **Validation/debugging**: Enable validation in development; disable selectively for performance-critical production paths.
- **Optional features**: Some advanced modules require optional deps (e.g., funsor, graphviz, horovod).
- **Complexity**: Repository is large and advanced; start from examples for stable patterns.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/pyro-ppl/pyro
- Official docs: https://docs.pyro.ai
- Examples directory: `examples/` in repository
- Tutorials: `tutorial/` in repository
- Tests (usage patterns): `tests/` in repository