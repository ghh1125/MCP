# pyPDAF MCP (Model Context Protocol) Service README

## 1) Project Introduction

`pyPDAF` is a Python interface to PDAF (Parallel Data Assimilation Framework), designed for ensemble-based data assimilation workflows in scientific/HPC settings.  
This MCP (Model Context Protocol) service wraps key pyPDAF capabilities so clients can:

- Configure and run assimilation workflows (offline and online patterns)
- Access PDAF/PDAF3/local/OMI variants through a unified service layer
- Use MPI-enabled execution for parallel experiments
- Reuse provided example pipelines as templates

Core package namespaces exposed by pyPDAF include:

- `pyPDAF.PDAF`
- `pyPDAF.PDAF3`
- `pyPDAF.PDAFlocal`
- `pyPDAF.PDAFomi`
- `pyPDAF.PDAFlocalomi`

---

## 2) Installation Method

### Prerequisites

- Python 3.x
- `numpy`
- `mpi4py`
- MPI runtime (OpenMPI/MPICH, depending on platform)
- PDAF native compiled backend/libraries available to pyPDAF

Optional (recommended):

- `pytest` for tests
- `cython` for build-related workflows

### Install

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install numpy mpi4py`
3. Install pyPDAF from source repository root:
   - `pip install .`

If your environment requires PDAF native libraries, ensure library paths are correctly configured (`LD_LIBRARY_PATH`/platform equivalent) before running.

---

## 3) Quick Start

Minimal Python usage flow for this MCP (Model Context Protocol) service:

1. Import pyPDAF namespace(s) you need (`PDAF`, `PDAF3`, or local/OMI variants).
2. Load/configure model, state vector, observations, and filter options.
3. Run assimilation using offline or online workflow.

Typical starting points in repository examples:

- Offline: `example/offline/main.py`
- Online: `example/online/main.py`

Also review supporting modules in each example directory:

- `config.py`, `filter_options.py`, `model.py`, `obs_factory.py`, `pdaf_system.py`, `parallelisation.py`, `prepost_processing.py`

These examples are the best practical templates for wiring the MCP (Model Context Protocol) service endpoints to real runs.

---

## 4) Available Tools and Endpoints List

This repository does not define a ready-made CLI endpoint set; expose these as MCP (Model Context Protocol) service endpoints in your service layer:

- `initialize_system`  
  Initialize MPI/PDAF context, model dimensions, ensemble settings, and runtime config.

- `configure_filter`  
  Select/filter configuration (ensemble filter type, localization settings, assimilation options).

- `register_observations`  
  Configure observation operators and observation streams (A/B variants shown in examples).

- `run_offline_assimilation`  
  Execute offline assimilation loop using provided ensemble/observation input files.

- `run_online_assimilation`  
  Execute online coupled integration + assimilation workflow step-by-step.

- `collect_diagnostics`  
  Return analysis metrics, innovation/residual summaries, and run-time diagnostics.

- `finalize`  
  Clean shutdown of MPI/PDAF resources.

Suggested endpoint mapping should follow example architecture under `example/offline` and `example/online`.

---

## 5) Common Issues and Notes

- MPI issues: `mpi4py` must match your system MPI implementation.
- Native backend: pyPDAF wrappers may fail if PDAF compiled libraries are missing/incompatible.
- Parallel execution: run with MPI launcher (`mpirun`/`mpiexec`) for multi-rank scenarios.
- Input consistency: ensemble/state/observation dimensions must align exactly.
- Performance: prefer distributed-memory runs and avoid unnecessary Python-side data copying.
- Testing: use included tests (`tests/`) to validate installation baseline before large experiments.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/yumengch/pyPDAF
- Root docs: `README.md`
- Documentation sources:
  - `docs/source/introduction.md`
  - `docs/source/install.md`
  - `docs/source/develop.md`
  - `docs/source/parallel.md`
  - `docs/source/hidden_functions.md`
- Example implementations:
  - `example/offline/`
  - `example/online/`
- Package source:
  - `src/pyPDAF/`