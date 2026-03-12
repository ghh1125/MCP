import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the pygeos repository source tree.

    Design goals:
    - Prefer direct import/use of repository modules under source/pygeos.
    - Gracefully degrade to fallback mode when native dependencies (GEOS/C extension) are unavailable.
    - Expose rich, maintainable wrappers with unified status dictionary responses.
    - Dynamically surface module-level functions to maximize API coverage.
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt module loading.

        Attributes:
            mode (str): Operation mode. "import" by default, switched to "fallback" on import issues.
            modules (Dict[str, Any]): Loaded module objects.
            errors (List[str]): Initialization/import errors.
            dynamic_function_index (Dict[str, Tuple[str, Any]]): function_name -> (module_name, callable)
        """
        self.mode: str = "import"
        self.modules: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.dynamic_function_index: Dict[str, Tuple[str, Any]] = {}

        self._module_names: List[str] = [
            "pygeos",
            "pygeos.creation",
            "pygeos.constructive",
            "pygeos.coordinates",
            "pygeos.geometry",
            "pygeos.io",
            "pygeos.linear",
            "pygeos.measurement",
            "pygeos.predicates",
            "pygeos.set_operations",
            "pygeos.strtree",
            "pygeos.testing",
            "pygeos.decorators",
            "pygeos.enum",
        ]

        self._load_modules()
        self._index_dynamic_functions()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _load_modules(self) -> None:
        """
        Load repository modules directly from source path.

        Fallback behavior:
        - If any core import fails due to missing binary dependencies or build artifacts,
          keep adapter usable in fallback mode with informative errors.
        """
        for name in self._module_names:
            try:
                self.modules[name] = importlib.import_module(name)
            except Exception as exc:
                self.errors.append(f"{name}: {exc}")

        if "pygeos" not in self.modules:
            self.mode = "fallback"

    def _index_dynamic_functions(self) -> None:
        """
        Build callable index across loaded pygeos submodules.

        This enables broad function coverage even when static analysis did not enumerate every symbol.
        """
        for module_name, mod in self.modules.items():
            try:
                for attr_name, attr_value in inspect.getmembers(mod):
                    if attr_name.startswith("_"):
                        continue
                    if inspect.isfunction(attr_value) or inspect.isbuiltin(attr_value):
                        self.dynamic_function_index[attr_name] = (module_name, attr_value)
            except Exception:
                continue

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import diagnostics.

        Returns:
            dict: Unified status payload with loaded module count, mode, and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(list(self.modules.keys())),
                "loaded_count": len(self.modules),
                "errors": self.errors,
                "dynamic_function_count": len(self.dynamic_function_index),
            },
            message="Adapter initialized",
        )

    def list_available_modules(self) -> Dict[str, Any]:
        """
        List modules successfully imported from repository source.

        Returns:
            dict: Unified status payload containing module names.
        """
        return self._ok({"modules": sorted(self.modules.keys())})

    def list_available_functions(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List callable functions discovered dynamically.

        Args:
            module_name: Optional fully-qualified module filter (e.g., "pygeos.creation").

        Returns:
            dict: Unified status payload with function listing.
        """
        try:
            if module_name:
                if module_name not in self.modules:
                    return self._fail(
                        f"Module not loaded: {module_name}",
                        guidance="Use list_available_modules() to inspect loaded modules.",
                    )
                funcs = sorted(
                    [
                        name
                        for name, (mod_name, _) in self.dynamic_function_index.items()
                        if mod_name == module_name
                    ]
                )
                return self._ok({"module": module_name, "functions": funcs})
            return self._ok(
                {
                    "functions": sorted(self.dynamic_function_index.keys()),
                    "count": len(self.dynamic_function_index),
                }
            )
        except Exception as exc:
            return self._fail("Failed to enumerate functions.", error=exc)

    # -------------------------------------------------------------------------
    # Generic dynamic execution
    # -------------------------------------------------------------------------
    def call_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a dynamically indexed pygeos function by name.

        Args:
            function_name: Function symbol name from loaded pygeos modules.
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: Unified status payload containing module, function, and result.
        """
        if self.mode != "import":
            return self._fail(
                "Adapter is in fallback mode; pygeos binary runtime is unavailable.",
                guidance=(
                    "Install GEOS runtime and ensure source build artifacts are available. "
                    "Then reinitialize the adapter."
                ),
            )
        try:
            if function_name not in self.dynamic_function_index:
                return self._fail(
                    f"Function not found: {function_name}",
                    guidance="Use list_available_functions() to discover supported function names.",
                )
            mod_name, func = self.dynamic_function_index[function_name]
            result = func(*args, **kwargs)
            return self._ok({"module": mod_name, "function": function_name, "result": result})
        except Exception as exc:
            return self._fail(
                f"Failed to execute function '{function_name}'.",
                error=exc,
                guidance="Verify argument types/shapes and geometry validity.",
            )

    # -------------------------------------------------------------------------
    # Class/instance methods for identified class-like APIs
    # -------------------------------------------------------------------------
    def create_strtree(self, geometries: Any, leafsize: int = 10) -> Dict[str, Any]:
        """
        Create a STRtree spatial index instance from input geometries.

        Args:
            geometries: Sequence/array-like geometries compatible with pygeos.
            leafsize: Optional node leaf size for tree construction.

        Returns:
            dict: Unified status payload with created STRtree instance.
        """
        if self.mode != "import":
            return self._fail(
                "Cannot create STRtree in fallback mode.",
                guidance="Enable import mode by resolving pygeos native dependency issues.",
            )
        try:
            mod = self.modules.get("pygeos.strtree")
            if mod is None or not hasattr(mod, "STRtree"):
                return self._fail(
                    "STRtree class is unavailable.",
                    guidance="Ensure pygeos.strtree is importable from source repository.",
                )
            tree = mod.STRtree(geometries, leafsize=leafsize)
            return self._ok({"instance": tree, "class": "pygeos.strtree.STRtree"})
        except Exception as exc:
            return self._fail(
                "Failed to create STRtree instance.",
                error=exc,
                guidance="Check input geometries and leafsize validity.",
            )

    # -------------------------------------------------------------------------
    # High-level grouped helpers by functional modules
    # -------------------------------------------------------------------------
    def call_creation(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.creation", function_name, *args, **kwargs)

    def call_constructive(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.constructive", function_name, *args, **kwargs)

    def call_coordinates(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.coordinates", function_name, *args, **kwargs)

    def call_geometry(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.geometry", function_name, *args, **kwargs)

    def call_io(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.io", function_name, *args, **kwargs)

    def call_linear(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.linear", function_name, *args, **kwargs)

    def call_measurement(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.measurement", function_name, *args, **kwargs)

    def call_predicates(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.predicates", function_name, *args, **kwargs)

    def call_set_operations(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.set_operations", function_name, *args, **kwargs)

    def call_testing(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_module_function("pygeos.testing", function_name, *args, **kwargs)

    def _call_module_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute function by explicit module and symbol names.

        Args:
            module_name: Fully-qualified module name (e.g., pygeos.io).
            function_name: Callable symbol in target module.
            *args: Positional arguments passed to callable.
            **kwargs: Keyword arguments passed to callable.

        Returns:
            dict: Unified status payload with invocation result.
        """
        if self.mode != "import":
            return self._fail(
                f"Cannot execute {module_name}.{function_name} in fallback mode.",
                guidance="Resolve GEOS/C-extension runtime requirements and retry.",
            )
        try:
            mod = self.modules.get(module_name)
            if mod is None:
                return self._fail(
                    f"Module not loaded: {module_name}",
                    guidance="Use health_check() to inspect import errors.",
                )
            if not hasattr(mod, function_name):
                return self._fail(
                    f"Function '{function_name}' not found in module '{module_name}'.",
                    guidance="Use list_available_functions(module_name=...) to inspect callables.",
                )
            fn = getattr(mod, function_name)
            if not callable(fn):
                return self._fail(
                    f"Attribute '{function_name}' in '{module_name}' is not callable.",
                    guidance="Select a valid callable symbol.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module": module_name, "function": function_name, "result": result})
        except Exception as exc:
            return self._fail(
                f"Execution failed for {module_name}.{function_name}.",
                error=exc,
                guidance="Validate input geometry types, dimensions, and optional parameters.",
            )