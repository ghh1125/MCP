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

try:
    import gala
    from gala import dynamics, integrate, potential, coordinates, units
except Exception:
    gala = None
    dynamics = None
    integrate = None
    potential = None
    coordinates = None
    units = None

mcp = FastMCP("gala_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="gala_package_info", description="Get gala package version and module availability.")
def gala_package_info() -> Dict[str, Any]:
    """
    Return basic package metadata and module availability.

    Returns:
        dict: Standard response with package version and import status.
    """
    if gala is None:
        return _err("Failed to import gala package from local source path.")
    return _ok(
        {
            "version": getattr(gala, "__version__", "unknown"),
            "modules": {
                "coordinates": coordinates is not None,
                "dynamics": dynamics is not None,
                "integrate": integrate is not None,
                "potential": potential is not None,
                "units": units is not None,
            },
        }
    )


@mcp.tool(name="list_builtin_potentials", description="List available built-in potential class names.")
def list_builtin_potentials() -> Dict[str, Any]:
    """
    List builtin potential classes exposed by gala.potential.

    Returns:
        dict: Standard response containing potential-like class names.
    """
    if potential is None:
        return _err("gala.potential is not available.")
    try:
        names: List[str] = []
        for n in dir(potential):
            if "Potential" in n and not n.startswith("_"):
                names.append(n)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="create_potential", description="Create a built-in potential instance by class name.")
def create_potential(
    class_name: str,
    units_name: Optional[str] = None,
    parameters: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Instantiate a gala built-in potential class.

    Parameters:
        class_name (str): Name of potential class in gala.potential.
        units_name (Optional[str]): Unit system name from gala.units (e.g., 'galactic').
        parameters (Optional[dict]): Keyword parameters for class constructor.

    Returns:
        dict: Standard response with lightweight serialization of the potential.
    """
    if potential is None:
        return _err("gala.potential is not available.")
    try:
        cls = getattr(potential, class_name, None)
        if cls is None:
            return _err(f"Potential class '{class_name}' not found.")
        kwargs: Dict[str, Any] = dict(parameters or {})
        if units_name:
            if units is None:
                return _err("gala.units is not available.")
            unit_system = getattr(units, units_name, None)
            if unit_system is None:
                return _err(f"Unit system '{units_name}' not found in gala.units.")
            kwargs["units"] = unit_system
        obj = cls(**kwargs)
        return _ok({"class_name": class_name, "repr": repr(obj)})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="evaluate_potential", description="Evaluate potential energy at a Cartesian position.")
def evaluate_potential(
    class_name: str,
    x: float,
    y: float,
    z: float,
    parameters: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Evaluate potential value at a position.

    Parameters:
        class_name (str): Built-in potential class name in gala.potential.
        x (float): X coordinate.
        y (float): Y coordinate.
        z (float): Z coordinate.
        parameters (Optional[dict]): Constructor parameters for potential class.

    Returns:
        dict: Standard response with evaluated value.
    """
    if potential is None:
        return _err("gala.potential is not available.")
    try:
        cls = getattr(potential, class_name, None)
        if cls is None:
            return _err(f"Potential class '{class_name}' not found.")
        pot = cls(**(parameters or {}))
        val = pot.energy([x, y, z])
        return _ok({"value": str(val)})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="evaluate_acceleration", description="Evaluate acceleration vector at a Cartesian position.")
def evaluate_acceleration(
    class_name: str,
    x: float,
    y: float,
    z: float,
    parameters: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Evaluate acceleration vector for a potential at a position.

    Parameters:
        class_name (str): Built-in potential class name.
        x (float): X coordinate.
        y (float): Y coordinate.
        z (float): Z coordinate.
        parameters (Optional[dict]): Constructor parameters.

    Returns:
        dict: Standard response with acceleration vector.
    """
    if potential is None:
        return _err("gala.potential is not available.")
    try:
        cls = getattr(potential, class_name, None)
        if cls is None:
            return _err(f"Potential class '{class_name}' not found.")
        pot = cls(**(parameters or {}))
        acc = pot.acceleration([x, y, z])
        return _ok({"acceleration": str(acc)})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="integrate_orbit", description="Integrate an orbit in a specified potential.")
def integrate_orbit(
    class_name: str,
    x: float,
    y: float,
    z: float,
    vx: float,
    vy: float,
    vz: float,
    dt: float,
    n_steps: int,
    parameters: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Integrate an orbit with simple Cartesian initial conditions.

    Parameters:
        class_name (str): Built-in potential class name.
        x (float): Initial x position.
        y (float): Initial y position.
        z (float): Initial z position.
        vx (float): Initial x velocity.
        vy (float): Initial y velocity.
        vz (float): Initial z velocity.
        dt (float): Timestep.
        n_steps (int): Number of integration steps.
        parameters (Optional[dict]): Potential constructor parameters.

    Returns:
        dict: Standard response with orbit representation.
    """
    if potential is None or dynamics is None:
        return _err("Required modules gala.potential or gala.dynamics are not available.")
    try:
        cls = getattr(potential, class_name, None)
        if cls is None:
            return _err(f"Potential class '{class_name}' not found.")
        pot = cls(**(parameters or {}))
        w0 = [x, y, z, vx, vy, vz]
        orbit = pot.integrate_orbit(w0=w0, dt=dt, n_steps=n_steps)
        return _ok({"orbit_repr": repr(orbit)})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="available_integrators", description="List available Python and Cython integrators in gala.")
def available_integrators() -> Dict[str, Any]:
    """
    List integrator classes and helpers exposed in gala.integrate.

    Returns:
        dict: Standard response with integrator-like symbols.
    """
    if integrate is None:
        return _err("gala.integrate is not available.")
    try:
        names: List[str] = []
        for n in dir(integrate):
            if ("Integrator" in n or "Leapfrog" in n or "DOPRI" in n or "RK" in n) and not n.startswith("_"):
                names.append(n)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_coordinates_frames", description="List available coordinate frames in gala.coordinates.")
def list_coordinates_frames() -> Dict[str, Any]:
    """
    Return stream and custom coordinate frame names available in gala.coordinates.

    Returns:
        dict: Standard response with frame-like symbols.
    """
    if coordinates is None:
        return _err("gala.coordinates is not available.")
    try:
        names: List[str] = []
        for n in dir(coordinates):
            if ("Frame" in n or n.lower().endswith("coordinates")) and not n.startswith("_"):
                names.append(n)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()