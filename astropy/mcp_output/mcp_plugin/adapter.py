import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for Astropy repository integration.

    This adapter prioritizes direct module imports from the local `source` tree.
    If imports are unavailable, methods return actionable fallback guidance.
    All public methods return a unified dictionary:
        {
            "status": "success" | "error",
            "mode": "import" | "fallback",
            ...
        }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, **payload: Any) -> Dict[str, Any]:
        data = {"status": "success", "mode": self.mode}
        data.update(payload)
        return data

    def _err(self, message: str, **payload: Any) -> Dict[str, Any]:
        data = {"status": "error", "mode": self.mode, "error": message}
        data.update(payload)
        return data

    def _safe_import(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[key] = None
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        module_map = {
            "fitscheck": "astropy.io.fits.scripts.fitscheck",
            "fitsdiff": "astropy.io.fits.scripts.fitsdiff",
            "fitsheader": "astropy.io.fits.scripts.fitsheader",
            "fitsinfo": "astropy.io.fits.scripts.fitsinfo",
            "showtable": "astropy.table.scripts.showtable",
            "fits2bitmap": "astropy.visualization.scripts.fits2bitmap",
        }
        for key, path in module_map.items():
            self._safe_import(key, path)

        if any(self._modules.values()):
            self.mode = "import"
        else:
            self.mode = "fallback"

    def get_health(self) -> Dict[str, Any]:
        """
        Report adapter import health and loaded modules.

        Returns:
            dict: Unified status with currently available modules and import errors.
        """
        available = [k for k, v in self._modules.items() if v is not None]
        missing = [k for k, v in self._modules.items() if v is None]
        return self._ok(
            available_modules=available,
            missing_modules=missing,
            import_errors=self._import_errors,
            source_path=source_path,
        )

    # -------------------------------------------------------------------------
    # CLI module instance accessors
    # -------------------------------------------------------------------------
    def instance_fitscheck(self) -> Dict[str, Any]:
        """
        Get imported module instance for FITS checksum validator CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("fitscheck")
        if mod is None:
            return self._err(
                "Module astropy.io.fits.scripts.fitscheck is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.io.fits.scripts.fitscheck")

    def instance_fitsdiff(self) -> Dict[str, Any]:
        """
        Get imported module instance for FITS diff CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("fitsdiff")
        if mod is None:
            return self._err(
                "Module astropy.io.fits.scripts.fitsdiff is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.io.fits.scripts.fitsdiff")

    def instance_fitsheader(self) -> Dict[str, Any]:
        """
        Get imported module instance for FITS header inspection CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("fitsheader")
        if mod is None:
            return self._err(
                "Module astropy.io.fits.scripts.fitsheader is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.io.fits.scripts.fitsheader")

    def instance_fitsinfo(self) -> Dict[str, Any]:
        """
        Get imported module instance for FITS structure summary CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("fitsinfo")
        if mod is None:
            return self._err(
                "Module astropy.io.fits.scripts.fitsinfo is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.io.fits.scripts.fitsinfo")

    def instance_showtable(self) -> Dict[str, Any]:
        """
        Get imported module instance for table display CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("showtable")
        if mod is None:
            return self._err(
                "Module astropy.table.scripts.showtable is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.table.scripts.showtable")

    def instance_fits2bitmap(self) -> Dict[str, Any]:
        """
        Get imported module instance for FITS to bitmap conversion CLI.

        Returns:
            dict: Contains module instance when available.
        """
        mod = self._modules.get("fits2bitmap")
        if mod is None:
            return self._err(
                "Module astropy.visualization.scripts.fits2bitmap is unavailable. Ensure repository source exists and dependencies are installed."
            )
        return self._ok(module=mod, module_name="astropy.visualization.scripts.fits2bitmap")

    # -------------------------------------------------------------------------
    # CLI function invokers
    # -------------------------------------------------------------------------
    def _invoke_main(self, key: str, args: Optional[list] = None) -> Dict[str, Any]:
        mod = self._modules.get(key)
        if mod is None:
            return self._err(
                f"Module for '{key}' is not available in import mode. Verify source checkout and Python dependencies."
            )

        args = args or []
        main_fn = getattr(mod, "main", None)
        if not callable(main_fn):
            return self._err(
                f"The module '{mod.__name__}' does not expose a callable main(). Use module instance and call supported APIs directly."
            )
        try:
            result = main_fn(args)
            return self._ok(command=key, args=args, result=result)
        except SystemExit as exc:
            return self._ok(
                command=key,
                args=args,
                result=None,
                note=f"Command exited via SystemExit with code: {exc.code}",
            )
        except Exception as exc:
            return self._err(
                f"Execution failed for '{key}'. Review arguments and file paths.",
                command=key,
                args=args,
                exception=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def call_fitscheck(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute FITS validation/checksum command.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("fitscheck", args)

    def call_fitsdiff(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute FITS file difference command.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("fitsdiff", args)

    def call_fitsheader(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute FITS header display command.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("fitsheader", args)

    def call_fitsinfo(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute FITS structure summary command.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("fitsinfo", args)

    def call_showtable(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute table display command for supported file formats.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("showtable", args)

    def call_fits2bitmap(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute FITS-to-bitmap conversion command.

        Args:
            args (list, optional): Command-line style arguments.

        Returns:
            dict: Unified status with execution result or actionable error.
        """
        return self._invoke_main("fits2bitmap", args)

    # -------------------------------------------------------------------------
    # Fallback guidance
    # -------------------------------------------------------------------------
    def get_fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide friendly, actionable guidance when import mode is partially or fully unavailable.

        Returns:
            dict: Guidance text and missing module diagnostics.
        """
        missing = [k for k, v in self._modules.items() if v is None]
        if not missing:
            return self._ok(message="Import mode is fully operational; fallback guidance is not required.")
        return self._err(
            "Some modules are unavailable in import mode.",
            guidance=[
                "Confirm the repository source is located at the expected 'source' directory.",
                "Install required dependencies: numpy, pyerfa, packaging, PyYAML.",
                "For extended functionality, install optional dependencies such as scipy, matplotlib, pandas, pyarrow, h5py, fsspec, dask, beautifulsoup4, and lxml.",
                "Validate that your runtime uses the same interpreter where dependencies are installed.",
            ],
            missing_modules=missing,
            import_errors=self._import_errors,
        )