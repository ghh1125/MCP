# CVXOPT MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes CVXOPT optimization capabilities through MCP (Model Context Protocol) tools with a thin, import-based adapter.

Primary goals:
- Solve optimization problems via CVXOPT `solvers` APIs
- Accept JSON-friendly inputs and convert them to CVXOPT matrices
- Return normalized JSON outputs for reliable downstream use
- Keep integration low-risk (no patching CVXOPT internals)

Main solver coverage:
- LP, QP, SOCP, SDP
- Cone LP/QP (`conelp`, `coneqp`)
- Optional GP/CP-style workflows when enabled

---

## 2) Installation Method

### Requirements
- Python >= 3.8
- `numpy`
- `cvxopt` (with compiled extensions)
- Optional native backends depending on your target usage:
  - GLPK, GSL, DSDP, MOSEK
  - SuiteSparse (CHOLMOD/UMFPACK), FFTW

### Recommended install
1. Create and activate a virtual environment.
2. Install CVXOPT and NumPy:
   - `pip install numpy cvxopt`
3. Install your MCP (Model Context Protocol) service package (your adapter layer).
4. Verify import:
   - `import cvxopt`
   - `from cvxopt import solvers`

If CVXOPT wheel/build is unavailable for your platform, use a container/prebuilt runtime and run this service in blackbox mode.

---

## 3) Quick Start

Typical flow:
1. Send JSON problem data (vectors/matrices as lists or sparse triplets).
2. Service converts input to `cvxopt.matrix` / `cvxopt.spmatrix`.
3. Service calls selected solver (`lp`, `qp`, `socp`, etc.).
4. Service returns normalized JSON:
   - `status`
   - `objective`
   - `x` (primal)
   - `y/z/s` (dual/slack when available)
   - `iterations`
   - backend/capability metadata

Minimal example request pattern:
- Tool: `solve_qp`
- Inputs: `P, q, G, h, A, b` (JSON arrays; optional constraints omitted as null)
- Output: standardized solve result with status/objective/solution vectors

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service tool set:

- `capabilities`
  - Returns detected solver/backends and feature flags (e.g., `mosek`, `glpk` availability).

- `solve_lp`
  - Linear programming via `solvers.lp`.

- `solve_qp`
  - Quadratic programming via `solvers.qp`.

- `solve_socp`
  - Second-order cone programming via `solvers.socp`.

- `solve_sdp`
  - Semidefinite programming via `solvers.sdp`.

- `solve_conelp`
  - General cone LP via `solvers.conelp`.

- `solve_coneqp`
  - General cone QP via `solvers.coneqp`.

- `solve_gp` (optional)
  - Geometric programming via `solvers.gp` where configured.

- `validate_problem` (recommended)
  - Shape/type checks before solve; returns actionable validation errors.

- `set_solver_options` (recommended)
  - Controlled update of CVXOPT solver options (tolerances, max iterations, verbosity).

---

## 5) Common Issues and Notes

- Build complexity:
  - CVXOPT may require compiled native dependencies; installation can fail on minimal systems.
- Backend variability:
  - Optional solvers (MOSEK/GLPK/DSDP) differ by environment; always query `capabilities`.
- Input shape mismatches:
  - Most failures are dimension/type errors in matrix inputs; validate before solving.
- Sparse vs dense:
  - Prefer sparse representation for large structured problems to reduce memory/time.
- Numerical stability:
  - Poorly scaled problems may converge slowly or fail; apply scaling/regularization when needed.
- Service safety:
  - Keep adapter read-only and thin; do not modify CVXOPT internals.
- Fallback mode:
  - If import/build fails, run a prebuilt CVXOPT container and expose a reduced stable subset (commonly LP/QP).

---

## 6) Reference Links / Documentation

- CVXOPT repository: https://github.com/cvxopt/cvxopt
- CVXOPT package docs (in repo): `doc/` and generated `doc/html/`
- Key API modules:
  - `src/python/solvers.py`
  - `src/python/modeling.py`
  - `src/python/coneprog.py`
  - `src/python/cvxprog.py`
- Tests/examples for expected behavior:
  - `tests/`
  - `examples/`

---

For production MCP (Model Context Protocol) service usage, prioritize:
- strict JSON schema validation,
- deterministic output formatting,
- runtime capability detection,
- and minimal-intrusion integration over `cvxopt.solvers`.