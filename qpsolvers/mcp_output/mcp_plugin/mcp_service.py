import os
import sys
from typing import Any, Dict, List, Optional

import numpy as np

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from qpsolvers import (
    Problem,
    available_solvers,
    solve_ls,
    solve_problem,
    solve_qp,
    solve_unconstrained,
)

mcp = FastMCP("qpsolvers_service")


def _to_array_1d(values: List[float], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a 1D list")
    return arr


def _to_array_2d(values: List[List[float]], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2D list")
    return arr


def _optional_1d(values: Optional[List[float]], name: str) -> Optional[np.ndarray]:
    if values is None:
        return None
    return _to_array_1d(values, name)


def _optional_2d(values: Optional[List[List[float]]], name: str) -> Optional[np.ndarray]:
    if values is None:
        return None
    return _to_array_2d(values, name)


@mcp.tool(name="list_available_solvers", description="List currently available QP solvers in the runtime.")
def list_available_solvers() -> Dict[str, Any]:
    """
    Return the list of solver backends detected by qpsolvers.

    Returns:
        Dict[str, Any]:
            - success (bool): True if listing succeeds.
            - result (Any): List of available solver names.
            - error (str | None): Error message if failed.
    """
    try:
        solvers = available_solvers
        if callable(available_solvers):
            solvers = available_solvers()
        return {"success": True, "result": list(solvers), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="solve_quadratic_program", description="Solve a quadratic program with optional equality and inequality constraints.")
def solve_quadratic_program(
    P: List[List[float]],
    q: List[float],
    solver: str,
    G: Optional[List[List[float]]] = None,
    h: Optional[List[float]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
    lb: Optional[List[float]] = None,
    ub: Optional[List[float]] = None,
    initvals: Optional[List[float]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Solve a quadratic program:

        minimize 0.5 x^T P x + q^T x
        subject to Gx <= h, Ax = b, lb <= x <= ub

    Parameters:
        P: Quadratic cost matrix (n x n).
        q: Linear cost vector (n).
        solver: Solver backend name.
        G: Inequality matrix (m x n), optional.
        h: Inequality bounds (m), optional.
        A: Equality matrix (p x n), optional.
        b: Equality targets (p), optional.
        lb: Lower bounds (n), optional.
        ub: Upper bounds (n), optional.
        initvals: Initial guess for solvers that support warm starts.
        verbose: Whether to print solver logs where supported.

    Returns:
        Dict[str, Any] with success/result/error.
    """
    try:
        P_arr = _to_array_2d(P, "P")
        q_arr = _to_array_1d(q, "q")
        G_arr = _optional_2d(G, "G")
        h_arr = _optional_1d(h, "h")
        A_arr = _optional_2d(A, "A")
        b_arr = _optional_1d(b, "b")
        lb_arr = _optional_1d(lb, "lb")
        ub_arr = _optional_1d(ub, "ub")
        init_arr = _optional_1d(initvals, "initvals")

        x = solve_qp(
            P=P_arr,
            q=q_arr,
            G=G_arr,
            h=h_arr,
            A=A_arr,
            b=b_arr,
            lb=lb_arr,
            ub=ub_arr,
            solver=solver,
            initvals=init_arr,
            verbose=verbose,
        )
        result = None if x is None else x.tolist()
        return {"success": x is not None, "result": result, "error": None if x is not None else "No solution returned"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="solve_least_squares_qp", description="Solve constrained least-squares with QP formulations.")
def solve_least_squares_qp(
    R: List[List[float]],
    s: List[float],
    solver: str,
    G: Optional[List[List[float]]] = None,
    h: Optional[List[float]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
    lb: Optional[List[float]] = None,
    ub: Optional[List[float]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Solve least-squares problem with optional constraints.

    Parameters:
        R: Regression/design matrix.
        s: Target vector.
        solver: Solver backend name.
        G, h, A, b, lb, ub: Optional constraints and bounds.
        verbose: Whether to print solver logs where supported.

    Returns:
        Dict[str, Any] with success/result/error.
    """
    try:
        R_arr = _to_array_2d(R, "R")
        s_arr = _to_array_1d(s, "s")
        G_arr = _optional_2d(G, "G")
        h_arr = _optional_1d(h, "h")
        A_arr = _optional_2d(A, "A")
        b_arr = _optional_1d(b, "b")
        lb_arr = _optional_1d(lb, "lb")
        ub_arr = _optional_1d(ub, "ub")

        x = solve_ls(
            R=R_arr,
            s=s_arr,
            G=G_arr,
            h=h_arr,
            A=A_arr,
            b=b_arr,
            lb=lb_arr,
            ub=ub_arr,
            solver=solver,
            verbose=verbose,
        )
        result = None if x is None else x.tolist()
        return {"success": x is not None, "result": result, "error": None if x is not None else "No solution returned"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="solve_unconstrained_qp", description="Solve an unconstrained quadratic objective.")
def solve_unconstrained_qp(P: List[List[float]], q: List[float]) -> Dict[str, Any]:
    """
    Solve unconstrained quadratic optimization:

        minimize 0.5 x^T P x + q^T x

    Parameters:
        P: Quadratic matrix (n x n).
        q: Linear term (n).

    Returns:
        Dict[str, Any] with success/result/error.
    """
    try:
        P_arr = _to_array_2d(P, "P")
        q_arr = _to_array_1d(q, "q")
        x = solve_unconstrained(P_arr, q_arr)
        return {"success": True, "result": x.tolist(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="solve_qp_via_problem_object", description="Build and solve a qpsolvers.Problem object for advanced workflows.")
def solve_qp_via_problem_object(
    P: List[List[float]],
    q: List[float],
    solver: str,
    G: Optional[List[List[float]]] = None,
    h: Optional[List[float]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
    lb: Optional[List[float]] = None,
    ub: Optional[List[float]] = None,
    initvals: Optional[List[float]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Construct a Problem instance and solve it via solve_problem.

    Parameters:
        P, q: Objective definition.
        solver: Solver backend name.
        G, h, A, b, lb, ub: Optional constraints and bounds.
        initvals: Optional warm-start vector.
        verbose: Optional solver logging flag.

    Returns:
        Dict[str, Any] with success/result/error.
    """
    try:
        P_arr = _to_array_2d(P, "P")
        q_arr = _to_array_1d(q, "q")
        G_arr = _optional_2d(G, "G")
        h_arr = _optional_1d(h, "h")
        A_arr = _optional_2d(A, "A")
        b_arr = _optional_1d(b, "b")
        lb_arr = _optional_1d(lb, "lb")
        ub_arr = _optional_1d(ub, "ub")
        init_arr = _optional_1d(initvals, "initvals")

        problem = Problem(P=P_arr, q=q_arr, G=G_arr, h=h_arr, A=A_arr, b=b_arr, lb=lb_arr, ub=ub_arr)
        solution = solve_problem(problem=problem, solver=solver, initvals=init_arr, verbose=verbose)

        if solution is None:
            return {"success": False, "result": None, "error": "No solution object returned"}

        result = {
            "x": None if solution.x is None else solution.x.tolist(),
            "obj": getattr(solution, "obj", None),
            "found": getattr(solution, "found", None),
            "extras": None if getattr(solution, "extras", None) is None else dict(solution.extras),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()