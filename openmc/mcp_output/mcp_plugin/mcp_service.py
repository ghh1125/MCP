import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

import openmc
import openmc.data
import openmc.deplete
import openmc.model
import openmc.mgxs

mcp = FastMCP("openmc_mcp_service")


def _ok(result: Any) -> dict:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> dict:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="openmc_version", description="Get installed OpenMC version information.")
def openmc_version() -> dict:
    """
    Return OpenMC package version metadata.

    Returns:
        dict: Standard response with version string in result.
    """
    try:
        return _ok({"version": getattr(openmc, "__version__", "unknown")})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_example_models", description="List available built-in OpenMC example model builders.")
def list_example_models() -> dict:
    """
    List callable public builders in openmc.examples.

    Returns:
        dict: Standard response with list of callable names.
    """
    try:
        import openmc.examples as examples

        names = []
        for name in dir(examples):
            if name.startswith("_"):
                continue
            obj = getattr(examples, name)
            if callable(obj):
                names.append(name)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="build_example_model", description="Build a built-in OpenMC example model and export XML input files.")
def build_example_model(example_name: str, output_dir: str) -> dict:
    """
    Build a built-in OpenMC example model and export its XML files.

    Parameters:
        example_name: Name of callable builder under openmc.examples.
        output_dir: Directory where XML files should be written.

    Returns:
        dict: Standard response with generated file paths.
    """
    try:
        import openmc.examples as examples

        if not hasattr(examples, example_name):
            return _err(f"Example '{example_name}' not found in openmc.examples")

        builder = getattr(examples, example_name)
        if not callable(builder):
            return _err(f"Attribute '{example_name}' is not callable")

        model = builder()
        if not isinstance(model, openmc.model.Model):
            return _err(f"Builder '{example_name}' did not return openmc.model.Model")

        os.makedirs(output_dir, exist_ok=True)
        model.export_to_xml(directory=output_dir)

        expected = ["materials.xml", "geometry.xml", "settings.xml", "tallies.xml", "plots.xml"]
        files = [os.path.join(output_dir, f) for f in expected if os.path.exists(os.path.join(output_dir, f))]
        return _ok({"output_dir": output_dir, "files": files})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="inspect_statepoint", description="Inspect key metadata from an OpenMC statepoint HDF5 file.")
def inspect_statepoint(statepoint_path: str) -> dict:
    """
    Open and summarize a statepoint file.

    Parameters:
        statepoint_path: Path to statepoint*.h5 file.

    Returns:
        dict: Standard response containing selected statepoint metadata.
    """
    try:
        sp = openmc.StatePoint(statepoint_path)
        result = {
            "path": statepoint_path,
            "run_mode": getattr(sp, "run_mode", None),
            "n_realizations": getattr(sp, "n_realizations", None),
            "keff": str(getattr(sp, "keff", None)),
            "n_tallies": len(getattr(sp, "tallies", {}) or {}),
        }
        sp.close()
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="load_summary", description="Load an OpenMC summary file and return high-level model counts.")
def load_summary(summary_path: str) -> dict:
    """
    Load summary.h5 and report object counts.

    Parameters:
        summary_path: Path to summary.h5.

    Returns:
        dict: Standard response with counts for cells, universes, and materials.
    """
    try:
        summary = openmc.Summary(summary_path)
        geometry = summary.geometry
        materials = summary.materials
        return _ok(
            {
                "path": summary_path,
                "cells": len(geometry.get_all_cells()),
                "universes": len(geometry.get_all_universes()),
                "materials": len(materials),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_depletion_integrators", description="List available depletion integrator classes.")
def list_depletion_integrators() -> dict:
    """
    Enumerate public integrator classes in openmc.deplete.integrators.

    Returns:
        dict: Standard response with integrator class names.
    """
    try:
        from openmc.deplete import integrators as ints

        names = []
        for name in dir(ints):
            if name.startswith("_"):
                continue
            obj = getattr(ints, name)
            if isinstance(obj, type):
                names.append(name)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_mgxs_types", description="List available MGXS classes from openmc.mgxs.")
def list_mgxs_types() -> dict:
    """
    Enumerate MGXS-related class names in openmc.mgxs.

    Returns:
        dict: Standard response with MGXS class names.
    """
    try:
        names = []
        for name in dir(openmc.mgxs):
            if name.startswith("_"):
                continue
            obj = getattr(openmc.mgxs, name)
            if isinstance(obj, type):
                names.append(name)
        return _ok(sorted(names))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="atomic_mass", description="Get atomic mass for a nuclide from openmc.data.")
def atomic_mass(nuclide: str) -> dict:
    """
    Retrieve atomic mass for a nuclide.

    Parameters:
        nuclide: Nuclide name (e.g., 'U235', 'H1').

    Returns:
        dict: Standard response with atomic mass value.
    """
    try:
        value = openmc.data.atomic_mass(nuclide)
        return _ok({"nuclide": nuclide, "atomic_mass": value})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="half_life", description="Get half-life for a nuclide from openmc.data.")
def half_life(nuclide: str) -> dict:
    """
    Retrieve half-life for a nuclide in seconds.

    Parameters:
        nuclide: Nuclide name (e.g., 'Co60').

    Returns:
        dict: Standard response with half-life.
    """
    try:
        value = openmc.data.half_life(nuclide)
        return _ok({"nuclide": nuclide, "half_life_seconds": value})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="water_density", description="Compute water density from temperature and pressure.")
def water_density(temperature_kelvin: float, pressure_mpa: float) -> dict:
    """
    Compute water density using OpenMC helper.

    Parameters:
        temperature_kelvin: Temperature in K.
        pressure_mpa: Pressure in MPa.

    Returns:
        dict: Standard response with water density in g/cm3.
    """
    try:
        density = openmc.data.water_density(temperature_kelvin, pressure_mpa)
        return _ok(
            {
                "temperature_kelvin": temperature_kelvin,
                "pressure_mpa": pressure_mpa,
                "density_g_per_cm3": density,
            }
        )
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()