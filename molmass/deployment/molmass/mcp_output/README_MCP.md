# molmass MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `molmass` chemistry engine to provide mass/formula analysis through MCP (Model Context Protocol).  
It is designed for developer use cases such as:

- Molecular formula parsing and validation
- Monoisotopic, average, and nominal mass calculation
- Elemental composition reporting
- Isotopic spectrum generation
- Sequence/oligo/peptide-derived formula conversion

Primary integration target: `source.molmass.molmass` (or `deployment.molmass.source.molmass` in alternate runtime layouts).

---

## 2) Installation

### Requirements
- Python 3.x
- Standard library only for core functionality
- Optional:
  - `tkinter` for GUI module (`elements_gui.py`)
  - CGI/web runtime for `web.py`

### Install from PyPI
pip install molmass

### Install from source
git clone https://github.com/cgohlke/molmass.git  
cd molmass  
pip install .

---

## 3) Quick Start

### Recommended imports
from source.molmass.molmass import analyze, Formula, from_string, from_sequence, from_peptide, from_oligo

### Typical usage patterns
- Parse and analyze a formula string:
  - `analyze("C8H10N4O2")`
- Create a formula object and compute masses/composition:
  - `Formula("H2O")`
- Build formulas from biological sequences:
  - `from_sequence(...)`, `from_peptide(...)`, `from_oligo(...)`
- Build from generic text input:
  - `from_string(...)`

### CLI execution
python -m source.molmass

(Depending on packaging/runtime, module path may be `molmass` or `deployment.molmass.source.molmass`.)

---

## 4) Available Tools and Endpoints

For MCP (Model Context Protocol) service design, expose these practical endpoints:

- `analyze_formula`
  - Backed by: `analyze`, `Formula`
  - Input: formula string
  - Output: parsed formula details, masses, composition, optional spectrum summary

- `parse_formula`
  - Backed by: `read_formula`, `split_formula`, `split_parts`, `split_charge`
  - Input: formula string
  - Output: normalized/parsed structure, charge handling, validation errors

- `calculate_mass`
  - Backed by: `Formula` properties/methods
  - Input: formula string
  - Output: monoisotopic/average/nominal masses

- `composition_from_formula`
  - Backed by: `Formula`, `Composition`
  - Input: formula string
  - Output: element counts and relative contributions

- `spectrum_from_formula`
  - Backed by: `Spectrum`, `SpectrumEntry`
  - Input: formula string, optional limits/precision
  - Output: isotope peaks and intensities

- `formula_from_sequence`
  - Backed by: `from_sequence`, `from_peptide`, `from_oligo`
  - Input: sequence + mode/options
  - Output: derived molecular formula and optional mass results

- `formula_from_elements_or_fractions`
  - Backed by: `from_elements`, `from_fractions`
  - Input: element map or mass fractions
  - Output: reconstructed/estimated formula

---

## 5) Common Issues and Notes

- Import path differences:
  - Prefer `source.molmass.*`
  - Fallback to `deployment.molmass.source.*` if required by environment

- Error handling:
  - Catch `FormulaError` for invalid syntax or unsupported input

- Precision/output formatting:
  - Use helper behavior such as `precision_digits`, `join_charge`, `hill_sorted` where needed for consistent output

- Optional modules:
  - `elements_gui.py` requires GUI support (`tkinter`)
  - `web.py` is useful as interface reference but not the preferred core MCP (Model Context Protocol) hook

- Performance:
  - Core operations are lightweight for typical formula queries
  - Isotopic spectrum generation can be heavier for large molecules

---

## 6) Reference Links

- Repository: https://github.com/cgohlke/molmass
- Core engine module: `molmass/molmass.py`
- Element data: `molmass/elements.py`
- Web adapter reference: `molmass/web.py`
- Tests/examples: `tests/test_molmass.py`