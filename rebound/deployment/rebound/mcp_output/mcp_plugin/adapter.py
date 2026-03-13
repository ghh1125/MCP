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
    MCP Import-mode adapter for the REBOUND repository.

    This adapter attempts to import the source package directly from the local
    `source` directory and exposes practical wrapper methods with unified
    dictionary responses.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._initialize_imports()

    # ---------------------------------------------------------------------
    # Internal utilities
    # ---------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception:
            return None

    def _initialize_imports(self) -> None:
        """
        Import primary REBOUND modules from source package path.

        Fallback behavior:
        - Keeps adapter usable in degraded mode.
        - Returns actionable guidance in method calls.
        """
        try:
            core_mod = self._import_module("rebound")
            sim_mod = self._import_module("rebound.simulation")
            particle_mod = self._import_module("rebound.particle")
            orbit_mod = self._import_module("rebound.orbit")
            rot_mod = self._import_module("rebound.rotation")
            vectors_mod = self._import_module("rebound.vectors")
            units_mod = self._import_module("rebound.units")
            sa_mod = self._import_module("rebound.simulationarchive")
            plotting_mod = self._import_module("rebound.plotting")
            data_mod = self._import_module("rebound.data")
            horizons_mod = self._import_module("rebound.horizons")
            freq_mod = self._import_module("rebound.frequency_analysis")
            tools_mod = self._import_module("rebound.tools")
            hash_mod = self._import_module("rebound.hash")
            variation_mod = self._import_module("rebound.variation")

            modules_for_state = [
                core_mod, sim_mod, particle_mod, orbit_mod, rot_mod, vectors_mod,
                units_mod, sa_mod, plotting_mod, data_mod, horizons_mod, freq_mod,
                tools_mod, hash_mod, variation_mod
            ]

            self._loaded = any(m is not None for m in modules_for_state)

            if core_mod is not None:
                for name in [
                    "Simulation",
                    "Particle",
                    "Orbit",
                    "Rotation",
                    "Vec3d",
                    "Simulationarchive",
                ]:
                    if hasattr(core_mod, name):
                        self._symbols[name] = getattr(core_mod, name)

            if sim_mod is not None and hasattr(sim_mod, "Simulation"):
                self._symbols["Simulation"] = getattr(sim_mod, "Simulation")
            if particle_mod is not None and hasattr(particle_mod, "Particle"):
                self._symbols["Particle"] = getattr(particle_mod, "Particle")
            if orbit_mod is not None and hasattr(orbit_mod, "Orbit"):
                self._symbols["Orbit"] = getattr(orbit_mod, "Orbit")
            if rot_mod is not None and hasattr(rot_mod, "Rotation"):
                self._symbols["Rotation"] = getattr(rot_mod, "Rotation")
            if vectors_mod is not None and hasattr(vectors_mod, "Vec3d"):
                self._symbols["Vec3d"] = getattr(vectors_mod, "Vec3d")
            if sa_mod is not None and hasattr(sa_mod, "Simulationarchive"):
                self._symbols["Simulationarchive"] = getattr(sa_mod, "Simulationarchive")

            if not self._loaded:
                self._import_error = (
                    "Unable to import REBOUND source modules. "
                    "Ensure compiled extension artifacts are available and source path is correct."
                )
        except Exception as e:
            self._loaded = False
            self._import_error = f"Import initialization failed: {e}"

    def _check_loaded(self) -> Optional[Dict[str, Any]]:
        if self._loaded:
            return None
        return self._fail(
            "Adapter is in fallback mode because import failed. "
            "Verify local source checkout, build native extension, and retry.",
            Exception(self._import_error or "Unknown import failure"),
        )

    def _safe_call(self, fn, *args, **kwargs) -> Dict[str, Any]:
        try:
            result = fn(*args, **kwargs)
            return self._ok(result)
        except Exception as e:
            return self._fail("Call failed. Check parameters and object state.", e)

    # ---------------------------------------------------------------------
    # Adapter status and diagnostics
    # ---------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import state and available modules.

        Returns:
            dict: Unified status dictionary with import diagnostics.
        """
        info = {
            "loaded": self._loaded,
            "import_error": self._import_error,
            "modules": sorted(self._modules.keys()),
            "symbols": sorted(self._symbols.keys()),
        }
        return self._ok(info) if self._loaded else self._fail(
            "Import mode is unavailable. Adapter running in fallback mode.",
            Exception(self._import_error or "No modules loaded"),
        )

    # ---------------------------------------------------------------------
    # Class instance factories
    # ---------------------------------------------------------------------
    def create_simulation(self, **kwargs) -> Dict[str, Any]:
        """
        Create a REBOUND Simulation instance.

        Parameters:
            **kwargs: Optional constructor arguments passed to Simulation().

        Returns:
            dict: {status, mode, message, data} where data is Simulation instance.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Simulation")
        if cls is None:
            return self._fail("Simulation class not available. Verify module import integrity.")
        return self._safe_call(cls, **kwargs)

    def create_particle(self, **kwargs) -> Dict[str, Any]:
        """
        Create a REBOUND Particle instance.

        Parameters:
            **kwargs: Particle constructor fields (e.g., m, x, y, z, vx, vy, vz, a, e, inc).

        Returns:
            dict: Unified status dictionary with created Particle.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Particle")
        if cls is None:
            return self._fail("Particle class not available. Verify module import integrity.")
        return self._safe_call(cls, **kwargs)

    def create_orbit(self, **kwargs) -> Dict[str, Any]:
        """
        Create an Orbit instance, when directly constructible.

        Parameters:
            **kwargs: Orbit constructor arguments.

        Returns:
            dict: Unified status dictionary.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Orbit")
        if cls is None:
            return self._fail("Orbit class not available in current build.")
        return self._safe_call(cls, **kwargs)

    def create_rotation(self, **kwargs) -> Dict[str, Any]:
        """
        Create a Rotation instance.

        Parameters:
            **kwargs: Rotation constructor arguments.

        Returns:
            dict: Unified status dictionary with Rotation object.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Rotation")
        if cls is None:
            return self._fail("Rotation class not available in current build.")
        return self._safe_call(cls, **kwargs)

    def create_vec3d(self, **kwargs) -> Dict[str, Any]:
        """
        Create a Vec3d vector instance.

        Parameters:
            **kwargs: Vector constructor arguments.

        Returns:
            dict: Unified status dictionary.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Vec3d")
        if cls is None:
            return self._fail("Vec3d class not available in current build.")
        return self._safe_call(cls, **kwargs)

    def create_simulationarchive(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Create a Simulationarchive instance from file path or stream.

        Parameters:
            *args: Positional arguments for Simulationarchive constructor.
            **kwargs: Keyword arguments for constructor.

        Returns:
            dict: Unified status dictionary.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        cls = self._symbols.get("Simulationarchive")
        if cls is None:
            return self._fail("Simulationarchive class not available in current build.")
        return self._safe_call(cls, *args, **kwargs)

    # ---------------------------------------------------------------------
    # Simulation operations
    # ---------------------------------------------------------------------
    def simulation_add_particle(self, simulation: Any, **particle_kwargs) -> Dict[str, Any]:
        failed = self._check_loaded()
        if failed:
            return failed
        if simulation is None:
            return self._fail("Simulation instance is required.")
        try:
            simulation.add(**particle_kwargs)
            return self._ok(simulation, "Particle added.")
        except Exception as e:
            return self._fail("Failed to add particle. Validate orbital/cartesian parameters.", e)

    def simulation_integrate(self, simulation: Any, tmax: float, exact_finish_time: int = 1) -> Dict[str, Any]:
        failed = self._check_loaded()
        if failed:
            return failed
        if simulation is None:
            return self._fail("Simulation instance is required.")
        try:
            simulation.integrate(tmax, exact_finish_time=exact_finish_time)
            return self._ok({"t": getattr(simulation, "t", None)}, "Integration completed.")
        except Exception as e:
            return self._fail("Integration failed. Check integrator settings and timestep stability.", e)

    def simulation_orbits(self, simulation: Any, **kwargs) -> Dict[str, Any]:
        failed = self._check_loaded()
        if failed:
            return failed
        if simulation is None:
            return self._fail("Simulation instance is required.")
        try:
            result = simulation.orbits(**kwargs)
            return self._ok(result)
        except Exception as e:
            return self._fail("Failed to compute orbits. Ensure enough particles and valid reference frame.", e)

    # ---------------------------------------------------------------------
    # Module function calls
    # ---------------------------------------------------------------------
    def call_horizons_query(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a Horizons utility function when available.

        Notes:
            This method probes common callable names in rebound.horizons.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        mod = self._modules.get("rebound.horizons")
        if mod is None:
            return self._fail("rebound.horizons module is unavailable.")
        for name in ["query_horizons_for_particle", "get_particle", "query"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._fail(
            "No supported Horizons callable found. Inspect rebound.horizons for available API names."
        )

    def call_frequency_analysis(self, *args, **kwargs) -> Dict[str, Any]:
        failed = self._check_loaded()
        if failed:
            return failed
        mod = self._modules.get("rebound.frequency_analysis")
        if mod is None:
            return self._fail("rebound.frequency_analysis module is unavailable.")
        for name in ["frequency", "find_frequency", "spectral_analysis"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._fail(
            "No known frequency-analysis callable found. Verify module version and function names."
        )

    def call_plot_orbits(self, *args, **kwargs) -> Dict[str, Any]:
        failed = self._check_loaded()
        if failed:
            return failed
        mod = self._modules.get("rebound.plotting")
        if mod is None:
            return self._fail("rebound.plotting module is unavailable.")
        for name in ["OrbitPlot", "plot_orbits"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._fail("No plotting callable found. Install matplotlib and verify plotting module API.")

    # ---------------------------------------------------------------------
    # Generic invocation helper
    # ---------------------------------------------------------------------
    def invoke(self, module_path: str, callable_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Generic dynamic invocation for any loaded REBOUND submodule callable.

        Parameters:
            module_path (str): Full module path (e.g., 'rebound.tools').
            callable_name (str): Function/class/callable name in that module.
            *args, **kwargs: Call parameters.

        Returns:
            dict: Unified status dictionary.
        """
        failed = self._check_loaded()
        if failed:
            return failed
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            target = getattr(module, callable_name, None)
            if target is None or not callable(target):
                return self._fail(
                    f"Callable '{callable_name}' not found in module '{module_path}'. "
                    "Check module path and symbol name."
                )
            return self._safe_call(target, *args, **kwargs)
        except Exception as e:
            return self._fail(
                "Dynamic invocation failed. Validate module path, callable name, and arguments.",
                e,
            )

    def get_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for diagnostics.

        Returns:
            dict: Unified status dictionary containing traceback text.
        """
        return self._ok({"traceback": traceback.format_exc()})