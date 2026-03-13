# gala MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core capabilities from the `gala` astrophysics library into MCP (Model Context Protocol)-friendly tools for:

- Defining gravitational potentials (e.g., Plummer, Hernquist, NFW, Miyamoto-Nagai)
- Managing physical unit systems consistently
- Integrating orbits with numerical integrators (Leapfrog, DOPRI853)
- Returning orbit trajectories and basic derived diagnostics

It is aimed at developer workflows where an LLM or external client needs structured access to orbit-dynamics computations.

---

## 2) Installation Method

### Prerequisites
- Python 3.10+ (recommended)
- `numpy`, `scipy`, `astropy`, `pyyaml`

### Core install
- `pip install gala`
- `pip install mcp` (or your MCP (Model Context Protocol) runtime package)

### Optional dependencies
- `matplotlib` for plotting/debug visualization
- `h5py` for data IO extensions
- `galpy` / `agama` for interoperability features
- C/Cython toolchain for compiled-performance paths

### Service setup (typical)
- Install this MCP (Model Context Protocol) service package in your environment
- Configure your MCP (Model Context Protocol) host/client to launch the service entry module
- Verify imports: `gala`, `astropy`, and integrator modules load successfully

---

## 3) Quick Start

### Typical flow
1. Create/select a `UnitSystem`
2. Build a potential (e.g., `PlummerPotential`)
3. Choose an integrator (`LeapfrogIntegrator` for robust default)
4. Parse or provide time specification
5. Run integration and return orbit samples

### Minimal usage pattern
- Input: potential type + parameters, initial phase-space state, time grid/spec
- Tool call: `integrate_orbit`
- Output: positions/velocities over time (Orbit-like structured result)

### Recommended defaults
- Integrator: `LeapfrogIntegrator` for Hamiltonian/symplectic-friendly tasks
- Adaptive alternative: `DOPRI853Integrator` for non-symplectic or accuracy-focused runs
- Keep units explicit (avoid silent unit mismatch)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints for this repository:

- `health_check`
  - Confirms service readiness and dependency import status.

- `list_potentials`
  - Returns supported built-in potential models (Plummer, Hernquist, NFW, Miyamoto-Nagai, Isochrone, Kepler, Logarithmic, HarmonicOscillator, etc.).

- `create_potential`
  - Creates a potential from model name + parameter dictionary + units.

- `compose_potential`
  - Builds a `CompositePotential` from multiple components.

- `set_unit_system`
  - Configures/validates `UnitSystem` or dimensionless mode.

- `parse_time_spec`
  - Uses gala time parsing logic to normalize integration time input.

- `integrate_orbit`
  - Main compute endpoint: integrates orbit from initial conditions under a selected potential/integrator.

- `orbit_summary`
  - Returns lightweight diagnostics from integrated orbit (shape, time range, basic invariants/metadata).

- `potential_serialize` / `potential_deserialize`
  - Converts potential objects to/from dictionary form (`to_dict` / `from_dict`) for reproducible workflows.

---

## 5) Common Issues and Notes

- Unit mismatches are the most common source of incorrect results.
  - Always provide explicit units for position, velocity, mass, and time.
- Performance depends on integrator and time grid density.
  - Start with coarse grids, then refine.
- Pure-Python integrators are easiest to deploy; compiled paths may need extra build tooling.
- Optional interop (`galpy`, `agama`) may require separate installation and compatible versions.
- For long integrations, monitor numerical stability and conservation behavior.
- Use repository tests (especially integrator tests) as smoke-test references for your service behavior.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/adrn/gala
- Main package source: `src/gala`
- Potentials core: `src/gala/potential/potential/core.py`
- Built-in potentials: `src/gala/potential/potential/builtin/core.py`
- Orbit object: `src/gala/dynamics/orbit.py`
- Integrators:
  - `src/gala/integrate/pyintegrators/leapfrog.py`
  - `src/gala/integrate/pyintegrators/dopri853.py`
- Tests for validation patterns: `tests/` (notably `tests/integrate/` and `tests/dynamics/`)