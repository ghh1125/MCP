import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for PlasmaPy.

    This adapter prioritizes direct imports from the repository source tree.
    If imports fail, it switches to a graceful fallback mode and returns
    actionable guidance in English.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._load_status = self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _initialize_imports(self) -> Dict[str, Any]:
        """
        Attempt to import key PlasmaPy modules using full package paths discovered
        in analysis. If any critical import fails, switch to fallback mode.
        """
        required_modules = [
            "src.plasmapy",
            "src.plasmapy.formulary",
            "src.plasmapy.particles",
            "src.plasmapy.plasma",
            "src.plasmapy.analysis",
            "src.plasmapy.diagnostics",
            "src.plasmapy.dispersion",
            "src.plasmapy.simulation",
            "src.plasmapy.utils",
        ]
        errors = {}
        for mod_name in required_modules:
            try:
                self._modules[mod_name] = importlib.import_module(mod_name)
            except Exception as exc:
                errors[mod_name] = str(exc)

        if errors:
            self.mode = "fallback"
            return self._result(
                "error",
                message=(
                    "Import mode initialization failed for one or more modules. "
                    "Verify repository layout includes 'source/src/plasmapy', and "
                    "ensure runtime dependencies are installed: numpy, scipy, astropy, packaging."
                ),
                errors=errors,
            )

        return self._result("success", message="All core PlasmaPy modules imported successfully.")

    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.

        Returns:
            dict: Unified response with mode, status, and initialization details.
        """
        return self._result("success", load_status=self._load_status, imported=list(self._modules.keys()))

    # -------------------------------------------------------------------------
    # Module accessors
    # -------------------------------------------------------------------------
    def get_module_plasmapy(self) -> Dict[str, Any]:
        """Get the root module `src.plasmapy`."""
        return self._get_module("src.plasmapy")

    def get_module_formulary(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.formulary`."""
        return self._get_module("src.plasmapy.formulary")

    def get_module_particles(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.particles`."""
        return self._get_module("src.plasmapy.particles")

    def get_module_plasma(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.plasma`."""
        return self._get_module("src.plasmapy.plasma")

    def get_module_analysis(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.analysis`."""
        return self._get_module("src.plasmapy.analysis")

    def get_module_diagnostics(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.diagnostics`."""
        return self._get_module("src.plasmapy.diagnostics")

    def get_module_dispersion(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.dispersion`."""
        return self._get_module("src.plasmapy.dispersion")

    def get_module_simulation(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.simulation`."""
        return self._get_module("src.plasmapy.simulation")

    def get_module_utils(self) -> Dict[str, Any]:
        """Get module `src.plasmapy.utils`."""
        return self._get_module("src.plasmapy.utils")

    def _get_module(self, module_name: str) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result(
                "error",
                message=(
                    f"Adapter is in fallback mode; cannot provide '{module_name}'. "
                    "Resolve import errors and retry."
                ),
            )
        module = self._modules.get(module_name)
        if module is None:
            return self._result(
                "error",
                message=f"Module '{module_name}' is not loaded. Re-run health_check for diagnostics.",
            )
        return self._result("success", module=module, module_name=module_name)

    # -------------------------------------------------------------------------
    # Generic class/function utilities (analysis did not provide explicit symbols)
    # -------------------------------------------------------------------------
    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically instantiate a class from a loaded or importable module.

        Parameters:
            module_name (str): Full module path (e.g., 'src.plasmapy.particles.particle_class').
            class_name (str): Exact class name in the target module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload containing the created instance on success.
        """
        if self.mode != "import":
            return self._result(
                "error",
                message=(
                    "Adapter is in fallback mode. Class instantiation is unavailable. "
                    "Fix import dependencies and project path configuration first."
                ),
            )
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._result(
                "success",
                module_name=module_name,
                class_name=class_name,
                instance=instance,
            )
        except ModuleNotFoundError:
            return self._result(
                "error",
                message=(
                    f"Module '{module_name}' was not found. Ensure the repository source tree is present "
                    "under the configured 'source' directory."
                ),
            )
        except AttributeError:
            return self._result(
                "error",
                message=f"Class '{class_name}' was not found in module '{module_name}'. Verify symbol spelling.",
            )
        except Exception as exc:
            return self._result(
                "error",
                message="Class instantiation failed due to an unexpected runtime error.",
                error=str(exc),
                traceback=traceback.format_exc(),
            )

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from any PlasmaPy module.

        Parameters:
            module_name (str): Full module path (e.g., 'src.plasmapy.formulary.frequencies').
            function_name (str): Exact function name in the module.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Unified status payload containing function result on success.
        """
        if self.mode != "import":
            return self._result(
                "error",
                message=(
                    "Adapter is in fallback mode. Function calls are unavailable. "
                    "Install required dependencies and validate import paths."
                ),
            )
        try:
            module = importlib.import_module(module_name)
            fn = getattr(module, function_name)
            if not callable(fn):
                return self._result(
                    "error",
                    message=(
                        f"Attribute '{function_name}' in '{module_name}' is not callable. "
                        "Provide a valid function name."
                    ),
                )
            output = fn(*args, **kwargs)
            return self._result(
                "success",
                module_name=module_name,
                function_name=function_name,
                result=output,
            )
        except ModuleNotFoundError:
            return self._result(
                "error",
                message=(
                    f"Module '{module_name}' was not found. Confirm local source checkout and sys.path setup."
                ),
            )
        except AttributeError:
            return self._result(
                "error",
                message=f"Function '{function_name}' was not found in module '{module_name}'.",
            )
        except Exception as exc:
            return self._result(
                "error",
                message="Function call failed due to an unexpected runtime error.",
                error=str(exc),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Convenience wrappers for commonly used PlasmaPy entry modules
    # -------------------------------------------------------------------------
    def call_formulary_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from `src.plasmapy.formulary` namespace.

        Parameters:
            function_name (str): Exported function in formulary.
            *args: Positional args.
            **kwargs: Keyword args.
        """
        return self.call_function("src.plasmapy.formulary", function_name, *args, **kwargs)

    def call_particles_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from `src.plasmapy.particles` namespace.
        """
        return self.call_function("src.plasmapy.particles", function_name, *args, **kwargs)

    def create_particles_instance(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from `src.plasmapy.particles` namespace.
        """
        return self.create_instance("src.plasmapy.particles", class_name, *args, **kwargs)

    def call_dispersion_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from `src.plasmapy.dispersion` namespace.
        """
        return self.call_function("src.plasmapy.dispersion", function_name, *args, **kwargs)

    def call_analysis_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from `src.plasmapy.analysis` namespace.
        """
        return self.call_function("src.plasmapy.analysis", function_name, *args, **kwargs)