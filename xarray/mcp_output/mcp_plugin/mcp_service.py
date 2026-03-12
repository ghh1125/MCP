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

mcp = FastMCP("xarray_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="xr_print_versions", description="Return xarray and dependency version information.")
def xr_print_versions() -> Dict[str, Any]:
    """
    Collect xarray runtime version diagnostics.

    Returns:
        Dict containing:
            success: True if operation succeeds, otherwise False.
            result: Version report string on success.
            error: Error message on failure, otherwise None.
    """
    try:
        from xarray.util.print_versions import show_versions
        from io import StringIO
        import contextlib

        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            show_versions()
        return _ok(buf.getvalue())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_open_dataset", description="Open a dataset from a file path/URL and return summary.")
def xr_open_dataset(
    path: str,
    engine: Optional[str] = None,
    decode_cf: bool = True,
    chunks: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Open an xarray Dataset and return a compact metadata summary.

    Parameters:
        path: Dataset path or URL.
        engine: Backend engine (e.g., 'netcdf4', 'h5netcdf', 'scipy', 'zarr').
        decode_cf: Whether to decode CF conventions.
        chunks: If provided, enables dask chunking with this chunk size.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        chunk_spec = {"__auto__": chunks} if chunks is not None else None
        if chunk_spec is not None:
            ds = xr.open_dataset(path, engine=engine, decode_cf=decode_cf, chunks=chunk_spec)
        else:
            ds = xr.open_dataset(path, engine=engine, decode_cf=decode_cf)

        result = {
            "dims": {k: int(v) for k, v in ds.sizes.items()},
            "data_vars": list(ds.data_vars),
            "coords": list(ds.coords),
            "attrs": dict(ds.attrs),
        }
        ds.close()
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_dataset_to_netcdf", description="Write an in-memory dataset description to NetCDF.")
def xr_dataset_to_netcdf(
    output_path: str,
    variable_name: str,
    values: List[float],
    dim_name: str = "dim_0",
) -> Dict[str, Any]:
    """
    Build a simple Dataset from numeric values and write it to NetCDF.

    Parameters:
        output_path: Destination file path.
        variable_name: Data variable name.
        values: 1D numeric values.
        dim_name: Dimension name for the 1D variable.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        ds = xr.Dataset({variable_name: (dim_name, values)})
        ds.to_netcdf(output_path)
        ds.close()
        return _ok({"written": output_path, "variable": variable_name, "length": len(values)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_open_dataarray", description="Open a DataArray and return summary metadata.")
def xr_open_dataarray(
    path: str,
    engine: Optional[str] = None,
    decode_cf: bool = True,
) -> Dict[str, Any]:
    """
    Open an xarray DataArray and return metadata summary.

    Parameters:
        path: DataArray file path or URL.
        engine: Optional backend engine.
        decode_cf: Whether to decode CF conventions.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        da = xr.open_dataarray(path, engine=engine, decode_cf=decode_cf)
        result = {
            "name": da.name,
            "dims": list(da.dims),
            "shape": list(da.shape),
            "dtype": str(da.dtype),
            "attrs": dict(da.attrs),
        }
        da.close()
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_merge_datasets", description="Merge two simple in-memory datasets by variable names.")
def xr_merge_datasets(
    var1_name: str,
    var1_values: List[float],
    var2_name: str,
    var2_values: List[float],
    dim_name: str = "x",
) -> Dict[str, Any]:
    """
    Create and merge two in-memory datasets.

    Parameters:
        var1_name: First variable name.
        var1_values: First 1D variable values.
        var2_name: Second variable name.
        var2_values: Second 1D variable values.
        dim_name: Shared dimension name.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        ds1 = xr.Dataset({var1_name: (dim_name, var1_values)})
        ds2 = xr.Dataset({var2_name: (dim_name, var2_values)})
        merged = xr.merge([ds1, ds2])
        return _ok(
            {
                "dims": {k: int(v) for k, v in merged.sizes.items()},
                "data_vars": list(merged.data_vars),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_concat_arrays", description="Concatenate two arrays along a new dimension.")
def xr_concat_arrays(
    first_values: List[float],
    second_values: List[float],
    concat_dim: str = "sample",
    value_dim: str = "x",
) -> Dict[str, Any]:
    """
    Concatenate two 1D DataArray objects into a 2D DataArray.

    Parameters:
        first_values: First array values.
        second_values: Second array values.
        concat_dim: New concatenation dimension name.
        value_dim: Existing value dimension name.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        da1 = xr.DataArray(first_values, dims=[value_dim], name="v")
        da2 = xr.DataArray(second_values, dims=[value_dim], name="v")
        out = xr.concat([da1, da2], dim=concat_dim)
        return _ok(
            {
                "dims": list(out.dims),
                "shape": list(out.shape),
                "values": out.values.tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="xr_align_arrays", description="Align two arrays by coordinate labels.")
def xr_align_arrays(
    left_values: List[float],
    left_coords: List[int],
    right_values: List[float],
    right_coords: List[int],
    join: str = "outer",
    dim_name: str = "x",
) -> Dict[str, Any]:
    """
    Align two arrays by coordinates using xarray.align.

    Parameters:
        left_values: Left array values.
        left_coords: Left coordinate labels.
        right_values: Right array values.
        right_coords: Right coordinate labels.
        join: Join strategy ('outer', 'inner', 'left', 'right', 'exact', 'override').
        dim_name: Dimension/coordinate name.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        left = xr.DataArray(left_values, dims=[dim_name], coords={dim_name: left_coords})
        right = xr.DataArray(right_values, dims=[dim_name], coords={dim_name: right_coords})
        a_left, a_right = xr.align(left, right, join=join)
        return _ok(
            {
                "coords": a_left[dim_name].values.tolist(),
                "left": a_left.values.tolist(),
                "right": a_right.values.tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()