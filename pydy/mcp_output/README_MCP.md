# PyDy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **PyDy** capabilities for symbolic-to-numeric multibody dynamics workflows.

It is designed for developers who want to:
- build equations of motion from SymPy mechanics objects,
- generate fast ODE right-hand-side functions,
- simulate dynamical systems,
- optionally prepare visualization artifacts.

Core mapped modules:
- `pydy.system.System`
- `pydy.models` (`multi_mass_spring_damper`, `n_link_pendulum_on_cart`)
- `pydy.codegen` (`generate_ode_function`, C/Cython/Octave matrix generators)
- `pydy.viz` (`Scene`, `VisualizationFrame`, cameras/lights/shapes)

---

## 2) Installation Method

### Requirements
- Python
- `sympy`
- `numpy`
- `scipy`

Optional (feature-dependent):
- `cython` (accelerated codegen paths)
- `theano` (legacy backend support)
- `matplotlib`
- `IPython` / Jupyter

### Install
- Install from PyPI:
  `pip install pydy`
- Or from source repository:
  `pip install .`

If developing locally:
- `setup.py` is present (no `pyproject.toml` in this snapshot).

---

## 3) Quick Start

### A. Use a built-in model
1. Import a model factory from `pydy.models` (e.g., `multi_mass_spring_damper`).
2. Build equations with desired parameters.
3. Create a `System` instance.
4. Set constants, initial conditions, and time vector.
5. Integrate.

Typical flow:
- build symbolic model → create `System` → `integrate()`.

### B. Generate ODE functions directly
Use `pydy.codegen.ode_function_generators.generate_ode_function` to convert symbolic mass-matrix/forcing forms into callable numeric RHS functions (NumPy/Cython/etc. depending on backend availability).

### C. Visualization
Use `pydy.viz.Scene` + `VisualizationFrame` and geometry objects from `pydy.viz.shapes` for browser-based scene output when needed.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints for this repository:

- `build_system_from_model`
  - Create a `System` from built-in model constructors (`multi_mass_spring_damper`, `n_link_pendulum_on_cart`).

- `configure_system`
  - Set constants, specified inputs, initial conditions, and integration timeline.

- `integrate_system`
  - Run numerical simulation through `System` integration workflow.

- `generate_ode_function`
  - Produce high-performance RHS callables from symbolic equations (`pydy.codegen.ode_function_generators`).

- `export_matrix_code`
  - Generate C/Cython/Octave matrix code via `CMatrixGenerator`, `CythonMatrixGenerator`, or `OctaveMatrixGenerator`.

- `create_visual_scene`
  - Build visualization scene descriptors using `Scene`, cameras, lights, and shape primitives.

- `list_example_scripts`
  - Enumerate example dynamics problems under `examples/` for reproducible templates.

---

## 5) Common Issues and Notes

- Backend availability affects performance:
  - Pure NumPy path is easiest.
  - Cython path is faster but requires compiler toolchain.
- Symbolic model size can grow quickly:
  - large systems may have long codegen/simplification times.
- Version compatibility:
  - keep `sympy`, `numpy`, and `scipy` in mutually compatible versions.
- Visualization stack may require notebook/browser context and static assets.
- This project includes many reference examples (Kane 1985 set + practical demos); use them to validate environment setup.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pydy/pydy
- Package modules of interest:
  - `pydy/system.py`
  - `pydy/models.py`
  - `pydy/codegen/ode_function_generators.py`
  - `pydy/viz/scene.py`
- Examples directory: `examples/` (double pendulum, rolling disc, rattleback, n-pendulum, etc.)
- License: `LICENSE.txt` (BSD-style, see repository)