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

try:
    import scanpy as sc
except Exception:
    from src.scanpy import __init__ as sc  # type: ignore

mcp = FastMCP("scanpy_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="scanpy_version", description="Get installed Scanpy version information.")
def scanpy_version() -> Dict[str, Any]:
    """
    Return Scanpy version.

    Returns:
        Dict with success/result/error. result is the version string.
    """
    try:
        version = getattr(sc, "__version__", "unknown")
        return _ok(version)
    except Exception as e:
        return _err(e)


@mcp.tool(
    name="load_builtin_dataset",
    description="Load a built-in Scanpy dataset by name.",
)
def load_builtin_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Load a Scanpy built-in dataset.

    Parameters:
        dataset_name: Name of dataset function under sc.datasets (e.g., 'pbmc3k').

    Returns:
        Dict with success/result/error. result includes shape and metadata keys.
    """
    try:
        if not hasattr(sc.datasets, dataset_name):
            raise ValueError(f"Unknown dataset: {dataset_name}")
        ds_fn = getattr(sc.datasets, dataset_name)
        adata = ds_fn()
        return _ok(
            {
                "dataset": dataset_name,
                "n_obs": int(adata.n_obs),
                "n_vars": int(adata.n_vars),
                "obs_columns": list(map(str, adata.obs.columns.tolist())),
                "var_columns": list(map(str, adata.var.columns.tolist())),
            }
        )
    except Exception as e:
        return _err(e)


@mcp.tool(
    name="read_h5ad_summary",
    description="Read an .h5ad file and return high-level summary.",
)
def read_h5ad_summary(path: str) -> Dict[str, Any]:
    """
    Read AnnData from disk and return summary stats.

    Parameters:
        path: Path to .h5ad file.

    Returns:
        Dict with success/result/error. result includes dimensions and annotation keys.
    """
    try:
        adata = sc.read_h5ad(path)
        return _ok(
            {
                "path": path,
                "n_obs": int(adata.n_obs),
                "n_vars": int(adata.n_vars),
                "obs_keys": list(map(str, adata.obs_keys())),
                "var_keys": list(map(str, adata.var_keys())),
                "obsm_keys": list(map(str, adata.obsm_keys())),
                "uns_keys": list(map(str, adata.uns_keys())),
            }
        )
    except Exception as e:
        return _err(e)


@mcp.tool(
    name="preprocess_basic",
    description="Run standard Scanpy preprocessing pipeline on a dataset.",
)
def preprocess_basic(
    dataset_name: str = "pbmc3k",
    min_genes: int = 200,
    min_cells: int = 3,
    target_sum: float = 10000.0,
    n_top_genes: int = 2000,
    max_n_genes_by_counts: Optional[int] = None,
    max_pct_counts_mt: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Execute a lightweight preprocessing workflow.

    Parameters:
        dataset_name: Built-in Scanpy dataset loader name.
        min_genes: Minimum genes per cell filter.
        min_cells: Minimum cells per gene filter.
        target_sum: Total-count normalization target.
        n_top_genes: Number of HVGs to keep.
        max_n_genes_by_counts: Optional cell QC upper bound.
        max_pct_counts_mt: Optional mitochondrial percentage upper bound.

    Returns:
        Dict with success/result/error. result includes filtered dimensions and HVG count.
    """
    try:
        if not hasattr(sc.datasets, dataset_name):
            raise ValueError(f"Unknown dataset: {dataset_name}")
        adata = getattr(sc.datasets, dataset_name)()

        sc.pp.filter_cells(adata, min_genes=min_genes)
        sc.pp.filter_genes(adata, min_cells=min_cells)

        adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
        sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

        if max_n_genes_by_counts is not None:
            adata = adata[adata.obs["n_genes_by_counts"] < max_n_genes_by_counts].copy()
        if max_pct_counts_mt is not None and "pct_counts_mt" in adata.obs:
            adata = adata[adata.obs["pct_counts_mt"] < max_pct_counts_mt].copy()

        sc.pp.normalize_total(adata, target_sum=target_sum)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, inplace=True)

        hvg_count = int(adata.var["highly_variable"].sum()) if "highly_variable" in adata.var else 0
        return _ok(
            {
                "dataset": dataset_name,
                "n_obs": int(adata.n_obs),
                "n_vars": int(adata.n_vars),
                "highly_variable_genes": hvg_count,
            }
        )
    except Exception as e:
        return _err(e)


@mcp.tool(
    name="compute_neighbors_and_umap",
    description="Compute PCA, neighborhood graph, and UMAP embedding.",
)
def compute_neighbors_and_umap(
    dataset_name: str = "pbmc3k",
    n_pcs: int = 30,
    n_neighbors: int = 10,
    random_state: int = 0,
) -> Dict[str, Any]:
    """
    Run dimensionality reduction and graph embedding workflow.

    Parameters:
        dataset_name: Built-in Scanpy dataset loader name.
        n_pcs: Number of principal components for neighbors graph.
        n_neighbors: Number of neighbors in graph construction.
        random_state: Random seed for PCA/UMAP reproducibility.

    Returns:
        Dict with success/result/error. result includes embedding presence and shape.
    """
    try:
        if not hasattr(sc.datasets, dataset_name):
            raise ValueError(f"Unknown dataset: {dataset_name}")
        adata = getattr(sc.datasets, dataset_name)()

        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=2000, inplace=True)
        if "highly_variable" in adata.var:
            adata = adata[:, adata.var["highly_variable"]].copy()

        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, svd_solver="arpack", random_state=random_state)
        sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs)
        sc.tl.umap(adata, random_state=random_state)

        umap = adata.obsm.get("X_umap")
        umap_shape: List[int] = list(umap.shape) if umap is not None else [0, 0]

        return _ok(
            {
                "dataset": dataset_name,
                "n_obs": int(adata.n_obs),
                "n_vars": int(adata.n_vars),
                "umap_shape": umap_shape,
                "obsm_keys": list(map(str, adata.obsm_keys())),
            }
        )
    except Exception as e:
        return _err(e)


@mcp.tool(
    name="cluster_leiden",
    description="Run Leiden clustering after neighbors graph construction.",
)
def cluster_leiden(
    dataset_name: str = "pbmc3k",
    resolution: float = 1.0,
    n_neighbors: int = 10,
    n_pcs: int = 30,
) -> Dict[str, Any]:
    """
    Perform Leiden clustering on a built-in dataset.

    Parameters:
        dataset_name: Built-in Scanpy dataset loader name.
        resolution: Leiden resolution parameter.
        n_neighbors: Graph neighbor count.
        n_pcs: Number of PCs for graph construction.

    Returns:
        Dict with success/result/error. result includes cluster labels and counts.
    """
    try:
        if not hasattr(sc.datasets, dataset_name):
            raise ValueError(f"Unknown dataset: {dataset_name}")
        adata = getattr(sc.datasets, dataset_name)()

        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=2000, inplace=True)
        if "highly_variable" in adata.var:
            adata = adata[:, adata.var["highly_variable"]].copy()

        sc.pp.pca(adata)
        sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs)
        sc.tl.leiden(adata, resolution=resolution)

        counts = adata.obs["leiden"].value_counts().to_dict()
        return _ok(
            {
                "dataset": dataset_name,
                "resolution": resolution,
                "n_clusters": int(len(counts)),
                "cluster_counts": {str(k): int(v) for k, v in counts.items()},
            }
        )
    except Exception as e:
        return _err(e)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()