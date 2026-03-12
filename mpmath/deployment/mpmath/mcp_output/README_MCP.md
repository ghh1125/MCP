# mpmath MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the `mpmath` library to provide high-precision numerical computation for LLM/tool workflows.

It is designed for:
- Arbitrary-precision real/complex arithmetic
- Numerical calculus (integration, differentiation, root finding)
- Special functions (zeta, Bessel, elliptic, etc.)
- Matrix and linear algebra operations
- Optional interval arithmetic for enclosure-safe results

Repository: https://github.com/fredrik-johansson/mpmath

---

## 2) Installation Method

### Requirements
- Python `>=3.8`
- Required: `mpmath`
- Optional:
  - `gmpy2` (faster big-number backend in some workloads)
  - `matplotlib` (plotting/visualization scenarios)

### Install
pip install mpmath

Optional extras:
pip install gmpy2 matplotlib

---

## 3) Quick Start

### Basic usage
import mpmath as mp
mp.mp.dps = 50
print(mp.sqrt(2))
print(mp.zeta(3))
print(mp.quad(lambda x: mp.sin(x), [0, mp.pi]))

### Root finding
import mpmath as mp
f = lambda x: mp.cos(x) - x
root = mp.findroot(f, 0.7)
print(root)

### Matrix / linear algebra
import mpmath as mp
A = mp.matrix([[1, 2], [3, 4]])
print(A**-1)
print(mp.det(A))

### CLI mode
python -m mpmath

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (developer-oriented mapping to `mpmath` APIs):

- `set_precision(dps)`  
  Set decimal precision (`mp.mp.dps`) for subsequent computations.

- `evaluate(expression, dps?)`  
  Evaluate a safe mathematical expression with high precision.

- `compute_function(name, args, dps?)`  
  Call elementary/special functions such as `sqrt`, `exp`, `log`, `sin`, `cos`, `zeta`, etc.

- `integrate(function_expr, interval, method?)`  
  Numerical integration via `quad`/related quadrature routines.

- `differentiate(function_expr, x, order?)`  
  Differentiation using `diff` and related helpers.

- `find_root(function_expr, x0, x1?)`  
  Root solving via `findroot`.

- `linear_algebra(operation, matrix, extra?)`  
  Operations like `det`, `inverse`, `lu`, `qr`, `svd`, `cond`.

- `interval_compute(name, args, dps?)`  
  Interval arithmetic via `iv` context (`mpi`, interval-safe transforms).

- `constants(name, dps?)`  
  Return constants (`pi`, `e`, etc.) at configured precision.

Notes:
- Prefer stateless endpoint design: precision passed per request when possible.
- Validate expression inputs carefully (avoid arbitrary code execution).

---

## 5) Common Issues and Notes

- Precision vs performance: higher `dps` increases CPU/memory cost.
- Convergence sensitivity: `findroot`, oscillatory integrals, and special functions may require better initial guesses or tuned precision.
- Numerical stability: consider interval arithmetic (`iv`) for rigorous bounds.
- Backend differences: availability of `gmpy2` can affect speed and behavior.
- Serialization: return numeric outputs as strings for very high precision to avoid float truncation.
- Security: never directly `eval` untrusted expressions without strict parsing/sandboxing.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/fredrik-johansson/mpmath
- Package docs/source tree (in repo): `docs/`, `mpmath/function_docs.py`
- CLI entry: `python -m mpmath`
- Core modules of interest:
  - `mpmath.ctx_mp` (arbitrary precision context)
  - `mpmath.calculus.quadrature` (integration)
  - `mpmath.calculus.optimization` (root finding)
  - `mpmath.calculus.differentiation` (derivatives/Taylor)
  - `mpmath.matrices.linalg` (linear algebra)
  - `mpmath.functions.*` (special functions)