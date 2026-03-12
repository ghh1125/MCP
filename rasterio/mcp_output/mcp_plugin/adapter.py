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
    MCP Import Mode Adapter for rasterio repository.

    This adapter prefers direct Python imports from the local source checkout and
    falls back gracefully with actionable guidance when runtime-native dependencies
    (notably GDAL) are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        return self._result("ok", **kwargs)

    def _error(self, message: str, hint: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = {"message": message}
        if hint:
            payload["hint"] = hint
        payload.update(kwargs)
        return self._result("error", **payload)

    def _import_module(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        module_map = {
            "rasterio": "rasterio",
            "rio_main": "rasterio.rio.main",
            "rio_blocks": "rasterio.rio.blocks",
            "rio_bounds": "rasterio.rio.bounds",
            "rio_calc": "rasterio.rio.calc",
            "rio_clip": "rasterio.rio.clip",
            "rio_convert": "rasterio.rio.convert",
            "rio_create": "rasterio.rio.create",
            "rio_edit_info": "rasterio.rio.edit_info",
            "rio_env": "rasterio.rio.env",
            "rio_gcps": "rasterio.rio.gcps",
            "rio_info": "rasterio.rio.info",
            "rio_insp": "rasterio.rio.insp",
            "rio_mask": "rasterio.rio.mask",
            "rio_merge": "rasterio.rio.merge",
            "rio_overview": "rasterio.rio.overview",
            "rio_rasterize": "rasterio.rio.rasterize",
            "rio_rm": "rasterio.rio.rm",
            "rio_sample": "rasterio.rio.sample",
            "rio_shapes": "rasterio.rio.shapes",
            "rio_stack": "rasterio.rio.stack",
            "rio_transform": "rasterio.rio.transform",
            "rio_warp": "rasterio.rio.warp",
        }
        for key, module_path in module_map.items():
            self._import_module(key, module_path)

    def _get_module(self, key: str) -> Dict[str, Any]:
        mod = self._modules.get(key)
        if mod is None:
            err = self._import_errors.get(key, "Module not imported.")
            return self._error(
                message=f"Unable to import module '{key}'.",
                hint=(
                    "Ensure local source path is correct and GDAL/native dependencies "
                    "are installed and discoverable."
                ),
                details=err,
                mode=self.mode,
            )
        return self._ok(module=mod)

    def health(self) -> Dict[str, Any]:
        """
        Report adapter import health and fallback readiness.
        """
        return self._ok(
            mode=self.mode,
            loaded_modules=sorted(self._modules.keys()),
            import_errors=self._import_errors,
            guidance=(
                "If imports fail, install rasterio build/runtime dependencies, especially GDAL, "
                "and verify shared libraries are available to Python."
            ),
        )

    # -------------------------------------------------------------------------
    # Core rasterio module wrappers
    # -------------------------------------------------------------------------
    def call_rasterio_open(self, path: str, mode: str = "r", **kwargs: Any) -> Dict[str, Any]:
        """
        Open a raster dataset using rasterio.open.

        Parameters:
        - path: Path/URI to raster dataset.
        - mode: File mode (e.g., 'r', 'w').
        - kwargs: Additional options forwarded to rasterio.open.

        Returns:
        Unified status dictionary with dataset handle or error.
        """
        info = self._get_module("rasterio")
        if info["status"] != "ok":
            return info
        try:
            ds = info["module"].open(path, mode=mode, **kwargs)
            return self._ok(dataset=ds, mode=self.mode)
        except Exception as exc:
            return self._error(
                message="Failed to open dataset via rasterio.open.",
                hint="Verify file path, format support, permissions, and GDAL driver availability.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # CLI command module wrappers (import-mode callable interfaces)
    # -------------------------------------------------------------------------
    def _call_module_main(self, module_key: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        m = self._get_module(module_key)
        if m["status"] != "ok":
            return m
        mod = m["module"]
        if not hasattr(mod, "main"):
            return self._error(
                message=f"Module '{module_key}' does not expose a 'main' callable.",
                hint="Inspect module implementation for alternate callable names.",
            )
        try:
            result = mod.main(args=args) if args is not None else mod.main()
            return self._ok(result=result, mode=self.mode)
        except SystemExit as exc:
            return self._ok(result=None, exit_code=getattr(exc, "code", 0), mode=self.mode)
        except Exception as exc:
            return self._error(
                message=f"Execution failed for module '{module_key}'.",
                hint="Check command arguments and input dataset validity.",
                details=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def call_rio(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute primary rio CLI entrypoint from rasterio.rio.main."""
        return self._call_module_main("rio_main", args=args)

    def call_rio_blocks(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio blocks command module."""
        return self._call_module_main("rio_blocks", args=args)

    def call_rio_bounds(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio bounds command module."""
        return self._call_module_main("rio_bounds", args=args)

    def call_rio_calc(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio calc command module."""
        return self._call_module_main("rio_calc", args=args)

    def call_rio_clip(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio clip command module."""
        return self._call_module_main("rio_clip", args=args)

    def call_rio_convert(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio convert command module."""
        return self._call_module_main("rio_convert", args=args)

    def call_rio_create(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio create command module."""
        return self._call_module_main("rio_create", args=args)

    def call_rio_edit_info(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio edit-info command module."""
        return self._call_module_main("rio_edit_info", args=args)

    def call_rio_env(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio env command module."""
        return self._call_module_main("rio_env", args=args)

    def call_rio_gcps(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio gcps command module."""
        return self._call_module_main("rio_gcps", args=args)

    def call_rio_info(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio info command module."""
        return self._call_module_main("rio_info", args=args)

    def call_rio_insp(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio insp command module."""
        return self._call_module_main("rio_insp", args=args)

    def call_rio_mask(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio mask command module."""
        return self._call_module_main("rio_mask", args=args)

    def call_rio_merge(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio merge command module."""
        return self._call_module_main("rio_merge", args=args)

    def call_rio_overview(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio overview command module."""
        return self._call_module_main("rio_overview", args=args)

    def call_rio_rasterize(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio rasterize command module."""
        return self._call_module_main("rio_rasterize", args=args)

    def call_rio_rm(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio rm command module."""
        return self._call_module_main("rio_rm", args=args)

    def call_rio_sample(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio sample command module."""
        return self._call_module_main("rio_sample", args=args)

    def call_rio_shapes(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio shapes command module."""
        return self._call_module_main("rio_shapes", args=args)

    def call_rio_stack(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio stack command module."""
        return self._call_module_main("rio_stack", args=args)

    def call_rio_transform(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio transform command module."""
        return self._call_module_main("rio_transform", args=args)

    def call_rio_warp(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute rio warp command module."""
        return self._call_module_main("rio_warp", args=args)