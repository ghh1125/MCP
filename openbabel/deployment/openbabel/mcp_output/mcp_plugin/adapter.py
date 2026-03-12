import os
import sys
import shutil
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the Open Babel repository.

    This adapter prefers Python import mode when local Open Babel Python bindings are available.
    It gracefully falls back to black-box CLI execution (`obabel`, optional `babel`) when imports
    are unavailable or incomplete.

    Unified return format for all public methods:
    {
        "status": "success" | "error",
        "mode": "import" | "blackbox",
        "data": ...,
        "message": "...",
        "error": "...",      # only on error
        "guidance": "...",   # actionable English-only guidance on failure
    }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self, obabel_path: Optional[str] = None, babel_path: Optional[str] = None) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._cli = {
            "obabel": obabel_path or shutil.which("obabel"),
            "babel": babel_path or shutil.which("babel"),
        }
        self._init_modules()

    def _ok(self, data: Any = None, message: str = "") -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "data": data,
            "message": message,
        }

    def _err(self, message: str, error: Optional[Exception] = None, guidance: str = "") -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(error) if error else "",
            "guidance": guidance or "Verify local Open Babel build/bindings or configure CLI executable paths.",
        }
        return payload

    def _init_modules(self) -> None:
        """
        Attempt to import Open Babel Python modules from local source/bindings.

        Full-path import attempts are used according to discovered repository layout.
        If all import attempts fail, adapter switches to blackbox mode.
        """
        import_errors: List[str] = []

        try:
            import scripts.python.openbabel.pybel as pybel  # type: ignore
            self._imports["scripts.python.openbabel.pybel"] = pybel
        except Exception as e:
            import_errors.append(f"scripts.python.openbabel.pybel import failed: {e}")

        try:
            import openbabel  # type: ignore
            self._imports["openbabel"] = openbabel
        except Exception as e:
            import_errors.append(f"openbabel import failed: {e}")

        if not self._imports:
            self.mode = "blackbox"
            self._import_error_summary = "; ".join(import_errors)
        else:
            self._import_error_summary = ""

    # -------------------------------------------------------------------------
    # Health and capability inspection
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter health, active mode, import availability, and CLI availability.
        """
        data = {
            "active_mode": self.mode,
            "imports_available": list(self._imports.keys()),
            "cli_available": {
                "obabel": self._cli.get("obabel"),
                "babel": self._cli.get("babel"),
            },
            "import_error_summary": self._import_error_summary,
        }
        if self.mode == "import":
            return self._ok(data=data, message="Import mode is active.")
        return self._ok(
            data=data,
            message="Fallback blackbox mode is active because Python imports are unavailable.",
        )

    def set_cli_paths(self, obabel_path: Optional[str] = None, babel_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Set or update explicit CLI executable paths.

        Parameters:
        - obabel_path: Absolute/relative path to obabel executable.
        - babel_path: Absolute/relative path to babel executable (optional legacy fallback).
        """
        if obabel_path:
            self._cli["obabel"] = obabel_path
        if babel_path:
            self._cli["babel"] = babel_path
        return self._ok(
            data={"cli": self._cli},
            message="CLI paths updated.",
        )

    # -------------------------------------------------------------------------
    # Core command execution (blackbox)
    # -------------------------------------------------------------------------
    def _run_cli(self, args: List[str], timeout: int = 120) -> Dict[str, Any]:
        exe = self._cli.get("obabel") or self._cli.get("babel")
        if not exe:
            return self._err(
                message="No Open Babel CLI executable found.",
                guidance="Install/build Open Babel and ensure 'obabel' is on PATH, or call set_cli_paths().",
            )
        try:
            proc = subprocess.run(
                [exe] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            if proc.returncode != 0:
                return self._err(
                    message="Open Babel CLI command failed.",
                    guidance="Check input format flags, file paths, and Open Babel installation.",
                    error=Exception(proc.stderr.strip() or f"Exit code {proc.returncode}"),
                )
            return self._ok(
                data={"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode},
                message="CLI command executed successfully.",
            )
        except subprocess.TimeoutExpired as e:
            return self._err(
                message="Open Babel CLI command timed out.",
                error=e,
                guidance="Use smaller inputs, simpler options, or increase timeout.",
            )
        except Exception as e:
            return self._err(
                message="Unexpected error while executing Open Babel CLI command.",
                error=e,
                guidance="Verify executable permissions and command arguments.",
            )

    # -------------------------------------------------------------------------
    # obabel/babel command wrappers from analysis
    # -------------------------------------------------------------------------
    def call_obabel(self, args: List[str], timeout: int = 120) -> Dict[str, Any]:
        """
        Execute Open Babel main CLI command (`obabel`) with provided arguments.

        Parameters:
        - args: List of raw Open Babel CLI arguments, e.g. ["-ismi", "in.smi", "-omol", "-O", "out.mol"].
        - timeout: Max execution time in seconds.

        Returns:
        - Unified status dictionary with stdout/stderr/return code.
        """
        return self._run_cli(args=args, timeout=timeout)

    def call_babel(self, args: List[str], timeout: int = 120) -> Dict[str, Any]:
        """
        Execute legacy/compat Open Babel CLI command (`babel`) if available, else fallback to `obabel`.

        Parameters:
        - args: List of raw CLI arguments.
        - timeout: Max execution time in seconds.
        """
        original_obabel = self._cli.get("obabel")
        try:
            if self._cli.get("babel"):
                self._cli["obabel"] = self._cli["babel"]
            return self._run_cli(args=args, timeout=timeout)
        finally:
            self._cli["obabel"] = original_obabel

    # -------------------------------------------------------------------------
    # Import-mode helpers (pybel/openbabel bindings)
    # -------------------------------------------------------------------------
    def create_pybel_molecule_from_string(self, fmt: str, text: str) -> Dict[str, Any]:
        """
        Create a Pybel molecule from in-memory string content.

        Parameters:
        - fmt: Input format token (e.g. "smi", "mol", "sdf", "inchi").
        - text: Molecule text in the given format.
        """
        if "scripts.python.openbabel.pybel" not in self._imports:
            return self._err(
                message="Pybel module is not available in import mode.",
                guidance="Build Open Babel Python bindings or use call_obabel() fallback.",
            )
        try:
            pybel = self._imports["scripts.python.openbabel.pybel"]
            mol = pybel.readstring(fmt, text)
            return self._ok(data={"molecule": mol}, message="Pybel molecule created from string.")
        except Exception as e:
            return self._err(
                message="Failed to create Pybel molecule from string.",
                error=e,
                guidance="Validate format token and molecular input content.",
            )

    def call_pybel_readfile(self, fmt: str, filename: str) -> Dict[str, Any]:
        """
        Read molecules from file via pybel.readfile and return count (stream consumed).

        Parameters:
        - fmt: Input format token.
        - filename: Path to input file.
        """
        if "scripts.python.openbabel.pybel" not in self._imports:
            return self._err(
                message="Pybel module is not available.",
                guidance="Use obabel CLI fallback or build Python bindings.",
            )
        try:
            pybel = self._imports["scripts.python.openbabel.pybel"]
            mols = list(pybel.readfile(fmt, filename))
            return self._ok(data={"count": len(mols), "molecules": mols}, message="Molecules loaded successfully.")
        except Exception as e:
            return self._err(
                message="Failed to read molecules from file with Pybel.",
                error=e,
                guidance="Verify file path, permissions, and matching input format.",
            )

    def call_pybel_write(self, input_format: str, output_format: str, text: str) -> Dict[str, Any]:
        """
        Convert a molecule text between formats using Pybel in import mode.

        Parameters:
        - input_format: Input format token.
        - output_format: Output format token.
        - text: Input molecular content.
        """
        created = self.create_pybel_molecule_from_string(input_format, text)
        if created["status"] != "success":
            return created
        try:
            mol = created["data"]["molecule"]
            converted = mol.write(output_format)
            return self._ok(data={"output": converted}, message="Format conversion completed in import mode.")
        except Exception as e:
            return self._err(
                message="Failed to convert molecule with Pybel.",
                error=e,
                guidance="Confirm requested output format is supported by your Open Babel build.",
            )