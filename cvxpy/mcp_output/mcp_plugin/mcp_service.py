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
import cvxpy as cp
import numpy as np


mcp = FastMCP("cvxpy_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="cvxpy_installed_solvers", description="List installed CVXPY solvers.")
def cvxpy_installed_solvers() -> Dict[str, Any]:
    """
    Return installed solver backends detected by CVXPY.

    Returns:
        Dict[str, Any]: Standard response with solver names.
    """
    try:
        return _ok(cp.installed_solvers())
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_least_squares", description="Solve a least-squares problem with optional regularization.")
def solve_least_squares(
    A: List[List[float]],
    b: List[float],
    nonnegative: bool = False,
    l2_reg: float = 0.0,
    solver: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Solve: minimize ||A x - b||_2^2 + l2_reg * ||x||_2^2, optionally with x >= 0.

    Parameters:
        A: 2D coefficient matrix.
        b: Right-hand-side vector.
        nonnegative: If True, enforce x >= 0.
        l2_reg: Nonnegative L2 regularization weight.
        solver: Optional solver name.

    Returns:
        Dict[str, Any]: Standard response containing solution details.
    """
    try:
        A_np = np.array(A, dtype=float)
        b_np = np.array(b, dtype=float)
        if A_np.ndim != 2:
            return _err("A must be a 2D matrix.")
        if b_np.ndim != 1:
            return _err("b must be a 1D vector.")
        if A_np.shape[0] != b_np.shape[0]:
            return _err("A row count must match length of b.")
        if l2_reg < 0:
            return _err("l2_reg must be nonnegative.")

        n = A_np.shape[1]
        x = cp.Variable(n)
        obj = cp.sum_squares(A_np @ x - b_np)
        if l2_reg > 0:
            obj += l2_reg * cp.sum_squares(x)

        constraints = [x >= 0] if nonnegative else []
        prob = cp.Problem(cp.Minimize(obj), constraints)

        if solver:
            val = prob.solve(solver=solver)
        else:
            val = prob.solve()

        return _ok(
            {
                "status": prob.status,
                "objective_value": float(val) if val is not None else None,
                "x": x.value.tolist() if x.value is not None else None,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_linear_program", description="Solve a linear program in standard inequality/equality form.")
def solve_linear_program(
    c: List[float],
    A_ub: Optional[List[List[float]]] = None,
    b_ub: Optional[List[float]] = None,
    A_eq: Optional[List[List[float]]] = None,
    b_eq: Optional[List[float]] = None,
    lb: Optional[List[float]] = None,
    ub: Optional[List[float]] = None,
    sense: str = "min",
    solver: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Solve LP:
      min/max c^T x
      s.t. A_ub x <= b_ub
           A_eq x == b_eq
           lb <= x <= ub

    Parameters:
        c: Objective coefficients.
        A_ub, b_ub: Inequality constraints.
        A_eq, b_eq: Equality constraints.
        lb, ub: Variable bounds vectors.
        sense: "min" or "max".
        solver: Optional solver name.

    Returns:
        Dict[str, Any]: Standard response with optimization result.
    """
    try:
        c_np = np.array(c, dtype=float)
        if c_np.ndim != 1:
            return _err("c must be a 1D vector.")
        n = c_np.shape[0]
        x = cp.Variable(n)

        constraints = []

        if A_ub is not None or b_ub is not None:
            if A_ub is None or b_ub is None:
                return _err("Both A_ub and b_ub must be provided together.")
            A_ub_np = np.array(A_ub, dtype=float)
            b_ub_np = np.array(b_ub, dtype=float)
            if A_ub_np.ndim != 2 or b_ub_np.ndim != 1 or A_ub_np.shape[0] != b_ub_np.shape[0] or A_ub_np.shape[1] != n:
                return _err("Invalid shapes for A_ub or b_ub.")
            constraints.append(A_ub_np @ x <= b_ub_np)

        if A_eq is not None or b_eq is not None:
            if A_eq is None or b_eq is None:
                return _err("Both A_eq and b_eq must be provided together.")
            A_eq_np = np.array(A_eq, dtype=float)
            b_eq_np = np.array(b_eq, dtype=float)
            if A_eq_np.ndim != 2 or b_eq_np.ndim != 1 or A_eq_np.shape[0] != b_eq_np.shape[0] or A_eq_np.shape[1] != n:
                return _err("Invalid shapes for A_eq or b_eq.")
            constraints.append(A_eq_np @ x == b_eq_np)

        if lb is not None:
            lb_np = np.array(lb, dtype=float)
            if lb_np.shape != (n,):
                return _err("lb must have the same length as c.")
            constraints.append(x >= lb_np)

        if ub is not None:
            ub_np = np.array(ub, dtype=float)
            if ub_np.shape != (n,):
                return _err("ub must have the same length as c.")
            constraints.append(x <= ub_np)

        if sense not in ("min", "max"):
            return _err("sense must be 'min' or 'max'.")

        objective_expr = c_np @ x
        objective = cp.Minimize(objective_expr) if sense == "min" else cp.Maximize(objective_expr)
        prob = cp.Problem(objective, constraints)

        if solver:
            val = prob.solve(solver=solver)
        else:
            val = prob.solve()

        return _ok(
            {
                "status": prob.status,
                "objective_value": float(val) if val is not None else None,
                "x": x.value.tolist() if x.value is not None else None,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_quadratic_program", description="Solve a convex quadratic program.")
def solve_quadratic_program(
    P: List[List[float]],
    q: List[float],
    A_ub: Optional[List[List[float]]] = None,
    b_ub: Optional[List[float]] = None,
    A_eq: Optional[List[List[float]]] = None,
    b_eq: Optional[List[float]] = None,
    lb: Optional[List[float]] = None,
    ub: Optional[List[float]] = None,
    solver: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Solve QP:
      minimize (1/2)x^T P x + q^T x
      subject to linear constraints and bounds.

    Parameters:
        P: Symmetric PSD matrix.
        q: Linear objective vector.
        A_ub, b_ub: Inequality constraints.
        A_eq, b_eq: Equality constraints.
        lb, ub: Variable bounds.
        solver: Optional solver name.

    Returns:
        Dict[str, Any]: Standard response with solution details.
    """
    try:
        P_np = np.array(P, dtype=float)
        q_np = np.array(q, dtype=float)

        if P_np.ndim != 2 or P_np.shape[0] != P_np.shape[1]:
            return _err("P must be a square 2D matrix.")
        n = P_np.shape[0]
        if q_np.shape != (n,):
            return _err("q must have length equal to P dimension.")

        x = cp.Variable(n)
        constraints = []

        if A_ub is not None or b_ub is not None:
            if A_ub is None or b_ub is None:
                return _err("Both A_ub and b_ub must be provided together.")
            A_ub_np = np.array(A_ub, dtype=float)
            b_ub_np = np.array(b_ub, dtype=float)
            if A_ub_np.ndim != 2 or b_ub_np.ndim != 1 or A_ub_np.shape[0] != b_ub_np.shape[0] or A_ub_np.shape[1] != n:
                return _err("Invalid shapes for A_ub or b_ub.")
            constraints.append(A_ub_np @ x <= b_ub_np)

        if A_eq is not None or b_eq is not None:
            if A_eq is None or b_eq is None:
                return _err("Both A_eq and b_eq must be provided together.")
            A_eq_np = np.array(A_eq, dtype=float)
            b_eq_np = np.array(b_eq, dtype=float)
            if A_eq_np.ndim != 2 or b_eq_np.ndim != 1 or A_eq_np.shape[0] != b_eq_np.shape[0] or A_eq_np.shape[1] != n:
                return _err("Invalid shapes for A_eq or b_eq.")
            constraints.append(A_eq_np @ x == b_eq_np)

        if lb is not None:
            lb_np = np.array(lb, dtype=float)
            if lb_np.shape != (n,):
                return _err("lb must have the same length as q.")
            constraints.append(x >= lb_np)

        if ub is not None:
            ub_np = np.array(ub, dtype=float)
            if ub_np.shape != (n,):
                return _err("ub must have the same length as q.")
            constraints.append(x <= ub_np)

        obj = 0.5 * cp.quad_form(x, P_np) + q_np @ x
        prob = cp.Problem(cp.Minimize(obj), constraints)

        if solver:
            val = prob.solve(solver=solver)
        else:
            val = prob.solve()

        return _ok(
            {
                "status": prob.status,
                "objective_value": float(val) if val is not None else None,
                "x": x.value.tolist() if x.value is not None else None,
            }
        )
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()