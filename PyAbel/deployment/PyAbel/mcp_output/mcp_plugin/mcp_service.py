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
import numpy as np
import abel
from abel.transform import Transform
from abel import direct, hansenlaw, basex, daun, dasch, linbasex, rbasex, onion_bordas

mcp = FastMCP("pyabel_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": ""}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


def _as_array2d(image: List[List[float]]) -> np.ndarray:
    arr = np.asarray(image, dtype=float)
    if arr.ndim != 2:
        raise ValueError("image must be a 2D list of floats")
    return arr


@mcp.tool(name="abel_transform", description="Run a generic Abel transform with selected method.")
def abel_transform(
    image: List[List[float]],
    method: str = "hansenlaw",
    direction: str = "inverse",
    symmetry_axis: Optional[int] = None,
    use_quadrants: bool = True,
) -> Dict[str, Any]:
    """
    Run PyAbel Transform on a 2D image.

    Parameters:
    - image: 2D image data as nested float lists.
    - method: Transform method (e.g., hansenlaw, basex, direct, daun, linbasex, rbasex, onion_bordas, two_point, three_point).
    - direction: 'inverse' or 'forward'.
    - symmetry_axis: Optional symmetry axis used by Transform.
    - use_quadrants: Whether to use quadrants in Transform.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        t = Transform(
            arr,
            method=method,
            direction=direction,
            symmetry_axis=symmetry_axis,
            use_quadrants=use_quadrants,
        )
        return _ok(t.transform.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="direct_transform", description="Run direct Abel transform.")
def direct_transform(
    image: List[List[float]],
    direction: str = "inverse",
    correction: bool = True,
) -> Dict[str, Any]:
    """
    Run direct method transform.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - correction: Apply end-point correction where supported.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        out = direct.direct_transform(arr, direction=direction, correction=correction)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="hansenlaw_transform", description="Run Hansen-Law Abel transform.")
def hansenlaw_transform(
    image: List[List[float]],
    direction: str = "inverse",
    hold_order: int = 0,
) -> Dict[str, Any]:
    """
    Run Hansen-Law transform.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - hold_order: Hold approximation order.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        out = hansenlaw.hansenlaw_transform(arr, direction=direction, hold_order=hold_order)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="basex_transform", description="Run BASEX Abel transform.")
def basex_transform(
    image: List[List[float]],
    direction: str = "inverse",
    sigma: float = 1.0,
    reg: float = 0.0,
) -> Dict[str, Any]:
    """
    Run BASEX transform.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - sigma: Gaussian width parameter.
    - reg: Regularization parameter.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        out = basex.basex_transform(arr, direction=direction, sigma=sigma, reg=reg)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="daun_transform", description="Run Daun Abel transform.")
def daun_transform(
    image: List[List[float]],
    direction: str = "inverse",
    degree: int = 0,
    reg: float = 0.0,
) -> Dict[str, Any]:
    """
    Run Daun transform.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - degree: Polynomial degree.
    - reg: Regularization parameter.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        out = daun.daun_transform(arr, direction=direction, degree=degree, reg=reg)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="dasch_transform", description="Run Dasch method transform (two_point/three_point/onion_peeling).")
def dasch_transform(
    image: List[List[float]],
    method: str = "three_point",
    direction: str = "inverse",
) -> Dict[str, Any]:
    """
    Run Dasch method transform via Transform wrapper.

    Parameters:
    - image: 2D image data.
    - method: one of 'two_point', 'three_point', 'onion_peeling'.
    - direction: 'inverse' or 'forward'.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        t = Transform(arr, method=method, direction=direction)
        return _ok(t.transform.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="linbasex_transform", description="Run Lin-Basex transform.")
def linbasex_transform(
    image: List[List[float]],
    proj_angles: Optional[List[float]] = None,
    legendre_orders: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Run Lin-Basex transform.

    Parameters:
    - image: 2D image data.
    - proj_angles: Optional projection angles in degrees.
    - legendre_orders: Optional Legendre orders.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        pa = None if proj_angles is None else np.asarray(proj_angles, dtype=float)
        lo = None if legendre_orders is None else np.asarray(legendre_orders, dtype=int)
        out = linbasex.linbasex_transform(arr, proj_angles=pa, legendre_orders=lo)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="rbasex_transform", description="Run rBasex transform.")
def rbasex_transform(
    image: List[List[float]],
    direction: str = "inverse",
    reg: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run rBasex transform via Transform wrapper.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - reg: Optional regularization strength.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        transform_options: Dict[str, Any] = {}
        if reg is not None:
            transform_options["reg"] = reg
        t = Transform(arr, method="rbasex", direction=direction, transform_options=transform_options)
        return _ok(t.transform.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="onion_bordas_transform", description="Run Onion-Bordas transform.")
def onion_bordas_transform(
    image: List[List[float]],
    direction: str = "inverse",
    shift_grid: bool = True,
) -> Dict[str, Any]:
    """
    Run Onion-Bordas transform.

    Parameters:
    - image: 2D image data.
    - direction: 'inverse' or 'forward'.
    - shift_grid: Whether to shift by half-pixel grid.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        arr = _as_array2d(image)
        out = onion_bordas.onion_bordas_transform(arr, direction=direction, shift_grid=shift_grid)
        return _ok(np.asarray(out).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pyabel_version", description="Get installed PyAbel version.")
def pyabel_version() -> Dict[str, Any]:
    """
    Return PyAbel version string.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        return _ok(getattr(abel, "__version__", "unknown"))
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()