# Rasterio MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key Rasterio capabilities as MCP (Model Context Protocol) tools for geospatial raster workflows.  
It is designed for developers who need reliable raster automation in AI/tooling pipelines.

Main functions include:

- Open/read/write raster datasets
- Inspect raster metadata (size, CRS, transform, bounds, bands)
- Windowed/subset reads for performance
- Reprojection and coordinate transformation
- Raster/vector conversion (rasterize, shapes extraction, masking)
- CLI fallback via `rio` commands when direct imports are constrained

Repository analyzed: https://github.com/rasterio/rasterio

---

## 2) Installation Method

### System requirements

- Python 3.9+ (recommended)
- GDAL native runtime/library installed and discoverable by Rasterio
- Build tools if installing from source (platform-dependent)

### Python dependencies (core)

- rasterio
- numpy
- affine
- attrs
- click
- cligj
- snuggs
- click-plugins
- setuptools

### Optional dependencies

- matplotlib (plotting paths)
- boto3/botocore (cloud/session integrations)
- pytest (testing)

### Typical install commands

- `pip install rasterio`
- If your MCP (Model Context Protocol) host requires local service packaging, install your service package after Rasterio:
  - `pip install -e .`

Note: GDAL compatibility is the most important install constraint. Prefer prebuilt wheels where possible.

---

## 3) Quick Start

### Minimal usage flow

1. Initialize the MCP (Model Context Protocol) service in your host.
2. Call an inspection tool (for example, raster info) on a dataset path/URI.
3. Run processing tools such as warp, clip, merge, rasterize, or shapes extraction.
4. Persist outputs to a target file or return structured metadata to the caller.

### Typical Python-side operations this service maps to

- `rasterio.open(...)`
- `rasterio.features.shapes(...)`
- `rasterio.features.rasterize(...)`
- `rasterio.warp.reproject(...)`
- `rasterio.warp.transform_bounds(...)`
- `rasterio.windows.from_bounds(...)`
- `rasterio.transform.xy(...)` / `rowcol(...)`

### CLI fallback pattern

If import-based execution is restricted, the service can route calls to `rio` subcommands (for example `rio info`, `rio warp`, `rio merge`).

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `raster.open_info`
  - Returns core metadata (driver, width, height, CRS, transform, bounds, band count, dtype, nodata).
- `raster.read_window`
  - Reads a spatial/pixel window from a raster for efficient partial access.
- `raster.reproject`
  - Reprojects raster data to a target CRS/resolution/resampling strategy.
- `raster.transform_coords`
  - Converts coordinates/bounds between CRSs.
- `raster.clip`
  - Clips raster by bounds or geometry mask.
- `raster.merge`
  - Merges multiple raster inputs into one output dataset.
- `raster.rasterize`
  - Burns vector geometries into raster output.
- `raster.shapes`
  - Extracts vector polygons from raster regions/values.
- `raster.sample`
  - Samples raster values at point coordinates.
- `raster.env_info`
  - Reports runtime environment/version details (useful for diagnostics).

CLI-backed equivalents (fallback):

- `rio info`
- `rio warp`
- `rio merge`
- `rio clip`
- `rio rasterize`
- `rio shapes`
- `rio bounds`

---

## 5) Common Issues and Notes

- GDAL mismatch errors:
  - Most failures are due to incompatible GDAL/Rasterio binaries. Align versions and prefer wheel-based installs.
- CRS pitfalls:
  - Always verify source and destination CRS before warp/transform operations.
- Memory/performance:
  - Use windowed reads/writes for large rasters.
  - Avoid loading full datasets when only subsets are needed.
- Cloud/remote data:
  - Access patterns depend on GDAL virtual filesystem support and environment configuration.
- Threading/process behavior:
  - Dataset handles are sensitive to process/thread boundaries; open datasets within worker context when parallelizing.
- Determinism:
  - Resampling method and nodata handling can change output values; set them explicitly in tool parameters.

---

## 6) Reference Links or Documentation

- Rasterio repository: https://github.com/rasterio/rasterio
- Rasterio documentation: https://rasterio.readthedocs.io/
- GDAL documentation: https://gdal.org/
- Rasterio CLI (`rio`) source entry: `rasterio/rio/main.py`
- Key modules:
  - `rasterio/io.py`
  - `rasterio/features.py`
  - `rasterio/warp.py`
  - `rasterio/windows.py`
  - `rasterio/transform.py`

If you want, I can also provide a ready-to-use MCP (Model Context Protocol) service manifest/template (tool schemas + input/output fields) aligned to these endpoints.