import os
import sys
import traceback
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the climlab repository.

    This adapter attempts direct import of climlab modules from the local `source` path.
    It exposes structured methods to instantiate key classes and call key functions across
    major functional areas: model construction, radiation, dynamics, domain setup,
    convection, utilities, and diagnostics.

    All public methods return a unified dictionary:
    {
        "status": "success" | "error" | "fallback",
        ...
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._import_all()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, **kwargs) -> Dict[str, Any]:
        out = {"status": "success"}
        out.update(kwargs)
        return out

    def _err(self, message: str, guidance: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        out = {"status": "error", "message": message}
        if guidance:
            out["guidance"] = guidance
        out.update(kwargs)
        return out

    def _fallback(self, message: str, guidance: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        out = {"status": "fallback", "message": message}
        if guidance:
            out["guidance"] = guidance
        out.update(kwargs)
        return out

    def _import_module(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = __import__(module_path, fromlist=["*"])
        except Exception as exc:
            self._errors[key] = f"{exc.__class__.__name__}: {exc}"

    def _import_all(self) -> None:
        module_map = {
            "climlab": "climlab",
            "model_column": "climlab.model.column",
            "model_ebm": "climlab.model.ebm",
            "process_process": "climlab.process.process",
            "process_tdp": "climlab.process.time_dependent_process",
            "domain_initial": "climlab.domain.initial",
            "domain_domain": "climlab.domain.domain",
            "domain_axis": "climlab.domain.axis",
            "radiation_insolation": "climlab.radiation.insolation",
            "solar_insolation": "climlab.solar.insolation",
            "solar_orbital_cycles": "climlab.solar.orbital_cycles",
            "radiation_aplusbt": "climlab.radiation.aplusbt",
            "radiation_boltzmann": "climlab.radiation.boltzmann",
            "radiation_greygas": "climlab.radiation.greygas",
            "radiation_transmissivity": "climlab.radiation.transmissivity",
            "radiation_water_vapor": "climlab.radiation.water_vapor",
            "surface_albedo": "climlab.surface.albedo",
            "surface_turbulent": "climlab.surface.turbulent",
            "surface_surface_radiation": "climlab.surface.surface_radiation",
            "dynamics_advdiff": "climlab.dynamics.advection_diffusion",
            "dynamics_meridional_heat_diffusion": "climlab.dynamics.meridional_heat_diffusion",
            "dynamics_meridional_moist_diffusion": "climlab.dynamics.meridional_moist_diffusion",
            "dynamics_budyko_transport": "climlab.dynamics.budyko_transport",
            "convection_convadj": "climlab.convection.convadj",
            "convection_sbm": "climlab.convection.simplified_betts_miller",
            "convection_emanuel": "climlab.convection.emanuel_convection",
            "utils_constants": "climlab.utils.constants",
            "utils_thermo": "climlab.utils.thermo",
            "utils_heat_capacity": "climlab.utils.heat_capacity",
            "utils_legendre": "climlab.utils.legendre",
        }
        for key, module_path in module_map.items():
            self._import_module(key, module_path)

    def health_check(self) -> Dict[str, Any]:
        """
        Check module import health and adapter readiness.

        Returns:
            dict: Unified status dictionary with loaded module count and import errors.
        """
        loaded = sorted(self._modules.keys())
        errors = dict(self._errors)
        if loaded:
            return self._ok(mode=self.mode, loaded_modules=loaded, import_errors=errors)
        return self._fallback(
            "No modules could be imported in import mode.",
            guidance="Verify the repository exists under the expected source path and required dependencies are installed.",
            mode=self.mode,
            import_errors=errors,
        )

    def list_available_symbols(self, module_key: str) -> Dict[str, Any]:
        """
        List public symbols for a loaded module.

        Args:
            module_key (str): Internal module key from the adapter's module registry.

        Returns:
            dict: Unified status dictionary containing discovered symbols.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._err(
                f"Module key '{module_key}' is not loaded.",
                guidance="Call health_check() to inspect import errors and available module keys.",
            )
        symbols = [s for s in dir(mod) if not s.startswith("_")]
        return self._ok(module_key=module_key, symbols=symbols)

    # -------------------------------------------------------------------------
    # Generic reflective constructor / function caller
    # -------------------------------------------------------------------------
    def create_instance(self, module_key: str, class_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Create an instance of a class from a loaded module.

        Args:
            module_key (str): Internal module key.
            class_name (str): Exact class name in the target module.
            *args: Positional args forwarded to class constructor.
            **kwargs: Keyword args forwarded to class constructor.

        Returns:
            dict: Unified status dictionary with created object.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._fallback(
                f"Module '{module_key}' is unavailable.",
                guidance="Ensure optional dependencies for this module are installed, then rerun health_check().",
            )
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(module_key=module_key, class_name=class_name, instance=instance)
        except AttributeError:
            return self._err(
                f"Class '{class_name}' was not found in module '{module_key}'.",
                guidance="Use list_available_symbols() to inspect available classes.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate '{class_name}' from '{module_key}': {exc}",
                guidance="Check constructor parameters and dependency availability.",
                traceback=traceback.format_exc(),
            )

    def call_function(self, module_key: str, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a function from a loaded module.

        Args:
            module_key (str): Internal module key.
            function_name (str): Exact function name.
            *args: Positional function args.
            **kwargs: Keyword function args.

        Returns:
            dict: Unified status dictionary with function output.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._fallback(
                f"Module '{module_key}' is unavailable.",
                guidance="Confirm imports via health_check() and install missing dependencies.",
            )
        try:
            fn = getattr(mod, function_name)
            if not callable(fn):
                return self._err(
                    f"Symbol '{function_name}' in '{module_key}' is not callable.",
                    guidance="Use list_available_symbols() to choose a callable function.",
                )
            result = fn(*args, **kwargs)
            return self._ok(module_key=module_key, function_name=function_name, result=result)
        except AttributeError:
            return self._err(
                f"Function '{function_name}' was not found in module '{module_key}'.",
                guidance="Use list_available_symbols() to inspect available functions.",
            )
        except Exception as exc:
            return self._err(
                f"Function call failed for '{function_name}' in '{module_key}': {exc}",
                guidance="Validate the function signature and argument values.",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Dedicated class instance methods (high-value, commonly used)
    # -------------------------------------------------------------------------
    def create_ebm(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.model.ebm.EBM."""
        return self.create_instance("model_ebm", "EBM", *args, **kwargs)

    def create_ebm_seasonal(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.model.ebm.EBM_seasonal."""
        return self.create_instance("model_ebm", "EBM_seasonal", *args, **kwargs)

    def create_radiative_convective_model(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.model.column.RadiativeConvectiveModel."""
        return self.create_instance("model_column", "RadiativeConvectiveModel", *args, **kwargs)

    def create_grey_radiation_model(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.model.column.GreyRadiationModel."""
        return self.create_instance("model_column", "GreyRadiationModel", *args, **kwargs)

    def create_band_rc_model(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.model.column.BandRCModel."""
        return self.create_instance("model_column", "BandRCModel", *args, **kwargs)

    def create_process(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.process.process.Process."""
        return self.create_instance("process_process", "Process", *args, **kwargs)

    def create_time_dependent_process(self, *args, **kwargs) -> Dict[str, Any]:
        """Instantiate climlab.process.time_dependent_process.TimeDependentProcess."""
        return self.create_instance("process_tdp", "TimeDependentProcess", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dedicated function call methods (broad utility coverage)
    # -------------------------------------------------------------------------
    def call_daily_insolation(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.solar.insolation.daily_insolation."""
        return self.call_function("solar_insolation", "daily_insolation", *args, **kwargs)

    def call_instant_insolation(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.solar.insolation.instant_insolation."""
        return self.call_function("solar_insolation", "instant_insolation", *args, **kwargs)

    def call_orbital_parameters(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.solar.orbital_cycles.OrbitalTable or helpers through generic function path."""
        return self.call_function("solar_orbital_cycles", "OrbitalTable", *args, **kwargs)

    def call_initial_column_state(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.domain.initial.column_state."""
        return self.call_function("domain_initial", "column_state", *args, **kwargs)

    def call_initial_surface_state(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.domain.initial.surface_state."""
        return self.call_function("domain_initial", "surface_state", *args, **kwargs)

    def call_potential_temperature(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.utils.thermo.potential_temperature."""
        return self.call_function("utils_thermo", "potential_temperature", *args, **kwargs)

    def call_clausius_clapeyron(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.utils.thermo.clausius_clapeyron."""
        return self.call_function("utils_thermo", "clausius_clapeyron", *args, **kwargs)

    def call_heat_capacity_atm(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.utils.heat_capacity.atmosphere."""
        return self.call_function("utils_heat_capacity", "atmosphere", *args, **kwargs)

    def call_legendre_polynomial(self, *args, **kwargs) -> Dict[str, Any]:
        """Call climlab.utils.legendre.Pn."""
        return self.call_function("utils_legendre", "Pn", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Introspection and discovery methods for full utilization
    # -------------------------------------------------------------------------
    def list_loaded_modules(self) -> Dict[str, Any]:
        """
        Return all successfully loaded modules and import failures.

        Returns:
            dict: Unified status dictionary with module inventory.
        """
        return self._ok(loaded_modules=sorted(self._modules.keys()), import_errors=self._errors)

    def describe_callable(self, module_key: str, symbol_name: str) -> Dict[str, Any]:
        """
        Describe signature and docstring of a callable symbol.

        Args:
            module_key (str): Internal module key.
            symbol_name (str): Symbol to inspect.

        Returns:
            dict: Unified status dictionary with signature and documentation snippet.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._err(
                f"Module key '{module_key}' is not loaded.",
                guidance="Use list_loaded_modules() to choose a valid module key.",
            )
        try:
            obj = getattr(mod, symbol_name)
            if not callable(obj):
                return self._err(
                    f"Symbol '{symbol_name}' in '{module_key}' is not callable.",
                    guidance="Choose a function or class symbol.",
                )
            sig = str(inspect.signature(obj))
            doc = inspect.getdoc(obj) or ""
            return self._ok(module_key=module_key, symbol_name=symbol_name, signature=sig, doc=doc[:3000])
        except Exception as exc:
            return self._err(
                f"Could not inspect '{symbol_name}' in '{module_key}': {exc}",
                guidance="Verify the symbol exists and can be introspected.",
            )