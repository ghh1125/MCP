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

import lightkurve as lk
from lightkurve.correctors import SFFCorrector
from lightkurve.io.read import read as lk_read

mcp = FastMCP("lightkurve_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="search_lightcurve", description="Search for light curve products by target and mission.")
def search_lightcurve(
    target: str,
    mission: Optional[str] = None,
    author: Optional[str] = None,
    cadence: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search available light curve files.

    Parameters:
        target: Target name, TIC/EPIC/KIC, or coordinates string.
        mission: Optional mission filter (e.g., "TESS", "Kepler", "K2").
        author: Optional author/pipeline filter.
        cadence: Optional cadence filter.
        limit: Maximum number of rows to return.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        res = lk.search_lightcurve(target=target, mission=mission, author=author, cadence=cadence)
        n = max(0, int(limit))
        table = res.table[:n]
        rows: List[Dict[str, Any]] = []
        for row in table:
            rows.append({col: str(row[col]) for col in table.colnames})
        return _ok(rows)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="search_targetpixelfile", description="Search for target pixel file products by target and mission.")
def search_targetpixelfile(
    target: str,
    mission: Optional[str] = None,
    author: Optional[str] = None,
    cadence: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search available target pixel files.

    Parameters:
        target: Target name, TIC/EPIC/KIC, or coordinates string.
        mission: Optional mission filter.
        author: Optional author/pipeline filter.
        cadence: Optional cadence filter.
        limit: Maximum number of rows to return.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        res = lk.search_targetpixelfile(target=target, mission=mission, author=author, cadence=cadence)
        n = max(0, int(limit))
        table = res.table[:n]
        rows: List[Dict[str, Any]] = []
        for row in table:
            rows.append({col: str(row[col]) for col in table.colnames})
        return _ok(rows)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="download_lightcurve", description="Download a single light curve and return a compact summary.")
def download_lightcurve(
    target: str,
    mission: Optional[str] = None,
    author: Optional[str] = None,
    cadence: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Download one light curve product and summarize key metadata.

    Parameters:
        target: Target query string.
        mission: Optional mission filter.
        author: Optional author filter.
        cadence: Optional cadence filter.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        sr = lk.search_lightcurve(target=target, mission=mission, author=author, cadence=cadence)
        lc = sr.download()
        if lc is None:
            return _err("No light curve download result.")
        result = {
            "label": str(getattr(lc, "label", "")),
            "mission": str(getattr(lc, "mission", "")),
            "n_points": int(len(lc.time)),
            "columns": [str(c) for c in lc.colnames],
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="flatten_lightcurve", description="Download and flatten a light curve using Savitzky-Golay detrending.")
def flatten_lightcurve(
    target: str,
    mission: Optional[str] = None,
    author: Optional[str] = None,
    cadence: Optional[str] = None,
    window_length: int = 101,
    polyorder: int = 2,
) -> Dict[str, Any]:
    """
    Flatten a downloaded light curve and return summary statistics.

    Parameters:
        target: Target query string.
        mission: Optional mission filter.
        author: Optional author filter.
        cadence: Optional cadence filter.
        window_length: Smoothing window length.
        polyorder: Polynomial order for filter.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        lc = lk.search_lightcurve(target=target, mission=mission, author=author, cadence=cadence).download()
        if lc is None:
            return _err("No light curve found for flattening.")
        flc = lc.flatten(window_length=window_length, polyorder=polyorder)
        result = {
            "label": str(getattr(flc, "label", "")),
            "n_points": int(len(flc.time)),
            "flux_median": float(flc.flux.value.mean()) if hasattr(flc.flux, "value") else float(flc.flux.mean()),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="estimate_period_bls", description="Estimate transit period using Box Least Squares periodogram.")
def estimate_period_bls(
    target: str,
    period_min: float = 0.5,
    period_max: float = 20.0,
    mission: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a BLS periodogram and return best period metrics.

    Parameters:
        target: Target query string.
        period_min: Minimum period in days.
        period_max: Maximum period in days.
        mission: Optional mission filter.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        lc = lk.search_lightcurve(target=target, mission=mission).download()
        if lc is None:
            return _err("No light curve found for period search.")
        clean = lc.remove_nans().normalize()
        bls = clean.to_periodogram(method="bls", period=[period_min, period_max])
        result = {
            "period_at_max_power": float(bls.period_at_max_power.value),
            "max_power": float(bls.max_power),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="apply_sff_correction", description="Apply SFF correction to a downloaded target pixel file light curve.")
def apply_sff_correction(
    target: str,
    mission: Optional[str] = None,
    aperture_mask: str = "pipeline",
    windows: int = 10,
) -> Dict[str, Any]:
    """
    Run SFF systematics correction on a light curve extracted from a TPF.

    Parameters:
        target: Target query string.
        mission: Optional mission filter.
        aperture_mask: Aperture mask passed to to_lightcurve().
        windows: Number of windows for SFF correction.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        tpf = lk.search_targetpixelfile(target=target, mission=mission).download()
        if tpf is None:
            return _err("No target pixel file found.")
        lc = tpf.to_lightcurve(aperture_mask=aperture_mask).remove_nans()
        corr = SFFCorrector(lc)
        corrected = corr.correct(windows=windows)
        result = {
            "n_points": int(len(corrected.time)),
            "label": str(getattr(corrected, "label", "")),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="read_local_file", description="Read a local FITS/LC/TPF file using lightkurve.io.read and summarize object.")
def read_local_file(file_path: str) -> Dict[str, Any]:
    """
    Read a local lightkurve-compatible file and return object summary.

    Parameters:
        file_path: Path to local file.

    Returns:
        Dictionary with success, result, error.
    """
    try:
        obj = lk_read(file_path)
        result = {
            "type": obj.__class__.__name__,
            "has_time": bool(hasattr(obj, "time")),
            "length": int(len(obj.time)) if hasattr(obj, "time") else None,
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp