import os
import sys
from typing import Dict, List, Optional

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("climlab_service")


def _ok(result):
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception):
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="climlab_version_info", description="Get version and basic availability information for climlab.")
def climlab_version_info() -> Dict:
    """
    Return basic package metadata.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        import climlab  # type: ignore

        return _ok(
            {
                "version": getattr(climlab, "__version__", "unknown"),
                "module": "climlab",
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="create_ebm_model", description="Create an Energy Balance Model (EBM) with configurable diffusion and grid.")
def create_ebm_model(num_lat: int = 90, D: float = 0.55, water_depth: float = 10.0) -> Dict:
    """
    Create a climlab EBM model instance and summarize key diagnostics.

    Args:
        num_lat: Number of latitude points.
        D: Diffusivity parameter for meridional heat transport.
        water_depth: Slab ocean water depth in meters.

    Returns:
        dict: Standard response dictionary with model summary.
    """
    try:
        from climlab.model.ebm import EBM  # type: ignore

        model = EBM(num_lat=num_lat, D=D, water_depth=water_depth)
        result = {
            "class": model.__class__.__name__,
            "num_lat": num_lat,
            "D": D,
            "water_depth": water_depth,
            "state_variables": list(model.state.keys()),
            "diagnostics": list(model.diagnostics.keys()),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="integrate_ebm", description="Integrate an EBM model forward in time and return global mean surface temperature.")
def integrate_ebm(num_lat: int = 90, years: float = 1.0, D: float = 0.55, water_depth: float = 10.0) -> Dict:
    """
    Run a climlab EBM simulation.

    Args:
        num_lat: Number of latitude points.
        years: Integration length in years.
        D: Diffusivity parameter.
        water_depth: Slab ocean water depth in meters.

    Returns:
        dict: Standard response dictionary with time-integrated summary.
    """
    try:
        import numpy as np  # type: ignore
        from climlab.model.ebm import EBM  # type: ignore

        model = EBM(num_lat=num_lat, D=D, water_depth=water_depth)
        model.integrate_years(years)

        ts = model.state.get("Ts")
        if ts is None:
            return _ok({"message": "Model integrated, but Ts state variable not found."})

        global_mean_ts = float(np.mean(ts))
        return _ok(
            {
                "years": years,
                "num_lat": num_lat,
                "global_mean_surface_temp": global_mean_ts,
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="compute_daily_insolation", description="Compute daily mean insolation for latitude/day with optional orbital parameters.")
def compute_daily_insolation(
    latitude: float,
    day_of_year: int,
    ecc: Optional[float] = None,
    long_peri: Optional[float] = None,
    obliquity: Optional[float] = None,
    solar_constant: float = 1365.2,
) -> Dict:
    """
    Compute daily insolation using climlab solar tools.

    Args:
        latitude: Latitude in degrees.
        day_of_year: Day of year (1-365/366).
        ecc: Orbital eccentricity (optional).
        long_peri: Longitude of perihelion in degrees (optional).
        obliquity: Obliquity in degrees (optional).
        solar_constant: Solar constant in W/m^2.

    Returns:
        dict: Standard response dictionary with insolation value(s).
    """
    try:
        from climlab.solar.insolation import daily_insolation  # type: ignore

        kwargs = {"S0": solar_constant}
        if ecc is not None:
            kwargs["ecc"] = ecc
        if long_peri is not None:
            kwargs["long_peri"] = long_peri
        if obliquity is not None:
            kwargs["obliquity"] = obliquity

        value = daily_insolation(lat=latitude, day=day_of_year, **kwargs)
        try:
            output = float(value)
        except Exception:
            output = str(value)

        return _ok(
            {
                "latitude": latitude,
                "day_of_year": day_of_year,
                "insolation": output,
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="compute_annual_mean_insolation_profile", description="Compute annual-mean insolation profile across latitude bands.")
def compute_annual_mean_insolation_profile(
    latitudes: List[float],
    days_per_year: int = 365,
    solar_constant: float = 1365.2,
) -> Dict:
    """
    Compute annual-mean insolation for a list of latitudes.

    Args:
        latitudes: List of latitude values in degrees.
        days_per_year: Number of days for averaging.
        solar_constant: Solar constant in W/m^2.

    Returns:
        dict: Standard response dictionary with latitude/insolation pairs.
    """
    try:
        import numpy as np  # type: ignore
        from climlab.solar.insolation import daily_insolation  # type: ignore

        days = np.arange(1, days_per_year + 1)
        profile = []
        for lat in latitudes:
            vals = daily_insolation(lat=lat, day=days, S0=solar_constant)
            mean_val = float(np.mean(vals))
            profile.append({"latitude": float(lat), "annual_mean_insolation": mean_val})
        return _ok({"profile": profile})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="blackbody_olr", description="Compute outgoing longwave radiation using Stefan-Boltzmann relation.")
def blackbody_olr(temperature: float, emissivity: float = 1.0) -> Dict:
    """
    Compute blackbody (or gray-body) outgoing longwave radiation.

    Args:
        temperature: Temperature in Kelvin.
        emissivity: Effective emissivity.

    Returns:
        dict: Standard response dictionary with OLR in W/m^2.
    """
    try:
        from climlab.radiation.boltzmann import Boltzmann  # type: ignore

        proc = Boltzmann(eps=emissivity)
        olr = float(proc._compute_emission(temperature))
        return _ok({"temperature": temperature, "emissivity": emissivity, "olr": olr})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="aplusbt_olr", description="Compute linearized OLR using A + B*T parameterization.")
def aplusbt_olr(temperature: float, A: float = 210.0, B: float = 2.0) -> Dict:
    """
    Compute outgoing longwave radiation using A+BT relation.

    Args:
        temperature: Temperature in Kelvin.
        A: Intercept parameter.
        B: Slope parameter.

    Returns:
        dict: Standard response dictionary with OLR.
    """
    try:
        from climlab.radiation.aplusbt import AplusBT  # type: ignore

        proc = AplusBT(A=A, B=B)
        olr = float(A + B * temperature)
        return _ok({"temperature": temperature, "A": A, "B": B, "olr": olr, "model": proc.__class__.__name__})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="moist_thermo_diagnostics", description="Compute core moist thermodynamic diagnostics from temperature and pressure.")
def moist_thermo_diagnostics(temperature: float, pressure: float) -> Dict:
    """
    Compute selected thermodynamic diagnostics.

    Args:
        temperature: Air temperature in Kelvin.
        pressure: Pressure in hPa.

    Returns:
        dict: Standard response dictionary with saturation vapor pressure and specific humidity estimates.
    """
    try:
        from climlab.utils.thermo import clausius_clapeyron, qsat  # type: ignore

        es = float(clausius_clapeyron(temperature))
        qsat_val = float(qsat(temperature, pressure))
        return _ok(
            {
                "temperature": temperature,
                "pressure_hPa": pressure,
                "saturation_vapor_pressure_Pa": es,
                "saturation_specific_humidity": qsat_val,
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="heat_capacity_ocean_slab", description="Compute areal heat capacity of an ocean slab.")
def heat_capacity_ocean_slab(water_depth: float) -> Dict:
    """
    Compute heat capacity for a slab ocean.

    Args:
        water_depth: Slab depth in meters.

    Returns:
        dict: Standard response dictionary with heat capacity in J m^-2 K^-1.
    """
    try:
        from climlab.utils.heat_capacity import ocean  # type: ignore

        cap = float(ocean(water_depth))
        return _ok({"water_depth": water_depth, "heat_capacity": cap})
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()