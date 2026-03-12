import os
import sys
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the SymPy repository.

    This adapter prefers direct Python imports from the checked-out source tree.
    It provides:
    - Capability/status introspection
    - Safe wrappers for key repo entry points identified by analysis
    - Unified dictionary responses with a `status` field
    - Graceful fallback guidance when imports are unavailable
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "ok"}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, hint: Optional[str] = None, exc: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "message": message}
        if hint:
            payload["hint"] = hint
        if exc is not None:
            payload["exception"] = str(exc)
        return payload

    def _load_modules(self) -> None:
        """
        Import modules discovered by analysis.

        Uses full package paths from repository layout.
        """
        targets: Tuple[Tuple[str, str], ...] = (
            ("isympy", "isympy"),
            ("sympy_testing_runtests", "sympy.testing.runtests"),
            ("sympy_init", "sympy.__init__"),
        )
        for key, path in targets:
            try:
                self._modules[key] = __import__(path, fromlist=["*"])
            except Exception as exc:
                self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _module_ready(self, key: str) -> bool:
        return key in self._modules

    # -------------------------------------------------------------------------
    # Adapter status and capabilities
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and module import status.

        Returns:
            dict: Unified status response with loaded modules and import errors.
        """
        return self._ok(
            {
                "mode": self.mode,
                "loaded_modules": list(self._modules.keys()),
                "import_errors": self._import_errors,
            }
        )

    def capabilities(self) -> Dict[str, Any]:
        """
        Return available capabilities based on successful imports.

        Returns:
            dict: Capability flags and fallback guidance.
        """
        return self._ok(
            {
                "mode": self.mode,
                "capabilities": {
                    "isympy_main": self._module_ready("isympy"),
                    "sympy_test_runner": self._module_ready("sympy_testing_runtests"),
                    "sympy_import_check": self._module_ready("sympy_init"),
                },
                "fallback": "If imports fail, ensure repository source is present at '<plugin_root>/source' and retry.",
            }
        )

    # -------------------------------------------------------------------------
    # Entry point wrappers (from analysis)
    # -------------------------------------------------------------------------
    def call_isympy_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Invoke `isympy.py` main entry in import mode.

        Parameters:
            argv (list, optional): Command-like argument list to pass via sys.argv simulation.

        Returns:
            dict: Unified status response with execution result.
        """
        if not self._module_ready("isympy"):
            return self._error(
                "Module import failed: isympy",
                "Verify source path and dependencies, then call health() for details.",
            )
        mod = self._modules["isympy"]
        if not hasattr(mod, "main"):
            return self._error(
                "Entry function not found: isympy.main",
                "Inspect repository version; expected function may have changed.",
            )
        old_argv = sys.argv[:]
        try:
            if argv is not None:
                sys.argv = ["isympy"] + list(argv)
            result = mod.main()
            return self._ok({"result": result})
        except SystemExit as exc:
            return self._ok({"result": None, "system_exit_code": getattr(exc, "code", 0)})
        except Exception as exc:
            return self._error(
                "Failed to execute isympy.main",
                "Check optional runtime dependencies and input arguments.",
                exc,
            )
        finally:
            sys.argv = old_argv

    def call_sympy_test(self, paths: Optional[list] = None, kwargs: Optional[dict] = None) -> Dict[str, Any]:
        """
        Call SymPy test runner via `sympy.testing.runtests`.

        Parameters:
            paths (list, optional): Test paths or selectors.
            kwargs (dict, optional): Extra keyword options passed to test() if available.

        Returns:
            dict: Unified status response with test invocation result.
        """
        if not self._module_ready("sympy_testing_runtests"):
            return self._error(
                "Module import failed: sympy.testing.runtests",
                "Run health() and ensure source tree is available.",
            )
        mod = self._modules["sympy_testing_runtests"]
        test_func = getattr(mod, "test", None)
        if test_func is None:
            return self._error(
                "Function not found: sympy.testing.runtests.test",
                "Use repository-compatible SymPy revision exposing this API.",
            )
        try:
            args = tuple(paths or [])
            options = dict(kwargs or {})
            result = test_func(*args, **options)
            return self._ok({"result": result})
        except Exception as exc:
            return self._error(
                "Failed to execute sympy test runner",
                "Reduce options to minimal arguments and retry.",
                exc,
            )

    def call_sympy_import_probe(self) -> Dict[str, Any]:
        """
        Probe core SymPy import metadata from `sympy.__init__`.

        Returns:
            dict: Unified status response with version and metadata.
        """
        if not self._module_ready("sympy_init"):
            return self._error(
                "Module import failed: sympy.__init__",
                "Ensure mpmath and Python compatibility for this source snapshot.",
            )
        try:
            mod = self._modules["sympy_init"]
            version = getattr(mod, "__version__", None)
            doc = getattr(mod, "__doc__", None)
            return self._ok({"version": version, "doc_present": bool(doc)})
        except Exception as exc:
            return self._error(
                "Failed to probe sympy import metadata",
                "Retry after validating environment and source integrity.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Generic fallback execution helper
    # -------------------------------------------------------------------------
    def fallback_cli_guidance(self) -> Dict[str, Any]:
        """
        Provide concise fallback instructions when import mode is unavailable.

        Returns:
            dict: Unified status response with actionable guidance.
        """
        return self._ok(
            {
                "mode": self.mode,
                "guidance": [
                    "Import mode is preferred for low-intrusive integration.",
                    "If imports fail, verify '<plugin_root>/source' contains the repository files.",
                    "Install required dependency: mpmath.",
                    "Optional dependencies may be needed for advanced features: numpy, scipy, matplotlib, gmpy2, antlr4-python3-runtime, lark, pycosat, z3-solver.",
                    "Use health() to inspect exact import errors.",
                ],
            }
        )

    def debug_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for diagnostics.

        Returns:
            dict: Unified status response with traceback text.
        """
        try:
            tb = traceback.format_exc()
            return self._ok({"traceback": tb})
        except Exception as exc:
            return self._error("Failed to capture traceback", "Call this method inside an exception context.", exc)