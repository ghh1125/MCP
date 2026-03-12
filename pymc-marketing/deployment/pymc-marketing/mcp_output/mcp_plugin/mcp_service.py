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
from pymc_marketing.model_builder import ModelBuilder

mcp = FastMCP("pymc_marketing_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="model_builder_introspect_class",
    description="Inspect ModelBuilder class metadata and public callables.",
)
def model_builder_introspect_class() -> Dict[str, Any]:
    """
    Introspect the ModelBuilder class.

    Returns:
        Dict[str, Any]: Standard response dictionary with:
            - success: True on success, False on error
            - result: Class metadata including module, qualname, and public methods
            - error: Error message when unsuccessful
    """
    try:
        public_methods: List[str] = sorted(
            [
                name
                for name in dir(ModelBuilder)
                if not name.startswith("_") and callable(getattr(ModelBuilder, name))
            ]
        )
        result = {
            "module": ModelBuilder.__module__,
            "qualname": ModelBuilder.__qualname__,
            "doc": (ModelBuilder.__doc__ or "").strip(),
            "public_methods": public_methods,
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="model_builder_list_public_attributes",
    description="List public attributes and methods from ModelBuilder.",
)
def model_builder_list_public_attributes(include_methods: bool = True) -> Dict[str, Any]:
    """
    List public attributes from ModelBuilder with optional method filtering.

    Args:
        include_methods (bool): If True, include callable public members.
            If False, include only non-callable public members.

    Returns:
        Dict[str, Any]: Standard response dictionary.
    """
    try:
        items: List[str] = []
        for name in dir(ModelBuilder):
            if name.startswith("_"):
                continue
            member = getattr(ModelBuilder, name)
            if include_methods and callable(member):
                items.append(name)
            elif not include_methods and not callable(member):
                items.append(name)
        return _ok(sorted(items))
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="model_builder_method_doc",
    description="Get docstring for a specific public ModelBuilder method.",
)
def model_builder_method_doc(method_name: str) -> Dict[str, Any]:
    """
    Fetch the docstring for a named ModelBuilder method.

    Args:
        method_name (str): Public method name on ModelBuilder.

    Returns:
        Dict[str, Any]: Standard response dictionary.
    """
    try:
        if not hasattr(ModelBuilder, method_name):
            return _err(f"Method not found: {method_name}")
        member = getattr(ModelBuilder, method_name)
        if not callable(member):
            return _err(f"Attribute is not callable: {method_name}")
        doc = (member.__doc__ or "").strip()
        return _ok({"method": method_name, "doc": doc})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="model_builder_method_signature",
    description="Get a readable signature for a ModelBuilder method.",
)
def model_builder_method_signature(method_name: str) -> Dict[str, Any]:
    """
    Get method signature string from ModelBuilder.

    Args:
        method_name (str): Name of a callable member on ModelBuilder.

    Returns:
        Dict[str, Any]: Standard response dictionary.
    """
    try:
        import inspect

        if not hasattr(ModelBuilder, method_name):
            return _err(f"Method not found: {method_name}")
        member = getattr(ModelBuilder, method_name)
        if not callable(member):
            return _err(f"Attribute is not callable: {method_name}")
        signature = str(inspect.signature(member))
        return _ok({"method": method_name, "signature": signature})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="model_builder_instantiate",
    description="Attempt to instantiate ModelBuilder and report basic instance info.",
)
def model_builder_instantiate() -> Dict[str, Any]:
    """
    Attempt to instantiate ModelBuilder without constructor arguments.

    Returns:
        Dict[str, Any]: Standard response dictionary containing instance type details,
        or an error if constructor arguments are required.
    """
    try:
        instance = ModelBuilder()
        result = {
            "instance_type": type(instance).__name__,
            "module": type(instance).__module__,
            "has_dict": hasattr(instance, "__dict__"),
            "public_instance_attrs": sorted(
                [k for k in dir(instance) if not k.startswith("_")]
            )[:200],
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="model_builder_check_method_exists",
    description="Check if a public callable exists on ModelBuilder.",
)
def model_builder_check_method_exists(method_name: str) -> Dict[str, Any]:
    """
    Validate whether a named public method exists.

    Args:
        method_name (str): Method name to check.

    Returns:
        Dict[str, Any]: Standard response dictionary with existence and callability.
    """
    try:
        exists = hasattr(ModelBuilder, method_name)
        callable_member = bool(exists and callable(getattr(ModelBuilder, method_name)))
        return _ok({"exists": exists, "callable": callable_member})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="service_health",
    description="Basic service health check and import validation.",
)
def service_health() -> Dict[str, Any]:
    """
    Run a lightweight health check for the MCP service.

    Returns:
        Dict[str, Any]: Standard response dictionary.
    """
    try:
        result = {
            "service": "pymc_marketing_service",
            "model_builder_imported": ModelBuilder is not None,
            "source_path_in_sys_path": source_path in sys.path,
            "python_version": sys.version,
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()