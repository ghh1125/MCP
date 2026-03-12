# GeoPandas MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core GeoPandas capabilities through MCP (Model Context Protocol): loading geospatial data, transforming and analyzing geometries, and exporting results.

Main capabilities:
- Read/write vector files (`read_file`, `to_file`)
- Arrow/GeoParquet I/O (`read_parquet`, `to_parquet`, `read_feather`, `to_feather`)
- PostGIS I/O (`read_postgis`, `to_postgis`)
- Spatial operations (`sjoin`, `sjoin_nearest`, `overlay`, `clip`)
- Core data structures (`GeoDataFrame`, `GeoSeries`)
- Environment diagnostics (`show_versions`)

---

## 2) Installation Method

### Requirements
- Python 3.11+ (recommended)
- Required libraries:
  - `numpy`
  - `pandas`
  - `shapely`
  - `pyproj`

### Optional dependencies (based on features)
- File I/O backends: `pyogrio` or `fiona`
- Parquet/Feather: `pyarrow`
- PostGIS: `sqlalchemy`, `geoalchemy2`, `psycopg` (or `psycopg2`)
- Spatial indexing/performance: `rtree`
- Plotting/explore: `matplotlib`, `mapclassify`, `folium`

### Install
- `pip install geopandas`
- Recommended extras (as needed): install optional packages above for full functionality.

---

## 3) Quick Start

### Basic workflow
- Load geospatial data into a `GeoDataFrame`
- Run a spatial operation
- Save output

Example flow:
1. Read layer with `read_file(...)`
2. Join with another layer using `sjoin(...)`
3. Clip result using `clip(...)`
4. Export with `to_parquet(...)` or `to_file(...)`

### Typical function calls
- `geopandas.read_file(path)`
- `geopandas.read_parquet(path)`
- `geopandas.read_postgis(sql, con)`
- `geopandas.sjoin(left, right, predicate="intersects")`
- `geopandas.overlay(df1, df2, how="intersection")`
- `geopandas.clip(gdf, mask)`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `read_file`
  - Read vector datasets (Shapefile, GeoPackage, etc.).
- `to_file`
  - Write vector datasets to disk.
- `list_layers`
  - List layers in multi-layer sources.
- `read_parquet` / `to_parquet`
  - Read/write GeoParquet.
- `read_feather` / `to_feather`
  - Read/write GeoArrow Feather.
- `read_postgis` / `to_postgis`
  - Import/export geospatial tables in PostGIS.
- `sjoin`
  - Spatial join by predicate (`intersects`, `within`, etc.).
- `sjoin_nearest`
  - Nearest-neighbor spatial join.
- `overlay`
  - Set operations (`intersection`, `union`, `difference`, etc.).
- `clip`
  - Clip geometries to mask/bounds.
- `show_versions`
  - Print dependency and environment versions for debugging.

Core data objects exposed by the service:
- `GeoDataFrame`
- `GeoSeries`
- `SpatialIndex` (internal acceleration layer used by joins/predicates)

---

## 5) Common Issues and Notes

- CRS mismatch is the #1 source of incorrect results.
  - Ensure layers use compatible CRS before spatial operations.
- Missing optional dependencies can disable endpoints.
  - Example: no `pyarrow` => no parquet/feather endpoints.
- File backend differences (`pyogrio` vs `fiona`) may affect behavior/performance.
- Large joins/overlays can be memory-intensive.
  - Prefer filtering, indexing, and chunked workflows when possible.
- PostGIS connectivity requires correct DB driver and SQLAlchemy setup.
- Use `show_versions` when reporting bugs to capture exact environment details.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/geopandas/geopandas
- Official docs: https://geopandas.org/
- API reference: https://geopandas.org/en/stable/docs/reference.html
- Changelog: https://github.com/geopandas/geopandas/blob/main/CHANGELOG.md
- Contributing guide: https://github.com/geopandas/geopandas/blob/main/CONTRIBUTING.md