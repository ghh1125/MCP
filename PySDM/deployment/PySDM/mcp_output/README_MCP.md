# PySDM MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **PySDM** (Python Super-Droplet Method) as an MCP (Model Context Protocol) interface for cloud microphysics simulations.  
It is designed for developers who want to programmatically run and inspect:

- simulation assembly (`Builder`)
- runtime stepping (`Particulator`)
- physics selection (`Formulae`)
- environments (e.g., `Box`, `Parcel`)
- core dynamics (e.g., `Condensation`, `Collision`)
- diagnostic outputs (Products)

Typical use cases: parcel-model experiments, box-model tests, collision/condensation studies, and extracting diagnostic spectra/moments.

---

## 2) Installation Method

### Recommended environment
- Python 3.10+ (3.11 commonly works well)
- Virtual environment (venv/conda)

### Core dependencies
- `numpy`
- `numba`
- `scipy`

### Optional dependencies
- `matplotlib` (plots/examples)
- `netCDF4` (NetCDF exporters)
- `vtk` (VTK exporters)
- CUDA/ThrustRTC runtime (GPU backend)

### Install commands
- `pip install -U pip setuptools wheel`
- `pip install pysdm`

If working from source repository:
- `pip install -e .`

For examples/tutorial-style workflows, install additional scientific stack as needed (plotting/export extras).

---

## 3) Quick Start

Minimal flow in this MCP (Model Context Protocol) service:

1. Create backend (usually `Numba` for CPU).
2. Choose environment (`Box` for simplest setup, `Parcel` for parcel studies).
3. Build simulation with `Builder`.
4. Register dynamics (e.g., condensation/collisions).
5. Run timesteps through `Particulator`.
6. Query products/diagnostics.

Typical service call sequence:
- `health` → check runtime readiness
- `create_simulation` → configure backend/environment/formulae
- `add_dynamic` → attach processes (condensation/collision/etc.)
- `run` → advance simulation
- `get_products` → fetch diagnostics
- `reset`/`dispose` → release simulation context

---

## 4) Available Tools and Endpoints

Below is a practical endpoint set for this MCP (Model Context Protocol) service.

- **health**  
  Returns service status, version, and backend availability.

- **list_backends**  
  Lists available compute backends (`Numba`, optional `ThrustRTC`).

- **list_environments**  
  Lists supported environments (`Box`, `Parcel`, `Kinematic1D`, `Kinematic2D` if exposed).

- **list_dynamics**  
  Lists dynamic processes (e.g., `Condensation`, `Collision`, `Freezing`, `Displacement`).

- **list_products**  
  Lists diagnostics/products available for extraction.

- **create_simulation**  
  Creates a simulation session using selected backend, formulae, and environment config.

- **add_dynamic**  
  Registers one dynamic process with parameters in the active simulation session.

- **configure_products**  
  Registers product outputs to track during/after run.

- **run**  
  Advances the simulation for `n_steps` or `t_end`.

- **get_state**  
  Returns current simulation metadata/state summary (time, step, counts, etc.).

- **get_products**  
  Returns computed diagnostics (moments, concentrations, spectra, RH, etc.).

- **reset_simulation / dispose_simulation**  
  Clears one simulation context and releases resources.

---

## 5) Common Issues and Notes

- **Numba warm-up/JIT latency**: first run can be slower; subsequent runs are faster.
- **GPU backend complexity**: `ThrustRTC` requires compatible CUDA runtime and extra setup.
- **Large simulations**: watch memory pressure from particle count and product history.
- **Exporter dependencies**: NetCDF/VTK tools require `netCDF4`/`vtk` installed.
- **Reproducibility**: set random seeds when supported by selected dynamics.
- **Incremental debugging**: start with `Box + Condensation` before adding collisions/freezing.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/atmos-cloud-sim-uj/PySDM
- Main package directory: `PySDM/`
- Core APIs:
  - `PySDM.builder.Builder`
  - `PySDM.particulator.Particulator`
  - `PySDM.formulae.Formulae`
- Key modules:
  - Backends: `PySDM.backends.numba`, `PySDM.backends.thrust_rtc`
  - Environments: `PySDM.environments.box`, `PySDM.environments.parcel`
  - Dynamics: `PySDM.dynamics.*`
  - Products: `PySDM.products.*`
- Examples: `examples/PySDM_examples/`
- Tests (usage patterns): `tests/smoke_tests/`, `tests/unit_tests/`