# poliastro MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core `poliastro` astrodynamics capabilities so LLM clients can run practical orbital analysis tasks through structured tools/services.

Main capabilities:
- Create and manipulate two-body orbits (`Orbit`)
- Propagate trajectories with multiple propagators (Cowell, Farnocchia, Vallado, etc.)
- Solve Lambert transfer problems (Izzo and Vallado)
- Build impulse maneuvers (e.g., Hohmann-like workflows)
- Access ephemerides and body constants
- Detect propagation events (node, altitude, eclipse-related)
- Generate orbit visualizations (2D/3D, backend-dependent)

---

## 2) Installation Method

Recommended environment: Python 3.10+ virtual environment.

Core dependencies:
- `numpy`
- `astropy`
- `scipy`

Optional (feature-dependent):
- `matplotlib` (2D plotting)
- `plotly` (interactive plotting)
- `numba` (performance acceleration in some paths)
- `astroquery`, `jplephem` (ephemerides/data workflows)

Install:
- `pip install poliastro`
- Optional extras as needed:
  - `pip install matplotlib plotly numba astroquery jplephem`

If you are packaging this as an MCP (Model Context Protocol) server, also install your MCP runtime/framework and expose the service handlers listed below.

---

## 3) Quick Start

Minimal developer flow:
1. Initialize service/client connection.
2. Call orbit creation service with attractor + state.
3. Call propagation service for future state sampling.
4. Optionally call maneuver or Lambert services for transfers.
5. Optionally call plotting service to produce visualization payloads.

Example usage flow:
- `orbit.create` → build an Earth-centered orbit from vectors or classical elements
- `orbit.propagate` → propagate to target epoch using selected propagator
- `iod.lambert.izzo` → compute transfer velocities between two position vectors and TOF
- `maneuver.hohmann` → generate impulse plan from initial orbit
- `plot.orbit.2d` or `plot.orbit.3d` → return plot artifact/serialized data

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) services/endpoints for this repo:

- `bodies.list`  
  Return supported celestial bodies and key constants.

- `orbit.create`  
  Create `Orbit` from elements, vectors, or attractor-based definitions.

- `orbit.propagate`  
  Propagate orbit with chosen method (`cowell`, `farnocchia`, `vallado`, etc.).

- `orbit.sample`  
  Sample orbit states over time grid.

- `orbit.events.propagate`  
  Propagate with event stopping/monitoring (node/altitude/eclipse conditions).

- `maneuver.create`  
  Build generic impulse maneuver.

- `maneuver.hohmann`  
  Compute Hohmann-style transfer maneuver from an initial orbit.

- `iod.lambert.izzo`  
  Lambert solve using Izzo implementation.

- `iod.lambert.vallado`  
  Lambert solve using Vallado implementation.

- `ephem.get`  
  Retrieve ephemerides states over time for supported bodies/objects.

- `earth.satellite.create`  
  Earth satellite-centric helper creation workflow.

- `plot.orbit.2d`  
  Produce 2D orbit plot output (typically matplotlib-backed).

- `plot.orbit.3d`  
  Produce 3D orbit plot output (typically plotly-backed).

- `health.check`  
  Service health/version/dependency readiness.

---

## 5) Common Issues and Notes

- Units are critical: `poliastro` is tightly integrated with `astropy.units`; always pass unit-aware values.
- Time handling: use consistent epochs/time scales to avoid subtle propagation errors.
- Propagator choice matters:
  - Fast/analytic methods for standard cases
  - Cowell/numerical for perturbed or custom force models
- Optional dependencies:
  - Missing plotting packages will break visualization services
  - Missing ephemeris packages limits some data retrieval workflows
- Performance:
  - Large sampling grids and event-heavy propagation can be expensive
  - Consider batching and configurable resolution/time windows
- Reliability:
  - Validate attractor/body consistency (e.g., Earth-centered states with Earth parameters)
  - Add input guards for singular/near-singular orbital element sets

---

## 6) Reference Links or Documentation

- Repository: https://github.com/poliastro/poliastro
- Official docs index: `docs/source/index.md` in repo
- Quickstart: `docs/source/quickstart.md`
- API overview: `docs/source/api.md`
- Examples gallery: `docs/source/examples/`
- Contribution guide: `CONTRIBUTING.md`