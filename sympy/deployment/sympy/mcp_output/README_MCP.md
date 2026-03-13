# SymPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes **SymPy** capabilities through MCP (Model Context Protocol) for symbolic math tasks in LLM workflows.

Main functions:
- Parse math expressions from text (`parse_expr`, `sympify`)
- Algebraic simplification (`simplify`, `factor`, `expand`)
- Calculus (`diff`, `integrate`, `limit`, `series`)
- Equation solving (`solve`, `nsolve`, `solveset`, `linsolve`, `nonlinsolve`)
- Linear algebra (`Matrix`)
- Output formatting (`latex`)

Best for: AI assistants, coding agents, and backend services that need reliable symbolic computation.

---

## 2) Installation Method

### Requirements
- Python `>=3.8`
- Required package: `sympy` (includes `mpmath` dependency in standard install)

### Install
pip install sympy

### Optional extras (recommended for broader functionality/performance)
pip install numpy scipy matplotlib gmpy2 pycosat antlr4-python3-runtime lark

---

## 3) Quick Start

### Minimal usage in your MCP (Model Context Protocol) service layer
from sympy import symbols, Eq, simplify, diff, integrate, solve, latex
from sympy.parsing.sympy_parser import parse_expr

x = symbols('x')
expr = parse_expr("x**2 + 2*x + 1")
result_simplify = simplify(expr)           # (x + 1)**2
result_diff = diff(expr, x)                # 2*x + 2
result_integral = integrate(expr, x)       # x**3/3 + x**2 + x
result_solve = solve(Eq(expr, 0), x)       # [-1]
result_latex = latex(result_simplify)      # "\\left(x + 1\\right)^{2}"

### Suggested MCP (Model Context Protocol) request flow
1. Accept user expression and task type.
2. Parse with `parse_expr` or `sympify`.
3. Route to target operation (`simplify`, `solve`, `integrate`, etc.).
4. Return both machine form (`str(expr)`) and presentation form (`latex(expr)`).

---

## 4) Available Tools and Endpoints List

Recommended service endpoints (names are suggestions):

- `parse_expression`
  - Convert user text into a SymPy expression.
  - Core APIs: `parse_expr`, `sympify`.

- `simplify_expression`
  - Perform general symbolic simplification.
  - Core APIs: `simplify`, optional `factor`/`expand`.

- `differentiate_expression`
  - Compute symbolic derivatives.
  - Core API: `diff`.

- `integrate_expression`
  - Compute symbolic antiderivatives/definite integrals.
  - Core API: `integrate` (returns `Integral` if unevaluated).

- `solve_equation`
  - Solve algebraic equations (symbolic/numeric).
  - Core APIs: `solve`, `nsolve`.

- `solve_set`
  - Set-based solving and systems.
  - Core APIs: `solveset`, `linsolve`, `nonlinsolve`.

- `matrix_operations`
  - Matrix creation and linear algebra operations.
  - Core class/API: `Matrix`.

- `render_latex`
  - Convert expressions to LaTeX.
  - Core API: `latex`.

---

## 5) Common Issues and Notes

- **Parsing safety**: Prefer controlled parsing (`parse_expr` with restricted transformations/locals) for untrusted input.
- **Unevaluated results**: Some operations may return symbolic containers (e.g., `Integral`) when closed forms are unavailable.
- **Numeric solving**: `nsolve` needs good initial guesses; poor seeds may fail.
- **Performance**: Large expressions can be expensive. Add timeouts, expression size limits, and caching in the service layer.
- **Optional dependency behavior**: Some advanced features improve with `numpy/scipy/gmpy2/pycosat/antlr4/lark`.
- **Environment consistency**: Pin SymPy version in production to avoid behavior drift across releases.

---

## 6) Reference Links or Documentation

- SymPy repository: https://github.com/sympy/sympy
- SymPy main docs: https://docs.sympy.org/
- Parsing docs (`sympy_parser`): https://docs.sympy.org/latest/modules/parsing.html
- Solvers docs: https://docs.sympy.org/latest/modules/solvers/solvers.html
- Integrals docs: https://docs.sympy.org/latest/modules/integrals/integrals.html
- Matrices docs: https://docs.sympy.org/latest/modules/matrices/index.html
- Printing/LaTeX docs: https://docs.sympy.org/latest/modules/printing.html