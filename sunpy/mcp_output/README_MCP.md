# SunPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical interface to core SunPy capabilities for solar/space-science workflows, including:

- Data search and download (Fido-based)
- Solar map loading and processing
- Time series loading and analysis
- Time parsing and time-range normalization
- Solar ephemeris calculations
- Coordinate frame conversion helpers

It is designed for agent/tooling scenarios where users need reliable, scriptable access to SunPy’s high-value APIs without navigating the full library surface.

---

## 2) Installation Method

### Requirements

Core dependencies (minimum):
- numpy
- astropy
- packaging

Common optional dependencies (recommended for full features):
- matplotlib, reproject, parfive
- drms, zeep
- asdf, scipy, pandas
- aiohttp, h5py

### Install commands

- Install SunPy:
  pip install sunpy

- Install commonly used optional extras manually (example):
  pip install matplotlib reproject parfive drms zeep asdf scipy pandas aiohttp h5py

If you package this as a standalone MCP (Model Context Protocol) service, include SunPy and optional dependencies in your service environment image or lockfile.

---

## 3) Quick Start

### A. Parse time and build time ranges
Use `sunpy.time.parse_time` and `sunpy.time.TimeRange` to normalize user input before any data query.

### B. Search and fetch data
Use `sunpy.net.Fido` with `sunpy.net.attrs` filters (time/instrument/provider, etc.) to perform discovery and downloads.

### C. Load maps
Use `sunpy.map.Map` (factory path via `MapFactory`) to ingest FITS/JP2 and other supported map formats into `GenericMap` objects.

### D. Load time series
Use `sunpy.timeseries.TimeSeries` (factory path via `TimeSeriesFactory`) to build `GenericTimeSeries` objects from supported sources/files.

### E. Solar geometry utilities
Use `sunpy.coordinates.sun` helpers such as:
- `angular_radius`
- `B0`, `L0`, `P`
- `carrington_rotation_number`

These are good stateless MCP (Model Context Protocol) tools for fast derived metadata.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `time.parse`
  - Parse/validate user time input into canonical format.

- `time.range.create`
  - Build a `TimeRange` from start/end or start/duration.

- `solar.ephemeris.compute`
  - Return solar geometry values (`B0`, `L0`, `P`, angular radius, Carrington rotation number).

- `data.search`
  - Query remote archives via Fido using attrs-based filters.

- `data.fetch`
  - Download query results to local cache/work directory.

- `map.load`
  - Load map file(s) into SunPy map objects.

- `map.inspect`
  - Return map metadata/WCS summary (instrument, wavelength, date, observer, scale, dimensions).

- `map.operations`
  - Common actions: submap, resample, rotate, reprojection hooks (if dependencies installed).

- `timeseries.load`
  - Load time-series source/file into `GenericTimeSeries`.

- `timeseries.inspect`
  - Return columns, units, time coverage, and basic stats.

---

## 5) Common Issues and Notes

- Optional dependency gaps:
  Some features silently require extra packages (e.g., `reproject`, `drms`, `zeep`, `asdf`). Validate availability at startup and expose capability flags.

- Remote service variability:
  Network/data-provider endpoints can be slow or unavailable. Implement retries, timeouts, and clear error mapping in service responses.

- Data volume/performance:
  Map and time-series workflows can be memory-heavy. Prefer bounded queries (shorter time ranges, targeted instruments) and streaming download patterns.

- Environment consistency:
  Pin SunPy + Astropy versions in production to avoid behavior drift across coordinate/time handling.

- Cache behavior:
  SunPy download/caching behavior should be documented for operators (cache location, cleanup strategy, retention policy).

- No built-in CLI entrypoints:
  This repository is library-first; your MCP (Model Context Protocol) service should define its own transport/server entrypoint.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/sunpy/sunpy
- SunPy documentation: https://docs.sunpy.org
- SunPy Net/Fido docs: https://docs.sunpy.org/en/stable/guide/acquiring_data/index.html
- SunPy Map docs: https://docs.sunpy.org/en/stable/guide/map/index.html
- SunPy TimeSeries docs: https://docs.sunpy.org/en/stable/guide/timeseries/index.html
- SunPy Coordinates docs: https://docs.sunpy.org/en/stable/guide/coordinates/index.html

If needed, I can also generate a production-ready version with explicit JSON tool schemas (request/response fields) for each MCP (Model Context Protocol) endpoint.