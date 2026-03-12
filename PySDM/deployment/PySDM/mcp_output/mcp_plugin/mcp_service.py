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

mcp = FastMCP("pysdm_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="get_project_summary",
    description="Return high-level project summary and module map for PySDM.",
)
def get_project_summary() -> Dict[str, Any]:
    """
    Returns a concise summary of the repository and major package groups.

    Returns:
        Dict with success/result/error where result is a project metadata dictionary.
    """
    try:
        result = {
            "repository": "https://github.com/atmos-cloud-sim-uj/PySDM",
            "packages": [
                "PySDM.attributes",
                "PySDM.backends",
                "PySDM.dynamics",
                "PySDM.environments",
                "PySDM.exporters",
                "PySDM.initialisation",
                "PySDM.physics",
                "PySDM.products",
            ],
            "main_dependencies": ["numpy", "numba", "scipy"],
            "optional_dependencies": ["matplotlib", "netCDF4", "vtk", "ThrustRTC/CUDA"],
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="list_available_dynamics",
    description="List available dynamics modules in PySDM.",
)
def list_available_dynamics() -> Dict[str, Any]:
    """
    Lists core dynamics available in the project.

    Returns:
        Dict with success/result/error; result is a list of dynamics names.
    """
    try:
        dynamics = [
            "ambient_thermodynamics",
            "aqueous_chemistry",
            "collisions",
            "condensation",
            "displacement",
            "eulerian_advection",
            "freezing",
            "isotopic_fractionation",
            "relaxed_velocity",
            "seeding",
            "terminal_velocity",
            "vapour_deposition_on_ice",
        ]
        return _ok(dynamics)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="list_available_environments",
    description="List environment classes/modules for setting simulations.",
)
def list_available_environments() -> Dict[str, Any]:
    """
    Lists major environment modules.

    Returns:
        Dict with success/result/error; result is a list of environment module names.
    """
    try:
        environments = ["box", "kinematic_1d", "kinematic_2d", "parcel"]
        return _ok(environments)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="list_available_backends",
    description="List computational backends and their intended runtime.",
)
def list_available_backends() -> Dict[str, Any]:
    """
    Lists supported backend options.

    Returns:
        Dict with success/result/error; result is backend metadata.
    """
    try:
        backends = [
            {"name": "numba", "module": "PySDM.backends.numba", "runtime": "CPU"},
            {
                "name": "thrust_rtc",
                "module": "PySDM.backends.thrust_rtc",
                "runtime": "GPU/CUDA",
            },
        ]
        return _ok(backends)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="list_products_by_group",
    description="List product modules grouped by category.",
)
def list_products_by_group(group: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists product groups and representative product modules.

    Args:
        group: Optional group filter (e.g., 'size_spectral', 'collision').

    Returns:
        Dict with success/result/error where result contains product groups.
    """
    try:
        product_groups = {
            "ambient_thermodynamics": [
                "ambient_temperature",
                "ambient_pressure",
                "ambient_relative_humidity",
            ],
            "aqueous_chemistry": ["acidity", "aqueous_mass_spectrum", "gaseous_mole_fraction"],
            "collision": ["collision_rates", "collision_timestep_mean", "collision_timestep_min"],
            "condensation": ["activable_fraction", "event_rates", "peak_saturation"],
            "displacement": ["averaged_terminal_velocity", "max_courant_number", "surface_precipitation"],
            "freezing": ["cooling_rate", "frozen_particle_concentration", "ice_nuclei_concentration"],
            "optical": ["cloud_albedo", "cloud_optical_depth"],
            "parcel": ["cloud_water_path", "parcel_displacement"],
            "size_spectral": ["effective_radius", "particle_size_spectrum", "water_mixing_ratio"],
            "housekeeping": ["time", "dynamic_wall_time", "timers"],
        }
        if group is None:
            return _ok(product_groups)
        if group not in product_groups:
            return _err(f"Unknown group: {group}")
        return _ok({group: product_groups[group]})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="inspect_module",
    description="Inspect a module by import path and list public attributes.",
)
def inspect_module(module_path: str, limit: int = 50) -> Dict[str, Any]:
    """
    Imports a module and returns basic introspection details.

    Args:
        module_path: Full python import path (e.g., 'PySDM.dynamics.condensation').
        limit: Max number of public attributes to return.

    Returns:
        Dict with success/result/error; result contains module metadata.
    """
    try:
        if limit <= 0:
            return _err("limit must be > 0")
        mod = __import__(module_path, fromlist=["*"])
        attrs = [name for name in dir(mod) if not name.startswith("_")]
        attrs = attrs[:limit]
        return _ok({"module": module_path, "attribute_count": len(attrs), "attributes": attrs})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="check_optional_dependency",
    description="Check whether an optional dependency is installed.",
)
def check_optional_dependency(package_name: str) -> Dict[str, Any]:
    """
    Checks importability of a given package.

    Args:
        package_name: Import name of a package (e.g., 'vtk', 'netCDF4').

    Returns:
        Dict with success/result/error; result is True/False.
    """
    try:
        __import__(package_name)
        return _ok(True)
    except Exception:
        return _ok(False)


@mcp.tool(
    name="validate_pysdm_import",
    description="Validate that the PySDM package can be imported from local source path.",
)
def validate_pysdm_import() -> Dict[str, Any]:
    """
    Verifies local import setup for PySDM modules.

    Returns:
        Dict with success/result/error and import status details.
    """
    try:
        import PySDM  # noqa: F401

        return _ok({"importable": True, "source_path": source_path})
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()