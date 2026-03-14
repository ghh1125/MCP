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
import rasterio
from rasterio import windows as rio_windows
from rasterio import warp as rio_warp
from rasterio import merge as rio_merge
from rasterio import features as rio_features


mcp = FastMCP("rasterio_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="raster_open_info", description="Open a raster dataset and return key metadata.")
def raster_open_info(path: str) -> Dict[str, Any]:
    """
    Open a raster dataset and return key metadata.

    Parameters:
        path: Path/URI to raster readable by GDAL/rasterio.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            result = {
                "name": ds.name,
                "driver": ds.driver,
                "width": ds.width,
                "height": ds.height,
                "count": ds.count,
                "dtypes": list(ds.dtypes),
                "crs": ds.crs.to_string() if ds.crs else None,
                "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
                "transform": list(ds.transform) if ds.transform else None,
                "nodata": ds.nodata,
            }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_read_band", description="Read one band from raster and return summary statistics.")
def raster_read_band(path: str, band: int = 1, masked: bool = True) -> Dict[str, Any]:
    """
    Read one raster band and return shape and simple statistics.

    Parameters:
        path: Path/URI to raster dataset.
        band: 1-based band index to read.
        masked: Whether to read with mask.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            arr = ds.read(band, masked=masked)
            if hasattr(arr, "compressed"):
                vals = arr.compressed()
            else:
                vals = arr.ravel()
            if vals.size == 0:
                stats = {"min": None, "max": None, "mean": None}
            else:
                stats = {
                    "min": float(vals.min()),
                    "max": float(vals.max()),
                    "mean": float(vals.mean()),
                }
            result = {
                "band": band,
                "shape": [int(arr.shape[0]), int(arr.shape[1])],
                "dtype": str(arr.dtype),
                "stats": stats,
            }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_window_read", description="Read a pixel window subset from a raster.")
def raster_window_read(
    path: str,
    col_off: int,
    row_off: int,
    width: int,
    height: int,
    band: int = 1,
) -> Dict[str, Any]:
    """
    Read a raster subset defined by pixel window offsets/sizes.

    Parameters:
        path: Path/URI to raster dataset.
        col_off: Column offset (x).
        row_off: Row offset (y).
        width: Window width in pixels.
        height: Window height in pixels.
        band: 1-based band index.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            win = rio_windows.Window(col_off=col_off, row_off=row_off, width=width, height=height)
            arr = ds.read(band, window=win, masked=True)
            vals = arr.compressed()
            result = {
                "window": {
                    "col_off": int(col_off),
                    "row_off": int(row_off),
                    "width": int(width),
                    "height": int(height),
                },
                "shape": [int(arr.shape[0]), int(arr.shape[1])],
                "min": float(vals.min()) if vals.size else None,
                "max": float(vals.max()) if vals.size else None,
                "mean": float(vals.mean()) if vals.size else None,
            }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_transform_xy", description="Transform pixel row/col to x/y coordinates.")
def raster_transform_xy(path: str, row: int, col: int, offset: str = "center") -> Dict[str, Any]:
    """
    Convert pixel coordinates to spatial coordinates.

    Parameters:
        path: Path/URI to raster dataset.
        row: Pixel row.
        col: Pixel column.
        offset: Pixel reference offset ('center', 'ul', 'ur', 'll', 'lr').

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            x, y = ds.xy(row, col, offset=offset)
            return _ok({"x": float(x), "y": float(y)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_bounds_in_crs", description="Reproject dataset bounds into another CRS.")
def raster_bounds_in_crs(path: str, dst_crs: str, densify_pts: int = 21) -> Dict[str, Any]:
    """
    Transform raster bounds from source CRS to destination CRS.

    Parameters:
        path: Path/URI to raster dataset.
        dst_crs: Destination CRS (e.g., 'EPSG:4326').
        densify_pts: Number of edge densification points for accurate transform.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            if ds.crs is None:
                return _err("Source dataset has no CRS.")
            left, bottom, right, top = rio_warp.transform_bounds(
                ds.crs, dst_crs, *ds.bounds, densify_pts=densify_pts
            )
            return _ok({"bounds": [left, bottom, right, top], "dst_crs": dst_crs})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_shapes_extract", description="Extract vectorized shapes from a raster band.")
def raster_shapes_extract(
    path: str,
    band: int = 1,
    connectivity: int = 4,
    with_nodata: bool = False,
) -> Dict[str, Any]:
    """
    Extract polygon-like shapes and values from raster pixels.

    Parameters:
        path: Path/URI to raster dataset.
        band: 1-based band index.
        connectivity: Pixel connectivity (4 or 8).
        with_nodata: Include nodata regions if True.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        with rasterio.open(path) as ds:
            arr = ds.read(band)
            mask = None if with_nodata else ds.read_masks(band).astype(bool)
            items = list(
                rio_features.shapes(
                    arr,
                    mask=mask,
                    connectivity=connectivity,
                    transform=ds.transform,
                )
            )
            sample: List[Dict[str, Any]] = []
            for geom, val in items[:20]:
                sample.append({"value": float(val), "geometry_type": geom.get("type")})
            return _ok({"count": len(items), "sample": sample})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="raster_merge_preview", description="Merge rasters in memory and return merged metadata.")
def raster_merge_preview(paths: List[str], method: str = "first") -> Dict[str, Any]:
    """
    Merge multiple rasters into an in-memory mosaic preview.

    Parameters:
        paths: List of raster paths/URIs.
        method: Merge method supported by rasterio.merge.merge.

    Returns:
        Dictionary with success/result/error fields.
    """
    datasets = []
    try:
        if not paths:
            return _err("At least one path is required.")
        for p in paths:
            datasets.append(rasterio.open(p))
        mosaic, transform = rio_merge.merge(datasets, method=method)
        result = {
            "shape": [int(mosaic.shape[0]), int(mosaic.shape[1]), int(mosaic.shape[2])],
            "dtype": str(mosaic.dtype),
            "transform": list(transform),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))
    finally:
        for ds in datasets:
            try:
                ds.close()
            except Exception:
                pass


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()