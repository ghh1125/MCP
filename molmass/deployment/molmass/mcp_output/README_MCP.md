# molmass MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `molmass` library as an MCP (Model Context Protocol) service for molecular formula and mass analysis.

It is designed for developer workflows that need to:
- Parse chemical formulas
- Compute average/monoisotopic mass
- Inspect elemental composition
- Generate isotope spectrum data
- Build formulas from peptide/oligo/sequence helpers

Primary integration target: `molmass/molmass.py` (`Formula`, `analyze`, `from_*` helpers).

---

## 2) Installation

### Requirements
- Python 3.x
- `molmass` package
- Optional:
  - `tkinter` (GUI only, not required for MCP (Model Context Protocol) service use)
  - CGI/web runtime (only if using `molmass.web`)

### Install with pip
pip install molmass

For local development (from repository):
pip install -e .

---

## 3) Quick Start

### Python usage
from molmass import Formula, analyze, from_peptide, from_oligo

f = Formula("C8H10N4O2")   # caffeine
mass = f.mass
composition = f.composition()
spectrum = f.spectrum()

result_text = analyze("C8H10N4O2")
peptide_formula = from_peptide("MDRGEQGLLK")
oligo_formula = from_oligo("ATCG")

### CLI usage
python -m molmass "C8H10N4O2"

If console scripts are available in your install:
- molmass "C8H10N4O2"
- molmass-web
- elements-gui

---

## 4) Available Tools and Endpoints

Suggested MCP (Model Context Protocol) service endpoints (developer-oriented mapping):

- `analyze_formula`
  - Backed by: `molmass.analyze`
  - Input: formula string
  - Output: parsed analysis text/structured fields (mass, composition, spectrum summary)

- `parse_formula`
  - Backed by: `molmass.Formula`
  - Input: formula string
  - Output: canonical formula, charge, atom counts, validation errors

- `get_composition`
  - Backed by: `Formula.composition()`
  - Input: formula string
  - Output: per-element counts/fractions/mass contributions

- `get_spectrum`
  - Backed by: `Formula.spectrum()`
  - Input: formula string, optional options (peak limits)
  - Output: isotope peak list (m/z, abundance)

- `from_peptide`
  - Backed by: `molmass.from_peptide`
  - Input: peptide sequence
  - Output: molecular formula string

- `from_oligo`
  - Backed by: `molmass.from_oligo`
  - Input: oligo sequence (DNA/RNA-style)
  - Output: molecular formula string

- `from_elements` / `from_fractions`
  - Backed by: corresponding helpers
  - Input: element-count map or mass fractions
  - Output: inferred molecular formula

---

## 5) Common Issues and Notes

- Formula parsing errors:
  - Catch `FormulaError` and return clear validation messages.
- Performance:
  - Typical formulas are fast; very large formulas or deep isotope calculations may cost more CPU.
- Dependency notes:
  - No heavy required runtime dependencies beyond Python.
  - GUI/web modules are optional and not needed for core MCP (Model Context Protocol) service features.
- Integration approach:
  - Prefer direct Python import over shelling out to CLI (higher reliability and lower overhead).
- Environment:
  - Use a virtual environment to avoid package conflicts.

---

## 6) Reference Links

- Repository: https://github.com/cgohlke/molmass
- Package module entry: `molmass/molmass.py`
- Module CLI: `python -m molmass`
- Optional interfaces:
  - `molmass/web.py`
  - `molmass/elements_gui.py`