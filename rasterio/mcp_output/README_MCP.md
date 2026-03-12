# Rasterio MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides geospatial raster capabilities powered by Rasterio (GDAL-based).  
It is designed for developer workflows that need reliable raster read/write, reprojection, masking, rasterization, and metadata inspection.

Main functions:
- Open/read/write raster datasets
- Windowed (chunked) access for large files
- Reproject and transform coordinates
- Mask, polygonize, rasterize, and merge rasters
- Inspect dataset metadata and environment configuration

---

## 2) Installation Method

### Requirements
- Python 3.9+ (recommended)
- Native GDAL runtime/library available on the system
- Python dependencies:
  - numpy
  - affine
  - attrs
  - click
  - cligj
  - snuggs
  - click-services
  - setuptools
- Optional:
  - matplotlib (plotting)
  - pytest (tests)

### Install
- Install Rasterio:
  - pip install rasterio
- Verify:
  - python -c "import rasterio; print(rasterio.__version__)"
  - rio --help

Note: GDAL compatibility is critical. If import fails, first verify GDAL shared libraries are correctly installed and discoverable.

---

## 3) Quick Start

### Basic open/read
import rasterio

with rasterio.open("input.tif") as src:
    arr = src.read(1)
    print(src.crs, src.transform, src.bounds)

### Reproject
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Typical flow: compute transform/shape, then reproject band data
# using source/destination CRS and chosen resampling.

### Mask by geometry
from rasterio.mask import mask

# Use GeoJSON-like geometries to crop/mask a dataset.

### Merge rasters
from rasterio.merge import merge

# Merge multiple sources into a mosaic array + transform.

---

## 4) Available Tools and Endpoints List

This service can expose Rasterio operations as MCP (Model Context Protocol) endpoints/tools such as:

- `open_dataset`  
  Open raster source and return core metadata (size, CRS, bounds, dtype, band count).

- `read_band`  
  Read one/more bands, optionally with windowed access for large rasters.

- `read_window`  
  Read by pixel window or bounds-derived window to reduce memory use.

- `get_info`  
  Return profile, tags, nodata, transform, overviews, and driver info.

- `reproject_raster`  
  Reproject to target CRS/resolution using Rasterio warp primitives.

- `transform_coords`  
  Convert coordinates or bounds between CRS systems.

- `mask_raster`  
  Apply geometry masks and optional crop.

- `rasterize_features`  
  Burn vector geometries into a raster grid.

- `extract_shapes`  
  Polygonize raster regions into vector-like geometries.

- `merge_rasters`  
  Mosaic multiple rasters into one output.

- `sample_points`  
  Sample raster values at coordinate pairs.

- `environment_info`  
  Inspect GDAL/PROJ runtime options and session-scoped environment.

CLI equivalents are available via `rio` subcommands (`rio info`, `rio warp`, `rio merge`, `rio mask`, etc.) if your MCP (Model Context Protocol) service uses command execution fallback.

---

## 5) Common Issues and Notes

- GDAL runtime mismatch  
  Most common failure source. Ensure Rasterio wheel/system GDAL versions are compatible.

- CRS/axis-order confusion  
  Always validate CRS definitions and coordinate ordering before warp/transform operations.

- Large raster performance  
  Prefer windowed reads/writes (`windows`) and avoid loading full arrays when unnecessary.

- Memory pressure  
  Reprojection/merge can be expensive; tune chunk sizes and intermediate array handling.

- Environment scoping  
  Use `rasterio.Env` for deterministic GDAL/PROJ config in server processes.

- Cloud/remote access  
  Some workflows require proper GDAL virtual filesystem or credential/session configuration.

- Native dependency deployment  
  Containerized environments should pin Rasterio + GDAL combinations to avoid runtime drift.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/rasterio/rasterio
- Official docs: https://rasterio.readthedocs.io/
- CLI help: `rio --help`
- Key modules:
  - `rasterio.io` (dataset IO, MemoryFile)
  - `rasterio.env` (runtime env)
  - `rasterio.features` (shapes/rasterize)
  - `rasterio.warp` (reprojection)
  - `rasterio.windows` (windowed access)
  - `rasterio.transform` (pixel/world transforms)

If you are wrapping these as MCP (Model Context Protocol) services, start with read/info/warp/mask endpoints first, then add merge/rasterize/shapes based on workload needs.