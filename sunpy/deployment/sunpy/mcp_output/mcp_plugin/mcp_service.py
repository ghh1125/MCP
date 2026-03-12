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

import sunpy.coordinates as sunpy_coordinates
import sunpy.map as sunpy_map
import sunpy.net as sunpy_net
import sunpy.time as sunpy_time
import sunpy.timeseries as sunpy_timeseries

mcp = FastMCP("sunpy_mcp_service")


@mcp.tool(
    name="parse_time",
    description="Parse a time input into an Astropy Time object representation.",
)
def parse_time(time_input: str) -> dict[str, Any]:
    """
    Parse a user-provided time string into SunPy/Astropy time.

    Parameters:
        time_input: Time string or supported time format (e.g. ISO timestamp).

    Returns:
        Dictionary with:
        - success: bool indicating whether parsing succeeded
        - result: Parsed time as string on success, else None
        - error: Error message on failure, else None
    """
    try:
        parsed = sunpy_time.parse_time(time_input)
        return {"success": True, "result": str(parsed), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="create_time_range",
    description="Create a SunPy TimeRange from start and end timestamps.",
)
def create_time_range(start: str, end: str) -> dict[str, Any]:
    """
    Create a time range object.

    Parameters:
        start: Start timestamp string.
        end: End timestamp string.

    Returns:
        Dictionary with:
        - success: bool
        - result: TimeRange summary string on success, else None
        - error: Error message on failure, else None
    """
    try:
        tr = sunpy_time.TimeRange(start, end)
        return {"success": True, "result": str(tr), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="load_map",
    description="Load a SunPy map from a file path.",
)
def load_map(file_path: str) -> dict[str, Any]:
    """
    Load a map using sunpy.map.Map.

    Parameters:
        file_path: Path to a solar data file supported by SunPy.

    Returns:
        Dictionary with:
        - success: bool
        - result: Basic map metadata on success, else None
        - error: Error message on failure, else None
    """
    try:
        m = sunpy_map.Map(file_path)
        result = {
            "map_type": type(m).__name__,
            "instrument": str(getattr(m, "instrument", "")),
            "observatory": str(getattr(m, "observatory", "")),
            "date": str(getattr(m, "date", "")),
            "dimensions": str(getattr(m, "dimensions", "")),
            "wavelength": str(getattr(m, "wavelength", "")),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="map_subregion_info",
    description="Extract submap info using coordinate bounds in arcseconds.",
)
def map_subregion_info(
    file_path: str,
    bottom_left_tx_arcsec: float,
    bottom_left_ty_arcsec: float,
    top_right_tx_arcsec: float,
    top_right_ty_arcsec: float,
) -> dict[str, Any]:
    """
    Build a submap from helioprojective bounds and return summary information.

    Parameters:
        file_path: Input map file path.
        bottom_left_tx_arcsec: Bottom-left x (arcsec).
        bottom_left_ty_arcsec: Bottom-left y (arcsec).
        top_right_tx_arcsec: Top-right x (arcsec).
        top_right_ty_arcsec: Top-right y (arcsec).

    Returns:
        Dictionary with:
        - success: bool
        - result: Submap summary on success, else None
        - error: Error message on failure, else None
    """
    try:
        import astropy.units as u
        from astropy.coordinates import SkyCoord

        m = sunpy_map.Map(file_path)
        frame = m.coordinate_frame
        bl = SkyCoord(bottom_left_tx_arcsec * u.arcsec, bottom_left_ty_arcsec * u.arcsec, frame=frame)
        tr = SkyCoord(top_right_tx_arcsec * u.arcsec, top_right_ty_arcsec * u.arcsec, frame=frame)
        sub = m.submap(bl, top_right=tr)
        result = {
            "shape": str(sub.data.shape),
            "date": str(getattr(sub, "date", "")),
            "dimensions": str(getattr(sub, "dimensions", "")),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="search_fido",
    description="Search remote solar data using sunpy.net.Fido.",
)
def search_fido(
    start_time: str,
    end_time: str,
    instrument: str,
) -> dict[str, Any]:
    """
    Query SunPy Fido for data matching time range and instrument.

    Parameters:
        start_time: Query start time.
        end_time: Query end time.
        instrument: Instrument name (e.g. AIA, HMI, EIT).

    Returns:
        Dictionary with:
        - success: bool
        - result: Stringified query response on success, else None
        - error: Error message on failure, else None
    """
    try:
        from sunpy.net import attrs as a

        query = sunpy_net.Fido.search(
            a.Time(start_time, end_time),
            a.Instrument(instrument),
        )
        return {"success": True, "result": str(query), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="peek_timeseries",
    description="Load a SunPy TimeSeries and return core metadata.",
)
def peek_timeseries(file_path: str) -> dict[str, Any]:
    """
    Load a timeseries file and expose core descriptive information.

    Parameters:
        file_path: Path to a time series file.

    Returns:
        Dictionary with:
        - success: bool
        - result: TimeSeries summary on success, else None
        - error: Error message on failure, else None
    """
    try:
        ts = sunpy_timeseries.TimeSeries(file_path)
        result = {
            "timeseries_type": type(ts).__name__,
            "columns": list(ts.columns) if hasattr(ts, "columns") else [],
            "time_range": str(getattr(ts, "time_range", "")),
            "units": str(getattr(ts, "units", "")),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="solar_angular_radius",
    description="Compute apparent solar angular radius at a given time.",
)
def solar_angular_radius(time_input: str) -> dict[str, Any]:
    """
    Compute solar angular radius using sunpy.coordinates.sun.

    Parameters:
        time_input: Observation time.

    Returns:
        Dictionary with:
        - success: bool
        - result: Angular radius string on success, else None
        - error: Error message on failure, else None
    """
    try:
        from sunpy.coordinates import sun

        t = sunpy_time.parse_time(time_input)
        radius = sun.angular_radius(t)
        return {"success": True, "result": str(radius), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="earth_sun_distance",
    description="Compute Earth-Sun distance at a given time.",
)
def earth_sun_distance(time_input: str) -> dict[str, Any]:
    """
    Compute Earth-Sun distance via sunpy.coordinates.sun.

    Parameters:
        time_input: Observation time.

    Returns:
        Dictionary with:
        - success: bool
        - result: Distance string on success, else None
        - error: Error message on failure, else None
    """
    try:
        from sunpy.coordinates import sun

        t = sunpy_time.parse_time(time_input)
        distance = sun.earth_distance(t)
        return {"success": True, "result": str(distance), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()