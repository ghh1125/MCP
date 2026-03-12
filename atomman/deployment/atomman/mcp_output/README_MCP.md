# atomman MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository provides an MCP (Model Context Protocol) service wrapper around the `atomman` Python library for atomistic/materials modeling workflows.

It is designed to let MCP clients load, inspect, transform, analyze, and export atomic systems through a small set of practical services, including:

- Core structure handling (`Atoms`, `Box`, `System`)
- Structure I/O (`load`, `dump`) across multiple formats
- Defect utilities (free surfaces, stacking faults, gamma surfaces)
- LAMMPS integration (`run`, log parsing)
- Crystallographic helpers (Miller index conversion)
- Unit conversion helpers

## 2) Installation Method

### Requirements

Required Python packages (from repository analysis):

- numpy
- scipy
- DataModelDict
- numericalunits

Optional packages (feature-dependent):

- matplotlib, pandas, plotly
- nglview, py3Dmol
- ase, pymatgen, spglib, phonopy, freud
- External LAMMPS executable (for `atomman.lammps.run`)

### Install

pip install atomman

For development setup from source repository:

pip install -e .

If you need optional format/visualization support, install relevant extras manually (for example: `ase`, `pymatgen`, `spglib`, `plotly`, etc.).

## 3) Quick Start

### Basic structure workflow

import atomman as am

# Create or load a system
system = am.load('atom_data', 'data.file')   # format key + source

# Access core components
atoms = system.atoms
box = system.box

# Compute displacement with periodic boundaries
dv = am.displacement(system0=system, system1=system)

# Export
text = am.dump('atom_data', system)

### LAMMPS workflow

from atomman.lammps import run, Log

# Run LAMMPS (requires external executable available in PATH)
results = run(lammps_command='lmp', script='in.sim')

# Parse log
log = Log('log.lammps')

### Crystallography/unit helpers

from atomman.tools import miller
from atomman import unitconvert as uc

hkil = miller.plane3to4([1, 0, 0])
value = uc.get_in_units(1.0, 'eV')

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints for this project:

- `system.load`
  - Wrapper over `atomman.load.load`
  - Load structures/data from supported formats (`atom_data`, `atom_dump`, `poscar`, `cif`, `system_model`, etc.)

- `system.dump`
  - Wrapper over `atomman.dump.dump`
  - Export systems to target formats (`atom_data`, `atom_dump`, `poscar`, `pdb`, `table`, etc.)

- `core.create_system` / `core.inspect_system`
  - Construct and inspect `System`, `Atoms`, `Box`
  - Return atom counts, box vectors, symbols, and properties

- `analysis.displacement`
  - Wrapper over `displacement`, `dvect`, `dmag`
  - Compute displacement vectors/magnitudes with periodic boundary handling

- `analysis.neighbor_list`
  - Wrapper over `NeighborList`
  - Build/query local atomic neighbors for structure analysis

- `defect.free_surface`
  - Wrapper over `FreeSurface`
  - Build free-surface models from crystal orientation settings

- `defect.stacking_fault`
  - Wrapper over `StackingFault`
  - Generate and evaluate stacking-fault configurations

- `defect.gamma_surface`
  - Wrapper over `GammaSurface`
  - Support gamma-surface style defect energetics workflows

- `lammps.run`
  - Wrapper over `atomman.lammps.run`
  - Execute LAMMPS scripts and collect outputs

- `lammps.parse_log`
  - Wrapper over `atomman.lammps.Log` / `NEBLog`
  - Parse thermo and NEB information from LAMMPS logs

- `tools.miller_convert`
  - Wrapper over `plane3to4`, `plane4to3`, `vector3to4`, `vector4to3`
  - Convert crystallographic indices

- `units.convert`
  - Wrapper over `unitconvert` (`set_in_units`, `get_in_units`, `parse`, `value_unit`)
  - Standardize unit-aware numeric values

## 5) Common Issues and Notes

- LAMMPS execution errors:
  - Ensure LAMMPS is installed and executable (e.g., `lmp`) is in `PATH`.
- Format support differences:
  - Some loaders/dumpers require optional packages (`ase`, `pymatgen`, `spglib`, `phonopy`).
- Visualization imports failing:
  - Install optional visualization dependencies (`plotly`, `nglview`, `py3Dmol`, `matplotlib`).
- Performance:
  - Large systems can make neighbor/defect analysis memory-heavy; prefer batched workflows and avoid unnecessary copies.
- Reproducibility:
  - Pin versions of scientific dependencies and external tools in CI or environment files.

## 6) Reference Links or Documentation

- Repository: https://github.com/usnistgov/atomman
- Package/module root: `atomman/`
- Tests/examples: `tests/` and `doc/`
- Key modules:
  - `atomman.core`
  - `atomman.load`
  - `atomman.dump`
  - `atomman.defect`
  - `atomman.lammps`
  - `atomman.tools`
  - `atomman.unitconvert`