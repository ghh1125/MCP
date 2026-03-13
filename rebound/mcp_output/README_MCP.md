# REBOUND MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the REBOUND N-body simulation library as an MCP (Model Context Protocol) service for agent/tool use.

It is designed for:
- Building and evolving gravitational simulations
- Managing particles and orbital elements
- Choosing integrators (IAS15, WHFast, Mercurius, TRACE, etc.)
- Saving/loading long runs via Simulationarchive
- Optional analysis utilities (units, variation, horizons bootstrap, plotting)

Primary core objects exposed by the service:
- `Simulation`
- `Particle` / `Particles`
- `Orbit`
- `Simulationarchive`

---

## 2) Installation Method

### Requirements
- Python 3.x
- `numpy`
- REBOUND package (includes native C extension)
- Optional:
  - `matplotlib` (plotting)
  - Jupyter/ipywidgets (notebook/widget usage)
  - MPI runtime + `mpi4py` (MPI workflows)
  - HTTP access for Horizons-based initialization

### Install
- Install from PyPI:
  - `pip install rebound`
- For development/service wiring:
  - `pip install -e .`
- Verify import:
  - `python -c "import rebound; print(rebound.__version__)"`

---

## 3) Quick Start

Create a minimal simulation workflow in your MCP (Model Context Protocol) service handler:

1. Create `Simulation`
2. Add bodies (`sim.add(...)`)
3. Select integrator (`sim.integrator = "ias15"` or `"whfast"`)
4. Integrate to target time (`sim.integrate(t_end)`)
5. Read particle states (`sim.particles[i].x`, `y`, `z`, etc.)
6. Optionally persist with `Simulationarchive`

Typical use cases:
- Two/three-body orbital evolution
- Stability/chaos experiments (with variation/frequency tools)
- Batch integrations with archive checkpoints and restart

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (developer-oriented surface):

- `simulation.create`
  - Create a new simulation with optional units, timestep, and integrator defaults.

- `simulation.add_particle`
  - Add particle by Cartesian state or orbital elements.

- `simulation.remove_particle`
  - Remove particle by index/hash.

- `simulation.configure_integrator`
  - Configure integrator type and integrator-specific options (`ias15`, `whfast`, `mercurius`, `trace`, etc.).

- `simulation.integrate`
  - Advance simulation to target time; optionally stream diagnostics.

- `simulation.state`
  - Return current simulation time, particle count, and particle states.

- `simulation.orbits`
  - Return derived orbital elements for selected particles.

- `simulation.save_archive`
  - Write simulation snapshots to Simulationarchive file.

- `simulation.load_archive`
  - Load/restart from Simulationarchive.

- `analysis.variation` (optional)
  - Run variational/sensitivity computations for chaos/stability workflows.

- `analysis.units_convert` (optional)
  - Unit conversion/helper endpoint.

- `data.horizons_fetch` (optional)
  - Initialize particles from JPL Horizons data.

- `visualization.plot` (optional)
  - Generate plots when matplotlib is available.

---

## 5) Common Issues and Notes

- Native extension build/import:
  - If install fails, ensure compiler toolchain and Python headers are available.
- Integrator choice matters:
  - `ias15` for high-accuracy adaptive integration.
  - `whfast` for long-term symplectic performance in appropriate regimes.
- Performance:
  - Large N-body runs can be CPU-heavy; prefer batch integration and archive checkpoints.
- Reproducibility:
  - Fix initial conditions, units, and integrator parameters.
- Horizons/network:
  - External ephemeris calls require network availability and may be rate-limited.
- MPI:
  - Only enable MPI endpoints in environments with configured runtime and `mpi4py`.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/hannorein/rebound
- Main docs index: `docs/index.md`
- API overview: `docs/api.md`
- Integrators: `docs/integrators.md`
- Quickstart installation: `docs/quickstart_installation.md`
- First example: `docs/quickstart_firstexample.md`
- Simulationarchive docs: `docs/simulationarchive.md`
- Python examples: `python_examples/`
- Tests (behavior references): `rebound/tests/`