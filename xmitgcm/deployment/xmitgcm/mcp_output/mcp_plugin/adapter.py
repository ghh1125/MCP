import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the xmitgcm repository.

    This adapter tries to import project modules directly from the local `source` directory.
    If import fails, it falls back to a non-intrusive "blackbox" mode and returns actionable
    guidance in English.

    Unified return schema for all public methods:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "blackbox",
        "data": Any,                 # optional
        "message": str,              # optional
        "error": str,                # optional
        "guidance": str,             # optional
        "details": dict              # optional
    }
    """

    # ---------------------------------------------------------------------
    # Lifecycle and module management
    # ---------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._load_errors: Dict[str, str] = {}
        self._module_names: List[str] = [
            "xmitgcm",
            "xmitgcm.file_utils",
            "xmitgcm.utils",
            "xmitgcm.variables",
            "xmitgcm.mds_store",
            "xmitgcm.default_diagnostics",
            "xmitgcm.llcreader",
            "xmitgcm.llcreader.duck_array_ops",
            "xmitgcm.llcreader.known_models",
            "xmitgcm.llcreader.llcmodel",
            "xmitgcm.llcreader.llcutils",
            "xmitgcm.llcreader.shrunk_index",
            "xmitgcm.llcreader.stores",
            "xmitgcm.test",
            "xmitgcm.test.test_file_utils",
            "xmitgcm.test.test_llcreader",
            "xmitgcm.test.test_mds_store",
            "xmitgcm.test.test_utils",
            "xmitgcm.test.test_xmitgcm_common",
        ]
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        for name in self._module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as exc:
                self._load_errors[name] = str(exc)

        if self._load_errors:
            self.mode = "blackbox"

    def _response(
        self,
        status: str,
        data: Any = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": status, "mode": self.mode}
        if data is not None:
            payload["data"] = data
        if message:
            payload["message"] = message
        if error:
            payload["error"] = error
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status dictionary with loaded modules and any failures.
        """
        if self.mode == "import":
            return self._response(
                "success",
                data={
                    "loaded_modules": sorted(list(self._modules.keys())),
                    "failed_modules": self._load_errors,
                },
                message="Adapter is ready in import mode.",
            )
        return self._response(
            "fallback",
            data={"failed_modules": self._load_errors},
            message="Adapter is running in fallback mode.",
            guidance=(
                "Ensure all required dependencies are installed: numpy, xarray, dask, cachetools. "
                "Optional features may need zarr, fsspec, netCDF4, scipy."
            ),
        )

    # ---------------------------------------------------------------------
    # Generic introspection and invocation helpers
    # ---------------------------------------------------------------------

    def list_modules(self) -> Dict[str, Any]:
        """
        List target repository modules configured by this adapter.

        Returns:
            dict: Unified response with configured, loaded, and failed modules.
        """
        return self._response(
            "success",
            data={
                "configured": self._module_names,
                "loaded": sorted(list(self._modules.keys())),
                "failed": self._load_errors,
            },
        )

    def list_module_members(self, module_path: str, include_private: bool = False) -> Dict[str, Any]:
        """
        List module members (functions, classes, constants) using reflection.

        Args:
            module_path (str): Full module path, e.g., 'xmitgcm.utils'.
            include_private (bool): Include names starting with underscore.

        Returns:
            dict: Unified status dictionary with members grouped by type.
        """
        try:
            module = self._modules.get(module_path)
            if module is None:
                if self.mode == "blackbox":
                    return self._response(
                        "fallback",
                        error=f"Module '{module_path}' is not available in fallback mode.",
                        guidance="Run health_check() and resolve import errors before introspection.",
                    )
                module = importlib.import_module(module_path)
                self._modules[module_path] = module

            members = inspect.getmembers(module)
            classes, functions, constants = [], [], []
            for name, obj in members:
                if not include_private and name.startswith("_"):
                    continue
                if inspect.isclass(obj):
                    classes.append(name)
                elif inspect.isfunction(obj) or inspect.ismethod(obj) or inspect.isbuiltin(obj):
                    functions.append(name)
                else:
                    constants.append(name)

            return self._response(
                "success",
                data={
                    "module": module_path,
                    "classes": sorted(classes),
                    "functions": sorted(functions),
                    "constants": sorted(constants),
                },
            )
        except Exception as exc:
            return self._response(
                "error",
                error=str(exc),
                guidance="Verify module path and dependency availability.",
            )

    def instantiate_class(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an instance of a class from a repository module.

        Args:
            module_path (str): Full module path, e.g., 'xmitgcm.llcreader.llcmodel'.
            class_name (str): Class name in target module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified response containing created instance in `data.instance`.
        """
        if self.mode == "blackbox":
            return self._response(
                "fallback",
                error="Cannot instantiate classes in fallback mode.",
                guidance="Resolve import errors and dependencies, then retry.",
            )
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._response(
                "success",
                data={
                    "module": module_path,
                    "class_name": class_name,
                    "instance": instance,
                },
            )
        except AttributeError:
            return self._response(
                "error",
                error=f"Class '{class_name}' not found in module '{module_path}'.",
                guidance="Use list_module_members() to confirm class names.",
            )
        except Exception as exc:
            return self._response(
                "error",
                error=str(exc),
                guidance="Check constructor arguments and required dependencies.",
            )

    def call_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from a repository module.

        Args:
            module_path (str): Full module path, e.g., 'xmitgcm.file_utils'.
            function_name (str): Function name in target module.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Unified response with function result.
        """
        if self.mode == "blackbox":
            return self._response(
                "fallback",
                error="Cannot execute repository functions in fallback mode.",
                guidance="Resolve import issues and run health_check() before calling functions.",
            )
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            func = getattr(module, function_name)
            result = func(*args, **kwargs)
            return self._response(
                "success",
                data={
                    "module": module_path,
                    "function_name": function_name,
                    "result": result,
                },
            )
        except AttributeError:
            return self._response(
                "error",
                error=f"Function '{function_name}' not found in module '{module_path}'.",
                guidance="Use list_module_members() to inspect available functions.",
            )
        except Exception as exc:
            return self._response(
                "error",
                error=str(exc),
                guidance="Validate function arguments and environment dependencies.",
            )

    # ---------------------------------------------------------------------
    # Dedicated instance methods for key classes (dynamic wrappers)
    # ---------------------------------------------------------------------

    def instance_mds_store(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.instantiate_class("xmitgcm.mds_store", "MDSDataStore", *args, **kwargs)

    def instance_llc_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.instantiate_class("xmitgcm.llcreader.llcmodel", "LLCModel", *args, **kwargs)

    def instance_base_store(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.instantiate_class("xmitgcm.llcreader.stores", "BaseStore", *args, **kwargs)

    # ---------------------------------------------------------------------
    # Dedicated call methods for core entry functions
    # ---------------------------------------------------------------------

    def call_open_mdsdataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xmitgcm.open_mdsdataset(...)

        Typical use:
            call_open_mdsdataset(data_dir, iters=[...], prefix=[...], ...)
        """
        return self.call_function("xmitgcm", "open_mdsdataset", *args, **kwargs)

    def call_open_mdsdataset_from_store(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xmitgcm.mds_store.open_mdsdataset(...)

        This wrapper targets the implementation in mds_store module.
        """
        return self.call_function("xmitgcm.mds_store", "open_mdsdataset", *args, **kwargs)

    def call_any(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Convenience alias to call any function by module path and function name.

        Args:
            module_path (str): Full import path under xmitgcm.
            function_name (str): Function to invoke.
        """
        return self.call_function(module_path, function_name, *args, **kwargs)

    # ---------------------------------------------------------------------
    # Fallback guidance utilities
    # ---------------------------------------------------------------------

    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide concise, actionable guidance when imports fail.

        Returns:
            dict: Unified status with dependency and environment hints.
        """
        return self._response(
            "fallback" if self.mode == "blackbox" else "success",
            data={
                "required_dependencies": ["numpy", "xarray", "dask", "cachetools"],
                "optional_dependencies": ["zarr", "fsspec", "netCDF4", "scipy"],
                "failed_imports": self._load_errors,
            },
            message=(
                "Install required dependencies and verify local source path resolution."
                if self.mode == "blackbox"
                else "Adapter is already in import mode."
            ),
            guidance=(
                "Use a clean virtual environment and install dependencies from pyproject.toml. "
                "Then reinitialize the Adapter."
            ),
        )