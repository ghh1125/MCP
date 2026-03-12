# SymPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core SymPy capabilities so LLM agents can perform reliable symbolic math operations through structured service calls.

Main capabilities:
- Parse math strings into symbolic expressions
- Simplify symbolic expressions
- Solve equations/systems
- Compute integrals, limits, and series expansions
- Run matrix operations
- Export expressions (LaTeX / readable string)
- Convert symbolic expressions to numeric callables (`lambdify`)

Repository source: https://github.com/sympy/sympy

---

## 2) Installation Method

### Requirements
- Python 3.10+ (recommended)
- Required runtime dependency: `mpmath`
- Optional but useful: `numpy`, `scipy`, `matplotlib`, `gmpy2`, `antlr4-python3-runtime`, `lark`, `pycosat`, `z3-solver`

### Install
pip install sympy mpmath

Optional extras:
pip install numpy scipy matplotlib gmpy2 antlr4-python3-runtime lark pycosat z3-solver

Verify:
python -c "import sympy; print(sympy.__version__)"

---

## 3) Quick Start

Typical service-backed operations map to these SymPy APIs:

from sympy import symbols, simplify, integrate, limit, series, solve, Matrix, latex
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify

x = symbols('x')

expr = parse_expr("sin(x)**2 + cos(x)**2")
print(simplify(expr))                     # 1

print(integrate(x**2, x))                 # x**3/3
print(limit((x**2 - 1)/(x - 1), x, 1))    # 2
print(series(1/(1-x), x, 0, 5))           # 1 + x + x**2 + x**3 + x**4 + O(x**5)
print(solve(x**2 - 4, x))                 # [-2, 2]

A = Matrix([[1, 2], [3, 4]])
print(A.det())                            # -2
print(latex(A))                           # LaTeX output

f = lambdify(x, x**2 + 1, "numpy")
print(f(3))                               # 10

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `parse_expression`
  - Uses: `sympy.parsing.sympy_parser.parse_expr`
  - Converts text math input to SymPy expressions.

- `sympify_expression`
  - Uses: `sympy.sympify`
  - Safer canonical conversion from Python/string objects.

- `simplify_expression`
  - Uses: `sympy.simplify`
  - General simplification pipeline.

- `solve_equation`
  - Uses: `sympy.solve`
  - Algebraic equation solving.

- `solve_set`
  - Uses: `sympy.solveset`, `linsolve`, `nonlinsolve`
  - Set-oriented solving and system solving.

- `integrate_expression`
  - Uses: `sympy.integrate`, `Integral`
  - Symbolic integration (evaluated or unevaluated).

- `compute_limit`
  - Uses: `sympy.limit`
  - Symbolic limits.

- `expand_series`
  - Uses: `sympy.series`
  - Taylor/Laurent-style expansions.

- `matrix_operations`
  - Uses: `Matrix`, `zeros`, `ones`, `eye`
  - Matrix creation and linear algebra operations.

- `to_latex`
  - Uses: `sympy.latex`
  - Expression-to-LaTeX conversion.

- `to_string`
  - Uses: `sympy.printing.str.sstr`
  - Stable readable string output.

- `lambdify_expression`
  - Uses: `sympy.lambdify`
  - Numeric function generation for NumPy/SciPy backends.

Optional operational endpoint:
- `health_check`
  - Validates import of `sympy` and key optional backends.

---

## 5) Common Issues and Notes

- Parsing safety:
  - Prefer controlled parsing/sympification paths; avoid unrestricted `eval`.
- Optional dependency gaps:
  - Some features (advanced parsing, SAT/SMT, numeric backends) require optional packages.
- Performance:
  - Symbolic solve/integrate/simplify can be expensive on large expressions.
  - Add timeouts, operation limits, and expression-size guards in service handlers.
- Determinism:
  - Some simplification/solve outputs may vary in form; normalize with `sstr` or sorted outputs.
- Testing:
  - SymPy has extensive tests, but your MCP (Model Context Protocol) service should add endpoint-level tests and input validation.
- CLI note:
  - `isympy` exists for interactive shell usage, but service integration should primarily use imports/APIs.

---

## 6) Reference Links / Documentation

- SymPy repository: https://github.com/sympy/sympy
- SymPy main docs: https://docs.sympy.org/
- Parsing docs (`parse_expr`): https://docs.sympy.org/latest/modules/parsing.html
- Solvers docs: https://docs.sympy.org/latest/modules/solvers/solvers.html
- Integrals docs: https://docs.sympy.org/latest/modules/integrals/integrals.html
- Matrices docs: https://docs.sympy.org/latest/modules/matrices/index.html
- Printing docs (LaTeX/string): https://docs.sympy.org/latest/modules/printing.html
- Lambdify docs: https://docs.sympy.org/latest/modules/utilities/lambdify.html