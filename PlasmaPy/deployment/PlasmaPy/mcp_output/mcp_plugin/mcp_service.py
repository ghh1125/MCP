import os
import sys
from typing import Dict, Any, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from plasmapy.particles import Particle
from plasmapy.formulary.frequencies import plasma_frequency, gyrofrequency
from plasmapy.formulary.lengths import Debye_length
from plasmapy.formulary.speeds import thermal_speed
from plasmapy.formulary.collisions.frequencies import collision_frequency


mcp = FastMCP("plasmapy_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="particle_summary",
    description="Create a PlasmaPy Particle and return key particle properties.",
)
def particle_summary(symbol: str, mass_numb: int | None = None, Z: int | None = None) -> Dict[str, Any]:
    """
    Create a particle object and return basic physical properties.

    Parameters:
        symbol: Particle symbol (e.g., 'e-', 'p+', 'He-4 1+').
        mass_numb: Optional mass number override.
        Z: Optional charge number override.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        kwargs: Dict[str, Any] = {}
        if mass_numb is not None:
            kwargs["mass_numb"] = mass_numb
        if Z is not None:
            kwargs["Z"] = Z

        p = Particle(symbol, **kwargs)
        result = {
            "symbol": p.symbol,
            "mass_kg": float(p.mass.si.value),
            "charge_c": float(p.charge.si.value),
            "charge_number": int(p.charge_number),
            "is_ion": bool(p.is_ion),
            "is_electron": bool(p.is_electron),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="compute_plasma_frequency",
    description="Compute plasma frequency for a species and number density.",
)
def compute_plasma_frequency(density_m3: float, particle: str, to_hz: bool = True) -> Dict[str, Any]:
    """
    Compute plasma frequency.

    Parameters:
        density_m3: Number density in m^-3.
        particle: Particle species string (e.g., 'e-', 'p+').
        to_hz: If True, return frequency in Hz; otherwise angular frequency in rad/s.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        omega_p = plasma_frequency(n=density_m3 * u.m**-3, particle=particle)
        if to_hz:
            value = omega_p.to(u.Hz, equivalencies=[(u.cy / u.s, u.Hz)]).value
            unit = "Hz"
        else:
            value = omega_p.to(u.rad / u.s).value
            unit = "rad/s"
        return _ok({"value": float(value), "unit": unit})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="compute_gyrofrequency",
    description="Compute cyclotron/gyrofrequency for a charged species in magnetic field.",
)
def compute_gyrofrequency(B_tesla: float, particle: str, signed: bool = False) -> Dict[str, Any]:
    """
    Compute gyrofrequency.

    Parameters:
        B_tesla: Magnetic field magnitude in tesla.
        particle: Particle species string.
        signed: If True, preserve sign by charge; else return magnitude.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        omega_c = gyrofrequency(B=B_tesla * u.T, particle=particle, signed=signed)
        return _ok({"value": float(omega_c.to(u.rad / u.s).value), "unit": "rad/s"})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="compute_debye_length",
    description="Compute Debye length from electron temperature and density.",
)
def compute_debye_length(temperature_K: float, density_m3: float) -> Dict[str, Any]:
    """
    Compute Debye length.

    Parameters:
        temperature_K: Plasma temperature in kelvin.
        density_m3: Electron number density in m^-3.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        ld = Debye_length(T_e=temperature_K * u.K, n_e=density_m3 * u.m**-3)
        return _ok({"value": float(ld.to(u.m).value), "unit": "m"})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="compute_thermal_speed",
    description="Compute thermal speed for a species at a given temperature.",
)
def compute_thermal_speed(
    temperature_K: float,
    particle: str,
    method: str = "most_probable",
    dimensions: int = 3,
) -> Dict[str, Any]:
    """
    Compute thermal speed.

    Parameters:
        temperature_K: Temperature in kelvin.
        particle: Particle species string.
        method: Thermal speed definition ('most_probable', 'rms', or 'mean_magnitude').
        dimensions: Number of dimensions (commonly 1, 2, or 3).

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        vth = thermal_speed(
            T=temperature_K * u.K,
            particle=particle,
            method=method,
            ndim=dimensions,
        )
        return _ok({"value": float(vth.to(u.m / u.s).value), "unit": "m/s"})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="compute_collision_frequency",
    description="Compute Coulomb collision frequency between test and field particles.",
)
def compute_collision_frequency(
    T_K: float,
    n_m3: float,
    test_particle: str,
    field_particle: str,
    coulomb_log: float = 10.0,
    V_m_per_s: float = 0.0,
) -> Dict[str, Any]:
    """
    Compute classical Coulomb collision frequency.

    Parameters:
        T_K: Temperature in kelvin.
        n_m3: Number density in m^-3.
        test_particle: Test particle species.
        field_particle: Field particle species.
        coulomb_log: Coulomb logarithm value.
        V_m_per_s: Relative drift speed in m/s.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        nu = collision_frequency(
            T=T_K * u.K,
            n=n_m3 * u.m**-3,
            test_particle=test_particle,
            field_particle=field_particle,
            V=V_m_per_s * u.m / u.s,
            coulomb_log=coulomb_log,
        )
        return _ok({"value": float(nu.to(1 / u.s).value), "unit": "1/s"})
    except Exception as exc:
        return _err(exc)


@mcp.tool(
    name="quick_plasma_diagnostics",
    description="Run a compact set of plasma diagnostics from common input parameters.",
)
def quick_plasma_diagnostics(
    electron_density_m3: float,
    electron_temperature_K: float,
    magnetic_field_T: float,
) -> Dict[str, Any]:
    """
    Compute a bundled set of common plasma diagnostics for electrons.

    Parameters:
        electron_density_m3: Electron density in m^-3.
        electron_temperature_K: Electron temperature in kelvin.
        magnetic_field_T: Magnetic field in tesla.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        import astropy.units as u

        wp = plasma_frequency(n=electron_density_m3 * u.m**-3, particle="e-")
        wc = gyrofrequency(B=magnetic_field_T * u.T, particle="e-")
        ld = Debye_length(T_e=electron_temperature_K * u.K, n_e=electron_density_m3 * u.m**-3)
        vth = thermal_speed(T=electron_temperature_K * u.K, particle="e-", method="most_probable", ndim=3)

        result = {
            "electron_plasma_frequency_rad_s": float(wp.to(u.rad / u.s).value),
            "electron_gyrofrequency_rad_s": float(wc.to(u.rad / u.s).value),
            "debye_length_m": float(ld.to(u.m).value),
            "electron_thermal_speed_m_s": float(vth.to(u.m / u.s).value),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()