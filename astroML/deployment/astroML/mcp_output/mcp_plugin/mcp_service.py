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

from astroML.correlation import two_point, bootstrap_two_point
from astroML.crossmatch import crossmatch_angular
from astroML.cosmology import Cosmology
from astroML.density_estimation.bayesian_blocks import bayesian_blocks
from astroML.density_estimation.density_estimation import KNeighborsDensity
from astroML.fourier import lomb_scargle
from astroML.linear_model.linear_regression import LinearRegression
from astroML.stats.random import bivariate_normal
from astroML.time_series.periodogram import lomb_scargle as ts_lomb_scargle

mcp = FastMCP("astroml_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="two_point_correlation", description="Compute two-point correlation function.")
def two_point_correlation(
    data: List[float],
    bins: List[float],
    method: str = "standard",
    data_random: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Compute the 1D two-point correlation function.

    Parameters:
    - data: Observed sample values.
    - bins: Bin edges for pair counts.
    - method: Estimator method passed to astroML.correlation.two_point.
    - data_random: Optional random catalog sample values.

    Returns:
    - Dict with success/result/error.
    """
    try:
        d = np.asarray(data, dtype=float)
        b = np.asarray(bins, dtype=float)
        r = None if data_random is None else np.asarray(data_random, dtype=float)
        xi = two_point(d, b, method=method, data_R=r)
        return _ok(xi.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="bootstrap_two_point_correlation", description="Compute bootstrapped two-point correlation.")
def bootstrap_two_point_correlation(
    data: List[float],
    bins: List[float],
    n_bootstraps: int = 10,
    method: str = "standard",
) -> Dict[str, Any]:
    """
    Compute bootstrapped two-point correlation statistics.

    Parameters:
    - data: Observed sample values.
    - bins: Bin edges for pair counts.
    - n_bootstraps: Number of bootstrap realizations.
    - method: Estimator method for two-point correlation.

    Returns:
    - Dict with success/result/error.
    """
    try:
        d = np.asarray(data, dtype=float)
        b = np.asarray(bins, dtype=float)
        mu, sigma = bootstrap_two_point(d, b, Nbootstrap=n_bootstraps, method=method)
        return _ok({"mean": mu.tolist(), "std": sigma.tolist()})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="crossmatch_angular", description="Crossmatch two sky catalogs by angular separation.")
def crossmatch_angular_tool(
    ra1: List[float],
    dec1: List[float],
    ra2: List[float],
    dec2: List[float],
    max_distance_deg: float,
) -> Dict[str, Any]:
    """
    Crossmatch two sky-coordinate catalogs.

    Parameters:
    - ra1, dec1: First catalog coordinates in degrees.
    - ra2, dec2: Second catalog coordinates in degrees.
    - max_distance_deg: Maximum matching radius in degrees.

    Returns:
    - Dict with indices and distances for best matches.
    """
    try:
        c1 = np.column_stack([np.asarray(ra1, dtype=float), np.asarray(dec1, dtype=float)])
        c2 = np.column_stack([np.asarray(ra2, dtype=float), np.asarray(dec2, dtype=float)])
        dist, ind = crossmatch_angular(c1, c2, max_distance_deg)
        return _ok({"distance_deg": dist.tolist(), "match_index": ind.tolist()})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="bayesian_blocks_edges", description="Compute Bayesian Blocks edges for event data.")
def bayesian_blocks_edges(
    t: List[float],
    p0: float = 0.05,
) -> Dict[str, Any]:
    """
    Compute adaptive histogram segmentation using Bayesian Blocks.

    Parameters:
    - t: Event times or scalar observations.
    - p0: False alarm probability prior.

    Returns:
    - Dict containing block edges.
    """
    try:
        arr = np.asarray(t, dtype=float)
        edges = bayesian_blocks(arr, p0=p0)
        return _ok(edges.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="kneighbors_density_score", description="Estimate density scores with k-nearest neighbors.")
def kneighbors_density_score(
    train_data: List[List[float]],
    query_data: List[List[float]],
    n_neighbors: int = 10,
    method: str = "simple",
) -> Dict[str, Any]:
    """
    Fit KNN density estimator and score query points.

    Parameters:
    - train_data: Training samples (n_samples, n_features).
    - query_data: Query samples (m_samples, n_features).
    - n_neighbors: Number of neighbors.
    - method: Estimation strategy.

    Returns:
    - Dict with log-density scores.
    """
    try:
        x_train = np.asarray(train_data, dtype=float)
        x_query = np.asarray(query_data, dtype=float)
        kde = KNeighborsDensity(method=method, n_neighbors=n_neighbors)
        kde.fit(x_train)
        scores = kde.score_samples(x_query)
        return _ok(scores.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="lomb_scargle_periodogram", description="Compute Lomb-Scargle periodogram from uneven samples.")
def lomb_scargle_periodogram(
    t: List[float],
    y: List[float],
    dy: List[float],
    omega: List[float],
) -> Dict[str, Any]:
    """
    Compute Lomb-Scargle power spectrum.

    Parameters:
    - t: Observation times.
    - y: Observed values.
    - dy: Measurement uncertainties.
    - omega: Angular frequencies to evaluate.

    Returns:
    - Dict with periodogram powers.
    """
    try:
        tt = np.asarray(t, dtype=float)
        yy = np.asarray(y, dtype=float)
        ddy = np.asarray(dy, dtype=float)
        ww = np.asarray(omega, dtype=float)
        power = lomb_scargle(tt, yy, ddy, ww)
        return _ok(power.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="time_series_lomb_scargle", description="Compute time_series Lomb-Scargle periodogram variant.")
def time_series_lomb_scargle(
    t: List[float],
    y: List[float],
    dy: List[float],
    omega: List[float],
) -> Dict[str, Any]:
    """
    Compute Lomb-Scargle periodogram via astroML.time_series.periodogram.

    Parameters:
    - t: Observation times.
    - y: Observed values.
    - dy: Measurement uncertainties.
    - omega: Angular frequencies.

    Returns:
    - Dict with periodogram powers.
    """
    try:
        tt = np.asarray(t, dtype=float)
        yy = np.asarray(y, dtype=float)
        ddy = np.asarray(dy, dtype=float)
        ww = np.asarray(omega, dtype=float)
        power = ts_lomb_scargle(tt, yy, ddy, ww)
        return _ok(power.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="linear_regression_fit_predict", description="Fit astroML linear regression and predict.")
def linear_regression_fit_predict(
    x_train: List[List[float]],
    y_train: List[float],
    x_predict: List[List[float]],
    regularization: str = "none",
) -> Dict[str, Any]:
    """
    Fit LinearRegression and predict outputs.

    Parameters:
    - x_train: Training features.
    - y_train: Training targets.
    - x_predict: Feature matrix for prediction.
    - regularization: Regularization mode supported by astroML LinearRegression.

    Returns:
    - Dict with predictions.
    """
    try:
        xt = np.asarray(x_train, dtype=float)
        yt = np.asarray(y_train, dtype=float)
        xp = np.asarray(x_predict, dtype=float)
        model = LinearRegression(regularization=regularization)
        model.fit(xt, yt)
        pred = model.predict(xp)
        return _ok(pred.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="bivariate_normal_sample", description="Sample from a bivariate normal distribution.")
def bivariate_normal_sample(
    mu_x: float,
    mu_y: float,
    sigma_x: float,
    sigma_y: float,
    alpha: float,
    size: int = 100,
    random_state: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Draw random samples from astroML.stats.random.bivariate_normal.

    Parameters:
    - mu_x, mu_y: Mean values.
    - sigma_x, sigma_y: Standard deviations.
    - alpha: Correlation angle/parameter as defined by astroML.
    - size: Number of samples.
    - random_state: Seed for reproducibility.

    Returns:
    - Dict with sampled x and y arrays.
    """
    try:
        rng = np.random.RandomState(random_state) if random_state is not None else np.random
        x, y = bivariate_normal(mu=[mu_x, mu_y], sigma_1=sigma_x, sigma_2=sigma_y, alpha=alpha, size=size, return_cov=False, random_state=rng)
        return _ok({"x": np.asarray(x).tolist(), "y": np.asarray(y).tolist()})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="cosmology_distance_modulus", description="Compute cosmological distance modulus for redshifts.")
def cosmology_distance_modulus(
    redshift: List[float],
    omega_m: float = 0.27,
    omega_l: float = 0.73,
    h: float = 0.71,
) -> Dict[str, Any]:
    """
    Compute distance modulus using astroML.cosmology.Cosmology.

    Parameters:
    - redshift: Redshift values.
    - omega_m: Matter density parameter.
    - omega_l: Dark energy density parameter.
    - h: Hubble parameter scaling.

    Returns:
    - Dict with distance modulus values.
    """
    try:
        z = np.asarray(redshift, dtype=float)
        cosmo = Cosmology(omegaM=omega_m, omegaL=omega_l, h=h)
        dm = cosmo.mu(z)
        return _ok(np.asarray(dm).tolist())
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()