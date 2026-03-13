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
    MCP import-mode adapter for python-igraph repository integration.

    This adapter prioritizes importing repository-local modules using full package paths
    derived from the analysis result, and exposes a structured API with unified status
    dictionaries for robust MCP plugin integration.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._available = False
        self._import_error: Optional[str] = None
        self._Graph = None
        self._shell_module = None
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        try:
            from src.igraph import Graph  # full path from analysis-derived source tree
            from src.igraph.app import shell as shell_module  # cli-related module

            self._Graph = Graph
            self._shell_module = shell_module
            self._available = True
            self._import_error = None
        except Exception as exc:
            self._available = False
            self._import_error = (
                f"Failed to import python-igraph repository modules. "
                f"Verify repository source is present under '{source_path}' and compatible runtime "
                f"dependencies are installed. Details: {exc}"
            )

    # -------------------------------------------------------------------------
    # Unified response helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _err(self, message: str, error: Optional[str] = None, data: Any = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = error
        if data is not None:
            payload["data"] = data
        return payload

    def _unavailable(self) -> Dict[str, Any]:
        return self._err(
            message="Import mode is unavailable.",
            error=self._import_error
            or "Repository modules could not be imported. Check source path and dependencies.",
            data={
                "guidance": [
                    "Ensure the repository source directory is mounted at the expected path.",
                    "Install runtime dependencies for python-igraph, including binary components.",
                    "Retry initialization after environment setup.",
                ]
            },
        )

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import-mode availability.

        Returns:
            dict: Unified status dictionary with adapter health details.
        """
        if self._available:
            return self._ok(
                data={
                    "available": True,
                    "import_strategy": "import",
                    "intrusiveness_risk": "low",
                    "complexity": "medium",
                },
                message="Adapter is ready in import mode.",
            )
        return self._unavailable()

    # -------------------------------------------------------------------------
    # Class instance methods (identified class: Graph)
    # -------------------------------------------------------------------------
    def create_graph_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a new igraph Graph instance.

        Parameters:
            *args: Positional arguments forwarded to src.igraph.Graph constructor.
            **kwargs: Keyword arguments forwarded to src.igraph.Graph constructor.

        Returns:
            dict: Unified status dictionary with created Graph object in `data`.
                  On failure, includes actionable error guidance.
        """
        if not self._available:
            return self._unavailable()
        try:
            graph_obj = self._Graph(*args, **kwargs)
            return self._ok(data={"graph": graph_obj}, message="Graph instance created.")
        except Exception as exc:
            return self._err(
                message="Failed to create Graph instance.",
                error=f"Check constructor arguments passed to Graph. Details: {exc}",
            )

    # -------------------------------------------------------------------------
    # CLI-related call methods (identified module: src.igraph.app.shell)
    # -------------------------------------------------------------------------
    def call_igraph_shell_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke igraph shell entry behavior from src.igraph.app.shell when available.

        Parameters:
            *args: Positional arguments forwarded to shell.main if present.
            **kwargs: Keyword arguments forwarded to shell.main if present.

        Returns:
            dict: Unified status dictionary with execution result or fallback guidance.
        """
        if not self._available:
            return self._unavailable()

        try:
            main_fn = getattr(self._shell_module, "main", None)
            if callable(main_fn):
                result = main_fn(*args, **kwargs)
                return self._ok(
                    data={"result": result},
                    message="igraph shell main executed.",
                )

            return self._err(
                message="igraph shell main is not exposed by module.",
                error=(
                    "The module 'src.igraph.app.shell' does not provide a callable 'main'. "
                    "Inspect module attributes or use interactive shell integration directly."
                ),
            )
        except Exception as exc:
            return self._err(
                message="Failed to execute igraph shell main.",
                error=f"Shell execution failed. Verify environment compatibility. Details: {exc}",
            )

    # -------------------------------------------------------------------------
    # General module management and fallback support
    # -------------------------------------------------------------------------
    def reload_imports(self) -> Dict[str, Any]:
        """
        Re-attempt repository module imports.

        Returns:
            dict: Unified status dictionary indicating whether imports were restored.
        """
        self._initialize_imports()
        if self._available:
            return self._ok(message="Imports reloaded successfully.", data={"available": True})
        return self._unavailable()

    def metadata(self) -> Dict[str, Any]:
        """
        Return adapter metadata derived from analysis signals.

        Returns:
            dict: Unified status dictionary with repository and capability metadata.
        """
        return self._ok(
            data={
                "repository_url": "https://github.com/igraph/python-igraph",
                "mode": self.mode,
                "primary_module": "src.igraph",
                "identified_class": "Graph",
                "identified_cli_module": "src.igraph.app.shell",
                "optional_dependencies": ["matplotlib", "plotly", "pycairo/cairocffi", "texttable"],
            },
            message="Adapter metadata retrieved.",
        )