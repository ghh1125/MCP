import os
import sys
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

import osmnx as ox

mcp = FastMCP("osmnx_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="geocode_place", description="Geocode a place name to latitude/longitude.")
def geocode_place(query: str) -> Dict[str, Any]:
    """
    Geocode a textual location query.

    Parameters:
        query: Place/address query string.

    Returns:
        Dict with success/result/error. On success, result is {'lat': float, 'lon': float}.
    """
    try:
        lat, lon = ox.geocode(query)
        return _ok({"lat": float(lat), "lon": float(lon)})
    except Exception as e:
        return _err(e)


@mcp.tool(name="graph_from_place", description="Build a street network graph from a place name.")
def graph_from_place(
    place: str,
    network_type: str = "drive",
    simplify: bool = True,
    retain_all: bool = False,
) -> Dict[str, Any]:
    """
    Create a graph for a place.

    Parameters:
        place: Place name query.
        network_type: OSMnx network type (e.g., drive, walk, bike, all).
        simplify: Whether to simplify graph topology.
        retain_all: Whether to keep all components.

    Returns:
        Dict with success/result/error. On success, result includes node/edge counts.
    """
    try:
        G = ox.graph_from_place(
            place,
            network_type=network_type,
            simplify=simplify,
            retain_all=retain_all,
        )
        return _ok({"nodes": int(len(G.nodes)), "edges": int(len(G.edges))})
    except Exception as e:
        return _err(e)


@mcp.tool(name="graph_from_bbox", description="Build a street network graph from a bounding box.")
def graph_from_bbox(
    north: float,
    south: float,
    east: float,
    west: float,
    network_type: str = "drive",
    simplify: bool = True,
    retain_all: bool = False,
) -> Dict[str, Any]:
    """
    Create a graph from bounding box coordinates.

    Parameters:
        north: Northern latitude.
        south: Southern latitude.
        east: Eastern longitude.
        west: Western longitude.
        network_type: OSMnx network type.
        simplify: Whether to simplify graph.
        retain_all: Whether to keep all components.

    Returns:
        Dict with success/result/error. On success, result includes node/edge counts.
    """
    try:
        G = ox.graph_from_bbox(
            (north, south, east, west),
            network_type=network_type,
            simplify=simplify,
            retain_all=retain_all,
        )
        return _ok({"nodes": int(len(G.nodes)), "edges": int(len(G.edges))})
    except Exception as e:
        return _err(e)


@mcp.tool(name="graph_from_point", description="Build a street network graph around a point.")
def graph_from_point(
    latitude: float,
    longitude: float,
    dist_m: int = 1000,
    network_type: str = "drive",
    simplify: bool = True,
    retain_all: bool = False,
) -> Dict[str, Any]:
    """
    Create a graph around a center point.

    Parameters:
        latitude: Center latitude.
        longitude: Center longitude.
        dist_m: Distance in meters from center.
        network_type: OSMnx network type.
        simplify: Whether to simplify graph.
        retain_all: Whether to keep all components.

    Returns:
        Dict with success/result/error. On success, result includes node/edge counts.
    """
    try:
        G = ox.graph_from_point(
            (latitude, longitude),
            dist=dist_m,
            network_type=network_type,
            simplify=simplify,
            retain_all=retain_all,
        )
        return _ok({"nodes": int(len(G.nodes)), "edges": int(len(G.edges))})
    except Exception as e:
        return _err(e)


@mcp.tool(name="features_from_place", description="Fetch OSM features for a place by tags.")
def features_from_place(
    place: str,
    tags: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Query OSM features for a place.

    Parameters:
        place: Place name query.
        tags: OSM tag filter dictionary.

    Returns:
        Dict with success/result/error. On success, result includes row count and columns.
    """
    try:
        gdf = ox.features_from_place(place, tags)
        return _ok({"rows": int(len(gdf)), "columns": [str(c) for c in gdf.columns]})
    except Exception as e:
        return _err(e)


@mcp.tool(name="nearest_node", description="Find nearest graph node to a coordinate.")
def nearest_node(
    place: str,
    latitude: float,
    longitude: float,
    network_type: str = "drive",
) -> Dict[str, Any]:
    """
    Find nearest node in a graph built from place.

    Parameters:
        place: Place query to build graph.
        latitude: Query latitude.
        longitude: Query longitude.
        network_type: OSMnx network type.

    Returns:
        Dict with success/result/error. On success, result contains nearest node id.
    """
    try:
        G = ox.graph_from_place(place, network_type=network_type)
        node_id = ox.distance.nearest_nodes(G, X=longitude, Y=latitude)
        return _ok({"node_id": int(node_id)})
    except Exception as e:
        return _err(e)


@mcp.tool(name="shortest_path", description="Compute shortest path length between two coordinates.")
def shortest_path(
    place: str,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    network_type: str = "drive",
    weight: str = "length",
) -> Dict[str, Any]:
    """
    Compute shortest route between origin and destination points.

    Parameters:
        place: Place query to build graph.
        origin_lat: Origin latitude.
        origin_lon: Origin longitude.
        dest_lat: Destination latitude.
        dest_lon: Destination longitude.
        network_type: OSMnx network type.
        weight: Edge weight attribute, typically 'length' or 'travel_time'.

    Returns:
        Dict with success/result/error. On success, result includes path node ids and route length.
    """
    try:
        G = ox.graph_from_place(place, network_type=network_type)
        orig = ox.distance.nearest_nodes(G, X=origin_lon, Y=origin_lat)
        dest = ox.distance.nearest_nodes(G, X=dest_lon, Y=dest_lat)
        route = ox.routing.shortest_path(G, orig, dest, weight=weight)
        if route is None:
            return _ok({"path": [], "total_weight": None})
        total_weight = 0.0
        for u, v in zip(route[:-1], route[1:]):
            edge_data = G.get_edge_data(u, v)
            if not edge_data:
                continue
            first_key = next(iter(edge_data))
            w = edge_data[first_key].get(weight, 0.0)
            total_weight += float(w if w is not None else 0.0)
        return _ok({"path": [int(n) for n in route], "total_weight": total_weight})
    except Exception as e:
        return _err(e)


@mcp.tool(name="basic_graph_stats", description="Compute basic graph statistics for a place.")
def basic_graph_stats(place: str, network_type: str = "drive") -> Dict[str, Any]:
    """
    Compute key statistics for a place graph.

    Parameters:
        place: Place query to build graph.
        network_type: OSMnx network type.

    Returns:
        Dict with success/result/error. On success, result includes selected graph stats.
    """
    try:
        G = ox.graph_from_place(place, network_type=network_type)
        stats = ox.stats.basic_stats(G)
        selected_keys = [
            "n",
            "m",
            "k_avg",
            "edge_length_total",
            "edge_length_avg",
            "streets_per_node_avg",
            "street_length_total",
            "street_segment_count",
            "intersection_count",
        ]
        out: Dict[str, Any] = {}
        for k in selected_keys:
            if k in stats:
                v = stats[k]
                out[k] = float(v) if isinstance(v, (int, float)) else v
        return _ok(out)
    except Exception as e:
        return _err(e)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()