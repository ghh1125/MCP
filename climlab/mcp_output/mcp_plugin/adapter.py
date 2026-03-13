import os
import sys
import traceback
import inspect
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for climlab repository.

    This adapter prioritizes direct import execution against repository source code.
    If import-based execution is unavailable, it gracefully degrades to fallback behavior
    with actionable error guidance.
    """

    # -------------------------------------------------------------------------
    # Initialization and Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._modules_to_load = [
            "climlab",
            "climlab.convection.akmaev_adjustment",
            "climlab.convection.convadj",
            "climlab.convection.emanuel_convection",
            "climlab.convection.simplified_betts_miller",
            "climlab.domain.axis",
            "climlab.domain.domain",
            "climlab.domain.field",
            "climlab.domain.initial",
            "climlab.domain.xarray",
            "climlab.dynamics.adv_diff_numerics",
            "climlab.dynamics.advection_diffusion",
            "climlab.dynamics.budyko_transport",
            "climlab.dynamics.large_scale_condensation",
            "climlab.dynamics.meridional_advection_diffusion",
            "climlab.dynamics.meridional_heat_diffusion",
            "climlab.dynamics.meridional_moist_diffusion",
            "climlab.model.column",
            "climlab.model.ebm",
            "climlab.model.stommelbox",
            "climlab.process.diagnostic",
            "climlab.process.energy_budget",
            "climlab.process.external_forcing",
            "climlab.process.implicit",
            "climlab.process.limiter",
            "climlab.process.process",
            "climlab.process.time_dependent_process",
            "climlab.radiation.absorbed_shorwave",
            "climlab.radiation.aplusbt",
            "climlab.radiation.boltzmann",
            "climlab.radiation.cam3",
            "climlab.radiation.greygas",
            "climlab.radiation.insolation",
            "climlab.radiation.nband",
            "climlab.radiation.radiation",
            "climlab.radiation.rrtm.rrtmg",
            "climlab.radiation.rrtm.rrtmg_lw",
            "climlab.radiation.rrtm.rrtmg_sw",
            "climlab.radiation.rrtm.utils",
            "climlab.radiation.transmissivity",
            "climlab.radiation.water_vapor",
            "climlab.solar.insolation",
            "climlab.solar.orbital.long",
            "climlab.solar.orbital.table",
            "climlab.solar.orbital_cycles",
            "climlab.surface.albedo",
            "climlab.surface.surface_radiation",
            "climlab.surface.turbulent",
            "climlab.utils.constants",
            "climlab.utils.heat_capacity",
            "climlab.utils.legendre",
            "climlab.utils.thermo",
            "climlab.utils.walk",
        ]
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status}
        data.update(kwargs)
        return data

    def _load_modules(self) -> None:
        for mod in self._modules_to_load:
            try:
                self._imports[mod] = importlib.import_module(mod)
            except Exception as e:
                self._import_errors[mod] = f"{type(e).__name__}: {e}"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import readiness.

        Returns:
            dict: Unified status dictionary with mode, loaded modules, and import errors.
        """
        return self._result(
            "ok" if len(self._import_errors) == 0 else "partial",
            mode=self.mode,
            loaded_count=len(self._imports),
            failed_count=len(self._import_errors),
            failed_modules=self._import_errors,
            guidance=(
                "Install required dependencies: numpy, scipy. "
                "Optional: xarray, matplotlib, netCDF4, numba. "
                "RRTMG modules may require Fortran-compiled extensions."
            ),
        )

    # -------------------------------------------------------------------------
    # Generic Reflection and Invocation Utilities
    # -------------------------------------------------------------------------
    def list_module_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        List public symbols in a module.

        Parameters:
            module_name (str): Full module path, e.g., 'climlab.model.ebm'.

        Returns:
            dict: Status + module symbols or error details.
        """
        try:
            mod = self._imports.get(module_name) or importlib.import_module(module_name)
            names = [n for n in dir(mod) if not n.startswith("_")]
            return self._result("ok", module=module_name, symbols=names)
        except Exception as e:
            return self._result(
                "error",
                module=module_name,
                error=f"{type(e).__name__}: {e}",
                guidance="Verify module path and required dependencies.",
            )

    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance from a class in the specified module.

        Parameters:
            module_name (str): Full module import path.
            class_name (str): Class name to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status + created object or actionable error guidance.
        """
        try:
            mod = self._imports.get(module_name) or importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._result("ok", module=module_name, class_name=class_name, instance=instance)
        except Exception as e:
            return self._result(
                "error",
                module=module_name,
                class_name=class_name,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                guidance="Check constructor arguments and optional compiled dependency requirements.",
            )

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from the specified module.

        Parameters:
            module_name (str): Full module import path.
            function_name (str): Function name to call.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Status + function result or clear error details.
        """
        try:
            mod = self._imports.get(module_name) or importlib.import_module(module_name)
            fn = getattr(mod, function_name)
            if not callable(fn):
                return self._result(
                    "error",
                    module=module_name,
                    function_name=function_name,
                    error="Attribute exists but is not callable.",
                    guidance="Use list_module_symbols() to inspect callable APIs.",
                )
            result = fn(*args, **kwargs)
            return self._result("ok", module=module_name, function_name=function_name, result=result)
        except Exception as e:
            return self._result(
                "error",
                module=module_name,
                function_name=function_name,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                guidance="Verify function signature and input types using describe_symbol().",
            )

    def describe_symbol(self, module_name: str, symbol_name: str) -> Dict[str, Any]:
        """
        Describe a symbol signature and docstring for safe invocation.

        Parameters:
            module_name (str): Full module path.
            symbol_name (str): Name of class/function/attribute.

        Returns:
            dict: Status + symbol metadata.
        """
        try:
            mod = self._imports.get(module_name) or importlib.import_module(module_name)
            sym = getattr(mod, symbol_name)
            signature = None
            if callable(sym):
                try:
                    signature = str(inspect.signature(sym))
                except Exception:
                    signature = "unavailable"
            doc = inspect.getdoc(sym) or ""
            return self._result(
                "ok",
                module=module_name,
                symbol_name=symbol_name,
                is_callable=callable(sym),
                signature=signature,
                doc=doc,
                type=str(type(sym)),
            )
        except Exception as e:
            return self._result(
                "error",
                module=module_name,
                symbol_name=symbol_name,
                error=f"{type(e).__name__}: {e}",
                guidance="Confirm symbol exists and module imports correctly.",
            )

    # -------------------------------------------------------------------------
    # Bulk Operations for Full Repository Utilization
    # -------------------------------------------------------------------------
    def scan_all_modules(self) -> Dict[str, Any]:
        """
        Scan all configured modules and report available public classes and functions.

        Returns:
            dict: Status + catalog of discovered APIs across climlab modules.
        """
        catalog: Dict[str, Dict[str, List[str]]] = {}
        errors: Dict[str, str] = {}
        for mod_name in self._modules_to_load:
            try:
                mod = self._imports.get(mod_name) or importlib.import_module(mod_name)
                classes = []
                functions = []
                for name, obj in inspect.getmembers(mod):
                    if name.startswith("_"):
                        continue
                    if inspect.isclass(obj):
                        classes.append(name)
                    elif inspect.isfunction(obj):
                        functions.append(name)
                catalog[mod_name] = {"classes": classes, "functions": functions}
            except Exception as e:
                errors[mod_name] = f"{type(e).__name__}: {e}"

        return self._result(
            "ok" if not errors else "partial",
            catalog=catalog,
            errors=errors,
            guidance="Use create_instance() and call_function() for concrete execution.",
        )

    def invoke(self, module_name: str, symbol_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Unified invoke entrypoint.
        - If symbol is a class: instantiate it.
        - If symbol is callable: call it.

        Parameters:
            module_name (str): Full module path.
            symbol_name (str): Symbol name in module.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status dictionary with invocation result.
        """
        try:
            mod = self._imports.get(module_name) or importlib.import_module(module_name)
            sym = getattr(mod, symbol_name)
            if inspect.isclass(sym):
                return self.create_instance(module_name, symbol_name, *args, **kwargs)
            if callable(sym):
                return self.call_function(module_name, symbol_name, *args, **kwargs)
            return self._result(
                "error",
                module=module_name,
                symbol_name=symbol_name,
                error="Symbol is not callable and not a class.",
                guidance="Use describe_symbol() to inspect valid operations.",
            )
        except Exception as e:
            return self._result(
                "error",
                module=module_name,
                symbol_name=symbol_name,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                guidance="Ensure correct module path and symbol name.",
            )