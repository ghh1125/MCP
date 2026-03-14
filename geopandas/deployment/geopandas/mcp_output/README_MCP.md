# GeoPandas MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core GeoPandas geospatial capabilities through an MCP (Model Context Protocol) interface for LLM/tooling workflows.  
It is designed for practical GIS data handling in pipelines: reading/writing spatial files, CRS transformations, geometry operations, spatial joins, overlays, clipping, and PostGIS integration.

Core capabilities:
- GeoDataFrame / GeoSeries creation and transformation
- File IO (Shapefile/GeoJSON/GPKG via backend drivers)
- Arrow IO (Parquet/Feather)
- Database IO (PostGIS)
- Spatial analysis tools (`sjoin`, `sjoin_nearest`, `overlay`, `clip`)
- Runtime diagnostics (`show_versions`)

---

## 2) Installation Method

### Requirements
- Python `>=3.11`
- Required: `numpy`, `pandas`, `shapely`, `pyproj`, `packaging`
- Optional (feature-dependent): `pyogrio` or `fiona`, `pyarrow`, `sqlalchemy`, `geoalchemy2`, `psycopg/psycopg2`, `rtree`, `scipy`, `matplotlib`, `folium`, `mapclassify`, `geopy`

### Typical install
- Base:
  - `pip install geopandas`
- Recommended IO/performance extras:
  - `pip install geopandas pyogrio pyarrow sqlalchemy psycopg[binary]`

---

## 3) Quick Start

Create and transform geospatial data:
- Build a `GeoDataFrame` from coordinates/geometries
- Set CRS and reproject with `to_crs`
- Save outputs via `to_file`, `to_parquet`, or `to_postgis`

Read and analyze:
- `read_file(...)` for common GIS files
- `read_parquet(...)` / `read_feather(...)` for columnar formats
- Spatial join with `sjoin(...)` or nearest with `sjoin_nearest(...)`
- Topological operations with `overlay(...)`
- Clip features with `clip(...)`

Health/debug:
- `show_versions()` for dependency/runtime diagnostics

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `read_file(path, layer=None, ...)`  
  Read geospatial files into `GeoDataFrame`.

- `to_file(gdf, path, driver=None, ...)`  
  Write `GeoDataFrame` to geospatial file formats.

- `read_parquet(path, ...)` / `to_parquet(gdf, path, ...)`  
  Columnar geospatial storage using GeoParquet metadata.

- `read_feather(path, ...)` / `to_feather(gdf, path, ...)`  
  Fast Arrow Feather round-trip for geospatial frames.

- `read_postgis(sql, con, ...)` / `to_postgis(gdf, name, con, ...)`  
  PostGIS import/export for database workflows.

- `set_crs(gdf_or_gs, crs, ...)` / `to_crs(gdf_or_gs, crs, ...)`  
  Define or transform coordinate reference systems.

- `sjoin(left, right, how='inner', predicate='intersects', ...)`  
  Spatial join by geometric predicate.

- `sjoin_nearest(left, right, ...)`  
  Nearest-neighbor spatial matching.

- `overlay(df1, df2, how='intersection'|'union'|'difference'|...)`  
  Topological overlay operations.

- `clip(gdf, mask, ...)`  
  Clip geometries to mask/bounds.

- `show_versions()`  
  Runtime environment and dependency report.

---

## 5) Common Issues and Notes

- CRS mismatches are the #1 error source. Always align CRS before joins/overlay/clip.
- IO backend matters:
  - Prefer `pyogrio` for speed.
  - Use `fiona` as fallback if required by environment.
- PostGIS usage requires proper DB drivers (`sqlalchemy` + `psycopg/psycopg2`, optionally `geoalchemy2`).
- Spatial indexing improves join/query performance (`rtree` or compatible backend).
- Large datasets:
  - Prefer Parquet/Feather over text formats for speed and size.
  - Avoid unnecessary geometry conversions.
- If behavior is unexpected, run `show_versions()` and include output in bug reports.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/geopandas/geopandas
- GeoPandas docs (start from repo README/docs): `README.md`, `doc/source/getting_started.md`
- Changelog: `CHANGELOG.md`
- Contribution guide: `CONTRIBUTING.md`
- Code of conduct: `CODE_OF_CONDUCT.md`