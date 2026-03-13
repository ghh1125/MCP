import os
import sys
import traceback
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for molmass repository.

    This adapter attempts direct import first and gracefully falls back to CLI mode
    using `python -m molmass` when direct import is unavailable.
    """

    # ---------------------------------------------------------------------
    # Initialization and module management
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._import_ok = False
        self._import_error: Optional[str] = None
        self._loaded_modules: Dict[str, Any] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _load_modules(self) -> None:
        """
        Try importing molmass modules from local source path.
        """
        try:
            import importlib

            # Full package path from analysis structure, without `source.` prefix.
            self._loaded_modules["deployment.molmass.source.molmass"] = importlib.import_module(
                "deployment.molmass.source.molmass"
            )
            self._loaded_modules["deployment.molmass.source.molmass.molmass"] = importlib.import_module(
                "deployment.molmass.source.molmass.molmass"
            )
            self._loaded_modules["deployment.molmass.source.molmass.elements"] = importlib.import_module(
                "deployment.molmass.source.molmass.elements"
            )
            self._loaded_modules["deployment.molmass.source.molmass.web"] = importlib.import_module(
                "deployment.molmass.source.molmass.web"
            )
            self._loaded_modules["deployment.molmass.source.molmass.__main__"] = importlib.import_module(
                "deployment.molmass.source.molmass.__main__"
            )

            self._import_ok = True
            self.mode = "import"
        except Exception as exc:
            self._import_ok = False
            self.mode = "cli"
            self._import_error = (
                f"Import mode unavailable. Falling back to CLI mode. "
                f"Ensure source files exist under deployment/molmass/source. "
                f"Details: {exc}"
            )

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.
        """
        return self._result(
            "success" if self._import_ok else "fallback",
            import_available=self._import_ok,
            import_error=self._import_error,
            loaded_modules=sorted(list(self._loaded_modules.keys())),
            cli_fallback_command="python -m molmass",
        )

    # ---------------------------------------------------------------------
    # CLI fallback helper
    # ---------------------------------------------------------------------
    def _run_cli(self, args: Optional[List[str]] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute molmass via CLI fallback.

        Parameters:
            args: Additional CLI args passed to `python -m molmass`.
            timeout: Subprocess timeout in seconds.

        Returns:
            Unified status dictionary with stdout/stderr/returncode.
        """
        cmd = [sys.executable, "-m", "molmass"] + (args or [])
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if proc.returncode == 0:
                return self._result(
                    "success",
                    command=cmd,
                    returncode=proc.returncode,
                    stdout=proc.stdout.strip(),
                    stderr=proc.stderr.strip(),
                )
            return self._result(
                "error",
                message=(
                    "CLI command failed. Verify formula input and command arguments. "
                    "Inspect stderr for details."
                ),
                command=cmd,
                returncode=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
            )
        except FileNotFoundError:
            return self._result(
                "error",
                message=(
                    "Python executable not found for CLI fallback. "
                    "Ensure Python is installed and available in PATH."
                ),
                command=cmd,
            )
        except subprocess.TimeoutExpired:
            return self._result(
                "error",
                message=(
                    "CLI execution timed out. Try a simpler input or increase timeout."
                ),
                command=cmd,
                timeout=timeout,
            )
        except Exception as exc:
            return self._result(
                "error",
                message="Unexpected CLI fallback error. Check environment configuration.",
                error=str(exc),
                traceback=traceback.format_exc(),
                command=cmd,
            )

    # ---------------------------------------------------------------------
    # Entry-point method from identified CLI command
    # ---------------------------------------------------------------------
    def call_module_main(self, args: Optional[List[str]] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Call the module entrypoint identified by analysis:
        deployment.molmass.source/molmass.__main__

        Parameters:
            args: Optional command-line style arguments.
            timeout: Timeout used only in CLI fallback mode.

        Returns:
            Unified status dictionary.
        """
        if self._import_ok:
            try:
                main_mod = self._loaded_modules["deployment.molmass.source.molmass.__main__"]
                # Best-effort direct call if main function exists.
                if hasattr(main_mod, "main"):
                    fn = getattr(main_mod, "main")
                    if args is None:
                        ret = fn()
                    else:
                        # Some CLI mains accept argv; if not, TypeError will be handled.
                        ret = fn(args)
                    return self._result("success", result=ret)
                return self._result(
                    "error",
                    message=(
                        "Entrypoint module imported but no callable `main` found. "
                        "Use CLI fallback with explicit arguments."
                    ),
                )
            except TypeError:
                # Retry without args if signature mismatch
                try:
                    ret = self._loaded_modules["deployment.molmass.source.molmass.__main__"].main()
                    return self._result("success", result=ret)
                except Exception as exc:
                    return self._result(
                        "error",
                        message="Failed to execute module main in import mode.",
                        error=str(exc),
                        traceback=traceback.format_exc(),
                    )
            except Exception as exc:
                return self._result(
                    "error",
                    message="Failed to execute module main in import mode.",
                    error=str(exc),
                    traceback=traceback.format_exc(),
                )

        return self._run_cli(args=args, timeout=timeout)

    # ---------------------------------------------------------------------
    # Generic import-mode utility methods to expose repository functionality
    # ---------------------------------------------------------------------
    def list_module_attributes(self, module_key: str) -> Dict[str, Any]:
        """
        List public attributes from an imported module.

        Parameters:
            module_key: One of loaded module keys, e.g.
                        'deployment.molmass.source.molmass.molmass'

        Returns:
            Unified status dictionary with public names.
        """
        if not self._import_ok:
            return self._result(
                "fallback",
                message=(
                    "Import mode unavailable. Use `call_module_main` for CLI fallback operations."
                ),
                import_error=self._import_error,
            )
        try:
            mod = self._loaded_modules[module_key]
            names = [n for n in dir(mod) if not n.startswith("_")]
            return self._result("success", module=module_key, attributes=names)
        except KeyError:
            return self._result(
                "error",
                message="Unknown module key. Call health() to see available loaded modules.",
                module_key=module_key,
            )
        except Exception as exc:
            return self._result(
                "error",
                message="Failed to list module attributes.",
                error=str(exc),
                traceback=traceback.format_exc(),
            )

    def call_function(
        self,
        module_key: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call any function from imported molmass modules dynamically.

        Parameters:
            module_key: Module key from loaded modules.
            function_name: Target function name.
            *args, **kwargs: Arguments for the function.

        Returns:
            Unified status dictionary with function result.
        """
        if not self._import_ok:
            return self._result(
                "fallback",
                message=(
                    "Import mode unavailable. Direct function call is not possible. "
                    "Use `call_module_main` with CLI args."
                ),
                import_error=self._import_error,
            )
        try:
            mod = self._loaded_modules[module_key]
            fn = getattr(mod, function_name)
            if not callable(fn):
                return self._result(
                    "error",
                    message="Resolved attribute is not callable.",
                    module=module_key,
                    function=function_name,
                )
            result = fn(*args, **kwargs)
            return self._result(
                "success",
                module=module_key,
                function=function_name,
                result=result,
            )
        except KeyError:
            return self._result(
                "error",
                message="Unknown module key. Call health() to inspect loaded modules.",
                module_key=module_key,
            )
        except AttributeError:
            return self._result(
                "error",
                message="Function not found in the specified module.",
                module=module_key,
                function=function_name,
            )
        except Exception as exc:
            return self._result(
                "error",
                message=(
                    "Function call failed. Validate argument types and function signature."
                ),
                module=module_key,
                function=function_name,
                error=str(exc),
                traceback=traceback.format_exc(),
            )

    def create_instance(
        self,
        module_key: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create an instance from any class in imported molmass modules.

        Parameters:
            module_key: Module key from loaded modules.
            class_name: Target class name.
            *args, **kwargs: Constructor arguments.

        Returns:
            Unified status dictionary with instance reference.
        """
        if not self._import_ok:
            return self._result(
                "fallback",
                message=(
                    "Import mode unavailable. Class instantiation is not possible in CLI fallback."
                ),
                import_error=self._import_error,
            )
        try:
            mod = self._loaded_modules[module_key]
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._result(
                "success",
                module=module_key,
                class_name=class_name,
                instance=instance,
            )
        except KeyError:
            return self._result(
                "error",
                message="Unknown module key. Call health() to inspect loaded modules.",
                module_key=module_key,
            )
        except AttributeError:
            return self._result(
                "error",
                message="Class not found in the specified module.",
                module=module_key,
                class_name=class_name,
            )
        except Exception as exc:
            return self._result(
                "error",
                message=(
                    "Class instantiation failed. Validate constructor parameters."
                ),
                module=module_key,
                class_name=class_name,
                error=str(exc),
                traceback=traceback.format_exc(),
            )