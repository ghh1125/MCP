# gala MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core capabilities of the `gala` astronomy dynamics library for use through MCP (Model Context Protocol).  
It is designed for developer workflows that need:

- Galactic potential modeling (analytic and composite models)
- Orbit integration and trajectory analysis
- Hamiltonian-based dynamics workflows
- Unit-safe numerical operations and serialization of models

Main exposed areas are based on:

- `gala.potential.potential.core` (`PotentialBase`, `CompositePotential`, load/save, symbolic conversion)
- `gala.potential.potential.builtin.core` (built-in models like Kepler, NFW, Plummer, etc.)
- `gala.dynamics.orbit` (`Orbit`)
- `gala.integrate.core` (`Integrator`)
- `gala.potential.hamiltonian` (`Hamiltonian`)
- `gala.units` (`UnitSystem`, `DimensionlessUnitSystem`)

---

## 2) Installation Method

### Requirements

- Python 3.9+ (recommended 3.10+)
- Required packages:
  - `numpy`
  - `scipy`
  - `astropy`
- Optional packages (feature-dependent):
  - `matplotlib` (plotting)
  - `pyyaml` (YAML I/O)
  - `h5py` (HDF5 I/O)
  - `galpy`, `agama` (interop workflows)

### Install

- Install core runtime:
  - `pip install numpy scipy astropy`
- Install gala:
  - `pip install gala`
- If running this as a local MCP (Model Context Protocol) service, also install your MCP runtime/framework package and register this service in your MCP host configuration.

---

## 3) Quick Start

### Typical flow

1. Create/select a unit system  
2. Build a potential (e.g., Plummer/NFW/composite)  
3. Wrap in a Hamiltonian (optional but common)  
4. Integrate orbits with an integrator  
5. Inspect `Orbit` outputs (positions, velocities, energies, etc.)

### Minimal Python usage example

import gala.potential as gp
import gala.dynamics as gd
from gala.units import galactic

pot = gp.PlummerPotential(m=1e11, b=5.0, units=galactic)
w0 = gd.PhaseSpacePosition(pos=[8., 0, 0], vel=[0, 220, 0])
orbit = pot.integrate_orbit(w0, dt=1.0, n_steps=1000)

### Composite potential example

disk = gp.MiyamotoNagaiPotential(m=6e10, a=6.5, b=0.26, units=galactic)
halo = gp.NFWPotential(m=1e12, r_s=20, units=galactic)
mw = gp.CompositePotential(disk=disk, halo=halo)

### Serialize/deserialize potential

mw.save("mw_model.yml")
mw2 = gp.load("mw_model.yml")

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (developer-facing contract):

- `potential.list_builtin`
  - List built-in potential classes (Kepler, Hernquist, NFW, Plummer, etc.)

- `potential.create`
  - Create a potential instance from model name + parameters + unit system

- `potential.compose`
  - Build a `CompositePotential` from multiple named components

- `potential.evaluate`
  - Evaluate potential/gradient/density at coordinates

- `potential.serialize`
  - Save potential definition to YAML/HDF5-compatible formats

- `potential.deserialize`
  - Load potential from serialized file/content

- `hamiltonian.create`
  - Construct `Hamiltonian` from potential (and optional frame)

- `orbit.integrate`
  - Integrate orbit from initial phase-space state and time grid/integration settings

- `orbit.analyze`
  - Return derived trajectory diagnostics (energy, angular momentum, basic summaries)

- `units.list` / `units.create`
  - Inspect built-in unit systems or define custom `UnitSystem`

Note: exact endpoint names depend on your MCP host conventions; the above is the practical mapping to gala core APIs.

---

## 5) Common Issues and Notes

- Units are critical:
  - Most runtime errors come from inconsistent units or missing `units=` when creating potentials.
- Optional dependency gaps:
  - Missing `pyyaml`/`h5py` may break some serialization paths.
  - Missing `matplotlib` only affects plotting.
- Numerical stability/performance:
  - Choose integrator/time step carefully (`dt`, `n_steps`).
  - Very long integrations or dense sampling can be expensive.
- Interop modules:
  - `galpy`/`agama` integrations require those libraries installed separately.
- Environment:
  - Prefer isolated virtual environments for reproducibility.
- Risk profile from analysis:
  - Import feasibility is high, intrusiveness risk is low, overall complexity is medium.

---

## 6) Reference Links / Documentation

- Upstream repository: https://github.com/adrn/gala
- Official documentation (project docs in repository): `docs/`
- Paper overview: `paper/paper.md`
- High-value source modules:
  - `src/gala/potential/potential/core.py`
  - `src/gala/potential/potential/builtin/core.py`
  - `src/gala/dynamics/orbit.py`
  - `src/gala/integrate/core.py`
  - `src/gala/potential/hamiltonian/`
  - `src/gala/units.py`
- Tests for usage patterns:
  - `tests/potential/`
  - `tests/dynamics/`
  - `tests/integrate/`