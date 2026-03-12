# qpsolvers MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `qpsolvers` Python library as an MCP (Model Context Protocol) service for solving quadratic optimization problems through a unified API.

It is designed for developers who need to:
- Solve standard Quadratic Programs (QP)
- Solve constrained least-squares problems
- Work with structured `Problem` / `Solution` objects
- Switch between multiple solver backends (OSQP, Clarabel, SCS, CVXOPT, etc.) with minimal code changes

Core capabilities:
- `solve_qp`: high-level QP solve entry point
- `solve_problem`: structured solve flow using `Problem`
- `solve_ls`: constrained least-squares
- `solve_unconstrained`: unconstrained quadratic solve
- `available_solvers`: detect installed solver backends

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Required:
  - `numpy`
  - `scipy`
- Optional solver dependencies (install only what you need):
  - `osqp`, `clarabel`, `scs`, `cvxopt`, `ecos`, `highspy`, `gurobipy`, `mosek`, `piqp`, `proxsuite`, `qpalm`, `qpax`, `qpswift`, `quadprog`, etc.

### Install base package
- `pip install qpsolvers`

### Install with specific solver extras (example)
- `pip install qpsolvers[osqp]`
- `pip install qpsolvers[clarabel]`
- `pip install qpsolvers[scs]`

(Exact extras availability depends on the package release; if extras are unavailable, install solver libraries directly.)

---

## 3) Quick Start

### Minimal QP solve flow
1. Prepare QP inputs (`P, q, G, h, A, b`, bounds if needed)
2. Select a solver name (for example `osqp`)
3. Call `solve_qp(...)`
4. Check returned solution vector (`x`) or status via structured API

### Typical MCP (Model Context Protocol) usage flow
- Call a service endpoint that maps to `available_solvers` to discover installed backends
- Submit a solve request to `solve_qp` or `solve_problem`
- Receive primal solution and optional dual/status fields
- Handle infeasible/unbounded/failed statuses gracefully in client logic

### Structured approach
Use:
- `Problem` to carry matrices/vectors and constraints
- `solve_problem(problem, solver=...)`
- `Solution` for standardized outputs (primal, dual, metadata)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `available_solvers`
  - Returns solver backends currently usable in the runtime environment.

- `solve_qp`
  - Solves a quadratic program using dense or sparse inputs.
  - Main endpoint for standard QP requests.

- `solve_problem`
  - Accepts a structured `Problem` object payload and returns a structured `Solution`.
  - Best for consistent, strongly typed integrations.

- `solve_ls`
  - Solves constrained least-squares problems through the same backend abstraction.

- `solve_unconstrained`
  - Fast path for unconstrained quadratic objectives.

- `socp_from_qp` (optional utility endpoint)
  - Converts QP representation to SOCP form for compatible conic solver pipelines.

---

## 5) Common Issues and Notes

- Solver not found:
  - `qpsolvers` is a dispatcher; many solvers are optional.
  - Ensure the target solver package is installed in the same environment.

- Dense vs sparse performance:
  - Large problems should usually use sparse matrices (`scipy.sparse`) for speed and memory efficiency.

- Numerical stability:
  - Poorly scaled matrices can cause slow convergence or inaccurate results.
  - Consider normalization/scaling and solver-specific tolerances.

- Backend behavior differences:
  - Status codes, dual outputs, and tolerance handling vary by solver.
  - Keep integration logic solver-aware when strict reproducibility is required.

- Environment setup:
  - Some commercial solvers (e.g., Gurobi, MOSEK, COPT) require licenses and native dependencies.

- Error handling:
  - Always handle infeasible, unbounded, and failure states explicitly in MCP (Model Context Protocol) clients.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/qpsolvers/qpsolvers
- Main README: https://github.com/qpsolvers/qpsolvers/blob/main/README.md
- Examples: https://github.com/qpsolvers/qpsolvers/tree/main/examples
- Changelog: https://github.com/qpsolvers/qpsolvers/blob/main/CHANGELOG.md
- Contributing: https://github.com/qpsolvers/qpsolvers/blob/main/CONTRIBUTING.md