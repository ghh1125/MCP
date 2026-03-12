import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the pymc-marketing repository.

    This adapter prioritizes direct imports from the local `source` directory and
    provides graceful fallback behavior when imports are unavailable.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize the adapter in import mode and attempt module/class loading.

        Attributes:
            mode: Adapter operating mode. Required to be "import".
            import_ok: Whether core imports succeeded.
            _import_error: Captured import failure message for diagnostics.
            _ModelBuilder: Imported ModelBuilder class reference or None.
        """
        self.mode = "import"
        self.import_ok = False
        self._import_error: Optional[str] = None
        self._ModelBuilder = None

        self._load_modules()

    def _load_modules(self) -> None:
        """
        Load required modules/classes from local source tree.

        This method uses full package paths derived from analysis output:
        - source.pymc_marketing.model_builder -> pymc_marketing.model_builder

        Returns:
            None
        """
        try:
            from pymc_marketing.model_builder import ModelBuilder

            self._ModelBuilder = ModelBuilder
            self.import_ok = True
            self._import_error = None
        except Exception as exc:
            self.import_ok = False
            self._ModelBuilder = None
            self._import_error = (
                f"Failed to import pymc_marketing.model_builder.ModelBuilder: {exc}. "
                "Ensure dependencies are installed (numpy, pandas, pymc, pytensor, "
                "arviz, scipy, xarray) and the local source directory is present."
            )

    # -------------------------------------------------------------------------
    # Unified response helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status dictionary with import diagnostics.
        """
        if self.import_ok:
            return self._ok(
                {
                    "import_ok": True,
                    "details": "Core imports loaded successfully.",
                    "core_module": "pymc_marketing.model_builder",
                    "core_class": "ModelBuilder",
                }
            )
        return self._err(
            "Import mode is unavailable. Verify local source path and required dependencies.",
            {"import_ok": False, "details": self._import_error},
        )

    # -------------------------------------------------------------------------
    # Class factory methods (identified classes)
    # -------------------------------------------------------------------------
    def create_model_builder_instance(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create an instance of pymc_marketing.model_builder.ModelBuilder.

        Parameters:
            *args: Positional arguments forwarded to ModelBuilder constructor.
            **kwargs: Keyword arguments forwarded to ModelBuilder constructor.

        Returns:
            dict:
                - status: "success" or "error"
                - mode: adapter mode
                - instance: created object on success
                - class_name/module: metadata
                - message/details: actionable errors on failure
        """
        if not self.import_ok or self._ModelBuilder is None:
            return self._err(
                "Cannot create ModelBuilder instance because imports failed. "
                "Run health_check() and install missing dependencies."
            )
        try:
            instance = self._ModelBuilder(*args, **kwargs)
            return self._ok(
                {
                    "instance": instance,
                    "class_name": "ModelBuilder",
                    "module": "pymc_marketing.model_builder",
                }
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate ModelBuilder: {exc}. "
                "Validate constructor arguments and repository compatibility."
            )

    # -------------------------------------------------------------------------
    # Function call methods (none identified in analysis)
    # -------------------------------------------------------------------------
    def call_identified_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic function call placeholder for identified top-level functions.

        The analysis result did not identify concrete top-level functions.
        This method provides a stable API with actionable guidance.

        Parameters:
            function_name: Expected function name to invoke.
            *args: Positional arguments (unused here).
            **kwargs: Keyword arguments (unused here).

        Returns:
            dict: Unified error response with guidance.
        """
        return self._err(
            f"No identified top-level function named '{function_name}' was provided by analysis. "
            "Use class-based methods (e.g., create_model_builder_instance) or extend adapter mappings."
        )