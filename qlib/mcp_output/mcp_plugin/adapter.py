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
    Import-mode adapter for Microsoft Qlib repository integration.

    This adapter prioritizes direct module imports from local source code under the
    configured `source` directory and exposes stable wrapper methods with unified
    return format.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt to load core Qlib modules.

        Returns
        -------
        None
        """
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data or {}}

    def _err(self, message: str, action: str = "", details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if action:
            payload["action"] = action
        if details:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        """
        Load all identified modules/functions from analysis.

        Imported targets:
        - qlib.init
        - qlib.auto_init
        - qlib.cli.run (module)
        - qlib.cli.data (module)
        - qlib.contrib.rolling.__main__ (module)
        """
        try:
            import qlib  # full package path from source.qlib -> qlib
            self._imports["qlib"] = qlib
            self._imports["init"] = getattr(qlib, "init", None)
            self._imports["auto_init"] = getattr(qlib, "auto_init", None)
        except Exception as e:
            self._import_errors["qlib"] = str(e)

        try:
            import qlib.cli.run as qlib_cli_run
            self._imports["qlib.cli.run"] = qlib_cli_run
        except Exception as e:
            self._import_errors["qlib.cli.run"] = str(e)

        try:
            import qlib.cli.data as qlib_cli_data
            self._imports["qlib.cli.data"] = qlib_cli_data
        except Exception as e:
            self._import_errors["qlib.cli.data"] = str(e)

        try:
            import qlib.contrib.rolling.__main__ as qlib_contrib_rolling_main
            self._imports["qlib.contrib.rolling.__main__"] = qlib_contrib_rolling_main
        except Exception as e:
            self._import_errors["qlib.contrib.rolling.__main__"] = str(e)

    def health_check(self) -> Dict[str, Any]:
        """
        Report current adapter import status and actionable guidance.

        Returns
        -------
        Dict[str, Any]
            Unified status payload with loaded modules and import errors.
        """
        if self._import_errors:
            return self._err(
                message="Some Qlib modules failed to import.",
                action="Verify local source path, Python version compatibility, and install required dependencies like numpy, pandas, pyyaml, mlflow, ruamel.yaml, requests, python-dateutil.",
                details=str(self._import_errors),
            )
        return self._ok(
            data={"loaded": sorted(self._imports.keys())},
            message="All targeted Qlib modules imported successfully.",
        )

    # -------------------------------------------------------------------------
    # Core qlib function wrappers (identified in LLM analysis)
    # -------------------------------------------------------------------------
    def call_init(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call qlib.init(**kwargs) to bootstrap Qlib runtime.

        Parameters
        ----------
        **kwargs : Any
            Arbitrary keyword arguments forwarded to qlib.init. Typical options
            include provider URI, region, expression/data cache settings.

        Returns
        -------
        Dict[str, Any]
            Unified status payload.
        """
        fn = self._imports.get("init")
        if fn is None:
            return self._err(
                message="qlib.init is unavailable.",
                action="Ensure qlib is importable from local source and dependencies are installed.",
                details=self._import_errors.get("qlib"),
            )
        try:
            result = fn(**kwargs)
            return self._ok(data={"result": result}, message="qlib.init executed.")
        except Exception as e:
            return self._err(
                message="Failed to execute qlib.init.",
                action="Review init arguments and verify provider/data paths are valid.",
                details=str(e),
            )

    def call_auto_init(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Call qlib.auto_init(**kwargs) for automatic environment initialization.

        Parameters
        ----------
        **kwargs : Any
            Arbitrary keyword arguments forwarded to qlib.auto_init.

        Returns
        -------
        Dict[str, Any]
            Unified status payload.
        """
        fn = self._imports.get("auto_init")
        if fn is None:
            return self._err(
                message="qlib.auto_init is unavailable.",
                action="Ensure qlib is importable from local source.",
                details=self._import_errors.get("qlib"),
            )
        try:
            result = fn(**kwargs)
            return self._ok(data={"result": result}, message="qlib.auto_init executed.")
        except Exception as e:
            return self._err(
                message="Failed to execute qlib.auto_init.",
                action="Check local environment and any runtime config expected by auto_init.",
                details=str(e),
            )

    # -------------------------------------------------------------------------
    # Module-level execution helpers for identified CLI entry modules
    # -------------------------------------------------------------------------
    def module_qlib_cli_run(self) -> Dict[str, Any]:
        """
        Expose qlib.cli.run module status and callable entry candidates.

        Returns
        -------
        Dict[str, Any]
            Unified status payload with detected callables from qlib.cli.run.
        """
        mod = self._imports.get("qlib.cli.run")
        if mod is None:
            return self._err(
                message="qlib.cli.run module is unavailable.",
                action="Validate source checkout includes qlib/cli/run.py and required dependencies.",
                details=self._import_errors.get("qlib.cli.run"),
            )
        try:
            candidates = [n for n in ("main", "run", "cli") if hasattr(mod, n)]
            return self._ok(
                data={"module": "qlib.cli.run", "callables": candidates},
                message="qlib.cli.run module loaded.",
            )
        except Exception as e:
            return self._err(
                message="Failed to inspect qlib.cli.run module.",
                action="Check module integrity in local source tree.",
                details=str(e),
            )

    def module_qlib_cli_data(self) -> Dict[str, Any]:
        """
        Expose qlib.cli.data module status and callable entry candidates.

        Returns
        -------
        Dict[str, Any]
            Unified status payload with detected callables from qlib.cli.data.
        """
        mod = self._imports.get("qlib.cli.data")
        if mod is None:
            return self._err(
                message="qlib.cli.data module is unavailable.",
                action="Validate source checkout includes qlib/cli/data.py.",
                details=self._import_errors.get("qlib.cli.data"),
            )
        try:
            candidates = [n for n in ("main", "run", "cli") if hasattr(mod, n)]
            return self._ok(
                data={"module": "qlib.cli.data", "callables": candidates},
                message="qlib.cli.data module loaded.",
            )
        except Exception as e:
            return self._err(
                message="Failed to inspect qlib.cli.data module.",
                action="Check module integrity in local source tree.",
                details=str(e),
            )

    def module_qlib_contrib_rolling_main(self) -> Dict[str, Any]:
        """
        Expose qlib.contrib.rolling.__main__ module status and callable entry candidates.

        Returns
        -------
        Dict[str, Any]
            Unified status payload with detected callables from rolling entry module.
        """
        mod = self._imports.get("qlib.contrib.rolling.__main__")
        if mod is None:
            return self._err(
                message="qlib.contrib.rolling.__main__ module is unavailable.",
                action="Ensure qlib/contrib/rolling/__main__.py exists and dependencies are satisfied.",
                details=self._import_errors.get("qlib.contrib.rolling.__main__"),
            )
        try:
            candidates = [n for n in ("main", "run", "cli") if hasattr(mod, n)]
            return self._ok(
                data={"module": "qlib.contrib.rolling.__main__", "callables": candidates},
                message="qlib.contrib.rolling.__main__ module loaded.",
            )
        except Exception as e:
            return self._err(
                message="Failed to inspect qlib.contrib.rolling.__main__ module.",
                action="Check rolling module code and dependency setup.",
                details=str(e),
            )

    # -------------------------------------------------------------------------
    # Graceful fallback helpers
    # -------------------------------------------------------------------------
    def fallback_hint(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when import-mode is partially unavailable.

        Returns
        -------
        Dict[str, Any]
            Unified status payload with practical next steps.
        """
        if not self._import_errors:
            return self._ok(message="Import mode is healthy; fallback is not required.")
        return self._err(
            message="Import mode has unresolved module issues.",
            action=(
                "1) Confirm repository source is mounted under ../source; "
                "2) Install required dependencies; "
                "3) Retry health_check; "
                "4) If needed, execute workflows via CLI modules once imports succeed."
            ),
            details=str(self._import_errors),
        )