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
    MCP Import Mode Adapter for the PyDy repository.

    This adapter prefers direct module imports from the local `source` directory.
    If imports are unavailable, it gracefully falls back to "blackbox" mode and
    returns actionable guidance in English.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
        }

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"
            return None

    def _load_modules(self) -> None:
        """
        Attempt to import all core modules identified in repository analysis.
        Switches to fallback mode if critical imports fail.
        """
        module_candidates = [
            "pydy",
            "pydy.models",
            "pydy.system",
            "pydy.utils",
            "pydy.codegen.c_code",
            "pydy.codegen.cython_code",
            "pydy.codegen.matrix_generator",
            "pydy.codegen.octave_code",
            "pydy.codegen.ode_function_generators",
            "pydy.viz.camera",
            "pydy.viz.light",
            "pydy.viz.scene",
            "pydy.viz.server",
            "pydy.viz.shapes",
            "pydy.viz.visualization_frame",
        ]

        for path in module_candidates:
            self._safe_import(path)

        critical = ["pydy", "pydy.system", "pydy.codegen.ode_function_generators"]
        if any(c not in self._modules for c in critical):
            self.mode = "blackbox"

    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter health status, current mode, loaded modules, and import errors.
        """
        return self._result(
            status="success",
            message="Adapter status retrieved.",
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
        )

    # -------------------------------------------------------------------------
    # Core API: pydy.system / pydy.models / pydy.utils
    # -------------------------------------------------------------------------
    def create_system(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate pydy.system.System.

        Parameters:
            *args: Positional arguments forwarded to pydy.system.System.
            **kwargs: Keyword arguments forwarded to pydy.system.System.

        Returns:
            dict: Unified status dictionary with the created instance under data.instance.
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Cannot instantiate System in fallback mode.",
                error="Ensure local source includes 'pydy/system.py' and dependencies (sympy, numpy, scipy).",
            )
        try:
            cls = getattr(self._modules["pydy.system"], "System")
            instance = cls(*args, **kwargs)
            return self._result(
                status="success",
                message="System instance created.",
                data={"instance": instance},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create System instance.",
                error=f"{type(exc).__name__}: {exc}",
            )

    def call_models_module(self, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call an attribute from pydy.models.

        Parameters:
            attr_name: Callable attribute name in pydy.models.
            *args/**kwargs: Forwarded call arguments.

        Returns:
            dict: Unified status dictionary with call result.
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Cannot call pydy.models in fallback mode.",
                error="Ensure local source includes 'pydy/models.py'.",
            )
        try:
            mod = self._modules["pydy.models"]
            fn = getattr(mod, attr_name)
            if not callable(fn):
                return self._result(
                    status="error",
                    message="Requested attribute is not callable.",
                    error=f"Attribute '{attr_name}' exists but is not callable.",
                )
            out = fn(*args, **kwargs)
            return self._result(
                status="success",
                message=f"pydy.models.{attr_name} executed.",
                data={"result": out},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute pydy.models.{attr_name}.",
                error=f"{type(exc).__name__}: {exc}",
            )

    def call_utils_module(self, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call an attribute from pydy.utils.
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Cannot call pydy.utils in fallback mode.",
                error="Ensure local source includes 'pydy/utils.py'.",
            )
        try:
            mod = self._modules["pydy.utils"]
            fn = getattr(mod, attr_name)
            if not callable(fn):
                return self._result(
                    status="error",
                    message="Requested attribute is not callable.",
                    error=f"Attribute '{attr_name}' exists but is not callable.",
                )
            out = fn(*args, **kwargs)
            return self._result(
                status="success",
                message=f"pydy.utils.{attr_name} executed.",
                data={"result": out},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute pydy.utils.{attr_name}.",
                error=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Codegen API wrappers
    # -------------------------------------------------------------------------
    def call_codegen_module(self, module_name: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function/class from selected pydy.codegen module.

        Parameters:
            module_name: One of c_code, cython_code, matrix_generator, octave_code, ode_function_generators.
            attr_name: Attribute name to call/construct.
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Cannot call codegen modules in fallback mode.",
                error="Verify local source path and install optional dependencies like cython when needed.",
            )
        path_map = {
            "c_code": "pydy.codegen.c_code",
            "cython_code": "pydy.codegen.cython_code",
            "matrix_generator": "pydy.codegen.matrix_generator",
            "octave_code": "pydy.codegen.octave_code",
            "ode_function_generators": "pydy.codegen.ode_function_generators",
        }
        try:
            module_path = path_map[module_name]
            mod = self._modules[module_path]
            target = getattr(mod, attr_name)
            if callable(target):
                out = target(*args, **kwargs)
                return self._result(
                    status="success",
                    message=f"{module_path}.{attr_name} executed.",
                    data={"result": out},
                )
            return self._result(
                status="success",
                message=f"{module_path}.{attr_name} retrieved.",
                data={"result": target},
            )
        except KeyError:
            return self._result(
                status="error",
                message="Unknown codegen module requested.",
                error=f"Supported module_name values: {list(path_map.keys())}",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute {module_name}.{attr_name}.",
                error=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Visualization API wrappers
    # -------------------------------------------------------------------------
    def create_viz_instance(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a visualization class from pydy.viz modules.

        Search order:
            pydy.viz.camera, pydy.viz.light, pydy.viz.scene, pydy.viz.server,
            pydy.viz.shapes, pydy.viz.visualization_frame
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Cannot instantiate visualization classes in fallback mode.",
                error="Ensure visualization modules exist in local source and JS assets are available for runtime usage.",
            )

        viz_modules = [
            "pydy.viz.camera",
            "pydy.viz.light",
            "pydy.viz.scene",
            "pydy.viz.server",
            "pydy.viz.shapes",
            "pydy.viz.visualization_frame",
        ]

        try:
            for mod_path in viz_modules:
                mod = self._modules.get(mod_path)
                if mod is None:
                    continue
                if hasattr(mod, class_name):
                    cls = getattr(mod, class_name)
                    instance = cls(*args, **kwargs)
                    return self._result(
                        status="success",
                        message=f"{mod_path}.{class_name} instance created.",
                        data={"instance": instance},
                    )
            return self._result(
                status="error",
                message="Requested visualization class was not found.",
                error=f"Class '{class_name}' not found in known pydy.viz modules.",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to create visualization instance for '{class_name}'.",
                error=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Generic callable utility (full coverage fallback)
    # -------------------------------------------------------------------------
    def call(self, module_path: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic executor for any imported module attribute.

        Parameters:
            module_path: Full module path, e.g., 'pydy.system'.
            attr_name: Attribute name in module.
            *args/**kwargs: Arguments for callable attributes.

        Returns:
            dict: Unified status dictionary.
        """
        if self.mode != "import":
            return self._result(
                status="error",
                message="Import mode unavailable. Generic call is disabled in fallback mode.",
                error="Fix import errors and verify source tree integrity before retrying.",
            )
        try:
            if module_path not in self._modules:
                imported = self._safe_import(module_path)
                if imported is None:
                    return self._result(
                        status="error",
                        message=f"Module import failed: {module_path}",
                        error=self._import_errors.get(module_path, "Unknown import error."),
                    )

            mod = self._modules[module_path]
            target = getattr(mod, attr_name)
            if callable(target):
                result = target(*args, **kwargs)
            else:
                result = target

            return self._result(
                status="success",
                message=f"{module_path}.{attr_name} resolved successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute {module_path}.{attr_name}.",
                error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=1)}",
            )