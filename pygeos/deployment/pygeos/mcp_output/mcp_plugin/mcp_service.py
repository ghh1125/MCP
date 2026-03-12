import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from pygeos import (
    creation,
    io,
    measurement,
    predicates,
    set_operations,
    constructive,
    coordinates,
    linear,
)

mcp = FastMCP("pygeos_service")


@mcp.tool(name="from_wkt", description="Create geometry from WKT text.")
def from_wkt(wkt: str) -> Dict[str, Any]:
    """
    Parse a WKT string into a geometry object.

    Parameters:
    - wkt: WKT geometry text.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        return {"success": True, "result": io.to_wkt(geom), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="to_wkt", description="Convert geometry from WKT input to normalized WKT output.")
def to_wkt(wkt: str, rounding_precision: int = 6, trim: bool = True) -> Dict[str, Any]:
    """
    Normalize WKT by parsing and serializing with formatting options.

    Parameters:
    - wkt: Input WKT geometry text.
    - rounding_precision: Decimal rounding precision in output.
    - trim: Whether to trim trailing zeros.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = io.to_wkt(geom, rounding_precision=rounding_precision, trim=trim)
        return {"success": True, "result": out, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="point", description="Create a point geometry.")
def point(x: float, y: float, z: Optional[float] = None) -> Dict[str, Any]:
    """
    Create a point from coordinates.

    Parameters:
    - x: X coordinate.
    - y: Y coordinate.
    - z: Optional Z coordinate.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        if z is None:
            geom = creation.points([[x, y]])[0]
        else:
            geom = creation.points([[x, y, z]])[0]
        return {"success": True, "result": io.to_wkt(geom), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="linestring", description="Create a LineString geometry from coordinate pairs.")
def linestring(coords: List[List[float]]) -> Dict[str, Any]:
    """
    Create a linestring from coordinate arrays.

    Parameters:
    - coords: List of coordinate lists, e.g. [[x1, y1], [x2, y2], ...].

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = creation.linestrings([coords])[0]
        return {"success": True, "result": io.to_wkt(geom), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="polygon", description="Create a Polygon geometry from shell coordinates.")
def polygon(shell: List[List[float]], holes: Optional[List[List[List[float]]]] = None) -> Dict[str, Any]:
    """
    Create a polygon from shell and optional holes.

    Parameters:
    - shell: Exterior ring coordinates.
    - holes: Optional list of interior ring coordinates.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        if holes is None:
            geom = creation.polygons([shell])[0]
        else:
            geom = creation.polygons([shell], holes=[holes])[0]
        return {"success": True, "result": io.to_wkt(geom), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="buffer", description="Compute geometry buffer.")
def buffer(wkt: str, distance: float, quadsegs: int = 8) -> Dict[str, Any]:
    """
    Compute a buffer around geometry.

    Parameters:
    - wkt: Input geometry in WKT.
    - distance: Buffer distance.
    - quadsegs: Number of quadrant segments.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = constructive.buffer(geom, distance, quadsegs=quadsegs)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="centroid", description="Compute geometry centroid.")
def centroid(wkt: str) -> Dict[str, Any]:
    """
    Compute centroid of input geometry.

    Parameters:
    - wkt: Input geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = constructive.centroid(geom)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="area", description="Compute geometry area.")
def area(wkt: str) -> Dict[str, Any]:
    """
    Compute area for input geometry.

    Parameters:
    - wkt: Input geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = measurement.area(geom)
        return {"success": True, "result": float(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="length", description="Compute geometry length/perimeter.")
def length(wkt: str) -> Dict[str, Any]:
    """
    Compute length for input geometry.

    Parameters:
    - wkt: Input geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = measurement.length(geom)
        return {"success": True, "result": float(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="distance", description="Compute distance between two geometries.")
def distance(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Compute distance between two geometries.

    Parameters:
    - wkt_a: First geometry in WKT.
    - wkt_b: Second geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = measurement.distance(a, b)
        return {"success": True, "result": float(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="intersects", description="Check if two geometries intersect.")
def intersects(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Evaluate intersects predicate.

    Parameters:
    - wkt_a: First geometry in WKT.
    - wkt_b: Second geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = predicates.intersects(a, b)
        return {"success": True, "result": bool(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="contains", description="Check if first geometry contains second.")
def contains(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Evaluate contains predicate.

    Parameters:
    - wkt_a: Container geometry in WKT.
    - wkt_b: Candidate geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = predicates.contains(a, b)
        return {"success": True, "result": bool(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="within", description="Check if first geometry is within second.")
def within(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Evaluate within predicate.

    Parameters:
    - wkt_a: Candidate geometry in WKT.
    - wkt_b: Container geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = predicates.within(a, b)
        return {"success": True, "result": bool(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="union", description="Compute union of two geometries.")
def union(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Compute union of two geometries.

    Parameters:
    - wkt_a: First geometry in WKT.
    - wkt_b: Second geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = set_operations.union(a, b)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="intersection", description="Compute intersection of two geometries.")
def intersection(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Compute intersection of two geometries.

    Parameters:
    - wkt_a: First geometry in WKT.
    - wkt_b: Second geometry in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = set_operations.intersection(a, b)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="difference", description="Compute difference of two geometries.")
def difference(wkt_a: str, wkt_b: str) -> Dict[str, Any]:
    """
    Compute A - B difference.

    Parameters:
    - wkt_a: First geometry (A) in WKT.
    - wkt_b: Second geometry (B) in WKT.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        a = io.from_wkt(wkt_a)
        b = io.from_wkt(wkt_b)
        out = set_operations.difference(a, b)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="line_interpolate_point", description="Interpolate a point along a linear geometry.")
def line_interpolate_point(wkt: str, distance: float, normalized: bool = False) -> Dict[str, Any]:
    """
    Interpolate point along a linestring.

    Parameters:
    - wkt: Input linear geometry in WKT.
    - distance: Distance or fraction along line.
    - normalized: Interpret distance as normalized fraction if True.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        out = linear.line_interpolate_point(geom, distance, normalized=normalized)
        return {"success": True, "result": io.to_wkt(out), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="get_coordinates", description="Extract coordinates from a geometry.")
def get_coordinates(wkt: str, include_z: bool = False) -> Dict[str, Any]:
    """
    Extract coordinate array from geometry.

    Parameters:
    - wkt: Input geometry in WKT.
    - include_z: Include Z dimension if present.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        geom = io.from_wkt(wkt)
        arr = coordinates.get_coordinates(geom, include_z=include_z)
        return {"success": True, "result": arr.tolist(), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp