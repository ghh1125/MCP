# ChemPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository can be wrapped as an MCP (Model Context Protocol) service to expose practical chemistry computation tools for LLM workflows.

Main capabilities:
- Parse and render chemical formulas
- Balance reaction stoichiometry
- Build reactions and reaction systems
- Solve equilibrium systems
- Generate kinetic ODE systems and evaluate rates
- Compute selected physical chemistry/electrochemistry properties (e.g., water density, Nernst potential)
- Optional unit-aware calculations

This service is best suited for scientific assistants, lab automation copilots, and educational chemistry workflows.

---

## 2) Installation Method

### Requirements
- Python 3.x
- Core libraries: `numpy`, `scipy`, `sympy`
- Optional (feature-dependent): `pyodesys`, `symengine`, `quantities`, `pint`, `matplotlib`, `ipywidgets`, `bokeh`

### Install ChemPy
- From PyPI:
  `pip install chempy`
- From source:
  1. Clone `https://github.com/bjodah/chempy`
  2. Run `pip install -e .`

### Verify install
- `python -c "import chempy; print(chempy.__version__)"`

---

## 3) Quick Start

Typical service-side calls you can expose through MCP (Model Context Protocol):

- Formula parsing/rendering  
  `chempy.util.parsing.formula_to_composition("H2SO4")`  
  `chempy.util.parsing.formula_to_latex("Fe2(SO4)3")`

- Stoichiometry balancing  
  `chempy.chemistry.balance_stoichiometry({"H2", "O2"}, {"H2O"})`

- Reaction object usage  
  Build `Reaction` / `Substance` objects from `chempy.chemistry` for validation and derived quantities.

- Equilibrium systems  
  Use `chempy.equilibria.EqSystem` (e.g., `EqSystem.from_string(...)`) for equilibrium setup/solve workflows.

- Kinetics ODE generation  
  `chempy.kinetics.ode.get_odesys(...)` for simulation-ready ODE systems.

- Electrochemistry  
  `chempy.electrochemistry.nernst.nernst_potential(...)`

- Units helpers  
  `chempy.units.to_unitless(...)`, `chempy.units.unit_of(...)`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `parse_formula`
  - Uses: `formula_to_composition`
  - Returns elemental composition mapping.

- `render_formula`
  - Uses: `formula_to_latex`, `formula_to_unicode`
  - Returns display-safe formula strings.

- `balance_stoichiometry`
  - Uses: `balance_stoichiometry`
  - Returns balanced reactant/product coefficients.

- `reaction_analyze`
  - Uses: `Reaction`, `Substance`, `equilibrium_quotient`, `mass_fractions`
  - Returns derived reaction properties and checks.

- `build_reaction_system`
  - Uses: `ReactionSystem`
  - Returns validated multi-reaction model metadata.

- `solve_equilibrium`
  - Uses: `EqSystem`
  - Returns equilibrium state/concentrations (given inputs).

- `build_kinetics_ode`
  - Uses: `get_odesys`, `dCdt_list`, rate classes (`MassAction`, `Arrhenius`, `Eyring`)
  - Returns ODE-ready model components.

- `nernst_potential`
  - Uses: `nernst_potential`
  - Returns electrochemical potential estimate.

- `water_density`
  - Uses: `chempy.properties.water_density_tanaka_2001.water_density`
  - Returns water density from correlation input.

- `unit_convert` (optional)
  - Uses: `to_unitless`, `unit_of`
  - Returns normalized/unit-aware values.

---

## 5) Common Issues and Notes

- No built-in CLI entry points are defined; MCP (Model Context Protocol) wrapping should call Python APIs directly.
- Optional dependencies should be installed only for endpoints that need them (especially kinetics/units/plotting).
- Some symbolic or ODE-heavy workflows can be slower; cache parsed formulas and prebuilt models where possible.
- Keep endpoint contracts strict (typed inputs, explicit units, deterministic outputs) to reduce ambiguity in LLM calls.
- Validate chemical formulas and reaction strings before solving to avoid cryptic downstream numerical errors.
- If unit-aware mode is enabled, enforce one unit backend (`pint` or `quantities`) consistently.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/bjodah/chempy
- Package structure highlights:
  - `chempy/chemistry.py`
  - `chempy/reactionsystem.py`
  - `chempy/equilibria.py`
  - `chempy/kinetics/ode.py`
  - `chempy/kinetics/rates.py`
  - `chempy/util/parsing.py`
  - `chempy/units.py`
  - `chempy/electrochemistry/nernst.py`
  - `chempy/properties/*`
- Tests for usage patterns:
  - `chempy/tests/`
  - `chempy/kinetics/tests/`
  - `chempy/util/tests/`

If you want, I can also generate a production-ready `service.py` skeleton mapping these endpoints to MCP (Model Context Protocol) handlers.