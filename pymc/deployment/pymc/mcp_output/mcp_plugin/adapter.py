import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the PyMC repository.

    This adapter focuses on stable, library-level entry points discovered by analysis:
    - Primary package: pymc
    - Developer script modules (non-stable CLI): scripts.run_mypy, scripts.publish_release_notes_to_discourse

    All public methods return a unified dictionary with at least:
    - status: "success" | "error" | "fallback"
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._modules[module_path] = None
            self._import_errors[module_path] = (
                f"Failed to import '{module_path}': {exc}. "
                f"Ensure repository source is available at '{source_path}', and required dependencies are installed."
            )
            return None

    def _initialize_imports(self) -> None:
        self._safe_import("pymc")
        self._safe_import("scripts.run_mypy")
        self._safe_import("scripts.publish_release_notes_to_discourse")

    def _get_module(self, module_path: str) -> Dict[str, Any]:
        module = self._modules.get(module_path)
        if module is not None:
            return self._result("success", module=module)

        err = self._import_errors.get(module_path)
        if err:
            return self._result(
                "fallback",
                message=err,
                guidance="Install required dependencies and verify the source path mapping before retrying.",
            )

        module = self._safe_import(module_path)
        if module is not None:
            return self._result("success", module=module)

        return self._result(
            "fallback",
            message=f"Module '{module_path}' is unavailable.",
            guidance="Retry import after checking environment and dependency setup.",
        )

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status payload including mode, loaded modules, and import errors.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        failed = {k: v for k, v in self._import_errors.items()}
        return self._result(
            "success",
            mode=self.mode,
            source_path=source_path,
            loaded_modules=loaded,
            failed_modules=failed,
        )

    # -------------------------------------------------------------------------
    # Core module accessors and calls: pymc
    # -------------------------------------------------------------------------
    def instance_pymc_module(self) -> Dict[str, Any]:
        """
        Return imported pymc module instance.

        Returns:
            dict: status and module (on success), or fallback information.
        """
        res = self._get_module("pymc")
        if res["status"] != "success":
            return res
        return self._result("success", module=res["module"])

    def call_pymc_attr(self, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a callable attribute from pymc by name.

        Parameters:
            attr_name (str): Name of attribute in pymc module (e.g., 'sample', 'Model', 'fit').
            *args: Positional arguments for callable.
            **kwargs: Keyword arguments for callable.

        Returns:
            dict: Unified status with result data or error/fallback guidance.
        """
        if not attr_name or not isinstance(attr_name, str):
            return self._result(
                "error",
                message="attr_name must be a non-empty string.",
                guidance="Pass a valid attribute name from the pymc module.",
            )

        mod_res = self._get_module("pymc")
        if mod_res["status"] != "success":
            return mod_res

        module = mod_res["module"]
        if not hasattr(module, attr_name):
            return self._result(
                "error",
                message=f"Attribute '{attr_name}' not found in pymc.",
                guidance="Use dir(pymc) to inspect available attributes and retry.",
            )

        target = getattr(module, attr_name)
        if not callable(target):
            return self._result(
                "success",
                attribute=attr_name,
                value=target,
                message="Requested attribute is not callable; returned raw value.",
            )

        try:
            value = target(*args, **kwargs)
            return self._result("success", attribute=attr_name, result=value)
        except Exception as exc:
            return self._result(
                "error",
                attribute=attr_name,
                message=f"Callable execution failed: {exc}",
                guidance="Validate arguments against PyMC API expectations.",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Developer utility module: scripts.run_mypy
    # -------------------------------------------------------------------------
    def instance_scripts_run_mypy(self) -> Dict[str, Any]:
        """
        Return imported scripts.run_mypy module instance.

        Returns:
            dict: status and module object, or fallback guidance.
        """
        res = self._get_module("scripts.run_mypy")
        if res["status"] != "success":
            return res
        return self._result("success", module=res["module"])

    def call_scripts_run_mypy_attr(self, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a callable attribute from scripts.run_mypy.

        Parameters:
            attr_name (str): Attribute/function name in scripts.run_mypy.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status and result/error metadata.
        """
        if not attr_name or not isinstance(attr_name, str):
            return self._result(
                "error",
                message="attr_name must be a non-empty string.",
                guidance="Provide a valid function or callable name from scripts.run_mypy.",
            )

        mod_res = self._get_module("scripts.run_mypy")
        if mod_res["status"] != "success":
            return mod_res

        module = mod_res["module"]
        if not hasattr(module, attr_name):
            return self._result(
                "error",
                message=f"Attribute '{attr_name}' not found in scripts.run_mypy.",
                guidance="Inspect module attributes and retry.",
            )

        target = getattr(module, attr_name)
        if not callable(target):
            return self._result(
                "success",
                attribute=attr_name,
                value=target,
                message="Requested attribute is not callable; returned raw value.",
            )

        try:
            value = target(*args, **kwargs)
            return self._result("success", attribute=attr_name, result=value)
        except Exception as exc:
            return self._result(
                "error",
                attribute=attr_name,
                message=f"Callable execution failed: {exc}",
                guidance="Verify script function arguments and environment.",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Developer utility module: scripts.publish_release_notes_to_discourse
    # -------------------------------------------------------------------------
    def instance_scripts_publish_release_notes_to_discourse(self) -> Dict[str, Any]:
        """
        Return imported scripts.publish_release_notes_to_discourse module instance.

        Returns:
            dict: status and module object, or fallback guidance.
        """
        res = self._get_module("scripts.publish_release_notes_to_discourse")
        if res["status"] != "success":
            return res
        return self._result("success", module=res["module"])

    def call_scripts_publish_release_notes_to_discourse_attr(
        self, attr_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a callable attribute from scripts.publish_release_notes_to_discourse.

        Parameters:
            attr_name (str): Attribute/function name in target module.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status and result/error metadata.
        """
        if not attr_name or not isinstance(attr_name, str):
            return self._result(
                "error",
                message="attr_name must be a non-empty string.",
                guidance="Provide a valid function or callable name from the target module.",
            )

        mod_res = self._get_module("scripts.publish_release_notes_to_discourse")
        if mod_res["status"] != "success":
            return mod_res

        module = mod_res["module"]
        if not hasattr(module, attr_name):
            return self._result(
                "error",
                message=f"Attribute '{attr_name}' not found in scripts.publish_release_notes_to_discourse.",
                guidance="Inspect available attributes and retry.",
            )

        target = getattr(module, attr_name)
        if not callable(target):
            return self._result(
                "success",
                attribute=attr_name,
                value=target,
                message="Requested attribute is not callable; returned raw value.",
            )

        try:
            value = target(*args, **kwargs)
            return self._result("success", attribute=attr_name, result=value)
        except Exception as exc:
            return self._result(
                "error",
                attribute=attr_name,
                message=f"Callable execution failed: {exc}",
                guidance="Validate input parameters and required environment variables.",
                traceback=traceback.format_exc(),
            )