# molmass MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `molmass` library as an MCP (Model Context Protocol) service for molecular formula analysis.

Primary capabilities:
- Parse molecular formulas (including charge handling)
- Compute average/monoisotopic mass
- Generate elemental composition
- Estimate isotopic/spectrum-related outputs
- Support formula construction from strings, sequences, or fractions

Core engine module: `molmass.molmass`  
Data model module: `molmass.elements`  
Optional HTTP adapter: `molmass.web`

---

## 2) Installation Method

### Requirements
- Python 3.x
- Core runtime is pure Python (standard library based)
- Optional:
  - `tkinter` for GUI-related module usage (`elements_gui`)
  - Web runtime context only if exposing `molmass.web` as HTTP endpoint

### Install with pip
- From PyPI:
  pip install molmass

- From source repository:
  pip install git+https://github.com/cgohlke/molmass.git

---

## 3) Quick Start

### Basic import and analysis flow
Use the core API from `molmass.molmass`:
- `analyze(formula_str)` for one-shot analysis output
- `Formula(...)` for object-oriented operations
- `from_string`, `from_sequence`, `from_fractions` for structured construction

### Example workflow (conceptual)
1. Accept formula input (for example: `C8H10N4O2`)
2. Build formula object via `Formula` or `from_string`
3. Return:
   - molecular mass
   - composition breakdown
   - optional spectrum/isotope details

### CLI usage
- `python -m molmass`  
Useful fallback path when direct import integration is not desired.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service tools to expose:

- `analyze_formula`
  - Backed by: `molmass.molmass.analyze`
  - Input: formula string
  - Output: parsed formula analysis summary (mass/composition/spectrum-oriented info)

- `build_formula_from_string`
  - Backed by: `from_string`
  - Input: formula string
  - Output: normalized/internal formula representation

- `build_formula_from_sequence`
  - Backed by: `from_sequence`
  - Input: sequence-style composition
  - Output: formula object/result

- `build_formula_from_fractions`
  - Backed by: `from_fractions`
  - Input: fractional elemental data
  - Output: inferred/constructed formula result

- `format_or_parse_charge`
  - Backed by: `split_charge`, `join_charge`, `format_charge`
  - Input: charged formula or charge components
  - Output: normalized charge/formula formatting

- `periodic_element_lookup` (optional)
  - Backed by: `molmass.elements` data structures (`Element`, `Isotope`, `Elements`)
  - Input: atomic symbol/number
  - Output: periodic/isotope metadata

Optional web endpoint layer (if enabled through `molmass.web`):
- `main`, `response`, `analyze`, `favicon`

---

## 5) Common Issues and Notes

- Dependency detection in automated scans may appear incomplete; this project includes `setup.py`/`pyproject.toml` in repo snapshots.
- Prefer direct Python import integration for MCP (Model Context Protocol) services; it is low-risk and simple.
- Use CLI (`python -m molmass`) as fallback integration mode.
- GUI module (`elements_gui`) is optional and not required for server-side MCP (Model Context Protocol) service deployments.
- Validate user input and surface `FormulaError` cleanly in tool responses.
- For large batch analysis, cache parsed formula objects where practical.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/cgohlke/molmass
- Package entry module: `molmass.__main__`
- Core engine: `molmass.molmass`
- Periodic table/isotope data: `molmass.elements`
- Optional web adapter: `molmass.web`
- Tests/examples of behavior: `tests/test_molmass.py`