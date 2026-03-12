# PlasmaPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core PlasmaPy scientific capabilities into callable service endpoints for LLM/agent workflows.

Primary goals:
- Expose reliable plasma physics calculations (frequencies, lengths, speeds)
- Provide particle/atomic metadata lookup
- Support advanced physics workflows (dispersion, Thomson scattering, grids)

Repository: https://github.com/PlasmaPy/PlasmaPy

---

## 2) Installation

### Requirements
Required Python dependencies:
- numpy
- scipy
- astropy
- packaging

Common optional dependencies:
- h5py
- xarray
- numba
- lmfit
- matplotlib

### Install steps
1. Create and activate a Python 3.10+ environment.
2. Install PlasmaPy:
   - `pip install plasmapy`
3. Install optional extras as needed:
   - `pip install h5py xarray numba lmfit matplotlib`

If you are building this MCP (Model Context Protocol) service from source, also install your MCP runtime package and register the service entrypoint in your host application.

---

## 3) Quick Start

Typical calls this service should expose:

- Plasma frequency:
  - module: `plasmapy.formulary.frequencies`
  - function: `plasma_frequency`
- Debye length:
  - module: `plasmapy.formulary.lengths`
  - function: `Debye_length`
- Thermal speed:
  - module: `plasmapy.formulary.speeds`
  - function: `thermal_speed`
- Atomic number lookup:
  - module: `plasmapy.particles.atomic`
  - function: `atomic_number`
- Thomson spectral density:
  - module: `plasmapy.diagnostics.thomson`
  - function: `spectral_density`

Minimal development flow:
1. Start MCP (Model Context Protocol) host.
2. Register this PlasmaPy service.
3. Call a tool endpoint with structured inputs (units-aware values recommended via Astropy).
4. Return numeric result + units + metadata/errors.

---

## 4) Available Tools and Endpoints

Suggested endpoint catalog for this service:

### Core formulary services
- `frequencies.plasma_frequency`  
  Compute plasma frequency from species and density inputs.
- `frequencies.gyrofrequency`  
  Compute cyclotron/gyro frequency.
- `frequencies.lower_hybrid_frequency`  
  Lower-hybrid characteristic frequency.
- `frequencies.upper_hybrid_frequency`  
  Upper-hybrid characteristic frequency.
- `lengths.Debye_length`  
  Debye shielding scale.
- `lengths.gyroradius`  
  Particle gyroradius / Larmor radius.
- `lengths.inertial_length`  
  Species inertial length.
- `speeds.thermal_speed`  
  Thermal speed from temperature/species assumptions.
- `speeds.Alfven_speed`  
  Alfvén speed from magnetic field and density.
- `speeds.sound_speed`  
  Plasma/ion-acoustic sound speed variants.

### Particle and atomic services
- `atomic.atomic_number`
- `atomic.mass_number`
- `atomic.isotope_symbol`
- `atomic.standard_atomic_weight`
- `particles.parse` (wrapper around `Particle` class behavior)  
  Normalize particle strings and return canonical properties.

### Advanced/diagnostic services
- `diagnostics.thomson.spectral_density`  
  Thomson scattering forward model.
- `dispersion.mhd_wave` (wrapper around `MHDWave`)  
  Analytical MHD wave/dispersion helper.
- `plasma.grid.create_cartesian` (wrapper around `CartesianGrid`)  
  Grid creation for simulation-like workflows.

---

## 5) Common Issues and Notes

- Units handling is critical: PlasmaPy is Astropy-units-centric. Prefer explicit units in all inputs.
- Invalid particle strings are a common failure mode. Validate early and return actionable errors.
- Some advanced diagnostics/IO paths may require optional dependencies (e.g., `h5py`, `xarray`).
- Performance: scalar calls are cheap; large vectorized parameter sweeps can be CPU-heavy.
- Numerical edge cases: extremely low/high densities, temperatures, or fields may trigger warnings or domain errors.
- Risk profile from analysis: low intrusiveness, medium complexity, high import feasibility (~0.91).

---

## 6) References

- PlasmaPy repository: https://github.com/PlasmaPy/PlasmaPy
- PlasmaPy docs: https://docs.plasmapy.org
- PyPI package: https://pypi.org/project/plasmapy/
- Astropy units docs: https://docs.astropy.org/en/stable/units/

If you want, I can also generate a production-ready `service.json` tool schema (names, params, and response contracts) for these MCP (Model Context Protocol) services.