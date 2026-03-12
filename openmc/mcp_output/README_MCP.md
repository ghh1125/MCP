# OpenMC MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository can be exposed as an MCP (Model Context Protocol) service to help LLM agents and developer tools create, run, and analyze OpenMC Monte Carlo simulations programmatically.

Main capabilities:
- Build and manage OpenMC models (`Model`, `Geometry`, `Materials`, `Settings`, `Tallies`)
- Execute transport workflows (`run`, `plot_geometry`, `calculate_volumes`)
- Read simulation outputs (`StatePoint`, `Summary`)
- Advanced workflows:
  - In-memory engine control via `openmc.lib` (`init`, `run`, `reset`, `finalize`)
  - Depletion coupling via `openmc.deplete.CoupledOperator`

---

## 2) Installation Method

### Requirements
- Python `>=3.10`
- Core Python deps: `numpy`, `h5py`, `lxml`, `scipy`, `uncertainties`
- Optional deps: `matplotlib`, `pandas`, `networkx`, `vtk`, `mpi4py`
- OpenMC executable/build available in environment (for full run/plot/volume workflows)

### Install (typical)
- `pip install openmc`
- or from source repository root: `pip install -e .`

### Notes for optional features
- DAGMC workflows require a DAGMC/MOAB-enabled OpenMC build
- NCrystal workflows require an NCrystal-enabled OpenMC build
- MPI/distributed runs require MPI runtime + `mpi4py` (if using Python-side MPI integrations)

---

## 3) Quick Start

### Basic model execution flow
1. Create model objects (`Materials`, `Geometry`, `Settings`, optional `Tallies`)
2. Build `openmc.model.Model(...)`
3. Export XML or run directly
4. Read `statepoint.*.h5` with `openmc.StatePoint` for results

### Minimal Python usage pattern
import openmc

# Build or load model
model = openmc.model.Model(...)
model.export_to_xml()

# Run transport
openmc.run()

# Post-process
sp = openmc.StatePoint("statepoint.###.h5")
print(sp.keff)

### In-memory engine control (advanced)
Use `openmc.lib` for tighter integration:
- `openmc.lib.init()`
- `openmc.lib.run()`
- `openmc.lib.reset()`
- `openmc.lib.finalize()`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints for this project:

- `model.create`
  - Create/update an OpenMC model structure (materials, geometry, settings, tallies).
- `model.export_xml`
  - Export XML input files from a model.
- `simulation.run`
  - Execute OpenMC transport (`openmc.run`).
- `simulation.plot_geometry`
  - Generate geometry plots (`openmc.plot_geometry` / model plot APIs).
- `simulation.calculate_volumes`
  - Run stochastic volume calculations (`openmc.calculate_volumes`).
- `results.load_statepoint`
  - Load statepoint HDF5 output and return key metadata.
- `results.get_keff`
  - Return eigenvalue estimate and uncertainty from a statepoint.
- `results.get_tally`
  - Query tally results by id/name/filter/score.
- `engine.lib.init_run_finalize`
  - Lifecycle wrapper for `openmc.lib` in-memory execution.
- `depletion.run_coupled`
  - Run depletion-coupled workflows using `openmc.deplete`.

---

## 5) Common Issues and Notes

- Binary/runtime dependency mismatch:
  - Python package installed but OpenMC executable/library unavailable in PATH/LD paths.
- HDF5 and cross-section data configuration:
  - Ensure nuclear data libraries and relevant environment variables are set correctly.
- Optional feature confusion:
  - DAGMC/NCrystal tests or workflows fail unless OpenMC is compiled with those features.
- Performance:
  - Large models and depletion workflows are compute-heavy; use MPI and tune particles/batches.
- API/engine coupling risk:
  - `openmc.lib` is powerful but more sensitive to runtime/library compatibility than CLI-driven runs.
- Testing scope:
  - Repository includes extensive unit/regression tests; use them to validate service wrappers.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/openmc-dev/openmc
- Project docs: https://docs.openmc.org
- Python API root: `openmc` package (notably `openmc.model`, `openmc.executor`, `openmc.statepoint`, `openmc.lib`, `openmc.deplete`)
- Examples directory: `examples/` in repository
- Test references for expected behavior: `tests/unit_tests/`, `tests/regression_tests/`