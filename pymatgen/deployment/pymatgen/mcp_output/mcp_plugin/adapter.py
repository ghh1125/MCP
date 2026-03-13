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
    Import-mode adapter for pymatgen MCP integration.

    This adapter prefers direct Python imports from the local repository source tree.
    If imports are unavailable, methods return actionable fallback guidance and can
    optionally provide CLI invocation hints.
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module registry
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
            "guidance": guidance,
        }

    def _safe_import(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        # CLI modules identified by LLM analysis
        module_paths = [
            "pymatgen.cli.pmg",
            "pymatgen.cli.pmg_analyze",
            "pymatgen.cli.pmg_config",
            "pymatgen.cli.pmg_plot",
            "pymatgen.cli.pmg_structure",
            "pymatgen.cli.get_environment",
            # commonly used extension modules from analysis file tree
            "pymatgen.ext.matproj",
            "pymatgen.ext.cod",
            "pymatgen.ext.optimade",
        ]
        for p in module_paths:
            self._safe_import(p)

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and imported module availability.

        Returns:
            dict: Unified status dictionary with loaded modules and import failures.
        """
        loaded = sorted(self._modules.keys())
        failed = dict(self._import_errors)
        if loaded:
            return self._result(
                status="success",
                message="Adapter initialized with import mode.",
                data={"loaded_modules": loaded, "failed_modules": failed},
                guidance="You can call module-specific methods. Check failed_modules for unavailable features.",
            )
        return self._result(
            status="error",
            message="No target modules could be imported.",
            error="Import initialization failed for all known modules.",
            data={"failed_modules": failed},
            guidance="Verify repository source path and Python dependencies from requirements.txt/pyproject.toml.",
        )

    # -------------------------------------------------------------------------
    # Generic invocation helpers
    # -------------------------------------------------------------------------

    def call_module_function(
        self, module_path: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from a loaded module dynamically.

        Args:
            module_path: Full module path (e.g., 'pymatgen.cli.pmg').
            function_name: Callable name inside the module.
            *args: Positional args passed to callable.
            **kwargs: Keyword args passed to callable.

        Returns:
            dict: Unified status dictionary with function result.
        """
        try:
            mod = self._modules.get(module_path)
            if mod is None:
                if module_path in self._import_errors:
                    return self._result(
                        status="error",
                        message=f"Module '{module_path}' is not available.",
                        error=self._import_errors[module_path],
                        guidance="Install missing dependencies and ensure local source is importable.",
                    )
                return self._result(
                    status="error",
                    message=f"Module '{module_path}' was not registered.",
                    guidance="Use health_check() to inspect available modules.",
                )

            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._result(
                    status="error",
                    message=f"Function '{function_name}' not found in '{module_path}'.",
                    guidance="Inspect module attributes or update function name.",
                )

            result = fn(*args, **kwargs)
            return self._result(
                status="success",
                message=f"Function '{function_name}' executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Function call failed: {module_path}.{function_name}",
                error=f"{type(exc).__name__}: {exc}",
                data={"traceback": traceback.format_exc()},
                guidance="Validate input arguments and module compatibility with current pymatgen version.",
            )

    def create_instance(
        self, module_path: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an instance of a class from a loaded module dynamically.

        Args:
            module_path: Full module path.
            class_name: Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status dictionary with created instance.
        """
        try:
            mod = self._modules.get(module_path)
            if mod is None:
                return self._result(
                    status="error",
                    message=f"Module '{module_path}' not available for instantiation.",
                    error=self._import_errors.get(module_path),
                    guidance="Run health_check() and install required dependencies.",
                )

            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._result(
                    status="error",
                    message=f"Class '{class_name}' not found in '{module_path}'.",
                    guidance="Confirm class name from the target module API.",
                )

            instance = cls(*args, **kwargs)
            return self._result(
                status="success",
                message=f"Instance of '{class_name}' created successfully.",
                data={"instance": instance},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to create instance: {module_path}.{class_name}",
                error=f"{type(exc).__name__}: {exc}",
                data={"traceback": traceback.format_exc()},
                guidance="Check constructor arguments and optional dependency requirements.",
            )

    # -------------------------------------------------------------------------
    # CLI module wrappers (identified by analysis)
    # -------------------------------------------------------------------------

    def pmg(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute pymatgen main CLI entry.

        Args:
            args: Optional list of CLI-like arguments.

        Returns:
            dict: Unified status dictionary with execution outcome.
        """
        args = args or []
        return self.call_module_function("pymatgen.cli.pmg", "main", args)

    def pmg_analyze(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        args = args or []
        return self.call_module_function("pymatgen.cli.pmg_analyze", "main", args)

    def pmg_config(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        args = args or []
        return self.call_module_function("pymatgen.cli.pmg_config", "main", args)

    def pmg_plot(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        args = args or []
        return self.call_module_function("pymatgen.cli.pmg_plot", "main", args)

    def pmg_structure(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        args = args or []
        return self.call_module_function("pymatgen.cli.pmg_structure", "main", args)

    def get_environment(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        args = args or []
        return self.call_module_function("pymatgen.cli.get_environment", "main", args)

    # -------------------------------------------------------------------------
    # Extension module wrappers (useful import-mode features)
    # -------------------------------------------------------------------------

    def matproj_create_rester(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate MPRester from pymatgen.ext.matproj.

        Returns:
            dict: Unified status dictionary containing MPRester instance.
        """
        return self.create_instance("pymatgen.ext.matproj", "MPRester", *args, **kwargs)

    def cod_create_rester(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate COD from pymatgen.ext.cod if available.
        """
        # class names may vary by version; try a few
        for cls_name in ("COD", "CODRester"):
            res = self.create_instance("pymatgen.ext.cod", cls_name, *args, **kwargs)
            if res["status"] == "success":
                return res
        return self._result(
            status="error",
            message="Unable to instantiate COD client.",
            guidance="Inspect pymatgen.ext.cod for available class names in this version.",
        )

    def optimade_create_rester(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate OptimadeRester from pymatgen.ext.optimade.
        """
        return self.create_instance(
            "pymatgen.ext.optimade", "OptimadeRester", *args, **kwargs
        )

    # -------------------------------------------------------------------------
    # Fallback helper
    # -------------------------------------------------------------------------

    def fallback_hint(self, command: str) -> Dict[str, Any]:
        """
        Provide graceful fallback guidance when import mode features are unavailable.

        Args:
            command: Desired command name, e.g. 'pmg', 'pmg_plot'.

        Returns:
            dict: Unified status dictionary with actionable guidance.
        """
        return self._result(
            status="error",
            message=f"Requested feature '{command}' is unavailable in import mode.",
            guidance=(
                f"Try CLI fallback: run '{command} --help'. "
                "If command is missing, install dependencies and ensure source path is correct."
            ),
        )