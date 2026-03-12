import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the yt repository.

    This adapter prioritizes direct module import and execution from the repository source tree.
    It provides safe wrappers with unified return payloads and graceful fallback behavior.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = {}
        self._import_errors = {}
        self._initialize_imports()

    # ============================================================
    # Internal helpers
    # ============================================================

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "ok") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data or {}}

    def _err(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _import_module(self, module_path: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        try:
            mod = importlib.import_module(module_path)
            self._loaded[module_path] = mod
            return True, mod, None
        except Exception as exc:
            msg = f"{exc.__class__.__name__}: {exc}"
            self._import_errors[module_path] = msg
            return False, None, msg

    def _initialize_imports(self) -> None:
        self._import_module("yt")
        self._import_module("yt.utilities.command_line")

    def _ensure_module(self, module_path: str) -> Dict[str, Any]:
        if module_path in self._loaded:
            return self._ok({"module": module_path}, "module already loaded")
        ok, mod, err = self._import_module(module_path)
        if ok and mod is not None:
            return self._ok({"module": module_path}, "module loaded")
        return self._err(
            f"Failed to import module '{module_path}'.",
            hint="Verify repository source is present under the configured 'source' directory and dependencies are installed.",
            error=Exception(err or "unknown import error"),
        )

    # ============================================================
    # Repository / environment inspection
    # ============================================================

    def get_adapter_info(self) -> Dict[str, Any]:
        """
        Return adapter metadata and import diagnostics.

        Returns:
            dict: Unified status dictionary containing mode, loaded modules, and import failures.
        """
        return self._ok(
            {
                "mode": self.mode,
                "source_path": source_path,
                "loaded_modules": sorted(self._loaded.keys()),
                "import_errors": self._import_errors.copy(),
            },
            "adapter info collected",
        )

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate base import readiness for yt and CLI module.

        Returns:
            dict: Unified status dictionary with readiness and actionable guidance.
        """
        required = ["yt", "yt.utilities.command_line"]
        missing = [m for m in required if m not in self._loaded]
        if not missing:
            return self._ok({"ready": True, "required_modules": required}, "environment is ready")
        return self._err(
            "Environment validation failed: required modules are not importable.",
            hint=f"Missing modules: {missing}. Install required dependencies (numpy, packaging, more-itertools, and yt optional stack as needed).",
        )

    # ============================================================
    # Core import strategy wrappers
    # ============================================================

    def import_yt(self) -> Dict[str, Any]:
        """
        Ensure the top-level yt package is importable.

        Returns:
            dict: Unified status dictionary with module details.
        """
        return self._ensure_module("yt")

    def load_dataset(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Load a dataset through yt.load using import mode.

        Parameters:
            path (str): Dataset path or identifier.
            **kwargs: Additional keyword arguments forwarded to yt.load.

        Returns:
            dict: Unified status dictionary with dataset summary metadata.
        """
        if "yt" not in self._loaded:
            resp = self._ensure_module("yt")
            if resp["status"] != "success":
                return resp
        try:
            yt_mod = self._loaded["yt"]
            ds = yt_mod.load(path, **kwargs)
            return self._ok(
                {
                    "dataset_repr": repr(ds),
                    "dataset_type": ds.__class__.__name__,
                    "parameter_filename": getattr(ds, "parameter_filename", None),
                    "domain_dimensions": getattr(ds, "domain_dimensions", None).tolist()
                    if hasattr(getattr(ds, "domain_dimensions", None), "tolist")
                    else getattr(ds, "domain_dimensions", None),
                },
                "dataset loaded",
            )
        except Exception as exc:
            return self._err(
                "Failed to load dataset via yt.load.",
                hint="Check dataset path, format support, and optional IO dependencies (e.g., h5py, netCDF4, astropy).",
                error=exc,
            )

    # ============================================================
    # CLI module wrappers (yt.utilities.command_line)
    # ============================================================

    def import_cli_module(self) -> Dict[str, Any]:
        """
        Ensure yt CLI implementation module is importable.

        Returns:
            dict: Unified status dictionary with module details.
        """
        return self._ensure_module("yt.utilities.command_line")

    def list_cli_commands(self) -> Dict[str, Any]:
        """
        Introspect likely callable CLI command handlers from yt.utilities.command_line.

        Returns:
            dict: Unified status dictionary containing discovered callables.
        """
        if "yt.utilities.command_line" not in self._loaded:
            resp = self._ensure_module("yt.utilities.command_line")
            if resp["status"] != "success":
                return resp
        try:
            mod = self._loaded["yt.utilities.command_line"]
            names = []
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                obj = getattr(mod, name, None)
                if callable(obj):
                    names.append(name)
            return self._ok({"module": mod.__name__, "callables": sorted(names)}, "CLI callables discovered")
        except Exception as exc:
            return self._err(
                "Failed to enumerate CLI callables.",
                hint="Re-run after confirming the command_line module imports cleanly.",
                error=exc,
            )

    def call_cli_callable(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a named callable from yt.utilities.command_line.

        Parameters:
            name (str): Callable attribute name inside yt.utilities.command_line.
            *args: Positional arguments forwarded to the callable.
            **kwargs: Keyword arguments forwarded to the callable.

        Returns:
            dict: Unified status dictionary including return value representation.
        """
        if "yt.utilities.command_line" not in self._loaded:
            resp = self._ensure_module("yt.utilities.command_line")
            if resp["status"] != "success":
                return resp
        try:
            mod = self._loaded["yt.utilities.command_line"]
            if not hasattr(mod, name):
                return self._err(
                    f"Callable '{name}' not found in yt.utilities.command_line.",
                    hint="Use list_cli_commands() to inspect available callables.",
                )
            fn = getattr(mod, name)
            if not callable(fn):
                return self._err(
                    f"Attribute '{name}' exists but is not callable.",
                    hint="Use list_cli_commands() and select a callable entry.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"callable": name, "result_repr": repr(result)}, "call executed")
        except Exception as exc:
            return self._err(
                f"Execution failed for callable '{name}'.",
                hint="Verify arguments for the selected callable and ensure required runtime context is provided.",
                error=exc,
            )

    # ============================================================
    # Generic module/function execution for extensibility
    # ============================================================

    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import any module from repository source using full package path.

        Parameters:
            module_path (str): Full import path, e.g. 'yt.frontends.api'.

        Returns:
            dict: Unified status dictionary.
        """
        return self._ensure_module(module_path)

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Import a module and call a function by name.

        Parameters:
            module_path (str): Full module import path.
            function_name (str): Function attribute name in module.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status dictionary containing function result representation.
        """
        resp = self._ensure_module(module_path)
        if resp["status"] != "success":
            return resp
        try:
            mod = self._loaded[module_path]
            fn = getattr(mod, function_name, None)
            if fn is None:
                return self._err(
                    f"Function '{function_name}' was not found in module '{module_path}'.",
                    hint="Check function name spelling and module path.",
                )
            if not callable(fn):
                return self._err(
                    f"Attribute '{function_name}' in '{module_path}' is not callable.",
                    hint="Provide a function or callable attribute name.",
                )
            result = fn(*args, **kwargs)
            return self._ok(
                {
                    "module": module_path,
                    "function": function_name,
                    "result_repr": repr(result),
                },
                "function call executed",
            )
        except Exception as exc:
            return self._err(
                f"Function call failed: {module_path}.{function_name}",
                hint="Validate provided arguments and required runtime prerequisites.",
                error=exc,
            )

    def get_traceback(self, module_path: str) -> Dict[str, Any]:
        """
        Return stored import error for a module with guidance.

        Parameters:
            module_path (str): Full module path previously attempted.

        Returns:
            dict: Unified status dictionary with error context if available.
        """
        if module_path in self._import_errors:
            return self._ok(
                {"module": module_path, "import_error": self._import_errors[module_path]},
                "stored import error found",
            )
        return self._err(
            f"No stored import error for module '{module_path}'.",
            hint="Call import_module(module_path) first to capture diagnostics.",
        )