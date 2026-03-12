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
from metpy.calc import (
    advection,
    cape_cin,
    dewpoint_from_relative_humidity,
    equivalent_potential_temperature,
    lcl,
    potential_temperature,
    relative_humidity_from_dewpoint,
    vorticity,
    wind_speed,
)
from metpy.constants import g
from metpy.io import parse_metar_file
from metpy.units import units

mcp = FastMCP("metpy_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="calc_wind_speed", description="Compute wind speed from u and v wind components.")
def calc_wind_speed(u_ms: float, v_ms: float) -> Dict[str, Any]:
    """
    Calculate scalar wind speed.

    Parameters:
        u_ms: Zonal wind component in meters per second.
        v_ms: Meridional wind component in meters per second.

    Returns:
        Dictionary with success/result/error where result is wind speed in m/s.
    """
    try:
        ws = wind_speed(u_ms * units("m/s"), v_ms * units("m/s"))
        return _ok(float(ws.to("m/s").magnitude))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_potential_temperature", description="Compute potential temperature from pressure and temperature.")
def calc_potential_temperature(pressure_hpa: float, temperature_c: float) -> Dict[str, Any]:
    """
    Calculate potential temperature.

    Parameters:
        pressure_hpa: Air pressure in hPa.
        temperature_c: Air temperature in degrees Celsius.

    Returns:
        Dictionary with success/result/error where result is theta in Kelvin.
    """
    try:
        theta = potential_temperature(pressure_hpa * units.hPa, temperature_c * units.degC)
        return _ok(float(theta.to("kelvin").magnitude))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_lcl", description="Compute lifting condensation level pressure and temperature.")
def calc_lcl(
    pressure_hpa: float, temperature_c: float, dewpoint_c: float
) -> Dict[str, Any]:
    """
    Calculate LCL pressure and temperature.

    Parameters:
        pressure_hpa: Parcel pressure in hPa.
        temperature_c: Parcel temperature in degrees Celsius.
        dewpoint_c: Parcel dewpoint in degrees Celsius.

    Returns:
        Dictionary with success/result/error where result contains lcl_pressure_hpa and lcl_temperature_c.
    """
    try:
        lcl_p, lcl_t = lcl(
            pressure_hpa * units.hPa,
            temperature_c * units.degC,
            dewpoint_c * units.degC,
        )
        return _ok(
            {
                "lcl_pressure_hpa": float(lcl_p.to("hPa").magnitude),
                "lcl_temperature_c": float(lcl_t.to("degC").magnitude),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_rh_from_dewpoint", description="Compute relative humidity from temperature and dewpoint.")
def calc_rh_from_dewpoint(temperature_c: float, dewpoint_c: float) -> Dict[str, Any]:
    """
    Calculate relative humidity.

    Parameters:
        temperature_c: Air temperature in degrees Celsius.
        dewpoint_c: Dewpoint temperature in degrees Celsius.

    Returns:
        Dictionary with success/result/error where result is relative humidity as a fraction [0, 1].
    """
    try:
        rh = relative_humidity_from_dewpoint(
            temperature_c * units.degC, dewpoint_c * units.degC
        )
        return _ok(float(rh.to("dimensionless").magnitude))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_dewpoint_from_rh", description="Compute dewpoint from air temperature and relative humidity.")
def calc_dewpoint_from_rh(temperature_c: float, relative_humidity: float) -> Dict[str, Any]:
    """
    Calculate dewpoint from temperature and RH.

    Parameters:
        temperature_c: Air temperature in degrees Celsius.
        relative_humidity: Relative humidity as fraction [0, 1].

    Returns:
        Dictionary with success/result/error where result is dewpoint in degrees Celsius.
    """
    try:
        td = dewpoint_from_relative_humidity(
            temperature_c * units.degC, relative_humidity * units.dimensionless
        )
        return _ok(float(td.to("degC").magnitude))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_equivalent_potential_temperature", description="Compute equivalent potential temperature.")
def calc_equivalent_potential_temperature(
    pressure_hpa: float, temperature_c: float, dewpoint_c: float
) -> Dict[str, Any]:
    """
    Calculate equivalent potential temperature.

    Parameters:
        pressure_hpa: Air pressure in hPa.
        temperature_c: Air temperature in degrees Celsius.
        dewpoint_c: Dewpoint temperature in degrees Celsius.

    Returns:
        Dictionary with success/result/error where result is theta-e in Kelvin.
    """
    try:
        theta_e = equivalent_potential_temperature(
            pressure_hpa * units.hPa, temperature_c * units.degC, dewpoint_c * units.degC
        )
        return _ok(float(theta_e.to("kelvin").magnitude))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_cape_cin", description="Compute CAPE and CIN from vertical profiles.")
def calc_cape_cin(
    pressure_hpa: List[float], temperature_c: List[float], dewpoint_c: List[float]
) -> Dict[str, Any]:
    """
    Calculate CAPE and CIN for a sounding profile.

    Parameters:
        pressure_hpa: Pressure profile in hPa.
        temperature_c: Temperature profile in degrees Celsius.
        dewpoint_c: Dewpoint profile in degrees Celsius.

    Returns:
        Dictionary with success/result/error where result contains cape_j_per_kg and cin_j_per_kg.
    """
    try:
        p = pressure_hpa * units.hPa
        t = temperature_c * units.degC
        td = dewpoint_c * units.degC
        cape, cin = cape_cin(p, t, td)
        return _ok(
            {
                "cape_j_per_kg": float(cape.to("J/kg").magnitude),
                "cin_j_per_kg": float(cin.to("J/kg").magnitude),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_vertical_vorticity", description="Compute vertical vorticity from wind and grid spacing.")
def calc_vertical_vorticity(
    u_ms: List[List[float]],
    v_ms: List[List[float]],
    dx_m: float,
    dy_m: float,
) -> Dict[str, Any]:
    """
    Calculate vertical vorticity on a regular grid.

    Parameters:
        u_ms: 2D zonal wind field in m/s.
        v_ms: 2D meridional wind field in m/s.
        dx_m: Grid spacing in x direction (meters).
        dy_m: Grid spacing in y direction (meters).

    Returns:
        Dictionary with success/result/error where result is a 2D list of vorticity in 1/s.
    """
    try:
        import numpy as np

        u = np.array(u_ms) * units("m/s")
        v = np.array(v_ms) * units("m/s")
        zeta = vorticity(u, v, dx=dx_m * units.meter, dy=dy_m * units.meter)
        return _ok(zeta.to("1/s").magnitude.tolist())
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="calc_advection_scalar", description="Compute scalar advection using wind and scalar field gradients.")
def calc_advection_scalar(
    scalar_field: List[List[float]],
    u_ms: List[List[float]],
    v_ms: List[List[float]],
    dx_m: float,
    dy_m: float,
) -> Dict[str, Any]:
    """
    Calculate horizontal advection of a scalar field.

    Parameters:
        scalar_field: 2D scalar field (unitless values).
        u_ms: 2D zonal wind field in m/s.
        v_ms: 2D meridional wind field in m/s.
        dx_m: Grid spacing in x direction in meters.
        dy_m: Grid spacing in y direction in meters.

    Returns:
        Dictionary with success/result/error where result is 2D advection field in scalar units per second.
    """
    try:
        import numpy as np

        s = np.array(scalar_field) * units.dimensionless
        u = np.array(u_ms) * units("m/s")
        v = np.array(v_ms) * units("m/s")
        adv = advection(s, u=u, v=v, dx=dx_m * units.meter, dy=dy_m * units.meter)
        return _ok(adv.to("1/s").magnitude.tolist())
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="parse_metar_text", description="Parse METAR text and return selected station records.")
def parse_metar_text(metar_text: str, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
    """
    Parse raw METAR text content.

    Parameters:
        metar_text: Raw METAR bulletin text with one report per line.
        year: Optional year for parsing date context.
        month: Optional month for parsing date context.

    Returns:
        Dictionary with success/result/error where result is a list of parsed records.
    """
    try:
        import io

        kwargs: Dict[str, Any] = {}
        if year is not None:
            kwargs["year"] = year
        if month is not None:
            kwargs["month"] = month

        df = parse_metar_file(io.StringIO(metar_text), **kwargs)
        records = df.head(100).to_dict(orient="records")
        return _ok(records)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="get_gravity_constant", description="Return standard gravity constant from MetPy constants.")
def get_gravity_constant() -> Dict[str, Any]:
    """
    Fetch standard gravitational acceleration.

    Parameters:
        None.

    Returns:
        Dictionary with success/result/error where result is gravity in m/s^2.
    """
    try:
        return _ok(float(g.to("m/s^2").magnitude))
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp