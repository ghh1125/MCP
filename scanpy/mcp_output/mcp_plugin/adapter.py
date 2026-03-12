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
    MCP Import Mode Adapter for Scanpy repository integration.

    This adapter prioritizes direct import execution from repository source code
    and provides a graceful fallback path when import execution is unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._scanpy = None
        self._cli_module = None
        self._import_error: Optional[str] = None
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        return self._err(
            message=f"Import mode unavailable for action: {action}.",
            hint=(
                "Ensure repository dependencies are installed and the source path is correct. "
                "You may fallback to CLI mode by running `python -m scanpy --help`."
            ),
        )

    def _initialize_imports(self) -> None:
        try:
            import scanpy as scanpy_module
            self._scanpy = scanpy_module
        except Exception as e:
            self._import_error = str(e)
            self._scanpy = None

        try:
            import scanpy.cli as cli_module
            self._cli_module = cli_module
        except Exception:
            self._cli_module = None

    def health_check(self) -> Dict[str, Any]:
        """
        Verify adapter readiness and import health.

        Returns:
            dict: Unified status dictionary with adapter health details.
        """
        if self._scanpy is None:
            return self._err(
                message="Scanpy import failed.",
                hint="Install required dependencies such as anndata, numpy, scipy, pandas, matplotlib, and scikit-learn.",
            )
        return self._ok(
            {
                "scanpy_version": getattr(self._scanpy, "__version__", "unknown"),
                "cli_available": self._cli_module is not None,
            },
            message="Import mode is ready.",
        )

    # -------------------------------------------------------------------------
    # Core module methods (scanpy)
    # -------------------------------------------------------------------------
    def get_module(self) -> Dict[str, Any]:
        """
        Return imported scanpy module metadata.

        Returns:
            dict: Status and basic module information.
        """
        if self._scanpy is None:
            return self._fallback("get_module")
        return self._ok(
            {
                "module": "scanpy",
                "file": getattr(self._scanpy, "__file__", None),
                "version": getattr(self._scanpy, "__version__", None),
            }
        )

    def run_function(
        self,
        function_path: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Invoke a Scanpy function dynamically by dotted path.

        Args:
            function_path: Dotted path under scanpy namespace, e.g. "pp.normalize_total" or "tl.umap".
            *args: Positional arguments passed to the target function.
            **kwargs: Keyword arguments passed to the target function.

        Returns:
            dict: Unified status dictionary with function result or error details.
        """
        if self._scanpy is None:
            return self._fallback(f"run_function:{function_path}")

        try:
            target = self._scanpy
            for part in function_path.split("."):
                target = getattr(target, part)
            if not callable(target):
                return self._err(
                    message=f"Target is not callable: {function_path}",
                    hint="Provide a valid callable function path under scanpy.",
                )
            result = target(*args, **kwargs)
            return self._ok({"function": function_path, "result": result})
        except Exception as e:
            return self._err(
                message=f"Failed to execute function: {function_path}",
                hint="Verify parameters, AnnData object state, and optional dependency availability.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # CLI module methods (scanpy.cli / python -m scanpy)
    # -------------------------------------------------------------------------
    def cli_help(self) -> Dict[str, Any]:
        """
        Return CLI availability information and usage guidance.

        Returns:
            dict: Unified status dictionary with CLI guidance.
        """
        if self._cli_module is None:
            return self._err(
                message="Scanpy CLI module is not available in import mode.",
                hint="Run `python -m scanpy --help` directly to validate CLI entry point.",
            )
        return self._ok(
            {
                "entrypoints": ["scanpy", "python -m scanpy"],
                "module": "scanpy.cli",
                "usage_hint": "Use subprocess execution for full CLI command support.",
            },
            message="CLI module loaded.",
        )

    def cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute Scanpy CLI main function when available.

        Args:
            argv: Optional argument list to pass to CLI parser behavior.

        Returns:
            dict: Unified status dictionary with execution outcome.
        """
        if self._cli_module is None:
            return self._fallback("cli_main")

        try:
            main_fn = getattr(self._cli_module, "main", None)
            if main_fn is None or not callable(main_fn):
                return self._err(
                    message="scanpy.cli.main is not callable or missing.",
                    hint="Inspect src/scanpy/cli.py for available callable entry points.",
                )
            result = main_fn(argv) if argv is not None else main_fn()
            return self._ok({"result": result}, message="CLI main executed.")
        except SystemExit as e:
            return self._ok({"exit_code": int(getattr(e, "code", 0) or 0)}, message="CLI exited normally.")
        except Exception as e:
            return self._err(
                message="CLI execution failed.",
                hint="Check CLI arguments and environment dependencies.",
                error=e,
            )