# Pyomo MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical interface to inspect, run, and diagnose Pyomo optimization workflows with low intrusiveness.  
It is designed for developer-facing automation (agents, assistants, CI tools) that need to:

- Build and inspect Pyomo models
- Solve models through `SolverFactory`
- Convert/export model representations (LP/NL/etc.)
- Report infeasibility and model size diagnostics

Primary integration surface: `pyomo.environ` and `pyomo.opt.base.solvers.SolverFactory`.

---

## 2) Installation

### Requirements

- Python >= 3.9
- Required package:
  - `ply`
- Recommended optional packages (depending on workflow):
  - `numpy`, `scipy`, `pandas`, `networkx`, `matplotlib`, `sympy`, `pyyaml`, `openpyxl`, `xlrd`, `lxml`, `mpi4py`
- External solver runtimes as needed:
  - `glpk`, `cbc`, `ipopt`, `gurobi`, `cplex`, `highs`, `knitro`, `baron`, `scip`, etc.

### Install commands

- Install Pyomo:
  `pip install pyomo`
- Or from source repository:
  `pip install .`
- Install optional extras/tools as needed:
  `pip install numpy scipy pandas pyyaml`

---

## 3) Quick Start

### Basic Python usage

- Import Pyomo and create a model via `pyomo.environ`
- Use `SolverFactory("<solver_name>")`
- Solve and inspect status/termination conditions
- Use diagnostics helpers:
  - `pyomo.util.infeasible.log_infeasible_constraints`
  - `pyomo.util.infeasible.log_infeasible_bounds`
  - `pyomo.util.model_size.build_model_size_report`

### CLI usage

- Main command:
  `pyomo`
- Solve:
  `pyomo solve ...`
- Convert:
  `pyomo convert ...`
- Download extensions:
  `pyomo download-extensions`

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) tool surface:

- `model.build`
  - Create/load a Pyomo model (ConcreteModel/AbstractModel workflows)

- `model.inspect`
  - Return high-level model metadata (variables, constraints, objectives, sets, params)

- `model.size_report`
  - Build and return model size report (`build_model_size_report`)

- `model.solve`
  - Solve using `SolverFactory`
  - Inputs: solver name, options, tee/log flags
  - Outputs: solver status, termination condition, objective value summary

- `model.infeasibility_report`
  - Run infeasibility diagnostics (`log_infeasible_constraints`, `log_infeasible_bounds`)

- `model.convert`
  - Convert/export to writer-backed formats (LP/NL/MPS/etc.)

- `system.solvers.list`
  - Detect and list available solver backends in current environment

- `system.health`
  - Environment checks: Python version, core deps, optional deps, solver executables

---

## 5) Common Issues and Notes

- Solver not found:
  - Ensure runtime is installed and on PATH (or configured per solver API)
- Infeasible model:
  - Run infeasibility report endpoint before changing solver settings
- Large model performance:
  - Use size report first; persistent/direct interfaces may reduce overhead in repeated solves
- Optional dependency errors:
  - Install only what your workflow needs (e.g., `pandas` for table/data-heavy flows)
- Native extension features:
  - Some advanced components (e.g., parts of PyNumero stack) may require extra build/runtime setup
- CI stability:
  - Pin Python + solver versions for reproducible runs

---

## 6) Reference Links

- Repository: https://github.com/Pyomo/pyomo
- Root README: https://github.com/Pyomo/pyomo/blob/main/README.md
- Contributing: https://github.com/Pyomo/pyomo/blob/main/CONTRIBUTING.md
- Changelog: https://github.com/Pyomo/pyomo/blob/main/CHANGELOG.md
- Docs source: `doc/OnlineDocs/` in repository
- Key modules:
  - `pyomo.environ`
  - `pyomo.opt.base.solvers.SolverFactory`
  - `pyomo.scripting.pyomo_main`
  - `pyomo.util.infeasible`
  - `pyomo.util.model_size`