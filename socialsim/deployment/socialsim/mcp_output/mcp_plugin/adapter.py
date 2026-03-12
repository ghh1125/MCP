import os
import sys
import importlib
import importlib.util
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the pnnl/socialsim repository.

    This adapter attempts to import identified modules/classes/functions from the
    repository using robust fallback strategies, including support for directories
    with hyphens (e.g., "december-measurements") via file-based dynamic imports.

    All public methods return a unified dictionary:
    {
        "status": "success" | "error",
        ...
    }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._cache: Dict[str, Any] = {}
        self._module_paths = {
            "december-measurements.validators": os.path.join(
                source_path, "december-measurements", "validators.py"
            ),
            "december-measurements.CommunityCentricMeasurements": os.path.join(
                source_path, "december-measurements", "CommunityCentricMeasurements.py"
            ),
            "december-measurements.cascade_measurements": os.path.join(
                source_path, "december-measurements", "cascade_measurements.py"
            ),
            "december-measurements.ContentCentricMeasurements": os.path.join(
                source_path, "december-measurements", "ContentCentricMeasurements.py"
            ),
            "december-measurements.network_measurements": os.path.join(
                source_path, "december-measurements", "network_measurements.py"
            ),
        }

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        result = {"status": "success"}
        result.update(kwargs)
        return result

    def _err(self, message: str, guidance: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        result = {"status": "error", "message": message}
        if guidance:
            result["guidance"] = guidance
        result.update(kwargs)
        return result

    def _import_module(self, full_module_path: str):
        if full_module_path in self._cache:
            return self._cache[full_module_path]

        # First try regular import
        try:
            mod = importlib.import_module(full_module_path)
            self._cache[full_module_path] = mod
            return mod
        except Exception:
            pass

        # Fallback for hyphenated paths via file import
        file_path = self._module_paths.get(full_module_path)
        if not file_path or not os.path.isfile(file_path):
            raise ImportError(
                f"Module '{full_module_path}' is not importable and file fallback is unavailable."
            )

        safe_name = full_module_path.replace("-", "_").replace(".", "_")
        spec = importlib.util.spec_from_file_location(safe_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Unable to load module spec for '{full_module_path}' from '{file_path}'."
            )

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self._cache[full_module_path] = mod
        return mod

    def _get_attr(self, module_path: str, attr_name: str):
        mod = self._import_module(module_path)
        if not hasattr(mod, attr_name):
            raise AttributeError(f"Attribute '{attr_name}' not found in '{module_path}'.")
        return getattr(mod, attr_name)

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate import readiness for all identified core modules.

        Returns:
            dict: status with per-module availability details.
        """
        results = {}
        for module_name in self._module_paths.keys():
            try:
                self._import_module(module_name)
                results[module_name] = "available"
            except Exception as exc:
                results[module_name] = f"unavailable: {exc}"

        unavailable = [k for k, v in results.items() if str(v).startswith("unavailable")]
        if unavailable:
            return self._err(
                "One or more modules failed to import.",
                guidance=(
                    "Verify repository files exist under the expected source path and install "
                    "required dependencies (pandas, numpy, scipy, networkx, matplotlib, "
                    "scikit-learn, joblib)."
                ),
                mode=self.mode,
                source_path=source_path,
                modules=results,
            )
        return self._ok(mode=self.mode, source_path=source_path, modules=results)

    # -------------------------------------------------------------------------
    # Function wrappers: december-measurements.validators
    # -------------------------------------------------------------------------
    def call_check_empty(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call validators.check_empty(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to check_empty.
            **kwargs: Keyword arguments forwarded to check_empty.

        Returns:
            dict: Unified status dict with function result.
        """
        try:
            fn = self._get_attr("december-measurements.validators", "check_empty")
            return self._ok(result=fn(*args, **kwargs), function="check_empty")
        except Exception as exc:
            return self._err(
                f"Failed to execute check_empty: {exc}",
                guidance="Inspect input arguments and confirm the validators module imports correctly.",
                function="check_empty",
            )

    def call_check_root_only(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call validators.check_root_only(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to check_root_only.
            **kwargs: Keyword arguments forwarded to check_root_only.

        Returns:
            dict: Unified status dict with function result.
        """
        try:
            fn = self._get_attr("december-measurements.validators", "check_root_only")
            return self._ok(result=fn(*args, **kwargs), function="check_root_only")
        except Exception as exc:
            return self._err(
                f"Failed to execute check_root_only: {exc}",
                guidance="Validate cascade/tree input format and module availability.",
                function="check_root_only",
            )

    # -------------------------------------------------------------------------
    # Function wrappers: december-measurements.cascade_measurements
    # -------------------------------------------------------------------------
    def call_get_original_tweet_ratio(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call cascade_measurements.get_original_tweet_ratio(*args, **kwargs).

        Parameters:
            *args: Positional arguments for the original function.
            **kwargs: Keyword arguments for the original function.

        Returns:
            dict: Unified status dict with function output.
        """
        try:
            fn = self._get_attr(
                "december-measurements.cascade_measurements",
                "get_original_tweet_ratio",
            )
            return self._ok(result=fn(*args, **kwargs), function="get_original_tweet_ratio")
        except Exception as exc:
            return self._err(
                f"Failed to execute get_original_tweet_ratio: {exc}",
                guidance="Ensure input data schema matches expected cascade format.",
                function="get_original_tweet_ratio",
            )

    def call_igraph_add_edges_to_existing_graph(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call cascade_measurements.igraph_add_edges_to_existing_graph(*args, **kwargs).

        Parameters:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            dict: Unified status dict with modified graph or function return.
        """
        try:
            fn = self._get_attr(
                "december-measurements.cascade_measurements",
                "igraph_add_edges_to_existing_graph",
            )
            return self._ok(
                result=fn(*args, **kwargs),
                function="igraph_add_edges_to_existing_graph",
            )
        except Exception as exc:
            return self._err(
                f"Failed to execute igraph_add_edges_to_existing_graph: {exc}",
                guidance="Confirm igraph-related dependencies and input edge list structure.",
                function="igraph_add_edges_to_existing_graph",
            )

    def call_igraph_from_pandas_edgelist(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call cascade_measurements.igraph_from_pandas_edgelist(*args, **kwargs).

        Parameters:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            dict: Unified status dict with created graph object.
        """
        try:
            fn = self._get_attr(
                "december-measurements.cascade_measurements",
                "igraph_from_pandas_edgelist",
            )
            return self._ok(result=fn(*args, **kwargs), function="igraph_from_pandas_edgelist")
        except Exception as exc:
            return self._err(
                f"Failed to execute igraph_from_pandas_edgelist: {exc}",
                guidance="Pass a valid pandas edge list DataFrame and verify igraph