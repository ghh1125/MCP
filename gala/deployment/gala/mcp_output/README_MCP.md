# Gala MCP (Model Context Protocol) Service README

## 1) Project Introduction

This project provides an MCP (Model Context Protocol) **service layer** for the [`gala`](https://github.com/adrn/gala) dynamics library, focused on practical astrophysics workflows:

- Build and validate gravitational potential models
- Integrate orbits from initial phase-space conditions
- Compute diagnostics (energies, angular momentum, basic orbit summaries)
- Handle astrophysical unit normalization safely
- Serialize/deserialize models for reproducible workflows

Primary target users are developers building AI-assisted scientific tooling, simulation backends, or research automation pipelines.

---

## 2) Installation

### Requirements

Core Python dependencies (from repository analysis):

- `numpy`
- `scipy`
- `astropy`
- `pyyaml`

Optional (feature-specific):

- `matplotlib` (plotting)
- `agama` (interop-related features/tests)
- `galpy` (interop-related features/tests)
- native acceleration toolchain (for some compiled/Fortran/C-extension paths)

### Install commands

Install base dependencies and gala:

pip install numpy scipy astropy pyyaml gala

If you are developing the MCP (Model Context Protocol) service itself, also install your service runtime dependencies (for example `mcp`, `pydantic`, etc.) per your server framework.

---

## 3) Quick Start

### A. Typical service flow

1. Create a unit system (`gala.units.UnitSystem`)
2. Instantiate a builtin potential (e.g., `HernquistPotential`, `NFWPotential`, `MiyamotoNagaiPotential`)
3. Integrate an orbit with a pure-Python integrator (`LeapfrogIntegrator` or `DOPRI853Integrator`)
4. Return sampled orbit states + diagnostics in service responses

### B. Minimal example flow (conceptual)

- `potential.create_builtin` → returns serialized potential handle/config
- `orbit.integrate` with initial conditions and time grid
- `orbit.diagnostics` for summary metrics
- `potential.serialize` for persistence/export

Use `Leapfrog` for speed and robust defaults; use `DOPRI853` when higher precision is needed.

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) **services**:

1. `units.normalize`
- Convert/validate incoming physical quantities to a declared unit system.
- Prevents mixed-unit input errors before simulation.

2. `potential.create_builtin`
- Create named builtin potentials (Kepler, Hernquist, NFW, Miyamoto-Nagai, Plummer, Logarithmic, etc.) from typed parameters.
- Returns a service-safe potential spec/handle.

3. `potential.evaluate`
- Evaluate potential value, acceleration/force, and optionally gradient/Hessian-like derived quantities at positions.

4. `potential.compose`
- Build `CompositePotential` from multiple components and weights/parameters.

5. `orbit.integrate`
- Integrate trajectories in a given potential from initial conditions over a time grid.
- Integrator options: `leapfrog`, `dopri853`.

6. `orbit.diagnostics`
- Compute derived quantities from integrated orbits (energy behavior, angular momentum, basic statistics).

7. `potential.serialize`
- Export potential definitions to dict/YAML-like payloads (compatible with gala I/O patterns).

8. `potential.deserialize`
- Reconstruct potential objects from serialized payloads.

---

## 5) Common Issues and Notes

- **Unit consistency is critical**: Always normalize inputs through a unit-system service before potential/orbit calls.
- **Integrator tradeoff**:
  - `leapfrog`: faster, good default for many exploratory runs
  - `dopri853`: slower but typically higher precision
- **Performance**: Pure-Python paths are easy to deploy, but large batch integrations may benefit from compiled acceleration.
- **Optional dependencies**: Missing `agama`/`galpy` only impacts interop-related functionality.
- **Numerical stability**: Very long integrations or extreme parameter ranges may require smaller timesteps and tighter tolerances.
- **Environment**: Prefer isolated virtual environments and pin scientific package versions for reproducibility.

---

## 6) References

- Gala repository: https://github.com/adrn/gala
- Gala documentation (project docs in repo): `docs/`
- Key modules for MCP (Model Context Protocol) service design:
  - `gala.potential.potential.core`
  - `gala.potential.potential.builtin.core`
  - `gala.dynamics.orbit`
  - `gala.integrate.pyintegrators.leapfrog`
  - `gala.integrate.pyintegrators.dopri853`
  - `gala.units`
  - `gala.potential.potential.io`