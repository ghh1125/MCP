# UFL MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes the core capabilities of [FEniCS UFL](https://github.com/FEniCS/ufl) through MCP (Model Context Protocol): symbolic construction, analysis, and transformation of variational forms and tensor expressions.

Primary use cases:
- Build symbolic PDE forms (test/trial functions, coefficients, measures, operators).
- Inspect forms/expressions (arguments, coefficients, constants, elements).
- Compute deterministic signatures for caching/idempotence.
- Apply controlled symbolic rewrites and form-data preparation.

## 2) Installation Method

Requirements:
- Python >= 3.9
- numpy

Install:
- `pip install ufl numpy`

For development/testing/docs:
- `pip install pytest sphinx`

If integrating into your MCP (Model Context Protocol) host, add this service as a Python-imported backend module (no native CLI entry points are defined in this repository).

## 3) Quick Start

Minimal workflow:
1. Import UFL public API from `ufl`.
2. Define element/function space/domain symbols.
3. Build expressions with operators (`grad`, `div`, `inner`, etc.).
4. Analyze/transform with `ufl.algorithms.*`.

Example actions your MCP (Model Context Protocol) service should support:
- Create a form expression (e.g., bilinear/linear forms).
- Extract metadata (`extract_arguments`, `extract_coefficients`, `extract_constants`).
- Compute stable signatures (`compute_form_signature`).
- Substitute symbols (`replace`).
- Prepare compiler-facing metadata (`compute_form_data`).

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `ufl.build_expression`  
  Build symbolic expressions/forms using UFL operators and terminals.

- `ufl.analyze.form_entities`  
  Wrapper around:
  - `extract_arguments`
  - `extract_coefficients`
  - `extract_constants`
  - `extract_elements`
  - `extract_sub_elements`

- `ufl.analyze.signature`  
  Wrapper around:
  - `compute_expression_signature`
  - `compute_form_signature`  
  Useful for caching and reproducible identity.

- `ufl.transform.replace`  
  Symbolic substitution via `ufl.algorithms.replace.replace`.

- `ufl.transform.compute_form_data`  
  Run `compute_form_data` for downstream compilation/processing metadata.

- `ufl.info.capabilities`  
  Return service version, supported operators/measures, and environment diagnostics.

## 5) Common Issues and Notes

- Version compatibility:
  - Ensure Python >= 3.9.
  - Keep `ufl` and downstream FEniCS components aligned by release series.

- No built-in CLI:
  - This repository is library-first; expose functionality through your MCP (Model Context Protocol) service layer.

- Performance:
  - Large symbolic DAGs can be expensive to transform repeatedly.
  - Use signatures to cache results of analysis/transformation endpoints.

- Safety/robustness:
  - Validate user-provided symbolic rewrite maps before `replace`.
  - Add request size/depth limits for very large expressions.

- Docs/tests dependencies:
  - `pytest` and `sphinx` are optional and intended for development workflows.

## 6) Reference Links and Documentation

- Repository: https://github.com/FEniCS/ufl  
- Upstream README: https://github.com/FEniCS/ufl/blob/main/README.md  
- Changelog: https://github.com/FEniCS/ufl/blob/main/ChangeLog.md  
- Package metadata (`pyproject.toml`): https://github.com/FEniCS/ufl/blob/main/pyproject.toml  
- FEniCS ecosystem: https://fenicsproject.org/