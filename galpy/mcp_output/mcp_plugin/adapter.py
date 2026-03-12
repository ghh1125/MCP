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
    MCP import-mode adapter for the galpy repository.

    This adapter prefers direct imports from the local `source` directory and
    gracefully degrades to a blackbox-like fallback mode when imports fail.
    All public methods return a unified dictionary with a mandatory `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Core utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success", **extra: Any) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode, "message": message, "data": data}
        if extra:
            result.update(extra)
        return result

    def _err(self, message: str, error: Optional[Exception] = None, **extra: Any) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            result["error"] = str(error)
            result["traceback"] = traceback.format_exc(limit=3)
        if extra:
            result.update(extra)
        return result

    def _fallback(self, action: str, guidance: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": f"Import mode unavailable for action '{action}'.",
            "guidance": guidance,
        }

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None

    def _initialize_imports(self) -> None:
        import_targets = [
            "galpy",
            "galpy.orbit",
            "galpy.potential",
            "galpy.actionAngle",
            "galpy.df",
            "galpy.snapshot",
            "galpy.util",
        ]
        success_count = 0
        for target in import_targets:
            if self._safe_import(target) is not None:
                success_count += 1

        if success_count == 0:
            self.mode = "blackbox"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified result including mode, imported modules, and failures.
        """
        return self._ok(
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            message="Adapter health report generated.",
        )

    # -------------------------------------------------------------------------
    # galpy root-level helpers
    # -------------------------------------------------------------------------
    def get_version(self) -> Dict[str, Any]:
        """
        Retrieve galpy version information.

        Returns:
            dict: Unified result containing the discovered version string.
        """
        if self.mode != "import":
            return self._fallback(
                "get_version",
                "Ensure repository source is present under the expected 'source' path and retry.",
            )
        try:
            galpy_mod = self._modules.get("galpy") or importlib.import_module("galpy")
            version = getattr(galpy_mod, "__version__", None)
            return self._ok(data={"version": version}, message="Version retrieved.")
        except Exception as exc:
            return self._err("Failed to retrieve version from galpy.", exc)

    # -------------------------------------------------------------------------
    # Orbit module management
    # -------------------------------------------------------------------------
    def create_orbit(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of galpy.orbit.Orbits.Orbit.

        Parameters:
            *args: Positional arguments forwarded to Orbit constructor.
            **kwargs: Keyword arguments forwarded to Orbit constructor.

        Returns:
            dict: Unified result with instantiated Orbit object on success.
        """
        if self.mode != "import":
            return self._fallback(
                "create_orbit",
                "Import mode is unavailable. Verify local source checkout and dependencies (numpy/scipy).",
            )
        try:
            orbit_mod = importlib.import_module("galpy.orbit.Orbits")
            Orbit = getattr(orbit_mod, "Orbit")
            obj = Orbit(*args, **kwargs)
            return self._ok(data={"instance": obj}, message="Orbit instance created.")
        except Exception as exc:
            return self._err(
                "Failed to create Orbit instance. Check constructor arguments and physical unit configuration.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Potential module management
    # -------------------------------------------------------------------------
    def create_potential(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a potential class from galpy.potential.

        Parameters:
            class_name (str): Exact class name in galpy.potential namespace.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified result with instantiated potential object.
        """
        if self.mode != "import":
            return self._fallback(
                "create_potential",
                "Switch to import mode by fixing import issues and ensure optional dependencies if required.",
            )
        try:
            pot_mod = self._modules.get("galpy.potential") or importlib.import_module("galpy.potential")
            cls = getattr(pot_mod, class_name, None)
            if cls is None:
                return self._err(
                    f"Potential class '{class_name}' was not found in galpy.potential. "
                    "Use an exact exported class name."
                )
            instance = cls(*args, **kwargs)
            return self._ok(data={"instance": instance, "class_name": class_name}, message="Potential instance created.")
        except Exception as exc:
            return self._err(
                f"Failed to create potential '{class_name}'. Validate parameters and units.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Action-angle module management
    # -------------------------------------------------------------------------
    def create_action_angle(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an action-angle class instance from galpy.actionAngle.

        Parameters:
            class_name (str): Exported class name under galpy.actionAngle.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified result with instantiated action-angle object.
        """
        if self.mode != "import":
            return self._fallback(
                "create_action_angle",
                "Enable import mode and verify compiled extension availability for C-accelerated paths.",
            )
        try:
            aa_mod = self._modules.get("galpy.actionAngle") or importlib.import_module("galpy.actionAngle")
            cls = getattr(aa_mod, class_name, None)
            if cls is None:
                return self._err(
                    f"Action-angle class '{class_name}' not found in galpy.actionAngle. "
                    "Confirm class export in package __init__."
                )
            instance = cls(*args, **kwargs)
            return self._ok(data={"instance": instance, "class_name": class_name}, message="Action-angle instance created.")
        except Exception as exc:
            return self._err(
                f"Failed to create action-angle instance '{class_name}'. Check constructor inputs.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Distribution function module management
    # -------------------------------------------------------------------------
    def create_df(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a distribution-function (DF) class instance from galpy.df.

        Parameters:
            class_name (str): DF class name exported by galpy.df.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified result with DF instance.
        """
        if self.mode != "import":
            return self._fallback(
                "create_df",
                "Resolve import errors and ensure required scientific stack is installed.",
            )
        try:
            df_mod = self._modules.get("galpy.df") or importlib.import_module("galpy.df")
            cls = getattr(df_mod, class_name, None)
            if cls is None:
                return self._err(
                    f"DF class '{class_name}' not found in galpy.df. "
                    "Use a class exported by galpy.df.__init__."
                )
            instance = cls(*args, **kwargs)
            return self._ok(data={"instance": instance, "class_name": class_name}, message="DF instance created.")
        except Exception as exc:
            return self._err(
                f"Failed to create DF instance '{class_name}'. Validate arguments and context.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Snapshot module management
    # -------------------------------------------------------------------------
    def create_snapshot(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create snapshot-related instances from galpy.snapshot.

        Parameters:
            class_name (str): Class name from galpy.snapshot namespace.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified result with created snapshot instance.
        """
        if self.mode != "import":
            return self._fallback(
                "create_snapshot",
                "Install optional snapshot dependencies (for example pynbody) if needed and retry.",
            )
        try:
            snap_mod = self._modules.get("galpy.snapshot") or importlib.import_module("galpy.snapshot")
            cls = getattr(snap_mod, class_name, None)
            if cls is None:
                return self._err(
                    f"Snapshot class '{class_name}' not found in galpy.snapshot. "
                    "Confirm class availability in package exports."
                )
            instance = cls(*args, **kwargs)
            return self._ok(data={"instance": instance, "class_name": class_name}, message="Snapshot instance created.")
        except Exception as exc:
            return self._err(
                f"Failed to create snapshot instance '{class_name}'. Check dependency and parameter compatibility.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Generic callable dispatcher
    # -------------------------------------------------------------------------
    def call_module_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call any function by explicit module path and function name.

        Parameters:
            module_path (str): Fully-qualified module path (for example: 'galpy.util.conversion').
            function_name (str): Exact function name in that module.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            dict: Unified result containing function return value.
        """
        if self.mode != "import":
            return self._fallback(
                "call_module_function",
                "Import mode is unavailable. Confirm source path injection and module importability.",
            )
        try:
            mod = importlib.import_module(module_path)
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found or not callable in module '{module_path}'."
                )
            value = fn(*args, **kwargs)
            return self._ok(
                data={"result": value, "module_path": module_path, "function_name": function_name},
                message="Function call completed.",
            )
        except Exception as exc:
            return self._err(
                f"Function call failed for '{module_path}.{function_name}'. Review arguments and module requirements.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Discovery helpers
    # -------------------------------------------------------------------------
    def list_exports(self, package_path: str) -> Dict[str, Any]:
        """
        List public exports from a package/module.

        Parameters:
            package_path (str): Target module path, e.g. 'galpy.potential'.

        Returns:
            dict: Unified result containing exported names.
        """
        if self.mode != "import":
            return self._fallback(
                "list_exports",
                "Re-enable import mode to introspect package exports.",
            )
        try:
            mod = importlib.import_module(package_path)
            names = [n for n in dir(mod) if not n.startswith("_")]
            return self._ok(data={"package": package_path, "exports": sorted(names)}, message="Exports listed.")
        except Exception as exc:
            return self._err(f"Failed to list exports for '{package_path}'.", exc)

    def list_core_packages(self) -> Dict[str, Any]:
        """
        Return core package targets identified by analysis.

        Returns:
            dict: Unified result containing package names and import status.
        """
        packages = [
            "galpy",
            "galpy.actionAngle",
            "galpy.df",
            "galpy.orbit",
            "galpy.potential",
            "galpy.snapshot",
            "galpy.util",
        ]
        status = {p: (p in self._modules) for p in packages}
        return self._ok(data={"packages": packages, "loaded": status}, message="Core package list prepared.")