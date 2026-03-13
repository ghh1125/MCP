import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional

# -----------------------------------------------------------------------------
# Path setup (required)
# -----------------------------------------------------------------------------
source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the dalle-mini repository.

    This adapter is intentionally resilient because repository preprocessing failed,
    and no concrete callable symbols were discovered from static analysis.
    It provides:
      - structured import checks for discovered package paths
      - graceful fallback guidance when imports fail
      - uniform dictionary responses with status
      - extensible wrappers for likely generation workflows
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._packages = [
            "deployment.dalle-mini.source",
            "mcp_output.mcp_plugin",
        ]
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, **data: Any) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode, "message": message}
        result.update(data)
        return result

    def _fail(self, message: str, **data: Any) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "message": message}
        result.update(data)
        return result

    def _fallback_guidance(self) -> str:
        return (
            "Import mode is unavailable for one or more required modules. "
            "Verify repository source files exist under the configured source path, "
            "confirm Python version >=3.8, and install likely runtime dependencies "
            "(jax, flax, transformers, Pillow)."
        )

    # -------------------------------------------------------------------------
    # Module management
    # -------------------------------------------------------------------------
    def initialize(self) -> Dict[str, Any]:
        """
        Initialize adapter by importing known package paths from analysis.

        Returns:
            dict: Unified status payload with imported modules and errors.
        """
        self._modules.clear()
        self._import_errors.clear()

        for package_name in self._packages:
            try:
                self._modules[package_name] = importlib.import_module(package_name)
            except Exception as exc:
                self._import_errors[package_name] = f"{exc.__class__.__name__}: {exc}"

        if self._import_errors:
            return self._fail(
                "Initialization completed with import failures.",
                imported=list(self._modules.keys()),
                failed=self._import_errors,
                guidance=self._fallback_guidance(),
            )

        return self._ok(
            "Initialization successful.",
            imported=list(self._modules.keys()),
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter health and import readiness.

        Returns:
            dict: Health status, imported modules, and actionable guidance if needed.
        """
        if not self._modules and not self._import_errors:
            init_result = self.initialize()
            if init_result.get("status") == "error":
                return init_result

        if self._import_errors:
            return self._fail(
                "Adapter is degraded due to import errors.",
                imported=list(self._modules.keys()),
                failed=self._import_errors,
                guidance=self._fallback_guidance(),
            )

        return self._ok(
            "Adapter is healthy.",
            imported=list(self._modules.keys()),
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List expected and currently imported modules.

        Returns:
            dict: Expected module list, imported module list, and import errors.
        """
        return self._ok(
            "Module listing generated.",
            expected=self._packages,
            imported=list(self._modules.keys()),
            failed=self._import_errors,
        )

    def get_module(self, module_path: str) -> Dict[str, Any]:
        """
        Retrieve an imported module by full package path.

        Args:
            module_path (str): Full module path (e.g., 'deployment.dalle-mini.source').

        Returns:
            dict: Status with module object when available.
        """
        if module_path in self._modules:
            return self._ok("Module retrieved.", module=self._modules[module_path])

        if module_path in self._import_errors:
            return self._fail(
                "Module is unavailable due to a previous import failure.",
                module_path=module_path,
                error=self._import_errors[module_path],
                guidance=self._fallback_guidance(),
            )

        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return self._ok("Module imported and retrieved.", module=mod)
        except Exception as exc:
            msg = f"{exc.__class__.__name__}: {exc}"
            self._import_errors[module_path] = msg
            return self._fail(
                "Failed to import requested module.",
                module_path=module_path,
                error=msg,
                guidance=self._fallback_guidance(),
            )

    # -------------------------------------------------------------------------
    # Dynamic symbol utilities (fallback-safe wrappers)
    # -------------------------------------------------------------------------
    def instantiate_class(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Dynamically instantiate a class from a module.

        Args:
            module_path (str): Full module path.
            class_name (str): Name of class to instantiate.
            *args: Positional args for class constructor.
            **kwargs: Keyword args for class constructor.

        Returns:
            dict: Status with created instance or error details.
        """
        try:
            module_result = self.get_module(module_path)
            if module_result.get("status") != "success":
                return module_result

            module = module_result["module"]
            if not hasattr(module, class_name):
                return self._fail(
                    "Class not found in module.",
                    module_path=module_path,
                    class_name=class_name,
                    guidance="Confirm class name spelling and module contents.",
                )

            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                "Class instance created.",
                module_path=module_path,
                class_name=class_name,
                instance=instance,
            )
        except Exception as exc:
            return self._fail(
                "Class instantiation failed.",
                module_path=module_path,
                class_name=class_name,
                error=f"{exc.__class__.__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def call_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Dynamically call a function from a module.

        Args:
            module_path (str): Full module path.
            function_name (str): Name of function to call.
            *args: Positional args for function.
            **kwargs: Keyword args for function.

        Returns:
            dict: Status with function output or error details.
        """
        try:
            module_result = self.get_module(module_path)
            if module_result.get("status") != "success":
                return module_result

            module = module_result["module"]
            if not hasattr(module, function_name):
                return self._fail(
                    "Function not found in module.",
                    module_path=module_path,
                    function_name=function_name,
                    guidance="Confirm function name spelling and module contents.",
                )

            fn = getattr(module, function_name)
            output = fn(*args, **kwargs)
            return self._ok(
                "Function executed successfully.",
                module_path=module_path,
                function_name=function_name,
                output=output,
            )
        except Exception as exc:
            return self._fail(
                "Function execution failed.",
                module_path=module_path,
                function_name=function_name,
                error=f"{exc.__class__.__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Repository-oriented convenience methods (best-effort)
    # -------------------------------------------------------------------------
    def create_pipeline_instance(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Best-effort helper to instantiate a likely pipeline/model class from known packages.

        Args:
            class_name (str): Target class name.
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: Success with instance or consolidated error.
        """
        errors = {}
        for module_path in self._packages:
            result = self.instantiate_class(module_path, class_name, *args, **kwargs)
            if result.get("status") == "success":
                return result
            errors[module_path] = result.get("message")
        return self._fail(
            "Unable to instantiate class from known packages.",
            class_name=class_name,
            attempted_modules=self._packages,
            errors=errors,
            guidance="Inspect repository modules and provide the exact module path.",
        )

    def run_generation(self, function_name: str = "generate", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Best-effort helper to call a likely image generation function.

        Args:
            function_name (str): Function name to invoke, default 'generate'.
            *args: Function positional args.
            **kwargs: Function keyword args.

        Returns:
            dict: Success with output or consolidated failure details.
        """
        errors = {}
        for module_path in self._packages:
            result = self.call_function(module_path, function_name, *args, **kwargs)
            if result.get("status") == "success":
                return result
            errors[module_path] = result.get("message")
        return self._fail(
            "Unable to execute generation function from known packages.",
            function_name=function_name,
            attempted_modules=self._packages,
            errors=errors,
            guidance=(
                "The repository structure could not be fully analyzed. "
                "Provide exact module path and callable name for generation."
            ),
        )

    # -------------------------------------------------------------------------
    # MCP plugin integration surface
    # -------------------------------------------------------------------------
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic MCP execution entrypoint.

        Supported actions:
            - initialize
            - health_check
            - list_modules
            - get_module
            - instantiate_class
            - call_function
            - create_pipeline_instance
            - run_generation

        Args:
            action (str): Operation name.
            params (dict, optional): Parameters for action.

        Returns:
            dict: Unified status response.
        """
        params = params or {}

        try:
            if action == "initialize":
                return self.initialize()
            if action == "health_check":
                return self.health_check()
            if action == "list_modules":
                return self.list_modules()
            if action == "get_module":
                return self.get_module(params.get("module_path", ""))
            if action == "instantiate_class":
                return self.instantiate_class(
                    params.get("module_path", ""),
                    params.get("class_name", ""),
                    *(params.get("args", []) or []),
                    **(params.get("kwargs", {}) or {}),
                )
            if action == "call_function":
                return self.call_function(
                    params.get("module_path", ""),
                    params.get("function_name", ""),
                    *(params.get("args", []) or []),
                    **(params.get("kwargs", {}) or {}),
                )
            if action == "create_pipeline_instance":
                return self.create_pipeline_instance(
                    params.get("class_name", ""),
                    *(params.get("args", []) or []),
                    **(params.get("kwargs", {}) or {}),
                )
            if action == "run_generation":
                return self.run_generation(
                    params.get("function_name", "generate"),
                    *(params.get("args", []) or []),
                    **(params.get("kwargs", {}) or {}),
                )

            return self._fail(
                "Unsupported action requested.",
                action=action,
                supported_actions=[
                    "initialize",
                    "health_check",
                    "list_modules",
                    "get_module",
                    "instantiate_class",
                    "call_function",
                    "create_pipeline_instance",
                    "run_generation",
                ],
            )
        except Exception as exc:
            return self._fail(
                "Unexpected adapter execution error.",
                action=action,
                error=f"{exc.__class__.__name__}: {exc}",
                traceback=traceback.format_exc(),
            )