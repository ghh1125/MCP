import os
import sys
import io
import json
import traceback
import contextlib
import runpy
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the molmass repository.

    This adapter prioritizes direct Python imports and falls back to CLI/module execution
    behavior when imports are unavailable. All public methods return a unified dictionary:
    {
        "status": "success" | "error",
        "mode": "import" | "fallback-cli",
        "data": ...,
        "error": ...,
        "hint": ...
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._load_errors: List[str] = []
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode, "data": data}
        if extra:
            result.update(extra)
        return result

    def _err(self, message: str, hint: Optional[str] = None, exc: Optional[BaseException] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "error": message}
        if hint:
            payload["hint"] = hint
        if exc is not None:
            payload["details"] = str(exc)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _initialize_imports(self) -> None:
        """
        Try importing repository modules and callable entry points discovered by analysis.
        """
        try:
            import molmass.__main__ as molmass_main_module
            self._imports["molmass.__main__"] = molmass_main_module
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.__main__: {e}")

        try:
            import molmass.molmass as molmass_module
            self._imports["molmass.molmass"] = molmass_module
            self._imports["molmass.molmass.main"] = getattr(molmass_module, "main", None)
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.molmass: {e}")

        try:
            import molmass.web as web_module
            self._imports["molmass.web"] = web_module
            self._imports["molmass.web.main"] = getattr(web_module, "main", None)
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.web: {e}")

        try:
            import molmass.elements_gui as gui_module
            self._imports["molmass.elements_gui"] = gui_module
            self._imports["molmass.elements_gui.main"] = getattr(gui_module, "main", None)
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.elements_gui: {e}")

        try:
            import molmass.elements as elements_module
            self._imports["molmass.elements"] = elements_module
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.elements: {e}")

        try:
            import molmass.elements_descriptions as elements_desc_module
            self._imports["molmass.elements_descriptions"] = elements_desc_module
        except Exception as e:
            self._load_errors.append(f"Failed to import molmass.elements_descriptions: {e}")

        if self._load_errors:
            self.mode = "fallback-cli"

    def health(self) -> Dict[str, Any]:
        """
        Report adapter readiness, import availability, and fallback reasons.

        Returns:
            Unified status dictionary with import summary and detected modules.
        """
        return self._ok(
            data={
                "imports_loaded": sorted(list(self._imports.keys())),
                "load_errors": self._load_errors,
                "import_ready": len(self._load_errors) == 0,
            }
        )

    # -------------------------------------------------------------------------
    # CLI / entry-point adapters
    # -------------------------------------------------------------------------
    def call_python_m_molmass(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute behavior equivalent to: python -m molmass

        Parameters:
            argv: Optional list of command-line arguments passed to module execution.

        Returns:
            Unified status dictionary containing captured stdout/stderr and exit metadata.
        """
        argv = argv or []
        original_argv = sys.argv[:]
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            sys.argv = ["-m", "molmass"] + argv
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                runpy.run_module("molmass", run_name="__main__", alter_sys=True)
            return self._ok(
                data={
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "argv": argv,
                    "runner": "runpy.run_module('molmass', run_name='__main__')",
                }
            )
        except SystemExit as e:
            code = getattr(e, "code", 0)
            status = "success" if code in (0, None) else "error"
            result = {
                "status": status,
                "mode": self.mode,
                "data": {
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "exit_code": code,
                    "argv": argv,
                },
            }
            if status == "error":
                result["error"] = "Module execution exited with a non-zero status."
                result["hint"] = "Check formula syntax and provided CLI flags."
            return result
        except Exception as e:
            return self._err(
                "Failed to execute module mode for molmass.",
                hint="Ensure repository source is present under the configured source path and dependencies are available.",
                exc=e,
            )
        finally:
            sys.argv = original_argv

    def call_molmass_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call molmass.molmass.main directly (console-script equivalent).

        Parameters:
            argv: Optional list of command-line arguments.

        Returns:
            Unified status dictionary with output and return value.
        """
        fn = self._imports.get("molmass.molmass.main")
        if fn is None:
            return self._err(
                "molmass.molmass.main is unavailable.",
                hint="Run health() and resolve import errors; fallback to call_python_m_molmass().",
            )

        argv = argv or []
        original_argv = sys.argv[:]
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            sys.argv = ["molmass"] + argv
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                ret = fn()
            return self._ok(
                data={
                    "return": ret,
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "argv": argv,
                }
            )
        except SystemExit as e:
            code = getattr(e, "code", 0)
            status = "success" if code in (0, None) else "error"
            result = {
                "status": status,
                "mode": self.mode,
                "data": {
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "exit_code": code,
                    "argv": argv,
                },
            }
            if status == "error":
                result["error"] = "molmass main exited with a non-zero status."
                result["hint"] = "Verify CLI arguments and formula input."
            return result
        except Exception as e:
            return self._err(
                "Failed to execute molmass.molmass.main.",
                hint="Use health() output to diagnose import/runtime errors.",
                exc=e,
            )
        finally:
            sys.argv = original_argv

    def call_web_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call molmass.web.main (web/CGI-style runner entry).

        Parameters:
            argv: Optional list of arguments for web main.

        Returns:
            Unified status dictionary with captured output.
        """
        fn = self._imports.get("molmass.web.main")
        if fn is None:
            return self._err(
                "molmass.web.main is unavailable.",
                hint="This entry may require specific web runtime context. Check import readiness with health().",
            )

        argv = argv or []
        original_argv = sys.argv[:]
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        try:
            sys.argv = ["molmass-web"] + argv
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                ret = fn()
            return self._ok(data={"return": ret, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()})
        except SystemExit as e:
            code = getattr(e, "code", 0)
            return self._ok(data={"exit_code": code, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()})
        except Exception as e:
            return self._err(
                "Failed to execute molmass.web.main.",
                hint="If running outside CGI/web context, use library APIs or CLI analysis paths instead.",
                exc=e,
            )
        finally:
            sys.argv = original_argv

    def call_elements_gui_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call molmass.elements_gui.main (desktop GUI launcher).

        Parameters:
            argv: Optional list of arguments for GUI launcher.

        Returns:
            Unified status dictionary. GUI launch may block depending on environment.
        """
        fn = self._imports.get("molmass.elements_gui.main")
        if fn is None:
            return self._err(
                "molmass.elements_gui.main is unavailable.",
                hint="Install/enable tkinter and ensure GUI environment is available.",
            )

        argv = argv or []
        original_argv = sys.argv[:]

        try:
            sys.argv = ["elements-gui"] + argv
            ret = fn()
            return self._ok(data={"return": ret, "message": "GUI entry point invoked."})
        except Exception as e:
            return self._err(
                "Failed to execute GUI entry point.",
                hint="Ensure a desktop environment and tkinter are available; avoid headless runtime for GUI launch.",
                exc=e,
            )
        finally:
            sys.argv = original_argv

    # -------------------------------------------------------------------------
    # Module object accessors (instance methods for identified modules/classes)
    # -------------------------------------------------------------------------
    def instance_molmass_module(self) -> Dict[str, Any]:
        """
        Return loaded molmass.molmass module instance.

        Returns:
            Unified status dictionary with module metadata and exported symbols.
        """
        mod = self._imports.get("molmass.molmass")
        if mod is None:
            return self._err("molmass.molmass module is unavailable.", hint="Check source path and import errors via health().")
        return self._ok(data={"module": "molmass.molmass", "name": getattr(mod, "__name__", None), "file": getattr(mod, "__file__", None)})

    def instance_web_module(self) -> Dict[str, Any]:
        mod = self._imports.get("molmass.web")
        if mod is None:
            return self._err("molmass.web module is unavailable.", hint="Check health() and runtime constraints.")
        return self._ok(data={"module": "molmass.web", "name": getattr(mod, "__name__", None), "file": getattr(mod, "__file__", None)})

    def instance_elements_gui_module(self) -> Dict[str, Any]:
        mod = self._imports.get("molmass.elements_gui")
        if mod is None:
            return self._err("molmass.elements_gui module is unavailable.", hint="tkinter may be missing or GUI dependencies unavailable.")
        return self._ok(data={"module": "molmass.elements_gui", "name": getattr(mod, "__name__", None), "file": getattr(mod, "__file__", None)})

    def instance_elements_module(self) -> Dict[str, Any]:
        mod = self._imports.get("molmass.elements")
        if mod is None:
            return self._err("molmass.elements module is unavailable.", hint="Check health() import errors and source path setup.")
        return self._ok(data={"module": "molmass.elements", "name": getattr(mod, "__name__", None), "file": getattr(mod, "__file__", None)})

    def instance_elements_descriptions_module(self) -> Dict[str, Any]:
        mod = self._imports.get("molmass.elements_descriptions")
        if mod is None:
            return self._err("molmass.elements_descriptions module is unavailable.", hint="Check health() import errors and source path setup.")
        return self._ok(data={"module": "molmass.elements_descriptions", "name": getattr(mod, "__name__", None), "file": getattr(mod, "__file__", None)})

    # -------------------------------------------------------------------------
    # Generic helpers for broad repository feature utilization
    # -------------------------------------------------------------------------
    def call_module_attr(self, module_name: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any callable attribute from a loaded repository module.

        Parameters:
            module_name: Full module key used by adapter (e.g., "molmass.molmass").
            attr_name: Callable attribute name in that module.
            *args, **kwargs: Arguments forwarded to the target callable.

        Returns:
            Unified status dictionary with return value and callable metadata.
        """
        mod = self._imports.get(module_name)
        if mod is None:
            return self._err(
                f"Module '{module_name}' is not loaded.",
                hint="Use health() to inspect available imports and resolve missing modules.",
            )
        target = getattr(mod, attr_name, None)
        if target is None:
            return self._err(
                f"Attribute '{attr_name}' not found in module '{module_name}'.",
                hint="Inspect module exports via list_module_symbols().",
            )
        if not callable(target):
            return self._ok(data={"value": target, "callable": False, "module": module_name, "attribute": attr_name})
        try:
            value = target(*args, **kwargs)
            return self._ok(data={"return": value, "callable": True, "module": module_name, "attribute": attr_name})
        except Exception as e:
            return self._err(
                f"Callable '{module_name}.{attr_name}' execution failed.",
                hint="Verify argument names/types against the repository function signature.",
                exc=e,
            )

    def list_module_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        List public symbols for a loaded module.

        Parameters:
            module_name: Adapter module key (full package path string).

        Returns:
            Unified status dictionary with symbol list.
        """
        mod = self._imports.get(module_name)
        if mod is None:
            return self._err(f"Module '{module_name}' is not loaded.", hint="Check health() for load diagnostics.")
        symbols = [name for name in dir(mod) if not name.startswith("_")]
        return self._ok(data={"module": module_name, "symbols": symbols, "count": len(symbols)})

    def export_state(self) -> Dict[str, Any]:
        """
        Export adapter operational state in JSON-serializable form.

        Returns:
            Unified status dictionary with mode, imports, and load errors.
        """
        state = {
            "mode": self.mode,
            "imports_loaded": sorted(list(self._imports.keys())),
            "load_errors": self._load_errors,
        }
        return self._ok(data=state, extra={"json": json.dumps(state, ensure_ascii=False)})