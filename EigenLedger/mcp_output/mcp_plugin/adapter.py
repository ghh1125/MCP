import os
import sys
import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for EigenLedger.

    This adapter prioritizes direct Python imports and provides graceful fallbacks
    when imports are unavailable or symbols cannot be resolved.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_name = "EigenLedger"
        self._modules: Dict[str, Optional[Any]] = {}
        self._functions: Dict[str, Callable[..., Any]] = {}
        self._classes: Dict[str, type] = {}
        self._load_state: Dict[str, Any] = {
            "status": "initializing",
            "imported_modules": [],
            "failed_modules": {},
            "available_functions": [],
            "available_classes": [],
            "notes": [],
        }
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
        }

    def _safe_import(self, module_path: str) -> Tuple[Optional[Any], Optional[str]]:
        try:
            module = importlib.import_module(module_path)
            return module, None
        except Exception as exc:
            return None, (
                f"Failed to import '{module_path}'. Verify repository source path, "
                f"Python version compatibility, and required dependencies. Details: {exc}"
            )

    def _register_module(self, module_path: str) -> None:
        module, err = self._safe_import(module_path)
        self._modules[module_path] = module
        if module is not None:
            self._load_state["imported_modules"].append(module_path)
        else:
            self._load_state["failed_modules"][module_path] = err

    def _extract_symbols(self, module_path: str) -> None:
        module = self._modules.get(module_path)
        if module is None:
            return
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            try:
                if inspect.isfunction(obj):
                    key = f"{module_path}.{name}"
                    self._functions[key] = obj
                elif inspect.isclass(obj):
                    key = f"{module_path}.{name}"
                    self._classes[key] = obj
            except Exception:
                continue

    def _initialize_imports(self) -> None:
        candidate_modules = [
            "EigenLedger.main",
            "EigenLedger.run",
            "EigenLedger.modules.empyrical",
            "EigenLedger.modules.empyrical.stats",
            "EigenLedger.modules.empyrical.utils",
            "EigenLedger.modules.empyrical.perf_attrib",
            "EigenLedger.modules.empyrical.periods",
            "EigenLedger.modules.empyrical.deprecate",
            "EigenLedger.modules.empyrical._version",
        ]

        for module_path in candidate_modules:
            self._register_module(module_path)

        for module_path in candidate_modules:
            self._extract_symbols(module_path)

        self._load_state["available_functions"] = sorted(self._functions.keys())
        self._load_state["available_classes"] = sorted(self._classes.keys())

        if self._load_state["imported_modules"]:
            self._load_state["status"] = "ready"
            self._load_state["notes"].append(
                "Import mode initialized. Direct function/class execution is available where symbols exist."
            )
        else:
            self._load_state["status"] = "fallback"
            self._load_state["notes"].append(
                "No target modules were imported. Use CLI fallback methods."
            )

    def _resolve_function(self, function_name: str) -> Optional[Callable[..., Any]]:
        direct_candidates = [
            function_name,
            f"EigenLedger.main.{function_name}",
            f"EigenLedger.run.{function_name}",
            f"EigenLedger.modules.empyrical.{function_name}",
            f"EigenLedger.modules.empyrical.stats.{function_name}",
            f"EigenLedger.modules.empyrical.utils.{function_name}",
            f"EigenLedger.modules.empyrical.perf_attrib.{function_name}",
            f"EigenLedger.modules.empyrical.periods.{function_name}",
            f"EigenLedger.modules.empyrical.deprecate.{function_name}",
            f"EigenLedger.modules.empyrical._version.{function_name}",
        ]
        for key in direct_candidates:
            if key in self._functions:
                return self._functions[key]
        return None

    def _resolve_class(self, class_name: str) -> Optional[type]:
        direct_candidates = [
            class_name,
            f"EigenLedger.main.{class_name}",
            f"EigenLedger.run.{class_name}",
            f"EigenLedger.modules.empyrical.{class_name}",
            f"EigenLedger.modules.empyrical.stats.{class_name}",
            f"EigenLedger.modules.empyrical.utils.{class_name}",
            f"EigenLedger.modules.empyrical.perf_attrib.{class_name}",
            f"EigenLedger.modules.empyrical.periods.{class_name}",
            f"EigenLedger.modules.empyrical.deprecate.{class_name}",
            f"EigenLedger.modules.empyrical._version.{class_name}",
        ]
        for key in direct_candidates:
            if key in self._classes:
                return self._classes[key]
        return None

    # -------------------------------------------------------------------------
    # Adapter status and discovery
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter initialization and import status.

        Returns:
            dict: Unified status dictionary with loaded modules, available symbols,
            and import errors if any.
        """
        return self._result(
            status="success",
            message="Adapter status retrieved.",
            data=self._load_state,
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List imported and failed modules managed by this adapter.

        Returns:
            dict: Includes imported module names and failure diagnostics.
        """
        data = {
            "imported_modules": self._load_state.get("imported_modules", []),
            "failed_modules": self._load_state.get("failed_modules", {}),
        }
        return self._result("success", "Module inventory retrieved.", data=data)

    def list_functions(self) -> Dict[str, Any]:
        """
        List all discovered callable functions from imported EigenLedger modules.

        Returns:
            dict: Available function symbol paths.
        """
        return self._result(
            "success",
            "Discovered functions retrieved.",
            data={"functions": self._load_state.get("available_functions", [])},
        )

    def list_classes(self) -> Dict[str, Any]:
        """
        List all discovered classes from imported EigenLedger modules.

        Returns:
            dict: Available class symbol paths.
        """
        return self._result(
            "success",
            "Discovered classes retrieved.",
            data={"classes": self._load_state.get("available_classes", [])},
        )

    # -------------------------------------------------------------------------
    # Generic invocation APIs (covers all identified functions/classes dynamically)
    # -------------------------------------------------------------------------
    def call_function(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call a repository function by name using import mode.

        Parameters:
            function_name (str): Function name or fully-qualified symbol path.
            *args: Positional arguments passed to the target function.
            **kwargs: Keyword arguments passed to the target function.

        Returns:
            dict: Unified result with execution output or actionable error guidance.
        """
        func = self._resolve_function(function_name)
        if func is None:
            return self._result(
                "error",
                "Requested function was not found in imported modules.",
                error=(
                    f"Function '{function_name}' is unavailable. "
                    "Use list_functions() to inspect valid names or switch to CLI fallback."
                ),
            )
        try:
            output = func(*args, **kwargs)
            return self._result(
                "success",
                f"Function '{function_name}' executed successfully.",
                data={"result": output},
            )
        except Exception as exc:
            return self._result(
                "error",
                f"Function '{function_name}' execution failed.",
                error=(
                    f"Check argument types, required data inputs, and function preconditions. Details: {exc}"
                ),
            )

    def create_instance(
        self,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Instantiate a repository class by name.

        Parameters:
            class_name (str): Class name or fully-qualified symbol path.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Contains instantiated object on success.
        """
        cls = self._resolve_class(class_name)
        if cls is None:
            return self._result(
                "error",
                "Requested class was not found in imported modules.",
                error=(
                    f"Class '{class_name}' is unavailable. "
                    "Use list_classes() to inspect valid names or switch to CLI fallback."
                ),
            )
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                "success",
                f"Class '{class_name}' instantiated successfully.",
                data={"instance": instance, "class": cls.__name__},
            )
        except Exception as exc:
            return self._result(
                "error",
                f"Class '{class_name}' instantiation failed.",
                error=(
                    f"Review constructor arguments and dependency availability. Details: {exc}"
                ),
            )

    def invoke_method(
        self,
        instance: Any,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Invoke a method on a previously created class instance.

        Parameters:
            instance (Any): Target object instance.
            method_name (str): Method name to invoke.
            *args: Positional method arguments.
            **kwargs: Keyword method arguments.

        Returns:
            dict: Method execution result or error details.
        """
        if instance is None:
            return self._result(
                "error",
                "Instance is required.",
                error="Pass a valid object instance returned by create_instance().",
            )
        method = getattr(instance, method_name, None)
        if method is None or not callable(method):
            return self._result(
                "error",
                "Method not found on instance.",
                error=(
                    f"Method '{method_name}' does not exist or is not callable on instance "
                    f"of type '{type(instance).__name__}'."
                ),
            )
        try:
            output = method(*args, **kwargs)
            return self._result(
                "success",
                f"Method '{method_name}' executed successfully.",
                data={"result": output},
            )
        except Exception as exc:
            return self._result(
                "error",
                f"Method '{method_name}' execution failed.",
                error=f"Verify method arguments and object state. Details: {exc}",
            )

    # -------------------------------------------------------------------------
    # CLI fallback management
    # -------------------------------------------------------------------------
    def get_cli_fallback_commands(self) -> Dict[str, Any]:
        """
        Return recommended CLI fallback commands from analysis.

        Returns:
            dict: Commands usable when direct imports are incomplete.
        """
        commands = [
            {
                "name": "python -m source.EigenLedger.run",
                "module": "source.EigenLedger.run",
                "description": "Use module-execution entry path when direct imports are unstable.",
            },
            {
                "name": "python -m source.EigenLedger.main",
                "module": "source.EigenLedger.main",
                "description": "Use orchestration module execution if available.",
            },
        ]
        return self._result(
            "success",
            "CLI fallback commands retrieved.",
            data={"commands": commands},
        )