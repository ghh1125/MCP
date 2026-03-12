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
import xarray as xr
from xmitgcm import open_mdsdataset
from xmitgcm.llcreader import known_models, llcmodel
from xmitgcm.llcreader.stores import BaseStore
from xmitgcm.utils import get_grid_from_input

mcp = FastMCP("xmitgcm_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="open_mds_dataset",
    description="Open MITgcm MDS output as an xarray Dataset.",
)
def open_mds_dataset(
    data_dir: str,
    iters: Optional[List[int]] = None,
    prefix: Optional[List[str]] = None,
    read_grid: bool = True,
    delta_t: Optional[float] = None,
    ref_date: Optional[str] = None,
    calendar: str = "gregorian",
    geometry: str = "cartesian",
    chunks: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Open an MITgcm MDS dataset from a directory.

    Parameters:
    - data_dir: Path to model output directory.
    - iters: Optional list of iteration numbers to read.
    - prefix: Optional list of variable/file prefixes to load.
    - read_grid: Whether to load grid variables.
    - delta_t: Optional model timestep in seconds.
    - ref_date: Optional reference date string.
    - calendar: Calendar name for CF decoding.
    - geometry: Grid geometry (e.g., cartesian, sphericalpolar, llc).
    - chunks: Optional dask chunk mapping.

    Returns:
    - Standard response dict with success/result/error.
    """
    try:
        ds = open_mdsdataset(
            data_dir,
            iters=iters,
            prefix=prefix,
            read_grid=read_grid,
            delta_t=delta_t,
            ref_date=ref_date,
            calendar=calendar,
            geometry=geometry,
            chunks=chunks,
        )
        result = {
            "dims": {k: int(v) for k, v in ds.dims.items()},
            "data_vars": sorted(list(ds.data_vars)),
            "coords": sorted(list(ds.coords)),
            "attrs": {k: str(v) for k, v in ds.attrs.items()},
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="dataset_summary",
    description="Return a compact summary for a NetCDF/Zarr dataset path.",
)
def dataset_summary(path: str, engine: Optional[str] = None) -> Dict[str, Any]:
    """
    Open a dataset by path and summarize dimensions, variables, and coordinates.

    Parameters:
    - path: Path/URI to dataset.
    - engine: Optional xarray engine hint.

    Returns:
    - Standard response dict with success/result/error.
    """
    try:
        if engine:
            ds = xr.open_dataset(path, engine=engine)
        else:
            ds = xr.open_dataset(path)
        result = {
            "dims": {k: int(v) for k, v in ds.dims.items()},
            "data_vars": sorted(list(ds.data_vars)),
            "coords": sorted(list(ds.coords)),
            "attrs": {k: str(v) for k, v in ds.attrs.items()},
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="extract_grid",
    description="Extract grid information from an xarray Dataset path.",
)
def extract_grid(path: str, engine: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a dataset and extract grid object information using xmitgcm utilities.

    Parameters:
    - path: Path/URI to dataset.
    - engine: Optional xarray engine hint.

    Returns:
    - Standard response dict with success/result/error.
    """
    try:
        if engine:
            ds = xr.open_dataset(path, engine=engine)
        else:
            ds = xr.open_dataset(path)
        grid = get_grid_from_input(ds)
        result = {
            "grid_type": type(grid).__name__,
            "grid_repr": repr(grid),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="list_llc_known_models",
    description="List known LLC model configurations available in xmitgcm.",
)
def list_llc_known_models() -> Dict[str, Any]:
    """
    Return available model names exposed by xmitgcm.llcreader.known_models.

    Returns:
    - Standard response dict with success/result/error.
    """
    try:
        names = []
        if hasattr(known_models, "MODELS") and isinstance(known_models.MODELS, dict):
            names = sorted(list(known_models.MODELS.keys()))
        else:
            names = sorted(
                [
                    n
                    for n in dir(known_models)
                    if not n.startswith("_") and n.lower().endswith("model")
                ]
            )
        return _ok({"models": names})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="llc_module_introspection",
    description="Inspect key public symbols in llcmodel and store modules.",
)
def llc_module_introspection() -> Dict[str, Any]:
    """
    Provide introspection details for LLC reader core classes and functions.

    Returns:
    - Standard response dict with success/result/error.
    """
    try:
        llc_symbols = [n for n in dir(llcmodel) if not n.startswith("_")]
        store_symbols = [n for n in dir(BaseStore) if not n.startswith("_")]
        result = {
            "llcmodel_public_symbols": sorted(llc_symbols),
            "base_store_public_members": sorted(store_symbols),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()