import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("qlib_core_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="qlib_init", description="Initialize Qlib runtime with provider and region.")
def qlib_init(
    provider_uri: str,
    region: str = "cn",
    expression_cache: Optional[str] = None,
    dataset_cache: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Initialize Qlib global runtime.

    Parameters:
        provider_uri: Local or remote data provider URI for Qlib.
        region: Market region, such as 'cn' or 'us'.
        expression_cache: Optional expression cache mode/path.
        dataset_cache: Optional dataset cache mode/path.

    Returns:
        A dictionary with success/result/error.
    """
    try:
        import qlib

        kwargs: Dict[str, Any] = {"provider_uri": provider_uri, "region": region}
        if expression_cache is not None:
            kwargs["expression_cache"] = expression_cache
        if dataset_cache is not None:
            kwargs["dataset_cache"] = dataset_cache

        qlib.init(**kwargs)
        return _ok("qlib initialized")
    except Exception as e:
        return _err(e)


@mcp.tool(name="qlib_auto_init", description="Auto initialize Qlib using discovered/default configuration.")
def qlib_auto_init() -> Dict[str, Any]:
    """
    Auto initialize Qlib.

    Returns:
        A dictionary with success/result/error.
    """
    try:
        import qlib

        qlib.auto_init()
        return _ok("qlib auto initialized")
    except Exception as e:
        return _err(e)


@mcp.tool(name="qlib_run_workflow", description="Run Qlib workflow from YAML config file.")
def qlib_run_workflow(config_path: str, experiment_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a Qlib workflow from a YAML configuration.

    Parameters:
        config_path: Path to workflow YAML config.
        experiment_name: Optional experiment name override.

    Returns:
        A dictionary with success/result/error.
    """
    try:
        import qlib
        from qlib.workflow import R

        qlib.init()
        recorder = R.start(experiment_name=experiment_name) if experiment_name else R.start()
        with recorder:
            from qlib.utils import init_instance_by_config
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            task = cfg.get("task", cfg)
            model = init_instance_by_config(task["model"])
            dataset = init_instance_by_config(task["dataset"])
            model.fit(dataset)
            preds = model.predict(dataset)

        return _ok({"predictions_type": str(type(preds)), "experiment_name": experiment_name})
    except Exception as e:
        return _err(e)


@mcp.tool(name="qlib_run_rolling_module", description="Run qlib.contrib.rolling module as main entrypoint.")
def qlib_run_rolling_module(config_path: str) -> Dict[str, Any]:
    """
    Run rolling workflow through qlib.contrib.rolling entry module.

    Parameters:
        config_path: Path to rolling config file.

    Returns:
        A dictionary with success/result/error.
    """
    try:
        import runpy

        old_argv = sys.argv[:]
        try:
            sys.argv = ["python -m qlib.contrib.rolling", config_path]
            runpy.run_module("qlib.contrib.rolling", run_name="__main__")
        finally:
            sys.argv = old_argv

        return _ok("rolling module executed")
    except Exception as e:
        return _err(e)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()