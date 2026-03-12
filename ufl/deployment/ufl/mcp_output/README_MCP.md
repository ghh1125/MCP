# UFL MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a developer-friendly interface to **UFL (Unified Form Language)** from FEniCS.  
It is designed for symbolic finite-element workflows: building variational forms, transforming expressions, differentiating forms, and extracting form metadata for downstream compilers/solvers.

Core capabilities:
- Build symbolic expressions/forms (e.g., `grad`, `div`, `inner`, `lhs`, `rhs`, `action`, `adjoint`)
- Automatic/symbolic differentiation (`derivative`, `diff`, algorithmic derivative application)
- Form and expression analysis (`extract_arguments`, `extract_coefficients`, etc.)
- Form normalization/metadata generation (`compute_form_data`)

---

## 2) Installation Method

### Requirements
- Python `>=3.9`
- `numpy`
- Optional for development/testing: `pytest`

### Install
- From PyPI:
  `pip install ufl`
- From source repository:
  `git clone https://github.com/FEniCS/ufl.git`
  `cd ufl`
  `pip install -e .`

### Verify
- `python -c "import ufl; print(ufl.__version__)"`

---

## 3) Quick Start

Create a simple symbolic form:
import ufl
cell = ufl.triangle
V = ufl.FunctionSpace(ufl.Mesh(cell), ufl.FiniteElement("Lagrange", cell, 1))
u = ufl.TrialFunction(V)
v = ufl.TestFunction(V)
a = ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx
L = ufl.Constant(cell) * v * ufl.dx

Differentiate a residual-like form:
J = ufl.derivative(L, u)

Analyze a form:
from ufl.algorithms.analysis import extract_arguments, extract_coefficients
args = extract_arguments(a)
coefs = extract_coefficients(a)

Compute normalized form data:
from ufl.algorithms.compute_form_data import compute_form_data
fd = compute_form_data(a)

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints:

- `ufl.build_expression`  
  Build symbolic expressions from operators/functions (`grad`, `div`, `inner`, `dot`, `conditional`, math functions).

- `ufl.build_form`  
  Construct `Form` objects with measures (`dx`, `ds`, `dS`) and arguments (`TestFunction`, `TrialFunction`, `Coefficient`, `Constant`).

- `ufl.transform_form`  
  Apply algebraic/form transforms (`lhs`, `rhs`, `system`, `action`, `adjoint`, replacement utilities).

- `ufl.differentiate`  
  Compute symbolic derivatives/Jacobians using UFL AD (`derivative`, `diff`, derivative algorithms).

- `ufl.analyze_form`  
  Extract static structure: arguments, coefficients, constants, type checks.

- `ufl.compute_form_data`  
  Produce backend-friendly normalized metadata/integrands (`FormData`).

- `ufl.inspect_expression`  
  DAG-level inspection, signatures/hashes, and expression diagnostics.

---

## 5) Common Issues and Notes

- UFL is a **symbolic language**, not a standalone PDE solver.  
  Use it with compatible FEM backends/compilers in the FEniCS ecosystem.
- Ensure consistent cell/element/function-space definitions; mismatches are a common source of errors.
- Complex forms and deep symbolic differentiation can be computationally heavy; cache intermediate forms when possible.
- If import/install fails, confirm Python version and `numpy` availability first.
- Run tests in source checkouts with `pytest` to validate environment integrity.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/FEniCS/ufl
- FEniCS project: https://fenicsproject.org/
- UFL source package modules of interest:
  - `ufl/__init__.py` (top-level API)
  - `ufl/algorithms/apply_derivatives.py`
  - `ufl/algorithms/analysis.py`
  - `ufl/algorithms/compute_form_data.py`
  - `ufl/form.py`

If you want, I can also generate a ready-to-use `mcp.json` service manifest for these endpoints.