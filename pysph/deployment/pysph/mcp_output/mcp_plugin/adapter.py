import os
import sys
import traceback
import importlib
import runpy
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the PySPH repository.

    This adapter prioritizes direct Python imports and falls back to CLI/module
    execution where import-based interaction is not feasible.
    """

    # ---------------------------------------------------------------------
    # Initialization and module management
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success"}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, exc: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "message": message}
        if guidance:
            payload["guidance"] = guidance
        if exc is not None:
            payload["exception"] = str(exc)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _load_modules(self) -> None:
        module_names = [
            "pysph.examples.run",
            "pysph.tools.cli",
            "pysph.tools.dump_xdmf",
            "pysph.tools.pysph_to_vtk",
            "pysph.tools.manage_cache",
        ]
        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors[name] = str(e)

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and report import availability.

        Returns:
            Dict with status, mode, loaded modules, and import failures.
        """
        return self._ok(
            {
                "mode": self.mode,
                "loaded_modules": sorted(self._modules.keys()),
                "import_failures": self._import_errors,
                "source_path": source_path,
            }
        )

    # ---------------------------------------------------------------------
    # Generic execution helpers
    # ---------------------------------------------------------------------
    def _run_module_as_main(self, module_name: str) -> Dict[str, Any]:
        try:
            runpy.run_module(module_name, run_name="__main__")
            return self._ok({"module": module_name, "execution": "runpy"})
        except Exception as e:
            return self._err(
                f"Failed to execute module '{module_name}' as __main__.",
                guidance="Verify module availability and runtime dependencies, then retry.",
                exc=e,
            )

    def _run_subprocess(self, argv: List[str]) -> Dict[str, Any]:
        try:
            result = subprocess.run(argv, capture_output=True, text=True, check=False)
            status = "success" if result.returncode == 0 else "error"
            return {
                "status": status,
                "command": argv,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return self._err(
                "Failed to execute subprocess command.",
                guidance="Ensure Python executable and module path are valid.",
                exc=e,
            )

    # ---------------------------------------------------------------------
    # CLI module wrappers identified by analysis
    # ---------------------------------------------------------------------
    def call_pysph_examples_run(self, args: Optional[List[str]] = None, prefer_subprocess: bool = True) -> Dict[str, Any]:
        """
        Execute `python -m pysph.examples.run`.

        Parameters:
            args: Optional list of CLI arguments.
            prefer_subprocess: If True, runs as subprocess to preserve CLI behavior.

        Returns:
            Unified status dictionary with execution details.
        """
        args = args or []
        module_name = "pysph.examples.run"
        if prefer_subprocess:
            return self._run_subprocess([sys.executable, "-m", module_name] + args)
        return self._run_module_as_main(module_name)

    def call_pysph_tools_cli(self, args: Optional[List[str]] = None, prefer_subprocess: bool = True) -> Dict[str, Any]:
        """
        Execute `python -m pysph.tools.cli`.

        Parameters:
            args: Optional list of CLI arguments.
            prefer_subprocess: If True, runs via subprocess for robust CLI semantics.

        Returns:
            Unified status dictionary.
        """
        args = args or []
        module_name = "pysph.tools.cli"
        if prefer_subprocess:
            return self._run_subprocess([sys.executable, "-m", module_name] + args)
        return self._run_module_as_main(module_name)

    def call_pysph_tools_dump_xdmf(self, args: Optional[List[str]] = None, prefer_subprocess: bool = True) -> Dict[str, Any]:
        """
        Execute `python -m pysph.tools.dump_xdmf`.

        Parameters:
            args: Optional list of CLI arguments.
            prefer_subprocess: Use subprocess execution when possible.

        Returns:
            Unified status dictionary with stdout/stderr when subprocess is used.
        """
        args = args or []
        module_name = "pysph.tools.dump_xdmf"
        if prefer_subprocess:
            return self._run_subprocess([sys.executable, "-m", module_name] + args)
        return self._run_module_as_main(module_name)

    def call_pysph_tools_pysph_to_vtk(self, args: Optional[List[str]] = None, prefer_subprocess: bool = True) -> Dict[str, Any]:
        """
        Execute `python -m pysph.tools.pysph_to_vtk`.

        Parameters:
            args: Optional list of CLI arguments.
            prefer_subprocess: If True, execute as subprocess.

        Returns:
            Unified status dictionary.
        """
        args = args or []
        module_name = "pysph.tools.pysph_to_vtk"
        if prefer_subprocess:
            return self._run_subprocess([sys.executable, "-m", module_name] + args)
        return self._run_module_as_main(module_name)

    def call_pysph_tools_manage_cache(self, args: Optional[List[str]] = None, prefer_subprocess: bool = True) -> Dict[str, Any]:
        """
        Execute `python -m pysph.tools.manage_cache`.

        Parameters:
            args: Optional list of CLI arguments.
            prefer_subprocess: If True, execute in subprocess mode.

        Returns:
            Unified status dictionary.
        """
        args = args or []
        module_name = "pysph.tools.manage_cache"
        if prefer_subprocess:
            return self._run_subprocess([sys.executable, "-m", module_name] + args)
        return self._run_module_as_main(module_name)

    # ---------------------------------------------------------------------
    # Import-mode utilities and graceful fallback
    # ---------------------------------------------------------------------
    def import_module(self, module_name: str) -> Dict[str, Any]:
        """
        Import a module dynamically and cache it.

        Parameters:
            module_name: Full module path (e.g., 'pysph.tools.cli').

        Returns:
            Unified status dictionary with module metadata.
        """
        try:
            mod = importlib.import_module(module_name)
            self._modules[module_name] = mod
            return self._ok({"module": module_name, "file": getattr(mod, "__file__", None)})
        except Exception as e:
            return self._err(
                f"Unable to import module '{module_name}'.",
                guidance="Confirm dependency installation (numpy, cython, mako, pyzoltan) and PYTHONPATH configuration.",
                exc=e,
            )

    def call_module_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a module using import-mode dispatch.

        Parameters:
            module_name: Full module path.
            function_name: Target function name.
            *args, **kwargs: Arguments passed to the target callable.

        Returns:
            Unified status dictionary with function result.
        """
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' was not found in module '{module_name}'.",
                    guidance="Inspect module attributes and provide a valid callable name.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module": module_name, "function": function_name, "result": result})
        except Exception as e:
            return self._err(
                f"Failed to call function '{function_name}' from module '{module_name}'.",
                guidance="Validate input arguments and ensure optional dependencies are installed for this code path.",
                exc=e,
            )

    def instantiate_class(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from a module.

        Parameters:
            module_name: Full module path.
            class_name: Class to instantiate.
            *args, **kwargs: Constructor arguments.

        Returns:
            Unified status dictionary with the created instance.
        """
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._err(
                    f"Class '{class_name}' was not found in module '{module_name}'.",
                    guidance="Verify class name and module path before retrying.",
                )
            instance = cls(*args, **kwargs)
            return self._ok({"module": module_name, "class": class_name, "instance": instance})
        except Exception as e:
            return self._err(
                f"Failed to instantiate class '{class_name}' from module '{module_name}'.",
                guidance="Check constructor arguments and module-level prerequisites.",
                exc=e,
            )