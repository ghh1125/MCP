# ASE MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes key ASE (Atomic Simulation Environment) capabilities through MCP (Model Context Protocol) tools for developer workflows.

Main functions:
- Build and edit atomic structures (`Atoms`, bulk/surface/molecule builders)
- Read/write many chemistry/materials formats (`ase.io`)
- Run calculator-backed evaluations (energy/forces/stress, depending on backend)
- Geometry optimization and MD workflows
- NEB/phonons/thermochemistry helper workflows
- Query/store results with ASE DB utilities

This is best for automating simulation pipelines from LLM/agent clients using MCP (Model Context Protocol).

---

## 2) Installation Method

### Requirements
- Python 3.x
- Required: `numpy`
- Optional but common: `scipy`, `matplotlib`
- Optional integrations:
  - GUI: `tkinter`
  - DB: `psycopg2`, `mysqlclient`
  - Trajectory/data: `netCDF4`
  - External calculators: VASP/CP2K/Quantum ESPRESSO/etc. executables

### Install ASE
- `pip install ase`
- Or from source repo:
  - `pip install .`

### Verify
- `python -c "import ase; print(ase.__version__)"`

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Build/load an `Atoms` object
2. Attach a calculator (e.g., EMT for quick local tests)
3. Run property evaluation or optimization
4. Export structures/results

### Minimal usage examples (service-side intent)
- Build crystal: use `ase.build.bulk(...)`
- Build molecule: use `ase.build.molecule(...)`
- Read structure: use `ase.io.read(...)`
- Write structure: use `ase.io.write(...)`
- Optimize: use `ase.optimize.BFGS(...)`
- NEB: use `ase.neb.NEB(...)`
- DB query/write: use `ase.db.connect(...)`

### CLI shortcuts (useful for ops/debug)
- `ase info`
- `ase build ...`
- `ase run ...`
- `ase find ...`
- `ase db ...`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `structure.build`
  - Create bulk/surface/molecule/nanotube/supercell structures.
- `structure.modify`
  - Apply constraints, transforms, repeats, adsorbates, vacuum, etc.
- `io.read`
  - Import structures/trajectories from supported formats.
- `io.write`
  - Export structures/trajectories (xyz, cif, vasp, espresso, etc.).
- `calculator.attach`
  - Configure and bind a calculator to `Atoms`.
- `calculator.evaluate`
  - Return energy/forces/stress and related properties.
- `optimize.run`
  - Execute geometry optimization (BFGS/LBFGS/FIRE/Precon variants).
- `md.run`
  - Run molecular dynamics (Verlet/Langevin/NVT/NPT variants).
- `neb.run`
  - Setup/interpolate/execute NEB and analyze barrier paths.
- `phonon.run`
  - Phonon displacements and post-processing helpers.
- `thermo.compute`
  - Thermochemistry utilities (ideal gas, harmonic, hindered, crystal).
- `db.query`
  - Query ASE databases (SQLite/PostgreSQL/MySQL backends).
- `db.write`
  - Store structures and results with metadata.
- `cli.exec`
  - Optional wrapper to invoke ASE CLI commands when needed.

---

## 5) Common Issues and Notes

- External calculators are not bundled: configure executable paths, pseudopotentials, and licenses separately.
- Many advanced workflows require optional Python deps (`scipy`, `matplotlib`, DB drivers).
- GUI tools need desktop environment and `tkinter`.
- Large trajectories/NEB/phonon jobs can be memory-heavy; prefer chunked I/O and explicit cleanup.
- For production MCP (Model Context Protocol) service use:
  - isolate environments per project
  - enforce execution timeouts
  - capture calculator stdout/stderr
  - persist artifacts (input/output/logs/trajectory)
- If running remotely/HPC, ensure MPI/executable environment is available to the MCP (Model Context Protocol) runtime.

---

## 6) Reference Links / Documentation

- Upstream repository: https://github.com/yfyh2013/ase
- ASE docs (official): https://wiki.fysik.dtu.dk/ase/
- CLI modules of interest:
  - `ase.cli.main`
  - `ase.cli.build`
  - `ase.cli.run`
  - `ase.cli.info`
  - `ase.cli.find`
  - `ase.db.cli`
- Core packages:
  - `ase.build`, `ase.io`, `ase.calculators`, `ase.optimize`, `ase.md`, `ase.neb`, `ase.db`, `ase.dft`, `ase.vibrations`