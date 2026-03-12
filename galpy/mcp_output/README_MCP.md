# galpy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core `galpy` capabilities into MCP (Model Context Protocol) tools for galactic dynamics workflows.  
It focuses on practical, high-value operations:

- Gravitational potential evaluation (forces, circular velocity, frequencies)
- Orbit creation and numerical integration
- Action-angle calculations
- Distribution-function sampling and moments
- Coordinate and unit conversions

Best fit: AI/automation-assisted astrophysics pipelines that need robust, scriptable dynamics computations.

---

## 2) Installation

### Requirements

- Python 3.x
- `numpy`
- `scipy`

Optional but recommended for richer workflows:

- `matplotlib` (plotting)
- `astropy` (units/astronomy ecosystem)
- `pynbody`, `amuse`, `numexpr` (advanced/optional integrations)

### Install commands

- Install galpy:
  `pip install galpy`

- (Optional) install extras you use:
  `pip install matplotlib astropy numexpr`

- If developing your MCP (Model Context Protocol) service wrapper locally:
  `pip install -e .`

---

## 3) Quick Start

Typical flow in this MCP (Model Context Protocol) service:

1. Choose or build a potential (e.g., Miyamoto-Nagai, NFW, Plummer, composite models)
2. Create an orbit with initial conditions
3. Integrate over time
4. Query diagnostics (energy, angular momentum, peri/apo-center, zmax)
5. Use conversion utilities for coordinate/unit transformations

Example usage pattern (service-level):

- `potential.evaluate`: evaluate potential/force at position(s)
- `orbit.integrate`: integrate an orbit in a chosen potential and time grid
- `orbit.diagnostics`: compute `E`, `L`, `e`, `rperi`, `rap`, `zmax`
- `action_angle.compute`: return actions/frequencies/angles
- `coords.transform`: convert between galactic/celestial coordinate systems

---

## 4) Available Tools and Endpoints

### Potential services
- `potential.evaluate`
  - Evaluate potential and related quantities at input phase-space points.
- `potential.forces`
  - Compute radial/vertical/azimuthal force components.
- `potential.circularity`
  - Circular velocity and orbital frequency helpers (`vcirc`, `omegac`, `epifreq`, etc.).

### Orbit services
- `orbit.create`
  - Build orbit objects from initial conditions.
- `orbit.integrate`
  - Numerically integrate orbit trajectories.
- `orbit.get_trajectory`
  - Return sampled orbit path over integration times.
- `orbit.diagnostics`
  - Compute energy, angular momentum, eccentricity, peri/apo-center, max height.

### Action-angle services
- `action_angle.actions_freqs`
  - Actions and frequencies for supported approximations/models.
- `action_angle.actions_freqs_angles`
  - Actions, frequencies, and angles in one call.
- `action_angle.orbital_extrema`
  - Derived quantities such as eccentricity, `zmax`, `rperi`, `rap`.

### Distribution-function services
- `df.sample`
  - Draw phase-space samples from DF models.
- `df.density`
  - Evaluate model density.
- `df.vmomentdensity`
  - Velocity-moment density calculations.

### Coordinate and unit services
- `coords.transform`
  - Conversions between galactocentric/cylindrical/cartesian/celestial forms.
- `units.convert`
  - Physical conversion helpers and unit-normalization accessors.

---

## 5) Common Issues and Notes

- Version compatibility:
  - Keep `numpy`/`scipy` current and compatible with your Python version.
- Optional dependencies:
  - Missing optional libraries only affect related functionality (e.g., plotting or external integrations).
- Performance:
  - Some orbit/action-angle/DF operations are computationally heavy; prefer batching and preconfigured potentials.
- Numerical settings:
  - Integration accuracy depends on timestep and integrator choice; validate against known cases.
- Units and scaling:
  - Be consistent with galpy’s physical scaling (`ro`, `vo`) across calls to avoid silent interpretation errors.
- Environment:
  - Use a clean virtual environment for reproducible MCP (Model Context Protocol) service behavior.

---

## 6) References

- Repository: https://github.com/jobovy/galpy
- Project README: https://github.com/jobovy/galpy/blob/main/README.md
- Documentation: https://docs.galpy.org
- Contributing guide: https://github.com/jobovy/galpy/blob/main/CONTRIBUTING.md
- Release/history context: https://github.com/jobovy/galpy/blob/main/HISTORY.txt