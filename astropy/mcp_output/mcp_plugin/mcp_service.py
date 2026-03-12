import os
import sys
from typing import Optional, List, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("astropy_service")


@mcp.tool(
    name="fits_info",
    description="Summarize FITS HDU structure and metadata for a file.",
)
def fits_info(file_path: str, ext: Optional[int] = None) -> dict:
    """
    Summarize FITS file structure and key metadata.

    Parameters:
        file_path: Path to the FITS file.
        ext: Optional HDU index to inspect in detail.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.io import fits

        with fits.open(file_path) as hdul:
            if ext is None:
                result = [
                    {
                        "index": i,
                        "name": hdu.name,
                        "type": type(hdu).__name__,
                        "shape": getattr(getattr(hdu, "data", None), "shape", None),
                    }
                    for i, hdu in enumerate(hdul)
                ]
            else:
                hdu = hdul[ext]
                result = {
                    "index": ext,
                    "name": hdu.name,
                    "type": type(hdu).__name__,
                    "shape": getattr(getattr(hdu, "data", None), "shape", None),
                    "header_keys": list(hdu.header.keys()),
                }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="fits_header",
    description="Read FITS header cards for a selected HDU.",
)
def fits_header(file_path: str, ext: int = 0) -> dict:
    """
    Get FITS header as a plain dictionary-like mapping.

    Parameters:
        file_path: Path to the FITS file.
        ext: HDU index (default 0).

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.io import fits

        header = fits.getheader(file_path, ext=ext)
        result = {k: header[k] for k in header.keys()}
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="table_read",
    description="Read a tabular file with astropy.table.Table.",
)
def table_read(file_path: str, format_name: Optional[str] = None) -> dict:
    """
    Read a table and return schema and preview rows.

    Parameters:
        file_path: Path to table file.
        format_name: Optional table format name recognized by Astropy.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.table import Table

        table = Table.read(file_path, format=format_name) if format_name else Table.read(file_path)
        preview_count = min(10, len(table))
        preview = [{col: table[col][i].item() if hasattr(table[col][i], "item") else table[col][i] for col in table.colnames} for i in range(preview_count)]
        result = {
            "n_rows": len(table),
            "n_cols": len(table.colnames),
            "columns": table.colnames,
            "preview": preview,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="coordinates_separation",
    description="Compute angular separation between two sky coordinates.",
)
def coordinates_separation(
    ra1_deg: float,
    dec1_deg: float,
    ra2_deg: float,
    dec2_deg: float,
    frame: str = "icrs",
) -> dict:
    """
    Compute sky-coordinate separation in degrees.

    Parameters:
        ra1_deg: Right ascension of first coordinate in degrees.
        dec1_deg: Declination of first coordinate in degrees.
        ra2_deg: Right ascension of second coordinate in degrees.
        dec2_deg: Declination of second coordinate in degrees.
        frame: Coordinate frame name (default 'icrs').

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        c1 = SkyCoord(ra=ra1_deg * u.deg, dec=dec1_deg * u.deg, frame=frame)
        c2 = SkyCoord(ra=ra2_deg * u.deg, dec=dec2_deg * u.deg, frame=frame)
        sep = c1.separation(c2).deg
        return {"success": True, "result": {"separation_deg": sep}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="time_convert",
    description="Convert astronomical time between formats/scales.",
)
def time_convert(
    value: str,
    input_format: str = "isot",
    output_format: str = "jd",
    scale: str = "utc",
) -> dict:
    """
    Convert time using astropy.time.Time.

    Parameters:
        value: Input time value string.
        input_format: Astropy input format (e.g., isot, jd, mjd).
        output_format: Desired output format.
        scale: Time scale (e.g., utc, tt, tai).

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.time import Time

        t = Time(value, format=input_format, scale=scale)
        t.format = output_format
        out = t.value
        return {"success": True, "result": {"value": out, "format": output_format, "scale": t.scale}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="units_convert",
    description="Convert numeric values between Astropy units.",
)
def units_convert(value: float, from_unit: str, to_unit: str) -> dict:
    """
    Convert value from one unit to another.

    Parameters:
        value: Numeric value.
        from_unit: Source unit string.
        to_unit: Target unit string.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        q = value * u.Unit(from_unit)
        converted = q.to(u.Unit(to_unit)).value
        return {"success": True, "result": {"value": converted, "unit": to_unit}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="sigma_clip",
    description="Apply sigma clipping to numeric data.",
)
def sigma_clip(data: List[float], sigma: float = 3.0, maxiters: int = 5) -> dict:
    """
    Perform sigma clipping on a list of numbers.

    Parameters:
        data: Input numeric sequence.
        sigma: Sigma threshold.
        maxiters: Maximum number of clipping iterations.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import numpy as np
        from astropy.stats import sigma_clip as _sigma_clip

        arr = np.asarray(data, dtype=float)
        clipped = _sigma_clip(arr, sigma=sigma, maxiters=maxiters)
        mask = clipped.mask.tolist() if hasattr(clipped.mask, "tolist") else []
        filtered = clipped.compressed().tolist()
        return {"success": True, "result": {"filtered": filtered, "mask": mask}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="cosmology_distance_modulus",
    description="Compute distance modulus at redshift for a named cosmology realization.",
)
def cosmology_distance_modulus(z: float, cosmology_name: str = "Planck18") -> dict:
    """
    Compute distance modulus using astropy.cosmology realizations.

    Parameters:
        z: Redshift.
        cosmology_name: Cosmology realization name (e.g., Planck18, WMAP9).

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        from astropy.cosmology import realizations

        cosmo = getattr(realizations, cosmology_name)
        distmod = float(cosmo.distmod(z).value)
        return {"success": True, "result": {"distmod_mag": distmod, "cosmology": cosmology_name}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()