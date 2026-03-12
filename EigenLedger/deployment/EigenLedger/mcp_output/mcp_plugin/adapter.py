import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the EigenLedger repository.

    This adapter prefers direct Python imports from the repository source tree and
    falls back to CLI guidance when import execution is unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_name = "EigenLedger"
        self._modules: Dict[str, Any] = {}
        self._import_errors: List[str] = []
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _initialize_modules(self) -> None:
        targets = {
            "EigenLedger.main": "main",
            "EigenLedger.run": "run",
            "EigenLedger.modules.empyrical": "empyrical",
            "EigenLedger.modules.empyrical.stats": "empyrical_stats",
            "EigenLedger.modules.empyrical.utils": "empyrical_utils",
            "EigenLedger.modules.empyrical.perf_attrib": "empyrical_perf_attrib",
            "EigenLedger.modules.empyrical.periods": "empyrical_periods",
            "EigenLedger.modules.empyrical.deprecate": "empyrical_deprecate",
            "EigenLedger.modules.empyrical._version": "empyrical_version",
        }
        for full_path, alias in targets.items():
            try:
                self._modules[alias] = importlib.import_module(full_path)
            except Exception as exc:
                self._modules[alias] = None
                self._import_errors.append(f"Failed to import {full_path}: {exc}")

    def _get_module(self, alias: str) -> Optional[Any]:
        return self._modules.get(alias)

    def _call_attr(self, module_alias: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._get_module(module_alias)
        if mod is None:
            return self._result(
                "error",
                mode=self.mode,
                message=(
                    f"Module '{module_alias}' is not available in import mode. "
                    "Check repository source placement under the 'source' directory, then retry. "
                    "You may also use CLI fallback: python -m EigenLedger.run"
                ),
                import_errors=self._import_errors,
            )
        try:
            if not hasattr(mod, attr_name):
                return self._result(
                    "error",
                    mode=self.mode,
                    message=f"Attribute '{attr_name}' does not exist in module '{module_alias}'.",
                )
            fn = getattr(mod, attr_name)
            if not callable(fn):
                return self._result(
                    "error",
                    mode=self.mode,
                    message=f"Attribute '{attr_name}' in '{module_alias}' is not callable.",
                )
            value = fn(*args, **kwargs)
            return self._result("success", mode=self.mode, data=value, module=module_alias, function=attr_name)
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Function call failed: {module_alias}.{attr_name}",
                error=str(exc),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate import availability and return diagnostics.

        Returns:
            dict: Unified status payload with import map and actionable guidance.
        """
        available = {k: v is not None for k, v in self._modules.items()}
        if all(available.values()):
            return self._result("success", mode=self.mode, available_modules=available, import_errors=self._import_errors)
        return self._result(
            "partial",
            mode=self.mode,
            available_modules=available,
            import_errors=self._import_errors,
            message=(
                "Some modules failed to import. Ensure the repository is unpacked into the 'source' directory "
                "and required dependencies are installed: numpy, pandas, scipy. "
                "Optional: streamlit, matplotlib, plotly, yfinance."
            ),
        )

    # -------------------------------------------------------------------------
    # Repository-level entry points
    # -------------------------------------------------------------------------
    def run_module(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute EigenLedger.run entrypoint logic when available.

        Parameters:
            argv (list[str], optional): Command-style argument list to pass when a main-like callable exists.

        Returns:
            dict: Unified status payload.
        """
        mod = self._get_module("run")
        if mod is None:
            return self._result(
                "error",
                mode=self.mode,
                message=(
                    "EigenLedger.run is unavailable for import execution. "
                    "Fallback commands: 'python -m EigenLedger.run' or 'python EigenLedger/run.py'."
                ),
                import_errors=self._import_errors,
            )

        # Try common entrypoint names
        for name in ("main", "run", "cli"):
            if hasattr(mod, name) and callable(getattr(mod, name)):
                try:
                    fn = getattr(mod, name)
                    result = fn(argv) if argv is not None else fn()
                    return self._result("success", mode=self.mode, entrypoint=name, data=result)
                except TypeError:
                    try:
                        result = getattr(mod, name)()
                        return self._result("success", mode=self.mode, entrypoint=name, data=result)
                    except Exception as exc:
                        return self._result(
                            "error",
                            mode=self.mode,
                            message=f"Entrypoint execution failed: EigenLedger.run.{name}",
                            error=str(exc),
                            traceback=traceback.format_exc(),
                        )
                except Exception as exc:
                    return self._result(
                        "error",
                        mode=self.mode,
                        message=f"Entrypoint execution failed: EigenLedger.run.{name}",
                        error=str(exc),
                        traceback=traceback.format_exc(),
                    )

        return self._result(
            "error",
            mode=self.mode,
            message=(
                "No callable entrypoint found in EigenLedger.run. "
                "Use direct CLI fallback: python -m EigenLedger.run"
            ),
        )

    def call_main(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a callable exposed in EigenLedger.main.

        Parameters:
            function_name (str): Name of the callable in EigenLedger.main.
            *args: Positional arguments for the callable.
            **kwargs: Keyword arguments for the callable.

        Returns:
            dict: Unified status payload.
        """
        return self._call_attr("main", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Empyrical module management
    # -------------------------------------------------------------------------
    def list_empyrical_functions(self, module_alias: str = "empyrical_stats") -> Dict[str, Any]:
        """
        List callable public functions from an empyrical-related module.

        Parameters:
            module_alias (str): One of:
                empyrical, empyrical_stats, empyrical_utils,
                empyrical_perf_attrib, empyrical_periods, empyrical_deprecate, empyrical_version

        Returns:
            dict: Unified status payload with discovered callable names.
        """
        mod = self._get_module(module_alias)
        if mod is None:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Module alias '{module_alias}' is unavailable.",
                import_errors=self._import_errors,
            )
        names = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n, None))]
        return self._result("success", mode=self.mode, module=module_alias, functions=sorted(names))

    def call_empyrical_function(
        self,
        module_alias: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call any callable from an empyrical submodule by alias and function name.

        Parameters:
            module_alias (str): Module alias managed by this adapter.
            function_name (str): Callable name in the selected module.
            *args: Positional arguments passed to callable.
            **kwargs: Keyword arguments passed to callable.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call_attr(module_alias, function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Version / metadata helpers
    # -------------------------------------------------------------------------
    def get_version_info(self) -> Dict[str, Any]:
        """
        Retrieve version-related fields from empyrical _version module if present.

        Returns:
            dict: Unified status payload containing discovered metadata.
        """
        mod = self._get_module("empyrical_version")
        if mod is None:
            return self._result(
                "error",
                mode=self.mode,
                message="Version module is unavailable. Verify source integrity and retry.",
                import_errors=self._import_errors,
            )
        keys = [k for k in dir(mod) if "version" in k.lower() or k in ("__version__", "version_json")]
        data = {k: getattr(mod, k, None) for k in keys}
        return self._result("success", mode=self.mode, data=data)

    # -------------------------------------------------------------------------
    # Generic class/function wrappers (analysis-driven, dynamic-safe)
    # -------------------------------------------------------------------------
    def create_instance(self, module_alias: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a managed module.

        Parameters:
            module_alias (str): Alias of imported module.
            class_name (str): Class name to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload with created instance.
        """
        mod = self._get_module(module_alias)
        if mod is None:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Module alias '{module_alias}' is unavailable for class instantiation.",
                import_errors=self._import_errors,
            )
        try:
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._result("error", mode=self.mode, message=f"Class '{class_name}' not found in '{module_alias}'.")
            instance = cls(*args, **kwargs)
            return self._result("success", mode=self.mode, module=module_alias, class_name=class_name, data=instance)
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Failed to instantiate class: {module_alias}.{class_name}",
                error=str(exc),
                traceback=traceback.format_exc(),
            )