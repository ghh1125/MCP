import os
import sys
from typing import Any, Dict

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

try:
    from oemof.cli import main as oemof_cli_main
except Exception:
    oemof_cli_main = None

try:
    import oemof
except Exception:
    oemof = None


mcp = FastMCP("oemof_service")


@mcp.tool(name="get_oemof_version", description="Get installed oemof package version.")
def get_oemof_version() -> Dict[str, Any]:
    """
    Return the detected oemof package version.

    Returns:
        Dict[str, Any]:
            success: True if version could be determined.
            result: Version string when successful, else None.
            error: Error message when unsuccessful, else None.
    """
    try:
        if oemof is None:
            return {"success": False, "result": None, "error": "oemof package is not importable"}
        version = getattr(oemof, "__version__", None)
        if version is None:
            return {"success": False, "result": None, "error": "__version__ not available in oemof package"}
        return {"success": True, "result": str(version), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="run_oemof_cli", description="Run oemof CLI main entrypoint with explicit arguments.")
def run_oemof_cli(args: str) -> Dict[str, Any]:
    """
    Execute oemof CLI main function with provided argument string.

    Parameters:
        args (str): Command-line arguments as a single string, e.g. "--help".

    Returns:
        Dict[str, Any]:
            success: True if CLI invocation completed without unhandled exception.
            result: Dict with execution details.
            error: Error message when unsuccessful, else None.
    """
    try:
        if oemof_cli_main is None:
            return {"success": False, "result": None, "error": "oemof.cli.main is not importable"}

        argv = [part for part in args.split(" ") if part.strip()] if args else []
        previous_argv = list(sys.argv)
        sys.argv = ["oemof"] + argv
        try:
            output = oemof_cli_main()
        except SystemExit as exc:
            return {
                "success": True,
                "result": {"system_exit_code": exc.code, "return_value": None, "argv": sys.argv},
                "error": None,
            }
        finally:
            sys.argv = previous_argv

        return {"success": True, "result": {"return_value": output, "argv": ["oemof"] + argv}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()