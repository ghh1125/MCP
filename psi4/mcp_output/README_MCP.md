# Psi4 MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps **Psi4** (quantum chemistry engine) so LLM agents can run computational chemistry tasks through standardized tool calls.

Primary capabilities:
- Single-point energy, gradient, Hessian
- Geometry optimization and frequency analysis
- Property calculations
- QCSchema/JSON execution pathways
- Optional advanced workflows (CBS, n-body, SAPT, TD-SCF) depending on environment

Core Python driver areas:
- `psi4.driver.driver` (energy/gradient/hessian/optimize/frequency/properties)
- `psi4.driver.schema_wrapper` (`run_qcschema`, `run_json`)
- `psi4.driver.task_planner` (method/basis planning support)

---

## 2) Installation Method

## System prerequisites
- Python 3.9+ recommended
- C/C++/Fortran toolchain only if building from source
- Best path for developers: Conda environment (Psi4 has `environment.yml` and multiple conda env specs)

## Minimal Python dependencies (runtime integration)
- `numpy`
- `qcelemental`
- `qcengine`
- Psi4 core binaries/libraries (installed via conda/package build)

## Typical setup
1. Create environment from project file (recommended):
   - `conda env create -f environment.yml`
2. Activate environment
3. Install Psi4 (conda-forge commonly used in practice)
4. Install your MCP (Model Context Protocol) server package that exposes Psi4 tools

If your MCP (Model Context Protocol) layer is separate, install it with pip in the same environment so it can import `psi4`.

---

## 3) Quick Start

## A. Verify Psi4 import
- Import `psi4` in Python
- Optionally set output file via `psi4.set_output_file(...)`

## B. Typical tool flow in MCP (Model Context Protocol)
1. Submit molecular input (geometry, method, basis, driver type)
2. Call a calculation tool (energy/gradient/hessian/optimize/frequency)
3. Receive structured result (energy/properties/wavefunction metadata depending on endpoint)

## C. Main callable functions (Python-side backend)
- `psi4.driver.energy(name)`
- `psi4.driver.gradient(name)`
- `psi4.driver.hessian(name)`
- `psi4.driver.optimize(name)`
- `psi4.driver.frequency(name)`
- `psi4.driver.properties(...)`
- `psi4.driver.schema_wrapper.run_qcschema(input_data, clean=True, postclean=True)`

## D. CLI fallback
When import-based execution is unavailable, use:
- `psi4`
- `python -m psi4`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) endpoint design for this repository:

- `psi4_energy`
  - Run single-point energy with method/basis and molecule input.

- `psi4_gradient`
  - Compute first derivatives for optimization pipelines.

- `psi4_hessian`
  - Compute second derivatives for vibrational analysis.

- `psi4_optimize`
  - Geometry optimization using Psi4 driver workflows.

- `psi4_frequency`
  - Harmonic frequency + thermochemistry-related outputs.

- `psi4_properties`
  - Dipole/response and related property calculations (method-dependent).

- `psi4_qcschema_run`
  - Execute QCSchema-compatible payload through `run_qcschema` / `run_json_qcschema`.

- `psi4_task_plan` (optional advanced)
  - Expose planning from `task_planner` for multi-step or composite jobs.

- `psi4_health`
  - Validate import availability, binary linkage, optional dependency availability.

---

## 5) Common Issues and Notes

- **Install complexity**: Psi4 is a complex scientific stack; prefer conda-based environments.
- **Optional features**: Many methods require extras (`adcc`, `cppe`, `ddx`, `dftd3`, `dftd4`, `gdma`, `geometric`, `mdi`, `pcmsolver`, `libefp`, `mrcc`, `chemps2`).
- **Performance**: High-level methods are CPU/RAM intensive. Enforce MCP (Model Context Protocol) request limits and job timeouts.
- **Threading/resources**: Align Psi4 thread/memory settings with MCP host limits to avoid oversubscription.
- **Schema mode reliability**: For agent workflows, QCSchema endpoints are usually more stable than raw text input parsing.
- **Fallback strategy**: Prefer Python import; fallback to CLI only when import fails.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/psi4/psi4
- Upstream README: `README.md` in repo root
- Python driver package: `psi4/driver/`
- QCSchema wrapper: `psi4/driver/schema_wrapper.py`
- Main runner: `psi4/run_psi4.py`
- Tests/examples:
  - `samples/json/`
  - `samples/python/`
  - `tests/pytests/`

If you are implementing this as an MCP (Model Context Protocol) service, start with `psi4_qcschema_run`, `psi4_energy`, and `psi4_health`, then add advanced endpoints incrementally.