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
    MCP Import-mode adapter for the `mobile-pest-identification` repository.

    This adapter attempts to import and expose runtime-accessible functionality from:
      - src/pest.py
      - src/utils.py

    It provides:
      - Unified status-based return dictionaries
      - Graceful fallback when imports fail
      - Introspection helpers to discover callable functions/classes
      - Safe invocation wrappers
    """

    # -------------------------------------------------------------------------
    # Initialization / Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt module imports.

        Returns
        -------
        None
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a unified result payload.

        Parameters
        ----------
        status : str
            Operation status, usually "success" or "error".
        message : str
            Human-readable summary.
        data : dict, optional
            Additional response payload.
        error : str, optional
            Error details in English.

        Returns
        -------
        dict
            Unified response dictionary containing at least `status`.
        """
        payload = {"status": status, "message": message}
        if data is not None:
            payload["data"] = data
        if error is not None:
            payload["error"] = error
        return payload

    def _load_modules(self) -> None:
        """
        Import repository modules using full in-repo paths inferred from analysis.

        Target modules:
          - src.pest
          - src.utils
        """
        targets = ["src.pest", "src.utils"]
        for module_path in targets:
            try:
                module = __import__(module_path, fromlist=["*"])
                self._modules[module_path] = module
            except Exception as exc:
                self._import_errors[module_path] = (
                    f"Failed to import '{module_path}'. "
                    f"Check repository layout and dependencies. Detail: {exc}"
                )

    # -------------------------------------------------------------------------
    # Health / Diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter and import health status.

        Returns
        -------
        dict
            Unified status dict with imported modules and import errors.
        """
        ok = len(self._modules) > 0
        return self._result(
            status="success" if ok else "error",
            message="Adapter initialized." if ok else "No modules imported.",
            data={
                "mode": self.mode,
                "imported_modules": sorted(list(self._modules.keys())),
                "import_errors": self._import_errors,
            },
            error=None if ok else "Import failed for all target modules. Install dependencies and verify source path.",
        )

    def list_available_symbols(self) -> Dict[str, Any]:
        """
        List classes and functions available from imported repository modules.

        Returns
        -------
        dict
            Unified status dict with module symbol inventory.
        """
        if not self._modules:
            return self._result(
                status="error",
                message="No modules available for introspection.",
                error="Import modules first. Verify `source/src` exists and dependencies are installed.",
            )

        inventory: Dict[str, Dict[str, List[str]]] = {}
        for module_name, module in self._modules.items():
            classes = []
            functions = []
            for name, obj in inspect.getmembers(module):
                if name.startswith("_"):
                    continue
                if inspect.isclass(obj) and getattr(obj, "__module__", "") == module.__name__:
                    classes.append(name)
                elif inspect.isfunction(obj) and getattr(obj, "__module__", "") == module.__name__:
                    functions.append(name)
            inventory[module_name] = {
                "classes": sorted(classes),
                "functions": sorted(functions),
            }

        return self._result(
            status="success",
            message="Symbol inventory generated.",
            data=inventory,
        )

    # -------------------------------------------------------------------------
    # Generic Invocation Utilities
    # -------------------------------------------------------------------------
    def _resolve_symbol(self, module_path: str, symbol_name: str) -> Dict[str, Any]:
        """
        Resolve a symbol from an imported module.

        Parameters
        ----------
        module_path : str
            Full module path (e.g., 'src.utils').
        symbol_name : str
            Symbol name to fetch.

        Returns
        -------
        dict
            Unified status dict with resolved symbol in data.symbol.
        """
        module = self._modules.get(module_path)
        if module is None:
            err = self._import_errors.get(
                module_path,
                f"Module '{module_path}' is not imported."
            )
            return self._result(
                status="error",
                message="Module not available.",
                error=err,
            )

        if not hasattr(module, symbol_name):
            return self._result(
                status="error",
                message="Symbol not found.",
                error=f"'{symbol_name}' does not exist in '{module_path}'. Use list_available_symbols() to inspect valid names.",
            )

        return self._result(
            status="success",
            message="Symbol resolved.",
            data={"symbol": getattr(module, symbol_name)},
        )

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a repository module.

        Parameters
        ----------
        module_path : str
            Full module path, e.g., 'src.utils' or 'src.pest'.
        class_name : str
            Class name to instantiate.
        *args : Any
            Positional arguments for class constructor.
        **kwargs : Any
            Keyword arguments for class constructor.

        Returns
        -------
        dict
            Unified status dict with instance object in data.instance.
        """
        resolved = self._resolve_symbol(module_path, class_name)
        if resolved["status"] != "success":
            return resolved

        cls = resolved["data"]["symbol"]
        if not inspect.isclass(cls):
            return self._result(
                status="error",
                message="Resolved symbol is not a class.",
                error=f"'{class_name}' in '{module_path}' is not a class. Use call_function() for callables.",
            )

        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="success",
                message="Class instance created.",
                data={"instance": instance, "module_path": module_path, "class_name": class_name},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create class instance.",
                error=f"{exc}",
                data={"traceback": traceback.format_exc()},
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a repository module.

        Parameters
        ----------
        module_path : str
            Full module path, e.g., 'src.utils' or 'src.pest'.
        function_name : str
            Function name to invoke.
        *args : Any
            Positional arguments passed to the function.
        **kwargs : Any
            Keyword arguments passed to the function.

        Returns
        -------
        dict
            Unified status dict containing invocation output in data.result.
        """
        resolved = self._resolve_symbol(module_path, function_name)
        if resolved["status"] != "success":
            return resolved

        fn = resolved["data"]["symbol"]
        if not callable(fn):
            return self._result(
                status="error",
                message="Resolved symbol is not callable.",
                error=f"'{function_name}' in '{module_path}' is not callable.",
            )

        try:
            result = fn(*args, **kwargs)
            return self._result(
                status="success",
                message="Function executed.",
                data={"result": result, "module_path": module_path, "function_name": function_name},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Function execution failed.",
                error=f"{exc}",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Repository-specific Convenience Methods
    # -------------------------------------------------------------------------
    def run_pest_script_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Attempt to run a likely entrypoint in `src.pest`.

        This method tries common entrypoint symbols in order:
          - main
          - run
          - predict
          - infer

        Parameters
        ----------
        *args : Any
            Positional args for entrypoint.
        **kwargs : Any
            Keyword args for entrypoint.

        Returns
        -------
        dict
            Unified status dict with result payload.
        """
        module_path = "src.pest"
        candidates = ["main", "run", "predict", "infer"]

        if module_path not in self._modules:
            return self._result(
                status="error",
                message="pest module unavailable.",
                error=self._import_errors.get(
                    module_path,
                    "Cannot import src.pest. Verify dependencies from requirements.txt."
                ),
            )

        for name in candidates:
            if hasattr(self._modules[module_path], name):
                return self.call_function(module_path, name, *args, **kwargs)

        return self._result(
            status="error",
            message="No recognized entrypoint found in src.pest.",
            error="Expected one of: main/run/predict/infer. Inspect module symbols with list_available_symbols().",
        )

    def call_utils_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function exposed by `src.utils`.

        Parameters
        ----------
        function_name : str
            Exact function name in src.utils.
        *args : Any
            Positional arguments.
        **kwargs : Any
            Keyword arguments.

        Returns
        -------
        dict
            Unified status dict with function result.
        """
        return self.call_function("src.utils", function_name, *args, **kwargs)

    def create_utils_class_instance(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class exposed by `src.utils`.

        Parameters
        ----------
        class_name : str
            Exact class name in src.utils.
        *args : Any
            Positional constructor arguments.
        **kwargs : Any
            Keyword constructor arguments.

        Returns
        -------
        dict
            Unified status dict with created instance.
        """
        return self.create_instance("src.utils", class_name, *args, **kwargs)

    def create_pest_class_instance(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class exposed by `src.pest`.

        Parameters
        ----------
        class_name : str
            Exact class name in src.pest.
        *args : Any
            Positional constructor arguments.
        **kwargs : Any
            Keyword constructor arguments.

        Returns
        -------
        dict
            Unified status dict with created instance.
        """
        return self.create_instance("src.pest", class_name, *args, **kwargs)