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

mcp = FastMCP("pysph_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="list_example_modules", description="List available PySPH example modules.")
def list_example_modules(limit: int = 200) -> Dict[str, Any]:
    """
    Discover importable modules inside pysph.examples.

    Parameters:
        limit: Maximum number of module names to return.

    Returns:
        Standard response dictionary with success/result/error.
    """
    try:
        import pkgutil
        import pysph.examples as examples_pkg

        modules: List[str] = []
        for mod in pkgutil.walk_packages(examples_pkg.__path__, prefix="pysph.examples."):
            if not mod.ispkg:
                modules.append(mod.name)
            if len(modules) >= limit:
                break
        return _ok(sorted(modules))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="run_example_module", description="Run a PySPH example module as a subprocess.")
def run_example_module(module: str, extra_args: Optional[List[str]] = None, timeout: int = 300) -> Dict[str, Any]:
    """
    Execute a PySPH example via Python module execution.

    Parameters:
        module: Fully-qualified module path (e.g., pysph.examples.cavity).
        extra_args: Additional CLI args for the module.
        timeout: Subprocess timeout in seconds.

    Returns:
        Standard response dictionary with process return code/stdout/stderr.
    """
    try:
        import subprocess

        args = [sys.executable, "-m", module]
        if extra_args:
            args.extend(extra_args)

        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return _ok(
            {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": args,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="run_examples_discovery", description="Use pysph.examples.run helper to list or run examples.")
def run_examples_discovery(action: str = "list", query: Optional[str] = None, timeout: int = 180) -> Dict[str, Any]:
    """
    Invoke the examples runner utility module.

    Parameters:
        action: Runner action hint, typically 'list' or 'run'.
        query: Optional query/filter or example name.
        timeout: Subprocess timeout in seconds.

    Returns:
        Standard response dictionary with process output.
    """
    try:
        import subprocess

        cmd = [sys.executable, "-m", "pysph.examples.run"]
        if action:
            cmd.append(action)
        if query:
            cmd.append(query)

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return _ok(
            {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": cmd,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="convert_output_to_xdmf", description="Run PySPH XDMF conversion utility.")
def convert_output_to_xdmf(input_path: str, output_path: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
    """
    Convert PySPH output to XDMF format via CLI utility.

    Parameters:
        input_path: Input file or directory path.
        output_path: Optional output destination path.
        timeout: Subprocess timeout in seconds.

    Returns:
        Standard response dictionary with process output.
    """
    try:
        import subprocess

        cmd = [sys.executable, "-m", "pysph.tools.dump_xdmf", input_path]
        if output_path:
            cmd.extend(["-o", output_path])

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return _ok(
            {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": cmd,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="convert_output_to_vtk", description="Run PySPH VTK conversion utility.")
def convert_output_to_vtk(input_path: str, output_dir: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
    """
    Convert PySPH output artifacts to VTK using provided utility.

    Parameters:
        input_path: Input file or directory path.
        output_dir: Optional output directory.
        timeout: Subprocess timeout in seconds.

    Returns:
        Standard response dictionary with process output.
    """
    try:
        import subprocess

        cmd = [sys.executable, "-m", "pysph.tools.pysph_to_vtk", input_path]
        if output_dir:
            cmd.extend(["-d", output_dir])

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return _ok(
            {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": cmd,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="manage_pysph_cache", description="Manage PySPH cache using built-in cache utility.")
def manage_pysph_cache(action: str = "list", cache_dir: Optional[str] = None, timeout: int = 180) -> Dict[str, Any]:
    """
    Perform cache operations using pysph.tools.manage_cache.

    Parameters:
        action: Cache operation (for example: list, clear).
        cache_dir: Optional target cache directory.
        timeout: Subprocess timeout in seconds.

    Returns:
        Standard response dictionary with process output.
    """
    try:
        import subprocess

        cmd = [sys.executable, "-m", "pysph.tools.manage_cache", action]
        if cache_dir:
            cmd.extend(["--path", cache_dir])

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return _ok(
            {
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "command": cmd,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="inspect_pysph_environment", description="Inspect PySPH import availability and version details.")
def inspect_pysph_environment() -> Dict[str, Any]:
    """
    Check whether key PySPH modules can be imported and gather basic metadata.

    Returns:
        Standard response dictionary with import status and versions.
    """
    try:
        result: Dict[str, Any] = {"python": sys.version, "source_path": source_path, "modules": {}}
        modules = [
            "pysph",
            "pysph.base",
            "pysph.solver",
            "pysph.sph",
            "pysph.tools",
            "pysph.examples",
        ]
        for name in modules:
            try:
                mod = __import__(name, fromlist=["*"])
                result["modules"][name] = {"importable": True, "file": getattr(mod, "__file__", None)}
            except Exception as ie:
                result["modules"][name] = {"importable": False, "file": None, "error": str(ie)}
        return _ok(result)
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()