# UFL MCP (Model Context Protocol) Service README

## 1) Introduction

This service exposes the FEniCS UFL (Unified Form Language) symbolic API through MCP (Model Context Protocol) for form authoring, inspection, and transformation.

Main capabilities:
- Build variational forms (trial/test functions, coefficients, measures, operators).
- Analyze and normalize expression DAGs using `ufl.algorithms`.
- Compute signatures and metadata for forms.
- Render forms/expressions to readable Unicode for explanations.

Primary integration surface:
- `ufl` (top-level DSL, recommended)
- `ufl.algorithms` (analysis/transform pipeline)
- `ufl.form` (form container utilities)
- `ufl.formatting.ufl2unicode` (human-readable rendering)

---

## 2) Installation

Requirements:
- Python `>=3.9`
- `numpy`
- Optional: `pytest` (tests), `sphinx` (docs)

Install:
- `pip install ufl`
- or from source repository:
  - `pip install .`

If you are packaging this as an MCP (Model Context Protocol) service, add your MCP host/runtime dependencies separately (not part of core UFL).

---

## 3) Quick Start

Typical workflow in this service:
1. Construct symbolic objects using `ufl`:
   - `FiniteElement`, `FunctionSpace`, `TrialFunction`, `TestFunction`, `Coefficient`, `Constant`
   - operators like `grad`, `div`, `inner`, measures `dx`, `ds`, `dS`
2. Build a `Form` (e.g., bilinear/linear forms).
3. Run analysis/transforms:
   - `compute_form_data`
   - `apply_derivatives`
   - `apply_algebra_lowering`
   - `apply_geometry_lowering`
   - `apply_restrictions`
   - `expand_indices`
   - `signature`
4. Return rendered output via `ufl2unicode` for explainability responses.

---

## 4) Tools / Endpoints

Suggested MCP (Model Context Protocol) service endpoints:

- `ufl.build_form`
  - Create symbolic forms from provided definitions.
  - Output: serialized form/expression handle.

- `ufl.analyze_form`
  - Run `compute_form_data`, extract arguments/coefficients/domains/degree estimates.
  - Output: structured metadata.

- `ufl.transform_form`
  - Apply pipeline steps (`apply_derivatives`, lowering, restrictions, index expansion, replace).
  - Output: transformed form handle + transform log.

- `ufl.signature`
  - Compute canonical form signature for caching/comparison.
  - Output: deterministic signature string.

- `ufl.render_unicode`
  - Render expression/form via `ufl2unicode`.
  - Output: readable mathematical text.

- `ufl.inspect_expr`
  - Low-level DAG/node inspection using `ufl.core` (`Expr`, `Operator`, `Terminal`).
  - Output: node types, shape, free indices, dependencies.

- `ufl.validate`
  - Basic consistency checks (arity/restrictions/domain sanity).
  - Output: warnings/errors list.

No native CLI entry points were detected in the scanned repository; MCP (Model Context Protocol) access should be provided by your service host.

---

## 5) Common Issues and Notes

- Version compatibility:
  - Ensure Python and UFL versions are aligned (`python>=3.9`).
- Environment confusion:
  - UFL is symbolic; full PDE solving requires external FEniCSx components (e.g., DOLFINx), which are not hard runtime dependencies for basic UFL import.
- Performance:
  - Large expression DAG transforms can be expensive; cache signatures and intermediate normalized forms.
- API stability:
  - Prefer top-level `ufl` and `ufl.algorithms` for service interfaces.
  - `ufl.core` is useful for deep inspection but lower-level and more change-prone.
- Serialization:
  - For MCP (Model Context Protocol), pass stable identifiers/serialized structures rather than raw Python object references across process boundaries.

---

## 6) References

- Repository: https://github.com/FEniCS/ufl
- UFL package docs (in repo): `README.md`, `doc/source/`
- Change history: `ChangeLog.md`
- Demos: `demo/`
- Tests/examples of behavior: `test/`