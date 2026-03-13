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
from cvxopt import matrix, spmatrix
from cvxopt import solvers as cvx_solvers
from cvxopt import setseed, uniform, normal

mcp = FastMCP("cvxopt_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


def _to_matrix(data: List[List[float]] | List[float]) -> matrix:
    if len(data) == 0:
        return matrix([])
    if isinstance(data[0], list):
        rows = len(data)
        cols = len(data[0])
        flat: List[float] = []
        for r in data:
            if len(r) != cols:
                raise ValueError("Inconsistent row lengths in matrix data.")
            flat.extend(float(v) for v in r)
        return matrix(flat, (rows, cols))
    return matrix([float(v) for v in data])


def _to_spmatrix(
    values: List[float],
    row_indices: List[int],
    col_indices: List[int],
    shape_rows: int,
    shape_cols: int,
) -> spmatrix:
    if not (len(values) == len(row_indices) == len(col_indices)):
        raise ValueError("values, row_indices, and col_indices lengths must match.")
    return spmatrix(
        [float(v) for v in values],
        [int(i) for i in row_indices],
        [int(j) for j in col_indices],
        (int(shape_rows), int(shape_cols)),
    )


def _matrix_to_list(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "size") and hasattr(obj, "__getitem__"):
        rows, cols = obj.size
        if cols == 1:
            return [float(obj[i]) for i in range(rows)]
        out: List[List[float]] = []
        for i in range(rows):
            out.append([float(obj[i, j]) for j in range(cols)])
        return out
    return obj


def _normalize_solution(sol: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "status",
        "primal objective",
        "dual objective",
        "gap",
        "relative gap",
        "primal infeasibility",
        "dual infeasibility",
        "iterations",
    ]
    out: Dict[str, Any] = {}
    for k in keys:
        if k in sol:
            out[k] = sol[k]
    for vec_key in ["x", "y", "z", "s", "sl", "sq", "snl", "zl", "zq", "znl"]:
        if vec_key in sol:
            out[vec_key] = _matrix_to_list(sol[vec_key])
    return out


@mcp.tool(name="set_random_seed", description="Set CVXOPT random generator seed.")
def set_random_seed(seed: int) -> Dict[str, Any]:
    """
    Set the random seed used by CVXOPT random functions.

    Parameters:
    - seed: Integer seed value.

    Returns:
    - Standard result dictionary with operation status.
    """
    try:
        setseed(int(seed))
        return _ok(True)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="generate_uniform_vector", description="Generate a CVXOPT uniform random vector.")
def generate_uniform_vector(length: int, a: float = 0.0, b: float = 1.0) -> Dict[str, Any]:
    """
    Generate a vector with uniform random values.

    Parameters:
    - length: Number of entries.
    - a: Lower bound.
    - b: Upper bound.

    Returns:
    - Standard result dictionary containing generated vector.
    """
    try:
        if length < 0:
            return _err("length must be non-negative")
        u = uniform(int(length), a=float(a), b=float(b))
        return _ok(_matrix_to_list(u))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="generate_normal_vector", description="Generate a CVXOPT normal random vector.")
def generate_normal_vector(length: int, mean: float = 0.0, stddev: float = 1.0) -> Dict[str, Any]:
    """
    Generate a vector with normal random values.

    Parameters:
    - length: Number of entries.
    - mean: Mean of distribution.
    - stddev: Standard deviation.

    Returns:
    - Standard result dictionary containing generated vector.
    """
    try:
        if length < 0:
            return _err("length must be non-negative")
        n = normal(int(length), mean=float(mean), std=float(stddev))
        return _ok(_matrix_to_list(n))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_lp", description="Solve a linear program using cvxopt.solvers.lp.")
