import os
import sys
import traceback
import inspect
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for Rasterio repository integration.

    This adapter attempts to import and call actual implementations from:
    - rasterio.__init__: open, band, pad
    - rasterio.io: open
    - rasterio.rio.main: CLI entry fallback support (rio)

    Design goals:
    - Unified return format with status field.
    - Graceful fallback when import-mode execution is unavailable.
    - Clear, actionable English error messages.
    """

    # =========================================================================
    # Initialization and Module Management
    # =========================================================================

    def __init__(self) -> None:
        """
        Initialize adapter in import mode and load target modules/functions.

        Attributes:
            mode (str): Execution mode, fixed to "import".
            _imports (dict): Imported modules/functions registry.
            _import_errors (dict): Import errors with actionable diagnostics.
        """
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_imports()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error is not None:
            payload["error"] = str(error)
            payload["error_type"] = error.__class__.__name__
        if hint:
            payload["hint"] = hint
        return payload

    def _load_imports(self) -> None:
        """
        Import required modules and functions from repository source code.

        Uses full package paths discovered in analysis:
        - rasterio.__init__
        - rasterio.io
        - rasterio.rio.main

        Any failure is recorded and exposed via health/status methods.
        """
        import_targets = {
            "rasterio_module": "rasterio",
            "rasterio_io_module": "rasterio.io",
            "rasterio_rio_main_module": "rasterio.rio.main",
        }

        for key, module_name in import_targets.items():
            try:
                self._imports[key] = __import__(module_name, fromlist=["*"])
            except Exception as exc:
                self._import_errors[key] = (
                    f"Failed to import '{module_name}'. Ensure native GDAL runtime is available, "
                    f"repository source path is correct, and compiled rasterio extensions are compatible. Details: {exc}"
                )

        self._bind_callable("rasterio_open", "rasterio_module", "open")
        self._bind_callable("rasterio_band", "rasterio_module", "band")
        self._bind_callable("rasterio_pad", "rasterio_module", "pad")
        self._bind_callable("rasterio_io_open", "rasterio_io_module", "open")
        self._bind_callable("rio_main", "rasterio_rio_main_module", "main")

    def _bind_callable(self, target_key: str, module_key: str, attr_name: str) -> None:
        """
        Bind callable from an imported module to internal registry.

        Args:
            target_key: Internal key name for callable.
            module_key: Key of module in _imports.
            attr_name: Attribute/callable name on module.
        """
        if module_key not in self._imports:
            self._import_errors[target_key] = (
                f"Cannot bind '{attr_name}' because module key '{module_key}' is unavailable."
            )
            return
        try:
            obj = getattr(self._imports[module_key], attr_name)
            self._imports[target_key] = obj
        except Exception as exc:
            self._import_errors[target_key] = (
                f"Failed to resolve '{attr_name}' from module '{module_key}'. Details: {exc}"
            )

    # =========================================================================
    # Adapter Diagnostics
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter health and import availability diagnostics.

        Returns:
            dict:
                {
                  "status": "success" | "error",
                  "mode": "import",
                  "message": str,
                  "available": {...},
                  "import_errors": {...}
                }
        """
        available = {
            "rasterio.open": "rasterio_open" in self._imports,
            "rasterio.band": "rasterio_band" in self._imports,
            "rasterio.pad": "rasterio_pad" in self._imports,
            "rasterio.io.open": "rasterio_io_open" in self._imports,
            "rasterio.rio.main.main": "rio_main" in self._imports,
        }
        if self._import_errors:
            return self._fail(
                message="Adapter initialized with partial import failures.",
                hint="Install/align GDAL and rasterio compiled extensions, then re-run.",
                error=RuntimeError("Some imports failed"),
            ) | {"available": available, "import_errors": self._import_errors}
        return self._ok(
            data={"available": available, "import_errors": {}},
            message="All target imports are available.",
        )

    # =========================================================================
    # Function Wrappers: rasterio.__init__
    # =========================================================================

    def call_rasterio_open(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call rasterio.open from rasterio.__init__.

        Parameters:
            *args: Positional arguments forwarded to rasterio.open (e.g., path, mode).
            **kwargs: Keyword arguments forwarded to rasterio.open.

        Returns:
            dict:
                status, message, and result metadata.
                The returned dataset object is included as `result` for chaining by MCP runtime.
        """
        fn = self._imports.get("rasterio_open")
        if fn is None:
            return self._fail(
                "Function 'rasterio.open' is unavailable in import mode.",
                hint="Verify source import path and GDAL/rasterio binary compatibility.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "function": "rasterio.open",
                    "result": result,
                    "result_type": type(result).__name__,
                },
                message="rasterio.open executed successfully.",
            )
        except Exception as exc:
            return self._fail(
                "Failed to execute 'rasterio.open'.",
                error=exc,
                hint="Check input path, mode, driver options, and dataset accessibility.",
            )

    def call_rasterio_band(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call rasterio.band from rasterio.__init__.

        Parameters:
            *args: Positional arguments forwarded to rasterio.band.
            **kwargs: Keyword arguments forwarded to rasterio.band.

        Returns:
            dict with unified status and call result.
        """
        fn = self._imports.get("rasterio_band")
        if fn is None:
            return self._fail(
                "Function 'rasterio.band' is unavailable in import mode.",
                hint="Ensure rasterio package imports correctly from repository source.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "function": "rasterio.band",
                    "result": result,
                    "result_type": type(result).__name__,
                },
                message="rasterio.band executed successfully.",
            )
        except Exception as exc:
            return self._fail(
                "Failed to execute 'rasterio.band'.",
                error=exc,
                hint="Pass a valid dataset object and a valid band index.",
            )

    def call_rasterio_pad(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call rasterio.pad from rasterio.__init__.

        Parameters:
            *args: Positional arguments forwarded to rasterio.pad.
            **kwargs: Keyword arguments forwarded to rasterio.pad.

        Returns:
            dict with unified status and call result.
        """
        fn = self._imports.get("rasterio_pad")
        if fn is None:
            return self._fail(
                "Function 'rasterio.pad' is unavailable in import mode.",
                hint="Confirm repository rasterio APIs are importable and complete.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "function": "rasterio.pad",
                    "result": result,
                    "result_type": type(result).__name__,
                },
                message="rasterio.pad executed successfully.",
            )
        except Exception as exc:
            return self._fail(
                "Failed to execute 'rasterio.pad'.",
                error=exc,
                hint="Validate array/window arguments and numeric padding configuration.",
            )

    # =========================================================================
    # Function Wrappers: rasterio.io
    # =========================================================================

    def call_rasterio_io_open(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call rasterio.io.open from rasterio.io module.

        Parameters:
            *args: Positional arguments for rasterio.io.open.
            **kwargs: Keyword arguments for rasterio.io.open.

        Returns:
            dict with unified status and call result.
        """
        fn = self._imports.get("rasterio_io_open")
        if fn is None:
            return self._fail(
                "Function 'rasterio.io.open' is unavailable in import mode.",
                hint="Check whether rasterio.io module imports without binary dependency errors.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "function": "rasterio.io.open",
                    "result": result,
                    "result_type": type(result).__name__,
                },
                message="rasterio.io.open executed successfully.",
            )
        except Exception as exc:
            return self._fail(
                "Failed to execute 'rasterio.io.open'.",
                error=exc,
                hint="Verify dataset URI/path, mode, and GDAL environment configuration.",
            )

    # =========================================================================
    # CLI Fallback Support (rio)
    # =========================================================================

    def call_rio_main(self, args: Optional[list] = None, standalone_mode: bool = False) -> Dict[str, Any]:
        """
        Invoke rasterio.rio.main.main as a fallback CLI pathway.

        Parameters:
            args: List of CLI-like arguments (e.g., ['info', 'file.tif']).
            standalone_mode: Forwarded to click command execution; False recommended for integration.

        Returns:
            dict with execution status and return value.
        """
        fn = self._imports.get("rio_main")
        if fn is None:
            return self._fail(
                "CLI fallback 'rasterio.rio.main.main' is unavailable.",
                hint="Ensure rasterio.rio modules are importable and click dependencies are installed.",
            )
        try:
            result = fn(args=args or [], standalone_mode=standalone_mode)
            return self._ok(
                data={
                    "function": "rasterio.rio.main.main",
                    "args": args or [],
                    "result": result,
                    "result_type": type(result).__name__,
                },
                message="rio main executed successfully.",
            )
        except SystemExit as exc:
            code = getattr(exc, "code", 1)
            if code == 0:
                return self._ok(
                    data={"function": "rasterio.rio.main.main", "exit_code": code},
                    message="rio command completed successfully.",
                )
            return self._fail(
                f"rio command exited with non-zero status: {code}.",
                error=exc,
                hint="Review CLI arguments and dataset paths.",
            )
        except Exception as exc:
            return self._fail(
                "Failed to execute rio CLI fallback.",
                error=exc,
                hint="Check command arguments and runtime dependencies (click, GDAL, rasterio extensions).",
            )

    # =========================================================================
    # Utility: Introspection and Safe Dispatch
    # =========================================================================

    def list_capabilities(self) -> Dict[str, Any]:
        """
        List exposed adapter methods and callable availability.

        Returns:
            dict with available call methods and import diagnostics.
        """
        call_methods = [name for name in dir(self) if name.startswith("call_") and callable(getattr(self, name))]
        return self._ok(
            data={
                "mode": self.mode,
                "call_methods": sorted(call_methods),
                "import_errors": self._import_errors,
            },
            message="Capabilities collected.",
        )

    def dispatch(self, method: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically dispatch adapter call methods by name.

        Parameters:
            method: Method name to call, e.g., 'call_rasterio_open'.
            *args/**kwargs: Arguments passed to target method.

        Returns:
            Unified status dictionary.
        """
        try:
            target = getattr(self, method, None)
            if target is None or not callable(target):
                return self._fail(
                    f"Unknown method '{method}'.",
                    hint="Use list_capabilities() to view supported method names.",
                )
            return target(*args, **kwargs)
        except Exception as exc:
            return self._fail(
                f"Dispatch failed for method '{method}'.",
                error=exc,
                hint="Check method name and parameter types.",
            )