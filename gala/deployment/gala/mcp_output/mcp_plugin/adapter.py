import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the gala repository.

    This adapter attempts direct imports from the repository source tree first.
    If imports fail (e.g., compiled extensions unavailable), it switches to a
    graceful fallback mode and returns actionable guidance.
    """

    # ---------------------------------------------------------------------
    # Initialization and module registry
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._module_names: List[str] = [
            "src.gala",
            "src.gala.coordinates",
            "src.gala.dynamics",
            "src.gala.integrate",
            "src.gala.potential",
            "src.gala.units",
            "src.gala.io",
            "src.gala.util",
            "src.gala.logging",
        ]
        self._import_all_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _import_all_modules(self) -> None:
        for name in self._module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._errors[name] = str(e)

        if self._errors:
            self.mode = "fallback"

    # ---------------------------------------------------------------------
    # Status and diagnostics
    # ---------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health, import mode, and module import diagnostics.

        Returns:
            dict: Unified status payload with loaded modules and failed imports.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "failed_imports": self._errors,
                "import_feasibility": 0.93,
                "intrusiveness_risk": "low",
                "complexity": "medium",
            }
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List target modules expected by this adapter.

        Returns:
            dict: Unified status payload including expected, loaded, and failed modules.
        """
        return self._ok(
            {
                "expected_modules": self._module_names,
                "loaded_modules": sorted(self._modules.keys()),
                "failed_imports": self._errors,
            }
        )

    # ---------------------------------------------------------------------
    # Generic module / symbol utilities
    # ---------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a given module path.

        Parameters:
            module_path (str): Full import path, e.g. 'src.gala.integrate.lookup'.
            function_name (str): Function name inside the module.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.

        Returns:
            dict: Unified status payload with function result or error guidance.
        """
        try:
            mod = importlib.import_module(module_path)
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._fail(
                    f"Function '{function_name}' was not found in module '{module_path}'.",
                    hint="Verify the function name with inspect_module_symbols before calling.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module": module_path, "function": function_name, "result": result})
        except Exception as e:
            return self._fail(
                f"Failed to call function '{function_name}' from '{module_path}'.",
                hint="Check arguments, dependency installation, and compiled extension availability.",
                error=e,
            )

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from a given module path.

        Parameters:
            module_path (str): Full import path, e.g. 'src.gala.dynamics.orbit'.
            class_name (str): Class name inside the module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload with class instance or error guidance.
        """
        try:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name, None)
            if cls is None or not inspect.isclass(cls):
                return self._fail(
                    f"Class '{class_name}' was not found in module '{module_path}'.",
                    hint="Verify the class name with inspect_module_symbols before creating an instance.",
                )
            instance = cls(*args, **kwargs)
            return self._ok({"module": module_path, "class": class_name, "instance": instance})
        except Exception as e:
            return self._fail(
                f"Failed to instantiate class '{class_name}' from '{module_path}'.",
                hint="Check constructor parameters and optional dependency requirements.",
                error=e,
            )

    def inspect_module_symbols(self, module_path: str) -> Dict[str, Any]:
        """
        Inspect a module and return discovered classes and functions.

        Parameters:
            module_path (str): Full import path under repository source.

        Returns:
            dict: Unified status payload with class/function symbol lists.
        """
        try:
            mod = importlib.import_module(module_path)
            classes = []
            functions = []
            for name, obj in inspect.getmembers(mod):
                if name.startswith("_"):
                    continue
                if inspect.isclass(obj):
                    classes.append(name)
                elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
                    functions.append(name)

            return self._ok(
                {
                    "module": module_path,
                    "classes": classes,
                    "functions": functions,
                }
            )
        except Exception as e:
            return self._fail(
                f"Failed to inspect module '{module_path}'.",
                hint="Ensure module path is correct and dependencies are installed.",
                error=e,
            )

    # ---------------------------------------------------------------------
    # Repository-focused helper methods (gala domain modules)
    # ---------------------------------------------------------------------
    def inspect_core_packages(self) -> Dict[str, Any]:
        """
        Inspect known gala core packages to expose available classes and functions.

        Returns:
            dict: Unified status payload containing per-module inspection summaries.
        """
        targets = [
            "src.gala",
            "src.gala.coordinates",
            "src.gala.dynamics",
            "src.gala.integrate",
            "src.gala.potential",
            "src.gala.units",
            "src.gala.io",
            "src.gala.util",
            "src.gala.logging",
        ]
        report: Dict[str, Any] = {}
        for module_path in targets:
            report[module_path] = self.inspect_module_symbols(module_path)
        return self._ok({"report": report})

    def dependency_guidance(self) -> Dict[str, Any]:
        """
        Return dependency guidance derived from analysis for successful import-mode operation.

        Returns:
            dict: Unified status payload with required and optional dependencies.
        """
        return self._ok(
            {
                "required": ["python", "numpy", "scipy", "astropy", "pyyaml"],
                "optional": ["matplotlib", "h5py", "galpy", "agama", "cython-compiled extension toolchain"],
                "notes": [
                    "Install required dependencies first.",
                    "If fallback mode is active, verify compiled extensions and build toolchain.",
                    "Use pure-Python pathways where available if extension modules are unavailable.",
                ],
            }
        )

    def fallback_help(self) -> Dict[str, Any]:
        """
        Provide friendly instructions when import mode cannot fully initialize.

        Returns:
            dict: Unified status payload with actionable remediation guidance.
        """
        if self.mode == "import":
            return self._ok({"message": "Adapter is in import mode; fallback guidance is not required."})

        return self._ok(
            {
                "message": "Adapter is running in fallback mode due to import failures.",
                "failed_imports": self._errors,
                "actions": [
                    "Install required dependencies: numpy, scipy, astropy, pyyaml.",
                    "Install optional scientific stack for extended features: matplotlib, h5py, galpy, agama.",
                    "Build/install compiled extensions using the project build system.",
                    "Retry adapter initialization after environment setup.",
                ],
            }
        )