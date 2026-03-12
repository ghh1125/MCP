# OSMnx MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps key OSMnx capabilities for working with OpenStreetMap data in Python workflows.  
It is designed for developers who need to:

- Download street networks as NetworkX graphs
- Fetch map features (buildings, amenities, land use, etc.) as GeoDataFrames
- Geocode places/addresses
- Run routing and nearest-node/edge queries
- Project, simplify, analyze, visualize, and persist graph data

Core value: quickly turn OSM data into analysis-ready network/geospatial objects.

---

## 2) Installation Method

### Requirements
- Python 3.10+ (recommended modern environment)
- System geospatial stack compatible with:
  - `geopandas`
  - `shapely`
  - `pyproj`
  - `networkx`
  - `pandas`
  - `numpy`
  - `requests`

Optional but useful:
- `matplotlib` (plotting)
- `scipy`, `scikit-learn` (advanced spatial/routing helpers)
- `rtree` (spatial indexing)
- `rasterio`, `rio-vrt` (elevation workflows)

### Install with pip
pip install osmnx

### Verify install
python -c "import osmnx as ox; print(ox.__version__)"

---

## 3) Quick Start

### Basic network download
import osmnx as ox

G = ox.graph_from_place("Piedmont, California, USA", network_type="drive")

### Geocode and feature extraction
import osmnx as ox

gdf_place = ox.geocode_to_gdf("Berkeley, California, USA")
tags = {"amenity": True}
gdf_features = ox.features_from_place("Berkeley, California, USA", tags=tags)

### Routing example
import osmnx as ox

G = ox.graph_from_place("Manhattan, New York, USA", network_type="drive")
orig = ox.distance.nearest_nodes(G, X=-73.9855, Y=40.7580)
dest = ox.distance.nearest_nodes(G, X=-73.9772, Y=40.7527)
route = ox.routing.shortest_path(G, orig, dest, weight="length")

### Save/load graph
import osmnx as ox

ox.io.save_graphml(G, "graph.graphml")
G2 = ox.io.load_graphml("graph.graphml")

---

## 4) Available Tools and Endpoints List

Use these as MCP (Model Context Protocol) service endpoints/tool actions:

- `graph_from_place / address / point / bbox / polygon / xml`  
  Build street-network graphs (`MultiDiGraph`) from OSM sources.

- `features_from_place / address / point / bbox / polygon / xml`  
  Fetch OSM feature layers as GeoDataFrames using tag filters.

- `geocode`, `geocode_to_gdf`  
  Resolve place/address text via Nominatim.

- `shortest_path`, `k_shortest_paths`  
  Route on graph topology using edge weights (e.g., length/travel time).

- `add_edge_speeds`, `add_edge_travel_times`  
  Enrich graph edges for travel-time routing.

- `nearest_nodes`, `nearest_edges`, `great_circle`, `euclidean`  
  Distance and nearest-neighbor utilities.

- `project_graph`, `project_gdf`, `project_geometry`  
  CRS transformation helpers.

- `simplify_graph`, `consolidate_intersections`  
  Clean/simplify topology for analysis.

- `basic_stats`  
  Compute core street-network metrics.

- `graph_to_gdfs`, `graph_from_gdfs`, `to_digraph`, `to_undirected`  
  Convert between graph and tabular geospatial structures.

- `save_graphml`, `load_graphml`, `save_graph_geopackage`, `save_graph_xml`  
  Persist and exchange graph data.

- `plot_graph`, `plot_graph_route`, `plot_graph_routes`, `plot_figure_ground`, `plot_footprints`, `plot_orientation`  
  Visualization utilities.

---

## 5) Common Issues and Notes

- **Rate limits / API etiquette**: OSM/Nominatim/Overpass endpoints can throttle requests. Use caching and avoid aggressive parallel querying.
- **CRS correctness**: Project to an appropriate local CRS before distance/area-sensitive analysis.
- **Large regions**: Big place queries can be slow or memory-heavy. Prefer bbox/polygon chunking when needed.
- **Optional deps missing**: Some advanced functions (plotting/elevation/spatial index) may fail if optional libraries are not installed.
- **Reproducibility**: Pin package versions in your environment for stable results across deployments.
- **I/O format choice**: Use GraphML for graph fidelity and GeoPackage when GIS interoperability is needed.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/gboeing/osmnx
- Official docs: https://osmnx.readthedocs.io/
- Changelog: https://github.com/gboeing/osmnx/blob/main/CHANGELOG.md
- Contributing guide: https://github.com/gboeing/osmnx/blob/main/CONTRIBUTING.md
- Tests/examples reference: https://github.com/gboeing/osmnx/tree/main/tests