import os
import sys
from typing import List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import numpy as np
import gstools as gs

mcp = FastMCP("gstools_service")


@mcp.tool(name="list_covariance_models", description="List available built-in covariance model classes in GSTools.")
def list_covariance_models() -> dict:
    """
    Return a list of common covariance model class names exposed by GSTools.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        model_names = [
            "Gaussian",
            "Exponential",
            "Matern",
            "Integral",
            "Stable",
            "Rational",
            "Cubic",
            "Linear",
            "Circular",
            "Spherical",
            "HyperSpherical",
            "SuperSpherical",
            "JBessel",
        ]
        available = [name for name in model_names if hasattr(gs, name)]
        return {"success": True, "result": available, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="create_covariance_model", description="Create a GSTools covariance model and return basic properties.")
def create_covariance_model(
    model_name: str,
    dim: int,
    var: float = 1.0,
    len_scale: float = 1.0,
    nugget: float = 0.0,
    anis: Optional[List[float]] = None,
) -> dict:
    """
    Create a covariance model by class name and return descriptive metadata.

    Parameters:
        model_name (str): Covariance model class name (e.g., Gaussian, Exponential, Matern).
        dim (int): Spatial dimension.
        var (float): Variance.
        len_scale (float): Correlation length scale.
        nugget (float): Nugget effect.
        anis (Optional[List[float]]): Optional anisotropy factors.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        if not hasattr(gs, model_name):
            return {"success": False, "result": None, "error": f"Unknown model: {model_name}"}
        model_cls = getattr(gs, model_name)
        kwargs = {"dim": dim, "var": var, "len_scale": len_scale, "nugget": nugget}
        if anis is not None:
            kwargs["anis"] = anis
        model = model_cls(**kwargs)
        result = {
            "name": model_name,
            "dim": int(model.dim),
            "var": float(model.var),
            "len_scale": float(model.len_scale),
            "nugget": float(model.nugget),
            "has_anis": anis is not None,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="evaluate_covariance", description="Evaluate covariance values for a set of lag distances.")
def evaluate_covariance(
    model_name: str,
    distances: List[float],
    dim: int = 1,
    var: float = 1.0,
    len_scale: float = 1.0,
    nugget: float = 0.0,
) -> dict:
    """
    Compute covariance values at given lag distances for a selected model.

    Parameters:
        model_name (str): Covariance model class name.
        distances (List[float]): Lag distances.
        dim (int): Spatial dimension.
        var (float): Variance.
        len_scale (float): Correlation length.
        nugget (float): Nugget effect.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        if not hasattr(gs, model_name):
            return {"success": False, "result": None, "error": f"Unknown model: {model_name}"}
        model = getattr(gs, model_name)(dim=dim, var=var, len_scale=len_scale, nugget=nugget)
        h = np.asarray(distances, dtype=float)
        cov = model.covariance(h)
        return {"success": True, "result": cov.tolist(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="generate_structured_random_field", description="Generate a structured random field on a regular grid.")
def generate_structured_random_field(
    model_name: str,
    dim: int,
    grid_shape: List[int],
    seed: int = 42,
    var: float = 1.0,
    len_scale: float = 10.0,
    nugget: float = 0.0,
) -> dict:
    """
    Generate a Gaussian random field on a structured grid using GSTools SRF.

    Parameters:
        model_name (str): Covariance model class name.
        dim (int): Spatial dimension.
        grid_shape (List[int]): Grid size per dimension.
        seed (int): Random seed for reproducibility.
        var (float): Variance.
        len_scale (float): Correlation length.
        nugget (float): Nugget effect.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        if len(grid_shape) != dim:
            return {"success": False, "result": None, "error": "grid_shape length must equal dim"}
        if not hasattr(gs, model_name):
            return {"success": False, "result": None, "error": f"Unknown model: {model_name}"}

        model = getattr(gs, model_name)(dim=dim, var=var, len_scale=len_scale, nugget=nugget)
        srf = gs.SRF(model, seed=seed)

        coords = [np.arange(n, dtype=float) for n in grid_shape]
        field = srf.structured(coords)

        stats = {
            "shape": list(field.shape),
            "mean": float(np.mean(field)),
            "std": float(np.std(field)),
            "min": float(np.min(field)),
            "max": float(np.max(field)),
        }
        return {"success": True, "result": stats, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="estimate_variogram", description="Estimate isotropic variogram from positions and values.")
