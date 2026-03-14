# GeoPandas MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core GeoPandas capabilities through an MCP (Model Context Protocol) interface for geospatial data workflows.  
It is designed for developer use cases such as:

- Reading/writing geospatial files and tabular formats
- Running spatial joins and overlays
- Clipping geometries
- Working with CRS transformations
- PostGIS import/export
- Environment diagnostics

Main wrapped APIs come from `geopandas` top-level functions and `geopandas.io` / `geopandas.tools`.

---

## 2) Installation Method

### Requirements

- Python 3.11+ (recommended)
- Required libs: `numpy`, `pandas`, `shapely`, `pyproj`
- Common optional libs:
  - File IO backends: `pyogrio` (recommended) or `fiona`
  - Arrow formats: `pyarrow`
  - Database: `sqlalchemy`, `geoalchemy2`
  - Spatial index/perf: `rtree` (or Shapely STRtree path)
  - Visualization: `matplotlib`, `folium`

### Install (typical)

pip install geopandas pyogrio pyarrow sqlalchemy geoalchemy2 rtree

If you need minimal install:

pip install geopandas

---

## 3) Quick Start

### Basic usage flow

1. `read_file` to load data  
2. Run operation (`sjoin`, `overlay`, `clip`, CRS conversion, etc.)  
3. Persist output (`to_file`, `to_parquet`, `to_postgis`)

### Example calls (service-level intent)

- Load vector data: `read_file(path_or_url)`
- Spatial join: `sjoin(left_gdf, right_gdf, how="inner", predicate="intersects")`
- Nearest join: `sjoin_nearest(left_gdf, right_gdf)`
- Overlay: `overlay(df1, df2, how="intersection")`
- Clip: `clip(gdf, mask)`
- Save: `to_parquet(path)`, `to_file(path, driver=...)`, `to_postgis(table, engine)`

---

## 4) Available Tools and Endpoints List

- `read_file`  
  Read geospatial files via Fiona/pyogrio backend.

- `list_layers`  
  Inspect available layers in multi-layer geospatial sources.

- `infer_schema`  
  Infer file schema for writing/export checks.

- `read_parquet` / `read_feather`  
  Load GeoParquet/Feather datasets.

- `to_parquet` / `to_feather`  
  Write Arrow-based geospatial formats.

- `read_postgis` / `to_postgis`  
  Read/write GeoDataFrames from/to PostGIS.

- `sjoin`  
  Spatial join using binary spatial predicates.

- `sjoin_nearest`  
  Nearest-neighbor spatial join.

- `overlay`  
  Set operations (intersection/union/difference/symmetric_difference).

- `clip`  
  Clip geometries to a mask/boundary.

- `show_versions`  
  Runtime dependency/version diagnostics for support and debugging.

---

## 5) Common Issues and Notes

- IO backend mismatch: install `pyogrio` or `fiona` explicitly if file read/write fails.
- CRS pitfalls: always verify CRS (`set_crs`, `to_crs`) before spatial operations.
- PostGIS errors: ensure correct SQLAlchemy engine URL, PostGIS extension enabled, and geometry column permissions.
- Performance:
  - Prefer Parquet/Feather for large datasets.
  - Use spatial indexes for joins.
  - Avoid unnecessary geometry conversions.
- Optional dependency behavior: some endpoints are available only when related packages are installed.
- Environment checks: run `show_versions` for reproducible bug reports.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/geopandas/geopandas
- Main documentation: https://geopandas.org/
- API reference: https://geopandas.org/en/stable/docs/reference.html
- Installation guide: https://geopandas.org/en/stable/getting_started/install.html
- Changelog: https://github.com/geopandas/geopandas/blob/main/CHANGELOG.md