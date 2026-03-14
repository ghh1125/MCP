import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the GMatch4py repository.

    This adapter attempts to import repository modules directly from the local
    `source` directory and exposes unified wrapper methods for discovered
    functions and classes.

    Unified return format:
        {
            "status": "success" | "error" | "fallback",
            "mode": "import",
            "message": str,
            ... extra fields ...
        }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self.repo_name = "GMatch4py"
        self.repo_url = "https://github.com/Jacobe2169/GMatch4py"
        self.import_strategy = {"primary": "import", "fallback": "blackbox", "confidence": 0.9}
        self.required_dependencies = ["numpy", "networkx", "scipy", "scikit-learn"]

        self.modules: Dict[str, Optional[Any]] = {}
        self.symbols: Dict[str, Optional[Any]] = {}
        self.last_error: Optional[str] = None

        self._initialize_imports()

    def _result(self, status: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status, "mode": self.mode, "message": message}
        data.update(kwargs)
        return data

    def _safe_import_module(self, module_path: str) -> Dict[str, Any]:
        try:
            module = importlib.import_module(module_path)
            self.modules[module_path] = module
            return self._result("success", f"Imported module '{module_path}' successfully.", module_path=module_path)
        except Exception as e:
            self.modules[module_path] = None
            err = f"Failed to import module '{module_path}': {e}"
            self.last_error = err
            return self._result(
                "fallback",
                err + " Verify local source files and Python dependencies are available.",
                module_path=module_path,
                error=str(e),
            )

    def _safe_get_symbol(self, module_path: str, symbol_name: str) -> Dict[str, Any]:
        module = self.modules.get(module_path)
        if module is None:
            return self._result(
                "fallback",
                f"Module '{module_path}' is not available. Import the module before requesting symbol '{symbol_name}'.",
                module_path=module_path,
                symbol_name=symbol_name,
            )
        try:
            symbol = getattr(module, symbol_name)
            self.symbols[f"{module_path}.{symbol_name}"] = symbol
            return self._result(
                "success",
                f"Loaded symbol '{symbol_name}' from '{module_path}'.",
                module_path=module_path,
                symbol_name=symbol_name,
            )
        except Exception as e:
            err = f"Failed to load symbol '{symbol_name}' from '{module_path}': {e}"
            self.last_error = err
            self.symbols[f"{module_path}.{symbol_name}"] = None
            return self._result(
                "fallback",
                err + " Confirm repository version contains this symbol.",
                module_path=module_path,
                symbol_name=symbol_name,
                error=str(e),
            )

    def _initialize_imports(self) -> None:
        target_modules = [
            "gmatch4py",
            "gmatch4py.embedding",
            "gmatch4py.ged",
            "gmatch4py.helpers",
            "gmatch4py.kernels",
            "setup",
        ]
        for module_path in target_modules:
            self._safe_import_module(module_path)

        # Discovered functions from analysis: setup.makeExtension, setup.scandir
        self._safe_get_symbol("setup", "makeExtension")
        self._safe_get_symbol("setup", "scandir")

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a basic health check for import-mode readiness.

        Returns:
            dict: Unified status payload including module availability and
                  discovered symbols.
        """
        module_status = {k: (v is not None) for k, v in self.modules.items()}
        symbol_status = {k: (v is not None) for k, v in self.symbols.items()}
        all_core_ok = module_status.get("setup", False) and symbol_status.get("setup.makeExtension", False)

        if all_core_ok:
            return self._result(
                "success",
                "Adapter is ready in import mode.",
                repository=self.repo_name,
                repository_url=self.repo_url,
                modules=module_status,
                symbols=symbol_status,
                dependencies=self.required_dependencies,
            )

        return self._result(
            "fallback",
            "Adapter initialized with partial imports. Install missing dependencies and verify source layout.",
            repository=self.repo_name,
            repository_url=self.repo_url,
            modules=module_status,
            symbols=symbol_status,
            dependencies=self.required_dependencies,
            last_error=self.last_error,
        )

    def list_available_symbols(self) -> Dict[str, Any]:
        """
        List currently loaded callable/class symbols discovered by the adapter.

        Returns:
            dict: Unified status payload with symbol metadata.
        """
        available = []
        for fq_name, sym in self.symbols.items():
            if sym is None:
                continue
            available.append(
                {
                    "name": fq_name,
                    "type": "class" if inspect.isclass(sym) else "function" if callable(sym) else type(sym).__name__,
                    "signature": str(inspect.signature(sym)) if callable(sym) else None,
                }
            )
        return self._result("success", "Collected available symbols.", symbols=available, count=len(available))

    # -------------------------------------------------------------------------
    # Function wrappers discovered from LLM analysis
    # -------------------------------------------------------------------------
    def call_setup_makeExtension(self, ext_name: str, file_path: str) -> Dict[str, Any]:
        """
        Call setup.makeExtension(ext_name, file_path).

        Parameters:
            ext_name (str): Extension name to build.
            file_path (str): File path used by setup logic.

        Returns:
            dict: Unified status payload containing function result.
        """
        fn = self.symbols.get("setup.makeExtension")
        if fn is None:
            return self._result(
                "fallback",
                "Function 'setup.makeExtension' is unavailable. Ensure 'source/setup.py' exists and imports cleanly.",
                function="setup.makeExtension",
            )
        try:
            result = fn(ext_name, file_path)
            return self._result(
                "success",
                "Function 'setup.makeExtension' executed successfully.",
                function="setup.makeExtension",
                inputs={"ext_name": ext_name, "file_path": file_path},
                result=result,
            )
        except Exception as e:
            return self._result(
                "error",
                "Execution failed for 'setup.makeExtension'. Validate parameters and repository compatibility.",
                function="setup.makeExtension",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    def call_setup_scandir(self, directory: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call setup.scandir(directory, files=None).

        Parameters:
            directory (str): Root directory to scan.
            files (list[str], optional): Pre-populated collector list.

        Returns:
            dict: Unified status payload containing function result.
        """
        fn = self.symbols.get("setup.scandir")
        if fn is None:
            return self._result(
                "fallback",
                "Function 'setup.scandir' is unavailable. Ensure 'source/setup.py' exists and imports cleanly.",
                function="setup.scandir",
            )
        try:
            if files is None:
                result = fn(directory)
                call_args = {"directory": directory}
            else:
                result = fn(directory, files)
                call_args = {"directory": directory, "files": files}
            return self._result(
                "success",
                "Function 'setup.scandir' executed successfully.",
                function="setup.scandir",
                inputs=call_args,
                result=result,
            )
        except Exception as e:
            return self._result(
                "error",
                "Execution failed for 'setup.scandir'. Verify directory path and access permissions.",
                function="setup.scandir",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Generic module-level helpers for extension and fallback usability
    # -------------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dynamic function caller.

        Parameters:
            module_path (str): Full module path (e.g., 'gmatch4py.kernels').
            function_name (str): Target function name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status payload with execution result.
        """
        if module_path not in self.modules or self.modules[module_path] is None:
            import_result = self._safe_import_module(module_path)
            if import_result["status"] not in ("success",):
                return import_result

        module = self.modules[module_path]
        try:
            fn = getattr(module, function_name)
        except Exception as e:
            return self._result(
                "fallback",
                f"Function '{function_name}' not found in module '{module_path}'. Check the repository API version.",
                module_path=module_path,
                function_name=function_name,
                error=str(e),
            )

        if not callable(fn):
            return self._result(
                "error",
                f"Symbol '{function_name}' in '{module_path}' is not callable.",
                module_path=module_path,
                function_name=function_name,
            )

        try:
            result = fn(*args, **kwargs)
            return self._result(
                "success",
                f"Function '{module_path}.{function_name}' executed successfully.",
                module_path=module_path,
                function_name=function_name,
                result=result,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Execution failed for '{module_path}.{function_name}'.",
                module_path=module_path,
                function_name=function_name,
                error=str(e),
                traceback=traceback.format_exc(),
            )

    def create_class_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dynamic class instantiation helper.

        Parameters:
            module_path (str): Full module path.
            class_name (str): Name of class to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        if module_path not in self.modules or self.modules[module_path] is None:
            import_result = self._safe_import_module(module_path)
            if import_result["status"] not in ("success",):
                return import_result

        module = self.modules[module_path]
        try:
            cls = getattr(module, class_name)
        except Exception as e:
            return self._result(
                "fallback",
                f"Class '{class_name}' not found in module '{module_path}'. Confirm API availability.",
                module_path=module_path,
                class_name=class_name,
                error=str(e),
            )

        if not inspect.isclass(cls):
            return self._result(
                "error",
                f"Symbol '{class_name}' in '{module_path}' is not a class.",
                module_path=module_path,
                class_name=class_name,
            )

        try:
            instance = cls(*args, **kwargs)
            return self._result(
                "success",
                f"Class '{module_path}.{class_name}' instantiated successfully.",
                module_path=module_path,
                class_name=class_name,
                instance=instance,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Failed to instantiate '{module_path}.{class_name}'. Check constructor arguments.",
                module_path=module_path,
                class_name=class_name,
                error=str(e),
                traceback=traceback.format_exc(),
            )