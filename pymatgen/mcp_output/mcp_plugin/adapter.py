import os
import sys
import traceback
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
    MCP Import-Mode Adapter for pymatgen.

    This adapter prioritizes direct Python imports from the repository source tree.
    If an import fails, it degrades gracefully and returns actionable messages.

    Design goals:
    - Unified return format for all methods
    - Robust error handling
    - Explicit import-path usage from repository modules
    - Simple module management helpers for extensibility
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_core_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success", **extra: Any) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message, "data": data}
        payload.update(extra)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, **extra: Any) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(error) if error else None,
        }
        if error is not None:
            payload["traceback"] = traceback.format_exc()
        payload.update(extra)
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None

    def _load_core_modules(self) -> None:
        targets = [
            "pymatgen.cli.pmg",
            "pymatgen.cli.pmg_analyze",
            "pymatgen.cli.pmg_config",
            "pymatgen.cli.pmg_plot",
            "pymatgen.cli.pmg_structure",
            "pymatgen.cli.pmg_potcar",
            "pymatgen.ext.matproj",
            "pymatgen.ext.optimade",
            "pymatgen.ext.cod",
            "pymatgen.analysis.phase_diagram",
            "pymatgen.analysis.reaction_calculator",
            "pymatgen.analysis.structure_matcher",
            "pymatgen.analysis.local_env",
            "pymatgen.analysis.diffraction.xrd",
            "pymatgen.analysis.pourbaix_diagram",
            "pymatgen.analysis.wulff",
            "pymatgen.apps.battery.insertion_battery",
            "pymatgen.apps.battery.conversion_battery",
            "pymatgen.apps.battery.analyzer",
        ]
        for m in targets:
            self._import_module(m)

    def _resolve_attr(self, module_path: str, attr_name: str) -> Any:
        mod = self._modules.get(module_path) or self._import_module(module_path)
        if mod is None:
            raise ImportError(
                f"Unable to import '{module_path}'. Ensure repository source is available under '{source_path}' "
                "and required dependencies are installed."
            )
        if not hasattr(mod, attr_name):
            raise AttributeError(
                f"Attribute '{attr_name}' not found in module '{module_path}'. "
                "Verify the pymatgen version and API compatibility."
            )
        return getattr(mod, attr_name)

    # -------------------------------------------------------------------------
    # Health and capability methods
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status payload with loaded modules, failed modules, and actionable guidance.
        """
        try:
            loaded = sorted(self._modules.keys())
            failed = dict(self._import_errors)
            guidance = []
            if failed:
                guidance.append("Some modules failed to import. Install missing dependencies listed in pyproject.")
                guidance.append("Verify that the source folder contains the pymatgen package.")
            return self._ok(
                data={"loaded_modules": loaded, "failed_modules": failed},
                message="Adapter health check completed.",
                guidance=guidance,
            )
        except Exception as exc:
            return self._fail("Health check failed.", exc)

    def list_cli_commands(self) -> Dict[str, Any]:
        """
        Return known CLI entry modules discovered during analysis.

        Returns:
            dict: Command metadata and module references.
        """
        commands = [
            {"name": "pmg", "module": "pymatgen.cli.pmg", "description": "Primary pymatgen CLI entrypoint."},
            {"name": "pmg analyze", "module": "pymatgen.cli.pmg_analyze", "description": "Analysis helpers."},
            {"name": "pmg config", "module": "pymatgen.cli.pmg_config", "description": "Configuration helpers."},
            {"name": "pmg plot", "module": "pymatgen.cli.pmg_plot", "description": "Plotting CLI helpers."},
            {"name": "pmg structure", "module": "pymatgen.cli.pmg_structure", "description": "Structure CLI helpers."},
            {"name": "pmg potcar", "module": "pymatgen.cli.pmg_potcar", "description": "POTCAR CLI helpers."},
        ]
        return self._ok(data=commands, message="CLI command metadata retrieved.")

    # -------------------------------------------------------------------------
    # External data access modules (pymatgen.ext.*)
    # -------------------------------------------------------------------------
    def instance_mprester(self, api_key: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of MPRester from pymatgen.ext.matproj.

        Parameters:
            api_key (str, optional): Materials Project API key.
            **kwargs: Additional keyword arguments forwarded to MPRester constructor.

        Returns:
            dict: status + instantiated object under data.instance.
        """
        try:
            cls = self._resolve_attr("pymatgen.ext.matproj", "MPRester")
            instance = cls(api_key=api_key, **kwargs)
            return self._ok(data={"instance": instance}, message="MPRester instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create MPRester instance. Provide a valid API key and install optional dependency 'mp-api'.",
                exc,
            )

    def instance_optimade_rester(self, aliases_or_resource_urls: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of OptimadeRester from pymatgen.ext.optimade.

        Parameters:
            aliases_or_resource_urls (list[str], optional): OPTIMADE providers or resource URLs.
            **kwargs: Additional constructor arguments.

        Returns:
            dict: status + instantiated object.
        """
        try:
            cls = self._resolve_attr("pymatgen.ext.optimade", "OptimadeRester")
            instance = cls(aliases_or_resource_urls=aliases_or_resource_urls, **kwargs)
            return self._ok(data={"instance": instance}, message="OptimadeRester instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create OptimadeRester instance. Verify network access and optional dependencies.",
                exc,
            )

    def instance_cod_rester(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of COD from pymatgen.ext.cod.

        Parameters:
            **kwargs: Constructor arguments for COD class.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._resolve_attr("pymatgen.ext.cod", "COD")
            instance = cls(**kwargs)
            return self._ok(data={"instance": instance}, message="COD instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create COD instance. Ensure requests/network dependencies are available.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Analysis module instances
    # -------------------------------------------------------------------------
    def instance_phase_diagram(self, entries: List[Any], elements: Optional[List[Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create PhaseDiagram instance.

        Parameters:
            entries (list): ComputedEntry-like objects.
            elements (list, optional): Optional element list.
            **kwargs: Additional PhaseDiagram constructor kwargs.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._resolve_attr("pymatgen.analysis.phase_diagram", "PhaseDiagram")
            instance = cls(entries=entries, elements=elements, **kwargs)
            return self._ok(data={"instance": instance}, message="PhaseDiagram instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create PhaseDiagram. Ensure entries are valid ComputedEntry-like objects.",
                exc,
            )

    def instance_reaction(self, reactants: List[Any], products: List[Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Create Reaction instance from pymatgen.analysis.reaction_calculator.

        Parameters:
            reactants (list): Reactant compositions/species.
            products (list): Product compositions/species.
            **kwargs: Additional constructor args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._resolve_attr("pymatgen.analysis.reaction_calculator", "Reaction")
            instance = cls(reactants, products, **kwargs)
            return self._ok(data={"instance": instance}, message="Reaction instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create Reaction. Validate reactant/product inputs.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Generic function and class execution helpers
    # -------------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any function in a pymatgen module.

        Parameters:
            module_path (str): Full module path, e.g., 'pymatgen.analysis.diffraction.xrd'
            function_name (str): Function name in module
            *args: Positional args for the function
            **kwargs: Keyword args for the function

        Returns:
            dict: status + function result.
        """
        try:
            fn = self._resolve_attr(module_path, function_name)
            if not callable(fn):
                return self._fail(
                    f"Resolved attribute '{function_name}' is not callable.",
                    None,
                    guidance="Use call_class_method for instance methods or provide a valid function name.",
                )
            result = fn(*args, **kwargs)
            return self._ok(data={"result": result}, message=f"Function '{function_name}' executed.")
        except Exception as exc:
            return self._fail(
                f"Failed to execute function '{function_name}' from '{module_path}'.",
                exc,
            )

    def call_class_method(
        self,
        module_path: str,
        class_name: str,
        method_name: str,
        init_args: Optional[List[Any]] = None,
        init_kwargs: Optional[Dict[str, Any]] = None,
        method_args: Optional[List[Any]] = None,
        method_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically instantiate a class and execute one of its methods.

        Parameters:
            module_path (str): Full module import path.
            class_name (str): Class name.
            method_name (str): Method name on class instance.
            init_args (list, optional): Positional args for class constructor.
            init_kwargs (dict, optional): Keyword args for constructor.
            method_args (list, optional): Positional args for method.
            method_kwargs (dict, optional): Keyword args for method.

        Returns:
            dict: status + instance + method result.
        """
        init_args = init_args or []
        init_kwargs = init_kwargs or {}
        method_args = method_args or []
        method_kwargs = method_kwargs or {}

        try:
            cls = self._resolve_attr(module_path, class_name)
            instance = cls(*init_args, **init_kwargs)
            method = getattr(instance, method_name, None)
            if method is None or not callable(method):
                return self._fail(
                    f"Method '{method_name}' not found or not callable on class '{class_name}'.",
                    None,
                    guidance="Check class API in your pymatgen version.",
                )
            result = method(*method_args, **method_kwargs)
            return self._ok(
                data={"instance": instance, "result": result},
                message=f"Method '{class_name}.{method_name}' executed.",
            )
        except Exception as exc:
            return self._fail(
                f"Failed to execute class method '{class_name}.{method_name}' from '{module_path}'.",
                exc,
            )

    # -------------------------------------------------------------------------
    # CLI fallback helpers (graceful fallback mode within import adapter)
    # -------------------------------------------------------------------------
    def fallback_cli_hint(self, command: str = "pmg --help") -> Dict[str, Any]:
        """
        Provide user guidance when direct import usage is unavailable.

        Parameters:
            command (str): Suggested CLI command.

        Returns:
            dict: status + human-readable guidance.
        """
        return self._ok(
            data={
                "suggested_command": command,
                "notes": [
                    "Import mode is preferred but some optional modules may be unavailable.",
                    "Use CLI commands for operational workflows while resolving Python dependency issues.",
                ],
            },
            message="Fallback guidance generated.",
        )