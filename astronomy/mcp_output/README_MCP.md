# Astronomy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the excellent **Astronomy Engine** project by [cosinekitty/astronomy](https://github.com/cosinekitty/astronomy) and exposes practical astronomy calculations through MCP (Model Context Protocol) tools.

It is designed for developer workflows that need:
- Planet/Moon/Sun positions
- Rise/set/transit events
- Moon phases, eclipses, apsides, nodes
- Coordinate transforms (equatorial/ecliptic/horizon/galactic)
- Illumination, elongation, sidereal time, and related search functions

Primary backend: `source/python/astronomy/astronomy.py` (large, self-contained library with rich API).

---

## 2) Installation Method

### Requirements
- Python 3.9+ (3.x supported; use modern Python)
- Standard library only for core engine usage
- No strict `requirements.txt` detected for the core Python source package

### Install options

#### Option A: Use upstream Python package layout
1. Clone repository
2. Install from `source/python`:
- `pip install -e source/python`

#### Option B: Local module usage (quick prototype)
- Copy or import `source/python/astronomy/astronomy.py` directly in your service project.

### Suggested MCP (Model Context Protocol) setup
- Register service handlers that map tool names to functions in `astronomy.py`.
- Keep one shared process/module instance to avoid repeated import overhead.

---

## 3) Quick Start

### Minimal usage flow
1. Create a `Time` value
2. Choose a `Body` and optional `Observer`
3. Call a computation/search function
4. Return structured JSON from your MCP (Model Context Protocol) service

### Example calls (typical)
- Geocentric vector: `GeoVector(body, time, aberration)`
- Horizontal coordinates: `Horizon(time, observer, ra, dec, refraction)`
- Rise/set search: `SearchRiseSet(body, observer, direction, startTime, limitDays, metersAboveGround)`
- Moon phase: `MoonPhase(time)` or `SearchMoonQuarter(startTime)`
- Eclipses: `SearchLunarEclipse(startTime)`, `SearchGlobalSolarEclipse(startTime)`

Recommended response shape for MCP (Model Context Protocol):
- `input`: validated request
- `result`: engine output (normalized fields)
- `units`: explicit units (AU, km, degrees, UTC time)
- `meta`: precision/refraction/aberration options used

---

## 4) Available Tools and Endpoints List

Suggested tool surface for your MCP (Model Context Protocol) service:

- `time.parse`  
  Parse/normalize input time into engine `Time`.

- `body.code`  
  Resolve body name to internal body code (`BodyCode`).

- `position.geo`  
  Geocentric vector/state (`GeoVector`, `GeoMoon`, `GeoMoonState`, `GeoEmbState`).

- `position.helio`  
  Heliocentric vector/state/distance (`HelioVector`, `HelioState`, `HelioDistance`).

- `position.bary`  
  Barycentric state (`BaryState`).

- `coords.equator`  
  Equatorial coordinates (`Equator`, `EquatorFromVector`).

- `coords.horizon`  
  Horizontal coordinates and reverse mapping (`Horizon`, `HorizonFromVector`, `VectorFromHorizon`).

- `coords.transforms`  
  Rotation matrix conversions between EQJ/EQD/ECL/ECT/GAL/HOR (`Rotation_*`, `RotateVector`, `RotateState`).

- `events.rise_set`  
  Rise/set and altitude searches (`SearchRiseSet`, `SearchAltitude`, `SearchHourAngle`).

- `events.moon`  
  Phase/quarter/node/apsis tools (`MoonPhase`, `SearchMoonPhase`, `SearchMoonQuarter`, `SearchMoonNode`, `SearchLunarApsis`).

- `events.eclipse`  
  Lunar/global/local solar eclipse search (`SearchLunarEclipse`, `SearchGlobalSolarEclipse`, `SearchLocalSolarEclipse`).

- `events.transit`  
  Transit search (`SearchTransit`, `NextTransit`).

- `astro.illumination`  
  Illumination/magnitude/elongation (`Illumination`, `Elongation`, `SearchPeakMagnitude`, `SearchMaxElongation`).

- `astro.misc`  
  Sidereal time, seasons, libration, Jupiter moons, constellation, Lagrange points.

---

## 5) Common Issues and Notes

- Time scale confusion: distinguish UTC/UT/TT carefully; always document what you accept/return.
- Units: many APIs use AU and degrees; don’t mix km/AU silently.
- Observer parameters: longitude/latitude sign conventions must be explicit.
- Refraction settings affect horizon results; expose `Refraction` mode in endpoint inputs.
- Performance: first import is heavy (large single-file module). Warm up service process at startup.
- Validation: reject unsupported body names early (`BodyCode` helpful).
- Determinism: use fixed tolerance/options for search APIs to keep stable outputs across environments.

---

## 6) Reference Links or Documentation

- Upstream repository: https://github.com/cosinekitty/astronomy
- Main project README: `README.md` (repo root)
- Python source docs: `source/python/README.md`
- Python engine module: `source/python/astronomy/astronomy.py`
- Multi-language demos:
  - `demo/python/README.md`
  - `demo/nodejs/README.md`
  - `demo/c/README.md`
  - `demo/csharp/README.md`
  - `demo/java/README.md`
  - `demo/kotlin/README.md`

If you want, I can also generate a ready-to-use MCP (Model Context Protocol) tool schema (names, inputs, outputs) for these endpoints.