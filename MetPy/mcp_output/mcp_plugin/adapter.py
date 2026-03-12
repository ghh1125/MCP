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
    MCP Import-Mode Adapter for MetPy repository.

    This adapter prefers direct import/use of repository modules and provides a
    graceful fallback "blackbox" mode when imports fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_url = "https://github.com/Unidata/MetPy"
        self.package_root = "src.metpy"
        self._modules: Dict[str, Any] = {}
        self._import_errors: List[str] = []
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success", **extra: Any) -> Dict[str, Any]:
        resp = {"status": "success", "mode": self.mode, "message": message, "data": data}
        if extra:
            resp.update(extra)
        return resp

    def _err(self, message: str, error: Optional[Exception] = None, **extra: Any) -> Dict[str, Any]:
        resp = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            resp["error"] = str(error)
            resp["traceback"] = traceback.format_exc(limit=2)
        if extra:
            resp.update(extra)
        return resp

    def _fallback(self, action: str, guidance: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "action": action,
            "message": "Import mode unavailable. Switched to fallback behavior.",
            "guidance": guidance,
        }

    def _load_modules(self) -> None:
        targets = [
            "src.metpy",
            "src.metpy.calc",
            "src.metpy.interpolate",
            "src.metpy.io",
            "src.metpy.plots",
            "src.metpy.remote",
            "src.metpy.units",
            "src.metpy.constants",
            "src.metpy.xarray",
        ]
        for name in targets:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors.append(f"{name}: {e}")

        if self._import_errors:
            self.mode = "blackbox"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._ok(
            data={
                "repo_url": self.repo_url,
                "package_root": self.package_root,
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # Module management
    # -------------------------------------------------------------------------
    def list_modules(self) -> Dict[str, Any]:
        """
        List managed MetPy modules loaded by this adapter.
        """
        return self._ok(data=sorted(self._modules.keys()))

    def get_module(self, module_name: str) -> Dict[str, Any]:
        """
        Get a loaded module by full path (e.g., 'src.metpy.calc').

        Parameters:
            module_name: Full module import path.
        """
        try:
            mod = self._modules.get(module_name)
            if mod is None:
                return self._err(
                    f"Module '{module_name}' is not loaded.",
                    None,
                    guidance="Call reload_module or verify source path and dependencies.",
                )
            return self._ok(data={"module": module_name, "repr": repr(mod)})
        except Exception as e:
            return self._err("Failed to access module.", e)

    def reload_module(self, module_name: str) -> Dict[str, Any]:
        """
        Reload a specific module by full path.
        """
        try:
            mod = importlib.import_module(module_name)
            mod = importlib.reload(mod)
            self._modules[module_name] = mod
            if self.mode == "blackbox":
                self.mode = "import"
            return self._ok(data={"module": module_name}, message="module reloaded")
        except Exception as e:
            self.mode = "blackbox"
            return self._err(
                f"Failed to reload module '{module_name}'.",
                e,
                guidance="Ensure optional dependencies are installed and module path is correct.",
            )

    # -------------------------------------------------------------------------
    # Generic invocation utilities (comprehensive fallback for unknown symbols)
    # -------------------------------------------------------------------------
    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from a managed module.

        Parameters:
            module_name: Full module path, e.g., 'src.metpy.calc'
            function_name: Function attribute name
            *args/**kwargs: Forwarded to target function
        """
        if self.mode != "import":
            return self._fallback(
                action="call_function",
                guidance="Restore import mode by installing required dependencies: numpy, scipy, pint, packaging.",
            )
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found in module '{module_name}'.",
                    None,
                    guidance="Inspect available names via inspect_module.",
                )
            result = fn(*args, **kwargs)
            return self._ok(data=result, message=f"{module_name}.{function_name} executed")
        except Exception as e:
            return self._err(
                f"Failed to execute function '{function_name}' from '{module_name}'.",
                e,
                guidance="Verify parameter units/types expected by MetPy functions.",
            )

    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class from a managed module.

        Parameters:
            module_name: Full module path, e.g., 'src.metpy.plots'
            class_name: Class attribute name
            *args/**kwargs: Forwarded to class constructor
        """
        if self.mode != "import":
            return self._fallback(
                action="create_instance",
                guidance="Install optional plotting/IO dependencies if constructing advanced classes.",
            )
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._err(
                    f"Class '{class_name}' not found in module '{module_name}'.",
                    None,
                    guidance="Inspect available names via inspect_module.",
                )
            instance = cls(*args, **kwargs)
            return self._ok(data={"class": class_name, "instance_repr": repr(instance)})
        except Exception as e:
            return self._err(
                f"Failed to instantiate class '{class_name}' from '{module_name}'.",
                e,
                guidance="Check constructor arguments and optional dependency availability.",
            )

    def inspect_module(self, module_name: str, include_private: bool = False) -> Dict[str, Any]:
        """
        Inspect attributes of a module and group into classes/functions/others.
        """
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            names = dir(mod)
            if not include_private:
                names = [n for n in names if not n.startswith("_")]
            classes, functions, others = [], [], []
            for n in names:
                obj = getattr(mod, n, None)
                if obj is None:
                    continue
                if isinstance(obj, type):
                    classes.append(n)
                elif callable(obj):
                    functions.append(n)
                else:
                    others.append(n)
            return self._ok(
                data={
                    "module": module_name,
                    "classes": sorted(classes),
                    "functions": sorted(functions),
                    "others": sorted(others),
                }
            )
        except Exception as e:
            return self._err("Failed to inspect module.", e)

    # -------------------------------------------------------------------------
    # High-level convenience wrappers for detected core modules
    # -------------------------------------------------------------------------
    def calc_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.calc."""
        return self.call_function("src.metpy.calc", function_name, *args, **kwargs)

    def interpolate_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.interpolate."""
        return self.call_function("src.metpy.interpolate", function_name, *args, **kwargs)

    def io_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.io."""
        return self.call_function("src.metpy.io", function_name, *args, **kwargs)

    def plots_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.plots."""
        return self.call_function("src.metpy.plots", function_name, *args, **kwargs)

    def remote_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.remote."""
        return self.call_function("src.metpy.remote", function_name, *args, **kwargs)

    def units_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.units."""
        return self.call_function("src.metpy.units", function_name, *args, **kwargs)

    def xarray_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from src.metpy.xarray."""
        return self.call_function("src.metpy.xarray", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dependency and guidance utilities
    # -------------------------------------------------------------------------
    def dependency_status(self) -> Dict[str, Any]:
        """
        Check required and optional dependencies from analysis guidance.
        """
        required = ["numpy", "scipy", "pint", "packaging"]
        optional = ["xarray", "pandas", "matplotlib", "cartopy", "pyproj", "netCDF4", "pooch", "siphon"]

        def check(pkg: str) -> bool:
            try:
                importlib.import_module(pkg)
                return True
            except Exception:
                return False

        req_status = {p: check(p) for p in required}
        opt_status = {p: check(p) for p in optional}
        return self._ok(
            data={
                "required": req_status,
                "optional": opt_status,
                "all_required_available": all(req_status.values()),
            }
        )