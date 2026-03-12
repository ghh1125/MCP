# pyproj MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core `pyproj` capabilities as MCP (Model Context Protocol) tools for geospatial workflows:

- Coordinate Reference System (CRS) parsing and conversion
- Coordinate transformation between CRS definitions (EPSG/WKT/PROJJSON/etc.)
- Geodesic calculations (distance, azimuth, forward/inverse)
- PROJ database queries (authorities, code lookup, UTM suggestions)
- PROJ data directory and network/grid management

It is designed for LLM/tooling scenarios where reliable geospatial operations are needed through structured service endpoints.

---

## 2) Installation Method

### Requirements

- Python 3.10+
- `pyproj` (includes native PROJ integration)
- Build/runtime essentials (platform-dependent): `setuptools`, `Cython` (mainly for builds), `certifi`
- Optional: network access for downloading transformation grids

### Install

pip install pyproj

(Optional) verify installation:

python -m pyproj

If you are building from source, ensure PROJ native library compatibility is available in your environment.

---

## 3) Quick Start

### Python usage (service backend core)

from pyproj import CRS, Transformer, Geod
from pyproj.database import get_authorities, get_codes, query_utm_crs_info

# CRS parsing
crs_wgs84 = CRS.from_epsg(4326)
crs_web = CRS.from_epsg(3857)

# Coordinate transform
transformer = Transformer.from_crs(crs_wgs84, crs_web, always_xy=True)
x, y = transformer.transform(12.0, 55.0)

# Geodesic distance
geod = Geod(ellps="WGS84")
az12, az21, dist_m = geod.inv(12.0, 55.0, 13.0, 56.0)

# Database lookup
authorities = get_authorities()
epsg_codes = get_codes("EPSG", "CRS")
utm_candidates = query_utm_crs_info(datum_name="WGS 84", area_of_interest=None)

### CLI utility check

python -m pyproj

Use this for environment/version inspection and PROJ runtime diagnostics.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoint map:

- `crs.parse`
  - Parse CRS input (EPSG, WKT, PROJ string, PROJJSON) into normalized representation.
- `crs.convert`
  - Convert CRS between formats (e.g., EPSG ↔ WKT ↔ PROJJSON).
- `transform.forward`
  - Transform coordinates from source CRS to target CRS.
- `transform.batch`
  - High-throughput/iterative coordinate transformations (`itransform`-style).
- `geod.inverse`
  - Compute azimuths and distance between two lon/lat points.
- `geod.forward`
  - Compute destination point given start point, azimuth, and distance.
- `database.authorities`
  - List available CRS authorities from PROJ database.
- `database.codes`
  - List codes for an authority/type pair.
- `database.utm.query`
  - Query likely UTM CRS candidates for an area/datum.
- `datadir.get`
  - Get active PROJ data directory/search path.
- `datadir.set`
  - Set/append PROJ data directories.
- `network.get_status`
  - Check whether PROJ network access is enabled.
- `network.set_status`
  - Enable/disable PROJ network access.
- `sync.grids.list`
  - List available transformation grids.
- `sync.grids.download`
  - Download/sync required transformation grids.

---

## 5) Common Issues and Notes

- Native dependency mismatch:
  - If import/runtime fails, verify pyproj wheel/PROJ compatibility for your OS and Python version.
- Missing grid files:
  - Some high-accuracy transforms require grid datasets; enable network or pre-sync grids.
- CRS axis-order confusion:
  - Use `always_xy=True` when you expect lon/lat ordering.
- Offline environments:
  - Disable network and ship required PROJ data/grids with deployment.
- Performance:
  - Reuse `Transformer` instances for repeated operations; avoid recreating per call.
- Data directory issues:
  - Explicitly manage PROJ data path via `pyproj.datadir` in containerized environments.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pyproj4/pyproj
- Official docs: https://pyproj4.github.io/pyproj/stable/
- CLI check: `python -m pyproj`
- PROJ project: https://proj.org/

If you are implementing this as an MCP (Model Context Protocol) server, map the endpoints above directly to your service handlers and return structured JSON for deterministic tool use.