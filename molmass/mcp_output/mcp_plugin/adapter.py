import os
import sys
import inspect
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for molmass repository.

    This adapter prioritizes direct module import and provides graceful CLI fallback.
    It exposes dedicated methods for discovered entry points:
      - source.molmass.__main__ (module execution dispatcher)
      - source.molmass.molmass.main (core CLI handler)
      - source.molmass.web.main (web/CGI-style entrypoint)

    All public methods return a unified dictionary format:
      {
        "status": "success" | "error" | "fallback",
        ...
      }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize adapter state, import mode, and lazy-load targets.

        Attributes:
            mode (str): Adapter operation mode, fixed to "import".
            modules (dict): Loaded module references.
            functions (dict): Loaded callable references.
            import_errors (list): Detailed import errors.
        """
        self.mode: str = "import"
        self.modules: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        self.import_errors: List[Dict[str, str]] = []
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Attempt to import all identified modules and function entrypoints.

        Uses full package paths from analysis and stores detailed errors for
        graceful fallback behavior.
        """
        import_targets = [
            ("source.molmass.__main__", None),
            ("source.molmass.molmass", "main"),
            ("source.molmass.web", "main"),
        ]

        for module_path, function_name in import_targets:
            try:
                module = __import__(module_path, fromlist=["*"])
                self.modules[module_path] = module
                if function_name:
                    func = getattr(module, function_name, None)
                    if callable(func):
                        self.functions[f"{module_path}.{function_name}"] = func
                    else:
                        self.import_errors.append(
                            {
                                "module": module_path,
                                "error": f"Function '{function_name}' not found or not callable.",
                            }
                        )
            except Exception as exc:
                self.import_errors.append(
                    {
                        "module": module_path,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter health and import readiness.

        Returns:
            dict: Unified status dictionary with loaded modules/functions and import diagnostics.
        """
        try:
            return {
                "status": "success",
                "mode": self.mode,
                "loaded_modules": sorted(self.modules.keys()),
                "loaded_functions": sorted(self.functions.keys()),
                "import_errors": self.import_errors,
                "ready": len(self.functions) > 0 or len(self.modules) > 0,
            }
        except Exception as exc:
            return self._error_response(
                message="Failed to run health check.",
                error=exc,
                guidance="Inspect adapter initialization and module import paths.",
            )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _success_response(self, **payload: Any) -> Dict[str, Any]:
        """
        Build a standardized success response.

        Args:
            **payload: Additional response fields.

        Returns:
            dict: Success response with status field.
        """
        data = {"status": "success"}
        data.update(payload)
        return data

    def _fallback_response(self, **payload: Any) -> Dict[str, Any]:
        """
        Build a standardized fallback response.

        Args:
            **payload: Additional response fields.

        Returns:
            dict: Fallback response with status field.
        """
        data = {"status": "fallback"}
        data.update(payload)
        return data

    def _error_response(self, message: str, error: Exception, guidance: str) -> Dict[str, Any]:
        """
        Build a standardized error response.

        Args:
            message: Human-readable high-level error.
            error: Caught exception instance.
            guidance: Actionable next step in English.

        Returns:
            dict: Error response with detailed diagnostics.
        """
        return {
            "status": "error",
            "message": message,
            "error_type": type(error).__name__,
            "error": str(error),
            "guidance": guidance,
            "traceback": traceback.format_exc(),
        }

    def _invoke_callable(self, func: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Safely invoke a callable with flexible argument support.

        If invocation fails because of incompatible signature, a secondary attempt
        is made without arguments for zero-arg CLI-style entrypoints.

        Args:
            func: Callable target.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified result dictionary.
        """
        try:
            result = func(*args, **kwargs)
            return self._success_response(result=result, callable_name=getattr(func, "__name__", str(func)))
        except TypeError:
            try:
                result = func()
                return self._success_response(
                    result=result,
                    callable_name=getattr(func, "__name__", str(func)),
                    note="Called without arguments due to signature mismatch.",
                )
            except Exception as exc:
                return self._error_response(
                    message="Callable invocation failed after retry.",
                    error=exc,
                    guidance="Check function signature and provide compatible arguments.",
                )
        except Exception as exc:
            return self._error_response(
                message="Callable invocation failed.",
                error=exc,
                guidance="Verify input values and runtime context required by the target function.",
            )

    def _run_cli_fallback(self, module_name: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute module through subprocess fallback mode.

        Args:
            module_name: Python module name for `python -m`.
            argv: Optional CLI arguments list.

        Returns:
            dict: Unified fallback/success/error response.
        """
        try:
            import subprocess

            cmd = [sys.executable, "-m", module_name]
            if argv:
                cmd.extend(argv)

            proc = subprocess.run(cmd, capture_output=True, text=True)
            status = "success" if proc.returncode == 0 else "fallback"
            return {
                "status": status,
                "mode": "cli_fallback",
                "command": cmd,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "guidance": (
                    "Import mode failed or was unavailable; CLI fallback was used."
                    if status == "fallback"
                    else "CLI fallback executed successfully."
                ),
            }
        except Exception as exc:
            return self._error_response(
                message="CLI fallback execution failed.",
                error=exc,
                guidance="Ensure Python runtime can execute the target module and verify module name.",
            )

    # -------------------------------------------------------------------------
    # Entry point wrappers: source.molmass.__main__
    # -------------------------------------------------------------------------

    def instance_source_molmass___main__(self) -> Dict[str, Any]:
        """
        Return imported module instance for source.molmass.__main__.

        Returns:
            dict: Contains module reference metadata when available.
        """
        try:
            key = "source.molmass.__main__"
            module = self.modules.get(key)
            if module is None:
                return self._fallback_response(
                    message="Module source.molmass.__main__ is not available in import mode.",
                    guidance="Use run_module_execution_fallback() to execute via python -m molmass.__main__.",
                    import_errors=self.import_errors,
                )
            return self._success_response(
                module_key=key,
                module_name=getattr(module, "__name__", key),
                attributes=sorted([a for a in dir(module) if not a.startswith("_")]),
            )
        except Exception as exc:
            return self._error_response(
                message="Failed to get module instance for source.molmass.__main__.",
                error=exc,
                guidance="Check import configuration and source path mapping.",
            )

    def call_source_molmass___main__(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute source.molmass.__main__ behavior.

        Because __main__ modules often dispatch through side effects or imported main(),
        this method attempts:
          1) direct call of module.main if available
          2) fallback to subprocess module execution

        Args:
            args: Optional CLI-like argument list for fallback execution.

        Returns:
            dict: Unified status dictionary with execution details.
        """
        try:
            module = self.modules.get("source.molmass.__main__")
            if module is not None and hasattr(module, "main") and callable(getattr(module, "main")):
                return self._invoke_callable(getattr(module, "main"), args or [])
            return self._run_cli_fallback("molmass.__main__", argv=args or [])
        except Exception as exc:
            return self._error_response(
                message="Failed to execute source.molmass.__main__ entrypoint.",
                error=exc,
                guidance="Use call_source_molmass_molmass_main() as primary CLI handler when available.",
            )

    # -------------------------------------------------------------------------
    # Entry point wrappers: source.molmass.molmass.main
    # -------------------------------------------------------------------------

    def instance_source_molmass_molmass_main(self) -> Dict[str, Any]:
        """
        Return function metadata for source.molmass.molmass.main.

        Returns:
            dict: Function signature/doc info when available.
        """
        try:
            key = "source.molmass.molmass.main"
            func = self.functions.get(key)
            if func is None:
                return self._fallback_response(
                    message="Function source.molmass.molmass.main is unavailable in import mode.",
                    guidance="Use call_source_molmass___main__() or run_module_execution_fallback().",
                    import_errors=self.import_errors,
                )
            return self._success_response(
                function_key=key,
                function_name=func.__name__,
                signature=str(inspect.signature(func)),
                doc=(inspect.getdoc(func) or ""),
            )
        except Exception as exc:
            return self._error_response(
                message="Failed to get function instance for source.molmass.molmass.main.",
                error=exc,
                guidance="Confirm module source.molmass.molmass is importable and intact.",
            )

    def call_source_molmass_molmass_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call core CLI handler: source.molmass.molmass.main.

        Args:
            *args: Positional arguments forwarded to molmass.main.
            **kwargs: Keyword arguments forwarded to molmass.main.

        Returns:
            dict: Unified result dictionary.
        """
        try:
            key = "source.molmass.molmass.main"
            func = self.functions.get(key)
            if func is None:
                return self._run_cli_fallback("molmass", argv=list(args) if args else None)
            return self._invoke_callable(func, *args, **kwargs)
        except Exception as exc:
            return self._error_response(
                message="Failed to execute source.molmass.molmass.main.",
                error=exc,
                guidance="Verify argument compatibility with molmass.main signature.",
            )

    # -------------------------------------------------------------------------
    # Entry point wrappers: source.molmass.web.main
    # -------------------------------------------------------------------------

    def instance_source_molmass_web_main(self) -> Dict[str, Any]:
        """
        Return function metadata for source.molmass.web.main.

        Returns:
            dict: Function signature/doc info when available.
        """
        try:
            key = "source.molmass.web.main"
            func = self.functions.get(key)
            if func is None:
                return self._fallback_response(
                    message="Function source.molmass.web.main is unavailable in import mode.",
                    guidance="Use call_source_molmass_molmass_main() for non-web usage or configure web runtime.",
                    import_errors=self.import_errors,
                )
            return self._success_response(
                function_key=key,
                function_name=func.__name__,
                signature=str(inspect.signature(func)),
                doc=(inspect.getdoc(func) or ""),
            )
        except Exception as exc:
            return self._error_response(
                message="Failed to get function instance for source.molmass.web.main.",
                error=exc,
                guidance="Confirm source.molmass.web imports correctly in current environment.",
            )

    def call_source_molmass_web_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call web/CGI-style entrypoint: source.molmass.web.main.

        Args:
            *args: Positional arguments forwarded to web.main.
            **kwargs: Keyword arguments forwarded to web.main.

        Returns:
            dict: Unified result dictionary.
        """
        try:
            key = "source.molmass.web.main"
            func = self.functions.get(key)
            if func is None:
                return self._fallback_response(
                    message="Web entrypoint unavailable in import mode.",
                    guidance="Configure web server/CGI context or verify source.molmass.web import path.",
                    import_errors=self.import_errors,
                )
            return self._invoke_callable(func, *args, **kwargs)
        except Exception as exc:
            return self._error_response(
                message="Failed to execute source.molmass.web.main.",
                error=exc,
                guidance="Ensure required web runtime context variables are provided.",
            )

    # -------------------------------------------------------------------------
    # Generic utility methods for MCP orchestration
    # -------------------------------------------------------------------------

    def run_module_execution_fallback(self, module_name: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Public utility to execute any target module with subprocess fallback.

        Args:
            module_name: Module name usable with `python -m`.
            argv: Optional command arguments list.

        Returns:
            dict: Unified execution response.
        """
        return self._run_cli_fallback(module_name=module_name, argv=argv)

    def list_capabilities(self) -> Dict[str, Any]:
        """
        List adapter-exposed capabilities and recommended use order.

        Returns:
            dict: Capability inventory and usage hints.
        """
        try:
            return self._success_response(
                mode=self.mode,
                capabilities=[
                    "instance_source_molmass___main__",
                    "call_source_molmass___main__",
                    "instance_source_molmass_molmass_main",
                    "call_source_molmass_molmass_main",
                    "instance_source_molmass_web_main",
                    "call_source_molmass_web_main",
                    "run_module_execution_fallback",
                    "health_check",
                ],
                recommended_order=[
                    "call_source_molmass_molmass_main",
                    "call_source_molmass___main__",
                    "call_source_molmass_web_main",
                ],
            )
        except Exception as exc:
            return self._error_response(
                message="Failed to list adapter capabilities.",
                error=exc,
                guidance="Reinitialize adapter and retry.",
            )