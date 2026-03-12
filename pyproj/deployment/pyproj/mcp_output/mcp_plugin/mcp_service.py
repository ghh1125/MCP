import os
import sys
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from pyproj import CRS, Geod, Proj, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.datadir import get_data_dir, set_data_dir
from pyproj.network import is_network_enabled, set_network_enabled
from pyproj.transformer import TransformerGroup

mcp = FastMCP("pyproj_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="get_version_info", description="Get pyproj and PROJ runtime version information.")
def get_version_info() -> Dict[str, Any]:
    """
    Return pyproj and PROJ version metadata.

    Returns:
        Dict[str, Any]:
            - success: bool indicating operation status
            - result: version details if successful
            - error: error string if failed
    """
    try:
        import pyproj

        return _ok(
            {
                "pyproj_version": pyproj.__version__,
                "proj_version": pyproj.proj_version_str,
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="crs_from_user_input", description="Parse a CRS from EPSG code, WKT, PROJ string, or JSON.")
def crs_from_user_input(user_input: str) -> Dict[str, Any]:
    """
    Build a CRS object from user-provided CRS text.

    Parameters:
        user_input: CRS expression (e.g., 'EPSG:4326', PROJ string, WKT, JSON).

    Returns:
        Dict[str, Any]:
            Standard result dictionary with CRS representations.
    """
    try:
        crs = CRS.from_user_input(user_input)
        return _ok(
            {
                "name": crs.name,
                "type_name": crs.type_name,
                "is_geographic": crs.is_geographic,
                "is_projected": crs.is_projected,
                "to_authority": crs.to_authority(),
                "to_epsg": crs.to_epsg(),
                "proj4": crs.to_proj4(),
                "wkt": crs.to_wkt(),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="transform_coordinates", description="Transform a single coordinate between CRS definitions.")
def transform_coordinates(
    from_crs: str,
    to_crs: str,
    x: float,
    y: float,
    z: Optional[float] = None,
    always_xy: bool = True,
) -> Dict[str, Any]:
    """
    Transform one coordinate tuple from source CRS to target CRS.

    Parameters:
        from_crs: Source CRS string.
        to_crs: Target CRS string.
        x: Input X/longitude/easting.
        y: Input Y/latitude/northing.
        z: Optional input Z value.
        always_xy: Force longitude-latitude/easting-northing axis order.

    Returns:
        Dict[str, Any]:
            Standard result dictionary containing transformed coordinates.
    """
    try:
        transformer = Transformer.from_crs(from_crs, to_crs, always_xy=always_xy)
        if z is None:
            tx, ty = transformer.transform(x, y)
            return _ok({"x": tx, "y": ty})
        tx, ty, tz = transformer.transform(x, y, z)
        return _ok({"x": tx, "y": ty, "z": tz})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="get_transformer_details", description="Inspect operation metadata between two CRS definitions.")
def get_transformer_details(
    from_crs: str,
    to_crs: str,
    always_xy: bool = True,
    area_west_lon: Optional[float] = None,
    area_south_lat: Optional[float] = None,
    area_east_lon: Optional[float] = None,
    area_north_lat: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build a TransformerGroup and return available operation details.

    Parameters:
        from_crs: Source CRS string.
        to_crs: Target CRS string.
        always_xy: Axis-order behavior.
        area_west_lon: Optional AOI west bound.
        area_south_lat: Optional AOI south bound.
        area_east_lon: Optional AOI east bound.
        area_north_lat: Optional AOI north bound.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with best/available operations.
    """
    try:
        area: Optional[AreaOfInterest] = None
        has_all = all(
            v is not None
            for v in [area_west_lon, area_south_lat, area_east_lon, area_north_lat]
        )
        if has_all:
            area = AreaOfInterest(
                west_lon_degree=float(area_west_lon),
                south_lat_degree=float(area_south_lat),
                east_lon_degree=float(area_east_lon),
                north_lat_degree=float(area_north_lat),
            )
        tg = TransformerGroup(from_crs, to_crs, always_xy=always_xy, area_of_interest=area)
        best_description = tg.transformers[0].description if tg.transformers else None
        return _ok(
            {
                "best_available": tg.best_available,
                "transformer_count": len(tg.transformers),
                "best_description": best_description,
                "unavailable_operations_count": len(tg.unavailable_operations),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="geodesic_inverse", description="Compute geodesic inverse: azimuths and distance between two points.")
def geodesic_inverse(
    lon1: float,
    lat1: float,
    lon2: float,
    lat2: float,
    ellps: str = "WGS84",
) -> Dict[str, Any]:
    """
    Compute forward azimuth, back azimuth, and distance between two lon/lat points.

    Parameters:
        lon1: First longitude.
        lat1: First latitude.
        lon2: Second longitude.
        lat2: Second latitude.
        ellps: Ellipsoid name.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with azimuths and meters distance.
    """
    try:
        geod = Geod(ellps=ellps)
        fwd_az, back_az, dist_m = geod.inv(lon1, lat1, lon2, lat2)
        return _ok(
            {
                "forward_azimuth": fwd_az,
                "back_azimuth": back_az,
                "distance_m": dist_m,
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="geodesic_forward", description="Compute destination point from start point, azimuth, and distance.")
def geodesic_forward(
    lon: float,
    lat: float,
    azimuth: float,
    distance_m: float,
    ellps: str = "WGS84",
) -> Dict[str, Any]:
    """
    Solve geodesic forward problem.

    Parameters:
        lon: Start longitude.
        lat: Start latitude.
        azimuth: Forward azimuth at start point.
        distance_m: Distance in meters.
        ellps: Ellipsoid name.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with destination and back azimuth.
    """
    try:
        geod = Geod(ellps=ellps)
        lon2, lat2, back_az = geod.fwd(lon, lat, azimuth, distance_m)
        return _ok({"lon": lon2, "lat": lat2, "back_azimuth": back_az})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="project_with_proj", description="Project a coordinate using a PROJ definition or EPSG code.")
def project_with_proj(
    proj_definition: str,
    x: float,
    y: float,
    inverse: bool = False,
) -> Dict[str, Any]:
    """
    Apply Proj transformation for one coordinate.

    Parameters:
        proj_definition: PROJ string, dictionary-like params, or EPSG reference string.
        x: Input x/lon value.
        y: Input y/lat value.
        inverse: Whether to apply inverse projection.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with projected coordinate.
    """
    try:
        p = Proj(proj_definition)
        ox, oy = p(x, y, inverse=inverse)
        return _ok({"x": ox, "y": oy})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="get_data_directory", description="Get current pyproj data directory.")
def get_data_directory() -> Dict[str, Any]:
    """
    Retrieve the active PROJ/pyproj data directory path.

    Returns:
        Dict[str, Any]:
            Standard result dictionary containing data directory path.
    """
    try:
        return _ok({"data_dir": get_data_dir()})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="set_data_directory", description="Set pyproj data directory.")
def set_data_directory(path: str) -> Dict[str, Any]:
    """
    Set the data directory used by pyproj.

    Parameters:
        path: Filesystem path to PROJ data directory.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with updated path.
    """
    try:
        set_data_dir(path)
        return _ok({"data_dir": get_data_dir()})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="get_network_status", description="Check whether pyproj network access is enabled.")
def get_network_status() -> Dict[str, Any]:
    """
    Get current pyproj network-enabled status.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with network flag.
    """
    try:
        return _ok({"network_enabled": bool(is_network_enabled())})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="set_network_status", description="Enable or disable pyproj network access.")
def set_network_status(enabled: bool) -> Dict[str, Any]:
    """
    Set pyproj network-enabled status.

    Parameters:
        enabled: True to enable remote network access, False to disable.

    Returns:
        Dict[str, Any]:
            Standard result dictionary with resulting network flag.
    """
    try:
        set_network_enabled(active=enabled)
        return _ok({"network_enabled": bool(is_network_enabled())})
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()