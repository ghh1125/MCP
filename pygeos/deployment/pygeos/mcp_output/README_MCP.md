# PyGEOS MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides high-performance, vectorized geometry operations powered by **PyGEOS** (GEOS-backed).  
It is designed for developer workflows that need fast spatial processing over single geometries or NumPy arrays.

Main capabilities:
- Geometry creation (Point, LineString, Polygon, Multi*, GeometryCollection)
- Geometry I/O (WKT/WKB read/write)
- Spatial predicates (intersects, contains, within, etc.)
- Measurements (area, length, distance, bounds)
- Set operations (union, intersection, difference)
- Constructive operations (buffer, centroid, convex hull, simplify, make_valid)
- Spatial indexing with `STRtree`

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ (recommended)
- `numpy`
- `packaging`
- GEOS native library available at runtime
- Build toolchain for source install (if wheel is unavailable)

### Install with pip
- Install package:
  `pip install pygeos`
- For development/testing:
  `pip install pytest asv sphinx`

If installation fails, ensure GEOS is installed and discoverable by your system linker.

---

## 3) Quick Start

### Basic usage flow
1. Create geometries from coordinates or WKT/WKB
2. Run predicates/measurements/operations
3. Serialize results or query with STRtree

### Example calls
- Create points: `pygeos.points([[0, 0], [1, 1]])`
- Parse WKT: `pygeos.from_wkt(["POINT (0 0)", "POINT (1 1)"])`
- Predicate: `pygeos.intersects(a, b)`
- Measurement: `pygeos.area(polygons)`
- Constructive: `pygeos.buffer(geoms, 10.0)`
- Set op: `pygeos.union(a, b)`
- I/O: `pygeos.to_wkb(geoms)` / `pygeos.to_wkt(geoms)`
- Spatial index: build `STRtree(geoms)` then query candidates by geometry/envelope

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints mapped to PyGEOS modules:

- `creation.points|linestrings|polygons|...`
  - Build geometries from arrays/parts; includes `from_wkt`, `from_wkb`, `box`.
- `io.to_wkt|to_wkb|from_wkt|from_wkb`
  - Convert geometries to/from WKT/WKB.
- `predicates.contains|within|intersects|touches|crosses|overlaps|...`
  - Boolean spatial relationships and validity checks.
- `measurement.area|length|distance|bounds|total_bounds|...`
  - Compute numeric geometry properties and extents.
- `set_operations.union|intersection|difference|symmetric_difference|unary_union`
  - Topological overlays and merges.
- `constructive.buffer|centroid|convex_hull|concave_hull|simplify|make_valid|...`
  - Transform geometries into derived outputs.
- `linear.line_interpolate_point|line_locate_point|line_merge|shared_paths`
  - Linear referencing and line operations.
- `coordinates.get_x|get_y|get_z|get_coordinates|set_coordinates|transform`
  - Coordinate extraction, mutation, and transformation.
- `geometry.get_type_id|get_num_coordinates|get_geometry|get_exterior_ring|set_precision|...`
  - Geometry metadata and component access.
- `strtree.STRtree`
  - Spatial index endpoint for fast candidate lookup.

---

## 5) Common Issues and Notes

- **GEOS runtime issues**: Most failures come from missing/incompatible GEOS shared libraries.
- **Source build issues**: Require compiler toolchain and Python headers.
- **Array semantics**: PyGEOS is vectorized; ensure input shapes/dtypes are consistent.
- **Performance**: Use batch/array operations instead of Python loops for best speed.
- **Validation**: Use `is_valid` and `make_valid` when ingesting external geometry data.
- **Project status note**: PyGEOS functionality is largely integrated into Shapely 2.x in modern stacks; verify your target ecosystem.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pygeos/pygeos
- API source modules:
  - `pygeos/creation.py`
  - `pygeos/io.py`
  - `pygeos/predicates.py`
  - `pygeos/measurement.py`
  - `pygeos/set_operations.py`
  - `pygeos/constructive.py`
  - `pygeos/linear.py`
  - `pygeos/coordinates.py`
  - `pygeos/geometry.py`
  - `pygeos/strtree.py`
- Tests (behavior reference): `pygeos/tests/`