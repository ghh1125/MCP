import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the LangGraph monorepo.

    This adapter prioritizes direct module imports from the repository source tree and
    provides a graceful CLI fallback when import-based operations are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._imports_ok = False
        self._import_errors: List[str] = []
        self._bootstrap_imports()

    # -------------------------------------------------------------------------
    # Internal Utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": status,
            "message": message,
            "data": data or {},
            "mode": self.mode,
        }

    def _bootstrap_imports(self) -> None:
        targets = {
            "cli": "libs.cli.langgraph_cli.cli",
            "config": "libs.cli.langgraph_cli.config",
            "schemas": "libs.cli.langgraph_cli.schemas",
            "templates": "libs.cli.langgraph_cli.templates",
            "sdk_client": "libs.sdk-py.langgraph_sdk.client".replace("-", "_"),
            "sdk_schema": "libs.sdk-py.langgraph_sdk.schema".replace("-", "_"),
            "graph_state": "libs.langgraph.langgraph.graph.state",
            "graph_message": "libs.langgraph.langgraph.graph.message",
            "pregel_main": "libs.langgraph.langgraph.pregel.main",
            "prebuilt_agent": "libs.prebuilt.langgraph.prebuilt.chat_agent_executor",
            "prebuilt_tool_node": "libs.prebuilt.langgraph.prebuilt.tool_node",
        }

        for key, module_path in targets.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._import_errors.append(f"{module_path}: {exc}")

        self._imports_ok = len(self._modules) > 0

    def _require_module(self, key: str) -> Optional[Any]:
        return self._modules.get(key)

    # -------------------------------------------------------------------------
    # Health / Status
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter readiness and import diagnostics.

        Returns:
            Unified status dictionary with loaded modules and import errors.
        """
        if self._imports_ok:
            return self._result(
                "ok",
                "Adapter is ready in import mode.",
                {
                    "loaded_modules": sorted(self._modules.keys()),
                    "import_errors": self._import_errors,
                },
            )
        return self._result(
            "error",
            "No import targets were loaded. Verify repository source is mounted under ./source and paths are correct.",
            {"import_errors": self._import_errors},
        )

    # -------------------------------------------------------------------------
    # CLI Module Methods
    # -------------------------------------------------------------------------
    def cli_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Invoke LangGraph CLI main entrypoint.

        Parameters:
            argv: Optional command argument list to pass to CLI.

        Returns:
            Unified status dictionary with execution outcome.
        """
        mod = self._require_module("cli")
        if mod is None:
            return self._result(
                "error",
                "CLI module import failed. Fallback: run `langgraph --help` in shell to validate installation.",
                {"import_errors": self._import_errors},
            )
        try:
            if hasattr(mod, "main"):
                out = mod.main(argv) if argv is not None else mod.main()
                return self._result("ok", "CLI main executed successfully.", {"result": out})
            return self._result("error", "CLI module does not expose `main`.", {})
        except Exception:
            return self._result("error", "CLI execution failed. Check arguments and project configuration.", {"traceback": traceback.format_exc()})

    def cli_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from langgraph CLI module.

        Parameters:
            function_name: Function attribute name in CLI module.
            *args/**kwargs: Function call arguments.

        Returns:
            Unified status dictionary with function result.
        """
        mod = self._require_module("cli")
        if mod is None:
            return self._result("error", "CLI module unavailable. Ensure source tree is complete.", {})
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._result("error", f"Function `{function_name}` not found or not callable in CLI module.", {})
            return self._result("ok", f"Function `{function_name}` executed.", {"result": fn(*args, **kwargs)})
        except Exception:
            return self._result(
                "error",
                f"Failed to execute CLI function `{function_name}`. Verify parameters and module compatibility.",
                {"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # SDK Module Methods
    # -------------------------------------------------------------------------
    def sdk_get_client_class(self) -> Dict[str, Any]:
        """
        Retrieve primary SDK client class symbols from langgraph_sdk.client.

        Returns:
            Unified status dictionary with discovered client-like classes.
        """
        mod = self._require_module("sdk_client")
        if mod is None:
            return self._result(
                "error",
                "SDK client module import failed. Confirm `libs/sdk-py` package path and underscores conversion are valid.",
                {"import_errors": self._import_errors},
            )
        try:
            names = [n for n in dir(mod) if "Client" in n]
            return self._result("ok", "SDK client symbols discovered.", {"symbols": names})
        except Exception:
            return self._result("error", "Failed to introspect SDK client module.", {"traceback": traceback.format_exc()})

    def sdk_call(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from loaded SDK modules.

        Parameters:
            module_key: Loaded module key, e.g. `sdk_client` or `sdk_schema`.
            function_name: Callable attribute name.
            *args/**kwargs: Call parameters.

        Returns:
            Unified status dictionary with call outcome.
        """
        mod = self._require_module(module_key)
        if mod is None:
            return self._result("error", f"Module `{module_key}` not loaded. Check import diagnostics.", {})
        try:
            fn = getattr(mod, function_name, None)
            if not callable(fn):
                return self._result("error", f"`{function_name}` is not callable in `{module_key}`.", {})
            return self._result("ok", f"{module_key}.{function_name} executed.", {"result": fn(*args, **kwargs)})
        except Exception:
            return self._result("error", f"Call failed for `{module_key}.{function_name}`.", {"traceback": traceback.format_exc()})

    # -------------------------------------------------------------------------
    # Core LangGraph Module Methods
    # -------------------------------------------------------------------------
    def create_instance(self, module_key: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from any loaded module.

        Parameters:
            module_key: Key in loaded module registry.
            class_name: Class attribute to instantiate.
            *args/**kwargs: Constructor parameters.

        Returns:
            Unified status dictionary with created instance metadata.
        """
        mod = self._require_module(module_key)
        if mod is None:
            return self._result("error", f"Module `{module_key}` is not loaded.", {})
        try:
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._result("error", f"Class `{class_name}` not found in `{module_key}`.", {})
            instance = cls(*args, **kwargs)
            return self._result(
                "ok",
                f"Instance of `{class_name}` created successfully.",
                {"class": class_name, "module_key": module_key, "instance_repr": repr(instance)},
            )
        except Exception:
            return self._result(
                "error",
                f"Failed to instantiate `{class_name}`. Verify constructor arguments and dependency setup.",
                {"traceback": traceback.format_exc()},
            )

    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from any loaded module.

        Parameters:
            module_key: Key in loaded module registry.
            function_name: Function name.
            *args/**kwargs: Call arguments.

        Returns:
            Unified status dictionary with function result.
        """
        mod = self._require_module(module_key)
        if mod is None:
            return self._result("error", f"Module `{module_key}` is not loaded.", {})
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._result("error", f"Function `{function_name}` is missing or not callable in `{module_key}`.", {})
            out = fn(*args, **kwargs)
            return self._result("ok", f"{module_key}.{function_name} executed.", {"result": out})
        except Exception:
            return self._result(
                "error",
                f"Execution failed for `{module_key}.{function_name}`. Review parameters and runtime dependencies.",
                {"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Fallback Helpers
    # -------------------------------------------------------------------------
    def fallback_cli_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable CLI fallback guidance when import mode is partially unavailable.

        Returns:
            Unified status dictionary with suggested next steps.
        """
        return self._result(
            "ok",
            "Fallback guidance generated.",
            {
                "steps": [
                    "Run `python -m libs.cli.langgraph_cli.cli --help` from repository root if import path is correct.",
                    "Or run installed binary `langgraph --help` to validate CLI availability.",
                    "Ensure ./source contains the full repository and adapter file depth matches expected sys.path logic.",
                    "For SDK operations, verify `libs/sdk-py` package naming and Python path normalization.",
                ]
            },
        )