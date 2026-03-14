import os
import sys
from typing import Any, Callable, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the Scanpy repository.

    This adapter prioritizes direct imports from repository source code and falls back
    to a lightweight CLI-compatible mode when imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._initialize_modules()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, guidance: Optional[str] = None, exc: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if exc is not None:
            payload["error"] = str(exc)
        return payload

    def _initialize_modules(self) -> None:
        try:
            import source.src.scanpy as scanpy_pkg
            import source.src.scanpy.cli as scanpy_cli
            import source.src.scanpy.__main__ as scanpy_main

            self._modules["scanpy"] = scanpy_pkg
            self._modules["cli"] = scanpy_cli
            self._modules["main"] = scanpy_main
        except Exception as exc:
            self.mode = "cli"
            self._import_error = str(exc)

    def _get_module(self, key: str) -> Optional[Any]:
        return self._modules.get(key)

    def _safe_call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as exc:
            return self._error(
                "Function execution failed.",
                guidance="Check arguments and data schema, then retry.",
                exc=exc,
            )

    # ---------------------------------------------------------------------
    # Status and environment
    # ---------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import state.

        Returns:
            dict: Unified response with status, mode, and module availability.
        """
        available = {k: bool(v) for k, v in self._modules.items()}
        if self.mode == "import":
            return self._ok({"modules": available}, "Adapter is ready in import mode.")
        return self._error(
            "Adapter is running in fallback mode due to import failure.",
            guidance=f"Verify repository path and dependencies. Import error: {self._import_error}",
        )

    # ---------------------------------------------------------------------
    # Core scanpy package access
    # ---------------------------------------------------------------------
    def instance_scanpy(self) -> Dict[str, Any]:
        """
        Return the imported scanpy module instance.

        Returns:
            dict: Unified response containing module object when available.
        """
        mod = self._get_module("scanpy")
        if mod is None:
            return self._error(
                "scanpy module is unavailable in current mode.",
                guidance="Install required dependencies and ensure source/src is importable.",
            )
        return self._ok({"module": mod}, "scanpy module loaded.")

    def call_scanpy_attr(self, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a top-level attribute from source.src.scanpy dynamically.

        Parameters:
            attr_name: Name of function/attribute on the scanpy package.
            *args: Positional arguments for callable attributes.
            **kwargs: Keyword arguments for callable attributes.

        Returns:
            dict: Unified response with call result or attribute value.
        """
        mod = self._get_module("scanpy")
        if mod is None:
            return self._error(
                "scanpy module is not imported.",
                guidance="Use health_check() and resolve import issues first.",
            )
        if not hasattr(mod, attr_name):
            return self._error(
                f"Attribute '{attr_name}' not found in scanpy module.",
                guidance="Check the attribute name against source.src.scanpy exports.",
            )
        target = getattr(mod, attr_name)
        if callable(target):
            return self._safe_call(target, *args, **kwargs)
        return self._ok({"result": target}, f"Attribute '{attr_name}' retrieved.")

    # ---------------------------------------------------------------------
    # CLI module wrappers (source.src.scanpy.cli)
    # ---------------------------------------------------------------------
    def instance_cli(self) -> Dict[str, Any]:
        """
        Return the imported CLI module instance.

        Returns:
            dict: Unified response containing CLI module object.
        """
        mod = self._get_module("cli")
        if mod is None:
            return self._error(
                "CLI module is unavailable.",
                guidance="Ensure source.src.scanpy.cli can be imported.",
            )
        return self._ok({"module": mod}, "CLI module loaded.")

    def call_cli_main(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke CLI entry behavior when available.

        Parameters:
            args: Optional argument list to emulate command-line input.

        Returns:
            dict: Unified response with CLI execution result.
        """
        mod = self._get_module("cli")
        if mod is None:
            return self._error(
                "CLI module is not available in fallback context.",
                guidance="Run 'python -m scanpy --help' in environment with dependencies.",
            )
        for candidate in ("main", "cli", "run"):
            if hasattr(mod, candidate) and callable(getattr(mod, candidate)):
                fn = getattr(mod, candidate)
                if args is None:
                    return self._safe_call(fn)
                return self._safe_call(fn, args)
        return self._error(
            "No callable CLI entry function found in source.src.scanpy.cli.",
            guidance="Inspect module for available public entry points and update adapter mapping.",
        )

    # ---------------------------------------------------------------------
    # __main__ module wrappers (source.src.scanpy.__main__)
    # ---------------------------------------------------------------------
    def instance_main(self) -> Dict[str, Any]:
        """
        Return the imported __main__ module instance.

        Returns:
            dict: Unified response containing __main__ module object.
        """
        mod = self._get_module("main")
        if mod is None:
            return self._error(
                "__main__ module is unavailable.",
                guidance="Ensure source.src.scanpy.__main__ is importable.",
            )
        return self._ok({"module": mod}, "__main__ module loaded.")

    def call_module_main(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke python -m scanpy style entry point behavior.

        Parameters:
            args: Optional list of arguments for module main function.

        Returns:
            dict: Unified response with execution outcome.
        """
        mod = self._get_module("main")
        if mod is None:
            return self._error(
                "__main__ module is unavailable in current mode.",
                guidance="Use environment with full dependencies or run CLI directly.",
            )
        for candidate in ("main",):
            if hasattr(mod, candidate) and callable(getattr(mod, candidate)):
                fn = getattr(mod, candidate)
                if args is None:
                    return self._safe_call(fn)
                return self._safe_call(fn, args)
        return self._error(
            "No callable main() found in source.src.scanpy.__main__.",
            guidance="Verify the repository version and update adapter expectations.",
        )