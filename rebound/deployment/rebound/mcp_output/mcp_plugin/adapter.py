import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the `rebound` repository.

    This adapter prioritizes direct imports from the local source tree and provides
    graceful fallback behavior when imports are unavailable.
    """

    # ---------------------------------------------------------------------
    # Initialization and module management
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _load_module(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as e:
            self._import_errors[module_path] = f"{type(e).__name__}: {e}"

    def _load_modules(self) -> None:
        module_paths = [
            "rebound",
            "rebound.simulation",
            "rebound.particle",
            "rebound.particles",
            "rebound.orbit",
            "rebound.rotation",
            "rebound.vectors",
            "rebound.variation",
            "rebound.units",
            "rebound.tools",
            "rebound.hash",
            "rebound.data",
            "rebound.plotting",
            "rebound.widget",
            "rebound.horizons",
            "rebound.frequency_analysis",
            "rebound.simulationarchive",
            "rebound.binary_field_descriptor",
            "rebound.citations",
            "rebound.integrators.bs",
            "rebound.integrators.custom",
            "rebound.integrators.eos",
            "rebound.integrators.ias15",
            "rebound.integrators.janus",
            "rebound.integrators.leapfrog",
            "rebound.integrators.mercurius",
            "rebound.integrators.saba",
            "rebound.integrators.sei",
            "rebound.integrators.trace",
            "rebound.integrators.whfast",
            "rebound.integrators.whfast512",
        ]
        for p in module_paths:
            self._load_module(p)

    def get_health(self) -> Dict[str, Any]:
        """
        Report adapter import health and fallback state.

        Returns:
            dict: Unified response with loaded modules, failed modules, and actionable guidance.
        """
        return self._result(
            "success" if len(self._import_errors) == 0 else "partial",
            mode=self.mode,
            loaded_modules=sorted(list(self._modules.keys())),
            failed_modules=self._import_errors,
            guidance=(
                "If imports fail, ensure the local repository exists under 'source/' "
                "and native build artifacts for rebound are available."
            ),
        )

    # ---------------------------------------------------------------------
    # Generic invocation helpers
    # ---------------------------------------------------------------------
    def _get_attr(self, module_path: str, attr_name: str) -> Dict[str, Any]:
        mod = self._modules.get(module_path)
        if mod is None:
            err = self._import_errors.get(module_path, "Module not loaded.")
            return self._result(
                "error",
                error=f"Module '{module_path}' unavailable: {err}",
                guidance="Validate source path and build native extensions before retrying.",
            )
        if not hasattr(mod, attr_name):
            return self._result(
                "error",
                error=f"Attribute '{attr_name}' not found in module '{module_path}'.",
                guidance="Check repository version and available public API members.",
            )
        return self._result("success", obj=getattr(mod, attr_name))

    def _instantiate(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from a module.

        Parameters:
            module_path: Full module path in repository package.
            class_name: Class attribute name.
            *args/**kwargs: Constructor arguments.

        Returns:
            dict: status + instance or error details.
        """
        got = self._get_attr(module_path, class_name)
        if got["status"] != "success":
            return got
        try:
            instance = got["obj"](*args, **kwargs)
            return self._result("success", instance=instance, class_name=class_name, module=module_path)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to instantiate {module_path}.{class_name}: {type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                guidance="Verify constructor arguments and runtime dependencies.",
            )

    def _call(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a module.

        Parameters:
            module_path: Full module path in repository package.
            function_name: Function attribute name.
            *args/**kwargs: Call arguments.

        Returns:
            dict: status + result or error details.
        """
        got = self._get_attr(module_path, function_name)
        if got["status"] != "success":
            return got
        try:
            value = got["obj"](*args, **kwargs)
            return self._result("success", result=value, function=function_name, module=module_path)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to call {module_path}.{function_name}: {type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                guidance="Validate function arguments and input object types.",
            )

    # ---------------------------------------------------------------------
    # Core rebound classes and constructors
    # ---------------------------------------------------------------------
    def create_simulation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.simulation.Simulation instance."""
        return self._instantiate("rebound.simulation", "Simulation", *args, **kwargs)

    def create_particle(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.particle.Particle instance."""
        return self._instantiate("rebound.particle", "Particle", *args, **kwargs)

    def create_orbit(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.orbit.Orbit instance."""
        return self._instantiate("rebound.orbit", "Orbit", *args, **kwargs)

    def create_rotation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.rotation.Rotation instance."""
        return self._instantiate("rebound.rotation", "Rotation", *args, **kwargs)

    def create_vectors(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create vector-like class if available in rebound.vectors."""
        candidates = ["Vec3d", "Vector", "Vectors"]
        for name in candidates:
            res = self._instantiate("rebound.vectors", name, *args, **kwargs)
            if res["status"] == "success":
                return res
        return self._result(
            "error",
            error="No supported vector class found in rebound.vectors.",
            guidance="Inspect rebound.vectors API for available class names.",
        )

    def create_variation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.variation.Variation instance if present."""
        return self._instantiate("rebound.variation", "Variation", *args, **kwargs)

    def create_simulationarchive(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create rebound.simulationarchive.SimulationArchive instance."""
        return self._instantiate("rebound.simulationarchive", "SimulationArchive", *args, **kwargs)

    # ---------------------------------------------------------------------
    # Functional wrappers for key modules
    # ---------------------------------------------------------------------
    def call_horizons(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call primary horizons helper.

        Tries common entry points in rebound.horizons to maximize compatibility.
        """
        for fn in ["get_particle", "query_horizons_for_particle", "horizons"]:
            res = self._call("rebound.horizons", fn, *args, **kwargs)
            if res["status"] == "success":
                return res
        return self._result(
            "error",
            error="No supported horizons call found in rebound.horizons.",
            guidance="Check the horizons module API and provide valid query arguments.",
        )

    def call_frequency_analysis(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call frequency analysis helper from rebound.frequency_analysis."""
        for fn in ["frequency_analysis", "calculate_frequency", "compute_frequency"]:
            res = self._call("rebound.frequency_analysis", fn, *args, **kwargs)
            if res["status"] == "success":
                return res
        return self._result(
            "error",
            error="No supported function found in rebound.frequency_analysis.",
            guidance="Inspect module functions and pass expected time-series inputs.",
        )

    def call_units_convert(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a unit conversion helper from rebound.units."""
        for fn in ["convert_units", "convert", "units_convert"]:
            res = self._call("rebound.units", fn, *args, **kwargs)
            if res["status"] == "success":
                return res
        return self._result(
            "error",
            error="No supported unit conversion function found in rebound.units.",
            guidance="Use documented unit utilities in rebound.units.",
        )

    def call_plotting(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call plotting helper from rebound.plotting."""
        for fn in ["OrbitPlot", "plot_orbits", "plot"]:
            got = self._get_attr("rebound.plotting", fn)
            if got["status"] != "success":
                continue
            try:
                out = got["obj"](*args, **kwargs)
                return self._result("success", result=out, function=fn, module="rebound.plotting")
            except Exception:
                continue
        return self._result(
            "error",
            error="No supported plotting callable succeeded in rebound.plotting.",
            guidance="Install matplotlib and provide a valid simulation object.",
        )

    # ---------------------------------------------------------------------
    # Integrator module access
    # ---------------------------------------------------------------------
    def get_integrator_module(self, name: str) -> Dict[str, Any]:
        """
        Retrieve an integrator module by short name.

        Supported names:
            bs, custom, eos, ias15, janus, leapfrog, mercurius, saba, sei, trace, whfast, whfast512
        """
        module_path = f"rebound.integrators.{name}"
        mod = self._modules.get(module_path)
        if mod is None:
            err = self._import_errors.get(module_path, "Integrator module not loaded.")
            return self._result(
                "error",
                error=f"Integrator module '{module_path}' unavailable: {err}",
                guidance="Ensure this integrator exists in the current repository version.",
            )
        return self._result("success", module=mod, module_path=module_path)

    # ---------------------------------------------------------------------
    # Generic advanced API
    # ---------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dispatcher to call any function in imported modules.

        Parameters:
            module_path: Full module path, e.g. 'rebound.tools'
            function_name: Function or callable attribute name
        """
        return self._call(module_path, function_name, *args, **kwargs)

    def create_class_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dispatcher to instantiate any class in imported modules.

        Parameters:
            module_path: Full module path, e.g. 'rebound.simulation'
            class_name: Class attribute name
        """
        return self._instantiate(module_path, class_name, *args, **kwargs)

    def list_available_api(self) -> Dict[str, Any]:
        """
        List available top-level attributes from loaded modules for discovery.

        Returns:
            dict: status and per-module public attribute names.
        """
        api: Dict[str, List[str]] = {}
        for mod_name, mod in self._modules.items():
            try:
                api[mod_name] = [x for x in dir(mod) if not x.startswith("_")]
            except Exception:
                api[mod_name] = []
        return self._result("success", api=api, failed_modules=self._import_errors)