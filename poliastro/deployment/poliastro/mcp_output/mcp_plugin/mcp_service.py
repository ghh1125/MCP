import os
import sys
from typing import Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from poliastro.bodies import Body, Earth, Jupiter, Mars, Mercury, Neptune, Saturn, Sun, Uranus, Venus
from poliastro.earth.atmosphere.coesa62 import COESA62
from poliastro.earth.atmosphere.coesa76 import COESA76
from poliastro.ephem import Ephem
from poliastro.iod.izzo import lambert as izzo_lambert
from poliastro.maneuver import Maneuver
from poliastro.twobody.orbit import Orbit

import astropy.units as u
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time


mcp = FastMCP("poliastro_service")


def _body_from_name(name: str) -> Body:
    mapping = {
        "sun": Sun,
        "mercury": Mercury,
        "venus": Venus,
        "earth": Earth,
        "mars": Mars,
        "jupiter": Jupiter,
        "saturn": Saturn,
        "uranus": Uranus,
        "neptune": Neptune,
    }
    key = name.strip().lower()
    if key not in mapping:
        raise ValueError(f"Unsupported body '{name}'.")
    return mapping[key]


@mcp.tool(name="list_supported_bodies", description="List supported central body names.")
def list_supported_bodies() -> Dict[str, object]:
    """
    Return supported body names for orbit creation and ephemeris utilities.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        return {
            "success": True,
            "result": ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="create_orbit_from_vectors", description="Create an orbit from position and velocity vectors.")
def create_orbit_from_vectors(
    attractor: str,
    epoch_iso: str,
    r_km: List[float],
    v_km_s: List[float],
) -> Dict[str, object]:
    """
    Build an orbit from state vectors in km and km/s.

    Parameters:
        attractor: Name of central body.
        epoch_iso: ISO epoch string.
        r_km: Position vector [x, y, z] in km.
        v_km_s: Velocity vector [vx, vy, vz] in km/s.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        if len(r_km) != 3 or len(v_km_s) != 3:
            raise ValueError("r_km and v_km_s must have exactly 3 elements.")
        body = _body_from_name(attractor)
        epoch = Time(epoch_iso)
        orbit = Orbit.from_vectors(
            body,
            r_km * u.km,
            v_km_s * (u.km / u.s),
            epoch=epoch,
        )
        result = {
            "attractor": attractor,
            "epoch_iso": orbit.epoch.isot,
            "a_km": orbit.a.to_value(u.km),
            "ecc": float(orbit.ecc.value),
            "inc_deg": orbit.inc.to_value(u.deg),
            "raan_deg": orbit.raan.to_value(u.deg),
            "argp_deg": orbit.argp.to_value(u.deg),
            "nu_deg": orbit.nu.to_value(u.deg),
            "period_s": orbit.period.to_value(u.s) if orbit.ecc < 1 else None,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="propagate_orbit", description="Propagate an orbit by a time-of-flight in seconds.")
def propagate_orbit(
    attractor: str,
    epoch_iso: str,
    r_km: List[float],
    v_km_s: List[float],
    tof_seconds: float,
) -> Dict[str, object]:
    """
    Propagate an orbit from initial vectors over a given time-of-flight.

    Parameters:
        attractor: Name of central body.
        epoch_iso: Initial epoch as ISO string.
        r_km: Initial position vector [x, y, z] in km.
        v_km_s: Initial velocity vector [vx, vy, vz] in km/s.
        tof_seconds: Time of flight in seconds.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        if len(r_km) != 3 or len(v_km_s) != 3:
            raise ValueError("r_km and v_km_s must have exactly 3 elements.")
        body = _body_from_name(attractor)
        orbit0 = Orbit.from_vectors(body, r_km * u.km, v_km_s * (u.km / u.s), epoch=Time(epoch_iso))
        orbitf = orbit0.propagate(tof_seconds * u.s)
        result = {
            "final_epoch_iso": orbitf.epoch.isot,
            "r_km": orbitf.r.to_value(u.km).tolist(),
            "v_km_s": orbitf.v.to_value(u.km / u.s).tolist(),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="compute_hohmann_delta_v", description="Compute Hohmann transfer maneuvers between two circular radii.")
def compute_hohmann_delta_v(
    attractor: str,
    epoch_iso: str,
    r_initial_km: float,
    r_final_km: float,
) -> Dict[str, object]:
    """
    Compute Hohmann transfer burns and transfer time between circular coplanar orbits.

    Parameters:
        attractor: Name of central body.
        epoch_iso: Epoch as ISO string.
        r_initial_km: Initial circular orbit radius in km.
        r_final_km: Final circular orbit radius in km.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        body = _body_from_name(attractor)
        orbit_i = Orbit.circular(body, r_initial_km * u.km, epoch=Time(epoch_iso))
        maneuver = Maneuver.hohmann(orbit_i, r_final_km * u.km)
        impulses = maneuver.impulses
        dv1 = impulses[0][1].norm().to_value(u.km / u.s)
        dv2 = impulses[1][1].norm().to_value(u.km / u.s)
        total = dv1 + dv2
        tof_s = impulses[1][0].to_value(u.s)
        result = {
            "dv1_km_s": dv1,
            "dv2_km_s": dv2,
            "total_dv_km_s": total,
            "transfer_time_s": tof_s,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="solve_lambert_izzo", description="Solve Lambert problem using Izzo's algorithm.")
