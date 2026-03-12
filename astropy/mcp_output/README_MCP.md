# Astropy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical Astropy capabilities through MCP (Model Context Protocol) tools for astronomy/scientific workflows.  
It is designed for agents and developer tooling that need reliable operations on:

- Units and quantities (`Quantity`, `Unit`)
- Coordinates (`SkyCoord`)
- Time systems (`Time`, `TimeDelta`)
- Tables and unified I/O (`Table`, `QTable`, I/O registry)
- FITS file operations (`open`, `getdata`, `getheader`, `writeto`, etc.)
- WCS transforms (`WCS`)
- Optional science helpers (cosmology, sigma clipping)

Best fit: building LLM/agent services that need structured astrophysical data access and transformations, not just raw file parsing.

---

## 2) Installation Method

### Requirements
- Python (modern supported version)
- Core deps: `numpy`, `pyerfa`, `packaging`, `PyYAML`
- Optional (feature-dependent): `scipy`, `matplotlib`, `pandas`, `pyarrow`, `h5py`, `fsspec`, `dask`, `beautifulsoup4`, `lxml`

### Install
- `pip install astropy`
- Optional extras as needed, e.g.:
  - `pip install scipy matplotlib pandas pyarrow h5py fsspec dask lxml beautifulsoup4`

If your MCP (Model Context Protocol) runtime has a dedicated environment, install these there.

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Start your MCP (Model Context Protocol) server runtime.
2. Register this Astropy service.
3. Call service tools from your client/agent.

### Example operations to expose in your service
- Parse a FITS file and return header summary.
- Convert pixel coordinates to sky coordinates via WCS.
- Transform celestial frames (e.g., ICRS → Galactic).
- Compute robust stats with sigma clipping.
- Read/write tabular astronomy formats through unified I/O.

### Minimal Python-side usage patterns
- FITS: call high-level helpers from `astropy.io.fits.convenience`
- Coordinates: use `SkyCoord` for parsing and frame transforms
- Time: use `Time`/`TimeDelta` for scale and format conversion
- Tables: use `Table.read` / `Table.write`
- WCS: create `WCS` and perform pixel/world conversions

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `fits_open`  
  Open FITS files and inspect HDUs.

- `fits_getdata`  
  Load FITS data array from target HDU.

- `fits_getheader`  
  Return FITS header cards/metadata.

- `fits_writeto` / `fits_append` / `fits_update`  
  Write or modify FITS files.

- `table_read` / `table_write`  
  Unified table I/O (ASCII, ECSV, FITS, VOTable, etc., depending on installed deps).

- `coords_transform`  
  Parse coordinates and transform between frames via `SkyCoord`.

- `time_convert`  
  Convert time scales/formats using `Time` and `TimeDelta`.

- `wcs_pixel_to_world` / `wcs_world_to_pixel`  
  Coordinate conversion with `WCS`.

- `units_convert`  
  Safe unit conversion and quantity-aware arithmetic.

- `stats_sigma_clip` / `stats_sigma_clipped_stats`  
  Robust outlier rejection/statistics.

- `cosmology_compute` (optional)  
  Cosmology model calculations (`LambdaCDM`, `FlatLambdaCDM`).

- `cli_bridge_fitscheck` / `cli_bridge_fitsdiff` / `cli_bridge_fitsheader` / `cli_bridge_fitsinfo` / `cli_bridge_showtable` / `cli_bridge_fits2bitmap`  
  Optional wrappers around Astropy CLI tools when import-path integration is not desired.

---

## 5) Common Issues and Notes

- Dependency gaps: many formats/features are optional; missing libs cause partial capability.
- Performance: large FITS cubes/tables can be memory-heavy; stream or subset when possible.
- WCS complexity: invalid/incomplete FITS headers can break transforms.
- Time/ephemeris data: some coordinate/time operations depend on external data availability and configuration.
- Intrusiveness risk is medium: Astropy is broad; expose only the endpoints you need.
- Prefer import-based integration first; keep CLI fallback for isolated or low-trust execution.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/astropy/astropy
- Astropy docs: https://docs.astropy.org/
- FITS I/O docs: https://docs.astropy.org/en/stable/io/fits/
- Coordinates docs: https://docs.astropy.org/en/stable/coordinates/
- WCS docs: https://docs.astropy.org/en/stable/wcs/
- Table docs: https://docs.astropy.org/en/stable/table/
- Time docs: https://docs.astropy.org/en/stable/time/
- Units docs: https://docs.astropy.org/en/stable/units/
- Stats docs: https://docs.astropy.org/en/stable/stats/