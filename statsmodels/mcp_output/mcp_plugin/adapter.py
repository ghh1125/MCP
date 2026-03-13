import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the statsmodels repository.

    This adapter attempts to load modules from the local source tree (source/statsmodels).
    It exposes utility methods that wrap commonly useful entry points identified in analysis:
    - statsmodels.api
    - statsmodels.formula.api
    - statsmodels.tsa.api
    - statsmodels.stats.api
    - statsmodels.graphics.api
    - statsmodels.tools.print_version (diagnostic module)

    All methods return a unified dictionary format:
    {
        "status": "success" | "error" | "fallback",
        "message": str,
        ...additional fields...
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "success", "message": message}
        payload.update(kwargs)
        return payload

    def _err(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "error", "message": message}
        payload.update(kwargs)
        return payload

    def _fallback(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "fallback", "message": message}
        payload.update(kwargs)
        return payload

    def _safe_import(self, module_path: str, alias: str) -> None:
        try:
            self._modules[alias] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[alias] = None
            self._import_errors[alias] = f"{type(exc).__name__}: {exc}"

    def _initialize_imports(self) -> None:
        self._safe_import("statsmodels", "statsmodels_root")
        self._safe_import("statsmodels.api", "sm_api")
        self._safe_import("statsmodels.formula.api", "smf_api")
        self._safe_import("statsmodels.tsa.api", "tsa_api")
        self._safe_import("statsmodels.stats.api", "stats_api")
        self._safe_import("statsmodels.graphics.api", "graphics_api")
        self._safe_import("statsmodels.tools.print_version", "print_version_mod")

    def _require_module(self, alias: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        mod = self._modules.get(alias)
        if mod is not None:
            return self._ok("Module is available.", module=alias)
        msg = self._import_errors.get(alias, "Module import failed for unknown reasons.")
        help_msg = guidance or "Verify local source path and required dependencies are installed."
        return self._fallback(
            f"Module '{alias}' is unavailable. {msg}",
            guidance=help_msg,
            import_error=msg,
            module=alias,
        )

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        available = [k for k, v in self._modules.items() if v is not None]
        unavailable = {k: self._import_errors.get(k, "Unknown error") for k, v in self._modules.items() if v is None}
        return self._ok(
            "Adapter initialized.",
            mode=self.mode,
            source_path=source_path,
            available_modules=available,
            unavailable_modules=unavailable,
        )

    def get_version(self) -> Dict[str, Any]:
        mod = self._modules.get("statsmodels_root")
        if mod is None:
            return self._require_module("statsmodels_root", "Ensure source/statsmodels is present and importable.")
        version = getattr(mod, "__version__", None)
        return self._ok("Version retrieved.", version=version)

    def call_print_version_module(self) -> Dict[str, Any]:
        check = self._require_module("print_version_mod", "Try importing statsmodels.tools.print_version directly.")
        if check["status"] != "success":
            return check
        mod = self._modules["print_version_mod"]
        attrs = [a for a in dir(mod) if not a.startswith("_")]
        return self._ok(
            "Diagnostic module loaded.",
            module="statsmodels.tools.print_version",
            public_attributes=attrs,
            note="This module is intended for environment/version diagnostics.",
        )

    # -------------------------------------------------------------------------
    # API module accessors
    # -------------------------------------------------------------------------
    def instance_statsmodels_api(self) -> Dict[str, Any]:
        return self._require_module("sm_api", "Install required dependencies: numpy, scipy, pandas, patsy, packaging.")

    def instance_formula_api(self) -> Dict[str, Any]:
        return self._require_module("smf_api", "Ensure patsy is installed for formula support.")

    def instance_tsa_api(self) -> Dict[str, Any]:
        return self._require_module("tsa_api", "Ensure time-series dependencies are available (numpy/scipy/pandas).")

    def instance_stats_api(self) -> Dict[str, Any]:
        return self._require_module("stats_api", "Ensure core scientific dependencies are available.")

    def instance_graphics_api(self) -> Dict[str, Any]:
        return self._require_module("graphics_api", "Install matplotlib for plotting-related features.")

    # -------------------------------------------------------------------------
    # Dynamic class/function execution utilities
    # -------------------------------------------------------------------------
    def create_instance(self, module_alias: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from an imported module alias.

        Parameters:
            module_alias: One of the imported aliases (e.g., 'sm_api', 'tsa_api').
            class_name: Exact class name to instantiate.
            *args, **kwargs: Constructor parameters.

        Returns:
            Unified status dictionary with created instance (if successful).
        """
        check = self._require_module(module_alias)
        if check["status"] != "success":
            return check
        mod = self._modules[module_alias]
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                "Class instance created.",
                module_alias=module_alias,
                class_name=class_name,
                instance=instance,
            )
        except AttributeError:
            return self._err(
                f"Class '{class_name}' was not found in module alias '{module_alias}'.",
                guidance="Verify class name and module alias.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate class '{class_name}'.",
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def call_function(self, module_alias: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from an imported module alias.

        Parameters:
            module_alias: One of the imported aliases (e.g., 'sm_api', 'smf_api', 'tsa_api').
            function_name: Function name to call.
            *args, **kwargs: Function parameters.

        Returns:
            Unified status dictionary with function result.
        """
        check = self._require_module(module_alias)
        if check["status"] != "success":
            return check
        mod = self._modules[module_alias]
        try:
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok(
                "Function executed successfully.",
                module_alias=module_alias,
                function_name=function_name,
                result=result,
            )
        except AttributeError:
            return self._err(
                f"Function '{function_name}' was not found in module alias '{module_alias}'.",
                guidance="Verify function name and module alias.",
            )
        except Exception as exc:
            return self._err(
                f"Function '{function_name}' execution failed.",
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Convenience wrappers for common statsmodels usage
    # -------------------------------------------------------------------------
    def list_public_members(self, module_alias: str) -> Dict[str, Any]:
        check = self._require_module(module_alias)
        if check["status"] != "success":
            return check
        mod = self._modules[module_alias]
        public = [a for a in dir(mod) if not a.startswith("_")]
        return self._ok("Public members listed.", module_alias=module_alias, members=public)

    def run_module_function(self, full_module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Import any module by full path and execute one function.

        Parameters:
            full_module_path: e.g., 'statsmodels.tools.print_version'
            function_name: function to call inside module
            *args, **kwargs: function arguments

        Returns:
            Unified status dictionary.
        """
        try:
            mod = importlib.import_module(full_module_path)
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok(
                "Module function executed successfully.",
                module=full_module_path,
                function=function_name,
                result=result,
            )
        except ModuleNotFoundError:
            return self._fallback(
                f"Module '{full_module_path}' could not be imported.",
                guidance="Check source path and ensure repository source files are available.",
            )
        except AttributeError:
            return self._err(
                f"Function '{function_name}' was not found in module '{full_module_path}'.",
                guidance="Verify function name and module path.",
            )
        except Exception as exc:
            return self._err(
                f"Execution failed for '{full_module_path}.{function_name}'.",
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def supported_modules(self) -> Dict[str, Any]:
        return self._ok(
            "Supported module aliases returned.",
            aliases={
                "statsmodels_root": "statsmodels",
                "sm_api": "statsmodels.api",
                "smf_api": "statsmodels.formula.api",
                "tsa_api": "statsmodels.tsa.api",
                "stats_api": "statsmodels.stats.api",
                "graphics_api": "statsmodels.graphics.api",
                "print_version_mod": "statsmodels.tools.print_version",
            },
            required_dependencies=["numpy", "scipy", "pandas", "patsy", "packaging"],
            optional_dependencies=["matplotlib", "cvxopt", "joblib", "pytest", "x13as external binary"],
        )