def solve_lambert_izzo(
    attractor: str,
    r1_km: List[float],
    r2_km: List[float],
    tof_seconds: float,
    num_revs: int = 0,
    prograde: bool = True,
    lowpath: bool = True,
) -> Dict[str, object]:
    """
    Compute transfer velocities for Lambert arc between two positions.

    Parameters:
        attractor: Central body name for gravitational parameter.
        r1_km: Initial position vector [x, y, z] in km.
        r2_km: Final position vector [x, y, z] in km.
        tof_seconds: Time of flight in seconds.
        num_revs: Number of revolutions.
        prograde: Prograde transfer flag.
        lowpath: Low-path transfer flag.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        if len(r1_km) != 3 or len(r2_km) != 3:
            raise ValueError("r1_km and r2_km must have exactly 3 elements.")
        body = _body_from_name(attractor)
        sols = list(
            izzo_lambert(
                body.k,
                r1_km * u.km,
                r2_km * u.km,
                tof_seconds * u.s,
                M=num_revs,
                prograde=prograde,
                lowpath=lowpath,
            )
        )
        result = [
            {
                "v1_km_s": v1.to_value(u.km / u.s).tolist(),
                "v2_km_s": v2.to_value(u.km / u.s).tolist(),
            }
            for v1, v2 in sols
        ]
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="planet_ephemeris", description="Get heliocentric ephemeris state for a solar system body.")
def planet_ephemeris(
    body_name: str,
    epoch_iso: str,
    ephemeris: Optional[str] = "builtin",
) -> Dict[str, object]:
    """
    Retrieve heliocentric position and velocity for a body at an epoch.

    Parameters:
        body_name: Solar system body name (e.g., 'earth', 'mars').
        epoch_iso: Epoch as ISO string.
        ephemeris: Astropy solar system ephemeris name.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        epoch = Time(epoch_iso)
        with solar_system_ephemeris.set(ephemeris):
            eph = Ephem.from_body(_body_from_name(body_name), epoch)
        r, v = eph.rv(epoch)
        result = {
            "epoch_iso": epoch.isot,
            "r_km": r.to_value(u.km).tolist(),
            "v_km_s": v.to_value(u.km / u.s).tolist(),
            "ephemeris": ephemeris,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="earth_atmosphere_properties", description="Compute Earth atmosphere properties from COESA models.")
def earth_atmosphere_properties(
    model: str,
    altitude_km: float,
) -> Dict[str, object]:
    """
    Compute atmospheric properties at a given altitude using COESA62 or COESA76.

    Parameters:
        model: Atmosphere model, one of 'coesa62' or 'coesa76'.
        altitude_km: Geometric altitude in km.

    Returns:
        dict: Standard result dictionary with success/result/error keys.
    """
    try:
        model_key = model.strip().lower()
        h = altitude_km * u.km

        if model_key == "coesa62":
            atm = COESA62()
        elif model_key == "coesa76":
            atm = COESA76()
        else:
            raise ValueError("model must be 'coesa62' or 'coesa76'.")

        T, p, rho = atm.properties(h)
        result = {
            "model": model_key,
            "altitude_km": altitude_km,
            "temperature_K": T.to_value(u.K),
            "pressure_Pa": p.to_value(u.Pa),
            "density_kg_m3": rho.to_value(u.kg / (u.m ** 3)),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()