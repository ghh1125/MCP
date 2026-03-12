# REBOUND MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the REBOUND N-body simulation library as an MCP (Model Context Protocol) service so LLM clients can create, run, inspect, and persist gravitational simulations programmatically.

Primary capabilities:
- Build and configure `Simulation` objects
- Add/manage particles (`Particle`, `Particles`)
- Integrate forward in time with selectable integrators
- Compute orbital/diagnostic outputs
- Save/load runs via `Simulationarchive`
- Optional ephemeris initialization via JPL Horizons helpers

---

## 2) Installation Method

### Requirements
- Python 3.x
- `numpy`
- Build tooling: `setuptools`, `wheel`
- Optional:
  - `matplotlib` (plotting)
  - Jupyter/ipywidgets stack (notebook widgets)
  - Network access for Horizons-based initialization
  - MPI runtime for MPI workflows

### Install REBOUND
- `pip install rebound`

If building from source:
- Clone repository, then install in editable mode:
  - `pip install -e .`

---

## 3) Quick Start

### Typical flow in this MCP (Model Context Protocol) service
1. Create simulation  
2. Add bodies (mass + state or orbital elements)  
3. Choose integrator and timestep  
4. Integrate to target time  
5. Query particles/orbits/diagnostics  
6. Persist or reload archive

### Minimal usage example (service-level workflow)
- `simulation.create` with units/integrator config
- `particles.add` for star/planets/test particles
- `simulation.integrate` to time `t_end`
- `simulation.state` or `orbits.compute` for results
- `archive.save` for reproducibility

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `simulation.create`  
  Create a new REBOUND `Simulation` session with base config (integrator, timestep, units).

- `simulation.configure`  
  Update simulation settings (gravity options, boundary/collision modes, reference frame options).

- `particles.add`  
  Add one or many particles by Cartesian state or orbital elements.

- `particles.list`  
  Return particle inventory and key fields (mass, position, velocity, hash/index).

- `particles.update`  
  Modify particle properties or orbital parameters.

- `particles.remove`  
  Remove particle(s) by index/hash.

- `simulation.integrate`  
  Advance simulation to a target time; optionally stream checkpoints.

- `simulation.state`  
  Fetch current simulation time, energy/diagnostics, and selected particle states.

- `orbits.compute`  
  Compute osculating orbital elements from current particle states.

- `variation.enable` / `variation.metrics`  
  Enable variational equations and expose chaos indicators (e.g., MEGNO-related workflows).

- `archive.save`  
  Persist run snapshots via `Simulationarchive`.

- `archive.load`  
  Reload prior archives for replay/inspection.

- `archive.sample`  
  Query archived states at specific times/indices.

- `analysis.frequency`  
  Run frequency-analysis utilities on trajectory data.

- `horizons.resolve`  
  Initialize objects from JPL Horizons data (network-dependent).

- `units.convert`  
  Convert and validate units for safer user-facing calls.

- `health.ping`  
  Basic service liveness/readiness check.

---

## 5) Common Issues and Notes

- Native build requirements: some environments need compiler toolchains for scientific packages.
- Integrator choice matters:
  - Long-term orbital stability studies often use symplectic methods (e.g., WHFast family).
  - High-accuracy close-encounter cases may prefer IAS15/BS-style workflows.
- Horizons calls require internet access and may fail in restricted environments.
- Large particle counts can be CPU/memory intensive; prefer archive checkpoints over full in-memory history.
- Keep units explicit to avoid subtle interpretation errors.
- For reproducibility, store:
  - integrator + timestep
  - initial conditions
  - random seeds (if used)
  - archive files and REBOUND version

---

## 6) Reference Links / Documentation

- Repository: https://github.com/hannorein/rebound
- Main docs index: `docs/index.md`
- API overview: `docs/api.md`
- Integrators: `docs/integrators.md`
- Simulation variables/reference: `docs/simulationvariables.md`
- Simulation archive: `docs/simulationarchive.md`
- Quickstart install: `docs/quickstart_installation.md`
- Examples:
  - `python_examples/`
  - `docs/examples.md`

If you want, I can also provide a production-ready `tools` schema (JSON-style input/output contracts) for each MCP (Model Context Protocol) service endpoint above.