def estimate_variogram(
    positions: List[List[float]],
    values: List[float],
    bin_count: int = 10,
    max_dist: Optional[float] = None,
) -> dict:
    """
    Estimate an empirical variogram from unstructured sample data.

    Parameters:
        positions (List[List[float]]): Coordinates as [[x1, x2, ...], [y1, y2, ...], ...] per dimension.
        values (List[float]): Sample values at coordinates.
        bin_count (int): Number of distance bins.
        max_dist (Optional[float]): Optional maximum lag distance.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        pos_arr = [np.asarray(p, dtype=float) for p in positions]
        val_arr = np.asarray(values, dtype=float)

        if len(pos_arr) == 0:
            return {"success": False, "result": None, "error": "positions must not be empty"}
        n = len(val_arr)
        if any(len(p) != n for p in pos_arr):
            return {"success": False, "result": None, "error": "all position arrays must match values length"}

        bins = np.linspace(0.0, float(max_dist) if max_dist is not None else np.nan, bin_count + 1)
        if max_dist is None:
            bins = bin_count

        bin_center, gamma = gs.vario_estimate(pos_arr, val_arr, bin_edges=bins)
        result = {
            "bin_center": np.asarray(bin_center).tolist(),
            "gamma": np.asarray(gamma).tolist(),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="ordinary_kriging_predict", description="Perform ordinary kriging prediction on query points.")
def ordinary_kriging_predict(
    model_name: str,
    cond_pos: List[List[float]],
    cond_val: List[float],
    query_pos: List[List[float]],
    dim: int,
    var: float = 1.0,
    len_scale: float = 10.0,
    nugget: float = 0.0,
) -> dict:
    """
    Fit ordinary kriging with provided conditions and predict at query positions.

    Parameters:
        model_name (str): Covariance model class name.
        cond_pos (List[List[float]]): Conditioning coordinates per dimension.
        cond_val (List[float]): Conditioning values.
        query_pos (List[List[float]]): Query coordinates per dimension.
        dim (int): Spatial dimension.
        var (float): Variance.
        len_scale (float): Correlation length.
        nugget (float): Nugget effect.

    Returns:
        dict: Standard response with success/result/error.
    """
    try:
        if not hasattr(gs, model_name):
            return {"success": False, "result": None, "error": f"Unknown model: {model_name}"}
        if len(cond_pos) != dim or len(query_pos) != dim:
            return {"success": False, "result": None, "error": "cond_pos/query_pos dimensions must equal dim"}

        cond_arrays = [np.asarray(a, dtype=float) for a in cond_pos]
        query_arrays = [np.asarray(a, dtype=float) for a in query_pos]
        cond_values = np.asarray(cond_val, dtype=float)

        n_cond = len(cond_values)
        if any(len(a) != n_cond for a in cond_arrays):
            return {"success": False, "result": None, "error": "conditioning position lengths must match cond_val"}

        n_query = len(query_arrays[0]) if len(query_arrays) > 0 else 0
        if any(len(a) != n_query for a in query_arrays):
            return {"success": False, "result": None, "error": "query position arrays must have equal lengths"}

        model = getattr(gs, model_name)(dim=dim, var=var, len_scale=len_scale, nugget=nugget)
        ok = gs.krige.Ordinary(model, cond_pos=cond_arrays, cond_val=cond_values)
        pred, var_est = ok(query_arrays, return_var=True)

        result = {
            "prediction": np.asarray(pred).tolist(),
            "variance": np.asarray(var_est).tolist(),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()