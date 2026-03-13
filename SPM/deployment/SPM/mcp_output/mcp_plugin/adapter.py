import os
import sys
import inspect
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

# =============================================================================
# Adapter Module: Import-mode MCP adapter for SPM
# Repository: https://github.com/YanLab-Westlake/SPM
# Primary module target:
#   deployment.SPM.source.scripts.SequencePatternMatching
# Fallback mode:
#   CLI-style guidance for "python scripts/SequencePatternMatching.py"
# =============================================================================


class Adapter:
    """
    MCP Import Mode Adapter for SPM Sequence Pattern Matching.

    This adapter attempts to import and execute repository-native functions:
    - loadUniprotDB
    - peptideSearching
    - volumeScoring

    If import fails, the adapter gracefully falls back to guidance mode (CLI-like).
    All public methods return a unified dictionary format with at least:
    - status: "success" | "error" | "fallback"
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt dynamic import binding.

        Attributes:
            mode (str): Adapter operating mode. Defaults to "import".
            module_path (str): Full target module path inferred from analysis.
            module (Any): Imported module object when available.
            import_ready (bool): Whether import-mode execution is available.
            import_error (str): Last import error, if any.
        """
        self.mode: str = "import"
        self.module_path: str = "deployment.SPM.source.scripts.SequencePatternMatching"
        self.module: Optional[Any] = None
        self.import_ready: bool = False
        self.import_error: Optional[str] = None

        self._fn_load_uniprot_db = None
        self._fn_peptide_searching = None
        self._fn_volume_scoring = None

        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """Attempt import and bind required repository functions."""
        try:
            module = __import__(self.module_path, fromlist=["*"])
            self.module = module

            self._fn_load_uniprot_db = getattr(module, "loadUniprotDB", None)
            self._fn_peptide_searching = getattr(module, "peptideSearching", None)
            self._fn_volume_scoring = getattr(module, "volumeScoring", None)

            missing = []
            if self._fn_load_uniprot_db is None:
                missing.append("loadUniprotDB")
            if self._fn_peptide_searching is None:
                missing.append("peptideSearching")
            if self._fn_volume_scoring is None:
                missing.append("volumeScoring")

            if missing:
                self.import_ready = False
                self.import_error = (
                    f"Imported module but missing expected functions: {', '.join(missing)}. "
                    f"Please verify repository version and function names in {self.module_path}."
                )
            else:
                self.import_ready = True
                self.import_error = None

        except Exception as exc:
            self.import_ready = False
            self.import_error = (
                f"Failed to import module '{self.module_path}'. "
                f"Ensure source path is correct and dependencies are available. "
                f"Details: {exc}"
            )

    # -------------------------------------------------------------------------
    # Unified Response Helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "message": message,
            "data": data or {},
        }

    def _fallback(self, message: str, guidance: Optional[List[str]] = None) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": message,
            "guidance": guidance or [
                "Run the script directly: python scripts/SequencePatternMatching.py",
                "Confirm source path points to repository root containing scripts/SequencePatternMatching.py",
                "Check Python 3 environment and local file inputs required by the script.",
            ],
            "import_error": self.import_error,
        }

    def _error(self, message: str, exception: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if exception is not None:
            payload["error"] = str(exception)
            payload["traceback"] = traceback.format_exc()
        return payload

    # -------------------------------------------------------------------------
    # Module / Capability Management
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and imported function availability.

        Returns:
            dict: Unified status payload with import readiness, function list,
                  module path, and optional import error guidance.
        """
        try:
            functions = {
                "loadUniprotDB": self._fn_load_uniprot_db is not None,
                "peptideSearching": self._fn_peptide_searching is not None,
                "volumeScoring": self._fn_volume_scoring is not None,
            }
            if self.import_ready:
                return self._ok(
                    "Adapter is ready in import mode.",
                    data={
                        "import_ready": True,
                        "module_path": self.module_path,
                        "functions": functions,
                    },
                )
            return self._fallback(
                "Adapter is not ready for import-mode execution.",
                guidance=[
                    "Verify the repository is mounted at deployment/SPM/source.",
                    f"Expected import module: {self.module_path}",
                    "If import remains unavailable, execute via CLI: python scripts/SequencePatternMatching.py",
                ],
            )
        except Exception as exc:
            return self._error("Health check failed unexpectedly.", exc)

    def describe_module(self) -> Dict[str, Any]:
        """
        Provide introspection details for the target module and bound functions.

        Returns:
            dict: Module metadata including function signatures where available.
        """
        try:
            if not self.import_ready or self.module is None:
                return self._fallback(
                    "Cannot describe module because import mode is unavailable."
                )

            signatures = {}
            for fn_name, fn_obj in [
                ("loadUniprotDB", self._fn_load_uniprot_db),
                ("peptideSearching", self._fn_peptide_searching),
                ("volumeScoring", self._fn_volume_scoring),
            ]:
                try:
                    signatures[fn_name] = str(inspect.signature(fn_obj))
                except Exception:
                    signatures[fn_name] = "signature unavailable"

            return self._ok(
                "Module description retrieved successfully.",
                data={
                    "module_path": self.module_path,
                    "module_file": getattr(self.module, "__file__", None),
                    "functions": signatures,
                    "doc": getattr(self.module, "__doc__", None),
                },
            )
        except Exception as exc:
            return self._error("Failed to describe target module.", exc)

    # -------------------------------------------------------------------------
    # Wrapped Repository Functions
    # -------------------------------------------------------------------------
    def call_loadUniprotDB(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call SequencePatternMatching.loadUniprotDB.

        Parameters:
            *args: Positional arguments forwarded to the original function.
            **kwargs: Keyword arguments forwarded to the original function.

        Returns:
            dict: Unified status payload containing function result in data.result.

        Notes:
            - Exact parameter contract depends on repository implementation.
            - Use describe_module() to inspect callable signature when available.
        """
        try:
            if not self.import_ready or self._fn_load_uniprot_db is None:
                return self._fallback(
                    "loadUniprotDB is unavailable in import mode.",
                    guidance=[
                        "Check function existence in scripts/SequencePatternMatching.py",
                        "Run module directly for script-style workflow: python scripts/SequencePatternMatching.py",
                    ],
                )

            result = self._fn_load_uniprot_db(*args, **kwargs)
            return self._ok(
                "loadUniprotDB executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._error(
                "loadUniprotDB execution failed. Verify input file paths and parameter types.",
                exc,
            )

    def call_peptideSearching(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call SequencePatternMatching.peptideSearching.

        Parameters:
            *args: Positional arguments forwarded to the original function.
            **kwargs: Keyword arguments forwarded to the original function.

        Returns:
            dict: Unified status payload containing function result in data.result.

        Notes:
            - Intended for sequence pattern matching search operations.
            - Ensure sequence/query format aligns with repository expectations.
        """
        try:
            if not self.import_ready or self._fn_peptide_searching is None:
                return self._fallback(
                    "peptideSearching is unavailable in import mode.",
                    guidance=[
                        "Confirm function name and repository version.",
                        "Fallback execution: python scripts/SequencePatternMatching.py",
                    ],
                )

            result = self._fn_peptide_searching(*args, **kwargs)
            return self._ok(
                "peptideSearching executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._error(
                "peptideSearching execution failed. Check peptide/query inputs and database loading steps.",
                exc,
            )

    def call_volumeScoring(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call SequencePatternMatching.volumeScoring.

        Parameters:
            *args: Positional arguments forwarded to the original function.
            **kwargs: Keyword arguments forwarded to the original function.

        Returns:
            dict: Unified status payload containing function result in data.result.

        Notes:
            - Typically used to score/rank matched sequence results.
            - Validate scoring inputs are correctly preprocessed.
        """
        try:
            if not self.import_ready or self._fn_volume_scoring is None:
                return self._fallback(
                    "volumeScoring is unavailable in import mode.",
                    guidance=[
                        "Ensure prior search outputs are valid before scoring.",
                        "Use CLI fallback if import path cannot be resolved.",
                    ],
                )

            result = self._fn_volume_scoring(*args, **kwargs)
            return self._ok(
                "volumeScoring executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._error(
                "volumeScoring execution failed. Verify scoring inputs and numeric data validity.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Orchestration Convenience
    # -------------------------------------------------------------------------
    def run_pipeline(
        self,
        load_args: Optional[List[Any]] = None,
        load_kwargs: Optional[Dict[str, Any]] = None,
        search_args: Optional[List[Any]] = None,
        search_kwargs: Optional[Dict[str, Any]] = None,
        score_args: Optional[List[Any]] = None,
        score_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a simple 3-step pipeline:
        1) loadUniprotDB
        2) peptideSearching
        3) volumeScoring

        Parameters:
            load_args/load_kwargs: Arguments for loadUniprotDB.
            search_args/search_kwargs: Arguments for peptideSearching.
            score_args/score_kwargs: Arguments for volumeScoring.

        Returns:
            dict: Unified status payload with per-step execution results.

        Important:
            This method does not auto-wire outputs between steps because original
            function contracts may vary by repository version. Pass explicit args.
        """
        try:
            if not self.import_ready:
                return self._fallback(
                    "Pipeline cannot run because import mode is unavailable."
                )

            load_resp = self.call_loadUniprotDB(*(load_args or []), **(load_kwargs or {}))
            if load_resp.get("status") != "success":
                return self._error(
                    "Pipeline stopped at loadUniprotDB. Resolve the previous error and retry."
                )

            search_resp = self.call_peptideSearching(*(search_args or []), **(search_kwargs or {}))
            if search_resp.get("status") != "success":
                return self._error(
                    "Pipeline stopped at peptideSearching. Resolve the previous error and retry."
                )

            score_resp = self.call_volumeScoring(*(score_args or []), **(score_kwargs or {}))
            if score_resp.get("status") != "success":
                return self._error(
                    "Pipeline stopped at volumeScoring. Resolve the previous error and retry."
                )

            return self._ok(
                "Pipeline executed successfully.",
                data={
                    "loadUniprotDB": load_resp.get("data", {}).get("result"),
                    "peptideSearching": search_resp.get("data", {}).get("result"),
                    "volumeScoring": score_resp.get("data", {}).get("result"),
                },
            )
        except Exception as exc:
            return self._error("Pipeline execution failed unexpectedly.", exc)