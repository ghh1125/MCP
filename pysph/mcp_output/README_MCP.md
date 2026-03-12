# PySPH MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical interface to run and automate common PySPH workflows:

- Run built-in simulation examples
- Execute solver/application pipelines programmatically
- Evaluate SPH equations on particle arrays
- Convert simulation outputs to XDMF/VTK
- Manage generated cache/artifacts

It is designed for developer use in scripting, orchestration, and post-processing pipelines.

---

## 2) Installation

### Requirements

Core dependencies (from repository analysis):

- numpy
- cython
- mako
- pyzoltan

Common optional dependencies:

- mpi4py (parallel runs)
- compyle (accelerated compute paths)
- h5py (I/O)
- vtk (visualization/export)
- mayavi (interactive visualization)
- ipywidgets/jupyter (notebook tools)
- gmsh (mesh-related tooling)

### Install Commands

- Clone and install:
  - `git clone https://github.com/pypr/pysph.git`
  - `cd pysph`
  - `pip install -U pip`
  - `pip install -r requirements.txt`
  - `pip install -e .`

- For tests/dev:
  - `pip install -r requirements-test.txt`

---

## 3) Quick Start

### A. Run an example simulation

- `python -m pysph.examples.run dam_break_2d`
- Or run module directly:
  - `python -m pysph.examples.dam_break_2d`

### B. Use core API objects in your service logic

Typical flow in code:

1. Build particle arrays (e.g., via `pysph.base.utils.get_particle_array`)
2. Define equations/groups (`Equation`, `Group`, `MultiStageEquations`)
3. Select a scheme (`Scheme`, `SchemeChooser`)
4. Configure `Solver` and `Integrator`
5. Run through `Application`

### C. Post-process outputs

- Export XDMF: `python -m pysph.tools.dump_xdmf ...`
- Convert to VTK: `python -m pysph.tools.pysph_to_vtk ...`

---

## 4) Available Tools and Endpoints

For this MCP (Model Context Protocol) service, expose the following practical endpoints:

- `run_example`
  - Runs bundled PySPH examples (backed by `pysph.examples.run`)
  - Inputs: example name, runtime args
  - Output: run status, output directory, logs

- `run_application`
  - Executes a PySPH `Application` class/script
  - Inputs: module/class path, simulation parameters
  - Output: status, generated files, summary metrics

- `evaluate_sph`
  - Uses `SPHEvaluator` for equation evaluation outside a full solver loop
  - Inputs: particle arrays, equations, kernel/config
  - Output: computed particle properties

- `export_xdmf`
  - Converts PySPH outputs into XDMF (via `pysph.tools.dump_xdmf`)
  - Inputs: output path, selection options
  - Output: XDMF artifacts

- `export_vtk`
  - Converts outputs to VTK (via `pysph.tools.pysph_to_vtk`)
  - Inputs: output path, conversion options
  - Output: VTK files

- `manage_cache`
  - Cleans/inspects generated cache/compiled artifacts
  - Inputs: cache scope, action
  - Output: cleanup/report result

- `list_examples`
  - Lists discoverable bundled examples
  - Output: names, modules, categories

- `health_check`
  - Validates runtime dependencies and importability
  - Output: environment diagnostics

---

## 5) Common Issues and Notes

- Build/toolchain issues:
  - PySPH uses compiled paths (Cython/related tooling). Ensure compiler toolchain is available.
- Optional dependency gaps:
  - Missing `vtk`, `h5py`, `mayavi`, `mpi4py`, etc. will disable related features/endpoints.
- Parallel execution:
  - MPI workflows need compatible MPI runtime and `mpi4py`.
- Performance:
  - Large cases are CPU/memory intensive; tune particle count, timestep, and output frequency.
- Import feasibility:
  - Repo complexity is high; keep endpoint implementations thin and prefer subprocess isolation for long runs.
- Reproducibility:
  - Pin dependency versions and keep consistent Python environment across nodes.

---

## 6) References

- Repository: https://github.com/pypr/pysph
- Package layout highlights:
  - `pysph/solver` (Application/Solver)
  - `pysph/sph` (equations, schemes, integrators)
  - `pysph/base` (particle arrays, kernels, NNPS utilities)
  - `pysph/tools` (conversion, cache, evaluators)
  - `pysph/examples` (ready-to-run cases)
- Docs config present in repo: `docs/source/conf.py` (Sphinx-based documentation setup).