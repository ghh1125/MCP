import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

try:
    import atomman as am
    from atomman.load import load as am_load
    from atomman.dump import dump as am_dump
    from atomman.unitconvert import get_in_units, set_in_units, value_unit
except Exception as e:
    raise ImportError(f"Failed to import atomman modules: {e}") from e

mcp = FastMCP("atomman_core_service")


@mcp.tool(
    name="unit_set_in_units",
    description="Convert a numeric value into the target unit system.",
)
def unit_set_in_units(value: float, units: str) -> Dict[str, Any]:
    """
    Convert a numeric value into specified units.

    Parameters:
        value: Numeric value to convert.
        units: Target units string recognized by atomman.unitconvert.

    Returns:
        A dictionary with conversion result or error.
    """
    try:
        result = set_in_units(value, units)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="unit_get_in_units",
    description="Convert a value from atomman/numericalunits representation to requested units.",
)
def unit_get_in_units(value: float, units: str) -> Dict[str, Any]:
    """
    Convert a value to requested display/output units.

    Parameters:
        value: Numeric value in internal/base units.
        units: Desired output units string.

    Returns:
        A dictionary with converted value or error.
    """
    try:
        result = get_in_units(value, units)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="unit_value_unit",
    description="Build a unit-aware value from a number and units string.",
)
def unit_value_unit(value: float, unit: str) -> Dict[str, Any]:
    """
    Construct a unit-bound value using atomman.unitconvert.value_unit.

    Parameters:
        value: Numeric value.
        unit: Unit label string.

    Returns:
        A dictionary with unit-aware value or error.
    """
    try:
        result = value_unit(value=value, unit=unit)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="load_system",
    description="Load an atomman object/system from a file format supported by atomman.load.",
)
def load_system(style: str, input_file: str, key: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a structure/data object from file.

    Parameters:
        style: Loader style (e.g., 'atom_data', 'poscar', 'cif', 'system_model', etc.).
        input_file: Path to source file.
        key: Optional key/record selector used by some formats.

    Returns:
        A dictionary with a compact summary of the loaded object or error.
    """
    try:
        kwargs: Dict[str, Any] = {"style": style, "inputfile": input_file}
        if key is not None:
            kwargs["key"] = key

        obj = am_load(**kwargs)

        summary: Dict[str, Any] = {"python_type": type(obj).__name__}
        if hasattr(obj, "natoms"):
            summary["natoms"] = int(obj.natoms)
        if hasattr(obj, "box") and getattr(obj, "box") is not None:
            try:
                summary["box"] = getattr(obj.box, "vects", None).tolist()
            except Exception:
                summary["box"] = str(obj.box)

        return {"success": True, "result": summary, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="dump_system",
    description="Export an atomman object/system to a selected format using atomman.dump.",
)
def dump_system(style: str, output_file: str, natoms: int = 1) -> Dict[str, Any]:
    """
    Dump a minimal generated atomman.System into target format/file.

    Parameters:
        style: Dumper style (e.g., 'atom_data', 'poscar', 'pdb', etc.).
        output_file: Destination file path.
        natoms: Number of atoms for generated demo system.

    Returns:
        A dictionary with output path/style or error.
    """
    try:
        if natoms < 1:
            raise ValueError("natoms must be >= 1")

        box = am.Box.cubic(a=1.0)
        atype = [1] * natoms
        pos = [[0.0, 0.0, 0.0] for _ in range(natoms)]
        atoms = am.Atoms(natoms=natoms, atype=atype, pos=pos)
        system = am.System(atoms=atoms, box=box, pbc=[True, True, True])

        am_dump(style, system, f=output_file)
        return {"success": True, "result": {"style": style, "output_file": output_file}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()