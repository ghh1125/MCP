import os
import sys
from typing import Any, Callable, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the Sage repository.

    This adapter prioritizes import-based execution and gracefully falls back when
    Sage runtime dependencies are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._available: Dict[str, bool] = {}
        self._errors: Dict[str, str] = {}
        self._modules: Dict[str, Any] = {}
        self._initialize_imports()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "ok", "mode": self.mode}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            result["guidance"] = guidance
        return result

    def _call(self, key: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if not self._available.get(key, False):
            return self._fail(
                f"Feature '{key}' is unavailable in current runtime.",
                guidance=self._errors.get(
                    key,
                    "Ensure Sage is installed and runtime dependencies are available.",
                ),
            )
        try:
            value = fn(*args, **kwargs)
            return self._ok({"result": value})
        except Exception as exc:
            return self._fail(
                f"Execution failed for '{key}': {exc}",
                guidance="Check input arguments and verify the Sage runtime environment.",
            )

    def _initialize_imports(self) -> None:
        self._import_sage_cli()
        self._import_sage_docbuild()
        self._import_sage_bootstrap()

    def _mark_import(self, key: str, ok: bool, module: Any = None, err: Optional[str] = None) -> None:
        self._available[key] = ok
        if ok and module is not None:
            self._modules[key] = module
        if not ok and err:
            self._errors[key] = err

    # ---------------------------------------------------------------------
    # Imports: CLI
    # ---------------------------------------------------------------------
    def _import_sage_cli(self) -> None:
        try:
            import sage.cli.__main__ as m  # full package path
            self._mark_import("sage_cli_main", True, m)
        except Exception as exc:
            self._mark_import(
                "sage_cli_main",
                False,
                err=f"Cannot import sage.cli.__main__: {exc}. Install full Sage runtime.",
            )

        for key, modpath in [
            ("sage_cli_eval_cmd", "sage.cli.eval_cmd"),
            ("sage_cli_run_file_cmd", "sage.cli.run_file_cmd"),
            ("sage_cli_notebook_cmd", "sage.cli.notebook_cmd"),
            ("sage_cli_version_cmd", "sage.cli.version_cmd"),
            ("sage_cli_interactive_shell_cmd", "sage.cli.interactive_shell_cmd"),
            ("sage_cli_options", "sage.cli.options"),
        ]:
            try:
                module = __import__(modpath, fromlist=["*"])
                self._mark_import(key, True, module)
            except Exception as exc:
                self._mark_import(
                    key,
                    False,
                    err=f"Cannot import {modpath}: {exc}. Verify Sage CLI dependencies.",
                )

    # ---------------------------------------------------------------------
    # Imports: docbuild
    # ---------------------------------------------------------------------
    def _import_sage_docbuild(self) -> None:
        try:
            import sage_docbuild.__main__ as m  # full package path
            self._mark_import("sage_docbuild_main", True, m)
        except Exception as exc:
            self._mark_import(
                "sage_docbuild_main",
                False,
                err=f"Cannot import sage_docbuild.__main__: {exc}. Install docbuild dependencies (Sphinx stack).",
            )

    # ---------------------------------------------------------------------
    # Imports: bootstrap
    # ---------------------------------------------------------------------
    def _import_sage_bootstrap(self) -> None:
        try:
            import build.sage_bootstrap.cmdline as m  # full package path
            self._mark_import("sage_bootstrap_cmdline", True, m)
        except Exception as exc:
            self._mark_import(
                "sage_bootstrap_cmdline",
                False,
                err=f"Cannot import build.sage_bootstrap.cmdline: {exc}. Use source checkout with build tooling.",
            )

    # ---------------------------------------------------------------------
    # Adapter status and diagnostics
    # ---------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload with available modules and import errors.
        """
        return self._ok(
            {
                "available": self._available,
                "errors": self._errors,
            }
        )

    # ---------------------------------------------------------------------
    # CLI command-family wrappers
    # ---------------------------------------------------------------------
    def run_sage_cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute the Sage CLI entry module.

        Parameters:
            argv (list, optional): Command arguments to pass when supported by module API.

        Returns:
            dict: status/result or status/error payload.
        """
        mod = self._modules.get("sage_cli_main")
        if mod is None:
            return self._fail(
                "sage.cli.__main__ is not available.",
                guidance=self._errors.get("sage_cli_main"),
            )

        # Flexible invocation: try common entrypoints.
        for attr in ("main", "run", "cli"):
            fn = getattr(mod, attr, None)
            if callable(fn):
                if argv is None:
                    return self._call("sage_cli_main", fn)
                return self._call("sage_cli_main", fn, argv)

        return self._fail(
            "No callable entrypoint found in sage.cli.__main__.",
            guidance="Inspect module for available callable entry function.",
        )

    def run_eval(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage eval command pathway.

        Parameters:
            *args: Positional arguments for eval command API.
            **kwargs: Keyword arguments for eval command API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_eval_cmd", *args, **kwargs)

    def run_file(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage run-file command pathway.

        Parameters:
            *args: Positional arguments for run-file command API.
            **kwargs: Keyword arguments for run-file command API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_run_file_cmd", *args, **kwargs)

    def run_notebook(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage notebook command pathway.

        Parameters:
            *args: Positional arguments for notebook command API.
            **kwargs: Keyword arguments for notebook command API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_notebook_cmd", *args, **kwargs)

    def run_version(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage version command pathway.

        Parameters:
            *args: Positional arguments for version command API.
            **kwargs: Keyword arguments for version command API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_version_cmd", *args, **kwargs)

    def run_interactive_shell(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage interactive shell command pathway.

        Parameters:
            *args: Positional arguments for interactive shell command API.
            **kwargs: Keyword arguments for interactive shell command API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_interactive_shell_cmd", *args, **kwargs)

    def run_cli_options(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute Sage CLI options helper pathway.

        Parameters:
            *args: Positional arguments for options API.
            **kwargs: Keyword arguments for options API.

        Returns:
            dict: status/result or status/error.
        """
        return self._run_module_entry("sage_cli_options", *args, **kwargs)

    # ---------------------------------------------------------------------
    # Doc build wrapper
    # ---------------------------------------------------------------------
    def run_docbuild(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute sage_docbuild command entry.

        Parameters:
            argv (list, optional): Arguments for docbuild entrypoint if supported.

        Returns:
            dict: status/result or status/error.
        """
        mod = self._modules.get("sage_docbuild_main")
        if mod is None:
            return self._fail(
                "sage_docbuild.__main__ is not available.",
                guidance=self._errors.get("sage_docbuild_main"),
            )

        for attr in ("main", "run", "cli"):
            fn = getattr(mod, attr, None)
            if callable(fn):
                if argv is None:
                    return self._call("sage_docbuild_main", fn)
                return self._call("sage_docbuild_main", fn, argv)

        return self._fail(
            "No callable entrypoint found in sage_docbuild.__main__.",
            guidance="Verify the installed sage_docbuild module exposes a main-style function.",
        )

    # ---------------------------------------------------------------------
    # Bootstrap tooling wrapper
    # ---------------------------------------------------------------------
    def run_bootstrap(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute bootstrap tooling command entry.

        Parameters:
            argv (list, optional): Bootstrap command arguments.

        Returns:
            dict: status/result or status/error.
        """
        mod = self._modules.get("sage_bootstrap_cmdline")
        if mod is None:
            return self._fail(
                "build.sage_bootstrap.cmdline is not available.",
                guidance=self._errors.get("sage_bootstrap_cmdline"),
            )

        for attr in ("main", "run", "cli"):
            fn = getattr(mod, attr, None)
            if callable(fn):
                if argv is None:
                    return self._call("sage_bootstrap_cmdline", fn)
                return self._call("sage_bootstrap_cmdline", fn, argv)

        return self._fail(
            "No callable entrypoint found in build.sage_bootstrap.cmdline.",
            guidance="Check source tree integrity and bootstrap command module API.",
        )

    # ---------------------------------------------------------------------
    # Generic module entry runner
    # ---------------------------------------------------------------------
    def _run_module_entry(self, key: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._modules.get(key)
        if mod is None:
            return self._fail(
                f"Module for '{key}' is not available.",
                guidance=self._errors.get(key),
            )

        for attr in ("main", "run", "cli", "execute"):
            fn = getattr(mod, attr, None)
            if callable(fn):
                return self._call(key, fn, *args, **kwargs)

        return self._fail(
            f"No callable entrypoint found for '{key}'.",
            guidance="Inspect module and expose a callable such as main/run/cli/execute.",
        )