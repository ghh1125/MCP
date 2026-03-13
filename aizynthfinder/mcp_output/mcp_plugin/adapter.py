import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the aizynthfinder repository.

    This adapter prioritizes direct Python imports from the local source tree and
    provides a CLI fallback path if import-mode operations cannot proceed.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode}
        if data:
            out.update(data)
        return out

    def _fail(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = str(error)
        return payload

    def _load_modules(self) -> None:
        """
        Attempt to import key modules discovered by analysis.
        Uses full package paths rooted in local source tree.
        """
        targets = {
            "aizynthfinder_main": "aizynthfinder.aizynthfinder",
            "analysis_routes": "aizynthfinder.analysis.routes",
            "analysis_tree_analysis": "aizynthfinder.analysis.tree_analysis",
            "analysis_utils": "aizynthfinder.analysis.utils",
            "interfaces_cli": "aizynthfinder.interfaces.aizynthcli",
            "interfaces_app": "aizynthfinder.interfaces.aizynthapp",
            "tool_download_public_data": "aizynthfinder.tools.download_public_data",
            "tool_make_stock": "aizynthfinder.tools.make_stock",
            "tool_cat_output": "aizynthfinder.tools.cat_output",
            "reactiontree": "aizynthfinder.reactiontree",
        }

        failed = {}
        for key, mod_path in targets.items():
            try:
                self._modules[key] = importlib.import_module(mod_path)
            except Exception as exc:
                failed[key] = f"{type(exc).__name__}: {exc}"

        if failed:
            self._import_error = (
                "Some modules failed to import. Import mode is partially available. "
                "Use CLI fallback methods where needed."
            )
            self._modules["__failed__"] = failed

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health details, including loaded and failed modules.
        """
        failed = self._modules.get("__failed__", {})
        return self._ok(
            {
                "loaded_modules": sorted([k for k in self._modules.keys() if not k.startswith("__")]),
                "failed_modules": failed,
                "import_warning": self._import_error,
            }
        )

    # -------------------------------------------------------------------------
    # Core import-mode entrypoint wrappers
    # -------------------------------------------------------------------------
    def run_aizynthfinder(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the main aizynthfinder module in import mode.

        Parameters:
            *args: Positional args forwarded to discovered callable.
            **kwargs: Keyword args forwarded to discovered callable.

        Returns:
            Unified status dictionary with execution details or actionable error.
        """
        mod = self._modules.get("aizynthfinder_main")
        if not mod:
            return self._fail(
                "Main module is unavailable in import mode.",
                hint="Try CLI fallback using call_aizynthcli().",
            )

        try:
            for candidate in ("main", "run", "execute"):
                fn = getattr(mod, candidate, None)
                if callable(fn):
                    result = fn(*args, **kwargs)
                    return self._ok({"result": result, "callable": candidate, "module": mod.__name__})
            return self._fail(
                "No callable entrypoint (main/run/execute) found in main module.",
                hint="Inspect module API or use call_aizynthcli() fallback.",
            )
        except Exception as exc:
            return self._fail("Failed to execute main module.", hint="Check config/model paths and dependencies.", error=exc)

    def call_aizynthcli(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke CLI module entrypoint in-process as fallback.

        Parameters:
            argv: Optional list of CLI-like arguments.

        Returns:
            Unified status dictionary.
        """
        mod = self._modules.get("interfaces_cli")
        if not mod:
            return self._fail(
                "CLI module could not be imported.",
                hint="Verify local source path and required dependencies.",
            )

        try:
            for candidate in ("main", "run_cli", "cli"):
                fn = getattr(mod, candidate, None)
                if callable(fn):
                    result = fn(argv) if argv is not None else fn()
                    return self._ok({"result": result, "callable": candidate, "module": mod.__name__})
            return self._fail(
                "No CLI callable found (main/run_cli/cli).",
                hint="Check aizynthfinder.interfaces.aizynthcli for the current entrypoint function.",
            )
        except Exception as exc:
            return self._fail(
                "CLI execution failed.",
                hint="Validate CLI arguments and data/model file availability.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Tools wrappers
    # -------------------------------------------------------------------------
    def call_download_public_data(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call the public-data download tool module.

        Parameters:
            argv: Optional argument list forwarded to tool entrypoint.

        Returns:
            Unified status dictionary.
        """
        return self._call_tool_module("tool_download_public_data", argv)

    def call_make_stock(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call the make_stock tool module.

        Parameters:
            argv: Optional argument list forwarded to tool entrypoint.

        Returns:
            Unified status dictionary.
        """
        return self._call_tool_module("tool_make_stock", argv)

    def call_cat_output(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call the cat_output tool module.

        Parameters:
            argv: Optional argument list forwarded to tool entrypoint.

        Returns:
            Unified status dictionary.
        """
        return self._call_tool_module("tool_cat_output", argv)

    def _call_tool_module(self, module_key: str, argv: Optional[list]) -> Dict[str, Any]:
        mod = self._modules.get(module_key)
        if not mod:
            return self._fail(
                f"Tool module '{module_key}' could not be imported.",
                hint="Check source path and optional dependencies.",
            )
        try:
            for candidate in ("main", "run", "cli"):
                fn = getattr(mod, candidate, None)
                if callable(fn):
                    result = fn(argv) if argv is not None else fn()
                    return self._ok({"result": result, "callable": candidate, "module": mod.__name__})
            return self._fail(
                f"No callable entrypoint found in module '{mod.__name__}'.",
                hint="Expected one of: main, run, cli.",
            )
        except Exception as exc:
            return self._fail(
                f"Execution failed for module '{mod.__name__}'.",
                hint="Review input arguments and file paths.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Analysis helpers
    # -------------------------------------------------------------------------
    def call_analysis_routes(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from aizynthfinder.analysis.routes by name.
        """
        return self._call_module_function("analysis_routes", function_name, *args, **kwargs)

    def call_analysis_tree_analysis(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from aizynthfinder.analysis.tree_analysis by name.
        """
        return self._call_module_function("analysis_tree_analysis", function_name, *args, **kwargs)

    def call_analysis_utils(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from aizynthfinder.analysis.utils by name.
        """
        return self._call_module_function("analysis_utils", function_name, *args, **kwargs)

    def _call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._modules.get(module_key)
        if not mod:
            return self._fail(
                f"Module '{module_key}' is unavailable.",
                hint="Run health_check() and use CLI fallback if needed.",
            )
        try:
            fn = getattr(mod, function_name, None)
            if not callable(fn):
                return self._fail(
                    f"Function '{function_name}' not found or not callable in '{mod.__name__}'.",
                    hint="Check module function names and signatures.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result": result, "module": mod.__name__, "function": function_name})
        except Exception as exc:
            return self._fail(
                f"Failed while calling '{function_name}' in '{mod.__name__}'.",
                hint="Validate provided arguments against function signature.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Class instance factory methods (generic + targeted)
    # -------------------------------------------------------------------------
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance from any class via dynamic import.

        Parameters:
            module_path: Full import path, e.g. 'aizynthfinder.context.config'
            class_name: Class name to instantiate.
            *args/**kwargs: Constructor arguments.

        Returns:
            Unified status dictionary with created instance or error guidance.
        """
        try:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._fail(
                    f"Class '{class_name}' was not found in module '{module_path}'.",
                    hint="Verify class name and module path from repository source.",
                )
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance, "module": module_path, "class": class_name})
        except Exception as exc:
            return self._fail(
                f"Failed to create instance '{class_name}' from '{module_path}'.",
                hint="Check constructor parameters and required dependencies.",
                error=exc,
            )

    def create_reaction_tree_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a class instance from aizynthfinder.reactiontree module.

        Note:
            Because class names can vary across versions, this method can use:
            - kwargs['class_name'] to explicitly choose a class.
            - default class candidates when omitted.
        """
        mod = self._modules.get("reactiontree")
        if not mod:
            return self._fail(
                "Reaction tree module is unavailable.",
                hint="Run health_check() and verify source import path.",
            )
        try:
            class_name = kwargs.pop("class_name", None)
            candidates = [class_name] if class_name else ["ReactionTree", "RouteCollection", "TreeAnalysis"]
            candidates = [c for c in candidates if c]
            for name in candidates:
                cls = getattr(mod, name, None)
                if cls is not None:
                    instance = cls(*args, **kwargs)
                    return self._ok({"instance": instance, "module": mod.__name__, "class": name})
            return self._fail(
                "No known class found in reactiontree module.",
                hint="Pass class_name explicitly to create_reaction_tree_instance().",
            )
        except Exception as exc:
            return self._fail(
                "Failed to instantiate class from reactiontree module.",
                hint="Check constructor arguments and class_name.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Fallback utilities
    # -------------------------------------------------------------------------
    def fallback_cli_guidance(self) -> Dict[str, Any]:
        """
        Provide concise actionable fallback guidance.
        """
        return self._ok(
            {
                "message": "Import mode is unavailable or partial. Use CLI fallbacks.",
                "recommended_calls": [
                    "call_aizynthcli(argv=[...])",
                    "call_download_public_data(argv=[...])",
                    "call_make_stock(argv=[...])",
                    "call_cat_output(argv=[...])",
                ],
            }
        )

    def debug_trace(self) -> Dict[str, Any]:
        """
        Return captured import errors and traceback context for diagnostics.
        """
        try:
            failed = self._modules.get("__failed__", {})
            return self._ok(
                {
                    "import_error_summary": self._import_error,
                    "failed_modules": failed,
                    "traceback_note": "Runtime tracebacks are returned per method on failure.",
                    "stack": traceback.format_exc(),
                }
            )
        except Exception as exc:
            return self._fail("Failed to build debug trace.", error=exc)