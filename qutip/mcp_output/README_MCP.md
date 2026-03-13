# QuTiP MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core QuTiP capabilities for quantum simulation workflows through MCP (Model Context Protocol)-style callable tools.

Primary service goals:
- Build and manipulate quantum objects (`Qobj`)
- Create common operators and states
- Run core dynamics solvers (Schrödinger, master equation, Monte Carlo)
- Compute steady states
- Generate common quantum visualizations and phase-space functions

Main mapped QuTiP areas:
- `qutip.core.qobj` (quantum object operations)
- `qutip.core.operators`, `qutip.core.states`
- `qutip.solver.sesolve`, `mesolve`, `mcsolve`, `steadystate`
- `qutip.visualization`, `qutip.bloch`, `qutip.wigner`

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Required: `numpy`, `scipy`
- Optional but useful: `matplotlib`, `cython`, `packaging`, `tqdm`, `mpi4py`, `numexpr`, `sympy`, `pillow`

### Install
- Install QuTiP:
  - `pip install qutip`
- Or install from source repository:
  - `pip install .`

If you enable visualization endpoints, also install:
- `pip install matplotlib pillow`

---

## 3) Quick Start

Typical MCP (Model Context Protocol) service flow:
1. Create operators/states (`destroy`, `create`, `basis`, `ket2dm`)
2. Build Hamiltonian/collapse operators
3. Run solver (`sesolve`/`mesolve`/`mcsolve`)
4. Post-process (`expect`, Wigner/Q-function, plots)

Example workflow (conceptual):
- Define a two-level system Hamiltonian using Pauli operators.
- Define initial state with `basis(...)`.
- Call `sesolve` for closed dynamics or `mesolve` with collapse operators for open dynamics.
- Return expectation values and optionally generate Bloch/Wigner visual outputs.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `qobj_create`
  - Create/load a `Qobj` and validate dimensions/type.

- `qobj_ops`
  - Common `Qobj` operations: dagger (`dag`), trace (`tr`), matrix exponential (`expm`), eigenstates.

- `operators_standard`
  - Generate standard operators: `destroy`, `create`, `qeye`, `sigmax`, `sigmay`, `sigmaz`.

- `states_standard`
  - Generate states: `basis`, `fock`, `coherent`, `ket2dm`.

- `solve_se`
  - Closed-system evolution via `sesolve`.

- `solve_me`
  - Open-system Lindblad/master-equation evolution via `mesolve`.

- `solve_mc`
  - Monte Carlo trajectories via `mcsolve`.

- `solve_steadystate`
  - Compute steady states via `steadystate`.

- `phase_space`
  - Compute `wigner` and `qfunc`.

- `visualize_quantum`
  - Plot helpers: `hinton`, `matrix_histogram`, `plot_wigner`, Bloch sphere rendering (`Bloch`).

---

## 5) Common Issues and Notes

- Version/environment mismatch:
  - Ensure `numpy`/`scipy` versions are compatible with your QuTiP version.
- Performance:
  - Large Hilbert spaces are expensive; prefer sparse operators and minimal truncation sizes.
- Parallel/stochastic solvers:
  - `mcsolve` and parallel workflows may require extra runtime configuration.
- Visualization in headless environments:
  - Use non-interactive matplotlib backend (for servers/CI).
- Optional acceleration:
  - Cython/OpenMP/MKL-related speedups may depend on platform/toolchain availability.
- Import feasibility is high and risk is low according to analysis, but solver complexity is medium; validate endpoint inputs carefully.

---

## 6) Reference Links / Documentation

- QuTiP repository: https://github.com/qutip/qutip
- QuTiP main README (project overview): `README.md` in repo root
- QuTiP docs source: `doc/README.md` and `doc/conf.py`
- Packaging and dependencies:
  - `pyproject.toml`
  - `setup.py`
  - `requirements.txt`