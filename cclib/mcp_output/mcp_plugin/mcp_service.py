import os
import sys
import io
import contextlib
from typing import Any, List, Optional, Dict

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from cclib.io import ccread, ccwrite
from cclib.scripts import ccget as ccget_script
from cclib.scripts import ccframe as ccframe_script
from cclib.scripts import cda as cda_script

mcp = FastMCP("cclib_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="parse_logfile", description="Parse a computational chemistry logfile and return selected attributes.")
def parse_logfile(path: str, attributes: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Parse a supported computational chemistry output file.

    Parameters:
        path: Path to the input logfile.
        attributes: Optional list of attribute names to extract. If omitted, returns basic metadata.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        data = ccread(path)
        if data is None:
            return _err(f"Failed to parse file: {path}")

        if attributes:
            extracted: Dict[str, Any] = {}
            for attr in attributes:
                extracted[attr] = getattr(data, attr, None)
            return _ok(extracted)

        summary = {
            "natom": getattr(data, "natom", None),
            "nbasis": getattr(data, "nbasis", None),
            "nmo": getattr(data, "nmo", None),
            "charge": getattr(data, "charge", None),
            "mult": getattr(data, "mult", None),
            "available_attributes": sorted([k for k in data.__dict__.keys() if not k.startswith("_")]),
        }
        return _ok(summary)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="convert_logfile", description="Convert parsed output into another supported format.")
def convert_logfile(path: str, outputtype: str, outputdest: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert a computational chemistry logfile to another format using cclib IO.

    Parameters:
        path: Path to input logfile.
        outputtype: Output format, e.g. cjson, xyz, molden, wfx.
        outputdest: Optional destination file path. If omitted, returns converted text.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        data = ccread(path)
        if data is None:
            return _err(f"Failed to parse file: {path}")

        converted = ccwrite(data, outputtype=outputtype, outputdest=outputdest)
        if outputdest:
            return _ok({"written_to": outputdest, "outputtype": outputtype})
        return _ok(converted)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="run_ccget", description="Run ccget-like extraction for selected attributes from one or more files.")
def run_ccget(attributes: List[str], files: List[str]) -> Dict[str, Any]:
    """
    Extract selected attributes from one or more files in a ccget-like workflow.

    Parameters:
        attributes: List of attribute names to extract.
        files: List of input file paths.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        results: Dict[str, Dict[str, Any]] = {}
        for file_path in files:
            data = ccread(file_path)
            if data is None:
                results[file_path] = {"error": "parse_failed"}
                continue
            entry: Dict[str, Any] = {}
            for attr in attributes:
                entry[attr] = getattr(data, attr, None)
            results[file_path] = entry
        return _ok(results)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="run_ccframe", description="Aggregate selected attributes from multiple files in table-like rows.")
def run_ccframe(files: List[str], attributes: List[str]) -> Dict[str, Any]:
    """
    Produce a table-style aggregation similar to ccframe output.

    Parameters:
        files: Input file paths.
        attributes: Attributes to include as columns.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        rows: List[Dict[str, Any]] = []
        for file_path in files:
            data = ccread(file_path)
            if data is None:
                rows.append({"file": file_path, "parse_error": True})
                continue
            row: Dict[str, Any] = {"file": file_path}
            for attr in attributes:
                row[attr] = getattr(data, attr, None)
            rows.append(row)
        return _ok(rows)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="run_cda_cli", description="Execute cclib CDA CLI main with explicit arguments and capture output.")
def run_cda_cli(logfile: str, fragment1: str, fragment2: str) -> Dict[str, Any]:
    """
    Run the CDA script main flow with three explicit arguments.

    Parameters:
        logfile: Supermolecule logfile path.
        fragment1: Fragment 1 logfile path.
        fragment2: Fragment 2 logfile path.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        argv = ["cda", logfile, fragment1, fragment2]
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        old_argv = sys.argv[:]
        try:
            sys.argv = argv
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                cda_script.main()
        finally:
            sys.argv = old_argv
        return _ok({"stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="cclib_script_versions", description="Return lightweight availability info for cclib script modules.")
def cclib_script_versions() -> Dict[str, Any]:
    """
    Report script module availability and file locations for ccget/ccwrite/ccframe/cda.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        result = {
            "ccget_module": getattr(ccget_script, "__file__", None),
            "ccframe_module": getattr(ccframe_script, "__file__", None),
            "cda_module": getattr(cda_script, "__file__", None),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()