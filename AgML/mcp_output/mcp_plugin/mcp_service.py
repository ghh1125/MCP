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

mcp = FastMCP("agml_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


def _import_agml():
    try:
        import agml  # type: ignore
        return agml, None
    except Exception as e:
        return None, str(e)


@mcp.tool(
    name="agml_health_check",
    description="Check whether AgML is importable and report version details.",
)
def agml_health_check() -> Dict[str, Any]:
    """
    Validate AgML importability.

    Returns:
        Dict containing:
        - success: bool indicating operation success.
        - result: Version and basic module info when successful.
        - error: Error message if import failed.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")
    version = getattr(agml, "__version__", None)
    return _ok({"module": "agml", "version": version})


@mcp.tool(
    name="list_public_datasets",
    description="List AgML public dataset names.",
)
def list_public_datasets() -> Dict[str, Any]:
    """
    Return all publicly listed AgML datasets.

    Returns:
        Dict with success/result/error.
        result is expected to be a list of dataset names.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")
    try:
        datasets = agml.data.public_data_sources()  # type: ignore[attr-defined]
        return _ok(list(datasets))
    except Exception:
        try:
            from agml.data import public as public_mod  # type: ignore

            if hasattr(public_mod, "public_data_sources"):
                datasets = public_mod.public_data_sources()
                return _ok(list(datasets))
            return _err("No compatible public dataset listing API found.")
        except Exception as e:
            return _err(f"Failed to list datasets: {e}")


@mcp.tool(
    name="validate_dataset_name",
    description="Validate whether a dataset name exists in AgML public sources.",
)
def validate_dataset_name(dataset_name: str) -> Dict[str, Any]:
    """
    Validate a dataset name against AgML public datasets.

    Parameters:
        dataset_name: Dataset identifier to validate.

    Returns:
        Dict with success/result/error.
        result contains validity and close matches.
    """
    all_ds_resp = list_public_datasets()
    if not all_ds_resp["success"]:
        return all_ds_resp
    datasets: List[str] = all_ds_resp["result"]
    valid = dataset_name in datasets
    matches = [d for d in datasets if dataset_name.lower() in d.lower()][:15]
    return _ok({"valid": valid, "matches": matches})


@mcp.tool(
    name="get_dataset_metadata",
    description="Retrieve metadata for a specific AgML dataset.",
)
def get_dataset_metadata(dataset_name: str) -> Dict[str, Any]:
    """
    Fetch dataset metadata from AgML.

    Parameters:
        dataset_name: Name of a public AgML dataset.

    Returns:
        Dict with success/result/error.
        result includes structured metadata when available.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")

    try:
        from agml.data import metadata as metadata_mod  # type: ignore

        if hasattr(metadata_mod, "DatasetMetadata"):
            meta_obj = metadata_mod.DatasetMetadata(dataset_name)
            data = {}
            for key in dir(meta_obj):
                if key.startswith("_"):
                    continue
                try:
                    value = getattr(meta_obj, key)
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        data[key] = value
                except Exception:
                    continue
            return _ok(data)
    except Exception:
        pass

    try:
        loader = agml.data.AgMLDataLoader(dataset_name)  # type: ignore[attr-defined]
        summary = {
            "dataset_name": dataset_name,
            "num_images": getattr(loader, "num_images", None),
            "task": getattr(loader, "task", None),
            "classes": getattr(loader, "classes", None),
        }
        return _ok(summary)
    except Exception as e:
        return _err(f"Failed to get metadata for '{dataset_name}': {e}")


@mcp.tool(
    name="show_dataset_splits",
    description="Show available splits and split sizes for a dataset.",
)
def show_dataset_splits(dataset_name: str) -> Dict[str, Any]:
    """
    Provide split information for an AgML dataset.

    Parameters:
        dataset_name: Name of the dataset.

    Returns:
        Dict with success/result/error.
        result includes split-related information if available.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")

    try:
        loader = agml.data.AgMLDataLoader(dataset_name)  # type: ignore[attr-defined]
        result = {}
        for attr in ["splits", "split", "train_data", "val_data", "test_data", "num_images"]:
            if hasattr(loader, attr):
                try:
                    value = getattr(loader, attr)
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        result[attr] = value
                    else:
                        result[attr] = str(type(value))
                except Exception:
                    continue
        return _ok(result)
    except Exception as e:
        return _err(f"Failed to inspect splits for '{dataset_name}': {e}")


@mcp.tool(
    name="instantiate_loader",
    description="Instantiate AgML data loader and return basic dataset summary.",
)
def instantiate_loader(
    dataset_name: str,
    download: bool = False,
) -> Dict[str, Any]:
    """
    Create an AgMLDataLoader for a dataset.

    Parameters:
        dataset_name: Name of the dataset.
        download: Whether to allow dataset download.

    Returns:
        Dict with success/result/error.
        result includes basic loader summary fields.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")

    try:
        loader = agml.data.AgMLDataLoader(dataset_name, download=download)  # type: ignore[attr-defined]
        result = {
            "dataset_name": dataset_name,
            "num_images": getattr(loader, "num_images", None),
            "task": getattr(loader, "task", None),
            "classes": getattr(loader, "classes", None),
        }
        return _ok(result)
    except Exception as e:
        return _err(f"Failed to instantiate loader: {e}")


@mcp.tool(
    name="sample_batch_summary",
    description="Load a small sample and summarize image/annotation structure.",
)
def sample_batch_summary(
    dataset_name: str,
    download: bool = False,
    sample_count: int = 1,
) -> Dict[str, Any]:
    """
    Sample one or more records from a dataset and summarize shapes/types.

    Parameters:
        dataset_name: Dataset to sample.
        download: Whether to permit automatic download.
        sample_count: Number of samples to inspect (best effort).

    Returns:
        Dict with success/result/error.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")

    try:
        loader = agml.data.AgMLDataLoader(dataset_name, download=download)  # type: ignore[attr-defined]
        samples = []
        max_n = max(1, min(sample_count, 10))
        for i, item in enumerate(loader):
            if i >= max_n:
                break
            sample_info: Dict[str, Any] = {"index": i}
            try:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    x, y = item[0], item[1]
                    sample_info["x_type"] = type(x).__name__
                    sample_info["y_type"] = type(y).__name__
                    sample_info["x_shape"] = getattr(x, "shape", None)
                    sample_info["y_shape"] = getattr(y, "shape", None)
                else:
                    sample_info["item_type"] = type(item).__name__
                    sample_info["item_shape"] = getattr(item, "shape", None)
            except Exception as e:
                sample_info["error"] = str(e)
            samples.append(sample_info)
        return _ok({"dataset_name": dataset_name, "samples": samples})
    except Exception as e:
        return _err(f"Failed to sample dataset: {e}")


@mcp.tool(
    name="model_catalog_discovery",
    description="List available AgML model APIs and benchmark helpers.",
)
def model_catalog_discovery() -> Dict[str, Any]:
    """
    Discover model-related modules and common callable entry points in AgML.

    Returns:
        Dict with success/result/error.
    """
    agml, err = _import_agml()
    if agml is None:
        return _err(f"Failed to import agml: {err}")

    try:
        import agml.models as models_mod  # type: ignore

        callables = []
        for name in dir(models_mod):
            if name.startswith("_"):
                continue
            try:
                obj = getattr(models_mod, name)
                if callable(obj):
                    callables.append(name)
            except Exception:
                continue
        return _ok({"module": "agml.models", "callables": sorted(callables)})
    except Exception as e:
        return _err(f"Failed model discovery: {e}")


def create_app() -> FastMCP:
    return mcp