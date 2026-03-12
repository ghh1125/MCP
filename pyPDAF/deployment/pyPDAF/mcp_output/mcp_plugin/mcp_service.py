import os
import sys
from typing import List, Dict, Any

from fastmcp import FastMCP

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

mcp = FastMCP("pypdaf_service")


def _import_error_result(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="list_pypdaf_modules", description="List available pyPDAF submodules.")
def list_pypdaf_modules() -> Dict[str, Any]:
    """
    Return the known pyPDAF wrapper submodules that are expected in this repository.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    modules = ["pyPDAF", "pyPDAF.PDAF", "pyPDAF.PDAF3", "pyPDAF.PDAFomi", "pyPDAF.PDAFlocal", "pyPDAF.PDAFlocalomi"]
    return {"success": True, "result": modules, "error": None}


@mcp.tool(name="get_pypdaf_version", description="Get pyPDAF package version if available.")
def get_pypdaf_version() -> Dict[str, Any]:
    """
    Read and return pyPDAF package version metadata.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        import pyPDAF  # type: ignore

        version = getattr(pyPDAF, "__version__", None)
        return {"success": True, "result": {"version": version}, "error": None}
    except Exception as exc:
        return _import_error_result(exc)


@mcp.tool(name="inspect_pypdaf_namespace", description="Inspect callables and symbols in a pyPDAF module.")
def inspect_pypdaf_namespace(module_name: str, include_private: bool = False) -> Dict[str, Any]:
    """
    Inspect symbols in a selected pyPDAF module.

    Args:
        module_name: Import path for a module, e.g. 'pyPDAF.PDAF'.
        include_private: Whether to include names starting with underscore.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        module = __import__(module_name, fromlist=["*"])
        names = dir(module)
        if not include_private:
            names = [n for n in names if not n.startswith("_")]
        callables = [n for n in names if callable(getattr(module, n, None))]
        constants = [n for n in names if not callable(getattr(module, n, None))]
        return {
            "success": True,
            "result": {
                "module": module_name,
                "symbols": names,
                "callables": callables,
                "constants": constants,
            },
            "error": None,
        }
    except Exception as exc:
        return _import_error_result(exc)


@mcp.tool(name="list_example_scenarios", description="List shipped pyPDAF example scenarios.")
def list_example_scenarios() -> Dict[str, Any]:
    """
    Return available example scenario families identified in the repository.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    scenarios = ["offline", "online"]
    return {"success": True, "result": scenarios, "error": None}


@mcp.tool(name="get_example_file_tree", description="Get selected example input/output file inventory.")
def get_example_file_tree(scenario: str) -> Dict[str, Any]:
    """
    Return a curated file inventory for example scenarios.

    Args:
        scenario: Scenario name ('offline' or 'online').

    Returns:
        dict: Standard response with success/result/error fields.
    """
    example_map: Dict[str, List[str]] = {
        "offline": [
            "example/offline/main.py",
            "example/offline/model.py",
            "example/offline/pdaf_system.py",
            "example/offline/prepost_processing.py",
            "example/offline/obs_a.py",
            "example/offline/obs_b.py",
            "example/inputs_offline/state_ini.txt",
            "example/inputs_offline/obs.txt",
            "example/inputs_offline/true.txt",
        ],
        "online": [
            "example/online/main.py",
            "example/online/model.py",
            "example/online/model_integrator.py",
            "example/online/pdaf_system.py",
            "example/online/prepost_processing.py",
            "example/online/obs_a.py",
            "example/online/obs_b.py",
            "example/inputs_online/state_ini.txt",
            "example/inputs_online/obs_step1.txt",
            "example/inputs_online/true_step1.txt",
        ],
    }
    if scenario not in example_map:
        return {"success": False, "result": None, "error": f"Unknown scenario: {scenario}"}
    return {"success": True, "result": {"scenario": scenario, "files": example_map[scenario]}, "error": None}


@mcp.tool(name="read_repository_summary", description="Return repository-level analysis summary.")
def read_repository_summary() -> Dict[str, Any]:
    """
    Provide concise repository metadata inferred from analysis.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    summary = {
        "repository_url": "https://github.com/yumengch/pyPDAF",
        "processed_by": "zip_fallback",
        "file_count": 165,
        "dependencies": {
            "required": ["python", "numpy", "mpi4py"],
            "optional": [
                "pdaf native/compiled libraries",
                "cython (build-time)",
                "pytest (test-time)",
            ],
        },
        "risk": {
            "import_feasibility": 0.72,
            "intrusiveness_risk": "low",
            "complexity": "medium",
        },
    }
    return {"success": True, "result": summary, "error": None}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()