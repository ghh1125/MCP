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
    MCP import-mode adapter for mne-python.

    This adapter prioritizes direct in-repo imports and provides graceful fallback
    guidance when imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._commands: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "OK") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            out["guidance"] = guidance
        return out

    def _import_module(self, dotted_path: str, alias: str) -> None:
        try:
            self._modules[alias] = __import__(dotted_path, fromlist=["*"])
        except Exception as e:
            self._modules[alias] = None
            if self._import_error is None:
                self._import_error = str(e)

    def _initialize_imports(self) -> None:
        # Core package
        self._import_module("mne", "mne")

        # CLI command modules identified by analysis
        self._import_module("mne.commands.mne_browse_raw", "cmd_browse_raw")
        self._import_module("mne.commands.mne_report", "cmd_report")
        self._import_module("mne.commands.mne_sys_info", "cmd_sys_info")
        self._import_module("mne.commands.mne_show_fiff", "cmd_show_fiff")
        self._import_module("mne.commands.mne_what", "cmd_what")

        # Track command callables where possible
        for alias in ["cmd_browse_raw", "cmd_report", "cmd_sys_info", "cmd_show_fiff", "cmd_what"]:
            mod = self._modules.get(alias)
            self._commands[alias] = getattr(mod, "run", None) if mod else None

    def _check_available(self, alias: str, feature_name: str) -> Optional[Dict[str, Any]]:
        if self._modules.get(alias) is None:
            return self._err(
                f"{feature_name} is unavailable because module import failed.",
                guidance=(
                    "Ensure the repository source tree exists under the configured source path "
                    "and that required dependencies are installed."
                ),
            )
        return None

    # -------------------------------------------------------------------------
    # Status / diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        available = {k: v is not None for k, v in self._modules.items()}
        if all(available.values()):
            return self._ok({"available_modules": available}, "All modules imported successfully.")
        return self._err(
            "Some modules could not be imported.",
            guidance=f"Import diagnostics: {self._import_error or 'Unknown import error.'}",
        )

    def get_dependency_hints(self) -> Dict[str, Any]:
        """
        Return dependency hints derived from analysis.
        """
        return self._ok(
            {
                "required": ["numpy", "scipy", "matplotlib", "packaging", "pooch", "jinja2", "tqdm"],
                "optional": [
                    "scikit-learn", "pandas", "h5py", "nibabel", "pyvista",
                    "PyQt5/PySide6", "numba", "joblib", "dipy", "mne-qt-browser",
                    "neo", "pyxdf", "eeglabio",
                ],
            },
            "Dependency hints generated from repository analysis.",
        )

    # -------------------------------------------------------------------------
    # Core mne module methods
    # -------------------------------------------------------------------------
    def create_info(self, ch_names, sfreq, ch_types="misc", **kwargs) -> Dict[str, Any]:
        """
        Create an MNE Info object via mne.create_info.

        Parameters:
        - ch_names: list of channel names.
        - sfreq: sampling frequency.
        - ch_types: channel type(s).
        - kwargs: forwarded to mne.create_info.

        Returns:
        - Unified status dictionary with created info in `result`.
        """
        unavailable = self._check_available("mne", "mne.create_info")
        if unavailable:
            return unavailable
        try:
            result = self._modules["mne"].create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types, **kwargs)
            return self._ok({"result": result}, "Info object created.")
        except Exception as e:
            return self._err(
                f"Failed to create Info object: {e}",
                guidance="Validate channel names, sfreq type, and channel type definitions.",
            )

    def instantiate_raw_array(self, data, info, first_samp=0, copy="auto", verbose=None) -> Dict[str, Any]:
        """
        Instantiate mne.io.RawArray.

        Parameters:
        - data: ndarray, shape (n_channels, n_times).
        - info: mne.Info object.
        - first_samp: first sample index.
        - copy: copy behavior.
        - verbose: MNE verbosity.

        Returns:
        - Unified status dictionary with RawArray instance in `result`.
        """
        unavailable = self._check_available("mne", "mne.io.RawArray")
        if unavailable:
            return unavailable
        try:
            raw = self._modules["mne"].io.RawArray(data=data, info=info, first_samp=first_samp, copy=copy, verbose=verbose)
            return self._ok({"result": raw}, "RawArray instance created.")
        except Exception as e:
            return self._err(
                f"Failed to instantiate RawArray: {e}",
                guidance="Ensure data is 2D numeric and matches Info channel count.",
            )

    def call_read_raw(self, fname, **kwargs) -> Dict[str, Any]:
        """
        Call mne.io.read_raw for auto-detected format reading.

        Parameters:
        - fname: input file path.
        - kwargs: forwarded to mne.io.read_raw.

        Returns:
        - Unified status dictionary with raw object in `result`.
        """
        unavailable = self._check_available("mne", "mne.io.read_raw")
        if unavailable:
            return unavailable
        try:
            raw = self._modules["mne"].io.read_raw(fname, **kwargs)
            return self._ok({"result": raw}, "Raw file loaded.")
        except Exception as e:
            return self._err(
                f"Failed to read raw data: {e}",
                guidance="Confirm file path, format support, and related optional dependencies.",
            )

    # -------------------------------------------------------------------------
    # CLI wrappers from mne/commands/*
    # -------------------------------------------------------------------------
    def call_mne_browse_raw(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute mne browse_raw command module run().

        Parameters:
        - argv: optional command-style argument list.

        Returns:
        - Unified status dictionary with command return value if available.
        """
        unavailable = self._check_available("cmd_browse_raw", "mne browse_raw")
        if unavailable:
            return unavailable
        try:
            run = self._commands.get("cmd_browse_raw")
            if run is None:
                return self._err(
                    "browse_raw command entrypoint not found.",
                    guidance="Inspect mne.commands.mne_browse_raw for available callable entrypoints.",
                )
            out = run(argv or [])
            return self._ok({"result": out}, "mne browse_raw executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute mne browse_raw: {e}",
                guidance="Provide valid command arguments and ensure GUI backend dependencies are installed.",
            )

    def call_mne_report(self, argv: Optional[list] = None) -> Dict[str, Any]:
        unavailable = self._check_available("cmd_report", "mne report")
        if unavailable:
            return unavailable
        try:
            run = self._commands.get("cmd_report")
            if run is None:
                return self._err("report command entrypoint not found.", guidance="Check mne.commands.mne_report module.")
            out = run(argv or [])
            return self._ok({"result": out}, "mne report executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute mne report: {e}",
                guidance="Verify report arguments and paths are correct.",
            )

    def call_mne_sys_info(self, argv: Optional[list] = None) -> Dict[str, Any]:
        unavailable = self._check_available("cmd_sys_info", "mne sys_info")
        if unavailable:
            return unavailable
        try:
            run = self._commands.get("cmd_sys_info")
            if run is None:
                return self._err("sys_info command entrypoint not found.", guidance="Check mne.commands.mne_sys_info module.")
            out = run(argv or [])
            return self._ok({"result": out}, "mne sys_info executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute mne sys_info: {e}",
                guidance="Try running with no arguments to print environment diagnostics.",
            )

    def call_mne_show_fiff(self, argv: Optional[list] = None) -> Dict[str, Any]:
        unavailable = self._check_available("cmd_show_fiff", "mne show_fiff")
        if unavailable:
            return unavailable
        try:
            run = self._commands.get("cmd_show_fiff")
            if run is None:
                return self._err("show_fiff command entrypoint not found.", guidance="Check mne.commands.mne_show_fiff module.")
            out = run(argv or [])
            return self._ok({"result": out}, "mne show_fiff executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute mne show_fiff: {e}",
                guidance="Ensure the FIFF file exists and is readable.",
            )

    def call_mne_what(self, argv: Optional[list] = None) -> Dict[str, Any]:
        unavailable = self._check_available("cmd_what", "mne what")
        if unavailable:
            return unavailable
        try:
            run = self._commands.get("cmd_what")
            if run is None:
                return self._err("what command entrypoint not found.", guidance="Check mne.commands.mne_what module.")
            out = run(argv or [])
            return self._ok({"result": out}, "mne what executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute mne what: {e}",
                guidance="Pass a valid file path to identify file type.",
            )

    # -------------------------------------------------------------------------
    # Unified dispatcher
    # -------------------------------------------------------------------------
    def call(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Generic dispatcher for adapter operations.

        Supported operations:
        - health_check
        - get_dependency_hints
        - create_info
        - instantiate_raw_array
        - call_read_raw
        - call_mne_browse_raw
        - call_mne_report
        - call_mne_sys_info
        - call_mne_show_fiff
        - call_mne_what
        """
        mapping = {
            "health_check": self.health_check,
            "get_dependency_hints": self.get_dependency_hints,
            "create_info": self.create_info,
            "instantiate_raw_array": self.instantiate_raw_array,
            "call_read_raw": self.call_read_raw,
            "call_mne_browse_raw": self.call_mne_browse_raw,
            "call_mne_report": self.call_mne_report,
            "call_mne_sys_info": self.call_mne_sys_info,
            "call_mne_show_fiff": self.call_mne_show_fiff,
            "call_mne_what": self.call_mne_what,
        }
        fn = mapping.get(operation)
        if fn is None:
            return self._err(
                f"Unknown operation: {operation}",
                guidance=f"Use one of: {', '.join(mapping.keys())}",
            )
        try:
            return fn(**kwargs)
        except TypeError as e:
            return self._err(
                f"Invalid parameters for operation '{operation}': {e}",
                guidance="Check required parameters and parameter names.",
            )