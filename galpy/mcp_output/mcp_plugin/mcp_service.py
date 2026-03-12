import os
import sys
from typing import Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

try:
    import galpy
    from galpy.orbit import Orbit
    from galpy import potential as gp
    from galpy import actionAngle as gaa
    from galpy import df as gdf
except Exception as import_error:
    galpy = None
    Orbit = None
    gp = None
    gaa = None
    gdf = None
    _IMPORT_ERROR = str(import_error)
else:
    _IMPORT_ERROR = None

mcp = FastMCP("galpy_service")


def _ok(result):
    return {"success": True, "result": result, "error": None}


def _err(message: str):
    return {"success": False, "result": None, "error": message}


def _ensure_imports():
    if _IMPORT_ERROR is not None:
        return False, f"Failed to import galpy modules: {_IMPORT_ERROR}"
    return True, None


@mcp.tool(name="galpy_version", description="Get installed galpy version.")
def galpy_version() -> dict:
    """
    Return galpy package version.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)
    return _ok(getattr(galpy, "__version__", "unknown"))


@mcp.tool(name="list_common_potentials", description="List commonly used galpy potential classes.")
def list_common_potentials() -> dict:
    """
    List core potential model class names available in galpy.potential.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    candidates = [
        "MiyamotoNagaiPotential",
        "NFWPotential",
        "HernquistPotential",
        "PlummerPotential",
        "LogarithmicHaloPotential",
        "IsochronePotential",
        "PowerSphericalPotential",
        "DehnenBarPotential",
        "SpiralArmsPotential",
        "MWPotential2014",
    ]
    available = [name for name in candidates if hasattr(gp, name)]
    return _ok(available)


