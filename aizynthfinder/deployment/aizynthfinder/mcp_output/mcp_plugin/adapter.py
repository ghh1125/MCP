import os
import sys
import traceback
import importlib
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the aizynthfinder repository.

    This adapter prefers direct Python imports and provides a CLI fallback path.
    It exposes methods for key modules and commands identified in repository analysis:
    - aizynthfinder.interfaces.aizynthcli
    - aizynthfinder.tools.cat_output
    - aizynthfinder.tools.download_public_data
    - aizynthfinder.tools.make_stock
    - aizynthfinder.aizynthfinder (programmatic entry module)

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
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._module_paths = {
            "aizynthcli": "aizynthfinder.interfaces.aizynthcli",
            "cat_output": "aizynthfinder.tools.cat_output",
            "download_public_data": "aizynthfinder.tools.download_public_data",
            "make_stock": "aizynthfinder.tools.make_stock",
            "finder": "aizynthfinder.aizynthfinder",
        }
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _load_modules(self) -> None:
        for key, module_path in self._module_paths.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._modules[key] = None
                self._import_errors[key] = (
                    f"Failed to import '{module_path}'. "
                    f"Ensure project dependencies are installed (e.g., rdkit, onnxruntime, numpy, pandas, PyYAML, networkx). "
                    f"Original error: {exc}"
                )

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import availability.

        Returns:
            dict: Unified status payload with loaded modules, missing modules, and actionable hints.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        missing = [k for k, v in self._modules.items() if v is None]
        status = "success" if not missing else "fallback"
        return self._result(
            status,
            mode=self.mode,
            loaded_modules=loaded,
            missing_modules=missing,
            import_errors=self._import_errors,
            guidance=(
                "Install required dependencies and verify source path mapping if modules are missing."
                if missing
                else "All key modules imported successfully."
            ),
        )

    # -------------------------------------------------------------------------
    # Internal execution helpers
    # -------------------------------------------------------------------------
    def _run_subprocess(self, cmd: List[str], timeout: int = 3600) -> Dict[str, Any]:
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                check=False,
            )
            if proc.returncode == 0:
                return self._result(
                    "success",
                    command=cmd,
                    returncode=proc.returncode,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                )
            return self._result(
                "error",
                command=cmd,
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                message="CLI command failed. Review stderr for corrective action.",
            )
        except subprocess.TimeoutExpired:
            return self._result(
                "error",
                command=cmd,
                message="CLI command timed out. Increase timeout or reduce workload.",
            )
        except Exception as exc:
            return self._result(
                "error",
                command=cmd,
                message=f"Failed to execute CLI command: {exc}",
            )

    def _call_module_main(self, module_key: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        argv = argv or []
        module = self._modules.get(module_key)
        if module is None:
            return self._result(
                "fallback",
                message=self._import_errors.get(module_key, "Module import unavailable."),
                guidance="Using subprocess fallback is recommended.",
            )

        candidates = ["main", "cli", "run"]
        for name in candidates:
            func = getattr(module, name, None)
            if callable(func):
                try:
                    result = func(argv) if self._accepts_argv(func) else func()
                    return self._result(
                        "success",
                        module=self._module_paths[module_key],
                        called=name,
                        result=result,
                    )
                except SystemExit as exc:
                    return self._result(
                        "success" if int(getattr(exc, "code", 0) or 0) == 0 else "error",
                        module=self._module_paths[module_key],
                        called=name,
                        exit_code=getattr(exc, "code", None),
                        message="Module executed with SystemExit.",
                    )
                except Exception as exc:
                    return self._result(
                        "error",
                        module=self._module_paths[module_key],
                        called=name,
                        message=f"Imported module execution failed: {exc}",
                        traceback=traceback.format_exc(),
                    )

        return self._result(
            "fallback",
            module=self._module_paths[module_key],
            message="No callable entrypoint found in imported module.",
            guidance="Use CLI fallback method with explicit arguments.",
        )

    def _accepts_argv(self, func: Any) -> bool:
        try:
            import inspect
            sig = inspect.signature(func)
            return len(sig.parameters) > 0
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Instance methods for imported modules (as requested)
    # -------------------------------------------------------------------------
    def instance_aizynthcli(self) -> Dict[str, Any]:
        """
        Return metadata and readiness for `aizynthfinder.interfaces.aizynthcli`.

        Returns:
            dict: status payload containing module availability and path.
        """
        key = "aizynthcli"
        mod = self._modules.get(key)
        if mod is None:
            return self._result(
                "error",
                module=self._module_paths[key],
                message=self._import_errors.get(key, "Module not available."),
            )
        return self._result("success", module=self._module_paths[key], instance=repr(mod))

    def instance_cat_output(self) -> Dict[str, Any]:
        """
        Return metadata and readiness for `aizynthfinder.tools.cat_output`.

        Returns:
            dict: status payload containing module availability and path.
        """
        key = "cat_output"
        mod = self._modules.get(key)
        if mod is None:
            return self._result(
                "error",
                module=self._module_paths[key],
                message=self._import_errors.get(key, "Module not available."),
            )
        return self._result("success", module=self._module_paths[key], instance=repr(mod))

    def instance_download_public_data(self) -> Dict[str, Any]:
        """
        Return metadata and readiness for `aizynthfinder.tools.download_public_data`.

        Returns:
            dict: status payload containing module availability and path.
        """
        key = "download_public_data"
        mod = self._modules.get(key)
        if mod is None:
            return self._result(
                "error",
                module=self._module_paths[key],
                message=self._import_errors.get(key, "Module not available."),
            )
        return self._result("success", module=self._module_paths[key], instance=repr(mod))

    def instance_make_stock(self) -> Dict[str, Any]:
        """
        Return metadata and readiness for `aizynthfinder.tools.make_stock`.

        Returns:
            dict: status payload containing module availability and path.
        """
        key = "make_stock"
        mod = self._modules.get(key)
        if mod is None:
            return self._result(
                "error",
                module=self._module_paths[key],
                message=self._import_errors.get(key, "Module not available."),
            )
        return self._result("success", module=self._module_paths[key], instance=repr(mod))

    def instance_finder_module(self) -> Dict[str, Any]:
        """
        Return metadata and readiness for `aizynthfinder.aizynthfinder`.

        Returns:
            dict: status payload containing module availability and path.
        """
        key = "finder"
        mod = self._modules.get(key)
        if mod is None:
            return self._result(
                "error",
                module=self._module_paths[key],
                message=self._import_errors.get(key, "Module not available."),
            )
        return self._result("success", module=self._module_paths[key], instance=repr(mod))

    # -------------------------------------------------------------------------
    # Call methods for identified CLI functions/commands
    # -------------------------------------------------------------------------
    def call_aizynthcli(self, args: Optional[List[str]] = None, use_cli_fallback: bool = True) -> Dict[str, Any]:
        """
        Execute the main retrosynthesis CLI workflow.

        Args:
            args: List of command-line style arguments for aizynthcli.
            use_cli_fallback: If True, fallback to subprocess invocation when import execution is unavailable.

        Returns:
            dict: Unified status payload with execution result.
        """
        args = args or []
        imported_run = self._call_module_main("aizynthcli", args)
        if imported_run["status"] in {"success", "error"} or not use_cli_fallback:
            return imported_run
        return self._run_subprocess(["aizynthcli"] + args)

    def call_cat_aizynth_output(self, args: Optional[List[str]] = None, use_cli_fallback: bool = True) -> Dict[str, Any]:
        """
        Execute output concatenation/inspection utility.

        Args:
            args: List of command-line style arguments for cat_aizynth_output.
            use_cli_fallback: If True, fallback to subprocess command.

        Returns:
            dict: Unified status payload.
        """
        args = args or []
        imported_run = self._call_module_main("cat_output", args)
        if imported_run["status"] in {"success", "error"} or not use_cli_fallback:
            return imported_run
        return self._run_subprocess(["cat_aizynth_output"] + args)

    def call_download_public_data(self, args: Optional[List[str]] = None, use_cli_fallback: bool = True) -> Dict[str, Any]:
        """
        Download public model and data assets used by AiZynthFinder.

        Args:
            args: List of command-line style arguments for download_public_data.
            use_cli_fallback: If True, fallback to subprocess command.

        Returns:
            dict: Unified status payload.
        """
        args = args or []
        imported_run = self._call_module_main("download_public_data", args)
        if imported_run["status"] in {"success", "error"} or not use_cli_fallback:
            return imported_run
        return self._run_subprocess(["download_public_data"] + args)

    def call_make_stock(self, args: Optional[List[str]] = None, use_cli_fallback: bool = True) -> Dict[str, Any]:
        """
        Build stock artifacts/databases for stock availability checks.

        Args:
            args: List of command-line style arguments for make_stock.
            use_cli_fallback: If True, fallback to subprocess command.

        Returns:
            dict: Unified status payload.
        """
        args = args or []
        imported_run = self._call_module_main("make_stock", args)
        if imported_run["status"] in {"success", "error"} or not use_cli_fallback:
            return imported_run
        return self._run_subprocess(["make_stock"] + args)

    # -------------------------------------------------------------------------
    # Programmatic finder entry (best-effort import mode)
    # -------------------------------------------------------------------------
    def call_finder_entry(self, method_name: str = "main", kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Attempt to call an entry method in `aizynthfinder.aizynthfinder`.

        Args:
            method_name: Name of callable attribute in the module.
            kwargs: Keyword arguments for the target callable.

        Returns:
            dict: Unified status payload.
        """
        kwargs = kwargs or {}
        module = self._modules.get("finder")
        if module is None:
            return self._result(
                "error",
                module=self._module_paths["finder"],
                message=self._import_errors.get("finder", "Finder module unavailable."),
            )
        func = getattr(module, method_name, None)
        if not callable(func):
            return self._result(
                "error",
                module=self._module_paths["finder"],
                message=f"Method '{method_name}' not found or not callable.",
                guidance="Use an existing callable in aizynthfinder.aizynthfinder or switch to CLI mode.",
            )
        try:
            result = func(**kwargs)
            return self._result(
                "success",
                module=self._module_paths["finder"],
                called=method_name,
                result=result,
            )
        except Exception as exc:
            return self._result(
                "error",
                module=self._module_paths["finder"],
                called=method_name,
                message=f"Finder call failed: {exc}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Generic dispatcher
    # -------------------------------------------------------------------------
    def call(self, command: str, args: Optional[List[str]] = None, kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic command dispatcher.

        Supported commands:
            - "aizynthcli"
            - "cat_aizynth_output"
            - "download_public_data"
            - "make_stock"
            - "finder_entry"

        Args:
            command: Command key.
            args: CLI-style args for command methods.
            kwargs: Extra kwargs (used by finder_entry).

        Returns:
            dict: Unified status payload.
        """
        args = args or []
        kwargs = kwargs or {}

        if command == "aizynthcli":
            return self.call_aizynthcli(args=args)
        if command == "cat_aizynth_output":
            return self.call_cat_aizynth_output(args=args)
        if command == "download_public_data":
            return self.call_download_public_data(args=args)
        if command == "make_stock":
            return self.call_make_stock(args=args)
        if command == "finder_entry":
            method_name = kwargs.pop("method_name", "main")
            return self.call_finder_entry(method_name=method_name, kwargs=kwargs)

        return self._result(
            "error",
            message=f"Unsupported command '{command}'.",
            supported_commands=[
                "aizynthcli",
                "cat_aizynth_output",
                "download_public_data",
                "make_stock",
                "finder_entry",
            ],
        )