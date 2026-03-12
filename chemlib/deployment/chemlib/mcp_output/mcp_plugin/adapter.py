import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for repository: harirakul/chemlib

    This adapter prioritizes import-based integration and provides a graceful fallback
    when modules are unavailable. It exposes methods for all identified importable
    functions/classes from analysis results.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._functions: Dict[str, Any] = {}
        self._classes: Dict[str, Any] = {}
        self._initialize_imports()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "error": message}
        if hint:
            payload["hint"] = hint
        return payload

    def _initialize_imports(self) -> None:
        """
        Attempt importing discovered modules/functions/classes.
        Falls back to blackbox mode when import fails.
        """
        try:
            import importlib

            conf_module = importlib.import_module("chemlib.docs.source.conf")
            self._modules["chemlib.docs.source.conf"] = conf_module

            if hasattr(conf_module, "get_type_hints"):
                self._functions["get_type_hints"] = getattr(conf_module, "get_type_hints")

            self.mode = "import"
        except Exception as exc:
            self.mode = "blackbox"
            self._modules = {}
            self._functions = {}
            self._classes = {}
            self._import_error = str(exc)

    # -------------------------------------------------------------------------
    # Health and capability inspection
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness.

        Returns:
            dict: Unified status payload with mode, available modules, and features.
        """
        if self.mode == "import":
            return self._ok(
                {
                    "message": "Adapter initialized in import mode.",
                    "modules": list(self._modules.keys()),
                    "functions": list(self._functions.keys()),
                    "classes": list(self._classes.keys()),
                }
            )
        return self._err(
            "Adapter is running in fallback mode due to import failure.",
            hint="Verify repository source path and dependencies (numpy, sympy), then retry.",
        )

    def list_capabilities(self) -> Dict[str, Any]:
        """
        List all callable features exposed by this adapter.

        Returns:
            dict: Unified status payload containing callable methods.
        """
        return self._ok(
            {
                "capabilities": {
                    "functions": ["call_get_type_hints"],
                    "classes": [],
                    "utility": ["health_check", "list_capabilities"],
                }
            }
        )

    # -------------------------------------------------------------------------
    # Function call wrappers
    # -------------------------------------------------------------------------
    def call_get_type_hints(self, obj: Any, globalns: Optional[dict] = None, localns: Optional[dict] = None) -> Dict[str, Any]:
        """
        Call the discovered function: get_type_hints from chemlib.docs.source.conf.

        Parameters:
            obj (Any):
                The object to inspect for type hints (function, class, method, etc.).
            globalns (dict, optional):
                Optional globals namespace to resolve forward references.
            localns (dict, optional):
                Optional locals namespace to resolve forward references.

        Returns:
            dict:
                Unified status payload with function output when successful.
                On failure, includes actionable error guidance.
        """
        if self.mode != "import":
            return self._err(
                "Function unavailable in fallback mode.",
                hint="Ensure source import works and dependencies are installed, then call again.",
            )

        fn = self._functions.get("get_type_hints")
        if fn is None:
            return self._err(
                "Function 'get_type_hints' is not loaded.",
                hint="Reinitialize adapter and confirm module chemlib.docs.source.conf is accessible.",
            )

        try:
            result = fn(obj, globalns=globalns, localns=localns)
            return self._ok({"function": "get_type_hints", "result": result})
        except TypeError:
            try:
                result = fn(obj)
                return self._ok({"function": "get_type_hints", "result": result})
            except Exception as exc:
                return self._err(
                    f"Failed to execute 'get_type_hints': {exc}",
                    hint="Pass a valid Python object and optional namespace dictionaries.",
                )
        except Exception as exc:
            return self._err(
                f"Failed to execute 'get_type_hints': {exc}",
                hint="Check input object validity and Python typing compatibility.",
            )