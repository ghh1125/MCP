# Rasterio MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core Rasterio capabilities as MCP (Model Context Protocol) service operations so LLM agents and developer tools can read, inspect, transform, and export raster geospatial data safely and consistently.

Main capabilities:
- Open/read raster datasets (local or supported virtual paths)
- Inspect metadata (CRS, bounds, transform, dtype, nodata, bands)
- Windowed reads and sampling
- Reprojection/warping
- Masking, clipping, merge/stack workflows
- Rasterize/shapes-style feature conversion (if enabled by service implementation)

This project is based on the Rasterio codebase (`rasterio/rasterio`) and GDAL runtime behavior.

---

## 2) Installation Method

### Prerequisites
- Python 3.x
- GDAL runtime and development libraries compatible with your Rasterio version
- Recommended system build tools for native dependencies

### Python dependencies (typical)
- rasterio
- numpy
- click
- affine
- attrs
- snuggs
- click-plugins

Optional:
- matplotlib (plot/preview flows)
- pytest (test/dev)
- cloud/session extras depending on your environment (for remote storage access)

### Install
- `pip install rasterio`
- If your MCP (Model Context Protocol) host requires a service package, install that package as well (for example: `pip install <your-mcp-service-package>`).

### Verify
- Confirm Rasterio loads and GDAL is visible in runtime.
- Run a basic dataset open/read call from your MCP (Model Context Protocol) client.

---

## 3) Quick Start

### Typical service flow
1. Open dataset
2. Read metadata/info
3. Read data (full or windowed)
4. Apply transform (warp/mask/merge)
5. Write/export result

### Example MCP (Model Context Protocol) usage pattern
- Call `raster.open` with dataset URI/path
- Call `raster.info` to inspect CRS, bounds, size, dtype
- Call `raster.read` with optional band indexes and window
- Optionally call `raster.warp` or `raster.mask`
- Call `raster.write` to persist output

Use small windows first for large rasters to reduce memory pressure and latency.

---

## 4) Available Tools and Endpoints List

Note: exact endpoint names depend on your MCP (Model Context Protocol) host/service adapter. Recommended practical mapping:

- `raster.open`
  - Open or validate a raster source handle.
- `raster.info`
  - Return metadata: dimensions, count, CRS, transform, bounds, nodata, dtype.
- `raster.read`
  - Read pixel arrays by band and optional window/bounds.
- `raster.sample`
  - Sample pixel values at coordinate points.
- `raster.mask`
  - Apply geometry mask/crop.
- `raster.warp`
  - Reproject/resample to target CRS/resolution.
- `raster.merge`
  - Merge multiple rasters into one output.
- `raster.stack`
  - Stack multiple inputs into multiband output.
- `raster.write`
  - Write array + profile to output dataset.
- `raster.env`
  - Manage GDAL/Rasterio environment options (cache, drivers, credentials).
- `raster.shapes` / `raster.rasterize` (optional)
  - Convert raster-to-vector shapes or vector-to-raster burn.

If your implementation exposes fewer operations, keep the same semantics and return structured errors for unsupported calls.

---

## 5) Common Issues and Notes

- GDAL mismatch is the #1 issue  
  Ensure Rasterio and GDAL binary compatibility.
- CRS and axis-order confusion  
  Always verify CRS and coordinate order before sampling/warp.
- Large raster memory usage  
  Prefer windowed reads, overviews, and tiling-aware workflows.
- Remote/Cloud access  
  Requires proper session/environment configuration (credentials, VSI options).
- Performance  
  Reprojection and merge are CPU/I/O intensive; tune block sizes and cache settings.
- Error handling  
  Return clear MCP (Model Context Protocol) service errors for invalid paths, unsupported drivers, and CRS transform failures.

Risk profile from analysis:
- Import feasibility: medium-low in constrained environments
- Intrusiveness risk: medium
- Overall complexity: high (geospatial + native runtime stack)

---

## 6) Reference Links and Documentation

- Rasterio repository: https://github.com/rasterio/rasterio
- Rasterio docs: https://rasterio.readthedocs.io/
- GDAL docs: https://gdal.org/
- Rasterio CLI modules (reference for operation design): `rasterio/rio/*`
- MCP (Model Context Protocol) specification: use your platform’s official MCP docs for transport, schema, and tool registration.