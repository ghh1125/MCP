import os
import sys
import traceback
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

try:
    from stanza.utils.datasets.depparse.check_results import main as depparse_check_results_main
    IMPORT_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as e:
    depparse_check_results_main = None
    IMPORT_AVAILABLE = False
    IMPORT_ERROR = str(e)


class Adapter:
    """
    MCP import-mode adapter for the Stanza repository.

    This adapter prefers direct Python imports from the local `source` tree and
    gracefully falls back to CLI execution when imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._import_available = IMPORT_AVAILABLE
        self._import_error = IMPORT_ERROR

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode}
        if data:
            result.update(data)
        return result

    def _error(self, message: str, guidance: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            result["guidance"] = guidance
        if extra:
            result.update(extra)
        return result

    def _run_cli(self, module: str, args: Optional[List[str]] = None, timeout: int = 3600) -> Dict[str, Any]:
        cmd = [sys.executable, "-m", module] + (args or [])
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if proc.returncode == 0:
                return self._ok(
                    {
                        "fallback": "cli",
                        "module": module,
                        "returncode": proc.returncode,
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                        "command": cmd,
                    }
                )
            return self._error(
                f"CLI command failed with return code {proc.returncode}.",
                guidance="Inspect stderr and verify module dependencies and input arguments.",
                extra={
                    "fallback": "cli",
                    "module": module,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "command": cmd,
                },
            )
        except subprocess.TimeoutExpired:
            return self._error(
                "CLI command timed out.",
                guidance="Increase timeout or reduce workload size.",
                extra={"fallback": "cli", "module": module, "command": cmd},
            )
        except Exception as e:
            return self._error(
                f"Failed to execute CLI command: {e}",
                guidance="Check Python executable, module path, and runtime environment.",
                extra={"fallback": "cli", "module": module, "traceback": traceback.format_exc(), "command": cmd},
            )

    # ---------------------------------------------------------------------
    # Health & diagnostics
    # ---------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import availability.

        Returns:
            dict: Unified status payload including mode and import diagnostics.
        """
        if self._import_available:
            return self._ok(
                {
                    "import_available": True,
                    "imported_modules": ["stanza.utils.datasets.depparse.check_results"],
                }
            )
        return self._error(
            "Import mode is not fully available.",
            guidance="Ensure repository source is present at the expected path and all dependencies are installed.",
            extra={"import_available": False, "import_error": self._import_error},
        )

    # ---------------------------------------------------------------------
    # Imported function wrappers
    # ---------------------------------------------------------------------
    def call_stanza_utils_datasets_depparse_check_results_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call `main` from `stanza.utils.datasets.depparse.check_results`.

        Parameters:
            argv (Optional[List[str]]):
                Optional argument list for compatibility. The upstream `main`
                may parse process-level arguments depending on implementation.

        Returns:
            dict:
                Unified result with `status` field. Includes execution result
                when successful, or actionable error guidance on failure.
        """
        if self._import_available and depparse_check_results_main is not None:
            try:
                result = depparse_check_results_main() if argv is None else depparse_check_results_main()
                return self._ok(
                    {
                        "function": "stanza.utils.datasets.depparse.check_results.main",
                        "result": result,
                    }
                )
            except Exception as e:
                return self._error(
                    f"Imported function execution failed: {e}",
                    guidance="Validate input files and expected runtime arguments for check_results.main.",
                    extra={
                        "function": "stanza.utils.datasets.depparse.check_results.main",
                        "traceback": traceback.format_exc(),
                    },
                )

        return self._run_cli("stanza.utils.datasets.depparse.check_results", args=argv or [])

    # ---------------------------------------------------------------------
    # CLI convenience wrappers from analysis
    # ---------------------------------------------------------------------
    def run_server_main(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run `python -m stanza.server.main` as a fallback-capable CLI workflow."""
        return self._run_cli("stanza.server.main", args=args or [])

    def run_pipeline_demo_server(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run `python -m stanza.pipeline.demo.demo_server` for demo visualization."""
        return self._run_cli("stanza.pipeline.demo.demo_server", args=args or [])

    def run_training_tokenizer(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run tokenizer training CLI: `python -m stanza.utils.training.run_tokenizer`."""
        return self._run_cli("stanza.utils.training.run_tokenizer", args=args or [])

    def run_training_pos(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run POS training CLI: `python -m stanza.utils.training.run_pos`."""
        return self._run_cli("stanza.utils.training.run_pos", args=args or [])

    def run_training_lemma(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run lemmatizer training CLI: `python -m stanza.utils.training.run_lemma`."""
        return self._run_cli("stanza.utils.training.run_lemma", args=args or [])

    def run_training_depparse(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run dependency parser training CLI: `python -m stanza.utils.training.run_depparse`."""
        return self._run_cli("stanza.utils.training.run_depparse", args=args or [])

    def run_training_ner(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run NER training CLI: `python -m stanza.utils.training.run_ner`."""
        return self._run_cli("stanza.utils.training.run_ner", args=args or [])

    def run_training_sentiment(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run sentiment training CLI: `python -m stanza.utils.training.run_sentiment`."""
        return self._run_cli("stanza.utils.training.run_sentiment", args=args or [])

    def run_training_constituency(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run constituency training CLI: `python -m stanza.utils.training.run_constituency`."""
        return self._run_cli("stanza.utils.training.run_constituency", args=args or [])

    # ---------------------------------------------------------------------
    # Capability summary
    # ---------------------------------------------------------------------
    def capabilities(self) -> Dict[str, Any]:
        """
        Return adapter capabilities and available execution paths.

        Returns:
            dict: Unified status payload with import and CLI capability details.
        """
        return self._ok(
            {
                "import_strategy": {
                    "primary": "import",
                    "fallback": "cli",
                    "import_available": self._import_available,
                    "import_error": self._import_error,
                },
                "imported_functions": [
                    "stanza.utils.datasets.depparse.check_results.main",
                ],
                "cli_commands": [
                    "stanza.server.main",
                    "stanza.pipeline.demo.demo_server",
                    "stanza.utils.training.run_tokenizer",
                    "stanza.utils.training.run_pos",
                    "stanza.utils.training.run_lemma",
                    "stanza.utils.training.run_depparse",
                    "stanza.utils.training.run_ner",
                    "stanza.utils.training.run_sentiment",
                    "stanza.utils.training.run_constituency",
                ],
            }
        )