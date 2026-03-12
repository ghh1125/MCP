import os
import sys
import traceback
import runpy
import shlex
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for repository: YanLab-Westlake/SPM

    This adapter attempts to use direct import mode first. Based on the repository scan,
    no formal package exports were discovered and the practical entry appears to be:

        python scripts/SequencePatternMatching.py

    Therefore, this adapter provides:
    1) Import-attempt pathway for scripts.SequencePatternMatching
    2) Graceful fallback to script execution (CLI-style)
    3) Unified status dictionary outputs for MCP plugin integration
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt to load repository modules.

        Attributes:
            mode (str): Adapter mode, fixed to "import".
            module_sequence_pattern_matching (Any): Imported module object if available.
            import_errors (List[str]): Collected import error messages.
        """
        self.mode = "import"
        self.module_sequence_pattern_matching = None
        self.import_errors: List[str] = []
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Attempt to import known repository modules using full path discovered by analysis.
        """
        try:
            import scripts.SequencePatternMatching as sequence_pattern_matching_module
            self.module_sequence_pattern_matching = sequence_pattern_matching_module
        except Exception as exc:
            self.import_errors.append(
                f"Failed to import scripts.SequencePatternMatching. "
                f"Please verify source layout and dependencies. Details: {exc}"
            )

    # -------------------------------------------------------------------------
    # Unified response helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if details:
            payload["details"] = details
        return payload

    # -------------------------------------------------------------------------
    # Capability and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and module import state.

        Returns:
            dict: Unified status dictionary with import diagnostics.
        """
        imported = self.module_sequence_pattern_matching is not None
        return self._ok(
            data={
                "import_ready": imported,
                "import_errors": self.import_errors,
                "available_module": "scripts.SequencePatternMatching" if imported else None,
                "recommended_entry": "python scripts/SequencePatternMatching.py",
            },
            message="Adapter health check completed.",
        )

    def get_repository_summary(self) -> Dict[str, Any]:
        """
        Return repository analysis summary embedded in adapter for runtime introspection.

        Returns:
            dict: Unified status dictionary containing summarized metadata.
        """
        return self._ok(
            data={
                "repository_url": "https://github.com/YanLab-Westlake/SPM",
                "import_feasibility": 0.35,
                "intrusiveness_risk": "medium",
                "complexity": "simple",
                "primary_strategy": "import",
                "fallback_strategy": "cli",
                "known_entry_command": "python scripts/SequencePatternMatching.py",
                "known_files": [
                    "README.md",
                    "output/test1_ranked.txt",
                    "scripts/SequencePatternMatching.py",
                ],
            },
            message="Repository summary loaded.",
        )

    # -------------------------------------------------------------------------
    # Import-mode execution methods (module-level, best-effort)
    # -------------------------------------------------------------------------
    def run_sequence_pattern_matching_module(
        self,
        init_globals: Optional[Dict[str, Any]] = None,
        run_name: str = "__main__",
    ) -> Dict[str, Any]:
        """
        Execute scripts.SequencePatternMatching through Python module runner semantics.

        Parameters:
            init_globals (dict, optional): Initial globals passed into runpy.run_module.
            run_name (str): Execution name, default "__main__".

        Returns:
            dict: Unified status dictionary with execution results or actionable errors.
        """
        try:
            result_globals = runpy.run_module(
                "scripts.SequencePatternMatching",
                init_globals=init_globals,
                run_name=run_name,
            )
            return self._ok(
                data={
                    "execution": "run_module",
                    "module": "scripts.SequencePatternMatching",
                    "result_keys": sorted(list(result_globals.keys()))[:50],
                },
                message="Module executed successfully via import mode.",
            )
        except Exception as exc:
            return self._error(
                "Module execution failed in import mode. Use CLI fallback with explicit script path and arguments.",
                details=f"{exc}\n{traceback.format_exc()}",
            )

    def call_module_attribute(
        self,
        attribute_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically call an attribute from scripts.SequencePatternMatching if callable.

        This method is provided because static analysis did not expose explicit function/class
        signatures from the scanned result. It allows full utilization of discovered module
        functionality when attributes are known at runtime.

        Parameters:
            attribute_name (str): Name of module attribute to invoke.
            args (list, optional): Positional arguments for the callable.
            kwargs (dict, optional): Keyword arguments for the callable.

        Returns:
            dict: Unified status dictionary with call results or guidance.
        """
        args = args or []
        kwargs = kwargs or {}

        if self.module_sequence_pattern_matching is None:
            return self._error(
                "Import mode module is unavailable. Run health_check and then use CLI fallback.",
                details="scripts.SequencePatternMatching failed to import.",
            )

        try:
            if not hasattr(self.module_sequence_pattern_matching, attribute_name):
                return self._error(
                    f"Attribute '{attribute_name}' not found in scripts.SequencePatternMatching.",
                    details="Check exact attribute name in scripts/SequencePatternMatching.py.",
                )

            target = getattr(self.module_sequence_pattern_matching, attribute_name)
            if not callable(target):
                return self._ok(
                    data={"attribute_name": attribute_name, "value": target},
                    message=f"Attribute '{attribute_name}' retrieved successfully (not callable).",
                )

            result = target(*args, **kwargs)
            return self._ok(
                data={"attribute_name": attribute_name, "result": result},
                message=f"Callable attribute '{attribute_name}' executed successfully.",
            )
        except Exception as exc:
            return self._error(
                f"Failed to execute attribute '{attribute_name}'.",
                details=f"{exc}\n{traceback.format_exc()}",
            )

    # -------------------------------------------------------------------------
    # CLI fallback methods
    # -------------------------------------------------------------------------
    def run_cli_fallback(
        self,
        script_relative_path: str = os.path.join("scripts", "SequencePatternMatching.py"),
        script_args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute repository script via subprocess as a fallback when import mode is limited.

        Parameters:
            script_relative_path (str): Script path relative to source directory.
            script_args (list[str], optional): CLI arguments passed to script.
            cwd (str, optional): Working directory for subprocess.
            timeout (int, optional): Process timeout in seconds.

        Returns:
            dict: Unified status dictionary with stdout/stderr and return code.
        """
        script_args = script_args or []
        script_abs_path = os.path.join(source_path, script_relative_path)

        if not os.path.exists(script_abs_path):
            return self._error(
                "CLI fallback script was not found.",
                details=(
                    f"Expected path: {script_abs_path}. "
                    "Ensure repository files are correctly mounted under source/."
                ),
            )

        cmd = [sys.executable, script_abs_path] + script_args
        try:
            completed = subprocess.run(
                cmd,
                cwd=cwd or source_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            status = "success" if completed.returncode == 0 else "error"
            return {
                "status": status,
                "mode": self.mode,
                "message": "CLI fallback execution completed." if status == "success" else "CLI fallback execution failed.",
                "command": cmd,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except subprocess.TimeoutExpired as exc:
            return self._error(
                "CLI fallback timed out.",
                details=f"Increase timeout value or reduce input size. Details: {exc}",
            )
        except Exception as exc:
            return self._error(
                "CLI fallback execution encountered an unexpected error.",
                details=f"{exc}\n{traceback.format_exc()}",
            )

    def run_cli_command_string(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Run an arbitrary CLI command string safely tokenized with shlex.

        Parameters:
            command (str): Raw command string, e.g. "python scripts/SequencePatternMatching.py".
            cwd (str, optional): Working directory.
            timeout (int, optional): Timeout in seconds.

        Returns:
            dict: Unified status dictionary with process output.
        """
        try:
            parts = shlex.split(command)
            if not parts:
                return self._error("Empty command string provided.", details="Provide a valid command.")
            completed = subprocess.run(
                parts,
                cwd=cwd or source_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            status = "success" if completed.returncode == 0 else "error"
            return {
                "status": status,
                "mode": self.mode,
                "message": "Command executed." if status == "success" else "Command failed.",
                "command": parts,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except Exception as exc:
            return self._error(
                "Failed to run command string.",
                details=f"{exc}\n{traceback.format_exc()}",
            )