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
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex


mcp = FastMCP("sympy_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


def _parse(expression: str) -> sp.Expr:
    return parse_expr(expression, evaluate=True)


@mcp.tool(name="sympy_simplify", description="Simplify a symbolic expression.")
def sympy_simplify(expression: str) -> Dict[str, Any]:
    """
    Simplify a symbolic expression string.

    Parameters:
    - expression: SymPy-compatible expression string.

    Returns:
    - Dictionary with success/result/error. On success, result is the simplified expression string.
    """
    try:
        expr = _parse(expression)
        return _ok(str(sp.simplify(expr)))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_expand", description="Expand a symbolic expression.")
def sympy_expand(expression: str) -> Dict[str, Any]:
    """
    Expand a symbolic expression string.

    Parameters:
    - expression: SymPy-compatible expression string.

    Returns:
    - Dictionary with success/result/error. On success, result is the expanded expression string.
    """
    try:
        expr = _parse(expression)
        return _ok(str(sp.expand(expr)))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_factor", description="Factor a symbolic expression.")
def sympy_factor(expression: str) -> Dict[str, Any]:
    """
    Factor a symbolic expression string.

    Parameters:
    - expression: SymPy-compatible expression string.

    Returns:
    - Dictionary with success/result/error. On success, result is the factored expression string.
    """
    try:
        expr = _parse(expression)
        return _ok(str(sp.factor(expr)))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_diff", description="Differentiate an expression with respect to a variable.")
def sympy_diff(expression: str, variable: str, order: int = 1) -> Dict[str, Any]:
    """
    Differentiate an expression.

    Parameters:
    - expression: SymPy-compatible expression string.
    - variable: Variable name to differentiate by.
    - order: Derivative order (>=1).

    Returns:
    - Dictionary with success/result/error. On success, result is derivative expression string.
    """
    try:
        if order < 1:
            raise ValueError("order must be >= 1")
        expr = _parse(expression)
        var = sp.Symbol(variable)
        result = sp.diff(expr, var, order)
        return _ok(str(result))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_integrate", description="Integrate an expression (definite or indefinite).")
def sympy_integrate(
    expression: str,
    variable: str,
    lower: Optional[float] = None,
    upper: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Integrate an expression.

    Parameters:
    - expression: SymPy-compatible expression string.
    - variable: Integration variable name.
    - lower: Optional lower bound for definite integration.
    - upper: Optional upper bound for definite integration.

    Returns:
    - Dictionary with success/result/error. On success, result is integral expression/value string.
    """
    try:
        expr = _parse(expression)
        var = sp.Symbol(variable)
        if lower is None or upper is None:
            result = sp.integrate(expr, var)
        else:
            result = sp.integrate(expr, (var, lower, upper))
        return _ok(str(result))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_solve", description="Solve algebraic equation(s) for variable(s).")
def sympy_solve(equation: str, variables: List[str]) -> Dict[str, Any]:
    """
    Solve one equation for one or more variables.

    Parameters:
    - equation: Equation string, e.g. 'x**2 - 4' or 'Eq(x + y, 3)'.
    - variables: List of variable names to solve for.

    Returns:
    - Dictionary with success/result/error. On success, result contains stringified solutions.
    """
    try:
        eq_expr = _parse(equation)
        vars_syms = [sp.Symbol(v) for v in variables]
        result = sp.solve(eq_expr, vars_syms if len(vars_syms) > 1 else vars_syms[0], dict=True)
        return _ok([str(r) for r in result])
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_solve_linear_system", description="Solve a linear system from equations and variables.")
def sympy_solve_linear_system(equations: List[str], variables: List[str]) -> Dict[str, Any]:
    """
    Solve a system of linear equations.

    Parameters:
    - equations: List of equation strings, e.g. ['Eq(x + y, 2)', 'Eq(x - y, 0)'].
    - variables: List of variable names.

    Returns:
    - Dictionary with success/result/error. On success, result is a stringified mapping.
    """
    try:
        eqs = [_parse(eq) for eq in equations]
        vars_syms = [sp.Symbol(v) for v in variables]
        result = sp.linsolve(eqs, vars_syms)
        return _ok(str(result))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_limit", description="Compute the limit of an expression.")
def sympy_limit(expression: str, variable: str, point: float, direction: str = "+") -> Dict[str, Any]:
    """
    Compute a one-sided or two-sided limit.

    Parameters:
    - expression: SymPy-compatible expression string.
    - variable: Variable name.
    - point: Point of approach.
    - direction: '+', '-', or '+-'.

    Returns:
    - Dictionary with success/result/error. On success, result is limit expression/value string.
    """
    try:
        expr = _parse(expression)
        var = sp.Symbol(variable)
        if direction not in {"+", "-", "+-"}:
            raise ValueError("direction must be one of '+', '-', '+-'")
        result = sp.limit(expr, var, point, dir=direction)
        return _ok(str(result))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_series", description="Compute series expansion around a point.")
def sympy_series(expression: str, variable: str, point: float = 0.0, order: int = 6) -> Dict[str, Any]:
    """
    Compute truncated series expansion.

    Parameters:
    - expression: SymPy-compatible expression string.
    - variable: Variable name.
    - point: Expansion point.
    - order: Truncation order.

    Returns:
    - Dictionary with success/result/error. On success, result is series string.
    """
    try:
        if order < 1:
            raise ValueError("order must be >= 1")
        expr = _parse(expression)
        var = sp.Symbol(variable)
        result = sp.series(expr, var, point, order)
        return _ok(str(result))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_matrix_inverse", description="Compute inverse of a matrix.")
def sympy_matrix_inverse(matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Compute inverse of a numeric matrix.

    Parameters:
    - matrix: 2D list representing a square matrix.

    Returns:
    - Dictionary with success/result/error. On success, result is inverse matrix as nested lists.
    """
    try:
        m = sp.Matrix(matrix)
        inv = m.inv()
        return _ok([[str(cell) for cell in row] for row in inv.tolist()])
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_matrix_determinant", description="Compute determinant of a matrix.")
def sympy_matrix_determinant(matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Compute determinant of a matrix.

    Parameters:
    - matrix: 2D list representing a square matrix.

    Returns:
    - Dictionary with success/result/error. On success, result is determinant string.
    """
    try:
        m = sp.Matrix(matrix)
        return _ok(str(m.det()))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_to_latex", description="Convert expression to LaTeX.")
def sympy_to_latex(expression: str) -> Dict[str, Any]:
    """
    Convert expression string to LaTeX format.

    Parameters:
    - expression: SymPy-compatible expression string.

    Returns:
    - Dictionary with success/result/error. On success, result is LaTeX string.
    """
    try:
        expr = _parse(expression)
        return _ok(latex(expr))
    except Exception as e:
        return _err(e)


@mcp.tool(name="sympy_numeric_eval", description="Numerically evaluate expression with substitutions.")
def sympy_numeric_eval(expression: str, substitutions: Dict[str, float], precision: int = 15) -> Dict[str, Any]:
    """
    Numerically evaluate expression.

    Parameters:
    - expression: SymPy-compatible expression string.
    - substitutions: Mapping from variable name to numeric value.
    - precision: Decimal precision for evalf.

    Returns:
    - Dictionary with success/result/error. On success, result is numeric value string.
    """
    try:
        expr = _parse(expression)
        subs = {sp.Symbol(k): v for k, v in substitutions.items()}
        result = expr.subs(subs).evalf(precision)
        return _ok(str(result))
    except Exception as e:
        return _err(e)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()