def solve_lp(
    c: List[float],
    G: List[List[float]],
    h: List[float],
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Solve LP: minimize c^T x subject to Gx <= h and optionally Ax = b.

    Parameters:
    - c: Objective vector.
    - G: Inequality matrix.
    - h: Inequality vector.
    - A: Optional equality matrix.
    - b: Optional equality vector.

    Returns:
    - Standard result dictionary containing normalized solver output.
    """
    try:
        c_m = _to_matrix(c)
        G_m = _to_matrix(G)
        h_m = _to_matrix(h)
        A_m = _to_matrix(A) if A is not None else None
        b_m = _to_matrix(b) if b is not None else None
        sol = cvx_solvers.lp(c_m, G_m, h_m, A_m, b_m)
        return _ok(_normalize_solution(sol))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_qp", description="Solve a quadratic program using cvxopt.solvers.qp.")
def solve_qp(
    P: List[List[float]],
    q: List[float],
    G: Optional[List[List[float]]] = None,
    h: Optional[List[float]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Solve QP: minimize (1/2)x^T P x + q^T x with optional inequality/equality constraints.

    Parameters:
    - P: Quadratic term matrix.
    - q: Linear term vector.
    - G: Optional inequality matrix.
    - h: Optional inequality vector.
    - A: Optional equality matrix.
    - b: Optional equality vector.

    Returns:
    - Standard result dictionary containing normalized solver output.
    """
    try:
        P_m = _to_matrix(P)
        q_m = _to_matrix(q)
        G_m = _to_matrix(G) if G is not None else None
        h_m = _to_matrix(h) if h is not None else None
        A_m = _to_matrix(A) if A is not None else None
        b_m = _to_matrix(b) if b is not None else None
        sol = cvx_solvers.qp(P_m, q_m, G_m, h_m, A_m, b_m)
        return _ok(_normalize_solution(sol))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_socp", description="Solve a second-order cone program using cvxopt.solvers.socp.")
def solve_socp(
    c: List[float],
    Gl_blocks: Optional[List[List[float]]] = None,
    hl: Optional[List[float]] = None,
    Gq_blocks: Optional[List[List[List[float]]]] = None,
    hq_blocks: Optional[List[List[float]]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Solve SOCP with linear and quadratic cone constraints.

    Parameters:
    - c: Objective vector.
    - Gl_blocks: Optional linear inequality matrix block.
    - hl: Optional linear inequality vector.
    - Gq_blocks: Optional list of SOC matrix blocks.
    - hq_blocks: Optional list of SOC vector blocks.
    - A: Optional equality matrix.
    - b: Optional equality vector.

    Returns:
    - Standard result dictionary containing normalized solver output.
    """
    try:
        c_m = _to_matrix(c)
        Gl_m = _to_matrix(Gl_blocks) if Gl_blocks is not None else None
        hl_m = _to_matrix(hl) if hl is not None else None
        Gq_m = [_to_matrix(block) for block in Gq_blocks] if Gq_blocks is not None else []
        hq_m = [_to_matrix(block) for block in hq_blocks] if hq_blocks is not None else []
        A_m = _to_matrix(A) if A is not None else None
        b_m = _to_matrix(b) if b is not None else None
        sol = cvx_solvers.socp(c_m, Gl=Gl_m, hl=hl_m, Gq=Gq_m, hq=hq_m, A=A_m, b=b_m)
        return _ok(_normalize_solution(sol))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solve_sdp", description="Solve a semidefinite program using cvxopt.solvers.sdp.")
def solve_sdp(
    c: List[float],
    Gl: Optional[List[List[float]]] = None,
    hl: Optional[List[float]] = None,
    A: Optional[List[List[float]]] = None,
    b: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Solve SDP with optional linear inequality/equality constraints.

    Parameters:
    - c: Objective vector.
    - Gl: Optional linear inequality matrix.
    - hl: Optional linear inequality vector.
    - A: Optional equality matrix.
    - b: Optional equality vector.

    Returns:
    - Standard result dictionary containing normalized solver output.
    """
    try:
        c_m = _to_matrix(c)
        Gl_m = _to_matrix(Gl) if Gl is not None else None
        hl_m = _to_matrix(hl) if hl is not None else None
        A_m = _to_matrix(A) if A is not None else None
        b_m = _to_matrix(b) if b is not None else None
        sol = cvx_solvers.sdp(c_m, Gl=Gl_m, hl=hl_m, A=A_m, b=b_m)
        return _ok(_normalize_solution(sol))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="solver_options", description="Get or set cvxopt solver options.")
def solver_options(
    action: str,
    key: Optional[str] = None,
    value: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Manage CVXOPT solver options.

    Parameters:
    - action: One of 'get_all', 'get', 'set', 'reset'.
    - key: Option key for get/set.
    - value: Numeric option value for set.

    Returns:
    - Standard result dictionary containing requested option data.
    """
    try:
        act = action.lower().strip()
        if act == "get_all":
            return _ok(dict(cvx_solvers.options))
        if act == "reset":
            cvx_solvers.options.clear()
            return _ok(True)
        if act == "get":
            if not key:
                return _err("key is required for action='get'")
            return _ok(cvx_solvers.options.get(key))
        if act == "set":
            if not key:
                return _err("key is required for action='set'")
            cvx_solvers.options[key] = value
            return _ok(True)
        return _err("invalid action; use get_all, get, set, or reset")
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()