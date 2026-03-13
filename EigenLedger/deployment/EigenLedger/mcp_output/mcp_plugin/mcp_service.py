import os
import sys
from typing import Any, Dict, Optional

from fastmcp import FastMCP

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

try:
    from EigenLedger.main import EigenLedger as _EigenLedgerClass
except Exception:
    _EigenLedgerClass = None

mcp = FastMCP("eigenledger_service")


def _safe_response(success: bool, result: Any = None, error: Optional[str] = None) -> Dict[str, Any]:
    return {"success": success, "result": result, "error": error}


def _ensure_engine() -> Any:
    if _EigenLedgerClass is None:
        raise ImportError("Unable to import EigenLedger.main.EigenLedger")
    return _EigenLedgerClass()


@mcp.tool(name="health_check", description="Check service and import readiness.")
def health_check() -> Dict[str, Any]:
    """
    Perform a basic service health check.

    Returns:
        dict: Standard response dictionary with service status details.
    """
    try:
        import_ready = _EigenLedgerClass is not None
        return _safe_response(True, {"service": "eigenledger_service", "import_ready": import_ready}, None)
    except Exception as exc:
        return _safe_response(False, None, str(exc))


@mcp.tool(name="list_engine_methods", description="List callable public methods exposed by EigenLedger engine.")
def list_engine_methods() -> Dict[str, Any]:
    """
    Inspect EigenLedger engine and return available public callables.

    Returns:
        dict: Standard response dictionary with sorted method names.
    """
    try:
        engine = _ensure_engine()
        methods = [
            n for n in dir(engine)
            if not n.startswith("_") and callable(getattr(engine, n, None))
        ]
        return _safe_response(True, sorted(methods), None)
    except Exception as exc:
        return _safe_response(False, None, str(exc))


@mcp.tool(name="run_method_no_args", description="Run a no-argument public method on EigenLedger engine.")
def run_method_no_args(method_name: str) -> Dict[str, Any]:
    """
    Execute a public no-argument method on the EigenLedger engine.

    Args:
        method_name: Name of a callable method that does not require positional arguments.

    Returns:
        dict: Standard response dictionary with method execution result.
    """
    try:
        engine = _ensure_engine()
        if method_name.startswith("_"):
            return _safe_response(False, None, "Private methods are not allowed")
        if not hasattr(engine, method_name):
            return _safe_response(False, None, f"Method not found: {method_name}")

        method = getattr(engine, method_name)
        if not callable(method):
            return _safe_response(False, None, f"Attribute is not callable: {method_name}")

        output = method()
        return _safe_response(True, output, None)
    except TypeError as exc:
        return _safe_response(False, None, f"Method signature mismatch: {exc}")
    except Exception as exc:
        return _safe_response(False, None, str(exc))


@mcp.tool(name="run_method_with_json_args", description="Run a public EigenLedger method with JSON object keyword arguments.")
def run_method_with_json_args(method_name: str, kwargs_json: str) -> Dict[str, Any]:
    """
    Execute a public method on the EigenLedger engine using JSON keyword arguments.

    Args:
        method_name: Name of the engine method to execute.
        kwargs_json: JSON string encoding a dictionary of keyword arguments.

    Returns:
        dict: Standard response dictionary with method execution result.
    """
    try:
        import json

        engine = _ensure_engine()
        if method_name.startswith("_"):
            return _safe_response(False, None, "Private methods are not allowed")
        if not hasattr(engine, method_name):
            return _safe_response(False, None, f"Method not found: {method_name}")

        method = getattr(engine, method_name)
        if not callable(method):
            return _safe_response(False, None, f"Attribute is not callable: {method_name}")

        parsed = json.loads(kwargs_json)
        if not isinstance(parsed, dict):
            return _safe_response(False, None, "kwargs_json must decode to a JSON object")

        output = method(**parsed)
        return _safe_response(True, output, None)
    except Exception as exc:
        return _safe_response(False, None, str(exc))


@mcp.tool(name="get_engine_attribute", description="Read a public non-callable attribute from EigenLedger engine.")
def get_engine_attribute(attribute_name: str) -> Dict[str, Any]:
    """
    Retrieve a public non-callable attribute from the EigenLedger engine.

    Args:
        attribute_name: Name of the public attribute.

    Returns:
        dict: Standard response dictionary with attribute value.
    """
    try:
        engine = _ensure_engine()
        if attribute_name.startswith("_"):
            return _safe_response(False, None, "Private attributes are not allowed")
        if not hasattr(engine, attribute_name):
            return _safe_response(False, None, f"Attribute not found: {attribute_name}")

        value = getattr(engine, attribute_name)
        if callable(value):
            return _safe_response(False, None, f"Attribute is callable, use method tools: {attribute_name}")

        return _safe_response(True, value, None)
    except Exception as exc:
        return _safe_response(False, None, str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()