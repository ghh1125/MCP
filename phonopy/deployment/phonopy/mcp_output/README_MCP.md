# Phonopy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `phonopy` Python library as an MCP (Model Context Protocol) service for phonon workflows.  
It is designed for developers who want programmatic access to:

- phonon model loading and initialization
- displacement / force-constant file handling
- band structure, mesh, DOS, and thermal property calculations
- QHA and Grüneisen post-processing
- calculator format conversion helpers (VASP, QE, CP2K, ABINIT, LAMMPS, etc.)

Core integration targets in this repository are:

- `phonopy.api_phonopy.Phonopy`
- `phonopy.api_qha.PhonopyQHA`
- `phonopy.api_gruneisen.PhonopyGruneisen`
- `phonopy.cui.load.load`
- `phonopy.file_IO` parsing/writing utilities

---

## 2) Installation Method

### Prerequisites

- Python 3.x
- `numpy`
- `PyYAML`
- `matplotlib`

Optional but commonly needed:

- `h5py`
- `spglib`
- `symfc`
- `pypolymlp`
- external calculator tools/data (VASP, QE, CP2K, ABINIT, LAMMPS, etc.)

### Install commands

- Install phonopy:
  - `pip install phonopy`
- Recommended extras for broader workflows:
  - `pip install spglib h5py symfc pypolymlp`

If your MCP (Model Context Protocol) service has its own package, add `phonopy` and the above runtime dependencies to your service dependency list.

---

## 3) Quick Start

### Typical service flow

1. Load a phonopy YAML/params input via `phonopy.cui.load.load`.
2. Build/use a `Phonopy` object.
3. Run requested computation (band, mesh, DOS, thermal).
4. Return parsed structured output (JSON-friendly), and optionally write standard files.

### Minimal Python usage pattern (inside service handlers)

- Import and load:
  - `from phonopy.cui.load import load`
  - `phonon = load("phonopy.yaml")`
- Example operations:
  - run mesh / DOS / thermal calculations through `phonon` methods
  - parse/write files using:
    - `parse_FORCE_SETS`, `parse_FORCE_CONSTANTS`, `parse_BORN`
    - `write_FORCE_SETS`, `write_FORCE_CONSTANTS`

For QHA/Grüneisen endpoints, use `PhonopyQHA` / `PhonopyGruneisen` APIs with precomputed harmonic inputs.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `phonopy.load`
  - Load `phonopy.yaml` or related params into a working model context.

- `phonopy.structure.read`
  - Read crystal structure via calculator interface abstraction.

- `phonopy.structure.write`
  - Write crystal structure in calculator-specific format.

- `phonopy.forcesets.parse`
  - Parse `FORCE_SETS` into structured data.

- `phonopy.forceconstants.parse`
  - Parse `FORCE_CONSTANTS` into structured data.

- `phonopy.forcesets.write`
  - Write `FORCE_SETS` from structured input.

- `phonopy.forceconstants.write`
  - Write `FORCE_CONSTANTS` from structured input.

- `phonopy.band.compute`
  - Compute phonon band structure from loaded model.

- `phonopy.mesh.compute`
  - Compute mesh phonons / derived quantities.

- `phonopy.dos.compute`
  - Compute total/projected DOS.

- `phonopy.thermal.compute`
  - Compute thermal properties.

- `phonopy.qha.compute`
  - QHA workflow endpoint (volume-temperature thermodynamics).

- `phonopy.gruneisen.compute`
  - Grüneisen parameter workflow endpoint.

- `phonopy.convert.calculator_format`
  - Convert between supported calculator formats.

---

## 5) Common Issues and Notes

- **spglib missing**: symmetry-dependent features may fail or degrade.
- **Large supercells**: memory and runtime grow quickly for FC and mesh operations.
- **Input consistency**: force files, structure files, and units must match calculator conventions.
- **NAC/BORN data**: ensure correct dielectric/Born effective charge inputs for non-analytical corrections.
- **Plot dependencies**: plotting-related tasks require `matplotlib` and suitable backend in headless environments.
- **External calculators**: this service does not run DFT itself; it orchestrates phonopy-side processing.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/phonopy/phonopy
- Main docs index: `doc/index.md`
- Installation docs: `doc/install.md`
- API/module usage: `doc/phonopy-module.md`
- CLI/options: `doc/command-options.md`
- Input format: `doc/input-files.md`
- Output format: `doc/output-files.md`
- Interfaces: `doc/interfaces.md`
- QHA: `doc/qha.md`
- Grüneisen: `doc/gruneisen.md`