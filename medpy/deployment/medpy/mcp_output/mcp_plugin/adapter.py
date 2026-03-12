import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the medpy repository.

    This adapter prioritizes direct Python imports from the local `source` tree and
    gracefully falls back to a CLI-guidance mode when imports or runtime calls fail.
    All public methods return a unified dictionary format with at least:
      - status: "success" | "error" | "fallback"
      - mode: "import" | "cli"
      - data / error / guidance fields where relevant
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._imports: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": status, "mode": self.mode}
        if data is not None:
            payload["data"] = data
        if error is not None:
            payload["error"] = error
        if guidance is not None:
            payload["guidance"] = guidance
        if details is not None:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        targets = {
            "setup": "setup",
            "bin.medpy_reslice_3d_to_4d": "bin.medpy_reslice_3d_to_4d",
            "bin.medpy_extract_min_max": "bin.medpy_extract_min_max",
            "bin.medpy_convert": "bin.medpy_convert",
        }
        for key, path in targets.items():
            try:
                self._modules[key] = importlib.import_module(path)
            except Exception as exc:
                self._import_errors[key] = f"{type(exc).__name__}: {exc}"

        self._bind_imports()
        if self._import_errors:
            self.mode = "cli"

    def _bind_imports(self) -> None:
        # setup.py symbols
        setup_mod = self._modules.get("setup")
        if setup_mod is not None:
            for symbol in ["read", "run_setup", "try_find_library", "BuildFailed", "ve_build_ext"]:
                if hasattr(setup_mod, symbol):
                    self._imports[f"setup.{symbol}"] = getattr(setup_mod, symbol)

        # bin/medpy_reslice_3d_to_4d.py symbols
        r_mod = self._modules.get("bin.medpy_reslice_3d_to_4d")
        if r_mod is not None:
            for symbol in ["getArguments", "getParser", "main"]:
                if hasattr(r_mod, symbol):
                    self._imports[f"bin.medpy_reslice_3d_to_4d.{symbol}"] = getattr(r_mod, symbol)

        # bin/medpy_extract_min_max.py symbols
        emm = self._modules.get("bin.medpy_extract_min_max")
        if emm is not None:
            for symbol in ["getArguments", "getParser", "main"]:
                if hasattr(emm, symbol):
                    self._imports[f"bin.medpy_extract_min_max.{symbol}"] = getattr(emm, symbol)

        # bin/medpy_convert.py symbols
        c_mod = self._modules.get("bin.medpy_convert")
        if c_mod is not None and hasattr(c_mod, "getArguments"):
            self._imports["bin.medpy_convert.getArguments"] = getattr(c_mod, "getArguments")

    def health(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import status.

        Returns:
            Dict with status, mode, imported modules, available symbols, and import errors.
        """
        return self._result(
            status="success" if not self._import_errors else "fallback",
            data={
                "imported_modules": sorted(self._modules.keys()),
                "available_symbols": sorted(self._imports.keys()),
                "import_errors": self._import_errors,
            },
            guidance=(
                "Import mode fully available."
                if not self._import_errors
                else "Some imports failed. Use CLI commands as fallback."
            ),
        )

    # -------------------------------------------------------------------------
    # Utility execution wrappers
    # -------------------------------------------------------------------------

    def _call(self, key: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func = self._imports.get(key)
        if func is None:
            return self._result(
                status="fallback",
                error=f"Function '{key}' is not available in import mode.",
                guidance="Verify source checkout and dependencies, or run the corresponding CLI command.",
                details={"import_errors": self._import_errors},
            )
        try:
            value = func(*args, **kwargs)
            return self._result(status="success", data={"result": value, "callable": key})
        except Exception as exc:
            return self._result(
                status="error",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check input arguments and required runtime dependencies (e.g., numpy/scipy).",
                details={"traceback": traceback.format_exc(), "callable": key},
            )

    # -------------------------------------------------------------------------
    # setup.py classes and functions
    # -------------------------------------------------------------------------

    def create_build_failed(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of setup.BuildFailed.

        Parameters:
            *args, **kwargs: Forwarded to BuildFailed constructor.

        Returns:
            Unified status dictionary with the created instance in data.result.
        """
        cls = self._imports.get("setup.BuildFailed")
        if cls is None:
            return self._result(
                status="fallback",
                error="Class 'setup.BuildFailed' is not available.",
                guidance="Ensure setup.py can be imported from source.",
                details={"import_errors": self._import_errors},
            )
        try:
            obj = cls(*args, **kwargs)
            return self._result(status="success", data={"result": obj, "class": "setup.BuildFailed"})
        except Exception as exc:
            return self._result(
                status="error",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Review constructor arguments for BuildFailed.",
                details={"traceback": traceback.format_exc()},
            )

    def create_ve_build_ext(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of setup.ve_build_ext.

        Parameters:
            *args, **kwargs: Forwarded to ve_build_ext constructor.

        Returns:
            Unified status dictionary with the created instance in data.result.
        """
        cls = self._imports.get("setup.ve_build_ext")
        if cls is None:
            return self._result(
                status="fallback",
                error="Class 'setup.ve_build_ext' is not available.",
                guidance="Ensure setuptools extension build class is importable from setup.py.",
                details={"import_errors": self._import_errors},
            )
        try:
            obj = cls(*args, **kwargs)
            return self._result(status="success", data={"result": obj, "class": "setup.ve_build_ext"})
        except Exception as exc:
            return self._result(
                status="error",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Pass a valid setuptools Distribution object and expected parameters.",
                details={"traceback": traceback.format_exc()},
            )

    def call_setup_read(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call setup.read(*args, **kwargs)."""
        return self._call("setup.read", *args, **kwargs)

    def call_setup_run_setup(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call setup.run_setup(*args, **kwargs)."""
        return self._call("setup.run_setup", *args, **kwargs)

    def call_setup_try_find_library(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call setup.try_find_library(*args, **kwargs)."""
        return self._call("setup.try_find_library", *args, **kwargs)

    # -------------------------------------------------------------------------
    # bin.medpy_reslice_3d_to_4d functions
    # -------------------------------------------------------------------------

    def call_medpy_reslice_3d_to_4d_get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_reslice_3d_to_4d.getArguments.

        Typically parses CLI-like arguments for reslicing 3D volumes into 4D.
        """
        return self._call("bin.medpy_reslice_3d_to_4d.getArguments", *args, **kwargs)

    def call_medpy_reslice_3d_to_4d_get_parser(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_reslice_3d_to_4d.getParser.

        Returns parser object used by the script.
        """
        return self._call("bin.medpy_reslice_3d_to_4d.getParser", *args, **kwargs)

    def call_medpy_reslice_3d_to_4d_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_reslice_3d_to_4d.main.

        Executes the script main flow in import mode.
        """
        return self._call("bin.medpy_reslice_3d_to_4d.main", *args, **kwargs)

    # -------------------------------------------------------------------------
    # bin.medpy_extract_min_max functions
    # -------------------------------------------------------------------------

    def call_medpy_extract_min_max_get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_extract_min_max.getArguments.

        Typically parses arguments for min/max extraction from medical volumes.
        """
        return self._call("bin.medpy_extract_min_max.getArguments", *args, **kwargs)

    def call_medpy_extract_min_max_get_parser(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_extract_min_max.getParser.

        Returns parser object used by the script.
        """
        return self._call("bin.medpy_extract_min_max.getParser", *args, **kwargs)

    def call_medpy_extract_min_max_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_extract_min_max.main.

        Executes min/max extraction script logic.
        """
        return self._call("bin.medpy_extract_min_max.main", *args, **kwargs)

    # -------------------------------------------------------------------------
    # bin.medpy_convert functions
    # -------------------------------------------------------------------------

    def call_medpy_convert_get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bin.medpy_convert.getArguments.

        Parses conversion CLI arguments for supported medical image formats.
        """
        return self._call("bin.medpy_convert.getArguments", *args, **kwargs)

    # -------------------------------------------------------------------------
    # CLI fallback guidance (from analysis-reported commands)
    # -------------------------------------------------------------------------

    def cli_fallback_commands(self) -> Dict[str, Any]:
        """
        Provide curated CLI fallback commands detected by analysis.

        Returns:
            Unified dictionary with command list and descriptions.
        """
        commands: List[Dict[str, str]] = [
            {"name": "medpy_info", "module": "bin/medpy_info.py", "description": "Inspect image metadata and dimensional information."},
            {"name": "medpy_convert", "module": "bin/medpy_convert.py", "description": "Convert medical image volumes between supported formats."},
            {"name": "medpy_diff", "module": "bin/medpy_diff.py", "description": "Compare two images/volumes and report differences."},
            {"name": "medpy_resample", "module": "bin/medpy_resample.py", "description": "Resample image volume to target spacing/shape."},
            {"name": "medpy_anisotropic_diffusion", "module": "bin/medpy_anisotropic_diffusion.py", "description": "Apply anisotropic diffusion filtering to a volume."},
            {"name": "medpy_watershed", "module": "bin/medpy_watershed.py", "description": "Run watershed segmentation on image data."},
            {"name": "medpy_graphcut_voxel", "module": "bin/medpy_graphcut_voxel.py", "description": "Voxel-level graph-cut segmentation CLI workflow."},
            {"name": "medpy_graphcut_label", "module": "bin/medpy_graphcut_label.py", "description": "Label-based graph-cut segmentation CLI workflow."},
        ]
        return self._result(
            status="success",
            data={"commands": commands},
            guidance="If import calls fail, run these commands from the project environment where medpy dependencies are installed.",
        )