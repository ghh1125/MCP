import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the gala repository.

    This adapter prioritizes direct imports from deployment.gala.source-compatible paths
    and provides graceful fallback behavior when imports or runtime calls fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._bootstrap_imports()

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
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"
            return None

    def _bootstrap_imports(self) -> None:
        module_paths = [
            "gala",
            "gala.coordinates",
            "gala.dynamics",
            "gala.dynamics.actionangle",
            "gala.dynamics.mockstream",
            "gala.dynamics.nbody",
            "gala.integrate",
            "gala.integrate.pyintegrators",
            "gala.potential",
            "gala.potential.frame",
            "gala.potential.hamiltonian",
            "gala.potential.potential",
            "gala.potential.scf",
            "gala.units",
            "gala.util",
            "gala.io",
            "numpy",
            "scipy",
            "astropy",
        ]
        for path in module_paths:
            self._safe_import(path)

    def health(self) -> Dict[str, Any]:
        """
        Return adapter import health and loaded-module diagnostics.
        """
        return self._result(
            "success",
            mode=self.mode,
            loaded_modules=sorted(self._modules.keys()),
            import_errors=self._import_errors,
            guidance=(
                "If critical gala modules failed to import, ensure repository source is available "
                "under the expected 'source' directory and dependencies are installed."
            ),
        )

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def _resolve_attr(self, module_path: str, attr_name: str) -> Dict[str, Any]:
        module = self._modules.get(module_path) or self._safe_import(module_path)
        if module is None:
            return self._result(
                "error",
                message=f"Failed to import module '{module_path}'.",
                details=self._import_errors.get(module_path, "Unknown import error."),
                action="Verify source path and required dependencies, then retry.",
            )
        if not hasattr(module, attr_name):
            return self._result(
                "error",
                message=f"Attribute '{attr_name}' not found in module '{module_path}'.",
                action="Check the installed repository version and attribute name.",
            )
        return self._result("success", target=getattr(module, attr_name))

    def _call_function(self, module_path: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        resolved = self._resolve_attr(module_path, func_name)
        if resolved["status"] != "success":
            return resolved
        func = resolved["target"]
        try:
            output = func(*args, **kwargs)
            return self._result("success", module=module_path, function=func_name, result=output)
        except Exception as exc:
            return self._result(
                "error",
                message=f"Function call failed: {module_path}.{func_name}",
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(limit=3),
                action="Validate function arguments and compatible input types.",
            )

    def _create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        resolved = self._resolve_attr(module_path, class_name)
        if resolved["status"] != "success":
            return resolved
        cls = resolved["target"]
        try:
            instance = cls(*args, **kwargs)
            return self._result("success", module=module_path, class_name=class_name, instance=instance)
        except Exception as exc:
            return self._result(
                "error",
                message=f"Class instantiation failed: {module_path}.{class_name}",
                error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(limit=3),
                action="Verify constructor parameters and required units/data formats.",
            )

    # -------------------------------------------------------------------------
    # Discovery utilities (rich fallback when DeepWiki/class-function list missing)
    # -------------------------------------------------------------------------
    def list_available_attributes(self, module_path: str, public_only: bool = True) -> Dict[str, Any]:
        """
        List module attributes for dynamic exploration.

        Parameters:
            module_path: Full module path, e.g., 'gala.potential'.
            public_only: If True, hide private names beginning with underscore.

        Returns:
            Unified status dictionary with discovered attributes.
        """
        module = self._modules.get(module_path) or self._safe_import(module_path)
        if module is None:
            return self._result(
                "error",
                message=f"Unable to inspect module '{module_path}' because import failed.",
                details=self._import_errors.get(module_path, "Unknown import error."),
                action="Install missing dependencies and verify source path.",
            )
        attrs = dir(module)
        if public_only:
            attrs = [a for a in attrs if not a.startswith("_")]
        return self._result("success", module=module_path, attributes=attrs)

    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any function exposed by a loaded/importable module.

        Parameters:
            module_path: Full module path, e.g., 'gala.integrate.timespec'.
            function_name: Function symbol name in module.
            *args/**kwargs: Forwarded to target function.

        Returns:
            Unified status dictionary with call result.
        """
        return self._call_function(module_path, function_name, *args, **kwargs)

    def create_module_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically instantiate any class exposed by a loaded/importable module.

        Parameters:
            module_path: Full module path, e.g., 'gala.dynamics'.
            class_name: Class symbol name in module.
            *args/**kwargs: Forwarded to class constructor.

        Returns:
            Unified status dictionary with created instance.
        """
        return self._create_instance(module_path, class_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Core package convenience methods
    # -------------------------------------------------------------------------
    def import_gala(self) -> Dict[str, Any]:
        """
        Import and return the top-level gala module.
        """
        mod = self._safe_import("gala")
        if mod is None:
            return self._result(
                "error",
                message="Failed to import 'gala'.",
                details=self._import_errors.get("gala", "Unknown import error."),
                action="Ensure required dependencies (numpy, scipy, astropy) are installed.",
            )
        return self._result("success", module="gala", result=mod)

    def get_dependency_status(self) -> Dict[str, Any]:
        """
        Check availability of required/optional dependencies inferred by analysis.
        """
        required = ["python", "numpy", "scipy", "astropy"]
        optional = ["matplotlib", "pyyaml", "h5py", "galpy", "agama"]

        req_status = {}
        for pkg in required:
            if pkg == "python":
                req_status[pkg] = True
            else:
                req_status[pkg] = self._safe_import(pkg) is not None

        opt_status = {pkg: self._safe_import(pkg) is not None for pkg in optional}

        return self._result(
            "success",
            required=req_status,
            optional=opt_status,
            guidance="Install any missing required dependencies before running heavy dynamics/potential workflows.",
        )

    def suggest_fallback(self) -> Dict[str, Any]:
        """
        Provide actionable guidance for fallback mode when import execution is incomplete.
        """
        if not self._import_errors:
            return self._result(
                "success",
                message="Import mode is healthy; fallback mode is not required.",
            )
        return self._result(
            "warning",
            message="Some modules failed to import. Use dynamic calls only for available modules.",
            import_errors=self._import_errors,
            action_items=[
                "Confirm the source directory is mounted at the expected location.",
                "Install required dependencies: numpy, scipy, astropy.",
                "Install optional packages as needed: matplotlib, pyyaml, h5py, galpy, agama.",
                "Retry health() and then targeted module imports.",
            ],
        )