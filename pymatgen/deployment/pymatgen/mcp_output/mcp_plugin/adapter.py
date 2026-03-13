import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for pymatgen.

    This adapter prioritizes direct module import usage and provides a graceful
    CLI fallback mode when import is unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._bootstrap()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "ok") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        details = str(error) if error else ""
        guidance = (
            "Ensure the repository source is available at '../source' and dependencies are installed. "
            "If import mode is unavailable, use CLI fallback via the `pmg` command."
        )
        return {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": details,
            "guidance": guidance,
        }

    def _bootstrap(self) -> None:
        targets = {
            "pmg_cli": "pymatgen.cli.pmg",
            "pmg_analyze": "pymatgen.cli.pmg_analyze",
            "pmg_plot": "pymatgen.cli.pmg_plot",
            "pmg_structure": "pymatgen.cli.pmg_structure",
            "pmg_config": "pymatgen.cli.pmg_config",
        }
        for key, mod in targets.items():
            try:
                self._imports[key] = importlib.import_module(mod)
            except Exception as e:
                self._import_errors[key] = f"{type(e).__name__}: {e}"

        if not self._imports:
            self.mode = "cli"

    def _safe_call(self, func: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                "Function call failed. Verify parameters and runtime dependencies.",
                e,
            )

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Get adapter health information.

        Returns:
            dict: Unified status dictionary including mode, loaded modules, and import errors.
        """
        return self._ok(
            {
                "loaded_modules": list(self._imports.keys()),
                "import_errors": self._import_errors,
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # CLI module instances (identified modules from analysis)
    # -------------------------------------------------------------------------
    def instance_pmg_cli(self) -> Dict[str, Any]:
        """
        Return imported pymatgen main CLI module instance.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        mod = self._imports.get("pmg_cli")
        if mod is None:
            return self._err("pymatgen.cli.pmg is not available in import mode.")
        return self._ok({"module": mod}, "pymatgen.cli.pmg loaded")

    def instance_pmg_analyze(self) -> Dict[str, Any]:
        """
        Return imported pymatgen analyze CLI helper module instance.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        mod = self._imports.get("pmg_analyze")
        if mod is None:
            return self._err("pymatgen.cli.pmg_analyze is not available in import mode.")
        return self._ok({"module": mod}, "pymatgen.cli.pmg_analyze loaded")

    def instance_pmg_plot(self) -> Dict[str, Any]:
        """
        Return imported pymatgen plot CLI helper module instance.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        mod = self._imports.get("pmg_plot")
        if mod is None:
            return self._err("pymatgen.cli.pmg_plot is not available in import mode.")
        return self._ok({"module": mod}, "pymatgen.cli.pmg_plot loaded")

    def instance_pmg_structure(self) -> Dict[str, Any]:
        """
        Return imported pymatgen structure CLI helper module instance.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        mod = self._imports.get("pmg_structure")
        if mod is None:
            return self._err("pymatgen.cli.pmg_structure is not available in import mode.")
        return self._ok({"module": mod}, "pymatgen.cli.pmg_structure loaded")

    def instance_pmg_config(self) -> Dict[str, Any]:
        """
        Return imported pymatgen config CLI helper module instance.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        mod = self._imports.get("pmg_config")
        if mod is None:
            return self._err("pymatgen.cli.pmg_config is not available in import mode.")
        return self._ok({"module": mod}, "pymatgen.cli.pmg_config loaded")

    # -------------------------------------------------------------------------
    # Callable wrappers for identified CLI-oriented entry behaviors
    # -------------------------------------------------------------------------
    def call_pmg_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Invoke pymatgen main CLI entry logic when available.

        Parameters:
            argv (list[str] | None): Optional argument vector for CLI-style invocation.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        mod = self._imports.get("pmg_cli")
        if mod is None:
            return self._err(
                "Import mode unavailable for pymatgen.cli.pmg. Use CLI fallback: `pmg <subcommand>`."
            )

        candidate_names = ["main", "run", "cli"]
        for name in candidate_names:
            fn = getattr(mod, name, None)
            if callable(fn):
                if argv is None:
                    return self._safe_call(fn)
                return self._safe_call(fn, argv)

        return self._err(
            "No callable entrypoint found in pymatgen.cli.pmg. Try running external CLI command `pmg`."
        )

    def call_pmg_analyze(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke analyze helper entrypoint if exposed by pymatgen.cli.pmg_analyze.

        Parameters:
            *args: Positional arguments passed to discovered callable.
            **kwargs: Keyword arguments passed to discovered callable.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        mod = self._imports.get("pmg_analyze")
        if mod is None:
            return self._err(
                "Import mode unavailable for pymatgen.cli.pmg_analyze. Use CLI fallback: `pmg analyze`."
            )
        for name in ["main", "analyze", "run"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._err("No callable analyze entrypoint found in pymatgen.cli.pmg_analyze.")

    def call_pmg_plot(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke plot helper entrypoint if exposed by pymatgen.cli.pmg_plot.

        Parameters:
            *args: Positional arguments passed to discovered callable.
            **kwargs: Keyword arguments passed to discovered callable.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        mod = self._imports.get("pmg_plot")
        if mod is None:
            return self._err(
                "Import mode unavailable for pymatgen.cli.pmg_plot. Use CLI fallback: `pmg plot`."
            )
        for name in ["main", "plot", "run"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._err("No callable plot entrypoint found in pymatgen.cli.pmg_plot.")

    def call_pmg_structure(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke structure helper entrypoint if exposed by pymatgen.cli.pmg_structure.

        Parameters:
            *args: Positional arguments passed to discovered callable.
            **kwargs: Keyword arguments passed to discovered callable.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        mod = self._imports.get("pmg_structure")
        if mod is None:
            return self._err(
                "Import mode unavailable for pymatgen.cli.pmg_structure. Use CLI fallback: `pmg structure`."
            )
        for name in ["main", "structure", "run"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._err("No callable structure entrypoint found in pymatgen.cli.pmg_structure.")

    def call_pmg_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke config helper entrypoint if exposed by pymatgen.cli.pmg_config.

        Parameters:
            *args: Positional arguments passed to discovered callable.
            **kwargs: Keyword arguments passed to discovered callable.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        mod = self._imports.get("pmg_config")
        if mod is None:
            return self._err(
                "Import mode unavailable for pymatgen.cli.pmg_config. Use CLI fallback: `pmg config`."
            )
        for name in ["main", "configure", "run"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, *args, **kwargs)
        return self._err("No callable config entrypoint found in pymatgen.cli.pmg_config.")