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

try:
    import ufl
    from ufl.algorithms import (
        apply_algebra_lowering,
        apply_derivatives,
        estimate_total_polynomial_degree,
        expand_derivatives,
        expand_indices,
        replace,
    )
except Exception as import_error:
    raise ImportError(f"Failed to import UFL from local source path: {import_error}") from import_error

mcp = FastMCP("ufl_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="ufl_version", description="Get installed UFL version information.")
def ufl_version() -> Dict[str, Any]:
    """
    Return version metadata for the UFL package.

    Returns:
        Dict[str, Any]: Standard response with success/result/error fields.
    """
    try:
        version = getattr(ufl, "__version__", "unknown")
        return _ok({"version": version})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="list_ufl_symbols", description="List public UFL symbols available in the package.")
def list_ufl_symbols(limit: int = 200) -> Dict[str, Any]:
    """
    List exported symbols from the top-level ufl namespace.

    Parameters:
        limit (int): Maximum number of symbols to return.

    Returns:
        Dict[str, Any]: Standard response with success/result/error fields.
    """
    try:
        symbols = [s for s in dir(ufl) if not s.startswith("_")]
        symbols.sort()
        if limit < 1:
            limit = 1
        return _ok(symbols[:limit])
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="parse_ufl_expression", description="Parse a UFL expression from a Python expression string.")
def parse_ufl_expression(expression: str) -> Dict[str, Any]:
    """
    Parse a textual Python expression into a UFL expression object.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with parsed expression string form.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        return _ok({"repr": repr(expr), "str": str(expr), "type": type(expr).__name__})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="estimate_polynomial_degree", description="Estimate total polynomial degree of a UFL expression.")
def estimate_polynomial_degree(expression: str) -> Dict[str, Any]:
    """
    Estimate the total polynomial degree for a UFL expression.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with degree estimate.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        degree = estimate_total_polynomial_degree(expr)
        return _ok({"degree": int(degree) if degree is not None else None})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="expand_indices", description="Expand free indices in a UFL expression.")
def expand_indices_tool(expression: str) -> Dict[str, Any]:
    """
    Expand index notation in a UFL expression.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with transformed expression.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        transformed = expand_indices(expr)
        return _ok({"repr": repr(transformed), "str": str(transformed)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="expand_derivatives", description="Expand derivative nodes in a UFL expression.")
def expand_derivatives_tool(expression: str) -> Dict[str, Any]:
    """
    Expand derivatives in a UFL expression.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with transformed expression.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        transformed = expand_derivatives(expr)
        return _ok({"repr": repr(transformed), "str": str(transformed)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="apply_derivatives", description="Apply derivative rules to a UFL expression.")
def apply_derivatives_tool(expression: str) -> Dict[str, Any]:
    """
    Apply derivative algorithms to a UFL expression.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with transformed expression.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        transformed = apply_derivatives(expr)
        return _ok({"repr": repr(transformed), "str": str(transformed)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="apply_algebra_lowering", description="Apply algebra lowering transformations to UFL expressions.")
def apply_algebra_lowering_tool(expression: str) -> Dict[str, Any]:
    """
    Lower high-level algebraic constructs in a UFL expression.

    Parameters:
        expression (str): Python expression string evaluated with the ufl namespace.

    Returns:
        Dict[str, Any]: Standard response with transformed expression.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        transformed = apply_algebra_lowering(expr)
        return _ok({"repr": repr(transformed), "str": str(transformed)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="replace_in_expression", description="Replace subexpressions in a UFL expression.")
def replace_in_expression(expression: str, replacements: List[str]) -> Dict[str, Any]:
    """
    Replace symbolic subexpressions in a UFL expression.

    Parameters:
        expression (str): Target expression string evaluated with the ufl namespace.
        replacements (List[str]): List of replacement rules as 'lhs=rhs' expression strings.

    Returns:
        Dict[str, Any]: Standard response with transformed expression.
    """
    try:
        env: Dict[str, Any] = {k: getattr(ufl, k) for k in dir(ufl) if not k.startswith("_")}
        expr = eval(expression, {"__builtins__": {}}, env)
        mapping: Dict[Any, Any] = {}
        for item in replacements:
            if "=" not in item:
                return _err(f"Invalid replacement rule '{item}', expected 'lhs=rhs'.")
            lhs, rhs = item.split("=", 1)
            lhs_expr = eval(lhs.strip(), {"__builtins__": {}}, env)
            rhs_expr = eval(rhs.strip(), {"__builtins__": {}}, env)
            mapping[lhs_expr] = rhs_expr
        transformed = replace(expr, mapping)
        return _ok({"repr": repr(transformed), "str": str(transformed)})
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()