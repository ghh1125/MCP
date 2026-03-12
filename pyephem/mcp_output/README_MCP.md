# PyEphem MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the **PyEphem** astronomy library to provide practical celestial calculations for applications and agents.

Typical use cases:
- Compute Sun/Moon/planet positions from an observer location and time
- Find rise/set/transit events
- Query lunar phases (new/full/quarter moon times)
- Compute equinoxes and solstices
- Resolve built-in stars and cities

Core PyEphem modules used:
- `ephem` (main astronomy API)
- `ephem.stars` (star lookup)
- `ephem.cities` (city lookup)

---

## 2) Installation Method

Prerequisites:
- Python 3.x
- Build toolchain for C extension (PyEphem includes a compiled extension; setup uses `setup.py`/CMake flow)

Install dependencies:
- `pip install -r requirements.txt`

Install package/service locally:
- `pip install .`

If you are building an MCP (Model Context Protocol) server wrapper around this repo, install your MCP runtime framework separately, then add this package as a dependency.

---

## 3) Quick Start

Basic usage examples (inside your MCP (Model Context Protocol) service handlers):

- Create observer and compute Sun position:
  import ephem
  obs = ephem.Observer()
  obs.lat, obs.lon = '40.7128', '-74.0060'
  obs.date = '2026/03/12 12:00:00'
  sun = ephem.Sun(obs)
  print(sun.alt, sun.az)

- Next moon phase:
  import ephem
  print(ephem.next_full_moon('2026/03/12'))

- Rise/set times:
  import ephem
  obs = ephem.Observer()
  obs.lat, obs.lon = '51.5074', '-0.1278'
  obs.date = '2026/03/12'
  sun = ephem.Sun()
  print(obs.next_rising(sun), obs.next_setting(sun))

- Star and city lookup:
  import ephem
  sirius = ephem.star('Sirius')
  london = ephem.city('London')
  print(sirius, london)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (mapped to PyEphem):

1. `get_body_position`
- Input: `body`, `observer(lat, lon, elevation?)`, `date`
- Uses classes like `Sun`, `Moon`, `Mars`, `Jupiter`, etc.
- Output: altitude, azimuth, RA/Dec, distance (as available)

2. `get_rise_set_transit`
- Input: `body`, `observer`, `date`, `method?`
- Uses `Observer.next_rising/next_setting/next_transit`
- Output: rise/set/transit timestamps

3. `get_moon_phase_events`
- Input: `date`, `direction(next|previous)`
- Uses:
  - `next_new_moon`, `next_first_quarter_moon`, `next_full_moon`, `next_last_quarter_moon`
  - previous equivalents
- Output: phase event timestamps

4. `get_season_events`
- Input: `date`, `direction(next|previous)`, `type(equinox|solstice|specific season point)`
- Uses `next_equinox/solstice` and seasonal helpers
- Output: event timestamp

5. `resolve_star`
- Input: `name`
- Uses `ephem.star(name)`
- Output: star object fields (RA/Dec, etc.)

6. `resolve_city`
- Input: `name`
- Uses `ephem.city(name)` / `ephem.cities.lookup(...)`
- Output: city observer data (lat/lon/elevation/timezone fields if available)

7. `convert_time`
- Input: `date`, `tzinfo`
- Uses `localtime`, `to_timezone`
- Output: converted datetime

---

## 5) Common Issues and Notes

- C extension build errors:
  - Ensure compiler/build tools are installed.
  - Upgrade pip/setuptools/wheel first.
- Date/time handling:
  - PyEphem uses its own date conventions; always pass explicit UTC-aware values when possible.
- Observer accuracy:
  - Correct latitude/longitude/elevation is essential for reliable rise/set results.
- Circumpolar edge cases:
  - Handle `AlwaysUpError`, `NeverUpError`, and `CircumpolarError` in service responses.
- Name lookup limitations:
  - Built-in star/city catalogs are finite; add fallback logic for unknown names.
- Performance:
  - Single queries are fast; batch requests should reuse observer/object instances where practical.
- Validation:
  - Use input validation for body names, date formats, and coordinate ranges in your MCP (Model Context Protocol) endpoints.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/brandon-rhodes/pyephem
- Package entry module: `ephem/__init__.py`
- Useful source files:
  - `ephem/stars.py`
  - `ephem/cities.py`
- Tests (great for expected behavior and edge cases):
  - `ephem/tests/test_bodies.py`
  - `ephem/tests/test_rise_set.py`
  - `ephem/tests/test_usno.py`
  - `ephem/tests/test_stars.py`