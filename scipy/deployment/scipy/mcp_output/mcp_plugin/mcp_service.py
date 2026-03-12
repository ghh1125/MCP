import os
import sys
from typing import Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import scipy
from scipy import fft, linalg, optimize, signal, sparse, spatial, special, stats

mcp = FastMCP("scipy_core_service")


@mcp.tool(name="scipy_version", description="Get the installed SciPy version.")
def scipy_version() -> dict:
    """
    Return the SciPy version string.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        return {"success": True, "result": scipy.__version__, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="fft_rfft", description="Compute 1D real-input FFT.")
def fft_rfft(values: list[float]) -> dict:
    """
    Compute the real FFT of a sequence.

    Args:
        values: Real-valued input sequence.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        out = fft.rfft(values)
        result = [{"real": float(c.real), "imag": float(c.imag)} for c in out]
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="linalg_solve", description="Solve linear system Ax=b.")
def linalg_solve(a: list[list[float]], b: list[float]) -> dict:
    """
    Solve a dense linear system.

    Args:
        a: Coefficient matrix.
        b: Right-hand side vector.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        x = linalg.solve(a, b)
        return {"success": True, "result": [float(v) for v in x], "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="optimize_minimize", description="Minimize a quadratic objective in 2D.")
def optimize_minimize(x0: list[float], a: float = 1.0, b: float = -2.0) -> dict:
    """
    Minimize f(x, y) = (x-a)^2 + (y-b)^2 from initial guess x0.

    Args:
        x0: Initial point [x, y].
        a: Target x-coordinate for minimum.
        b: Target y-coordinate for minimum.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        if len(x0) != 2:
            return {"success": False, "result": None, "error": "x0 must have length 2"}

        def fun(v: list[float]) -> float:
            return (v[0] - a) ** 2 + (v[1] - b) ** 2

        res = optimize.minimize(fun, x0)
        result = {
            "x": [float(v) for v in res.x],
            "fun": float(res.fun),
            "nit": int(res.nit) if hasattr(res, "nit") else 0,
            "status": int(res.status),
            "message": str(res.message),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="signal_find_peaks", description="Find peaks in a 1D signal.")
def signal_find_peaks(values: list[float], height: Optional[float] = None) -> dict:
    """
    Detect local maxima in a signal.

    Args:
        values: Signal samples.
        height: Optional minimum peak height.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        peaks, props = signal.find_peaks(values, height=height)
        result = {
            "peaks": [int(i) for i in peaks],
            "peak_heights": [float(v) for v in props.get("peak_heights", [])],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="sparse_csr_matvec", description="Multiply CSR sparse matrix by dense vector.")
def sparse_csr_matvec(
    data: list[float],
    indices: list[int],
    indptr: list[int],
    rows: int,
    cols: int,
    vector: list[float],
) -> dict:
    """
    Build a CSR matrix from components and compute matrix-vector product.

    Args:
        data: CSR data array.
        indices: CSR column indices.
        indptr: CSR index pointer array.
        rows: Number of rows.
        cols: Number of columns.
        vector: Dense vector to multiply.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        mat = sparse.csr_matrix((data, indices, indptr), shape=(rows, cols))
        y = mat.dot(vector)
        return {"success": True, "result": [float(v) for v in y], "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spatial_cdist_euclidean", description="Compute pairwise Euclidean distances between two point sets.")
def spatial_cdist_euclidean(xa: list[list[float]], xb: list[list[float]]) -> dict:
    """
    Compute Euclidean distance matrix using scipy.spatial.distance.cdist.

    Args:
        xa: First set of points.
        xb: Second set of points.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        d = spatial.distance.cdist(xa, xb, metric="euclidean")
        return {"success": True, "result": d.tolist(), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="special_erf", description="Compute Gaussian error function values.")
def special_erf(values: list[float]) -> dict:
    """
    Compute erf element-wise.

    Args:
        values: Input real values.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        out = special.erf(values)
        return {"success": True, "result": [float(v) for v in out], "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="stats_describe", description="Compute descriptive statistics for a sample.")
def stats_describe(values: list[float]) -> dict:
    """
    Produce summary statistics for numeric data.

    Args:
        values: Sample values.

    Returns:
        dict: Standard response with success/result/error fields.
    """
    try:
        d = stats.describe(values)
        result = {
            "nobs": int(d.nobs),
            "minmax": [float(d.minmax[0]), float(d.minmax[1])],
            "mean": float(d.mean),
            "variance": float(d.variance),
            "skewness": float(d.skewness),
            "kurtosis": float(d.kurtosis),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp