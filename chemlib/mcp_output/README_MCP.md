# chemlib MCP (Model Context Protocol) Service README

## 1) Project Introduction

`chemlib` is a Python chemistry toolkit that can be exposed as an MCP (Model Context Protocol) service for LLM-driven scientific workflows.  
It provides practical chemistry calculations including:

- Core chemistry objects: `Element`, `Compound`, `Reaction`, `Solution`, `PeriodicTable`
- Stoichiometry and reaction balancing workflows
- Formula parsing and empirical formula estimation
- pH calculations
- Electrochemistry helpers (electrolysis, galvanic cell modeling)
- Thermochemistry and combustion analysis
- Basic quantum mechanics utilities (Rydberg and hydrogen orbital energy)

This service is best for tool-enabled assistants that need reliable, programmatic chemistry computations.

---

## 2) Installation Method

### Requirements

- Python 3.x
- Required libraries:
  - `numpy`
  - `sympy`

### Install from PyPI

pip install chemlib

### Install from source

git clone https://github.com/harirakul/chemlib.git  
cd chemlib  
pip install -r requirements.txt  
pip install .

---

## 3) Quick Start

### Basic import and chemistry usage

from chemlib.chemistry import Compound, Reaction, pH

water = Compound("H2O")
acidic = pH(H=1e-3)   # example usage if pH helper is exposed this way
rxn = Reaction.by_formula("H2 + O2 --> H2O")
rxn.balance()

### Parse a formula

from chemlib.parse import parse_formula

atoms = parse_formula("C6H12O6")

### Electrochemistry

from chemlib.electrochemistry import electrolysis

result = electrolysis("Cu", n=2)

### Thermochemistry

from chemlib.thermochemistry import combustion_analysis

analysis = combustion_analysis(CO2=44, H2O=18)

### Quantum mechanics

from chemlib.quantum_mechanics import rydberg, energy_of_hydrogen_orbital

line = rydberg("H", n1=1, n2=2)
energy = energy_of_hydrogen_orbital(1)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints (map 1:1 to library APIs):

- `chemistry.compound`
  - Build and inspect a chemical compound (`Compound`).
- `chemistry.reaction`
  - Create, parse, and balance reactions (`Reaction`).
- `chemistry.ph`
  - Compute pH-related values (`pH`).
- `chemistry.empirical_formula`
  - Estimate empirical formula from percent composition (`empirical_formula_by_percent_comp`).
- `chemistry.parse_formula`
  - Parse molecular formula into element/count mapping (`parse_formula`).
- `electrochemistry.electrolysis`
  - Electrolysis calculations (`electrolysis`).
- `electrochemistry.galvanic_cell`
  - Galvanic cell modeling (`Galvanic_Cell`).
- `thermochemistry.combustion_analysis`
  - Derive composition from combustion products (`combustion_analysis`).
- `thermochemistry.calorimetry`
  - Calorimetry models (`Bomb`, `CoffeeCup`, `Calorimeter`, `Combustion`).
- `quantum.rydberg`
  - Spectral transition calculations (`rydberg`).
- `quantum.hydrogen_orbital_energy`
  - Hydrogen orbital energy levels (`energy_of_hydrogen_orbital`).

---

## 5) Common Issues and Notes

- Dependency errors (`numpy`, `sympy`)  
  Ensure both are installed in the same Python environment used by your MCP (Model Context Protocol) service runtime.

- Formula/reaction input formatting  
  Use valid chemical notation (for example: `H2SO4`, `C6H12O6`, `H2 + O2 --> H2O`).

- API shape differences across versions  
  If function signatures differ, pin a specific version and test with your service wrappers.

- Numerical precision  
  Some chemistry calculations may involve floating-point rounding; apply output normalization in service responses when needed.

- Runtime complexity  
  Repository analysis indicates low complexity and low intrusiveness risk, so it is suitable for straightforward service exposure.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/harirakul/chemlib
- Package README: https://github.com/harirakul/chemlib/blob/master/README.md
- Changelog: https://github.com/harirakul/chemlib/blob/master/CHANGELOG.md
- License: https://github.com/harirakul/chemlib/blob/master/LICENSE.txt