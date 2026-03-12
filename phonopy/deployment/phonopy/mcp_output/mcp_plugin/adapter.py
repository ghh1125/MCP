import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for phonopy.

    This adapter prioritizes direct module imports and provides graceful CLI fallback hints
    when import-mode execution is unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._cli_commands = {
            "phonopy": "phonopy.scripts.phonopy",
            "phonopy-load": "phonopy.scripts.phonopy_load",
            "phonopy-bandplot": "phonopy.scripts.phonopy_bandplot",
            "phonopy-gruneisen": "phonopy.scripts.phonopy_gruneisen",
            "phonopy-gruneisenplot": "phonopy.scripts.phonopy_gruneisenplot",
            "phonopy-qha": "phonopy.scripts.phonopy_qha",
            "phonopy-qe-born": "phonopy.scripts.phonopy_qe_born",
            "phonopy-vasp-born": "phonopy.scripts.phonopy_vasp_born",
            "phonopy-vasp-efe": "phonopy.scripts.phonopy_vasp_efe",
            "phonopy-calc-convert": "phonopy.scripts.phonopy_calc_convert",
            "phonopy-pdosplot": "phonopy.scripts.phonopy_pdosplot",
            "phonopy-propplot": "phonopy.scripts.phonopy_propplot",
            "phonopy-tdplot": "phonopy.scripts.phonopy_tdplot",
        }
        self._load_core_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
            "guidance": guidance,
        }

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"
            return None

    def _load_core_modules(self) -> None:
        module_candidates = [
            "phonopy",
            "phonopy.api_phonopy",
            "phonopy.api_gruneisen",
            "phonopy.api_qha",
            "phonopy.cui.load",
            "phonopy.cui.phonopy_script",
            "phonopy.interface.calculator",
            "phonopy.interface.phonopy_yaml",
        ]
        for module_path in module_candidates:
            self._safe_import(module_path)

    def _get_module(self, module_path: str) -> Optional[Any]:
        if module_path in self._modules:
            return self._modules[module_path]
        return self._safe_import(module_path)

    def _resolve_callable(self, module_path: str, attr_name: str) -> Dict[str, Any]:
        mod = self._get_module(module_path)
        if mod is None:
            return self._result(
                status="error",
                message=f"Failed to import module '{module_path}'.",
                error=self._import_errors.get(module_path),
                guidance="Verify dependencies (numpy, PyYAML, matplotlib, spglib) and repository source path.",
            )
        fn = getattr(mod, attr_name, None)
        if fn is None or not callable(fn):
            return self._result(
                status="error",
                message=f"Callable '{attr_name}' not found in '{module_path}'.",
                guidance="Check repository version and available module attributes.",
            )
        return self._result(
            status="ok",
            message=f"Resolved callable '{module_path}.{attr_name}'.",
            data={"callable": fn},
        )

    # -------------------------------------------------------------------------
    # Status and capability methods
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            Unified status dictionary with imported modules and import errors.
        """
        return self._result(
            status="ok" if "phonopy" in self._modules else "warning",
            message="Adapter health check completed.",
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "cli_commands": self._cli_commands,
            },
            guidance=(
                "If critical modules failed, install missing dependencies and ensure source path is correct."
                if self._import_errors
                else None
            ),
        )

    def list_cli_commands(self) -> Dict[str, Any]:
        """
        Return known phonopy CLI commands discovered during analysis.

        Returns:
            Unified status dictionary with command-to-module mapping.
        """
        return self._result(
            status="ok",
            message="CLI command map available.",
            data={"commands": self._cli_commands},
        )

    def get_dependency_guidance(self) -> Dict[str, Any]:
        """
        Provide concise runtime dependency guidance inferred from analysis.

        Returns:
            Unified status dictionary with required and optional dependencies.
        """
        return self._result(
            status="ok",
            message="Dependency guidance prepared.",
            data={
                "required": ["python>=3.x", "numpy", "PyYAML", "matplotlib"],
                "optional": ["h5py", "spglib", "symfc", "pypolymlp"],
            },
        )

    # -------------------------------------------------------------------------
    # Class instance creators (identified main classes)
    # -------------------------------------------------------------------------
    def create_phonopy_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_phonopy.Phonopy.

        Parameters:
            *args: Positional arguments forwarded to Phonopy constructor.
            **kwargs: Keyword arguments forwarded to Phonopy constructor.

        Returns:
            Unified status dictionary containing created instance on success.
        """
        resolved = self._resolve_callable("phonopy.api_phonopy", "Phonopy")
        if resolved["status"] != "ok":
            return resolved
        cls = resolved["data"]["callable"]
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message="Phonopy instance created successfully.",
                data={"instance": instance, "class": "phonopy.api_phonopy.Phonopy"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create Phonopy instance.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Validate constructor inputs such as unitcell, supercell_matrix, and primitive_matrix.",
            )

    def create_gruneisen_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_gruneisen.PhonopyGruneisen.

        Parameters:
            *args: Positional arguments for PhonopyGruneisen.
            **kwargs: Keyword arguments for PhonopyGruneisen.

        Returns:
            Unified status dictionary with instance on success.
        """
        resolved = self._resolve_callable("phonopy.api_gruneisen", "PhonopyGruneisen")
        if resolved["status"] != "ok":
            return resolved
        cls = resolved["data"]["callable"]
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message="PhonopyGruneisen instance created successfully.",
                data={"instance": instance, "class": "phonopy.api_gruneisen.PhonopyGruneisen"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create PhonopyGruneisen instance.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Ensure valid phonon objects or expected inputs are provided.",
            )

    def create_qha_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_qha.PhonopyQHA.

        Parameters:
            *args: Positional arguments for PhonopyQHA.
            **kwargs: Keyword arguments for PhonopyQHA.

        Returns:
            Unified status dictionary with instance on success.
        """
        resolved = self._resolve_callable("phonopy.api_qha", "PhonopyQHA")
        if resolved["status"] != "ok":
            return resolved
        cls = resolved["data"]["callable"]
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message="PhonopyQHA instance created successfully.",
                data={"instance": instance, "class": "phonopy.api_qha.PhonopyQHA"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create PhonopyQHA instance.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check volumes, energies, and thermal properties input arrays.",
            )

    # -------------------------------------------------------------------------
    # Function callers (generic, full-path driven)
    # -------------------------------------------------------------------------
    def call_module_function(
        self, module_path: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call any function using full module path and function name.

        Parameters:
            module_path: Full repository module path (e.g., 'phonopy.cui.load').
            function_name: Target callable name in module.
            *args: Positional arguments for the callable.
            **kwargs: Keyword arguments for the callable.

        Returns:
            Unified status dictionary with function result.
        """
        resolved = self._resolve_callable(module_path, function_name)
        if resolved["status"] != "ok":
            return resolved
        fn = resolved["data"]["callable"]
        try:
            value = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Executed {module_path}.{function_name} successfully.",
                data={"result": value},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Execution failed for {module_path}.{function_name}.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Review argument types and required runtime files.",
            )

    # -------------------------------------------------------------------------
    # CLI module fallback helpers (import-first, actionable fallback)
    # -------------------------------------------------------------------------
    def run_cli_entry(self, command_name: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a CLI script module in import mode by calling its main() when available.

        Parameters:
            command_name: One of known commands (e.g., 'phonopy', 'phonopy-qha').
            argv: Optional argument list for scripts supporting argv-based entry.

        Returns:
            Unified status dictionary with execution outcome and fallback guidance.
        """
        if command_name not in self._cli_commands:
            return self._result(
                status="error",
                message=f"Unknown CLI command '{command_name}'.",
                guidance="Use list_cli_commands() to inspect supported commands.",
            )

        module_path = self._cli_commands[command_name]
        mod = self._get_module(module_path)
        if mod is None:
            return self._result(
                status="error",
                message=f"Failed to import CLI module '{module_path}'.",
                error=self._import_errors.get(module_path),
                guidance=f"Run command directly in shell as fallback: {command_name}",
            )

        main_fn = getattr(mod, "main", None)
        if not callable(main_fn):
            return self._result(
                status="warning",
                message=f"No callable main() in '{module_path}'.",
                guidance=f"Run command directly in shell as fallback: {command_name}",
            )

        try:
            if argv is None:
                result = main_fn()
            else:
                sig = inspect.signature(main_fn)
                result = main_fn(argv) if len(sig.parameters) >= 1 else main_fn()
            return self._result(
                status="ok",
                message=f"CLI module '{command_name}' executed in import mode.",
                data={"result": result, "module": module_path},
            )
        except SystemExit as exc:
            return self._result(
                status="ok",
                message=f"CLI '{command_name}' exited with SystemExit.",
                data={"exit_code": getattr(exc, "code", 0)},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"CLI execution failed for '{command_name}'.",
                error=f"{type(exc).__name__}: {exc}",
                guidance=f"Try shell fallback: {command_name} {' '.join(argv or [])}".strip(),
            )

    # -------------------------------------------------------------------------
    # Discovery helpers
    # -------------------------------------------------------------------------
    def inspect_module(self, module_path: str) -> Dict[str, Any]:
        """
        Inspect module attributes to discover classes and functions dynamically.

        Parameters:
            module_path: Full module import path.

        Returns:
            Unified status dictionary with discovered callables.
        """
        mod = self._get_module(module_path)
        if mod is None:
            return self._result(
                status="error",
                message=f"Failed to inspect module '{module_path}'.",
                error=self._import_errors.get(module_path),
                guidance="Verify path setup and dependencies.",
            )

        classes = []
        functions = []
        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
            if inspect.isclass(obj):
                classes.append(name)
            elif inspect.isfunction(obj) or inspect.isbuiltin(obj):
                functions.append(name)

        return self._result(
            status="ok",
            message=f"Inspected module '{module_path}'.",
            data={"classes": classes, "functions": functions},
        )

    def get_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for debugging workflows.

        Returns:
            Unified status dictionary with traceback text.
        """
        return self._result(
            status="ok",
            message="Traceback snapshot collected.",
            data={"traceback": traceback.format_exc()},
        )