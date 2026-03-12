import os
import sys
import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the OSMnx repository.

    This adapter attempts to import the local repository implementation from the
    configured source path and exposes a broad, dynamic API for calling module-level
    functions and creating class instances.

    Unified return format:
    {
        "status": "success" | "error" | "fallback",
        ...
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._functions: Dict[str, Callable[..., Any]] = {}
        self._classes: Dict[str, type] = {}

        self._target_modules = [
            "osmnx",
            "osmnx._api_v1",
            "osmnx._errors",
            "osmnx._http",
            "osmnx._nominatim",
            "osmnx._osm_xml",
            "osmnx._overpass",
            "osmnx._validate",
            "osmnx.bearing",
            "osmnx.convert",
            "osmnx.distance",
            "osmnx.elevation",
            "osmnx.features",
            "osmnx.geocoder",
            "osmnx.graph",
            "osmnx.io",
            "osmnx.plot",
            "osmnx.projection",
            "osmnx.routing",
            "osmnx.settings",
            "osmnx.simplification",
            "osmnx.stats",
            "osmnx.truncate",
            "osmnx.utils",
            "osmnx.utils_geo",
        ]

        self._load_imports()

    # -------------------------------------------------------------------------
    # Core lifecycle
    # -------------------------------------------------------------------------
    def _load_imports(self) -> None:
        try:
            for mod_name in self._target_modules:
                try:
                    module = importlib.import_module(mod_name)
                    self._modules[mod_name] = module
                    self._register_members(module, mod_name)
                except Exception:
                    continue

            self._loaded = len(self._modules) > 0
            if not self._loaded:
                self._import_error = (
                    "No OSMnx modules were imported. Verify repository source is present "
                    "under the expected 'source' directory and dependencies are installed."
                )
        except Exception as exc:
            self._loaded = False
            self._import_error = (
                f"Import initialization failed: {exc}. "
                "Check Python version and required dependencies (networkx, geopandas, "
                "shapely, pandas, numpy, requests, pyproj)."
            )

    def _register_members(self, module: Any, module_name: str) -> None:
        try:
            for name, obj in inspect.getmembers(module):
                if name.startswith("_"):
                    continue
                if inspect.isfunction(obj):
                    self._functions[f"{module_name}.{name}"] = obj
                elif inspect.isclass(obj):
                    self._classes[f"{module_name}.{name}"] = obj
        except Exception:
            pass

    def _fallback(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": message,
            "guidance": guidance
            or "Install required dependencies and ensure local repository source is available.",
            "import_error": self._import_error,
        }

    def _success(self, **payload: Any) -> Dict[str, Any]:
        data = {"status": "success", "mode": self.mode}
        data.update(payload)
        return data

    def _error(self, message: str, exc: Optional[Exception] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(exc) if exc else None,
        }

    # -------------------------------------------------------------------------
    # Status and discovery
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter health and import state.

        Returns:
            dict: Unified status dictionary containing loaded module/function/class counts.
        """
        if not self._loaded:
            return self._fallback(
                "Adapter is running in fallback mode because imports are unavailable.",
                "Confirm the local path contains source/osmnx and install core dependencies.",
            )
        return self._success(
            loaded=True,
            modules=len(self._modules),
            functions=len(self._functions),
            classes=len(self._classes),
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List successfully imported modules.

        Returns:
            dict: Unified status dictionary with module names.
        """
        if not self._loaded:
            return self._fallback("Cannot list modules because import mode is not active.")
        return self._success(modules=sorted(self._modules.keys()))

    def list_functions(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        List discovered functions, optionally filtered by module prefix.

        Args:
            module: Full module name (e.g., 'osmnx.graph') to filter.

        Returns:
            dict: Unified status dictionary with function identifiers.
        """
        if not self._loaded:
            return self._fallback("Cannot list functions because imports failed.")
        names = sorted(self._functions.keys())
        if module:
            names = [n for n in names if n.startswith(f"{module}.")]
        return self._success(functions=names)

    def list_classes(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        List discovered classes, optionally filtered by module prefix.

        Args:
            module: Full module name (e.g., 'osmnx._errors') to filter.

        Returns:
            dict: Unified status dictionary with class identifiers.
        """
        if not self._loaded:
            return self._fallback("Cannot list classes because imports failed.")
        names = sorted(self._classes.keys())
        if module:
            names = [n for n in names if n.startswith(f"{module}.")]
        return self._success(classes=names)

    # -------------------------------------------------------------------------
    # Dynamic function and class execution
    # -------------------------------------------------------------------------
    def call_function(self, function_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a discovered OSMnx function by its full path.

        Args:
            function_path: Full function identifier, e.g. 'osmnx.graph.graph_from_place'.
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: Unified status dictionary with function result.
        """
        if not self._loaded:
            return self._fallback(
                f"Cannot call '{function_path}' because import mode is unavailable."
            )

        fn = self._functions.get(function_path)
        if fn is None:
            return self._error(
                f"Function not found: {function_path}. Use list_functions() to discover valid names."
            )

        try:
            result = fn(*args, **kwargs)
            return self._success(function=function_path, result=result)
        except Exception as exc:
            return self._error(
                f"Function call failed for {function_path}. Check parameter names and value types.",
                exc,
            )

    def create_instance(self, class_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a discovered class by its full path.

        Args:
            class_path: Full class identifier, e.g. 'osmnx._errors.ResponseStatusCodeError'.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status dictionary with instance object.
        """
        if not self._loaded:
            return self._fallback(
                f"Cannot instantiate '{class_path}' because import mode is unavailable."
            )

        cls = self._classes.get(class_path)
        if cls is None:
            return self._error(
                f"Class not found: {class_path}. Use list_classes() to discover valid names."
            )

        try:
            instance = cls(*args, **kwargs)
            return self._success(class_name=class_path, instance=instance)
        except Exception as exc:
            return self._error(
                f"Class instantiation failed for {class_path}. Verify constructor parameters.",
                exc,
            )

    # -------------------------------------------------------------------------
    # OSMnx convenience wrappers (high-value common entry points)
    # -------------------------------------------------------------------------
    def call_osmnx(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function exposed on the top-level 'osmnx' module.

        Args:
            function_name: Public function name available in osmnx namespace.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status dictionary with function result.
        """
        return self.call_function(f"osmnx.{function_name}", *args, **kwargs)

    def call_module_function(
        self, module_name: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from any imported module using module + function name.

        Args:
            module_name: Full module name (e.g., 'osmnx.graph').
            function_name: Function name in that module.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status dictionary with function result.
        """
        return self.call_function(f"{module_name}.{function_name}", *args, **kwargs)

    def create_module_instance(
        self, module_name: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an instance from any imported module using module + class name.

        Args:
            module_name: Full module name (e.g., 'osmnx._errors').
            class_name: Class name in that module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status dictionary with created instance.
        """
        return self.create_instance(f"{module_name}.{class_name}", *args, **kwargs)