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
    Import-mode MCP adapter for ObsPy source tree.

    This adapter prioritizes direct module import from local `source` path and provides:
    - Runtime import health check
    - Generic import/call helpers
    - Dedicated wrappers for identified CLI modules/functions from analysis
    - Graceful fallback guidance when import/runtime fails
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._module_cache: Dict[str, Any] = {}
        self._cli_modules = {
            "obspy-print": "obspy.scripts.print",
            "obspy-flinn-engdahl": "obspy.scripts.flinnengdahl",
            "obspy-reftek-rescue": "obspy.scripts.reftekrescue",
            "obspy-sds-report": "obspy.scripts.sds_html_report",
        }
        self._dependency_hints = {
            "required": ["numpy", "scipy", "matplotlib", "lxml", "setuptools"],
            "optional": ["cartopy", "requests", "sqlalchemy", "geographiclib", "pyproj"],
        }

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, exc: Optional[BaseException] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if exc is not None:
            payload["error_type"] = exc.__class__.__name__
            payload["error"] = str(exc)
            payload["traceback"] = traceback.format_exc(limit=3)
        return payload

    def _import_module(self, module_path: str) -> Any:
        if module_path in self._module_cache:
            return self._module_cache[module_path]
        module = importlib.import_module(module_path)
        self._module_cache[module_path] = module
        return module

    def _resolve_callable(self, module_path: str, function_name: str) -> Any:
        module = self._import_module(module_path)
        if not hasattr(module, function_name):
            raise AttributeError(
                f"Function '{function_name}' was not found in module '{module_path}'. "
                "Verify source version or available API names."
            )
        fn = getattr(module, function_name)
        if not callable(fn):
            raise TypeError(f"Attribute '{function_name}' in module '{module_path}' is not callable.")
        return fn

    # -------------------------------------------------------------------------
    # Health / environment
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check import readiness for key ObsPy modules and dependency hints.

        Returns:
            dict: Unified status payload with import check details.
        """
        required_modules = [
            "obspy",
            "obspy.core",
            "obspy.scripts.print",
            "obspy.scripts.flinnengdahl",
            "obspy.scripts.reftekrescue",
            "obspy.scripts.sds_html_report",
        ]
        results = {}
        for mod in required_modules:
            try:
                self._import_module(mod)
                results[mod] = "ok"
            except Exception as exc:
                results[mod] = f"failed: {exc.__class__.__name__}: {exc}"

        failures = {k: v for k, v in results.items() if not str(v).startswith("ok")}
        if failures:
            return self._err(
                "One or more critical imports failed.",
                guidance=(
                    "Ensure the local source tree exists under the configured 'source' directory and "
                    "install required dependencies: " + ", ".join(self._dependency_hints["required"])
                ),
            ) | {"checks": results, "dependency_hints": self._dependency_hints}
        return self._ok({"checks": results, "dependency_hints": self._dependency_hints})

    # -------------------------------------------------------------------------
    # Generic import/call API
    # -------------------------------------------------------------------------
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance from a class in a target module.

        Parameters:
            module_path: Full module import path (e.g., 'obspy.clients.fdsn.client').
            class_name: Target class name.
            *args, **kwargs: Arguments passed to class constructor.

        Returns:
            dict: status payload; on success includes 'instance'.
        """
        try:
            module = self._import_module(module_path)
            if not hasattr(module, class_name):
                return self._err(
                    f"Class '{class_name}' not found in module '{module_path}'.",
                    guidance="Check class name spelling and module path from repository source.",
                )
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, f"Instance created: {module_path}.{class_name}")
        except Exception as exc:
            return self._err(
                f"Failed to create instance for {module_path}.{class_name}.",
                guidance="Verify constructor parameters and required runtime dependencies.",
                exc=exc,
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a target module.

        Parameters:
            module_path: Full module import path.
            function_name: Function name in the module.
            *args, **kwargs: Function arguments.

        Returns:
            dict: status payload; on success includes 'result'.
        """
        try:
            fn = self._resolve_callable(module_path, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, f"Function executed: {module_path}.{function_name}")
        except Exception as exc:
            return self._err(
                f"Failed to call function {module_path}.{function_name}.",
                guidance="Confirm function signature and input argument types.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Dedicated wrappers for identified CLI modules
    # -------------------------------------------------------------------------
    def cli_obspy_print(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute ObsPy print script entry function from module `obspy.scripts.print`.

        Parameters:
            args: Optional CLI-like argument list. If omitted, defaults to [].

        Returns:
            dict: status payload with execution result.
        """
        return self._run_cli_module("obspy-print", args or [])

    def cli_obspy_flinn_engdahl(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute ObsPy Flinn-Engdahl resolver from module `obspy.scripts.flinnengdahl`.

        Parameters:
            args: Optional CLI-like argument list.

        Returns:
            dict: status payload with execution result.
        """
        return self._run_cli_module("obspy-flinn-engdahl", args or [])

    def cli_obspy_reftek_rescue(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute ObsPy Reftek rescue utility from module `obspy.scripts.reftekrescue`.

        Parameters:
            args: Optional CLI-like argument list.

        Returns:
            dict: status payload with execution result.
        """
        return self._run_cli_module("obspy-reftek-rescue", args or [])

    def cli_obspy_sds_report(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute ObsPy SDS HTML report utility from module `obspy.scripts.sds_html_report`.

        Parameters:
            args: Optional CLI-like argument list.

        Returns:
            dict: status payload with execution result.
        """
        return self._run_cli_module("obspy-sds-report", args or [])

    def _run_cli_module(self, cli_name: str, args: List[str]) -> Dict[str, Any]:
        try:
            if cli_name not in self._cli_modules:
                return self._err(
                    f"Unknown CLI name '{cli_name}'.",
                    guidance=f"Supported CLI names: {', '.join(sorted(self._cli_modules.keys()))}",
                )
            module_path = self._cli_modules[cli_name]
            module = self._import_module(module_path)

            target_candidates = ["main", "_main"]
            target = None
            for name in target_candidates:
                if hasattr(module, name) and callable(getattr(module, name)):
                    target = getattr(module, name)
                    break

            if target is None:
                return self._err(
                    f"No callable main entry point found in '{module_path}'.",
                    guidance="Inspect module to identify its callable entry function.",
                )

            result = target(args) if args is not None else target()
            return self._ok(
                {"result": result, "module": module_path, "cli_name": cli_name, "args": args},
                f"CLI module executed: {cli_name}",
            )
        except SystemExit as exc:
            return self._ok(
                {"exit_code": getattr(exc, "code", 0), "cli_name": cli_name, "args": args},
                "CLI requested process exit; captured safely.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to execute CLI module '{cli_name}'.",
                guidance="Validate CLI arguments and ensure optional dependencies are installed.",
                exc=exc,
            )

    # -------------------------------------------------------------------------
    # Discovery helpers
    # -------------------------------------------------------------------------
    def list_supported_cli(self) -> Dict[str, Any]:
        """
        List supported CLI commands identified by analysis.

        Returns:
            dict: status payload with command mapping.
        """
        return self._ok({"commands": self._cli_modules})

    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import and cache a module by full path.

        Parameters:
            module_path: Module path (e.g., 'obspy.signal.filter').

        Returns:
            dict: status payload with module representation.
        """
        try:
            module = self._import_module(module_path)
            return self._ok({"module": module, "module_path": module_path}, "Module imported.")
        except Exception as exc:
            return self._err(
                f"Failed to import module '{module_path}'.",
                guidance="Check module path and source layout under the 'source' directory.",
                exc=exc,
            )