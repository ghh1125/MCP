import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the Tellurium repository.

    This adapter is designed to:
    - Prefer direct imports from repository modules under the local `source` directory.
    - Gracefully degrade to fallback mode when imports are unavailable.
    - Provide a unified method interface with consistent response dictionaries.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._imports_ready = False
        self._load_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success", meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "message": message,
            "data": data,
            "meta": meta or {},
        }

    def _err(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "guidance": guidance or "Verify repository source path and dependencies, then retry.",
        }
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": "blackbox",
            "message": f"Import mode is unavailable for action '{action}'.",
            "guidance": "Ensure local source modules exist and required dependencies are installed.",
            "data": None,
        }

    def _safe_import(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception:
            self._modules[key] = None

    def _load_imports(self) -> None:
        """
        Load all discovered core modules from analysis in a resilient manner.
        """
        self._safe_import("docs_conf", "docs.conf")
        self._safe_import("events", "examples.tellurium-files.events.events")
        self._safe_import("download_count", "scripts.download_count")
        self._imports_ready = any(m is not None for m in self._modules.values())

    def health(self) -> Dict[str, Any]:
        """
        Report adapter import health and module readiness.
        """
        try:
            module_status = {k: v is not None for k, v in self._modules.items()}
            return self._ok(
                data={"imports_ready": self._imports_ready, "modules": module_status},
                message="Adapter health check complete.",
            )
        except Exception as e:
            return self._err("Health check failed.", error=e)

    # -------------------------------------------------------------------------
    # Module: docs.conf (class: Mock)
    # -------------------------------------------------------------------------
    def create_docs_conf_mock(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of docs.conf.Mock.

        Parameters:
        - *args: Positional arguments forwarded to Mock constructor.
        - **kwargs: Keyword arguments forwarded to Mock constructor.

        Returns:
        Unified dictionary with status and created instance in `data.instance`.
        """
        try:
            mod = self._modules.get("docs_conf")
            if mod is None or not hasattr(mod, "Mock"):
                return self._fallback("create_docs_conf_mock")
            instance = mod.Mock(*args, **kwargs)
            return self._ok(data={"instance": instance}, message="docs.conf.Mock instance created.")
        except Exception as e:
            return self._err(
                "Failed to create docs.conf.Mock instance.",
                error=e,
                guidance="Check constructor parameters and ensure docs/conf.py is importable.",
            )

    # -------------------------------------------------------------------------
    # Module: examples.tellurium-files.events.events (functions)
    # -------------------------------------------------------------------------
    def call_onEvent(self, rr: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call examples.tellurium-files.events.events.onEvent.

        Parameters:
        - rr: RoadRunner-like simulation object expected by original function.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        Unified dictionary with execution result.
        """
        try:
            mod = self._modules.get("events")
            if mod is None or not hasattr(mod, "onEvent"):
                return self._fallback("call_onEvent")
            result = mod.onEvent(rr, *args, **kwargs)
            return self._ok(data=result, message="onEvent executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute onEvent.",
                error=e,
                guidance="Provide a valid simulation object and verify function preconditions.",
            )

    def call_onEventAssignment(self, rr: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call examples.tellurium-files.events.events.onEventAssignment.

        Parameters:
        - rr: RoadRunner-like simulation object expected by original function.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        Unified dictionary with execution result.
        """
        try:
            mod = self._modules.get("events")
            if mod is None or not hasattr(mod, "onEventAssignment"):
                return self._fallback("call_onEventAssignment")
            result = mod.onEventAssignment(rr, *args, **kwargs)
            return self._ok(data=result, message="onEventAssignment executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute onEventAssignment.",
                error=e,
                guidance="Confirm event assignment inputs and model state validity.",
            )

    def call_onEventTrigger(self, rr: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call examples.tellurium-files.events.events.onEventTrigger.

        Parameters:
        - rr: RoadRunner-like simulation object expected by original function.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        Unified dictionary with execution result.
        """
        try:
            mod = self._modules.get("events")
            if mod is None or not hasattr(mod, "onEventTrigger"):
                return self._fallback("call_onEventTrigger")
            result = mod.onEventTrigger(rr, *args, **kwargs)
            return self._ok(data=result, message="onEventTrigger executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute onEventTrigger.",
                error=e,
                guidance="Validate trigger settings and provide a compatible simulation object.",
            )

    # -------------------------------------------------------------------------
    # Module: scripts.download_count (functions)
    # -------------------------------------------------------------------------
    def call_get_git_releases_json(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call scripts.download_count.get_git_releases_json.

        Parameters:
        - *args: Positional arguments for the original function.
        - **kwargs: Keyword arguments for the original function.

        Returns:
        Unified dictionary with JSON or API response data.
        """
        try:
            mod = self._modules.get("download_count")
            if mod is None or not hasattr(mod, "get_git_releases_json"):
                return self._fallback("call_get_git_releases_json")
            result = mod.get_git_releases_json(*args, **kwargs)
            return self._ok(data=result, message="get_git_releases_json executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute get_git_releases_json.",
                error=e,
                guidance="Check network access, API endpoint, and repository metadata.",
            )

    def call_parse_release_json(self, release_json: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call scripts.download_count.parse_release_json.

        Parameters:
        - release_json: Release JSON payload to parse.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        Unified dictionary with parsed release DataFrame or parsed structure.
        """
        try:
            mod = self._modules.get("download_count")
            if mod is None or not hasattr(mod, "parse_release_json"):
                return self._fallback("call_parse_release_json")
            result = mod.parse_release_json(release_json, *args, **kwargs)
            return self._ok(data=result, message="parse_release_json executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute parse_release_json.",
                error=e,
                guidance="Ensure release_json format matches the GitHub releases schema.",
            )

    def call_plot_release_df(self, release_df: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call scripts.download_count.plot_release_df.

        Parameters:
        - release_df: DataFrame-like object expected by plotting function.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        Unified dictionary with plot operation outcome.
        """
        try:
            mod = self._modules.get("download_count")
            if mod is None or not hasattr(mod, "plot_release_df"):
                return self._fallback("call_plot_release_df")
            result = mod.plot_release_df(release_df, *args, **kwargs)
            return self._ok(data=result, message="plot_release_df executed successfully.")
        except Exception as e:
            return self._err(
                "Failed to execute plot_release_df.",
                error=e,
                guidance="Provide a valid DataFrame and ensure plotting backend dependencies are installed.",
            )