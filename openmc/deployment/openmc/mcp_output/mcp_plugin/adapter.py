import os
import sys

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)

import traceback
from typing import Any, Dict, Optional


class Adapter:
    """
    MCP import-mode adapter for the OpenMC repository.

    This adapter prioritizes Python import usage and gracefully falls back
    with actionable error messages when imports or runtime calls fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data or {}}

    def _err(self, message: str, hint: Optional[str] = None, exc: Optional[BaseException] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if exc is not None:
            payload["error_type"] = type(exc).__name__
            payload["details"] = str(exc)
        return payload

    def _initialize_imports(self) -> None:
        try:
            import openmc  # full repository package from source path

            self._modules["openmc"] = openmc
        except Exception as exc:
            self._import_errors["openmc"] = f"{type(exc).__name__}: {exc}"

        try:
            import openmc.executor  # identified by analysis as CLI-related module

            self._modules["openmc.executor"] = openmc.executor
        except Exception as exc:
            self._import_errors["openmc.executor"] = f"{type(exc).__name__}: {exc}"

    def _require(self, key: str) -> Any:
        mod = self._modules.get(key)
        if mod is None:
            raise ImportError(
                f"Module '{key}' is not available. "
                f"Check local source checkout, Python path, and required dependencies."
            )
        return mod

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness, import health, and fallback guidance.

        Returns:
            dict: Unified status payload containing imported modules and import errors.
        """
        imported = sorted(self._modules.keys())
        if imported:
            return self._ok(
                {
                    "imported_modules": imported,
                    "import_errors": self._import_errors,
                    "python": sys.version,
                    "source_path": source_path,
                },
                message="Adapter initialized in import mode.",
            )
        return self._err(
            "Failed to import required OpenMC modules.",
            hint=(
                "Verify repository source exists at the configured source path, "
                "install required dependencies (numpy, h5py, lxml, scipy, uncertainties), "
                "and ensure compatible Python version (>=3.10)."
            ),
        )

    # -------------------------------------------------------------------------
    # OpenMC package instance methods (class-level utility access)
    # -------------------------------------------------------------------------
    def get_openmc_module(self) -> Dict[str, Any]:
        """
        Return the imported top-level OpenMC module instance.

        Returns:
            dict: status + module metadata if available.
        """
        try:
            mod = self._require("openmc")
            return self._ok(
                {
                    "module_name": mod.__name__,
                    "module_file": getattr(mod, "__file__", None),
                    "version": getattr(mod, "__version__", None),
                }
            )
        except Exception as exc:
            return self._err(
                "Unable to access OpenMC module.",
                hint="Run health_check() and fix import issues before calling module methods.",
                exc=exc,
            )

    def get_executor_module(self) -> Dict[str, Any]:
        """
        Return the imported openmc.executor module instance metadata.

        Returns:
            dict: status + executor module details.
        """
        try:
            mod = self._require("openmc.executor")
            return self._ok(
                {
                    "module_name": mod.__name__,
                    "module_file": getattr(mod, "__file__", None),
                    "available_attributes": [n for n in dir(mod) if not n.startswith("_")][:100],
                }
            )
        except Exception as exc:
            return self._err(
                "Unable to access openmc.executor module.",
                hint="Ensure the local source tree is complete and dependencies are installed.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Function call methods based on analysis (executor/CLI-focused)
    # -------------------------------------------------------------------------
    def call_openmc_run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call openmc.run(...) via import mode.

        Parameters:
            **kwargs: Keyword arguments forwarded to openmc.run.

        Returns:
            dict: Unified status with return value or error details.
        """
        try:
            openmc = self._require("openmc")
            if not hasattr(openmc, "run"):
                return self._err(
                    "openmc.run is not available in this build.",
                    hint="Use an OpenMC-compatible source/build that exposes Python run wrappers.",
                )
            result = openmc.run(**kwargs)
            return self._ok({"result": result}, message="openmc.run executed successfully.")
        except Exception as exc:
            return self._err(
                "Failed to execute openmc.run.",
                hint="Validate runtime settings, executable availability, and model input files.",
                exc=exc,
            )

    def call_openmc_plot_geometry(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call openmc.plot_geometry(...) via import mode.

        Parameters:
            **kwargs: Keyword arguments forwarded to openmc.plot_geometry.

        Returns:
            dict: Unified status with return payload or actionable error.
        """
        try:
            openmc = self._require("openmc")
            if not hasattr(openmc, "plot_geometry"):
                return self._err(
                    "openmc.plot_geometry is not available.",
                    hint="Check OpenMC Python API version and plotting support in your environment.",
                )
            result = openmc.plot_geometry(**kwargs)
            return self._ok({"result": result}, message="openmc.plot_geometry executed successfully.")
        except Exception as exc:
            return self._err(
                "Failed to execute openmc.plot_geometry.",
                hint="Ensure geometry.xml/plots.xml exist or pass proper model/export arguments.",
                exc=exc,
            )

    def call_openmc_calculate_volumes(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call openmc.calculate_volumes(...) via import mode.

        Parameters:
            **kwargs: Keyword arguments forwarded to openmc.calculate_volumes.

        Returns:
            dict: Unified status with return payload or clear error message.
        """
        try:
            openmc = self._require("openmc")
            if not hasattr(openmc, "calculate_volumes"):
                return self._err(
                    "openmc.calculate_volumes is not available.",
                    hint="Use an OpenMC version exposing volume calculation in the Python API.",
                )
            result = openmc.calculate_volumes(**kwargs)
            return self._ok({"result": result}, message="openmc.calculate_volumes executed successfully.")
        except Exception as exc:
            return self._err(
                "Failed to execute openmc.calculate_volumes.",
                hint="Ensure settings and volume calculation configuration are valid.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Generic extensible import-call utilities
    # -------------------------------------------------------------------------
    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke any function from an already imported module.

        Parameters:
            module_key (str): Module registry key (e.g., 'openmc', 'openmc.executor').
            function_name (str): Function attribute to call.
            *args: Positional arguments to forward.
            **kwargs: Keyword arguments to forward.

        Returns:
            dict: Unified status with function result or detailed error.
        """
        try:
            module = self._require(module_key)
            fn = getattr(module, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found or not callable in module '{module_key}'.",
                    hint="Inspect available attributes via get_openmc_module/get_executor_module.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"{module_key}.{function_name} executed successfully.")
        except Exception as exc:
            return self._err(
                f"Failed to execute {module_key}.{function_name}.",
                hint="Check function signature and runtime prerequisites.",
                exc=exc,
            )

    def debug_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot helper for diagnostics.

        Returns:
            dict: Unified status with traceback text.
        """
        try:
            tb = traceback.format_exc()
            return self._ok({"traceback": tb}, message="Traceback snapshot captured.")
        except Exception as exc:
            return self._err("Failed to capture traceback.", exc=exc)