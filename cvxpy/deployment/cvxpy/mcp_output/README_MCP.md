# CVXPY MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes a practical MCP (Model Context Protocol) interface for CVXPY-based mathematical optimization workflows.  
It is designed for developers who want to build, validate, and solve convex optimization problems from LLM/tooling environments.

Main capabilities:
- Build optimization models with `Variable`, `Parameter`, objectives (`Minimize` / `Maximize`), atoms, and constraints
- Run solver-backed optimization (`Problem.solve`)
- Inspect solver availability and compatibility
- Support parameterized repeated solves (DPP-style workflows)

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Required: `numpy`, `scipy`
- Recommended solver backends: `osqp`, `scs`, `clarabel`, `ecos` (install as needed)

### Install commands
- Core:
  `pip install cvxpy`
- Common open-source solvers:
  `pip install cvxpy[scs,ecos,osqp]`  
  (If extras are unavailable in your environment, install solvers directly: `pip install scs ecos osqp clarabel`)

### Verify install
- `python -c "import cvxpy as cp; print(cp.__version__)"`

---

## 3) Quick Start

### Typical flow
1. Create variables/parameters  
2. Build objective and constraints  
3. Create `Problem`  
4. Call solve and read results

Example usage pattern:
import cvxpy as cp  
x = cp.Variable(3)  
target = cp.Parameter(3)  
target.value = [1.0, 2.0, 3.0]  

objective = cp.Minimize(cp.sum_squares(x - target))  
constraints = [x >= 0, cp.sum(x) == 1]  
prob = cp.Problem(objective, constraints)  
value = prob.solve(solver="OSQP")  

print("status:", prob.status)  
print("opt value:", value)  
print("x:", x.value)

For repeated solves, update parameter values (`target.value = ...`) and call `prob.solve(...)` again.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `build_problem`  
  Build a CVXPY problem from objective, variables, constraints, and atoms.

- `solve_problem`  
  Solve a compiled problem with selected solver and options; returns status, objective value, primal values.

- `list_solvers`  
  Return installed/available solvers and basic capabilities.

- `check_solver_compatibility`  
  Validate whether a problem class is compatible with a target solver.

- `set_parameters`  
  Update `Parameter` values for fast repeated solves.

- `get_problem_summary`  
  Return model dimensions, constraint families (SOC/PSD/EXP/etc.), and DCP/DGP compliance signals.

- `get_solution`  
  Fetch variable values, duals (if available), and solver stats.

- `validate_model`  
  Run rule checks (e.g., DCP/DGP) before solve and return actionable diagnostics.

- `upgrade_legacy_syntax` (utility)  
  Wraps `cvxpy_upgrade` script-like migration helper.

- `generate_release_notes` (maintenance)  
  Developer utility