@mcp.tool(name="evaluate_potential", description="Evaluate a galpy potential at (R, z, phi, t).")
def evaluate_potential(
    potential_name: str,
    R: float,
    z: float = 0.0,
    phi: float = 0.0,
    t: float = 0.0,
    amp: float = 1.0,
) -> dict:
    """
    Evaluate potential value for a selected galpy potential class.

    Parameters:
        potential_name (str): Name of potential class in galpy.potential.
        R (float): Cylindrical radius.
        z (float): Vertical coordinate.
        phi (float): Azimuth.
        t (float): Time.
        amp (float): Potential amplitude parameter where supported.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    if not hasattr(gp, potential_name):
        return _err(f"Unknown potential: {potential_name}")

    try:
        pot_cls = getattr(gp, potential_name)
        try:
            pot = pot_cls(amp=amp)
        except TypeError:
            pot = pot_cls()
        value = pot(R, z, phi=phi, t=t)
        return _ok(float(value))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="evaluate_forces", description="Compute radial and vertical forces for a galpy potential.")
def evaluate_forces(
    potential_name: str,
    R: float,
    z: float = 0.0,
    phi: float = 0.0,
    t: float = 0.0,
    amp: float = 1.0,
) -> dict:
    """
    Compute R-force and z-force for a selected galpy potential.

    Parameters:
        potential_name (str): Name of potential class in galpy.potential.
        R (float): Cylindrical radius.
        z (float): Vertical coordinate.
        phi (float): Azimuth.
        t (float): Time.
        amp (float): Potential amplitude parameter where supported.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    if not hasattr(gp, potential_name):
        return _err(f"Unknown potential: {potential_name}")

    try:
        pot_cls = getattr(gp, potential_name)
        try:
            pot = pot_cls(amp=amp)
        except TypeError:
            pot = pot_cls()
        rforce = pot.Rforce(R, z, phi=phi, t=t)
        zforce = pot.zforce(R, z, phi=phi, t=t)
        return _ok({"Rforce": float(rforce), "zforce": float(zforce)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="integrate_orbit", description="Integrate a galpy orbit in a chosen potential.")
def integrate_orbit(
    potential_name: str,
    R: float,
    vR: float,
    vT: float,
    z: float,
    vz: float,
    phi: float,
    t_end: float,
    n_steps: int = 1000,
) -> dict:
    """
    Integrate an orbit and return final phase-space state.

    Parameters:
        potential_name (str): Name of potential class in galpy.potential.
        R (float): Initial radius.
        vR (float): Initial radial velocity.
        vT (float): Initial tangential velocity.
        z (float): Initial height.
        vz (float): Initial vertical velocity.
        phi (float): Initial azimuth.
        t_end (float): End time for integration.
        n_steps (int): Number of time samples.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    if not hasattr(gp, potential_name):
        return _err(f"Unknown potential: {potential_name}")
    if n_steps < 2:
        return _err("n_steps must be >= 2")

    try:
        import numpy as np

        pot_cls = getattr(gp, potential_name)
        pot = pot_cls()  # keep explicit/simple
        o = Orbit([R, vR, vT, z, vz, phi])
        ts = np.linspace(0.0, t_end, n_steps)
        o.integrate(ts, pot)
        final_state = {
            "R": float(o.R(ts[-1])),
            "vR": float(o.vR(ts[-1])),
            "vT": float(o.vT(ts[-1])),
            "z": float(o.z(ts[-1])),
            "vz": float(o.vz(ts[-1])),
            "phi": float(o.phi(ts[-1])),
        }
        return _ok(final_state)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="compute_actions_staeckel", description="Compute orbital actions using actionAngleStaeckel.")
def compute_actions_staeckel(
    potential_name: str,
    R: float,
    vR: float,
    vT: float,
    z: float,
    vz: float,
    delta: float = 0.45,
) -> dict:
    """
    Compute actions (jr, lz, jz) using galpy.actionAngle.actionAngleStaeckel.

    Parameters:
        potential_name (str): Name of potential class in galpy.potential.
        R (float): Radius.
        vR (float): Radial velocity.
        vT (float): Tangential velocity.
        z (float): Height.
        vz (float): Vertical velocity.
        delta (float): Staeckel focal parameter.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)
    if not hasattr(gp, potential_name):
        return _err(f"Unknown potential: {potential_name}")

    try:
        pot = getattr(gp, potential_name)()
        aA = gaa.actionAngleStaeckel(pot=pot, delta=delta)
        jr, lz, jz = aA(R, vR, vT, z, vz)
        return _ok({"jr": float(jr), "lz": float(lz), "jz": float(jz)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="sample_shu_df", description="Evaluate a Shu distribution function at one phase-space point.")
def sample_shu_df(
    hr: float,
    sr: float,
    sz: float,
    R: float,
    vR: float,
    vT: float,
    z: float,
    vz: float,
) -> dict:
    """
    Evaluate dehnen/shu-like disk DF via galpy.df.quasiisothermaldf where possible.

    Parameters:
        hr (float): Radial scale length.
        sr (float): Radial velocity dispersion scale.
        sz (float): Vertical velocity dispersion scale.
        R (float): Radius.
        vR (float): Radial velocity.
        vT (float): Tangential velocity.
        z (float): Height.
        vz (float): Vertical velocity.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    try:
        pot = gp.MWPotential2014 if hasattr(gp, "MWPotential2014") else gp.LogarithmicHaloPotential()
        aA = gaa.actionAngleStaeckel(pot=pot, delta=0.45)
        qdf = gdf.quasiisothermaldf(hr=hr, sr=sr, sz=sz, pot=pot, aA=aA)
        val = qdf(R, vR, vT, z, vz)
        return _ok(float(val))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="available_action_angle_methods", description="List available actionAngle classes.")
def available_action_angle_methods() -> dict:
    """
    List actionAngle class names available in galpy.actionAngle.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    ok, msg = _ensure_imports()
    if not ok:
        return _err(msg)

    names: List[str] = []
    for name in dir(gaa):
        if name.startswith("actionAngle") and name[0].islower():
            names.append(name)
    names.sort()
    return _ok(names)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()