# ObsPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core ObsPy capabilities into MCP (Model Context Protocol)-friendly tools for seismic workflows.

Main capabilities:
- Read/write seismic waveform, station metadata, and event catalog formats
- Access remote FDSN services for waveforms/stations/events
- Perform common signal processing (filtering, envelope, preprocessing)
- Run travel-time and ray-path calculations (TauP)
- Support bulk data acquisition workflows (mass downloader)

Target users: developers building AI agents, automation, or data pipelines for seismology/geophysics.

---

## 2) Installation Method

Recommended environment: Python 3.10+ (3.9+ may work depending on your stack).

Core dependencies:
- numpy
- scipy
- matplotlib
- lxml
- sqlalchemy
- requests

Optional (feature-specific):
- cartopy
- pyproj
- geographiclib
- numba
- pyshp (shapefile)

Install:
- pip install obspy
- (optional extras) pip install cartopy pyproj geographiclib numba pyshp

If system wheels are unavailable, ensure build toolchain and scientific libs are available.

---

## 3) Quick Start

Typical service usage should expose ObsPy-backed MCP (Model Context Protocol) tools such as:

- Read waveform data into `Stream` / `Trace`
- Apply processing (`bandpass`, `lowpass`, `highpass`, `envelope`)
- Query remote FDSN data via `Client`
- Compute travel times with `TauPyModel`
- Export MiniSEED / StationXML / QuakeML

Minimal developer flow:
1. Initialize your MCP (Model Context Protocol) server.
2. Register ObsPy-backed services/endpoints (see section 4).
3. Invoke tool calls from client/agent with input params (file path, network/station/channel, time window, filter settings, phase list, etc.).
4. Return compact structured outputs (summary + artifacts/paths).

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `waveform.read`
  - Read local seismic files into stream objects (multi-format via ObsPy I/O).
- `waveform.write_mseed`
  - Write waveform streams to MiniSEED.
- `waveform.filter`
  - Apply `bandpass`, `bandstop`, `lowpass`, `highpass`, `envelope`.
- `waveform.slice_merge`
  - Slice by time, merge traces, basic preprocessing.
- `fdsn.get_waveforms`
  - Fetch waveform data from FDSN servers.
- `fdsn.get_stations`
  - Fetch station/instrument metadata (StationXML-compatible).
- `fdsn.get_events`
  - Query event catalogs from FDSN event services.
- `fdsn.mass_download`
  - Bulk waveform + metadata download orchestration.
- `event.read_quakeml` / `event.write_quakeml`
  - Read/write QuakeML catalogs.
- `inventory.read_stationxml` / `inventory.write_stationxml`
  - Read/write StationXML inventory/response metadata.
- `taup.travel_times`
  - Compute phase travel times using `TauPyModel`.
- `taup.ray_paths`
  - Compute ray-path or pierce-point style outputs.
- `system.file_summary`
  - Quick metadata summary for ObsPy-readable files (similar to `obspy-print` CLI behavior).

Related ObsPy CLI commands (optional integration):
- `obspy-print`
- `obspy-flinn-engdahl`
- `obspy-reftek-rescue`
- `obspy-scan`
- `obspy-plot`
- `obspy-mopad`
- `obspy-runtests`

---

## 5) Common Issues and Notes

- Large files: MiniSEED and archive scans can be memory/IO heavy; stream in chunks when possible.
- Remote services: FDSN endpoints may rate-limit or vary in supported parameters; add retries/timeouts.
- Optional geospatial plotting: requires extra dependencies (`cartopy`, `pyproj`, etc.).
- Native/scientific stack: `numpy/scipy/lxml` installation may require platform-specific wheels/toolchains.
- Reproducibility: pin ObsPy + numpy/scipy versions in production.
- Performance: use bulk download APIs for many stations/time windows instead of many tiny requests.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/obspy/obspy
- ObsPy documentation: https://docs.obspy.org/
- FDSN web services spec: https://www.fdsn.org/webservices/
- QuakeML format: https://quake.ethz.ch/quakeml/
- StationXML format: https://www.fdsn.org/xml/station/