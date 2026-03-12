# Pyrocko MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **Pyrocko** capabilities for seismology workflows, so LLM agents and developer tools can query waveform data, metadata, travel times, event catalogs, and Green’s-function modeling from a single interface.

Primary functions:
- Waveform I/O and processing (`trace`, `pile`, `io`)
- Travel-time and ray calculations (`cake`)
- Green’s-function forward modeling (`gf.seismosizer`, `gf.store`, `fomosto`)
- Event and station metadata handling (`model`, `io.stationxml`, `io.quakeml`)
- Remote data access (FDSN and catalog clients)
- Indexed data workflows with `squirrel`

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Core deps: `numpy`, `scipy`, `PyYAML`, `requests`
- Optional deps by feature:
  - Plotting: `matplotlib`
  - GUI: `PyQt5` or `PySide2`
  - 3D visualization: `vtk`
  - XML/advanced I/O: `lxml`
  - HDF5: `h5py`
  - Mapping/geodesy: `pyproj`, `cartopy`
  - Interop: `obspy`

### Install
- From PyPI:
  - `pip install pyrocko`
- From source:
  - `git clone https://github.com/pyrocko/pyrocko.git`
  - `cd pyrocko`
  - `pip install -e .`

If building an MCP (Model Context Protocol) server wrapper, install your MCP runtime (e.g., FastMCP/SDK) in the same environment.

---

## 3) Quick Start

Typical MCP (Model Context Protocol) service flow:
1. Start MCP server process.
2. Register Pyrocko-backed tools.
3. Call tools from MCP client (IDE/agent/runtime).

Example operations to expose:
- Load waveform files (`io.load`, `io.iload`)
- Process traces (`Trace.rotate`, `Trace.project`, correlation/deconvolution helpers)
- Query travel times (`cake.load_model`, phase arrivals)
- Fetch remote data (`client.fdsn.station/dataselect/event`)
- Run forward modeling (`gf.LocalEngine`, GF store access)
- Manage indexed datasets (`squirrel.Squirrel.add/update/get_waveforms`)

Recommended first tests:
- Validate `cake` arrival queries for a known phase set.
- Load a miniSEED sample and run a simple trace transform.
- Run a small `squirrel` scan + waveform query.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoints for this service:

- `waveform.load`
  - Load traces from local files/streams (miniSEED, SAC, etc.).
- `waveform.save`
  - Save traces to target format.
- `waveform.process`
  - Basic operations: rotate/project/correlate/deconvolve/filter windowing.
- `pile.create`
  - Build/query multi-file waveform collections.
- `travel_time.compute`
  - Compute arrivals/rays from Earth models via `cake`.
- `event.load` / `event.dump`
  - Read/write event catalogs (QuakeML and Pyrocko models).
- `station.query`
  - Access station metadata from local/XML/FDSN sources.
- `fdsn.station`, `fdsn.dataselect`, `fdsn.event`
  - Remote service requests through Pyrocko FDSN client.
- `gf.store.open`
  - Open/create GF stores.
- `gf.forward`
  - Forward syntheses with local/remote engines.
- `squirrel.add`, `squirrel.update`, `squirrel.get_waveforms`
  - Indexed data ingestion, refresh, and retrieval.
- `cli.exec` (optional, guarded)
  - Controlled access to `cake`, `fomosto`, `jackseis`, `squirrel` CLI operations.

---

## 5) Common Issues and Notes

- **Large dependency surface**: install only optional packages you need.
- **GUI failures on servers**: omit Qt/VTK deps in headless environments.
- **GF computations can be expensive**: cache stores and constrain query windows.
- **Remote FDSN instability**: set retries/timeouts and handle service-specific limits.
- **Format edge cases**: station/event parsing may require `lxml`.
- **Performance**:
  - Prefer `squirrel` indexing for repeated queries.
  - Avoid loading full archives when `iload`/streamed access is sufficient.
- **Security**:
  - If exposing `cli.exec`, whitelist commands and sanitize arguments.
  - Restrict filesystem/network scope for MCP runtime.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pyrocko/pyrocko
- Main docs entry: `README.md` in repository root
- Developer guidance: `CONTRIBUTING.md`
- Examples: `examples/`
- Key CLIs:
  - `pyrocko`
  - `cake`
  - `fomosto`
  - `jackseis`
  - `squirrel`

For production MCP (Model Context Protocol) deployment, document your final tool schemas (inputs/outputs/errors) and pin Pyrocko + dependency versions for reproducibility.