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
    MCP Import Mode Adapter for the Whoosh repository.

    This adapter prioritizes direct imports from repository source code and exposes
    structured methods for discovered classes/functions from the analysis result.
    All public methods return a unified dictionary containing at least a `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._imports_ready = False
        self._import_errors = []
        self._load_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
        if hint:
            payload["hint"] = hint
        return payload

    def _fallback(self, feature: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": "fallback",
            "message": f"Import mode is unavailable for '{feature}'.",
            "hint": (
                "Ensure repository source exists at '../../../source' relative to this file, "
                "and required module paths are present. Then reinitialize the adapter."
            ),
            "import_errors": list(self._import_errors),
        }

    def _load_imports(self) -> None:
        try:
            from benchmark.enron import Enron
            from benchmark.reuters import Reuters
            from benchmark.dictionary import VulgarTongue
            from benchmark.marc21 import author, getfields, isbn

            self.Enron = Enron
            self.Reuters = Reuters
            self.VulgarTongue = VulgarTongue
            self.author = author
            self.getfields = getfields
            self.isbn = isbn

            self._imports_ready = True
        except Exception as exc:
            self._imports_ready = False
            self._import_errors.append(str(exc))

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status response with import readiness and diagnostics.
        """
        if self._imports_ready:
            return self._ok(
                {
                    "imports_ready": True,
                    "source_path": source_path,
                },
                message="Adapter is ready in import mode.",
            )
        return self._fail(
            "Adapter imports failed.",
            hint="Verify source path and repository extraction integrity.",
        )

    # -------------------------------------------------------------------------
    # Class instance methods
    # -------------------------------------------------------------------------
    def create_enron_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and return an instance of benchmark.enron.Enron.

        Parameters:
            *args: Positional arguments forwarded to Enron constructor.
            **kwargs: Keyword arguments forwarded to Enron constructor.

        Returns:
            dict: Status payload with constructed object or detailed import/runtime error.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.enron.Enron")
        try:
            instance = self.Enron(*args, **kwargs)
            return self._ok({"instance": instance, "class": "benchmark.enron.Enron"})
        except Exception as exc:
            return self._fail(
                "Failed to create Enron instance.",
                error=exc,
                hint="Validate constructor arguments expected by benchmark.enron.Enron.",
            )

    def create_reuters_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and return an instance of benchmark.reuters.Reuters.

        Parameters:
            *args: Positional arguments forwarded to Reuters constructor.
            **kwargs: Keyword arguments forwarded to Reuters constructor.

        Returns:
            dict: Status payload with constructed object or detailed import/runtime error.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.reuters.Reuters")
        try:
            instance = self.Reuters(*args, **kwargs)
            return self._ok({"instance": instance, "class": "benchmark.reuters.Reuters"})
        except Exception as exc:
            return self._fail(
                "Failed to create Reuters instance.",
                error=exc,
                hint="Validate constructor arguments expected by benchmark.reuters.Reuters.",
            )

    def create_vulgartongue_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and return an instance of benchmark.dictionary.VulgarTongue.

        Parameters:
            *args: Positional arguments forwarded to VulgarTongue constructor.
            **kwargs: Keyword arguments forwarded to VulgarTongue constructor.

        Returns:
            dict: Status payload with constructed object or detailed import/runtime error.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.dictionary.VulgarTongue")
        try:
            instance = self.VulgarTongue(*args, **kwargs)
            return self._ok({"instance": instance, "class": "benchmark.dictionary.VulgarTongue"})
        except Exception as exc:
            return self._fail(
                "Failed to create VulgarTongue instance.",
                error=exc,
                hint="Validate constructor arguments expected by benchmark.dictionary.VulgarTongue.",
            )

    # -------------------------------------------------------------------------
    # Function call methods
    # -------------------------------------------------------------------------
    def call_marc21_author(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call benchmark.marc21.author.

        Parameters:
            *args: Positional arguments for author().
            **kwargs: Keyword arguments for author().

        Returns:
            dict: Status payload containing function result or actionable error details.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.marc21.author")
        try:
            result = self.author(*args, **kwargs)
            return self._ok({"result": result, "function": "benchmark.marc21.author"})
        except Exception as exc:
            return self._fail(
                "Failed to execute benchmark.marc21.author.",
                error=exc,
                hint="Check input structure and argument types expected by author().",
            )

    def call_marc21_getfields(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call benchmark.marc21.getfields.

        Parameters:
            *args: Positional arguments for getfields().
            **kwargs: Keyword arguments for getfields().

        Returns:
            dict: Status payload containing function result or actionable error details.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.marc21.getfields")
        try:
            result = self.getfields(*args, **kwargs)
            return self._ok({"result": result, "function": "benchmark.marc21.getfields"})
        except Exception as exc:
            return self._fail(
                "Failed to execute benchmark.marc21.getfields.",
                error=exc,
                hint="Ensure MARC data and field arguments match getfields() expectations.",
            )

    def call_marc21_isbn(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call benchmark.marc21.isbn.

        Parameters:
            *args: Positional arguments for isbn().
            **kwargs: Keyword arguments for isbn().

        Returns:
            dict: Status payload containing function result or actionable error details.
        """
        if not self._imports_ready:
            return self._fallback("benchmark.marc21.isbn")
        try:
            result = self.isbn(*args, **kwargs)
            return self._ok({"result": result, "function": "benchmark.marc21.isbn"})
        except Exception as exc:
            return self._fail(
                "Failed to execute benchmark.marc21.isbn.",
                error=exc,
                hint="Validate ISBN-related source input and argument formats.",
            )