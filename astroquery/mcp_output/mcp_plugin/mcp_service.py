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
from astroquery.simbad.core import SimbadClass
from astroquery.vizier.core import VizierClass
from astroquery.mast.observations import ObservationsClass
from astroquery.gaia.core import GaiaClass
from astroquery.sdss.core import SDSSClass
from astroquery.jplhorizons.core import HorizonsClass

mcp = FastMCP("astroquery_mcp_service")


def _to_serializable(obj: Any, max_rows: int = 200) -> Any:
    try:
        from astropy.table import Table
        if isinstance(obj, Table):
            rows: List[Dict[str, Any]] = []
            names = list(obj.colnames)
            limit = min(len(obj), max_rows)
            for i in range(limit):
                row = {}
                for name in names:
                    v = obj[name][i]
                    try:
                        row[name] = v.item() if hasattr(v, "item") else str(v)
                    except Exception:
                        row[name] = str(v)
                rows.append(row)
            return rows
    except Exception:
        pass

    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_serializable(v, max_rows=max_rows) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v, max_rows=max_rows) for v in obj]
    return str(obj)


@mcp.tool(name="simbad_query_object", description="Query SIMBAD for a single object by identifier.")
def simbad_query_object(object_name: str) -> Dict[str, Any]:
    """
    Query SIMBAD object metadata.

    Parameters:
        object_name: Astronomical object identifier (e.g., 'M31', 'Betelgeuse').

    Returns:
        Dictionary with success/result/error.
    """
    try:
        simbad = SimbadClass()
        result = simbad.query_object(object_name)
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="simbad_query_region", description="Query SIMBAD objects around sky coordinates.")
def simbad_query_region(ra_deg: float, dec_deg: float, radius_deg: float) -> Dict[str, Any]:
    """
    Query SIMBAD around a sky region.

    Parameters:
        ra_deg: Right ascension in degrees.
        dec_deg: Declination in degrees.
        radius_deg: Search radius in degrees.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        simbad = SimbadClass()
        coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame="icrs")
        result = simbad.query_region(coord, radius=radius_deg * u.deg)
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="vizier_query_object", description="Query VizieR catalogs for an object name.")
def vizier_query_object(object_name: str, row_limit: int = 50, catalog: Optional[str] = None) -> Dict[str, Any]:
    """
    Query VizieR by object identifier.

    Parameters:
        object_name: Target object identifier.
        row_limit: Maximum rows per returned table.
        catalog: Optional catalog identifier/filter.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        viz = VizierClass(row_limit=row_limit)
        if catalog:
            tables = viz.query_object(object_name, catalog=catalog)
        else:
            tables = viz.query_object(object_name)
        result = [_to_serializable(t) for t in tables] if tables is not None else []
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="vizier_query_region", description="Query VizieR catalogs in a sky region.")
def vizier_query_region(
    ra_deg: float,
    dec_deg: float,
    radius_deg: float,
    row_limit: int = 50,
    catalog: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query VizieR by sky cone.

    Parameters:
        ra_deg: Right ascension in degrees.
        dec_deg: Declination in degrees.
        radius_deg: Search radius in degrees.
        row_limit: Maximum rows per returned table.
        catalog: Optional catalog identifier/filter.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        viz = VizierClass(row_limit=row_limit)
        coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame="icrs")
        if catalog:
            tables = viz.query_region(coord, radius=radius_deg * u.deg, catalog=catalog)
        else:
            tables = viz.query_region(coord, radius=radius_deg * u.deg)
        result = [_to_serializable(t) for t in tables] if tables is not None else []
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="mast_query_object", description="Query MAST observations for an object.")
def mast_query_object(object_name: str, radius_deg: float = 0.1) -> Dict[str, Any]:
    """
    Query MAST observations by object name.

    Parameters:
        object_name: Target object identifier.
        radius_deg: Cone radius in degrees.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        from astropy.coordinates import Angle
        import astropy.units as u

        obs = ObservationsClass()
        radius = Angle(radius_deg, unit=u.deg)
        result = obs.query_object(object_name, radius=radius)
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="mast_query_criteria", description="Query MAST observations with basic criteria.")
def mast_query_criteria(
    obs_collection: Optional[str] = None,
    dataproduct_type: Optional[str] = None,
    target_name: Optional[str] = None,
    intent_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query MAST with selected criteria fields.

    Parameters:
        obs_collection: Mission/collection (e.g., 'HST', 'TESS').
        dataproduct_type: Product type (e.g., 'image', 'spectrum').
        target_name: Target name filter.
        intent_type: Intent type filter.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        obs = ObservationsClass()
        kwargs: Dict[str, Any] = {}
        if obs_collection is not None:
            kwargs["obs_collection"] = obs_collection
        if dataproduct_type is not None:
            kwargs["dataproduct_type"] = dataproduct_type
        if target_name is not None:
            kwargs["target_name"] = target_name
        if intent_type is not None:
            kwargs["intentType"] = intent_type
        result = obs.query_criteria(**kwargs)
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="gaia_launch_job", description="Run a synchronous ADQL query on Gaia archive.")
def gaia_launch_job(adql_query: str) -> Dict[str, Any]:
    """
    Execute synchronous ADQL query against Gaia TAP.

    Parameters:
        adql_query: ADQL SQL-like query string.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        gaia = GaiaClass()
        job = gaia.launch_job(adql_query)
        table = job.get_results()
        return {"success": True, "result": _to_serializable(table), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="sdss_query_region", description="Query SDSS around sky coordinates.")
def sdss_query_region(ra_deg: float, dec_deg: float, radius_arcmin: float = 2.0) -> Dict[str, Any]:
    """
    Cone-search SDSS around coordinates.

    Parameters:
        ra_deg: Right ascension in degrees.
        dec_deg: Declination in degrees.
        radius_arcmin: Search radius in arcminutes.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        sdss = SDSSClass()
        coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame="icrs")
        result = sdss.query_region(coord, radius=radius_arcmin * u.arcmin)
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="horizons_ephemerides", description="Fetch JPL Horizons ephemerides for a target.")
def horizons_ephemerides(
    target_id: str,
    location: str = "500",
    epochs_start: Optional[str] = None,
    epochs_stop: Optional[str] = None,
    epochs_step: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve ephemerides from JPL Horizons.

    Parameters:
        target_id: Target identifier (e.g., 'Ceres', '499').
        location: Observer location code (default geocenter '500').
        epochs_start: Optional start datetime string (e.g., '2025-01-01').
        epochs_stop: Optional stop datetime string.
        epochs_step: Optional step string (e.g., '1d').

    Returns:
        Dictionary with success/result/error.
    """
    try:
        epochs: Optional[Dict[str, str]] = None
        if epochs_start and epochs_stop and epochs_step:
            epochs = {"start": epochs_start, "stop": epochs_stop, "step": epochs_step}

        obj = HorizonsClass(id=target_id, location=location, epochs=epochs)
        result = obj.ephemerides()
        return {"success": True, "result": _to_serializable(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp

if __name__ == "__main__":
    mcp.run()