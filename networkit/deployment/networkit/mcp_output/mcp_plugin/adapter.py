import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the NetworKit repository.

    This adapter tries to import repository modules from the local `source` path and
    exposes structured wrapper methods with unified return payloads.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded_modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, data: Any = None, message: str = "", error: str = "") -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
            "error": error,
        }

    def _initialize_modules(self) -> None:
        module_names = [
            "networkit",
            "networkit.algebraic",
            "networkit.coloring",
            "networkit.nxadapter",
            "networkit.plot",
            "networkit.support",
            "networkit.vizbridges",
            "networkit.gephi.csv",
            "networkit.gephi.pyclient",
            "networkit.gephi.streaming",
            "networkit.profiling.job",
            "networkit.profiling.multiprocessing_helper",
            "networkit.profiling.plot",
            "networkit.profiling.profiling",
            "networkit.profiling.stat",
            "notebooks.test_notebooks",
        ]
        for mod in module_names:
            try:
                self._loaded_modules[mod] = importlib.import_module(mod)
            except Exception as exc:
                self._import_errors[mod] = str(exc)

    def _get_module(self, module_name: str) -> Optional[Any]:
        return self._loaded_modules.get(module_name)

    def _safe_call(self, module_name: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._get_module(module_name)
        if mod is None:
            err = self._import_errors.get(module_name, "Unknown import failure.")
            return self._result(
                "error",
                message=f"Module '{module_name}' is unavailable.",
                error=f"{err}. Verify compiled NetworKit bindings are built and available in source path.",
            )
        if not hasattr(mod, func_name):
            return self._result(
                "error",
                message=f"Function '{func_name}' not found in '{module_name}'.",
                error="Check repository version and function availability.",
            )
        try:
            fn = getattr(mod, func_name)
            return self._result("success", data=fn(*args, **kwargs), message=f"{module_name}.{func_name} executed.")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Execution failed for {module_name}.{func_name}.",
                error=f"{exc}\n{traceback.format_exc()}",
            )

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter import status and diagnostic information.
        """
        return self._result(
            "success",
            data={
                "loaded_modules": sorted(list(self._loaded_modules.keys())),
                "import_errors": self._import_errors,
                "mode": self.mode,
                "source_path": source_path,
            },
            message="Adapter health check completed.",
        )

    def list_available_modules(self) -> Dict[str, Any]:
        """
        List successfully imported modules.
        """
        return self._result("success", data=sorted(self._loaded_modules.keys()), message="Available modules listed.")

    # -------------------------------------------------------------------------
    # Core NetworKit module wrappers
    # -------------------------------------------------------------------------
    def get_networkit_module(self) -> Dict[str, Any]:
        """
        Get the imported `networkit` module object.

        Returns:
            Unified dictionary with status and module reference.
        """
        mod = self._get_module("networkit")
        if mod is None:
            return self._result(
                "error",
                message="networkit module import failed.",
                error=self._import_errors.get("networkit", "Unknown import failure."),
            )
        return self._result("success", data=mod, message="networkit module available.")

    def call_networkit_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a top-level function or callable attribute from `networkit`.

        Args:
            function_name: Name of the callable on `networkit`.
            *args, **kwargs: Arguments passed to the target callable.
        """
        return self._safe_call("networkit", function_name, *args, **kwargs)

    def instantiate_networkit_class(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from the top-level `networkit` module.

        Args:
            class_name: Class attribute name.
            *args, **kwargs: Constructor parameters.
        """
        mod = self._get_module("networkit")
        if mod is None:
            return self._result("error", message="networkit unavailable.", error=self._import_errors.get("networkit", ""))
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._result("success", data=instance, message=f"Instantiated networkit.{class_name}.")
        except AttributeError:
            return self._result("error", message=f"Class '{class_name}' not found in networkit.", error="Check class name.")
        except Exception as exc:
            return self._result("error", message=f"Failed to instantiate networkit.{class_name}.", error=str(exc))

    # -------------------------------------------------------------------------
    # Submodule generic wrappers
    # -------------------------------------------------------------------------
    def call_algebraic(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.algebraic", function_name, *args, **kwargs)

    def call_coloring(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.coloring", function_name, *args, **kwargs)

    def call_nxadapter(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.nxadapter", function_name, *args, **kwargs)

    def call_plot(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.plot", function_name, *args, **kwargs)

    def call_support(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.support", function_name, *args, **kwargs)

    def call_vizbridges(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.vizbridges", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Gephi module wrappers
    # -------------------------------------------------------------------------
    def call_gephi_csv(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.gephi.csv", function_name, *args, **kwargs)

    def call_gephi_pyclient(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.gephi.pyclient", function_name, *args, **kwargs)

    def call_gephi_streaming(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.gephi.streaming", function_name, *args, **kwargs)

    def instantiate_gephi_class(self, module_suffix: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from Gephi-related modules.

        Args:
            module_suffix: One of 'csv', 'pyclient', 'streaming'.
            class_name: Target class name.
        """
        module_name = f"networkit.gephi.{module_suffix}"
        mod = self._get_module(module_name)
        if mod is None:
            return self._result("error", message=f"{module_name} unavailable.", error=self._import_errors.get(module_name, ""))
        try:
            cls = getattr(mod, class_name)
            return self._result("success", data=cls(*args, **kwargs), message=f"Instantiated {module_name}.{class_name}.")
        except Exception as exc:
            return self._result("error", message=f"Failed to instantiate {module_name}.{class_name}.", error=str(exc))

    # -------------------------------------------------------------------------
    # Profiling module wrappers
    # -------------------------------------------------------------------------
    def call_profiling_job(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.profiling.job", function_name, *args, **kwargs)

    def call_profiling_multiprocessing_helper(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.profiling.multiprocessing_helper", function_name, *args, **kwargs)

    def call_profiling_plot(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.profiling.plot", function_name, *args, **kwargs)

    def call_profiling_profiling(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.profiling.profiling", function_name, *args, **kwargs)

    def call_profiling_stat(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._safe_call("networkit.profiling.stat", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Notebook test helper wrapper
    # -------------------------------------------------------------------------
    def run_notebook_tests(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute notebook test helper entrypoint if present.

        Tries common callable names in notebooks.test_notebooks.
        """
        module_name = "notebooks.test_notebooks"
        mod = self._get_module(module_name)
        if mod is None:
            return self._result(
                "error",
                message="Notebook test module unavailable.",
                error=self._import_errors.get(module_name, "Unknown import failure."),
            )

        for candidate in ("main", "run", "test_notebooks"):
            if hasattr(mod, candidate) and callable(getattr(mod, candidate)):
                try:
                    out = getattr(mod, candidate)(*args, **kwargs)
                    return self._result("success", data=out, message=f"{module_name}.{candidate} executed.")
                except Exception as exc:
                    return self._result("error", message=f"{module_name}.{candidate} failed.", error=str(exc))

        return self._result(
            "error",
            message="No executable notebook test entrypoint found.",
            error="Define one of: main, run, test_notebooks.",
        )