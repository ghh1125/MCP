# Phonopy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `phonopy` Python library as an MCP (Model Context Protocol) service for phonon workflows in materials science.

Main goals:
- Load and validate crystal/phonopy YAML inputs
- Generate and parse core phonopy artifacts (`FORCE_SETS`, `FORCE_CONSTANTS`, `BORN`)
- Run core phonon workflows (band structure, mesh, thermal properties)
- Support calculator I/O interoperability (VASP, QE, ABINIT, CP2K, etc.)
- Expose optional Grüneisen and QHA analysis paths

Core integration targets:
- `phonopy.Phonopy`
- `phonopy.load`
- `phonopy.api_gruneisen.PhonopyGruneisen`
- `phonopy.api_qha.PhonopyQHA`
- `phonopy.interface.calculator.*`
- `phonopy.interface.phonopy_yaml.*`
- `phonopy.file_IO.*`

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Required Python deps: `numpy`, `PyYAML`, `h5py`, `spglib`, `matplotlib`
- Optional: `scipy`, `symfc`, `ALM`, `pypolymlp`, `seekpath`
- External DFT calculators are optional and only needed for calculator-specific workflows

### Install
- pip install phonopy
- or from source repo:
  - pip install -r requirements.txt
  - pip install .

If you are building this MCP (Model Context Protocol) service layer, add your MCP runtime dependency (SDK/server framework) separately.

---

## 3) Quick Start

### Minimal workflow idea
1. Load existing phonopy data (`phonopy.load` or YAML loader).
2. Build/inspect force constants (`parse_FORCE_CONSTANTS`, `write_FORCE_CONSTANTS`).
3. Run phonon properties through `Phonopy` API methods.
4. Return structured MCP (Model Context Protocol) responses (JSON-serializable summaries + file paths).

### Typical service call patterns
- Load structure/YAML:
  - `phonopy.load(...)`
  - `phonopy.interface.phonopy_yaml.load_yaml(...)`
- Read/write core files:
  - `phonopy.file_IO.parse_FORCE_SETS(...)`
  - `phonopy.file_IO.write_FORCE_SETS(...)`
  - `phonopy.file_IO.parse_FORCE_CONSTANTS(...)`
  - `phonopy.file_IO.write_FORCE_CONSTANTS(...)`
  - `phonopy.file_IO.parse_BORN(...)`
- Calculator conversion:
  - `phonopy.interface.calculator.read_crystal_structure(...)`
  - `phonopy.interface.calculator.write_crystal_structure(...)`

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints:

- `phonopy.load_project`
  - Load phonopy YAML/params and return normalized metadata.

- `phonopy.read_structure`
  - Read structure from calculator-specific format via calculator interface.

- `phonopy.write_structure`
  - Export structure to target calculator format.

- `phonopy.parse_force_sets`
  - Parse `FORCE_SETS` and return displacement/force dataset summary.

- `phonopy.parse_force_constants`
  - Parse `FORCE_CONSTANTS` and return shape/consistency checks.

- `phonopy.write_force_sets`
  - Write validated `FORCE_SETS`.

- `phonopy.write_force_constants`
  - Write validated `FORCE_CONSTANTS`.

- `phonopy.parse_born`
  - Parse NAC-related `BORN` data.

- `phonopy.run_band_structure`
  - Compute band structure from loaded phonopy object and return output artifact paths.

- `phonopy.run_mesh`
  - Compute q-point mesh properties (DOS-ready outputs).

- `phonopy.run_thermal_properties`
  - Compute temperature-dependent thermodynamic properties.

- `phonopy.run_gruneisen` (optional)
  - Execute Grüneisen workflow via `PhonopyGruneisen`.

- `phonopy.run_qha` (optional)
  - Execute QHA workflow via `PhonopyQHA`.

- `phonopy.validate_inputs`
  - Perform preflight checks (units, symmetry, required files, dimensions).

---

## 5) Common Issues and Notes

- `spglib` availability is critical for symmetry operations.
- `matplotlib` is needed for plot-oriented CLI-equivalent outputs.
- Some advanced paths require optional dependencies (`scipy`, `symfc`, etc.).
- Calculator-specific workflows depend on correct external file formats and units.
- Large supercells and dense meshes can be memory/CPU intensive; prefer async job execution in service mode.
- Keep file I/O sandboxed (workspace directories) to avoid accidental overwrite.
- Validate NAC/BORN consistency early to prevent downstream non-physical results.
- Import-first strategy is preferred; CLI fallback is possible but less structured for service responses.

---

## 6) Reference Links / Documentation

- Official repository: https://github.com/phonopy/phonopy
- Main docs index: `doc/index.md` (in repository)
- Installation guide: `doc/install.md`
- API/module usage: `doc/phonopy-module.md`
- Input format details: `doc/input-files.md`
- Output format details: `doc/output-files.md`
- Calculator interfaces: `doc/interfaces.md`
- Command options: `doc/command-options.md`
- Examples: `example/` directory