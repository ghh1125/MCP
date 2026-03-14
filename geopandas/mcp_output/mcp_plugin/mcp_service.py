import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import geopandas as gpd
from geopandas.tools import clip as gpd_clip
from geopandas.tools import overlay as gpd_overlay
from geopandas.tools import sjoin as gpd_sjoin
from shapely import wkt

mcp = FastMCP("geopandas_mcp_service")


def _safe_read(path: str, layer: str | None = None) -> gpd.GeoDataFrame:
    if layer and layer.strip():
        return gpd.read_file(path, layer=layer)
    return gpd.read_file(path)


def _ok(result: Any) -> dict:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> dict:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="read_vector_file", description="Read a vector dataset and return summary information.")
def read_vector_file(path: str, layer: str | None = None) -> dict:
    """
    Read a vector geospatial file into a GeoDataFrame.

    Parameters:
        path: Path or URL to the vector dataset.
        layer: Optional layer name for multi-layer sources.

    Returns:
        Dictionary with success/result/error fields.
        result contains row count, column names, geometry column name, and CRS.
    """
    try:
        gdf = _safe_read(path, layer)
        return _ok(
            {
                "rows": int(len(gdf)),
                "columns": [str(c) for c in gdf.columns],
                "geometry_column": str(gdf.geometry.name),
                "crs": str(gdf.crs) if gdf.crs is not None else None,
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="transform_crs", description="Reproject a dataset to a target CRS and write it to disk.")
def transform_crs(
    input_path: str,
    output_path: str,
    target_crs: str,
    layer: str | None = None,
    driver: str | None = None,
) -> dict:
    """
    Reproject a vector dataset and save it.

    Parameters:
        input_path: Source dataset path.
        output_path: Destination dataset path.
        target_crs: Target CRS (e.g., 'EPSG:3857').
        layer: Optional layer name to read.
        driver: Optional output driver.

    Returns:
        Dictionary with success/result/error fields.
        result contains output path, target CRS, and written feature count.
    """
    try:
        gdf = _safe_read(input_path, layer)
        out = gdf.to_crs(target_crs)
        if driver and driver.strip():
            out.to_file(output_path, driver=driver)
        else:
            out.to_file(output_path)
        return _ok(
            {
                "output_path": output_path,
                "target_crs": str(out.crs) if out.crs is not None else None,
                "rows": int(len(out)),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="spatial_clip", description="Clip one dataset by another mask dataset and write output.")
def spatial_clip(
    input_path: str,
    mask_path: str,
    output_path: str,
    input_layer: str | None = None,
    mask_layer: str | None = None,
    driver: str | None = None,
) -> dict:
    """
    Clip features from one dataset using geometries from a mask dataset.

    Parameters:
        input_path: Path to input dataset.
        mask_path: Path to mask dataset.
        output_path: Path where clipped dataset is saved.
        input_layer: Optional input layer name.
        mask_layer: Optional mask layer name.
        driver: Optional output driver.

    Returns:
        Dictionary with success/result/error fields.
        result contains output path and feature count.
    """
    try:
        gdf = _safe_read(input_path, input_layer)
        mask = _safe_read(mask_path, mask_layer)
        clipped = gpd_clip(gdf, mask)
        if driver and driver.strip():
            clipped.to_file(output_path, driver=driver)
        else:
            clipped.to_file(output_path)
        return _ok({"output_path": output_path, "rows": int(len(clipped))})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="spatial_overlay", description="Run overlay operation between two datasets and save output.")
def spatial_overlay(
    left_path: str,
    right_path: str,
    how: str,
    output_path: str,
    left_layer: str | None = None,
    right_layer: str | None = None,
    keep_geom_type: bool = True,
    driver: str | None = None,
) -> dict:
    """
    Perform GeoPandas overlay operation.

    Parameters:
        left_path: Path to left dataset.
        right_path: Path to right dataset.
        how: Overlay mode: intersection, union, identity, symmetric_difference, or difference.
        output_path: Output dataset path.
        left_layer: Optional left layer.
        right_layer: Optional right layer.
        keep_geom_type: Preserve only original geometry types when True.
        driver: Optional output driver.

    Returns:
        Dictionary with success/result/error fields.
        result contains output path, mode, and feature count.
    """
    try:
        left = _safe_read(left_path, left_layer)
        right = _safe_read(right_path, right_layer)
        result = gpd_overlay(left, right, how=how, keep_geom_type=keep_geom_type)
        if driver and driver.strip():
            result.to_file(output_path, driver=driver)
        else:
            result.to_file(output_path)
        return _ok({"output_path": output_path, "how": how, "rows": int(len(result))})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="spatial_join", description="Run spatial join between two datasets and save output.")
def spatial_join(
    left_path: str,
    right_path: str,
    predicate: str,
    how: str,
    output_path: str,
    left_layer: str | None = None,
    right_layer: str | None = None,
    driver: str | None = None,
) -> dict:
    """
    Execute a spatial join.

    Parameters:
        left_path: Path to left dataset.
        right_path: Path to right dataset.
        predicate: Spatial predicate, e.g., intersects, within, contains.
        how: Join type: left, right, inner.
        output_path: Output dataset path.
        left_layer: Optional left layer.
        right_layer: Optional right layer.
        driver: Optional output driver.

    Returns:
        Dictionary with success/result/error fields.
        result contains output path, join metadata, and feature count.
    """
    try:
        left = _safe_read(left_path, left_layer)
        right = _safe_read(right_path, right_layer)
        joined = gpd_sjoin(left, right, how=how, predicate=predicate)
        if driver and driver.strip():
            joined.to_file(output_path, driver=driver)
        else:
            joined.to_file(output_path)
        return _ok(
            {
                "output_path": output_path,
                "how": how,
                "predicate": predicate,
                "rows": int(len(joined)),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="buffer_wkt", description="Buffer WKT geometries and return buffered geometries as WKT.")
def buffer_wkt(wkt_geometries: list[str], distance: float) -> dict:
    """
    Buffer a list of WKT geometries.

    Parameters:
        wkt_geometries: List of input geometries encoded as WKT strings.
        distance: Buffer distance.

    Returns:
        Dictionary with success/result/error fields.
        result is a list of buffered geometries in WKT form.
    """
    try:
        geoms = [wkt.loads(s) for s in wkt_geometries]
        gs = gpd.GeoSeries(geoms)
        buffered = gs.buffer(distance)
        return _ok([geom.wkt if geom is not None else None for geom in buffered])
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="dataset_bounds", description="Compute total bounds of a vector dataset.")
def dataset_bounds(path: str, layer: str | None = None) -> dict:
    """
    Compute bounding box for a dataset.

    Parameters:
        path: Path to dataset.
        layer: Optional layer name.

    Returns:
        Dictionary with success/result/error fields.
        result contains minx, miny, maxx, maxy and CRS.
    """
    try:
        gdf = _safe_read(path, layer)
        minx, miny, maxx, maxy = gdf.total_bounds.tolist()
        return _ok(
            {
                "minx": float(minx),
                "miny": float(miny),
                "maxx": float(maxx),
                "maxy": float(maxy),
                "crs": str(gdf.crs) if gdf.crs is not None else None,
            }
        )
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()