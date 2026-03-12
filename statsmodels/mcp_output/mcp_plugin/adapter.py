import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for statsmodels repository integration.

    This adapter favors direct imports from repository source code and provides
    graceful fallback behavior when import/runtime conditions are not met.
    """

    mode = "import"

    # -------------------------------------------------------------------------
    # Lifecycle and internal helpers
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self._modules: Dict[str, Any] = {}
        self._load_errors: Dict[str, str] = {}
        self._initialize_imports()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode}
        if data:
            result.update(data)
        return result

    def _err(self, message: str, guidance: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {
            "status": "error",
            "mode": self.mode,
            "error": message,
        }
        if guidance:
            result["guidance"] = guidance
        if extra:
            result.update(extra)
        return result

    def _initialize_imports(self) -> None:
        targets = {
            "print_version": "statsmodels.tools.print_version",
            "api": "statsmodels.api",
            "tsa_api": "statsmodels.tsa.api",
            "stats_api": "statsmodels.stats.api",
            "iolib_api": "statsmodels.iolib.api",
            "graphics_api": "statsmodels.graphics.api",
            "formula_api": "statsmodels.formula.api",
        }
        for key, module_path in targets.items():
            try:
                self._modules[key] = __import__(module_path, fromlist=["*"])
            except Exception as exc:
                self._load_errors[key] = f"{type(exc).__name__}: {exc}"

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter status and import diagnostics.

        Returns:
            dict: Unified status payload with loaded modules and load errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(list(self._modules.keys())),
                "import_errors": self._load_errors,
                "source_path": source_path,
            }
        )

    def run_print_version(self) -> Dict[str, Any]:
        """
        Execute statsmodels environment/version diagnostics.

        Uses:
            statsmodels.tools.print_version

        Returns:
            dict: Unified status payload.
        """
        mod = self._modules.get("print_version")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.tools.print_version.",
                "Ensure repository source dependencies are installed: numpy, scipy, pandas, patsy, packaging.",
                {"import_errors": self._load_errors},
            )
        try:
            if hasattr(mod, "show_versions"):
                mod.show_versions()
                return self._ok({"message": "show_versions executed."})
            if hasattr(mod, "main"):
                mod.main()
                return self._ok({"message": "print_version main executed."})
            return self._err(
                "No executable entry point found in statsmodels.tools.print_version.",
                "Use module attributes to inspect available diagnostic functions.",
            )
        except Exception as exc:
            return self._err(
                f"Diagnostics execution failed: {type(exc).__name__}: {exc}",
                "Check optional runtime dependencies and Python environment compatibility.",
            )

    # -------------------------------------------------------------------------
    # API accessors (module-level handles for downstream MCP tools)
    # -------------------------------------------------------------------------
    def get_statsmodels_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.api.",
                "Install required dependencies and verify source path configuration.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    def get_tsa_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.tsa.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("tsa_api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.tsa.api.",
                "Ensure time-series dependencies are available and source is intact.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    def get_stats_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.stats.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("stats_api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.stats.api.",
                "Validate base dependencies and statsmodels source integrity.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    def get_iolib_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.iolib.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("iolib_api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.iolib.api.",
                "Check statsmodels source files and import path setup.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    def get_graphics_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.graphics.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("graphics_api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.graphics.api.",
                "Install optional plotting dependency matplotlib if required.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    def get_formula_api(self) -> Dict[str, Any]:
        """
        Retrieve statsmodels.formula.api module handle.

        Returns:
            dict: Contains module object on success.
        """
        mod = self._modules.get("formula_api")
        if mod is None:
            return self._err(
                "Failed to import statsmodels.formula.api.",
                "Ensure patsy is installed for formula-based modeling.",
                {"import_errors": self._load_errors},
            )
        return self._ok({"module": mod})

    # -------------------------------------------------------------------------
    # Generic utility execution helpers
    # -------------------------------------------------------------------------
    def call_module_attr(self, module_key: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any callable attribute from a preloaded module key.

        Args:
            module_key (str): One of internal module keys loaded by adapter.
            attr_name (str): Callable attribute name to invoke.
            *args: Positional arguments for callable.
            **kwargs: Keyword arguments for callable.

        Returns:
            dict: Unified status payload with callable return value.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._err(
                f"Module key '{module_key}' is not loaded.",
                "Use get_status() to inspect available modules and import errors.",
            )
        if not hasattr(mod, attr_name):
            return self._err(
                f"Attribute '{attr_name}' not found in module '{module_key}'.",
                "Verify attribute name and module API compatibility.",
            )
        fn = getattr(mod, attr_name)
        if not callable(fn):
            return self._err(
                f"Attribute '{attr_name}' in module '{module_key}' is not callable.",
                "Use module inspection to access non-callable attributes directly.",
            )
        try:
            value = fn(*args, **kwargs)
            return self._ok({"result": value})
        except Exception as exc:
            return self._err(
                f"Callable execution failed: {type(exc).__name__}: {exc}",
                "Validate input arguments and dependency availability.",
            )