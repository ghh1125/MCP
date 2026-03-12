# Pyomo MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the **Pyomo** ecosystem as an MCP (Model Context Protocol) interface so LLM agents and developer tools can:

- Build optimization models (LP/MILP/NLP/MINLP, GDP, DAE, MPEC)
- Validate model structure (variables, constraints, objective, sets, params)
- Solve models through installed solvers
- Inspect and summarize results (status, objective, variable values)
- Convert/export models (LP/MPS/NL and related representations)

Pyomo is a large, production-grade optimization framework. This MCP (Model Context Protocol) service focuses on practical workflows for model creation, solve orchestration, and result reporting.

---

## 2) Installation Method

### Prerequisites
- Python 3.x
- pip
- At least one optimization solver available in PATH or via Python API

### Install core package
pip install pyomo ply

### Common optional dependencies
pip install numpy scipy sympy pandas pyyaml openpyxl xlrd networkx matplotlib

### Solver-specific extras (install only what you use)
- HiGHS: pip install highspy
- Gurobi: install gurobipy (requires licensed Gurobi)
- CPLEX: install cplex (requires licensed CPLEX)
- IPOPT interface: pip install cyipopt (plus native IPOPT libs)
- Others: mosek, xpress, casadi, mpi4py as needed

### Verify CLI
pyomo --help

---

## 3) Quick Start

### Python workflow
- Import high-level API from `pyomo.environ`
- Define `ConcreteModel` or `AbstractModel`
- Add `Var`, `Constraint`, `Objective`, `Set`, `Param`
- Solve via `SolverFactory("<solver_name>")`
- Read objective/variable values using `value(...)`

Typical solver names:
- `highs`
- `glpk`
- `cbc`
- `gurobi`
- `cplex`
- `ipopt`

### CLI workflow
Use the `pyomo` command for solve/convert/help driven scripting workflows in CI or terminal automation.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `health`
  - Check service readiness, Python/runtime version, and solver discovery status.

- `list_services`
  - Return supported service operations and argument schema.

- `model.validate`
  - Validate model structure (component existence, dimensions, domains, constraints/objective presence).

- `model.solve`
  - Solve a model with selected solver and options; return solve status and termination condition.

- `model.results`
  - Fetch objective value, selected variable values, duals/suffixes (if available), and summary stats.

- `model.convert`
  - Export/convert model to target representation (e.g., LP, MPS, NL) when supported.

- `solver.list`
  - List detected/available solver interfaces in the current environment.

- `solver.check`
  - Check whether a specific solver is available and runnable.

- `examples.list`
  - List packaged example families (DAE, GDP, kernel, tutorials, etc.) for quick onboarding.

- `examples.run`
  - Execute a selected example with configurable solver/options for smoke tests.

---

## 5) Common Issues and Notes

- **No solver found**: Pyomo installs modeling APIs, not solver binaries. Install/configure at least one solver.
- **License errors**: Commercial solvers (e.g., Gurobi/CPLEX/MOSEK/XPRESS) require valid licenses.
- **Native library issues**: IPOPT/cyipopt and some advanced stacks may require OS-level dependencies.
- **Large model performance**:
  - Prefer persistent/direct solver interfaces when appropriate.
  - Avoid unnecessary expression rebuilding.
  - Use sparse/indexed modeling patterns.
- **Optional package import failures**: Many Pyomo modules degrade gracefully; install extras only for required features.
- **Complex repository**: Pyomo includes many advanced domains; keep MCP (Model Context Protocol) surface minimal and task-focused for reliability.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/Pyomo/pyomo
- Main docs entry: https://pyomo.readthedocs.io/
- Local docs source in repo: `doc/OnlineDocs/`
- CLI entry module: `pyomo.scripting.pyomo_main`
- High-level API: `pyomo.environ`
- Solver factory API: `pyomo.opt.base.solvers.SolverFactory`