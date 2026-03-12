import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the Pyrocko repository.

    This adapter prefers direct Python imports from repository modules and
    provides a graceful fallback pathway when imports fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state, load known modules, and determine effective mode.

        Attributes:
            mode (str): "import" when repository modules are available, otherwise "fallback".
            modules (dict): Loaded module objects keyed by logical name.
            errors (list): Import/load issues captured during initialization.
        """
        self.mode = "import"
        self.modules: Dict[str, Any] = {}
        self.errors: List[str] = []
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode, "message": message}
        if data:
            out.update(data)
        return out

    def _fail(self, message: str, guidance: str = "", error: Optional[Exception] = None) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            out["guidance"] = guidance
        if error is not None:
            out["error_type"] = type(error).__name__
            out["error"] = str(error)
        return out

    def _import_module(self, key: str, module_path: str) -> None:
        try:
            self.modules[key] = importlib.import_module(module_path)
        except Exception as e:
            self.errors.append(f"Failed to import '{module_path}': {e}")

    def _load_modules(self) -> None:
        """
        Load modules identified by analysis for broad CLI and library coverage.
        """
        targets = {
            "apps_pyrocko": "src.apps.pyrocko",
            "apps_cake": "src.apps.cake",
            "apps_fomosto": "src.apps.fomosto",
            "apps_jackseis": "src.apps.jackseis",
            "apps_automap": "src.apps.automap",
            "apps_hamster": "src.apps.hamster",
            "squirrel_cli": "src.squirrel.tool.cli",
            "cake_core": "src.cake",
            "trace_core": "src.trace",
            "util_core": "src.util",
            "model_event": "src.model.event",
            "io_quakeml": "src.io.quakeml",
            "client_fdsn": "src.client.fdsn",
            "gf_store": "src.gf.store",
            "gf_seismosizer": "src.gf.seismosizer",
        }
        for key, path in targets.items():
            self._import_module(key, path)

        if self.errors:
            self.mode = "fallback"

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter health and import readiness.

        Returns:
            dict: Unified status dict with import diagnostics.
        """
        if self.mode == "import":
            return self._ok(
                {
                    "loaded_modules": sorted(self.modules.keys()),
                    "import_errors": self.errors,
                },
                "Adapter is operating in import mode.",
            )
        return self._fail(
            "Adapter is operating in fallback mode due to import failures.",
            guidance="Verify repository source is available under '<project>/source' and dependencies are installed.",
        )

    # -------------------------------------------------------------------------
    # CLI entry wrappers
    # -------------------------------------------------------------------------
    def call_pyrocko_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call main Pyrocko umbrella CLI module if available.

        Args:
            argv: Optional argument list to pass to CLI main callable.

        Returns:
            dict: Unified status dictionary.
        """
        return self._call_cli_module("apps_pyrocko", argv)

    def call_cake_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("apps_cake", argv)

    def call_fomosto_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("apps_fomosto", argv)

    def call_jackseis_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("apps_jackseis", argv)

    def call_automap_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("apps_automap", argv)

    def call_hamster_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("apps_hamster", argv)

    def call_squirrel_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._call_cli_module("squirrel_cli", argv)

    def _call_cli_module(self, module_key: str, argv: Optional[List[str]]) -> Dict[str, Any]:
        if self.mode != "import":
            return self._fail(
                f"Cannot execute '{module_key}' in fallback mode.",
                guidance="Restore import mode by fixing module path/dependencies, or run the corresponding command in shell.",
            )
        mod = self.modules.get(module_key)
        if mod is None:
            return self._fail(
                f"Module '{module_key}' not loaded.",
                guidance="Check import diagnostics via health().",
            )

        candidates = ["main", "run", "cli", "entrypoint"]
        try:
            for name in candidates:
                fn = getattr(mod, name, None)
                if callable(fn):
                    result = fn(argv) if argv is not None else fn()
                    return self._ok({"result": result}, f"Executed {module_key}.{name} successfully.")
            return self._fail(
                f"No callable CLI entry found in module '{module_key}'.",
                guidance="Inspect module and call exported command function manually.",
            )
        except Exception as e:
            return self._fail(
                f"Execution failed for module '{module_key}'.",
                guidance="Review provided arguments and module-specific CLI expectations.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # Generic function/class adapters
    # -------------------------------------------------------------------------
    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from a loaded module by name.

        Args:
            module_key: Logical key from loaded module registry.
            function_name: Function to invoke.
            *args, **kwargs: Forwarded invocation arguments.

        Returns:
            dict: Unified status dictionary with result.
        """
        if self.mode != "import":
            return self._fail(
                "Function calls are unavailable in fallback mode.",
                guidance="Fix imports and dependencies to re-enable direct function calls.",
            )
        mod = self.modules.get(module_key)
        if not mod:
            return self._fail(f"Unknown module key '{module_key}'.", guidance="Use health() to list loaded modules.")
        fn = getattr(mod, function_name, None)
        if not callable(fn):
            return self._fail(
                f"Function '{function_name}' not found or not callable in '{module_key}'.",
                guidance="Check exact function name and module exports.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, f"Called {module_key}.{function_name} successfully.")
        except Exception as e:
            return self._fail(
                f"Function call failed for {module_key}.{function_name}.",
                guidance="Validate parameters against the target function signature.",
                error=e,
            )

    def create_module_class_instance(
        self, module_key: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Instantiate any class from a loaded module by name.

        Args:
            module_key: Logical key from loaded module registry.
            class_name: Class name to instantiate.
            *args, **kwargs: Constructor arguments.

        Returns:
            dict: Unified status dictionary with instance reference.
        """
        if self.mode != "import":
            return self._fail(
                "Class instantiation is unavailable in fallback mode.",
                guidance="Fix import issues and retry.",
            )
        mod = self.modules.get(module_key)
        if not mod:
            return self._fail(f"Unknown module key '{module_key}'.", guidance="Use health() to discover loaded modules.")
        cls = getattr(mod, class_name, None)
        if cls is None or not isinstance(cls, type):
            return self._fail(
                f"Class '{class_name}' not found in '{module_key}'.",
                guidance="Check class name and module contents.",
            )
        try:
            obj = cls(*args, **kwargs)
            return self._ok({"instance": obj}, f"Instantiated {module_key}.{class_name} successfully.")
        except Exception as e:
            return self._fail(
                f"Class instantiation failed for {module_key}.{class_name}.",
                guidance="Verify constructor arguments.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # Fallback support
    # -------------------------------------------------------------------------
    def fallback_hint(self) -> Dict[str, Any]:
        """
        Return actionable fallback guidance when import mode is unavailable.
        """
        if self.mode == "import":
            return self._ok(message="Import mode is active; fallback not required.")
        return self._fail(
            "Import mode is not available.",
            guidance=(
                "Ensure repository code exists at '<project>/source', "
                "install required dependencies (numpy, scipy, PyYAML, requests), "
                "and reinitialize the adapter."
            ),
        )

    def debug_trace(self) -> Dict[str, Any]:
        """
        Provide debug trace payload for troubleshooting adapter execution.
        """
        return self._ok(
            {
                "mode": self.mode,
                "errors": list(self.errors),
                "loaded_modules": sorted(self.modules.keys()),
                "traceback_available": traceback.format_exc(),
            },
            "Debug information collected.",
        )