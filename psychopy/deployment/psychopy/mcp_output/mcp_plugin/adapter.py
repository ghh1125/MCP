import os
import sys
import traceback
import importlib
import inspect
import subprocess
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for PsychoPy repository integration.

    This adapter prioritizes direct in-process imports and method calls against
    repository modules discovered by analysis, with graceful CLI fallback paths
    for selected workflows if imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._capabilities: Dict[str, bool] = {}
        self._init_runtime()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
        }

    def _safe_import(self, module_path: str) -> Dict[str, Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            self._capabilities[module_path] = True
            return self._result(
                "success",
                f"Imported module '{module_path}' successfully.",
                {"module": module_path},
            )
        except Exception as exc:
            self._capabilities[module_path] = False
            return self._result(
                "error",
                f"Failed to import module '{module_path}'.",
                {"module": module_path},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    def _get_module(self, module_path: str) -> Optional[Any]:
        if module_path in self._modules:
            return self._modules[module_path]
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            self._capabilities[module_path] = True
            return module
        except Exception:
            self._capabilities[module_path] = False
            return None

    def _init_runtime(self) -> None:
        self._safe_import("psychopy.plugins")
        self._safe_import("psychopy.session")
        self._safe_import("psychopy.app.__main__")
        self._safe_import("psychopy.scripts.psyexpCompile")
        self._safe_import("psychopy.scripts.psychopy-pkgutil")

    def healthcheck(self) -> Dict[str, Any]:
        return self._result(
            "success",
            "Adapter initialized.",
            {
                "source_path": source_path,
                "capabilities": self._capabilities,
                "loaded_modules": list(self._modules.keys()),
            },
        )

    # -------------------------------------------------------------------------
    # psychopy.plugins function bindings
    # -------------------------------------------------------------------------
    def call_activatePlugins(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call psychopy.plugins.activatePlugins(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to activatePlugins.
            **kwargs: Keyword arguments forwarded to activatePlugins.

        Returns:
            Unified status dictionary containing call result or actionable error.
        """
        module = self._get_module("psychopy.plugins")
        if module is None or not hasattr(module, "activatePlugins"):
            return self._result(
                "error",
                "activatePlugins is unavailable in import mode.",
                {"hint": "Ensure repository source is present at ../source and dependencies are installed."},
            )
        try:
            fn = getattr(module, "activatePlugins")
            result = fn(*args, **kwargs)
            return self._result(
                "success",
                "activatePlugins executed successfully.",
                {"result": result},
            )
        except Exception as exc:
            return self._result(
                "error",
                "activatePlugins execution failed.",
                {"traceback": traceback.format_exc()},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    def call_listPlugins(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call psychopy.plugins.listPlugins(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to listPlugins.
            **kwargs: Keyword arguments forwarded to listPlugins.

        Returns:
            Unified status dictionary containing plugin list data if available.
        """
        module = self._get_module("psychopy.plugins")
        if module is None or not hasattr(module, "listPlugins"):
            return self._result(
                "error",
                "listPlugins is unavailable in import mode.",
                {"hint": "Validate psychopy.plugins import and optional plugin dependencies."},
            )
        try:
            fn = getattr(module, "listPlugins")
            result = fn(*args, **kwargs)
            return self._result(
                "success",
                "listPlugins executed successfully.",
                {"result": result},
            )
        except Exception as exc:
            return self._result(
                "error",
                "listPlugins execution failed.",
                {"traceback": traceback.format_exc()},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    def call_loadPlugin(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call psychopy.plugins.loadPlugin(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to loadPlugin.
            **kwargs: Keyword arguments forwarded to loadPlugin.

        Returns:
            Unified status dictionary containing load result.
        """
        module = self._get_module("psychopy.plugins")
        if module is None or not hasattr(module, "loadPlugin"):
            return self._result(
                "error",
                "loadPlugin is unavailable in import mode.",
                {"hint": "Check plugin package name and installation inside source environment."},
            )
        try:
            fn = getattr(module, "loadPlugin")
            result = fn(*args, **kwargs)
            return self._result(
                "success",
                "loadPlugin executed successfully.",
                {"result": result},
            )
        except Exception as exc:
            return self._result(
                "error",
                "loadPlugin execution failed.",
                {"traceback": traceback.format_exc()},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # psychopy.session class binding
    # -------------------------------------------------------------------------
    def create_Session(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate psychopy.session.Session(*args, **kwargs).

        Parameters:
            *args: Positional constructor arguments for Session.
            **kwargs: Keyword constructor arguments for Session.

        Returns:
            Unified status dictionary. On success, includes constructor signature
            and basic metadata. The instance itself is not returned directly for
            transport safety; it is cached in-memory.
        """
        module = self._get_module("psychopy.session")
        if module is None or not hasattr(module, "Session"):
            return self._result(
                "error",
                "Session class is unavailable in import mode.",
                {"hint": "Install required runtime dependencies and verify psychopy.session imports cleanly."},
            )
        try:
            cls = getattr(module, "Session")
            instance = cls(*args, **kwargs)
            self._modules["_session_instance"] = instance
            sig = str(inspect.signature(cls))
            return self._result(
                "success",
                "Session instance created successfully.",
                {"class": "psychopy.session.Session", "signature": sig},
            )
        except Exception as exc:
            return self._result(
                "error",
                "Failed to create Session instance.",
                {"traceback": traceback.format_exc()},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    def session_call_method(
        self, method_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Invoke a method on the cached Session instance.

        Parameters:
            method_name: Name of Session instance method to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            Unified status dictionary with method result.
        """
        inst = self._modules.get("_session_instance")
        if inst is None:
            return self._result(
                "error",
                "No Session instance is currently available.",
                {"hint": "Call create_Session(...) before invoking session methods."},
            )
        if not hasattr(inst, method_name):
            return self._result(
                "error",
                f"Session method '{method_name}' not found.",
                {"hint": "Use dir(Session) or inspect source.psychopy.session for valid methods."},
            )
        try:
            method = getattr(inst, method_name)
            result = method(*args, **kwargs)
            return self._result(
                "success",
                f"Session method '{method_name}' executed successfully.",
                {"result": result},
            )
        except Exception as exc:
            return self._result(
                "error",
                f"Session method '{method_name}' execution failed.",
                {"traceback": traceback.format_exc()},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # CLI fallback utilities
    # -------------------------------------------------------------------------
    def run_cli(self, command: List[str], timeout: int = 120) -> Dict[str, Any]:
        """
        Run a CLI command as fallback mode support.

        Parameters:
            command: Command list, e.g. ['python', '-m', 'psychopy.app'].
            timeout: Process timeout in seconds.

        Returns:
            Unified status dictionary with stdout/stderr/returncode.
        """
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=source_path,
            )
            status = "success" if proc.returncode == 0 else "error"
            message = "CLI command executed successfully." if proc.returncode == 0 else "CLI command failed."
            return self._result(
                status,
                message,
                {
                    "command": command,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
            )
        except subprocess.TimeoutExpired as exc:
            return self._result(
                "error",
                "CLI command timed out.",
                {"command": command, "timeout": timeout},
                error=f"TimeoutExpired: {exc}",
            )
        except Exception as exc:
            return self._result(
                "error",
                "CLI command could not be executed.",
                {"command": command},
                error=f"{exc.__class__.__name__}: {exc}",
            )

    def fallback_launch_app(self) -> Dict[str, Any]:
        return self.run_cli([sys.executable, "-m", "psychopy.app"])

    def fallback_psyexpCompile(self, *args: str) -> Dict[str, Any]:
        return self.run_cli([sys.executable, "-m", "psychopy.scripts.psyexpCompile", *args])

    def fallback_pkgutil(self, *args: str) -> Dict[str, Any]:
        return self.run_cli([sys.executable, "-m", "psychopy.scripts.psychopy-pkgutil", *args])