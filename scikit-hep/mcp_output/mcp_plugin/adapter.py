import os
import sys
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the scikit-hep repository.

    This adapter attempts to import and use the repository-local implementation
    from the configured source path. It provides unified status responses,
    graceful fallback guidance, and structured module management.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state and attempt imports.

        Attributes:
            mode (str): Execution mode, fixed to "import".
            available (bool): True if core imports succeeded.
            import_error (Optional[str]): Error details from import failure.
        """
        self.mode = "import"
        self.available = False
        self.import_error: Optional[str] = None

        self._skhep = None
        self._show_versions_func = None

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
        Load repository modules using full package paths from analysis.

        Packages identified:
            - source.skhep  -> import path: skhep
            - skhep._show_versions.show_versions
        """
        try:
            import skhep
            from skhep._show_versions import show_versions

            self._skhep = skhep
            self._show_versions_func = show_versions
            self.available = True
            self.import_error = None
        except Exception as exc:
            self.available = False
            self.import_error = (
                f"Failed to import repository modules. "
                f"Verify source path and repository integrity. Details: {exc}"
            )

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter availability and import health.

        Returns:
            dict: Unified status dictionary with import diagnostics.
        """
        if self.available:
            return self._result(
                "success",
                "Adapter is ready. Repository modules imported successfully.",
                data={
                    "source_path": source_path,
                    "imports": ["skhep", "skhep._show_versions.show_versions"],
                },
            )
        return self._result(
            "fallback",
            "Import mode is unavailable. Use fallback workflow or fix local source checkout.",
            data={"source_path": source_path},
            error=self.import_error,
        )

    # -------------------------------------------------------------------------
    # Repository module wrappers
    # -------------------------------------------------------------------------
    def get_version(self) -> Dict[str, Any]:
        """
        Retrieve scikit-hep package version from repository module.

        Returns:
            dict:
                status: success|fallback|error
                data.version: package version string when available
        """
        if not self.available or self._skhep is None:
            return self._result(
                "fallback",
                "Cannot read version because imports are unavailable.",
                error=self.import_error,
            )
        try:
            version = getattr(self._skhep, "__version__", None)
            if version is None:
                return self._result(
                    "error",
                    "Version attribute is missing from skhep module.",
                    error="Expected attribute '__version__' was not found.",
                )
            return self._result(
                "success",
                "Version retrieved successfully.",
                data={"version": str(version)},
            )
        except Exception as exc:
            return self._result(
                "error",
                "Failed to retrieve package version.",
                error=f"{exc}",
            )

    def get_citation(self) -> Dict[str, Any]:
        """
        Retrieve citation string from skhep module if available.

        Returns:
            dict:
                status: success|fallback|error
                data.citation: citation string when present
        """
        if not self.available or self._skhep is None:
            return self._result(
                "fallback",
                "Cannot read citation because imports are unavailable.",
                error=self.import_error,
            )
        try:
            citation = getattr(self._skhep, "__citation__", None)
            if citation is None:
                return self._result(
                    "error",
                    "Citation attribute is not available in this repository revision.",
                    error="Expected attribute '__citation__' was not found.",
                )
            return self._result(
                "success",
                "Citation retrieved successfully.",
                data={"citation": str(citation)},
            )
        except Exception as exc:
            return self._result(
                "error",
                "Failed to retrieve citation.",
                error=f"{exc}",
            )

    def call_show_versions(self) -> Dict[str, Any]:
        """
        Execute `skhep._show_versions.show_versions()`.

        This function prints environment and dependency version details to stdout
        in the upstream implementation.

        Returns:
            dict:
                status: success|fallback|error
                message: execution result
                data.note: indicates output is printed by upstream function
        """
        if not self.available or self._show_versions_func is None:
            return self._result(
                "fallback",
                "Cannot run show_versions because imports are unavailable.",
                error=self.import_error,
            )
        try:
            self._show_versions_func()
            return self._result(
                "success",
                "show_versions executed successfully.",
                data={
                    "note": "Version details were emitted by upstream function output."
                },
            )
        except Exception as exc:
            return self._result(
                "error",
                "show_versions execution failed.",
                error=f"{exc}",
            )

    # -------------------------------------------------------------------------
    # Dependency and fallback guidance
    # -------------------------------------------------------------------------
    def check_dependencies(self) -> Dict[str, Any]:
        """
        Check availability of key dependencies identified by LLM analysis.

        Required dependencies analyzed:
            numpy, scipy, pandas, matplotlib, uproot, awkward

        Returns:
            dict:
                status: success|error
                data.available: list of importable dependencies
                data.missing: list of missing dependencies
        """
        deps = ["numpy", "scipy", "pandas", "matplotlib", "uproot", "awkward"]
        available = []
        missing = []

        for dep in deps:
            try:
                __import__(dep)
                available.append(dep)
            except Exception:
                missing.append(dep)

        if missing:
            return self._result(
                "error",
                "Some required dependencies are missing. Install them to enable full functionality.",
                data={"available": available, "missing": missing},
                error="Install missing packages in the current Python environment.",
            )

        return self._result(
            "success",
            "All analyzed dependencies are available.",
            data={"available": available, "missing": missing},
        )

    def fallback_help(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance for import failures.

        Returns:
            dict: Unified status with troubleshooting steps.
        """
        steps = [
            "Ensure repository source is present under the expected 'source' directory.",
            "Verify this adapter file is located so the computed source_path is correct.",
            "Confirm package path contains 'skhep/__init__.py'.",
            "Install required dependencies: numpy scipy pandas matplotlib uproot awkward.",
            "Re-run health_check after fixing environment issues.",
        ]
        return self._result(
            "fallback",
            "Import mode fallback guidance.",
            data={"steps": steps, "source_path": source_path},
            error=self.import_error,
        )

    # -------------------------------------------------------------------------
    # Diagnostic utility
    # -------------------------------------------------------------------------
    def debug_traceback(self) -> Dict[str, Any]:
        """
        Return a traceback snapshot for last known import issue context.

        Returns:
            dict: success with traceback text if available, otherwise fallback.
        """
        if self.available:
            return self._result(
                "success",
                "No import traceback available because adapter is healthy.",
                data={},
            )

        tb = traceback.format_exc()
        if not tb or tb.strip() == "NoneType: None":
            tb = "No active exception traceback. Use health_check and fallback_help for guidance."
        return self._result(
            "fallback",
            "Diagnostic traceback generated.",
            data={"traceback": tb},
            error=self.import_error,
        )