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
    Import-mode adapter for the GMatch4py repository.

    This adapter attempts to import and expose repository-level functionality
    discovered during analysis, with graceful fallback behavior when imports fail.

    Key features:
    - Import mode with fallback-safe execution
    - Unified return schema for all methods
    - Function-level wrappers for discovered callable entries
    - Helpful, actionable English-only error messages
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize the adapter in import mode and attempt to load target modules.

        Attributes:
            mode (str): Adapter running mode, fixed as "import".
            loaded (bool): Whether required modules were loaded successfully.
            modules (dict): Cached imported modules keyed by logical name.
            errors (list): Captured import-time errors.
        """
        self.mode = "import"
        self.loaded = False
        self.modules: Dict[str, Any] = {}
        self.errors: List[str] = []
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
        }

    def _load_modules(self) -> None:
        """
        Load known modules discovered by analysis.

        The analysis identified:
        - package: setup
        - module: setup
        - functions: makeExtension, scandir

        Also attempts optional package imports for repository subpackages to
        maximize utility and diagnosability.
        """
        required_imports = {
            "setup": "setup",
        }
        optional_imports = {
            "gmatch4py": "gmatch4py",
            "embedding": "gmatch4py.embedding",
            "ged": "gmatch4py.ged",
            "helpers": "gmatch4py.helpers",
            "kernels": "gmatch4py.kernels",
        }

        for key, module_path in required_imports.items():
            try:
                self.modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self.errors.append(
                    f"Failed to import required module '{module_path}'. "
                    f"Verify repository source is present under 'source/' and dependencies are installed. "
                    f"Original error: {exc}"
                )

        for key, module_path in optional_imports.items():
            try:
                self.modules[key] = importlib.import_module(module_path)
            except Exception:
                pass

        self.loaded = "setup" in self.modules

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and module availability.

        Returns:
            dict: Unified status payload with loaded modules and import diagnostics.
        """
        if self.loaded:
            return self._result(
                status="success",
                message="Adapter is ready in import mode.",
                data={
                    "loaded": True,
                    "loaded_modules": sorted(list(self.modules.keys())),
                    "import_errors": self.errors,
                },
            )
        return self._result(
            status="error",
            message=(
                "Adapter is not fully ready. Required modules failed to import. "
                "Ensure the repository exists under 'source/' and install dependencies: numpy, networkx, scipy."
            ),
            data={
                "loaded": False,
                "loaded_modules": sorted(list(self.modules.keys())),
                "import_errors": self.errors,
            },
            error="Required import failure",
        )

    # -------------------------------------------------------------------------
    # Function wrappers (discovered via analysis): setup.makeExtension
    # -------------------------------------------------------------------------
    def call_makeExtension(
        self,
        ext_name: str,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Call setup.makeExtension(ext_name, file_path) from repository setup module.

        Parameters:
            ext_name (str): Extension module name expected by setup helper.
            file_path (str): Relative or absolute path used by the setup helper.

        Returns:
            dict: Unified status response containing call output under data.result.
        """
        if not self.loaded:
            return self._result(
                status="error",
                message=(
                    "Import mode is unavailable because required modules could not be loaded. "
                    "Run health_check() and fix import issues first."
                ),
                error="Adapter not ready",
            )

        setup_mod = self.modules.get("setup")
        if setup_mod is None or not hasattr(setup_mod, "makeExtension"):
            return self._result(
                status="error",
                message=(
                    "Function 'makeExtension' is not available in module 'setup'. "
                    "Check repository version compatibility."
                ),
                error="Missing function",
            )

        try:
            result = setup_mod.makeExtension(ext_name, file_path)
            return self._result(
                status="success",
                message="Function 'makeExtension' executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=(
                    "Execution of 'makeExtension' failed. "
                    "Validate ext_name and file_path inputs and ensure setup configuration is valid."
                ),
                error=f"{exc}\n{traceback.format_exc()}",
            )

    # -------------------------------------------------------------------------
    # Function wrappers (discovered via analysis): setup.scandir
    # -------------------------------------------------------------------------
    def call_scandir(
        self,
        directory: str,
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Call setup.scandir(directory, files) from repository setup module.

        Parameters:
            directory (str): Directory path to recursively scan.
            files (list[str], optional): Existing accumulator list used by the original function.

        Returns:
            dict: Unified status response containing scan result under data.result.
        """
        if not self.loaded:
            return self._result(
                status="error",
                message=(
                    "Import mode is unavailable because required modules could not be loaded. "
                    "Run health_check() and fix import issues first."
                ),
                error="Adapter not ready",
            )

        setup_mod = self.modules.get("setup")
        if setup_mod is None or not hasattr(setup_mod, "scandir"):
            return self._result(
                status="error",
                message=(
                    "Function 'scandir' is not available in module 'setup'. "
                    "Check repository version compatibility."
                ),
                error="Missing function",
            )

        if files is None:
            files = []

        try:
            result = setup_mod.scandir(directory, files)
            return self._result(
                status="success",
                message="Function 'scandir' executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=(
                    "Execution of 'scandir' failed. "
                    "Ensure 'directory' exists and is readable, and 'files' is a list."
                ),
                error=f"{exc}\n{traceback.format_exc()}",
            )

    # -------------------------------------------------------------------------
    # Package access helpers (graceful fallback utilities)
    # -------------------------------------------------------------------------
    def get_package_info(self) -> Dict[str, Any]:
        """
        Return package-level import information for discovered gmatch4py modules.

        Returns:
            dict: Unified status response including available package modules.
        """
        available = {
            k: v.__name__
            for k, v in self.modules.items()
            if k in {"gmatch4py", "embedding", "ged", "helpers", "kernels"}
        }
        return self._result(
            status="success",
            message="Collected package import information.",
            data={
                "available_packages": available,
                "required_ready": self.loaded,
                "import_errors": self.errors,
            },
        )

    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when import mode is partially unavailable.

        Returns:
            dict: Unified status response with practical troubleshooting steps.
        """
        guidance = [
            "Ensure the repository root contains a 'source/' directory with GMatch4py files.",
            "Install required dependencies: numpy, networkx, scipy.",
            "Optional dependency for plotting: matplotlib.",
            "Verify Python can import 'setup' from the repository source path.",
            "Use health_check() to inspect current import status and error details.",
        ]
        return self._result(
            status="success",
            message="Fallback guidance generated.",
            data={"steps": guidance, "import_errors": self.errors},
        )