# CVXPY MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a thin developer-facing interface over [CVXPY](https://github.com/cvxpy/cvxpy), a Python modeling library for convex optimization (plus selected quasiconvex, geometric, mixed-integer, and NLP workflows depending on solver support).

### Main functions
- Build optimization models from variables, parameters, objectives, and constraints.
- Solve models with available solvers (automatic or explicit selection).
- Support repeated solves via `Parameter` updates (DPP-friendly workflows).
- Expose solver capability and status metadata for downstream automation.

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended modern 3.x)
- Required runtime libraries:
  - `numpy`
  - `scipy`
- At least one solver backend (recommended defaults: `osqp`, `scs`, or `clarabel`)

### Install (minimal)
pip install cvxpy

### Install with common solvers
pip install "cvxpy[scs,osqp,clarabel]"

### Optional commercial/advanced solvers
Install separately per vendor/package, e.g. GUROBI, CPLEX, MOSEK, XPRESS, SCIP, IPOPT, KNITRO, etc., then ensure licenses/environment are configured.

---

## 3) Quick Start

### Basic modeling flow
import cvxpy as cp

x = cp.Variable()
obj = cp.Minimize((x - 1)**2)
prob = cp.Problem(obj, [x >= 0])
value = prob.solve()   # or prob.solve(solver=cp.OSQP)

print("status:", prob.status)
print("objective:", value)
print("x:", x.value)

### Parameterized repeated solve
import cvxpy as cp

x = cp.Variable()
p = cp.Parameter(nonneg=True, value=1.0)
prob = cp.Problem(cp.Minimize((x - p)**2), [x >= 0])

for v in [1.0, 2.0, 3.0]:
    p.value = v
    prob.solve()
    print(v, x.value)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service surface (practical mapping to CVXPY core APIs):

- `build_problem`
  - Create a `Problem` from objective + constraints.
  - Inputs: expression graph/spec.
  - Output: problem handle/id.

- `solve_problem`
  - Execute `Problem.solve(...)`.
  - Inputs: problem id, solver (optional), solver options (optional).
  - Output: status, objective value, variable values, timing/stats.

- `set_parameter`
  - Update `Parameter.value` for an existing problem.
  - Inputs: problem id, parameter name/id, value.
  - Output: confirmation + validation errors if any.

- `list_solvers`
  - Return installed/available solver backends and basic capability hints.
  - Backed by CVXPY solver definitions (`reductions/solvers/defines.py`).

- `get_problem_status`
  - Fetch last known solve status, infeasibility/unbounded flags, and metadata.

- `upgrade_legacy_source` (utility)
  - Wrapper for `python -m cvxpy.utilities.cvxpy_upgrade` for migration help.

---

## 5) Common Issues and Notes

- Solver not found:
  - CVXPY may install without all optional solvers. Install solver package explicitly.
- Performance:
  - Reuse a compiled model and update `Parameter` values instead of rebuilding.
- Numerical stability:
  - Try a different solver and/or scaling; inspect `prob.status` carefully.
- Mixed-integer / NLP:
  - Requires specific solver support; not all backends support all problem classes.
- Environment/licensing:
  - Commercial solvers require valid local licenses and vendor environment variables.
- Large models:
  - Prefer sparse data structures and avoid unnecessary dense matrix construction.

---

## 6) Reference Links or Documentation

- CVXPY repository: https://github.com/cvxpy/cvxpy  
- Official docs: https://www.cvxpy.org/  
- API entrypoint (`cvxpy/__init__.py`) and core model class (`cvxpy/problems/problem.py`)  
- Solver integration internals: `cvxpy/reductions/solvers/`  
- Migration utility: `python -m cvxpy.utilities.cvxpy_upgrade`