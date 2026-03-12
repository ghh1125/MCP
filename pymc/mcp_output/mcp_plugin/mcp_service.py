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
import pymc as pm
import arviz as az
import numpy as np
import pandas as pd


mcp = FastMCP("pymc_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="get_pymc_version", description="Get installed PyMC version information.")
def get_pymc_version() -> Dict[str, Any]:
    """
    Retrieve version metadata for PyMC and key companion libraries.

    Returns:
        Dict[str, Any]: Standard response dictionary with version values.
    """
    try:
        result = {
            "pymc": getattr(pm, "__version__", "unknown"),
            "arviz": getattr(az, "__version__", "unknown"),
            "numpy": getattr(np, "__version__", "unknown"),
            "pandas": getattr(pd, "__version__", "unknown"),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_pymc_distributions", description="List available PyMC distributions.")
def list_pymc_distributions(include_prefix: Optional[str] = None) -> Dict[str, Any]:
    """
    List distribution classes exported by pymc.distributions.

    Args:
        include_prefix: Optional name prefix filter.

    Returns:
        Dict[str, Any]: Standard response dictionary with a list of distribution names.
    """
    try:
        import pymc.distributions as pmd

        names: List[str] = []
        for attr in dir(pmd):
            if attr.startswith("_"):
                continue
            obj = getattr(pmd, attr, None)
            if isinstance(obj, type):
                names.append(attr)

        names = sorted(set(names))
        if include_prefix:
            names = [n for n in names if n.startswith(include_prefix)]
        return _ok(names)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="sample_prior_predictive_normal", description="Run prior predictive sampling for a simple Normal model.")
def sample_prior_predictive_normal(
    mu: float = 0.0,
    sigma: float = 1.0,
    draws: int = 500,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Build a minimal Normal model and sample from the prior predictive distribution.

    Args:
        mu: Mean of the Normal prior.
        sigma: Standard deviation of the Normal prior.
        draws: Number of prior predictive draws.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict[str, Any]: Standard response dictionary with sample summary.
    """
    try:
        with pm.Model() as model:
            pm.Normal("x", mu=mu, sigma=sigma)
            idata = pm.sample_prior_predictive(samples=draws, random_seed=random_seed)

        arr = idata.prior["x"].values
        result = {
            "variable": "x",
            "shape": list(arr.shape),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="fit_normal_model", description="Fit a simple Normal model with NUTS and return posterior summaries.")
def fit_normal_model(
    data: List[float],
    draws: int = 500,
    tune: int = 500,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit a univariate Normal model to observed data and return posterior diagnostics.

    Args:
        data: Observed numeric data points.
        draws: Number of posterior draws per chain.
        tune: Number of tuning iterations per chain.
        chains: Number of MCMC chains.
        target_accept: NUTS target acceptance probability.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict[str, Any]: Standard response dictionary with posterior summaries.
    """
    try:
        if len(data) < 2:
            return _err("data must contain at least 2 values")

        observed = np.asarray(data, dtype=float)
        with pm.Model() as model:
            mu = pm.Normal("mu", mu=float(np.mean(observed)), sigma=10.0)
            sigma = pm.HalfNormal("sigma", sigma=10.0)
            pm.Normal("y", mu=mu, sigma=sigma, observed=observed)
            idata = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=random_seed,
                progressbar=False,
            )

        summary_df = az.summary(idata, var_names=["mu", "sigma"])
        result = {
            "posterior_summary": summary_df.to_dict(orient="index"),
            "n_observations": int(observed.size),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="posterior_predictive_normal", description="Fit a Normal model and generate posterior predictive samples.")
def posterior_predictive_normal(
    data: List[float],
    draws: int = 300,
    tune: int = 300,
    chains: int = 2,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit a Normal likelihood model and sample posterior predictive values.

    Args:
        data: Observed numeric data points.
        draws: Number of posterior draws per chain.
        tune: Number of tuning draws per chain.
        chains: Number of MCMC chains.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict[str, Any]: Standard response dictionary with predictive sample statistics.
    """
    try:
        observed = np.asarray(data, dtype=float)
        if observed.size == 0:
            return _err("data cannot be empty")

        with pm.Model() as model:
            mu = pm.Normal("mu", mu=0.0, sigma=10.0)
            sigma = pm.HalfNormal("sigma", sigma=10.0)
            pm.Normal("y", mu=mu, sigma=sigma, observed=observed)
            idata = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                random_seed=random_seed,
                progressbar=False,
            )
            ppc = pm.sample_posterior_predictive(
                idata,
                var_names=["y"],
                random_seed=random_seed,
                progressbar=False,
            )

        ppc_arr = ppc.posterior_predictive["y"].values
        result = {
            "shape": list(ppc_arr.shape),
            "mean": float(np.mean(ppc_arr)),
            "std": float(np.std(ppc_arr)),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="compute_waic_normal_models", description="Compare one-group vs two-group Normal models using WAIC.")
def compute_waic_normal_models(
    data: List[float],
    split_index: int,
    draws: int = 400,
    tune: int = 400,
    chains: int = 2,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit two candidate models and compare them via WAIC.

    Args:
        data: Observed values.
        split_index: Index that separates data into group A and B for the two-group model.
        draws: Number of posterior draws per chain.
        tune: Number of tuning draws per chain.
        chains: Number of chains.
        random_seed: Random seed.

    Returns:
        Dict[str, Any]: Standard response dictionary with WAIC comparison table.
    """
    try:
        y = np.asarray(data, dtype=float)
        if y.size < 4:
            return _err("data must contain at least 4 values")
        if split_index <= 0 or split_index >= y.size:
            return _err("split_index must be between 1 and len(data)-1")

        with pm.Model() as m1:
            mu = pm.Normal("mu", mu=0.0, sigma=10.0)
            sigma = pm.HalfNormal("sigma", sigma=10.0)
            pm.Normal("y", mu=mu, sigma=sigma, observed=y)
            idata1 = pm.sample(
                draws=draws, tune=tune, chains=chains, random_seed=random_seed, progressbar=False
            )

        y1 = y[:split_index]
        y2 = y[split_index:]
        with pm.Model() as m2:
            mu1 = pm.Normal("mu1", mu=0.0, sigma=10.0)
            mu2 = pm.Normal("mu2", mu=0.0, sigma=10.0)
            sigma = pm.HalfNormal("sigma", sigma=10.0)
            pm.Normal("y1", mu=mu1, sigma=sigma, observed=y1)
            pm.Normal("y2", mu=mu2, sigma=sigma, observed=y2)
            idata2 = pm.sample(
                draws=draws, tune=tune, chains=chains, random_seed=random_seed, progressbar=False
            )

        cmp = az.compare({"one_group": idata1, "two_group": idata2}, ic="waic")
        return _ok(cmp.reset_index().to_dict(orient="records"))
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()