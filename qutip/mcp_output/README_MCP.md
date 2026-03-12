# QuTiP MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core QuTiP capabilities so LLM agents and developer tools can run common quantum simulation tasks through stable service endpoints.

Main capabilities:
- Build quantum objects (`Qobj`), operators, and states
- Run time evolution for closed/open systems (`sesolve`, `mesolve`, `mcsolve`)
- Compute steady states and propagators
- Calculate expectations and phase-space functions (Wigner/Q)
- Generate visualization-ready outputs (Bloch, matrix/state plots)

Target users: developers integrating quantum simulation into automation workflows, assistants, and internal tooling.

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Required packages:
  - `numpy`
  - `scipy`
  - `packaging`
- Optional (feature-dependent):
  - `matplotlib` (visualization)
  - `cython` (build/perf extensions)
  - `mpi4py` (parallel/distributed workloads)
  - MKL stack (accelerated sparse operations)

### Install QuTiP
- `pip install qutip`

### For development/testing
- `pip install -e .`
- `pip install pytest`

---

## 3) Quick Start

Minimal workflow:
1. Create operators/states (`sigmax`, `basis`, `ket2dm`, etc.)
2. Define Hamiltonian and optional collapse operators
3. Call solver endpoint (`sesolve` or `mesolve`)
4. Read `Result` payload (`states`, expectation values, metadata)

Example flow (conceptual):
- Build a qubit Hamiltonian with Pauli operators
- Evolve over a time grid with `sesolve`
- Request expectation values via `expect`
- Return structured JSON-compatible result for downstream tools

Common high-value functions:
- `qutip.core.operators`: `destroy`, `create`, `qeye`, `sigmax`, `sigmay`, `sigmaz`, `num`
- `qutip.core.states`: `basis`, `fock`, `coherent`, `ket2dm`
- `qutip.core.tensor`: `tensor`
- `qutip.solver`: `sesolve`, `mesolve`, `mcsolve`, `steadystate`, `propagator`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints for this repository:

- `qobj.create`
  - Create/validate `Qobj` payloads (state/operator/superoperator metadata).

- `operators.generate`
  - Build common operators (`qeye`, Pauli, ladder, number operators).

- `states.generate`
  - Build basis/Fock/coherent states and density matrices.

- `tensor.compose`
  - Compose multipartite systems via tensor products.

- `simulation.se_solve`
  - Closed-system Schrödinger evolution (`sesolve`).

- `simulation.me_solve`
  - Open-system master equation evolution (`mesolve`).

- `simulation.mc_solve`
  - Monte Carlo trajectory evolution (`mcsolve`).

- `simulation.steady_state`
  - Compute Lindbladian steady states (`steadystate`).

- `simulation.propagator`
  - Generate propagators/channels over time (`propagator`).

- `analysis.expectation`
  - Compute expectation values (`expect`) on returned states.

- `analysis.wigner`
  - Compute Wigner/Q functions (`wigner`, `qfunc`).

- `visualization.bloch`
  - Produce Bloch-sphere plotting data/instructions.

- `visualization.matrix`
  - Matrix histograms/Hinton-friendly data for UI rendering.

---

## 5) Common Issues and Notes

- Version/environment mismatches:
  - Use a clean virtual environment.
  - Pin `numpy/scipy/qutip` for reproducibility.

- Performance:
  - Large Hilbert spaces scale quickly in memory/time.
  - Prefer sparse-friendly formulations when possible.
  - Consider MKL/parallel options for heavy workloads.

- Numerical stability:
  - Validate dimensions and Hermiticity where expected.
  - Use solver options/tolerances suited to stiff dynamics.

- Visualization in headless environments:
  - Configure non-interactive matplotlib backend if rendering on servers/CI.

- Monte Carlo runs:
  - Set random seeds and trajectory counts explicitly for reproducible statistics.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/qutip/qutip
- QuTiP main docs: https://qutip.org/docs/latest/
- Repository README: https://github.com/qutip/qutip/blob/master/README.md
- Contribution guide: https://github.com/qutip/qutip/blob/master/CONTRIBUTING.md
- License: https://github.com/qutip/qutip/blob/master/LICENSE.txt