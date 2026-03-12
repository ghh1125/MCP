import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for deep-searcher.

    This adapter prioritizes direct Python imports from the local source tree and provides
    graceful fallbacks when imports or optional dependencies are unavailable.
    """

    mode = "import"

    # -------------------------------------------------------------------------
    # Initialization and module loading
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self._loaded = False
        self._import_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._classes: Dict[str, Any] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        try:
            import deepsearcher  # noqa: F401
            from deepsearcher.configuration import Configuration
            import deepsearcher.cli as cli_module
            import main as main_module

            self._classes["Configuration"] = Configuration
            self._modules["deepsearcher.cli"] = cli_module
            self._modules["main"] = main_module
            self._loaded = True
        except Exception as exc:
            self._loaded = False
            self._import_error = str(exc)

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import availability.

        Returns:
            Unified status dictionary with import readiness information.
        """
        if self._loaded:
            return self._ok(
                {
                    "loaded": True,
                    "available_classes": sorted(list(self._classes.keys())),
                    "available_modules": sorted(list(self._modules.keys())),
                },
                "Import mode is ready.",
            )
        return self._err(
            "Import mode initialization failed.",
            guidance="Ensure repository source exists under ./source and required dependencies are installed.",
            details=self._import_error,
        )

    # -------------------------------------------------------------------------
    # Core class adapter: deepsearcher.configuration.Configuration
    # -------------------------------------------------------------------------
    def create_configuration_instance(
        self,
        config_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create an instance of deepsearcher.configuration.Configuration.

        Parameters:
            config_path: Optional path to a YAML configuration file.
            **kwargs: Additional constructor parameters, passed through as-is.

        Returns:
            Unified status dictionary with:
            - instance: Created Configuration object (on success)
            - class_name: Class name
            - message/status details
        """
        if not self._loaded:
            return self._err(
                "Cannot create Configuration instance because imports are unavailable.",
                guidance="Call health_check() and resolve missing dependencies first.",
                details=self._import_error,
            )

        try:
            cls = self._classes["Configuration"]
            if config_path is not None:
                instance = cls(config_path=config_path, **kwargs)
            else:
                instance = cls(**kwargs)
            return self._ok(
                {
                    "instance": instance,
                    "class_name": "Configuration",
                },
                "Configuration instance created.",
            )
        except TypeError:
            try:
                cls = self._classes["Configuration"]
                if config_path is not None:
                    instance = cls(config_path, **kwargs)
                else:
                    instance = cls(**kwargs)
                return self._ok(
                    {
                        "instance": instance,
                        "class_name": "Configuration",
                    },
                    "Configuration instance created.",
                )
            except Exception as exc:
                return self._err(
                    "Failed to initialize Configuration.",
                    guidance="Verify constructor parameters and YAML file path.",
                    details=str(exc),
                )
        except Exception as exc:
            return self._err(
                "Failed to initialize Configuration.",
                guidance="Verify constructor parameters and YAML file path.",
                details=str(exc),
            )

    # -------------------------------------------------------------------------
    # CLI module adapter: deepsearcher.cli
    # -------------------------------------------------------------------------
    def call_deepsearcher_cli(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke deepsearcher CLI entry function if available.

        Parameters:
            argv: Optional argument list to inject into sys.argv for CLI execution.

        Returns:
            Unified status dictionary with return value if callable was found.
        """
        if not self._loaded:
            return self._err(
                "CLI module is unavailable because imports failed.",
                guidance="Install optional runtime dependencies and ensure ./source is correctly mounted.",
                details=self._import_error,
            )

        try:
            cli_module = self._modules["deepsearcher.cli"]

            candidates = ["main", "cli", "run"]
            callable_name = next((name for name in candidates if hasattr(cli_module, name)), None)
            if not callable_name:
                return self._err(
                    "No callable CLI entry found in deepsearcher.cli.",
                    guidance="Check deepsearcher/cli.py and expose one of: main, cli, or run.",
                )

            fn = getattr(cli_module, callable_name)
            if not callable(fn):
                return self._err(
                    f"Resolved attribute '{callable_name}' is not callable.",
                    guidance="Ensure CLI entrypoint is a function.",
                )

            original_argv = sys.argv[:]
            try:
                if argv is not None:
                    sys.argv = [original_argv[0]] + list(argv)
                result = fn()
            finally:
                sys.argv = original_argv

            return self._ok(
                {"entrypoint": callable_name, "result": result},
                "CLI call completed.",
            )
        except SystemExit as exc:
            return self._ok(
                {"entrypoint": "system_exit", "exit_code": getattr(exc, "code", None)},
                "CLI exited normally via SystemExit.",
            )
        except Exception as exc:
            return self._err(
                "CLI execution failed.",
                guidance="Validate CLI arguments and provider credentials in configuration.",
                details=str(exc),
            )

    # -------------------------------------------------------------------------
    # Main module adapter: main.py
    # -------------------------------------------------------------------------
    def call_main_module(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke top-level main.py runnable entry if available.

        Parameters:
            argv: Optional list of CLI-like arguments.

        Returns:
            Unified status dictionary with invocation details and return payload.
        """
        if not self._loaded:
            return self._err(
                "Main module is unavailable because imports failed.",
                guidance="Confirm that main.py exists under ./source and imports are valid.",
                details=self._import_error,
            )

        try:
            main_module = self._modules["main"]
            candidates = ["main", "run", "cli"]
            callable_name = next((name for name in candidates if hasattr(main_module, name)), None)

            if not callable_name:
                return self._err(
                    "No callable entry function found in main module.",
                    guidance="Expose a main/run/cli function in main.py to support import execution.",
                )

            fn = getattr(main_module, callable_name)
            if not callable(fn):
                return self._err(
                    f"Resolved attribute '{callable_name}' is not callable.",
                    guidance="Ensure the selected entrypoint is a function.",
                )

            original_argv = sys.argv[:]
            try:
                if argv is not None:
                    sys.argv = [original_argv[0]] + list(argv)
                result = fn()
            finally:
                sys.argv = original_argv

            return self._ok(
                {"entrypoint": callable_name, "result": result},
                "Main module call completed.",
            )
        except SystemExit as exc:
            return self._ok(
                {"entrypoint": "system_exit", "exit_code": getattr(exc, "code", None)},
                "Main module exited normally via SystemExit.",
            )
        except Exception as exc:
            return self._err(
                "Main module execution failed.",
                guidance="Check runtime config, API keys, and optional provider dependencies.",
                details=str(exc),
            )

    # -------------------------------------------------------------------------
    # Fallback / capability helpers
    # -------------------------------------------------------------------------
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return adapter capabilities inferred from repository analysis.

        Returns:
            Unified status dictionary with discovered classes/modules and operating mode.
        """
        return self._ok(
            {
                "import_strategy": "import",
                "fallback_strategy": "cli-like invocation via module entrypoints",
                "classes": sorted(list(self._classes.keys())),
                "modules": sorted(list(self._modules.keys())),
                "loaded": self._loaded,
            },
            "Capabilities retrieved.",
        )

    def fallback_hint(self) -> Dict[str, Any]:
        """
        Provide concise operational guidance for import-failure scenarios.

        Returns:
            Unified status dictionary with actionable troubleshooting hints.
        """
        if self._loaded:
            return self._ok(
                {"hint": "Import mode is active; fallback not required."},
                "No fallback needed.",
            )
        return self._err(
            "Adapter is running in degraded state due to import failure.",
            guidance=(
                "1) Ensure repository is available at ./source\n"
                "2) Install pyproject dependencies\n"
                "3) Verify Python version compatibility (3.10+ recommended)\n"
                "4) Retry health_check()"
            ),
            details=self._import_error,
        )