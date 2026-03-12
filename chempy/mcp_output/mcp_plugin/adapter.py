import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for the chempy repository.

    This adapter prefers direct in-repo imports ("import" mode) and gracefully
    falls back to a non-executing mode ("blackbox") when imports fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "ok") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": (
                f"Import mode is unavailable for action '{action}'. "
                "Ensure repository source is mounted under 'source/' and required "
                "dependencies are installed (numpy, scipy, sympy)."
            ),
            "import_errors": self._import_errors,
        }

    def _safe_import(self, module_name: str) -> None:
        try:
            self._modules[module_name] = importlib.import_module(module_name)
        except Exception as exc:
            self._import_errors[module_name] = str(exc)

    def _load_modules(self) -> None:
        candidates = [
            "chempy",
            "chempy.chemistry",
            "chempy.equilibria",
            "chempy.reactionsystem",
            "chempy.units",
            "chempy.kinetics.ode",
            "chempy.kinetics.rates",
            "chempy.kinetics.arrhenius",
            "chempy.kinetics.eyring",
            "chempy.printing.string",
            "chempy.printing.pretty",
            "chempy.printing.table",
            "chempy.printing.tables",
            "chempy.printing.numbers",
            "chempy.util.parsing",
            "chempy.util.periodic",
            "chempy.util.stoich",
            "chempy.properties.water_density_tanaka_2001",
            "chempy.properties.water_diffusivity_holz_2000",
            "chempy.properties.water_permittivity_bradley_pitzer_1979",
            "chempy.properties.water_viscosity_korson_1969",
            "chempy.electrochemistry.nernst",
            "chempy.thermodynamics.expressions",
        ]
        for name in candidates:
            self._safe_import(name)

        if self._import_errors:
            self.mode = "blackbox"

    def _get_module(self, name: str) -> Optional[Any]:
        return self._modules.get(name)

    def _resolve_attr(self, module_name: str, attr_name: str) -> Any:
        mod = self._get_module(module_name)
        if mod is None:
            raise ImportError(f"Module '{module_name}' is not available.")
        if not hasattr(mod, attr_name):
            raise AttributeError(f"Attribute '{attr_name}' not found in '{module_name}'.")
        return getattr(mod, attr_name)

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "import_ok": len(self._import_errors) == 0,
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # Generic invocation APIs
    # -------------------------------------------------------------------------
    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from an imported chempy module.

        Args:
            module_name: Full module path (e.g., 'chempy.util.parsing').
            function_name: Function name in that module.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Unified status payload with function result or error details.
        """
        if self.mode != "import":
            return self._fallback(f"{module_name}.{function_name}")
        try:
            fn = self._resolve_attr(module_name, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"called {module_name}.{function_name}")
        except Exception as exc:
            return self._err(
                f"Failed calling function '{module_name}.{function_name}'. "
                "Verify function name and argument compatibility.",
                exc,
            )

    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from an imported chempy module.

        Args:
            module_name: Full module path (e.g., 'chempy.chemistry').
            class_name: Class name in that module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload containing the created instance.
        """
        if self.mode != "import":
            return self._fallback(f"{module_name}.{class_name}")
        try:
            cls = self._resolve_attr(module_name, class_name)
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, message=f"instantiated {module_name}.{class_name}")
        except Exception as exc:
            return self._err(
                f"Failed creating instance '{module_name}.{class_name}'. "
                "Check constructor parameters and dependency availability.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Dedicated high-value wrappers (derived from repository structure)
    # -------------------------------------------------------------------------
    def create_substance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create chempy.chemistry.Substance instance."""
        return self.create_instance("chempy.chemistry", "Substance", *args, **kwargs)

    def create_species(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create chempy.chemistry.Species instance."""
        return self.create_instance("chempy.chemistry", "Species", *args, **kwargs)

    def create_reaction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create chempy.chemistry.Reaction instance."""
        return self.create_instance("chempy.chemistry", "Reaction", *args, **kwargs)

    def create_reaction_system(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create chempy.reactionsystem.ReactionSystem instance."""
        return self.create_instance("chempy.reactionsystem", "ReactionSystem", *args, **kwargs)

    def equilibrium_from_reaction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create chempy.equilibria.EqSystem or equilibrium object based on call."""
        return self.call_function("chempy.equilibria", "EqSystem", *args, **kwargs)

    def parse_formula(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call formula parser utilities from chempy.util.parsing."""
        return self.call_function("chempy.util.parsing", "formula_to_composition", *args, **kwargs)

    def nernst_potential(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call electrochemical Nernst equation helper from chempy.electrochemistry.nernst."""
        return self.call_function("chempy.electrochemistry.nernst", "nernst_potential", *args, **kwargs)

    def arrhenius_equation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call Arrhenius equation helper from chempy.kinetics.arrhenius."""
        return self.call_function("chempy.kinetics.arrhenius", "arrhenius_equation", *args, **kwargs)

    def eyring_equation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call Eyring equation helper from chempy.kinetics.eyring."""
        return self.call_function("chempy.kinetics.eyring", "eyring_equation", *args, **kwargs)

    def water_density(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call water density model from chempy.properties.water_density_tanaka_2001."""
        return self.call_function("chempy.properties.water_density_tanaka_2001", "water_density", *args, **kwargs)

    def water_diffusivity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call water diffusivity model from chempy.properties.water_diffusivity_holz_2000."""
        return self.call_function("chempy.properties.water_diffusivity_holz_2000", "water_self_diffusion_coefficient", *args, **kwargs)

    def water_permittivity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call water permittivity model from chempy.properties.water_permittivity_bradley_pitzer_1979."""
        return self.call_function(
            "chempy.properties.water_permittivity_bradley_pitzer_1979",
            "water_permittivity",
            *args,
            **kwargs,
        )

    def water_viscosity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call water viscosity model from chempy.properties.water_viscosity_korson_1969."""
        return self.call_function("chempy.properties.water_viscosity_korson_1969", "water_viscosity", *args, **kwargs)

    def list_module_functions(self, module_name: str) -> Dict[str, Any]:
        """
        List callable public attributes in a loaded module.

        Args:
            module_name: Full module name.

        Returns:
            dict: Unified status payload with discovered callables.
        """
        if self.mode != "import":
            return self._fallback(f"{module_name}.*")
        try:
            mod = self._get_module(module_name)
            if mod is None:
                raise ImportError(f"Module '{module_name}' is not loaded.")
            funcs = sorted(
                name for name in dir(mod)
                if not name.startswith("_") and callable(getattr(mod, name, None))
            )
            return self._ok({"functions": funcs}, message=f"listed callables in {module_name}")
        except Exception as exc:
            return self._err(
                f"Failed listing module functions for '{module_name}'. "
                "Ensure the module exists and is imported.",
                exc,
            )