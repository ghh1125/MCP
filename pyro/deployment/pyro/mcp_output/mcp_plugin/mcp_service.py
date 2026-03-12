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

import pyro
import pyro.infer
import pyro.infer.mcmc
import pyro.optim
import pyro.poutine
import pyro.distributions as dist
import torch

mcp = FastMCP("pyro_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="get_pyro_version", description="Get installed Pyro and Torch versions.")
def get_pyro_version() -> Dict[str, Any]:
    """
    Retrieve runtime version metadata for core probabilistic programming dependencies.

    Returns:
        dict: Standard response containing versions for pyro and torch.
    """
    try:
        return _ok({"pyro_version": pyro.__version__, "torch_version": torch.__version__})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="clear_param_store",
    description="Clear Pyro global parameter store to reset model/guide parameters.",
)
def clear_param_store() -> Dict[str, Any]:
    """
    Clear the global Pyro parameter store.

    Returns:
        dict: Standard response indicating whether the store was cleared.
    """
    try:
        pyro.clear_param_store()
        return _ok("Parameter store cleared.")
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="sample_normal",
    description="Draw samples from a Normal distribution using pyro.distributions.",
)
def sample_normal(loc: float, scale: float, num_samples: int = 1, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Sample values from a Normal distribution.

    Args:
        loc: Mean of the Normal distribution.
        scale: Standard deviation of the Normal distribution; must be > 0.
        num_samples: Number of iid samples to draw.
        seed: Optional random seed for deterministic draws.

    Returns:
        dict: Standard response containing sampled values.
    """
    try:
        if scale <= 0:
            return _err("scale must be > 0")
        if num_samples <= 0:
            return _err("num_samples must be > 0")
        if seed is not None:
            pyro.set_rng_seed(seed)
        d = dist.Normal(torch.tensor(loc), torch.tensor(scale))
        samples = d.sample((num_samples,))
        return _ok(samples.detach().cpu().tolist())
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="run_svi_linear_regression",
    description="Run SVI on a Bayesian linear regression model and return learned parameters.",
)
def run_svi_linear_regression(
    x_values: List[float],
    y_values: List[float],
    num_steps: int = 500,
    lr: float = 0.02,
    seed: Optional[int] = 0,
) -> Dict[str, Any]:
    """
    Fit a simple Bayesian linear regression model using SVI.

    Args:
        x_values: Input feature values.
        y_values: Target values with same length as x_values.
        num_steps: Number of SVI optimization steps.
        lr: Learning rate for Adam optimizer.
        seed: Optional random seed.

    Returns:
        dict: Standard response containing loss trace summary and posterior parameter estimates.
    """
    try:
        if len(x_values) == 0 or len(y_values) == 0:
            return _err("x_values and y_values must be non-empty")
        if len(x_values) != len(y_values):
            return _err("x_values and y_values must have same length")
        if num_steps <= 0:
            return _err("num_steps must be > 0")
        if lr <= 0:
            return _err("lr must be > 0")

        if seed is not None:
            pyro.set_rng_seed(seed)
        pyro.clear_param_store()

        x = torch.tensor(x_values, dtype=torch.float32)
        y = torch.tensor(y_values, dtype=torch.float32)

        def model(x_data: torch.Tensor, y_data: torch.Tensor) -> None:
            w = pyro.sample("w", dist.Normal(torch.tensor(0.0), torch.tensor(10.0)))
            b = pyro.sample("b", dist.Normal(torch.tensor(0.0), torch.tensor(10.0)))
            sigma = pyro.sample("sigma", dist.LogNormal(torch.tensor(0.0), torch.tensor(0.5)))
            mean = w * x_data + b
            with pyro.plate("data", x_data.shape[0]):
                pyro.sample("obs", dist.Normal(mean, sigma), obs=y_data)

        def guide(x_data: torch.Tensor, y_data: torch.Tensor) -> None:
            w_loc = pyro.param("w_loc", torch.tensor(0.0))
            w_scale = pyro.param("w_scale", torch.tensor(1.0), constraint=dist.constraints.positive)
            b_loc = pyro.param("b_loc", torch.tensor(0.0))
            b_scale = pyro.param("b_scale", torch.tensor(1.0), constraint=dist.constraints.positive)
            sigma_loc = pyro.param("sigma_loc", torch.tensor(0.0))
            sigma_scale = pyro.param("sigma_scale", torch.tensor(0.5), constraint=dist.constraints.positive)

            pyro.sample("w", dist.Normal(w_loc, w_scale))
            pyro.sample("b", dist.Normal(b_loc, b_scale))
            pyro.sample("sigma", dist.LogNormal(sigma_loc, sigma_scale))

        optimizer = pyro.optim.Adam({"lr": lr})
        svi = pyro.infer.SVI(model=model, guide=guide, optim=optimizer, loss=pyro.infer.Trace_ELBO())

        losses: List[float] = []
        for _ in range(num_steps):
            loss = svi.step(x, y)
            losses.append(float(loss))

        result = {
            "final_loss": losses[-1],
            "initial_loss": losses[0],
            "w_loc": float(pyro.param("w_loc").item()),
            "b_loc": float(pyro.param("b_loc").item()),
            "sigma_median": float(torch.exp(pyro.param("sigma_loc")).item()),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="run_hmc_normal_mean",
    description="Run HMC to infer the mean of a Normal likelihood with known scale.",
)
def run_hmc_normal_mean(
    observations: List[float],
    known_scale: float = 1.0,
    num_samples: int = 200,
    warmup_steps: int = 100,
    seed: Optional[int] = 0,
) -> Dict[str, Any]:
    """
    Perform MCMC inference (HMC) for a scalar Normal mean parameter.

    Args:
        observations: Observed scalar data.
        known_scale: Known observation std-dev, must be > 0.
        num_samples: Number of posterior samples.
        warmup_steps: Number of warmup/adaptation steps.
        seed: Optional random seed.

    Returns:
        dict: Standard response with posterior summary and raw mean samples.
    """
    try:
        if len(observations) == 0:
            return _err("observations must be non-empty")
        if known_scale <= 0:
            return _err("known_scale must be > 0")
        if num_samples <= 0:
            return _err("num_samples must be > 0")
        if warmup_steps < 0:
            return _err("warmup_steps must be >= 0")

        if seed is not None:
            pyro.set_rng_seed(seed)

        obs = torch.tensor(observations, dtype=torch.float32)

        def model(data: torch.Tensor) -> None:
            mu = pyro.sample("mu", dist.Normal(torch.tensor(0.0), torch.tensor(10.0)))
            with pyro.plate("data", data.shape[0]):
                pyro.sample("obs", dist.Normal(mu, torch.tensor(known_scale)), obs=data)

        kernel = pyro.infer.mcmc.HMC(model, step_size=0.1, num_steps=4)
        mcmc = pyro.infer.mcmc.MCMC(kernel, num_samples=num_samples, warmup_steps=warmup_steps)
        mcmc.run(obs)
        samples = mcmc.get_samples()["mu"].detach().cpu()
        return _ok(
            {
                "posterior_mean": float(samples.mean().item()),
                "posterior_std": float(samples.std(unbiased=False).item()),
                "samples": samples.tolist(),
            }
        )
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="trace_model_sites",
    description="Trace a simple probabilistic model and return site metadata via poutine.",
)
def trace_model_sites(seed: int = 0) -> Dict[str, Any]:
    """
    Run a small model under poutine.trace and return sample-site details.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        dict: Standard response with traced sample node names and values.
    """
    try:
        pyro.set_rng_seed(seed)

        def model() -> torch.Tensor:
            z = pyro.sample("z", dist.Normal(torch.tensor(0.0), torch.tensor(1.0)))
            x = pyro.sample("x", dist.Normal(z, torch.tensor(1.0)))
            return x

        tr = pyro.poutine.trace(model).get_trace()
        sample_nodes = {}
        for name, node in tr.nodes.items():
            if node.get("type") == "sample":
                val = node.get("value")
                if torch.is_tensor(val):
                    sample_nodes[name] = val.detach().cpu().tolist()
                else:
                    sample_nodes[name] = val
        return _ok(sample_nodes)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()