import os
import sys
from typing import Any, Dict

from fastmcp import FastMCP

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

mcp = FastMCP("scikit_hep_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": ""}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="get_package_version",
    description="Return the installed scikit-hep package version string.",
)
def get_package_version() -> Dict[str, Any]:
    """
    Get the scikit-hep package version.

    Returns:
        Dict[str, Any]:
            A standard response dictionary with:
            - success: bool
            - result: version string on success
            - error: error message on failure
    """
    try:
        import skhep

        version = getattr(skhep, "__version__", None)
        if version is None:
            return _err("Version attribute '__version__' was not found in skhep.")
        return _ok(version)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="show_versions",
    description="Collect and return detailed version diagnostics from scikit-hep.",
)
def show_versions() -> Dict[str, Any]:
    """
    Return detailed dependency and environment version information.

    Returns:
        Dict[str, Any]:
            A standard response dictionary with:
            - success: bool
            - result: version diagnostic data or text
            - error: error message on failure
    """
    try:
        from skhep import _show_versions as sv

        if hasattr(sv, "_get_sys_info") and hasattr(sv, "_get_deps_info"):
            result = {
                "system": sv._get_sys_info(),
                "dependencies": sv._get_deps_info(),
            }
            return _ok(result)

        if hasattr(sv, "show_versions"):
            info = sv.show_versions()
            return _ok(info if info is not None else "show_versions executed successfully.")

        return _err("No usable version-report function found in skhep._show_versions.")
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="check_dependency_availability",
    description="Check whether key scientific dependencies can be imported.",
)
def check_dependency_availability() -> Dict[str, Any]:
    """
    Check import availability for key dependencies identified in analysis.

    Returns:
        Dict[str, Any]:
            A standard response dictionary with:
            - success: bool
            - result: mapping of dependency name to import status
            - error: error message on failure
    """
    deps = ["numpy", "scipy", "pandas", "matplotlib", "uproot", "awkward"]
    try:
        status: Dict[str, bool] = {}
        for dep in deps:
            try:
                __import__(dep)
                status[dep] = True
            except Exception:
                status[dep] = False
        return _ok(status)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="get_project_metadata",
    description="Return basic repository/package metadata inferred from local package.",
)
def get_project_metadata() -> Dict[str, Any]:
    """
    Return project metadata from local scikit-hep package and static analysis context.

    Returns:
        Dict[str, Any]:
            A standard response dictionary with:
            - success: bool
            - result: metadata dictionary
            - error: error message on failure
    """
    try:
        import skhep

        result = {
            "package": "skhep",
            "version": getattr(skhep, "__version__", "unknown"),
            "repository_url": "https://github.com/scikit-hep/scikit-hep",
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()