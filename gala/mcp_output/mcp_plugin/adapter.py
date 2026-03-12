import os
import sys
import importlib
import inspect
import traceback
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the gala repository.

    This adapter attempts to import and expose practical entry points from the
    `gala` package with graceful fallback behavior when optional dependencies
    or compiled extensions are unavailable.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = {}
        self._import_errors = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        targets = [
            "gala",
            "gala.coordinates",
            "gala.dynamics",
            "gala.integrate",
            "gala.potential",
            "gala.units",
            "gala.io",
            "gala.util",
        ]
        for mod in targets:
            self._safe_import(mod)

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "ok", **extra: Any) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode, "message": message, "data": data}
        out.update(extra)
        return out

    def _fail(self, message: str, error: Optional[Exception] = None, **extra: Any) -> Dict[str, Any]:
        out = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(error) if error else None,
        }
        out.update(extra)
        return out

    def _safe_import(self, module_path: str) -> Dict[str, Any]:
        try:
            module = importlib.import_module(module_path)
            self._loaded[module_path] = module
            return self._ok({"module": module_path}, f"Imported {module_path}")
        except Exception as e:
            self._import_errors[module_path] = traceback.format_exc()
            return self._fail(
                f"Failed to import module '{module_path}'. Ensure optional dependencies are installed.",
                e,
                module=module_path,
            )

    def _get_module(self, module_path: str):
        if module_path in self._loaded:
            return self._loaded[module_path]
        res = self._safe_import(module_path)
        if res["status"] == "success":
            return self._loaded.get(module_path)
        return None

    def _call_symbol(self, module_path: str, symbol: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._get_module(module_path)
        if mod is None:
            return self._fail(
                f"Module '{module_path}' is unavailable. Try installing required dependencies: numpy, scipy, astropy, pyyaml."
            )
        if not hasattr(mod, symbol):
            return self._fail(
                f"Symbol '{symbol}' not found in '{module_path}'. Verify version compatibility."
            )
        try:
            fn = getattr(mod, symbol)
            result = fn(*args, **kwargs)
            return self._ok(result, f"Called {module_path}.{symbol} successfully")
        except Exception as e:
            return self._fail(
                f"Execution failed for '{module_path}.{symbol}'. Check argument types and units.",
                e,
            )

    def _instantiate_symbol(self, module_path: str, symbol: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._get_module(module_path)
        if mod is None:
            return self._fail(
                f"Module '{module_path}' is unavailable. Install optional compiled/interop dependencies if needed."
            )
        if not hasattr(mod, symbol):
            return self._fail(
                f"Class '{symbol}' not found in '{module_path}'. Verify module and version."
            )
        try:
            cls = getattr(mod, symbol)
            instance = cls(*args, **kwargs)
            return self._ok(instance, f"Instantiated {module_path}.{symbol} successfully")
        except Exception as e:
            return self._fail(
                f"Instantiation failed for '{module_path}.{symbol}'. Review constructor arguments.",
                e,
            )

    # -------------------------------------------------------------------------
    # Health and discovery
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate import readiness and report environment status.

        Returns:
            dict: Unified status dictionary containing loaded modules,
            import errors, and actionable guidance.
        """
        guidance = [
            "Install required dependencies: numpy, scipy, astropy, pyyaml.",
            "For plotting paths install matplotlib.",
            "For interop tests or optional workflows install agama and galpy.",
            "If compiled extensions fail, use pure-Python fallback paths where available.",
        ]
        return self._ok(
            {
                "loaded_modules": sorted(list(self._loaded.keys())),
                "failed_modules": sorted(list(self._import_errors.keys())),
                "import_errors": self._import_errors,
                "guidance": guidance,
            },
            "Adapter health check completed",
        )

    def list_loaded_modules(self) -> Dict[str, Any]:
        return self._ok(sorted(self._loaded.keys()), "Loaded modules listed")

    def inspect_module(self, module_path: str) -> Dict[str, Any]:
        """
        Inspect a module and return public symbols.

        Args:
            module_path: Full module path (e.g., 'gala.dynamics').

        Returns:
            dict: status, module metadata, public symbols, and callable names.
        """
        mod = self._get_module(module_path)
        if mod is None:
            return self._fail(f"Cannot inspect '{module_path}' because import failed.")
        try:
            members = inspect.getmembers(mod)
            public = [n for n, _ in members if not n.startswith("_")]
            callables = [n for n, v in members if callable(v) and not n.startswith("_")]
            classes = [n for n, v in members if inspect.isclass(v) and not n.startswith("_")]
            return self._ok(
                {"module": module_path, "public": public, "callables": callables, "classes": classes},
                f"Inspected {module_path}",
            )
        except Exception as e:
            return self._fail(f"Failed to inspect module '{module_path}'.", e)

    # -------------------------------------------------------------------------
    # Generic invoke/instantiate methods (covers all discoverable features)
    # -------------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function exposed by a gala module.

        Args:
            module_path: Full module path under gala.
            function_name: Function symbol name.
            *args: Positional arguments forwarded to target function.
            **kwargs: Keyword arguments forwarded to target function.

        Returns:
            dict: Unified status and function output.
        """
        return self._call_symbol(module_path, function_name, *args, **kwargs)

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class exposed by a gala module.

        Args:
            module_path: Full module path under gala.
            class_name: Class symbol name.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status and created instance.
        """
        return self._instantiate_symbol(module_path, class_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Curated high-value module wrappers
    # -------------------------------------------------------------------------
    def import_coordinates(self) -> Dict[str, Any]:
        return self._safe_import("gala.coordinates")

    def import_dynamics(self) -> Dict[str, Any]:
        return self._safe_import("gala.dynamics")

    def import_integrate(self) -> Dict[str, Any]:
        return self._safe_import("gala.integrate")

    def import_potential(self) -> Dict[str, Any]:
        return self._safe_import("gala.potential")

    def import_units(self) -> Dict[str, Any]:
        return self._safe_import("gala.units")

    # -------------------------------------------------------------------------
    # Fallback guidance
    # -------------------------------------------------------------------------
    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable guidance when import-mode functionality is partially unavailable.
        """
        return self._ok(
            {
                "mode": self.mode,
                "fallback": "blackbox",
                "when_to_use": "Use blackbox mode if imports fail due to missing compiled extensions or optional interop packages.",
                "recommended_installs": ["numpy", "scipy", "astropy", "pyyaml", "matplotlib"],
                "optional_installs": ["agama", "galpy"],
            },
            "Fallback guidance generated",
        )