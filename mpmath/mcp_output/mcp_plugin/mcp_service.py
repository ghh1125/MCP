import os
import sys
from typing import List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import mpmath as mp

mcp = FastMCP("mpmath_service")


@mcp.tool(name="set_precision", description="Set global decimal precision for mpmath calculations.")
def set_precision(dps: int) -> dict:
    """
    Set mpmath decimal precision.

    Parameters:
        dps: Number of decimal digits to keep in mpmath.mp.dps.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        if dps < 2:
            raise ValueError("dps must be >= 2")
        mp.mp.dps = dps
        return {"success": True, "result": {"dps": mp.mp.dps}, "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="evaluate_expression", description="Evaluate a mathematical expression using mpmath context.")
def evaluate_expression(expression: str) -> dict:
    """
    Evaluate a Python expression with mpmath symbols available.

    Parameters:
        expression: Expression string, e.g. 'sin(pi/3) + sqrt(2)'.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        safe_globals = {"__builtins__": {}}
        safe_locals = {name: getattr(mp, name) for name in dir(mp) if not name.startswith("_")}
        value = eval(expression, safe_globals, safe_locals)
        return {"success": True, "result": str(value), "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="find_root", description="Find a root of a function using mpmath.findroot.")
def find_root(function_expression: str, x0: float) -> dict:
    """
    Find a numeric root for a single-variable function.

    Parameters:
        function_expression: Expression in variable x, e.g. 'cos(x)-x'.
        x0: Initial guess.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        safe_globals = {"__builtins__": {}}
        safe_locals = {name: getattr(mp, name) for name in dir(mp) if not name.startswith("_")}

        def f(x):
            local_ctx = dict(safe_locals)
            local_ctx["x"] = x
            return eval(function_expression, safe_globals, local_ctx)

        root = mp.findroot(f, x0)
        return {"success": True, "result": str(root), "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="integrate", description="Compute definite integral using mpmath.quad.")
def integrate(function_expression: str, a: float, b: float) -> dict:
    """
    Compute definite integral of f(x) from a to b.

    Parameters:
        function_expression: Expression in variable x, e.g. 'exp(-x**2)'.
        a: Lower bound.
        b: Upper bound.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        safe_globals = {"__builtins__": {}}
        safe_locals = {name: getattr(mp, name) for name in dir(mp) if not name.startswith("_")}

        def f(x):
            local_ctx = dict(safe_locals)
            local_ctx["x"] = x
            return eval(function_expression, safe_globals, local_ctx)

        val = mp.quad(f, [a, b])
        return {"success": True, "result": str(val), "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="differentiate", description="Compute n-th derivative at a point using mpmath.diff.")
def differentiate(function_expression: str, x: float, n: int) -> dict:
    """
    Compute derivative of order n for f at x.

    Parameters:
        function_expression: Expression in variable t, e.g. 'sin(t)*exp(t)'.
        x: Evaluation point.
        n: Derivative order (>=1).

    Returns:
        Dictionary with success/result/error.
    """
    try:
        if n < 1:
            raise ValueError("n must be >= 1")
        safe_globals = {"__builtins__": {}}
        safe_locals = {name: getattr(mp, name) for name in dir(mp) if not name.startswith("_")}

        def f(t):
            local_ctx = dict(safe_locals)
            local_ctx["t"] = t
            return eval(function_expression, safe_globals, local_ctx)

        val = mp.diff(f, x, n=n)
        return {"success": True, "result": str(val), "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="solve_linear_system", description="Solve a dense linear system A*x=b with mpmath matrices.")
def solve_linear_system(a_rows: List[List[float]], b_values: List[float]) -> dict:
    """
    Solve linear system A*x=b.

    Parameters:
        a_rows: Matrix rows for A.
        b_values: Vector b.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        if len(a_rows) == 0:
            raise ValueError("a_rows must not be empty")
        if len(a_rows) != len(b_values):
            raise ValueError("A row count must match b length")
        col_count = len(a_rows[0])
        if col_count == 0:
            raise ValueError("A must have at least one column")
        for row in a_rows:
            if len(row) != col_count:
                raise ValueError("All rows in A must have same length")

        A = mp.matrix(a_rows)
        b = mp.matrix([[v] for v in b_values])
        x = mp.lu_solve(A, b)
        result = [str(x[i]) for i in range(len(b_values))]
        return {"success": True, "result": result, "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="eigenvalues", description="Compute eigenvalues of a square matrix.")
def eigenvalues(matrix_rows: List[List[float]]) -> dict:
    """
    Compute eigenvalues of a square matrix.

    Parameters:
        matrix_rows: Square matrix rows.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        n = len(matrix_rows)
        if n == 0:
            raise ValueError("matrix_rows must not be empty")
        for row in matrix_rows:
            if len(row) != n:
                raise ValueError("Matrix must be square")
        M = mp.matrix(matrix_rows)
        vals = mp.eig(M, left=False, right=False)
        result = [str(v) for v in vals]
        return {"success": True, "result": result, "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="special_function", description="Evaluate selected special functions from mpmath.")
def special_function(function_name: str, x: float) -> dict:
    """
    Evaluate one supported special function at x.

    Parameters:
        function_name: One of ['gamma', 'zeta', 'erf', 'besselj0', 'bessely0', 'airyai', 'airybi'].
        x: Input value.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        fn = function_name.lower().strip()
        if fn == "gamma":
            v = mp.gamma(x)
        elif fn == "zeta":
            v = mp.zeta(x)
        elif fn == "erf":
            v = mp.erf(x)
        elif fn == "besselj0":
            v = mp.besselj(0, x)
        elif fn == "bessely0":
            v = mp.bessely(0, x)
        elif fn == "airyai":
            v = mp.airyai(x)
        elif fn == "airybi":
            v = mp.airybi(x)
        else:
            raise ValueError("Unsupported function_name")
        return {"success": True, "result": str(v), "error": ""}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()