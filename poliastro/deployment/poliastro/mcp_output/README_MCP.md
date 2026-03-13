# poliastro MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core **poliastro** astrodynamics capabilities through MCP (Model Context Protocol) tools for LLM-driven mission analysis workflows.

Main capabilities:
- Two-body orbit creation and conversion (`Orbit`)
- Orbit propagation with multiple propagators (Cowell, Farnocchia, Vallado, etc.)
- Lambert / initial orbit determination helpers (`iod`)
- Impulsive maneuver analysis (`Maneuver`)
- Ephemerides access (`Ephem`)
- Celestial body constants (`Body`)
- Optional orbit plotting workflows (`OrbitPlotter`)

Target use cases:
- Agent-assisted trajectory design
- Programmatic orbital what-if analysis
- Automated mission planning pipelines

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Core dependencies:
  - `numpy`
  - `astropy`
  - `scipy`
- Optional (feature-dependent):
  - `matplotlib` / `plotly` (plotting)
  - `numba` (performance)
  - `astroquery`, `jplephem`, `pandas` (ephemerides/data workflows)

### Install
pip install poliastro

Optional extras (install as needed):
pip install matplotlib plotly numba astroquery jplephem pandas

For MCP (Model Context Protocol) service runtime, also install your MCP server framework and register this service in your MCP host configuration.

---

## 3) Quick Start

### Minimal flow
1. Create an orbit from vectors or classical elements.
2. Propagate to a target epoch or time-of-flight.
3. Compute maneuvers or transfer candidates.
4. Return structured results (state vectors, elements, metadata).

Example usage pattern (service-level):
- `orbit.create_from_classical` → returns orbit handle + elements
- `orbit.propagate` → returns propagated state
- `maneuver.hohmann` → returns impulse sequence and total Δv
- `ephem.sample` → returns time-series position/velocity

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `bodies.list`
  - List supported celestial bodies and key constants.

- `orbit.create_from_vectors`
  - Create `Orbit` from position/velocity vectors.

- `orbit.create_from_classical`
  - Create `Orbit` from Keplerian elements.

- `orbit.create_from_ephem`
  - Create orbit state from ephemerides source.

- `orbit.propagate`
  - Propagate an orbit using selected propagator.

- `orbit.propagators`
  - List available propagators:
  `CowellPropagator`, `DanbyPropagator`, `FarnocchiaPropagator`, `GoodingPropagator`, `MarkleyPropagator`, `MikkolaPropagator`, `PimientaPropagator`, `RecseriesPropagator`, `ValladoPropagator`.

- `iod.lambert`
  - Solve Lambert transfer (Izzo/Vallado methods).

- `maneuver.compute`
  - Build/evaluate impulsive maneuvers (e.g., Hohmann, bi-elliptic style workflows).

- `ephem.sample`
  - Generate ephemeris samples for body/orbit/time range.

- `plot.orbit` (optional)
  - Generate orbit visualization payloads (matplotlib/plotly-backed).

---

## 5) Common Issues and Notes

- **Units are critical**: poliastro relies heavily on `astropy.units`; reject unitless inputs where possible.
- **Time scales/frames**: validate frame and epoch consistency before propagation or transfer solving.
- **Optional dependency errors**: plotting and some ephemeris/data features require extra packages.
- **Performance**:
  - Long propagations and dense sampling can be expensive.
  - Prefer adaptive sampling and constrained time windows.
  - Consider `numba` for speedups where supported.
- **Numerical edge cases**:
  - Near-parabolic/high-eccentricity orbits may require careful propagator choice.
  - Lambert multi-revolution cases may produce multiple valid solutions.
- **Service design note**:
  - Return structured JSON-friendly outputs (elements, vectors, units, metadata, warnings).
  - Preserve method/solver provenance in responses for reproducibility.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/poliastro/poliastro
- Official docs index: https://docs.poliastro.space/
- API docs entry: `docs/source/api.md` in repository
- Quickstart: `docs/source/quickstart.md`
- Examples gallery: `docs/source/examples/`
- Changelog: `docs/source/changelog.md`