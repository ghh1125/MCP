import os
import sys
import inspect
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the lightkurve repository.

    This adapter attempts to import the local repository package from `source/src/lightkurve`
    and exposes robust wrapper methods for module loading, class instantiation, function
    invocation, and common workflows.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._module_cache: Dict[str, Any] = {}
        self._class_cache: Dict[str, Any] = {}
        self._function_cache: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialized = False
        self._bootstrap()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode}
        if data:
            out.update(data)
        return out

    def _err(self, message: str, guidance: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "error": message}
        if guidance:
            out["guidance"] = guidance
        if extra:
            out.update(extra)
        return out

    def _bootstrap(self) -> None:
        try:
            self._import_module("lightkurve")
            self._initialized = True
        except Exception as exc:
            self._initialized = False
            self._import_errors["lightkurve"] = str(exc)

    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health and import readiness.
        """
        if self._initialized:
            return self._ok(
                {
                    "initialized": True,
                    "source_path": source_path,
                    "cached_modules": sorted(self._module_cache.keys()),
                }
            )
        return self._err(
            "Adapter initialization failed.",
            guidance="Ensure repository source is present under the expected 'source' directory and dependencies are installed.",
            extra={"initialized": False, "source_path": source_path, "import_errors": self._import_errors},
        )

    # -------------------------------------------------------------------------
    # Dynamic import helpers
    # -------------------------------------------------------------------------
    def _import_module(self, module_path: str) -> Any:
        if module_path in self._module_cache:
            return self._module_cache[module_path]
        mod = importlib.import_module(module_path)
        self._module_cache[module_path] = mod
        return mod

    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import a module by absolute path.

        Parameters:
        - module_path: Full module path (e.g., 'lightkurve.lightcurve').

        Returns:
        Unified status dictionary with module metadata.
        """
        try:
            mod = self._import_module(module_path)
            return self._ok(
                {
                    "module": module_path,
                    "file": getattr(mod, "__file__", None),
                    "name": getattr(mod, "__name__", module_path),
                }
            )
        except Exception as exc:
            return self._err(
                f"Failed to import module '{module_path}'.",
                guidance="Verify module path and confirm required dependencies are installed.",
                extra={"exception": str(exc)},
            )

    def list_known_modules(self) -> Dict[str, Any]:
        """
        List known high-value modules discovered from repository analysis.
        """
        modules = [
            "lightkurve",
            "lightkurve.collections",
            "lightkurve.config",
            "lightkurve.convenience",
            "lightkurve.correctors.cbvcorrector",
            "lightkurve.correctors.corrector",
            "lightkurve.correctors.designmatrix",
            "lightkurve.correctors.metrics",
            "lightkurve.correctors.pldcorrector",
            "lightkurve.correctors.regressioncorrector",
            "lightkurve.correctors.sffcorrector",
            "lightkurve.interact",
            "lightkurve.interact_bls",
            "lightkurve.io.cdips",
            "lightkurve.io.detect",
            "lightkurve.io.eleanor",
            "lightkurve.io.everest",
            "lightkurve.io.folded",
            "lightkurve.io.generic",
            "lightkurve.io.k2sff",
            "lightkurve.io.kepler",
            "lightkurve.io.kepseismic",
            "lightkurve.io.pathos",
            "lightkurve.io.qlp",
            "lightkurve.io.read",
            "lightkurve.io.tasoc",
            "lightkurve.io.tess",
            "lightkurve.io.tglc",
            "lightkurve.lightcurve",
            "lightkurve.lightcurvefile",
            "lightkurve.periodogram",
            "lightkurve.prf.prfmodel",
            "lightkurve.prf.tpfmodel",
            "lightkurve.search",
            "lightkurve.seismology.core",
            "lightkurve.seismology.deltanu_estimators",
            "lightkurve.seismology.numax_estimators",
            "lightkurve.seismology.stellar_estimators",
            "lightkurve.seismology.utils",
            "lightkurve.targetpixelfile",
            "lightkurve.time",
            "lightkurve.units",
            "lightkurve.utils",
        ]
        return self._ok({"modules": modules})

    # -------------------------------------------------------------------------
    # Generic class/function wrappers
    # -------------------------------------------------------------------------
    def _resolve_attr(self, module_path: str, attr_name: str) -> Tuple[Any, Any]:
        mod = self._import_module(module_path)
        if not hasattr(mod, attr_name):
            raise AttributeError(f"Attribute '{attr_name}' not found in module '{module_path}'.")
        return mod, getattr(mod, attr_name)

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a module.
        """
        key = f"{module_path}:{class_name}"
        try:
            _, cls = self._resolve_attr(module_path, class_name)
            obj = cls(*args, **kwargs)
            self._class_cache[key] = obj
            return self._ok({"key": key, "class_name": class_name, "module": module_path, "instance": obj})
        except Exception as exc:
            return self._err(
                f"Failed to create instance for '{class_name}' from '{module_path}'.",
                guidance="Check constructor parameters and ensure optional dependencies for this feature are installed.",
                extra={"exception": str(exc), "key": key},
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a module.
        """
        try:
            _, fn = self._resolve_attr(module_path, function_name)
            if not callable(fn):
                return self._err(f"Attribute '{function_name}' is not callable in '{module_path}'.")
            result = fn(*args, **kwargs)
            return self._ok({"module": module_path, "function": function_name, "result": result})
        except Exception as exc:
            return self._err(
                f"Failed to call function '{function_name}' from '{module_path}'.",
                guidance="Confirm function name and validate argument names/types.",
                extra={"exception": str(exc)},
            )

    # -------------------------------------------------------------------------
    # Lightkurve-specific convenience methods
    # -------------------------------------------------------------------------
    def import_lightkurve(self) -> Dict[str, Any]:
        """
        Import root lightkurve package and return version information when available.
        """
        try:
            lk = self._import_module("lightkurve")
            version = getattr(lk, "__version__", None)
            return self._ok({"module": "lightkurve", "version": version})
        except Exception as exc:
            return self._err(
                "Failed to import 'lightkurve'.",
                guidance="Install required dependencies: numpy, astropy, scipy, matplotlib, requests, astroquery.",
                extra={"exception": str(exc)},
            )

    def search_lightcurve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("lightkurve.search", "search_lightcurve", *args, **kwargs)

    def search_targetpixelfile(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("lightkurve.search", "search_targetpixelfile", *args, **kwargs)

    def read(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("lightkurve.io.read", "read", *args, **kwargs)

    def create_lightcurve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("lightkurve.lightcurve", "LightCurve", *args, **kwargs)

    def create_targetpixelfile(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("lightkurve.targetpixelfile", "TargetPixelFile", *args, **kwargs)

    def create_periodogram(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("lightkurve.periodogram", "Periodogram", *args, **kwargs)

    def create_seismology(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("lightkurve.seismology.core", "Seismology", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Introspection and discovery
    # -------------------------------------------------------------------------
    def module_public_api(self, module_path: str) -> Dict[str, Any]:
        """
        Return public classes/functions for a module.
        """
        try:
            mod = self._import_module(module_path)
            classes: List[str] = []
            functions: List[str] = []
            for name, obj in inspect.getmembers(mod):
                if name.startswith("_"):
                    continue
                if inspect.isclass(obj) and getattr(obj, "__module__", "").startswith(module_path.rsplit(".", 1)[0]):
                    classes.append(name)
                elif inspect.isfunction(obj):
                    functions.append(name)
            return self._ok({"module": module_path, "classes": sorted(set(classes)), "functions": sorted(set(functions))})
        except Exception as exc:
            return self._err(
                f"Failed to inspect module '{module_path}'.",
                guidance="Verify the module imports correctly before introspection.",
                extra={"exception": str(exc)},
            )