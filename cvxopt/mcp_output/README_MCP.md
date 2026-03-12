# CVXOPT MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical wrapper around **CVXOPT** optimization capabilities for LLM/tool-based workflows.  
It focuses on exposing reliable solver calls for:

- Linear Programming (LP)
- Quadratic Programming (QP)
- Second-Order Cone Programming (SOCP)
- Semidefinite Programming (SDP)
- Cone LP/QP (`conelp`, `coneqp`)
- Convex Programming (`cp`, `cpl`)
- Geometric Programming (`gp`)

Primary integration target: `cvxopt.solvers` (backed by `coneprog.py` and `cvxprog.py`).

---

## 2) Installation Method

### Prerequisites

- Python 3.8+ recommended
- NumPy
- BLAS/LAPACK runtime
- CVXOPT compiled extensions

Optional backends/features:

- GLPK (LP/MIP-related workflows)
- DSDP (SDP backend)
- GSL
- MOSEK (commercial, via `msk.py` adapter)

### Install

1. Install core runtime:
- `pip install numpy`

2. Install CVXOPT:
- `pip install cvxopt`

3. (Optional) Build from source repository if you need custom backend linkage:
- `pip install .`

---

## 3) Quick Start

Minimal Python usage pattern for this MCP (Model Context Protocol) service is to map service calls directly to `cvxopt.solvers.*`.

Example flow:

1. Create matrices/vectors with `cvxopt.matrix` / `cvxopt.spmatrix`
2. Call solver endpoint (for example `lp`, `qp`, or `socp`)
3. Return structured result fields like status/objective/primal variables

Typical call targets:

- `cvxopt.solvers.lp(...)`
- `cvxopt.solvers.qp(...)`
- `cvxopt.solvers.socp(...)`
- `cvxopt.solvers.sdp(...)`
- `cvxopt.solvers.conelp(...)`
- `cvxopt.solvers.coneqp(...)`
- `cvxopt.solvers.cp(...)`
- `cvxopt.solvers.cpl(...)`
- `cvxopt.solvers.gp(...)`

For higher-level model construction, use `cvxopt.modeling` (`variable`, `op`, `dot`, `sum`, etc.) before solving.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `solve_lp` → wraps `solvers.lp`  
  Solve standard linear programs.

- `solve_qp` → wraps `solvers.qp`  
  Solve convex quadratic programs.

- `solve_socp` → wraps `solvers.socp`  
  Solve second-order cone constrained problems.

- `solve_sdp` → wraps `solvers.sdp`  
  Solve semidefinite programs.

- `solve_conelp` → wraps `solvers.conelp`  
  General cone LP interface.

- `solve_coneqp` → wraps `solvers.coneqp`  
  General cone QP interface.

- `solve_cp` → wraps `solvers.cp`  
  Convex programming interface.

- `solve_cpl` → wraps `solvers.cpl`  
  Convex programming with linear structure.

- `solve_gp` → wraps `solvers.gp`  
  Geometric programming interface.

- `build_model` (optional helper) → wraps `modeling.variable/op/...`  
  Build symbolic models before solving.

- `solve_with_mosek` (optional) → wraps `msk.lp/qp/ilp/socp`  
  Route to MOSEK backend when available.

---

## 5) Common Issues and Notes

- CVXOPT is not pure Python; build/runtime linkage to BLAS/LAPACK matters.
- Some features are backend-dependent (GLPK/DSDP/MOSEK may be unavailable in default installs).
- Input matrix dimensions and cone definitions must match solver expectations exactly.
- Prefer sparse matrices (`spmatrix`) for large-scale problems to reduce memory usage.
- Numerical conditioning strongly affects convergence/performance; scale inputs when possible.
- In containerized deployments, prebuild wheels or validate native library presence at startup.
- If importing fails, verify Python version, wheel compatibility, and native dependencies first.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/cvxopt/cvxopt
- Project README: https://github.com/cvxopt/cvxopt/blob/master/README.md
- Documentation (included in repo under `doc/` and `doc/html/`)
- Core modules:
  - `src/python/solvers.py`
  - `src/python/coneprog.py`
  - `src/python/cvxprog.py`
  - `src/python/modeling.py`
  - `src/python/msk.py`