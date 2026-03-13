import os
import sys

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)

import importlib
import traceback
from typing import Any, Dict, Optional


class Adapter:
    """
    MCP Import Mode Adapter for BioSPPy repository integration.

    This adapter prioritizes direct import-based execution from local source code
    and provides graceful fallback responses when imports are unavailable.
    """

    # -------------------------------------------------------------------------
    # Initialization and Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state, import mode, and dynamic module registry.
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._classes: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialized = False
        self._initialize_imports()

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

    def _initialize_imports(self) -> None:
        """
        Dynamically import discovered modules/classes from analysis output.

        Targeted imports (from analysis):
        - setup.UploadCommand
        - docs.conf.Mock
        """
        import_targets = {
            "setup": "setup",
            "docs_conf": "docs.conf",
        }

        for key, module_path in import_targets.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._modules[key] = None
                self._import_errors[module_path] = str(exc)

        # Load classes if modules are available
        try:
            setup_mod = self._modules.get("setup")
            self._classes["UploadCommand"] = getattr(setup_mod, "UploadCommand") if setup_mod else None
            if setup_mod and self._classes["UploadCommand"] is None:
                self._import_errors["setup.UploadCommand"] = "Class not found in module."
        except Exception as exc:
            self._classes["UploadCommand"] = None
            self._import_errors["setup.UploadCommand"] = str(exc)

        try:
            conf_mod = self._modules.get("docs_conf")
            self._classes["Mock"] = getattr(conf_mod, "Mock") if conf_mod else None
            if conf_mod and self._classes["Mock"] is None:
                self._import_errors["docs.conf.Mock"] = "Class not found in module."
        except Exception as exc:
            self._classes["Mock"] = None
            self._import_errors["docs.conf.Mock"] = str(exc)

        self._initialized = True

    # -------------------------------------------------------------------------
    # Health and Status
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter readiness, import availability, and diagnostics.

        Returns:
            dict: Unified status payload with loaded modules, class availability,
            and actionable guidance for missing imports.
        """
        loaded_modules = {k: (v is not None) for k, v in self._modules.items()}
        loaded_classes = {k: (v is not None) for k, v in self._classes.items()}
        ok = any(loaded_modules.values()) or any(loaded_classes.values())

        guidance = None
        if not ok:
            guidance = (
                "No target modules could be imported. Ensure repository source is present at "
                "'.../source', verify dependencies from requirements.txt are installed, and retry."
            )

        return self._result(
            status="success" if ok else "fallback",
            message="Adapter health check completed.",
            data={
                "initialized": self._initialized,
                "loaded_modules": loaded_modules,
                "loaded_classes": loaded_classes,
                "import_errors": self._import_errors,
            },
            guidance=guidance,
        )

    # -------------------------------------------------------------------------
    # Class Instance Methods (from analysis.classes)
    # -------------------------------------------------------------------------
    def create_upload_command(self, dist: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create an instance of setup.UploadCommand.

        Parameters:
            dist (Any, optional): Distutils distribution object. If omitted, the
                method attempts a no-arg constructor fallback.

        Returns:
            dict: Unified status response containing instance metadata.
        """
        cls = self._classes.get("UploadCommand")
        if cls is None:
            return self._result(
                status="fallback",
                message="UploadCommand class is unavailable.",
                error=self._import_errors.get("setup.UploadCommand"),
                guidance="Verify that 'source/setup.py' exists and can be imported without side effects.",
            )

        try:
            if dist is not None:
                instance = cls(dist)
            else:
                try:
                    instance = cls()
                except TypeError:
                    return self._result(
                        status="error",
                        message="UploadCommand requires a dist argument.",
                        error="Constructor signature mismatch.",
                        guidance="Pass a valid distutils Distribution instance via 'dist'.",
                    )

            return self._result(
                status="success",
                message="UploadCommand instance created successfully.",
                data={
                    "class": "UploadCommand",
                    "instance_type": str(type(instance)),
                    "has_run_method": hasattr(instance, "run"),
                },
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create UploadCommand instance.",
                error=f"{exc}",
                guidance="Provide a valid dist object and ensure setup.py dependencies are satisfied.",
                data={"traceback": traceback.format_exc()},
            )

    def create_mock(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of docs.conf.Mock.

        Parameters:
            *args: Positional arguments forwarded to Mock constructor.
            **kwargs: Keyword arguments forwarded to Mock constructor.

        Returns:
            dict: Unified status response with instance metadata.
        """
        cls = self._classes.get("Mock")
        if cls is None:
            return self._result(
                status="fallback",
                message="Mock class is unavailable.",
                error=self._import_errors.get("docs.conf.Mock"),
                guidance="Ensure docs/conf.py is importable and optional doc dependencies are mocked correctly.",
            )

        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="success",
                message="Mock instance created successfully.",
                data={
                    "class": "Mock",
                    "instance_type": str(type(instance)),
                },
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create Mock instance.",
                error=f"{exc}",
                guidance="Review constructor arguments and docs configuration import assumptions.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Class Call Methods / Functional Wrappers
    # -------------------------------------------------------------------------
    def call_upload_command_method(
        self,
        method_name: str,
        method_args: Optional[list] = None,
        method_kwargs: Optional[dict] = None,
        dist: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Instantiate UploadCommand and invoke a method dynamically.

        Parameters:
            method_name (str): Name of the method to call on UploadCommand.
            method_args (list, optional): Positional arguments for the method.
            method_kwargs (dict, optional): Keyword arguments for the method.
            dist (Any, optional): Distribution object required by constructor in most setups.

        Returns:
            dict: Unified status response with call result.
        """
        method_args = method_args or []
        method_kwargs = method_kwargs or {}

        inst_resp = self.create_upload_command(dist=dist)
        if inst_resp["status"] != "success":
            return inst_resp

        try:
            cls = self._classes["UploadCommand"]
            instance = cls(dist) if dist is not None else cls()
            if not hasattr(instance, method_name):
                return self._result(
                    status="error",
                    message=f"Method '{method_name}' not found on UploadCommand.",
                    guidance="Check available methods in setup.UploadCommand before invoking.",
                )
            method = getattr(instance, method_name)
            output = method(*method_args, **method_kwargs)
            return self._result(
                status="success",
                message=f"UploadCommand.{method_name} executed successfully.",
                data={"result": output},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute UploadCommand.{method_name}.",
                error=f"{exc}",
                guidance="Validate method arguments and ensure environment supports setup command operations.",
                data={"traceback": traceback.format_exc()},
            )

    def call_mock_method(
        self,
        method_name: str,
        init_args: Optional[list] = None,
        init_kwargs: Optional[dict] = None,
        method_args: Optional[list] = None,
        method_kwargs: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Instantiate docs.conf.Mock and invoke a method dynamically.

        Parameters:
            method_name (str): Method to call on Mock instance.
            init_args (list, optional): Constructor positional arguments.
            init_kwargs (dict, optional): Constructor keyword arguments.
            method_args (list, optional): Method positional arguments.
            method_kwargs (dict, optional): Method keyword arguments.

        Returns:
            dict: Unified status response with invocation details and output.
        """
        init_args = init_args or []
        init_kwargs = init_kwargs or {}
        method_args = method_args or []
        method_kwargs = method_kwargs or {}

        cls = self._classes.get("Mock")
        if cls is None:
            return self._result(
                status="fallback",
                message="Mock class is unavailable.",
                error=self._import_errors.get("docs.conf.Mock"),
                guidance="Ensure docs.conf can be imported from local source tree.",
            )

        try:
            instance = cls(*init_args, **init_kwargs)
            if not hasattr(instance, method_name):
                return self._result(
                    status="error",
                    message=f"Method '{method_name}' not found on Mock.",
                    guidance="Inspect docs.conf.Mock attributes or call a valid method name.",
                )
            method = getattr(instance, method_name)
            output = method(*method_args, **method_kwargs)
            return self._result(
                status="success",
                message=f"Mock.{method_name} executed successfully.",
                data={"result": output},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute Mock.{method_name}.",
                error=f"{exc}",
                guidance="Verify method arguments and constructor inputs.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Generic Fallback/Utility
    # -------------------------------------------------------------------------
    def fallback_blackbox(self, target: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide graceful fallback response when direct import path is unavailable.

        Parameters:
            target (str): Logical operation target.
            payload (dict, optional): Request payload for traceability.

        Returns:
            dict: Fallback response with actionable guidance.
        """
        return self._result(
            status="fallback",
            message=f"Import-mode execution unavailable for target '{target}'.",
            data={"target": target, "payload": payload or {}},
            guidance=(
                "Use blackbox mode for non-importable modules, or install required dependencies "
                "from requirements.txt and re-run in import mode."
            ),
        )