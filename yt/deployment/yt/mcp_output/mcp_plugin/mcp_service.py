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

mcp = FastMCP("yt_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": f"{type(exc).__name__}: {exc}"}


@mcp.tool(
    name="yt_get_version",
    description="Return yt package version information.",
)
def yt_get_version() -> Dict[str, Any]:
    """
    Get yt package version.

    Returns:
        Dict with success/result/error.
        result is the yt version string.
    """
    try:
        import yt

        return _ok(yt.__version__)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_load_dataset",
    description="Load a yt dataset from path and return high-level metadata.",
)
def yt_load_dataset(path: str, hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a dataset via yt.load.

    Parameters:
        path: Filesystem path to dataset.
        hint: Optional frontend hint passed to yt.load.

    Returns:
        Dict with success/result/error.
        result includes dataset type, geometry, domain dimensions, and current time.
    """
    try:
        import yt

        ds = yt.load(path, hint=hint) if hint else yt.load(path)
        result = {
            "dataset_type": str(getattr(ds, "dataset_type", "")),
            "geometry": str(getattr(ds, "geometry", "")),
            "domain_dimensions": [int(x) for x in ds.domain_dimensions.tolist()],
            "current_time": str(getattr(ds, "current_time", "")),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_list_fields",
    description="List available fields in a dataset.",
)
def yt_list_fields(path: str, include_derived: bool = True) -> Dict[str, Any]:
    """
    List dataset fields.

    Parameters:
        path: Dataset path.
        include_derived: Include derived fields if True.

    Returns:
        Dict with success/result/error.
        result is a list of field names in 'type,name' format.
    """
    try:
        import yt

        ds = yt.load(path)
        fields = ds.derived_field_list if include_derived else ds.field_list
        serialized = [f"{ftype},{fname}" for ftype, fname in fields]
        return _ok(serialized)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_compute_quantities",
    description="Compute core aggregate quantities on all_data.",
)
def yt_compute_quantities(
    path: str,
    field_type: str,
    field_name: str,
    weight_field_type: Optional[str] = None,
    weight_field_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute min, max, and weighted/unweighted mean for a field.

    Parameters:
        path: Dataset path.
        field_type: Field type, e.g. 'gas'.
        field_name: Field name, e.g. 'density'.
        weight_field_type: Optional weight field type.
        weight_field_name: Optional weight field name.

    Returns:
        Dict with success/result/error.
        result contains min, max, and mean as strings for unit-safe serialization.
    """
    try:
        import yt

        ds = yt.load(path)
        ad = ds.all_data()
        field = (field_type, field_name)

        min_v, max_v = ad.quantities.extrema(field)
        if weight_field_type and weight_field_name:
            mean_v = ad.quantities.weighted_average_quantity(
                field, (weight_field_type, weight_field_name)
            )
        else:
            mean_v = ad.quantities.weighted_average_quantity(field, None)

        return _ok({"min": str(min_v), "max": str(max_v), "mean": str(mean_v)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_create_slice_plot",
    description="Create and save a slice plot image.",
)
def yt_create_slice_plot(
    path: str,
    axis: str,
    field_type: str,
    field_name: str,
    output_path: str,
    width: Optional[float] = None,
    width_unit: str = "unitary",
) -> Dict[str, Any]:
    """
    Create a 2D slice plot and save it.

    Parameters:
        path: Dataset path.
        axis: Slice axis ('x', 'y', 'z').
        field_type: Field type.
        field_name: Field name.
        output_path: Output image path.
        width: Optional width value.
        width_unit: Unit for width if provided.

    Returns:
        Dict with success/result/error.
        result is the output path.
    """
    try:
        import yt

        ds = yt.load(path)
        field = (field_type, field_name)
        slc = yt.SlicePlot(ds, axis, field)
        if width is not None:
            slc.set_width((width, width_unit))
        slc.save(output_path)
        return _ok(output_path)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_create_projection_plot",
    description="Create and save a projection plot image.",
)
def yt_create_projection_plot(
    path: str,
    axis: str,
    field_type: str,
    field_name: str,
    output_path: str,
    method: str = "integrate",
    weight_field_type: Optional[str] = None,
    weight_field_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a projection plot and save it.

    Parameters:
        path: Dataset path.
        axis: Projection axis ('x', 'y', 'z').
        field_type: Field type.
        field_name: Field name.
        output_path: Output image path.
        method: Projection method.
        weight_field_type: Optional weight field type.
        weight_field_name: Optional weight field name.

    Returns:
        Dict with success/result/error.
        result is the output path.
    """
    try:
        import yt

        ds = yt.load(path)
        field = (field_type, field_name)
        weight_field = (
            (weight_field_type, weight_field_name)
            if weight_field_type and weight_field_name
            else None
        )
        prj = yt.ProjectionPlot(ds, axis, field, weight_field=weight_field, method=method)
        prj.save(output_path)
        return _ok(output_path)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="yt_dataset_stats",
    description="Return concise dataset summary statistics.",
)
def yt_dataset_stats(path: str) -> Dict[str, Any]:
    """
    Gather common dataset metadata and counts.

    Parameters:
        path: Dataset path.

    Returns:
        Dict with success/result/error.
        result includes dimensionality, field counts, and domain bounds.
    """
    try:
        import yt

        ds = yt.load(path)
        result = {
            "dimensionality": int(getattr(ds, "dimensionality", 0)),
            "field_count": int(len(getattr(ds, "field_list", []))),
            "derived_field_count": int(len(getattr(ds, "derived_field_list", []))),
            "domain_left_edge": [float(x) for x in ds.domain_left_edge.to_value()],
            "domain_right_edge": [float(x) for x in ds.domain_right_edge.to_value()],
            "domain_width": [float(x) for x in ds.domain_width.to_value()],
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()