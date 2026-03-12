# PyDy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core PyDy capabilities for symbolic multibody dynamics so LLM clients can:

- Build standard mechanics models quickly
- Generate fast ODE right-hand-side functions from symbolic equations
- Run numerical simulations through PyDy’s `System` workflow
- Prepare/export basic visualization scenes

Repository: https://github.com/pydy/pydy

---

## 2) Installation Method

### Required runtime
- Python 3.x
- `sympy`
- `numpy`
- `scipy`

### Optional (feature-dependent)
- `cython` (faster generated ODE functions)
- `theano` (legacy backend support)
- `matplotlib` (plotting in examples)
- `joblib` (parallel example scripts)

### Install (recommended)
- `pip install pydy sympy numpy scipy`
- Optional extras as needed:
  - `pip install cython matplotlib joblib`

If running from source:
- Clone repo and install in editable mode: `pip install -e .`

---

## 3) Quick Start

### Typical service flow

1. Create/load a symbolic model (for example from `pydy.models`)
2. Generate ODE function with `pydy.codegen.ode_function_generators.generate_ode_function`
3. Configure constants, specified inputs, and initial conditions via `pydy.system.System`
4. Integrate numerically and return trajectories

### Minimal usage pattern (service-side mapping)

- Model factory:
  - `multi_mass_spring_damper`
  - `n_link_pendulum_on_cart`
  - `spherical_pendulum`
- Simulation object:
  - `System(...)`
- Code generation:
  - `generate_ode_function(...)`
- Utilities:
  - `state_derivatives`, `sort_sympy`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `models.multi_mass_spring_damper`  
  Build a parameterized mass-spring-damper symbolic model.

- `models.n_link_pendulum_on_cart`  
  Generate symbolic equations for cart + N-link pendulum systems.

- `models.spherical_pendulum`  
  Create a spherical pendulum symbolic model.

- `system.create`  
  Initialize a PyDy `System` from equations/models.

- `system.configure`  
  Set constants, specifieds, initial conditions, and time vector.

- `system.integrate`  
  Numerically integrate system dynamics and return state trajectories.

- `codegen.generate_ode_function`  
  Produce callable RHS/ODE functions (NumPy/Lambdify/Cython/Theano paths depending on availability).

- `utils.state_derivatives`  
  Extract/manage state derivative mappings from symbolic expressions.

- `utils.sort_sympy`  
  Deterministically sort symbols/expressions for stable outputs.

- `viz.scene.create`  
  Build visualization `Scene` objects.

- `viz.scene.export_or_serve`  
  Export scene assets or serve visualization via lightweight server utilities.

Also useful script-style utilities in repo:
- `bin/benchmark_pydy_code_gen.py`
- `bin/compare_linear_systems_solvers.py`
- `bin/time_rhs.py`

---

## 5) Common Issues and Notes

- Missing optional dependencies  
  Some acceleration/visualization paths fail if `cython`, plotting libs, or JS runtime expectations are absent.

- Performance considerations  
  Large symbolic systems can be slow in pure lambdify mode. Prefer compiled generation (`cython`) for repeated runs.

- Backend compatibility  
  Theano backend is legacy; prefer current NumPy/Cython paths unless explicitly required.

- Visualization stack  
  PyDy includes bundled static JS assets, but browser/server environment still matters for interactive rendering.

- Determinism and reproducibility  
  Use consistent symbol ordering (`sort_sympy`) and fixed solver settings/time grids for repeatable outputs.

- Environment metadata in this analysis  
  Auto-detection did not confirm a modern `pyproject.toml` flow; validate install path against current upstream branch/tag.

---

## 6) Reference Links or Documentation

- Upstream repository: https://github.com/pydy/pydy
- Core modules to review:
  - `pydy/system.py`
  - `pydy/models.py`
  - `pydy/codegen/ode_function_generators.py`
  - `pydy/viz/scene.py`
- Examples directory (practical patterns):
  - `examples/simple_pendulum`
  - `examples/double_pendulum`
  - `examples/rollingdisc`
  - `examples/three_link_conical_pendulum`

If you want, I can also provide a ready-to-use MCP (Model Context Protocol) service schema (tool names, input/output JSON shapes, and error model) based on these endpoints.