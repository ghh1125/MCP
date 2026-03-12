import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the xarray repository.

    This adapter prioritizes direct module import/use from the local `source` tree and
    provides safe fallbacks when optional dependencies or runtime conditions prevent
    successful execution.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "ok", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, hint: Optional[str] = None, exc: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if exc is not None:
            payload["details"] = f"{type(exc).__name__}: {exc}"
        return payload

    def _initialize_imports(self) -> None:
        try:
            import importlib

            self._modules["xarray"] = importlib.import_module("xarray")
            self._modules["print_versions"] = importlib.import_module("xarray.util.print_versions")
            self._modules["plugins"] = importlib.import_module("xarray.backends.plugins")
            self._modules["tutorial"] = importlib.import_module("xarray.tutorial")
        except Exception as exc:
            self._import_error = f"{type(exc).__name__}: {exc}"

    def _require(self, key: str) -> Any:
        mod = self._modules.get(key)
        if mod is None:
            raise ImportError(
                f"Required module '{key}' is not available. "
                f"Import initialization failed: {self._import_error or 'unknown reason'}"
            )
        return mod

    # -------------------------------------------------------------------------
    # Status and capability
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import readiness.

        Returns:
            Dict[str, Any]: Unified status payload with import diagnostics.
        """
        if self._import_error:
            return self._error(
                "Adapter import initialization is incomplete.",
                hint="Verify local source path and optional dependencies, then retry.",
            )
        return self._ok(
            {
                "imported_modules": sorted(self._modules.keys()),
                "source_path": source_path,
            },
            message="Adapter is ready.",
        )

    # -------------------------------------------------------------------------
    # Core xarray function wrappers
    # -------------------------------------------------------------------------
    def call_open_dataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.open_dataset with pass-through arguments.

        Parameters:
            *args: Positional args accepted by xarray.open_dataset.
            **kwargs: Keyword args accepted by xarray.open_dataset.

        Returns:
            Dict[str, Any]: status + dataset (on success) or actionable error.
        """
        try:
            xr = self._require("xarray")
            ds = xr.open_dataset(*args, **kwargs)
            return self._ok({"result": ds}, message="open_dataset executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.open_dataset.",
                hint="Check file path/engine and install optional backend dependencies (netCDF4/h5netcdf/scipy/zarr).",
                exc=exc,
            )

    def call_open_dataarray(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.open_dataarray with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            da = xr.open_dataarray(*args, **kwargs)
            return self._ok({"result": da}, message="open_dataarray executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.open_dataarray.",
                hint="Check input path/engine and backend availability.",
                exc=exc,
            )

    def call_open_mfdataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.open_mfdataset with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            ds = xr.open_mfdataset(*args, **kwargs)
            return self._ok({"result": ds}, message="open_mfdataset executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.open_mfdataset.",
                hint="Ensure dask is installed and file patterns/backend settings are valid.",
                exc=exc,
            )

    def call_load_dataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.load_dataset with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            ds = xr.load_dataset(*args, **kwargs)
            return self._ok({"result": ds}, message="load_dataset executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.load_dataset.",
                hint="Confirm file format/backend compatibility.",
                exc=exc,
            )

    def call_load_dataarray(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.load_dataarray with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            da = xr.load_dataarray(*args, **kwargs)
            return self._ok({"result": da}, message="load_dataarray executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.load_dataarray.",
                hint="Confirm source path and backend dependencies.",
                exc=exc,
            )

    def call_decode_cf(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.decode_cf with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.decode_cf(*args, **kwargs)
            return self._ok({"result": out}, message="decode_cf executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.decode_cf.",
                hint="Validate CF metadata and time decoding dependencies.",
                exc=exc,
            )

    def call_align(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.align with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.align(*args, **kwargs)
            return self._ok({"result": out}, message="align executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.align.",
                hint="Check object dimensions, indexes, and join strategy.",
                exc=exc,
            )

    def call_merge(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.merge with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.merge(*args, **kwargs)
            return self._ok({"result": out}, message="merge executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.merge.",
                hint="Inspect variable conflicts and compatibility options.",
                exc=exc,
            )

    def call_combine_by_coords(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.combine_by_coords with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.combine_by_coords(*args, **kwargs)
            return self._ok({"result": out}, message="combine_by_coords executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.combine_by_coords.",
                hint="Ensure coordinate variables are consistent across inputs.",
                exc=exc,
            )

    def call_combine_nested(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.combine_nested with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.combine_nested(*args, **kwargs)
            return self._ok({"result": out}, message="combine_nested executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.combine_nested.",
                hint="Validate nested structure and concat dimensions.",
                exc=exc,
            )

    def call_concat(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.concat with pass-through arguments.
        """
        try:
            xr = self._require("xarray")
            out = xr.concat(*args, **kwargs)
            return self._ok({"result": out}, message="concat executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.concat.",
                hint="Check concat dimension and object compatibility.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Backend plugin and diagnostics wrappers
    # -------------------------------------------------------------------------
    def call_list_engines(self) -> Dict[str, Any]:
        """
        List available xarray backends/engines.
        """
        try:
            plugins = self._require("plugins")
            engines = plugins.list_engines()
            return self._ok({"result": engines}, message="Engine list retrieved.")
        except Exception as exc:
            return self._error(
                "Failed to list xarray engines.",
                hint="Install optional backend libraries and verify import environment.",
                exc=exc,
            )

    def call_print_versions(self, as_json: bool = False) -> Dict[str, Any]:
        """
        Execute xarray.util.print_versions diagnostics.

        Parameters:
            as_json (bool): If True, request JSON-like output when supported.

        Returns:
            Dict[str, Any]: status + diagnostics execution result.
        """
        try:
            pv = self._require("print_versions")
            if hasattr(pv, "show_versions"):
                result = pv.show_versions(as_json=as_json)
            elif hasattr(pv, "main"):
                result = pv.main()
            else:
                return self._error(
                    "print_versions module does not expose an expected callable.",
                    hint="Use module execution: python -m xarray.util.print_versions",
                )
            return self._ok({"result": result}, message="Version diagnostics executed.")
        except Exception as exc:
            return self._error(
                "Failed to run version diagnostics.",
                hint="Run `python -m xarray.util.print_versions` directly for more context.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Tutorial/data helper wrappers
    # -------------------------------------------------------------------------
    def call_tutorial_open_dataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.tutorial.open_dataset for sample datasets.
        """
        try:
            tutorial = self._require("tutorial")
            out = tutorial.open_dataset(*args, **kwargs)
            return self._ok({"result": out}, message="tutorial.open_dataset executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.tutorial.open_dataset.",
                hint="Check network access and dataset name; tutorial datasets may require remote fetch.",
                exc=exc,
            )

    def call_tutorial_load_dataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call xarray.tutorial.load_dataset for eagerly loaded sample datasets.
        """
        try:
            tutorial = self._require("tutorial")
            out = tutorial.load_dataset(*args, **kwargs)
            return self._ok({"result": out}, message="tutorial.load_dataset executed.")
        except Exception as exc:
            return self._error(
                "Failed to execute xarray.tutorial.load_dataset.",
                hint="Check dataset availability and local cache permissions.",
                exc=exc,
            )