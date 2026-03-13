# poliastro MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a developer-friendly interface to core `poliastro` astrodynamics capabilities, including:

- Orbit creation and state handling (`Orbit`)
- Orbit propagation with multiple propagators (Cowell, Vallado, Farnocchia, etc.)
- Impulsive maneuver design and application (`Maneuver`)
- Lambert transfer solving (Izzo and Vallado methods)
- Ephemerides access (`Ephem`)
- Orbit visualization orchestration (`OrbitPlotter`)

It is designed for AI-agent and automation workflows that need reliable orbital mechanics operations through structured service endpoints.

---

## 2) Installation Method

### Requirements

- Python 3.9+ recommended
- Core dependencies:
  - `numpy`
  - `astropy`
  - `scipy`
- Optional (feature-dependent):
  - `matplotlib` / `plotly` (plotting)
  - `numba` (performance)
  - `jplephem`, `astroquery`, `pandas` (ephemerides/data workflows)

### Install

pip install poliastro numpy astropy scipy

Optional extras (as needed):

pip install matplotlib plotly numba jplephem astroquery pandas

---

## 3) Quick Start

### Typical service flow

1. Create orbit from body + elements or position/velocity  
2. Propagate orbit using selected propagator  
3. Compute transfer using Lambert solver  
4. Build/apply maneuver  
5. Return states and optional plot metadata

### Minimal Python usage example (service backend logic)

from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.propagation import CowellPropagator
from poliastro.maneuver import Maneuver

# Create orbit
orb = Orbit.circular(Earth, alt=500 * u.km)

# Propagate
future = orb.propagate(30 * u.min, method=CowellPropagator())

# Maneuver example
man = Maneuver.impulse([0, 0.1, 0] * u.km / u.s)
post = orb.apply_maneuver(man)

In an MCP (Model Context Protocol) service, these operations are exposed as structured tool endpoints returning JSON-safe outputs (state vectors, elements, metadata, warnings).

---

## 4) Available Tools and Endpoints List

Suggested endpoint set for this service:

- `orbit.create`
  - Create an `Orbit` from classical elements, vectors, or predefined constructors.
- `orbit.propagate`
  - Propagate an orbit to a target time-of-flight using a selected propagator.
- `orbit.sample`
  - Sample trajectory points for analysis/plotting.
- `maneuver.create`
  - Create impulsive maneuvers (single/multi-impulse).
- `maneuver.apply`
  - Apply maneuver to an orbit and return resulting state.
- `iod.lambert.izzo`
  - Solve Lambert boundary-value transfer with Izzo implementation.
- `iod.lambert.vallado`
  - Solve Lambert transfer with Vallado implementation (cross-check/robustness).
- `ephem.get`
  - Retrieve ephemerides-derived states for bodies/targets over time.
- `plot.orbit`
  - Generate plot-ready orbit data (2D/3D backend-aware payloads).

---

## 5) Common Issues and Notes

- Units are mandatory: `poliastro` relies heavily on `astropy.units`; unit mismatches are the #1 source of errors.
- Time handling: prefer `astropy.time.Time` for consistent epochs and frame conversions.
- Propagator choice matters:
  - Fast/simple: Markley, Mikkola
  - General numerical: Cowell
  - Problem-specific tradeoffs: Farnocchia, Vallado, etc.
- Optional dependencies:
  - Missing plotting libraries will break visualization endpoints only.
  - Missing ephemeris/data libraries affects advanced data retrieval only.
- Performance:
  - Large Monte Carlo/batch runs may require vectorization, caching, or `numba`.
- Reliability:
  - Keep endpoints deterministic (explicit propagator, tolerances, frame, epoch).
  - Return clear warnings for convergence/fallback conditions.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/poliastro/poliastro
- Official docs index: https://docs.poliastro.space/
- Quickstart: https://docs.poliastro.space/en/stable/quickstart.html
- API docs: https://docs.poliastro.space/en/stable/autoapi/
- Changelog: https://docs.poliastro.space/en/stable/changelog.html
- Contributing guide: https://github.com/poliastro/poliastro/blob/main/CONTRIBUTING.md