import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import scvelo as scv

mcp = FastMCP("scvelo_service")


def _ok(result: Any) -> dict:
    return {"success": True, "result": result, "error": ""}


def _err(error: Exception) -> dict:
    return {"success": False, "result": None, "error": str(error)}


@mcp.tool(name="datasets_list", description="List available dataset loader functions in scvelo.datasets.")
def datasets_list() -> dict:
    """
    List public dataset loader names from scvelo.datasets.

    Returns:
        dict: Standard response with list of dataset function names.
    """
    try:
        names = [
            n
            for n in dir(scv.datasets)
            if not n.startswith("_") and callable(getattr(scv.datasets, n))
        ]
        return _ok(sorted(names))
    except Exception as e:
        return _err(e)


@mcp.tool(name="read_data", description="Read AnnData from file using scvelo.read.")
def read_data(path: str, cache: bool = False) -> dict:
    """
    Read data into AnnData using scvelo.read.

    Parameters:
        path (str): Path to input file.
        cache (bool): Whether to use scanpy/scvelo caching.

    Returns:
        dict: Standard response containing AnnData shape metadata.
    """
    try:
        adata = scv.read(path, cache=cache)
        result = {
            "n_obs": int(adata.n_obs),
            "n_vars": int(adata.n_vars),
            "obs_keys": list(adata.obs_keys()),
            "var_keys": list(adata.var_keys()),
            "layers": list(adata.layers.keys()),
        }
        return _ok(result)
    except Exception as e:
        return _err(e)


@mcp.tool(name="pp_filter_and_normalize", description="Run scvelo preprocessing filter_and_normalize.")
def pp_filter_and_normalize(
    path: str,
    min_shared_counts: int = 20,
    n_top_genes: int = 2000,
    log_transform: bool = True,
) -> dict:
    """
    Apply scv.pp.filter_and_normalize to a dataset loaded from path.

    Parameters:
        path (str): Input AnnData path.
        min_shared_counts (int): Minimum shared counts threshold.
        n_top_genes (int): Number of top genes to keep.
        log_transform (bool): Whether to apply log1p transform.

    Returns:
        dict: Standard response with updated matrix shape.
    """
    try:
        adata = scv.read(path)
        scv.pp.filter_and_normalize(
            adata,
            min_shared_counts=min_shared_counts,
            n_top_genes=n_top_genes,
            log=log_transform,
        )
        return _ok({"n_obs": int(adata.n_obs), "n_vars": int(adata.n_vars)})
    except Exception as e:
        return _err(e)


@mcp.tool(name="pp_moments", description="Compute moments after neighbors graph construction.")
def pp_moments(path: str, n_pcs: int = 30, n_neighbors: int = 30) -> dict:
    """
    Compute moments using scvelo preprocessing.

    Parameters:
        path (str): Input AnnData path.
        n_pcs (int): Number of principal components.
        n_neighbors (int): Number of neighbors for graph construction.

    Returns:
        dict: Standard response with layers/obsp metadata.
    """
    try:
        adata = scv.read(path)
        scv.pp.moments(adata, n_pcs=n_pcs, n_neighbors=n_neighbors)
        return _ok(
            {
                "layers": list(adata.layers.keys()),
                "obsp_keys": list(adata.obsp.keys()),
                "uns_keys": list(adata.uns.keys()),
            }
        )
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_recover_dynamics", description="Fit dynamical model parameters with scvelo.")
def tl_recover_dynamics(path: str, n_jobs: int = 1) -> dict:
    """
    Recover transcriptional dynamics for genes.

    Parameters:
        path (str): Input AnnData path.
        n_jobs (int): Number of parallel jobs.

    Returns:
        dict: Standard response with learned parameter keys in var.
    """
    try:
        adata = scv.read(path)
        scv.tl.recover_dynamics(adata, n_jobs=n_jobs)
        var_keys = list(adata.var_keys())
        learned = [k for k in var_keys if "fit_" in k or "velocity" in k]
        return _ok({"var_keys_count": len(var_keys), "learned_keys": learned})
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_velocity", description="Compute RNA velocity.")
def tl_velocity(path: str, mode: str = "stochastic") -> dict:
    """
    Compute RNA velocity vectors.

    Parameters:
        path (str): Input AnnData path.
        mode (str): Velocity mode, e.g. 'stochastic' or 'dynamical'.

    Returns:
        dict: Standard response with created layers.
    """
    try:
        adata = scv.read(path)
        scv.tl.velocity(adata, mode=mode)
        return _ok({"layers": list(adata.layers.keys())})
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_velocity_graph", description="Compute velocity graph.")
def tl_velocity_graph(path: str, n_jobs: int = 1) -> dict:
    """
    Compute transition graph from velocity estimates.

    Parameters:
        path (str): Input AnnData path.
        n_jobs (int): Number of parallel jobs.

    Returns:
        dict: Standard response with graph-related keys.
    """
    try:
        adata = scv.read(path)
        scv.tl.velocity_graph(adata, n_jobs=n_jobs)
        return _ok({"uns_keys": list(adata.uns.keys()), "obsp_keys": list(adata.obsp.keys())})
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_velocity_pseudotime", description="Compute velocity pseudotime.")
def tl_velocity_pseudotime(path: str) -> dict:
    """
    Compute velocity pseudotime trajectory.

    Parameters:
        path (str): Input AnnData path.

    Returns:
        dict: Standard response with pseudotime availability.
    """
    try:
        adata = scv.read(path)
        scv.tl.velocity_pseudotime(adata)
        has_key = "velocity_pseudotime" in adata.obs_keys()
        return _ok({"velocity_pseudotime_in_obs": has_key})
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_rank_velocity_genes", description="Rank genes by velocity signal.")
def tl_rank_velocity_genes(path: str, groupby: str) -> dict:
    """
    Rank velocity genes per group.

    Parameters:
        path (str): Input AnnData path.
        groupby (str): Obs column for grouping cells.

    Returns:
        dict: Standard response with ranking metadata keys.
    """
    try:
        adata = scv.read(path)
        scv.tl.rank_velocity_genes(adata, groupby=groupby)
        keys = [k for k in adata.uns.keys() if "rank_velocity_genes" in k]
        return _ok({"uns_rank_keys": keys})
    except Exception as e:
        return _err(e)


@mcp.tool(name="tl_terminal_states", description="Estimate root and terminal states.")
def tl_terminal_states(path: str) -> dict:
    """
    Estimate terminal and root states.

    Parameters:
        path (str): Input AnnData path.

    Returns:
        dict: Standard response with state-related obs keys.
    """
    try:
        adata = scv.read(path)
        scv.tl.terminal_states(adata)
        obs_keys = list(adata.obs_keys())
        state_keys = [k for k in obs_keys if "root" in k or "end" in k or "terminal" in k]
        return _ok({"state_obs_keys": state_keys})
    except Exception as e:
        return _err(e)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()