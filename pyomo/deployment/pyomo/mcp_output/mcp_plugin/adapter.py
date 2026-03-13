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
    MCP import-mode adapter for the Pyomo repository.

    This adapter prioritizes direct module import from the local source tree and provides
    a CLI fallback pathway when import-time failures occur.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_url = "https://github.com/Pyomo/pyomo"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        base = {"status": "success", "mode": self.mode}
        if data:
            base.update(data)
        return base

    def _err(self, message: str, guidance: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _import_module(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[key] = None
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        # Full module paths based on analysis; "source." prefix intentionally removed.
        module_map = {
            "pyomo_main": "pyomo.scripting.pyomo_main",
            "solve_plugin": "pyomo.scripting.plugins.solve",
            "convert_plugin": "pyomo.scripting.plugins.convert",
            "download_plugin": "pyomo.scripting.plugins.download",
            "environ": "pyomo.environ",
            "opt": "pyomo.opt",
        }
        for key, module_path in module_map.items():
            self._import_module(key, module_path)

    def _module_or_fallback(self, key: str) -> Dict[str, Any]:
        mod = self._modules.get(key)
        if mod is not None:
            return self._ok({"module_loaded": True, "module_key": key})
        self.mode = "cli"
        return self._err(
            message=f"Import failed for module '{key}'. Switched to CLI fallback mode.",
            guidance="Verify local source tree under 'source/' and required dependencies (e.g., ply).",
            details=self._import_errors.get(key, "Unknown import error."),
        )

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter status, loaded modules, and import errors.

        Returns:
            dict: Unified status dictionary containing module load summary.
        """
        loaded = {k: (v is not None) for k, v in self._modules.items()}
        return self._ok(
            {
                "repository_url": self.repo_url,
                "loaded_modules": loaded,
                "import_errors": self._import_errors,
                "active_mode": self.mode,
            }
        )

    # -------------------------------------------------------------------------
    # Module-level entry points (identified by analysis)
    # -------------------------------------------------------------------------
    def call_pyomo_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call Pyomo primary CLI entry module function.

        Args:
            argv (list, optional): CLI-style argument vector.

        Returns:
            dict: Unified result with status and optional return value.
        """
        check = self._module_or_fallback("pyomo_main")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["pyomo_main"]
            fn = getattr(mod, "main", None) or getattr(mod, "pyomo_main", None)
            if fn is None:
                return self._err(
                    "No callable entry function found in pyomo.scripting.pyomo_main.",
                    "Inspect the module for available entry function names.",
                )
            ret = fn(argv) if argv is not None else fn()
            return self._ok({"result": ret})
        except Exception as exc:
            return self._err(
                "Failed to execute pyomo main entry.",
                "Check CLI arguments and installed optional solver runtimes.",
                f"{type(exc).__name__}: {exc}",
            )

    def call_solve_command(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute solve-plugin callable if exposed by pyomo.scripting.plugins.solve.

        Args:
            **kwargs: Dynamic keyword arguments forwarded to discovered callable.

        Returns:
            dict: Unified status/result dictionary.
        """
        check = self._module_or_fallback("solve_plugin")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["solve_plugin"]
            candidate_names = ["solve_exec", "solve", "create_parser", "register_options"]
            for name in candidate_names:
                fn = getattr(mod, name, None)
                if callable(fn):
                    result = fn(**kwargs) if kwargs else fn()
                    return self._ok({"called": name, "result": result})
            return self._err(
                "No supported callable found in solve plugin.",
                "Inspect pyomo.scripting.plugins.solve for callable exports.",
            )
        except Exception as exc:
            return self._err(
                "Solve plugin execution failed.",
                "Validate provided arguments and solver availability.",
                f"{type(exc).__name__}: {exc}",
            )

    def call_convert_command(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute convert-plugin callable if exposed by pyomo.scripting.plugins.convert.

        Args:
            **kwargs: Dynamic keyword arguments forwarded to discovered callable.

        Returns:
            dict: Unified status/result dictionary.
        """
        check = self._module_or_fallback("convert_plugin")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["convert_plugin"]
            candidate_names = ["convert_exec", "convert", "create_parser", "register_options"]
            for name in candidate_names:
                fn = getattr(mod, name, None)
                if callable(fn):
                    result = fn(**kwargs) if kwargs else fn()
                    return self._ok({"called": name, "result": result})
            return self._err(
                "No supported callable found in convert plugin.",
                "Inspect pyomo.scripting.plugins.convert for callable exports.",
            )
        except Exception as exc:
            return self._err(
                "Convert plugin execution failed.",
                "Validate model input path and output format options.",
                f"{type(exc).__name__}: {exc}",
            )

    def call_download_extensions_command(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute download plugin callable for extension retrieval workflow.

        Args:
            **kwargs: Dynamic keyword arguments forwarded to discovered callable.

        Returns:
            dict: Unified status/result dictionary.
        """
        check = self._module_or_fallback("download_plugin")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["download_plugin"]
            candidate_names = ["download_exec", "download", "create_parser", "register_options"]
            for name in candidate_names:
                fn = getattr(mod, name, None)
                if callable(fn):
                    result = fn(**kwargs) if kwargs else fn()
                    return self._ok({"called": name, "result": result})
            return self._err(
                "No supported callable found in download plugin.",
                "Inspect pyomo.scripting.plugins.download for callable exports.",
            )
        except Exception as exc:
            return self._err(
                "Download plugin execution failed.",
                "Check network connectivity and local permissions.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Class/function feature wrappers from key modules
    # -------------------------------------------------------------------------
    def create_solver_factory_instance(self, solver_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a solver instance using pyomo.opt.SolverFactory.

        Args:
            solver_name (str): Name of solver (e.g., glpk, cbc, ipopt, highs).
            **kwargs: Additional parameters forwarded to SolverFactory.

        Returns:
            dict: Unified status with created solver object metadata.
        """
        check = self._module_or_fallback("opt")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["opt"]
            cls_or_fn = getattr(mod, "SolverFactory", None)
            if cls_or_fn is None:
                return self._err(
                    "SolverFactory was not found in pyomo.opt.",
                    "Verify Pyomo source integrity and package layout.",
                )
            solver = cls_or_fn(solver_name, **kwargs)
            return self._ok({"solver_name": solver_name, "solver_repr": repr(solver)})
        except Exception as exc:
            return self._err(
                "Failed to create solver instance.",
                "Ensure the solver plugin is installed and discoverable.",
                f"{type(exc).__name__}: {exc}",
            )

    def create_abstract_model_instance(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate pyomo.environ.AbstractModel.

        Args:
            **kwargs: Optional constructor arguments.

        Returns:
            dict: Unified status with model representation.
        """
        check = self._module_or_fallback("environ")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["environ"]
            cls = getattr(mod, "AbstractModel", None)
            if cls is None:
                return self._err(
                    "AbstractModel class is unavailable in pyomo.environ.",
                    "Check source import path and dependency availability.",
                )
            model = cls(**kwargs)
            return self._ok({"model_type": "AbstractModel", "model_repr": repr(model)})
        except Exception as exc:
            return self._err(
                "Failed to instantiate AbstractModel.",
                "Review constructor arguments and Pyomo version compatibility.",
                f"{type(exc).__name__}: {exc}",
            )

    def create_concrete_model_instance(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate pyomo.environ.ConcreteModel.

        Args:
            **kwargs: Optional constructor arguments.

        Returns:
            dict: Unified status with model representation.
        """
        check = self._module_or_fallback("environ")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["environ"]
            cls = getattr(mod, "ConcreteModel", None)
            if cls is None:
                return self._err(
                    "ConcreteModel class is unavailable in pyomo.environ.",
                    "Check source import path and dependency availability.",
                )
            model = cls(**kwargs)
            return self._ok({"model_type": "ConcreteModel", "model_repr": repr(model)})
        except Exception as exc:
            return self._err(
                "Failed to instantiate ConcreteModel.",
                "Review constructor arguments and Pyomo version compatibility.",
                f"{type(exc).__name__}: {exc}",
            )

    def call_value_function(self, obj: Any, exception: bool = True) -> Dict[str, Any]:
        """
        Call pyomo.environ.value() on a Pyomo numeric object/expression.

        Args:
            obj (Any): Pyomo expression/value-like object.
            exception (bool): Whether value() should raise on evaluation issues.

        Returns:
            dict: Unified status with evaluated numeric value.
        """
        check = self._module_or_fallback("environ")
        if check["status"] != "success":
            return check
        try:
            mod = self._modules["environ"]
            fn = getattr(mod, "value", None)
            if fn is None:
                return self._err(
                    "value() function is unavailable in pyomo.environ.",
                    "Validate module exports in local source tree.",
                )
            val = fn(obj, exception=exception)
            return self._ok({"value": val})
        except Exception as exc:
            return self._err(
                "Failed to evaluate value().",
                "Ensure object is a valid Pyomo numeric/expression type.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Generic execution helper
    # -------------------------------------------------------------------------
    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any function from a loaded module.

        Args:
            module_key (str): One of loaded module keys (e.g., 'solve_plugin').
            function_name (str): Callable attribute name.
            *args: Positional args forwarded to target function.
            **kwargs: Keyword args forwarded to target function.

        Returns:
            dict: Unified status with function output.
        """
        check = self._module_or_fallback(module_key)
        if check["status"] != "success":
            return check
        try:
            mod = self._modules[module_key]
            fn = getattr(mod, function_name, None)
            if not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found or not callable in module '{module_key}'.",
                    "Use health_check() and inspect module attributes before calling.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module_key": module_key, "function_name": function_name, "result": result})
        except Exception:
            return self._err(
                f"Dynamic function call failed for '{function_name}'.",
                "Verify signature and provided arguments.",
                traceback.format_exc(limit=2),
            )