import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the vaderSentiment repository.

    This adapter attempts to import repository modules directly from the local
    source tree and exposes method wrappers for discovered callable features.
    It provides consistent status dictionaries for all operations and includes
    graceful fallback behavior when imports are unavailable.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and preload module/function handles.

        Attributes:
            mode (str): Adapter mode, always "import".
            available (bool): Whether core imports were successful.
            import_errors (list): Collection of import-related errors.
        """
        self.mode = "import"
        self.available = False
        self.import_errors: List[str] = []

        self._setup_module = None
        self._setup_read = None

        self._emoji_module = None
        self._append_to_file = None
        self._get_list_from_file = None
        self._pad_ref = None

        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Attempt to import all identified modules/functions from the repository.

        Import paths are aligned with analysis guidance:
        - setup.setup (module setup.py)
        - additional_resources.build_emoji_lexicon
        """
        ok = True

        try:
            import setup as setup_module  # full module path in source root
            self._setup_module = setup_module
            self._setup_read = getattr(setup_module, "read", None)
            if self._setup_read is None:
                ok = False
                self.import_errors.append(
                    "Imported module 'setup' but function 'read' was not found."
                )
        except Exception as e:
            ok = False
            self.import_errors.append(
                f"Failed to import module 'setup': {e}. Ensure source/setup.py exists and is readable."
            )

        try:
            from additional_resources import build_emoji_lexicon as emoji_module
            self._emoji_module = emoji_module
            self._append_to_file = getattr(emoji_module, "append_to_file", None)
            self._get_list_from_file = getattr(emoji_module, "get_list_from_file", None)
            self._pad_ref = getattr(emoji_module, "pad_ref", None)

            if self._append_to_file is None:
                ok = False
                self.import_errors.append(
                    "Imported 'additional_resources.build_emoji_lexicon' but function 'append_to_file' was not found."
                )
            if self._get_list_from_file is None:
                ok = False
                self.import_errors.append(
                    "Imported 'additional_resources.build_emoji_lexicon' but function 'get_list_from_file' was not found."
                )
            if self._pad_ref is None:
                ok = False
                self.import_errors.append(
                    "Imported 'additional_resources.build_emoji_lexicon' but function 'pad_ref' was not found."
                )
        except Exception as e:
            ok = False
            self.import_errors.append(
                "Failed to import module 'additional_resources.build_emoji_lexicon': "
                f"{e}. Ensure source/additional_resources/build_emoji_lexicon.py exists."
            )

        self.available = ok

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------
    def _status(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a unified response dictionary.

        Args:
            status: "success", "error", or "fallback".
            message: Human-readable operation result.
            data: Optional operation payload.
            error: Optional detailed error string.

        Returns:
            A unified dictionary with at least `status` and `message`.
        """
        result: Dict[str, Any] = {
            "status": status,
            "mode": self.mode,
            "message": message,
        }
        if data is not None:
            result["data"] = data
        if error is not None:
            result["error"] = error
        if self.import_errors:
            result["import_errors"] = list(self.import_errors)
        return result

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import diagnostics.

        Returns:
            dict: Unified status dict including availability and import details.
        """
        if self.available:
            return self._status(
                "success",
                "Adapter is ready in import mode.",
                data={"available": True},
            )
        return self._status(
            "fallback",
            "Adapter imports are incomplete. You can still call methods to receive actionable fallback guidance.",
            data={"available": False},
        )

    # -------------------------------------------------------------------------
    # setup.py wrapper methods
    # -------------------------------------------------------------------------
    def call_setup_read(self, fname: str) -> Dict[str, Any]:
        """
        Call setup.read(fname) from source/setup.py.

        This function typically reads repository-local files used by packaging.

        Args:
            fname: Relative filename/path expected by setup.read.

        Returns:
            dict: Unified status dict with file content on success.
        """
        if not self._setup_read:
            return self._status(
                "fallback",
                "Function 'setup.read' is unavailable.",
                error="Import failed. Verify source/setup.py and function definition 'read(fname)'.",
            )

        try:
            content = self._setup_read(fname)
            return self._status(
                "success",
                "setup.read executed successfully.",
                data={"fname": fname, "content": content},
            )
        except Exception as e:
            return self._status(
                "error",
                "Failed to execute setup.read.",
                error=f"{e}. Check that 'fname' is valid and readable from setup.py context.",
            )

    # -------------------------------------------------------------------------
    # additional_resources.build_emoji_lexicon wrapper methods
    # -------------------------------------------------------------------------
    def call_append_to_file(self, filename: str, line: str) -> Dict[str, Any]:
        """
        Call append_to_file(filename, line) from build_emoji_lexicon.

        Args:
            filename: Target file path for append operation.
            line: String line to append.

        Returns:
            dict: Unified status dict indicating write result.
        """
        if not self._append_to_file:
            return self._status(
                "fallback",
                "Function 'append_to_file' is unavailable.",
                error="Import failed. Verify source/additional_resources/build_emoji_lexicon.py.",
            )

        try:
            result = self._append_to_file(filename, line)
            return self._status(
                "success",
                "append_to_file executed successfully.",
                data={"filename": filename, "line": line, "result": result},
            )
        except Exception as e:
            return self._status(
                "error",
                "Failed to execute append_to_file.",
                error=f"{e}. Ensure target path is writable and inputs are valid strings.",
            )

    def call_get_list_from_file(self, filename: str) -> Dict[str, Any]:
        """
        Call get_list_from_file(filename) from build_emoji_lexicon.

        Args:
            filename: Source file path to parse into a list.

        Returns:
            dict: Unified status dict containing parsed list output.
        """
        if not self._get_list_from_file:
            return self._status(
                "fallback",
                "Function 'get_list_from_file' is unavailable.",
                error="Import failed. Verify source/additional_resources/build_emoji_lexicon.py.",
            )

        try:
            items = self._get_list_from_file(filename)
            return self._status(
                "success",
                "get_list_from_file executed successfully.",
                data={"filename": filename, "items": items},
            )
        except Exception as e:
            return self._status(
                "error",
                "Failed to execute get_list_from_file.",
                error=f"{e}. Ensure the file exists and is readable.",
            )

    def call_pad_ref(self, ref: Any, max_len: int) -> Dict[str, Any]:
        """
        Call pad_ref(ref, max_len) from build_emoji_lexicon.

        Args:
            ref: Input value/reference to pad.
            max_len: Desired maximum length for padding logic.

        Returns:
            dict: Unified status dict with padded output.
        """
        if not self._pad_ref:
            return self._status(
                "fallback",
                "Function 'pad_ref' is unavailable.",
                error="Import failed. Verify source/additional_resources/build_emoji_lexicon.py.",
            )

        try:
            padded = self._pad_ref(ref, max_len)
            return self._status(
                "success",
                "pad_ref executed successfully.",
                data={"ref": ref, "max_len": max_len, "result": padded},
            )
        except Exception as e:
            return self._status(
                "error",
                "Failed to execute pad_ref.",
                error=f"{e}. Ensure 'max_len' is an integer and 'ref' is compatible with function expectations.",
            )