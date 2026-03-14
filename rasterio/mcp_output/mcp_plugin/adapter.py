import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for Rasterio repository integration.

    This adapter prefers direct Python imports from local source code.
    If imports fail (commonly due to missing GDAL runtime/libs), methods
    return actionable fallback guidance while preserving a unified response format.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialized = False
        self._initialize_imports()

    def _ok(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "success", "message": message, "data": data or {}}

    def _fail(self, message: str, error: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "message": message, "data": data or {}}
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _fallback(self, action: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        guidance = (
            f"Import mode is unavailable for '{action}'. "
            "Ensure local source package is present and GDAL runtime/libs are installed and discoverable. "
            "Action: verify Python path, GDAL shared libraries, and compatible numpy build."
        )
        return self._fail(guidance, error=error, data={"mode": self.mode, "fallback": "cli_or_environment_fix"})

    def _safe_import(self, module_path: str) -> Tuple[bool, Optional[Any]]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return True, mod
        except Exception as e:
            self._import_errors[module_path] = f"{e}\n{traceback.format_exc()}"
            return False, None

    def _initialize_imports(self) -> None:
        """
        Load likely core Rasterio modules from repository source.
        Uses full package paths as required.
        """
        module_candidates = [
            "deployment.rasterio.source.rasterio",
            "deployment.rasterio.source.rasterio.io",
            "deployment.rasterio.source.rasterio.env",
            "deployment.rasterio.source.rasterio.features",
            "deployment.rasterio.source.rasterio.mask",
            "deployment.rasterio.source.rasterio.merge",
            "deployment.rasterio.source.rasterio.plot",
            "deployment.rasterio.source.rasterio.transform",
            "deployment.rasterio.source.rasterio.warp",
            "deployment.rasterio.source.rasterio.windows",
            "deployment.rasterio.source.rasterio.vrt",
            "deployment.rasterio.source.rasterio.session",
            "deployment.rasterio.source.rasterio.enums",
            "deployment.rasterio.source.rasterio.dtypes",
            "deployment.rasterio.source.rasterio.errors",
            "deployment.rasterio.source.rasterio.coords",
            "deployment.rasterio.source.rasterio.rpc",
            "deployment.rasterio.source.rasterio.sample",
            "deployment.rasterio.source.rasterio.fill",
            "deployment.rasterio.source.rasterio.stack",
            "deployment.rasterio.source.rasterio.tools",
            "deployment.rasterio.source.rasterio.profiles",
        ]
        for path in module_candidates:
            self._safe_import(path)

        self._initialized = True

    # -------------------------------------------------------------------------
    # Status / Diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and report import status.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        if not self._initialized:
            return self._fail("Adapter was not initialized properly.")
        return self._ok(
            "Adapter health check completed.",
            data={
                "mode": self.mode,
                "loaded_modules": sorted(list(self._modules.keys())),
                "import_error_count": len(self._import_errors),
                "import_errors": self._import_errors,
            },
        )

    # -------------------------------------------------------------------------
    # Core rasterio package wrappers
    # -------------------------------------------------------------------------
    def open_dataset(self, path: str, mode: str = "r", **kwargs: Any) -> Dict[str, Any]:
        """
        Open a raster dataset via rasterio.open.

        Parameters:
            path (str): Path or URI to raster dataset.
            mode (str): File mode, e.g., 'r', 'w', 'r+'.
            **kwargs: Extra open options forwarded to rasterio.open.

        Returns:
            dict: status, message, and dataset metadata preview.
        """
        try:
            mod = self._modules.get("deployment.rasterio.source.rasterio")
            if mod is None or not hasattr(mod, "open"):
                return self._fallback("open_dataset")
            with mod.open(path, mode=mode, **kwargs) as ds:
                meta = {
                    "name": getattr(ds, "name", None),
                    "driver": getattr(ds, "driver", None),
                    "width": getattr(ds, "width", None),
                    "height": getattr(ds, "height", None),
                    "count": getattr(ds, "count", None),
                    "crs": str(getattr(ds, "crs", None)),
                }
            return self._ok("Dataset opened successfully.", data=meta)
        except Exception as e:
            return self._fail("Failed to open dataset. Check path, permissions, driver support, and GDAL setup.", error=e)

    def show_versions(self) -> Dict[str, Any]:
        """
        Get Rasterio and environment version details.

        Returns:
            dict: status and version information text or structure.
        """
        try:
            mod = self._modules.get("deployment.rasterio.source.rasterio")
            if mod is None:
                return self._fallback("show_versions")
            show_versions_fn = getattr(mod, "show_versions", None)
            if callable(show_versions_fn):
                info = show_versions_fn()
                return self._ok("Version details retrieved.", data={"versions": info})
            return self._fail("show_versions is not available in imported module.")
        except Exception as e:
            return self._fail("Failed to retrieve version details.", error=e)

    # -------------------------------------------------------------------------
    # Functional module dispatcher (generic, rich fallback)
    # -------------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any function from an imported module.

        Parameters:
            module_path (str): Full module path, e.g., deployment.rasterio.source.rasterio.warp.
            function_name (str): Function to call from module.
            *args: Positional arguments for function.
            **kwargs: Keyword arguments for function.

        Returns:
            dict: Unified response with call result.
        """
        try:
            module = self._modules.get(module_path)
            if module is None:
                ok, module = self._safe_import(module_path)
                if not ok or module is None:
                    return self._fallback(f"call_module_function:{module_path}.{function_name}")
            fn = getattr(module, function_name, None)
            if not callable(fn):
                return self._fail(
                    f"Function '{function_name}' not found or not callable in module '{module_path}'.",
                    data={"module_path": module_path, "function_name": function_name},
                )
            result = fn(*args, **kwargs)
            return self._ok(
                f"Function '{function_name}' executed successfully.",
                data={"module_path": module_path, "function_name": function_name, "result": result},
            )
        except Exception as e:
            return self._fail(
                f"Function call failed for '{module_path}.{function_name}'. Validate parameters and runtime dependencies.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # Class factory / instantiation dispatcher
    # -------------------------------------------------------------------------
    def create_class_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically instantiate a class from an imported module.

        Parameters:
            module_path (str): Full module path.
            class_name (str): Class name to instantiate.
            *args: Positional args for constructor.
            **kwargs: Keyword args for constructor.

        Returns:
            dict: status and lightweight instance details.
        """
        try:
            module = self._modules.get(module_path)
            if module is None:
                ok, module = self._safe_import(module_path)
                if not ok or module is None:
                    return self._fallback(f"create_class_instance:{module_path}.{class_name}")
            cls = getattr(module, class_name, None)
            if cls is None:
                return self._fail(
                    f"Class '{class_name}' not found in module '{module_path}'.",
                    data={"module_path": module_path, "class_name": class_name},
                )
            instance = cls(*args, **kwargs)
            return self._ok(
                f"Instance of '{class_name}' created successfully.",
                data={
                    "module_path": module_path,
                    "class_name": class_name,
                    "instance_type": str(type(instance)),
                    "instance_repr": repr(instance),
                },
            )
        except Exception as e:
            return self._fail(
                f"Failed to instantiate '{module_path}.{class_name}'. Verify constructor arguments and dependencies.",
                error=e,
            )