import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for poliastro repository source code.

    This adapter tries to import repository modules directly from local source checkout,
    exposes structured helper methods for key modules, and provides graceful fallback
    behavior if imports fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_core_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "ok") -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode, "message": message}
        if data:
            result.update(data)
        return result

    def _fail(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if hint:
            payload["hint"] = hint
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None

    def _load_core_modules(self) -> None:
        candidates = [
            "src.poliastro",
            "src.poliastro.bodies",
            "src.poliastro.constants",
            "src.poliastro.ephem",
            "src.poliastro.io",
            "src.poliastro.maneuver",
            "src.poliastro.util",
            "src.poliastro.examples",
            "src.poliastro.frames",
            "src.poliastro.plotting",
            "src.poliastro.earth",
            "src.poliastro.sensors",
            "src.poliastro.spheroid_location",
            "src.poliastro.threebody",
            "src.poliastro.twobody",
            "src.poliastro.twobody.orbit.scalar",
            "src.poliastro.twobody.orbit.creation",
            "src.poliastro.twobody.propagation",
            "src.poliastro.iod.izzo",
            "src.poliastro.iod.vallado",
        ]
        for mod in candidates:
            self._import_module(mod)

    # -------------------------------------------------------------------------
    # Adapter diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health information.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(list(self._modules.keys())),
                "import_errors": self._import_errors,
                "import_ready": len(self._modules) > 0,
            },
            message="Adapter health check completed",
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List all modules currently loaded by this adapter.

        Returns:
            dict: Unified status payload with module list.
        """
        return self._ok({"modules": sorted(self._modules.keys())}, message="Loaded module list")

    # -------------------------------------------------------------------------
    # Generic dynamic invocation helpers
    # -------------------------------------------------------------------------
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically create an instance of a class from a given module.

        Parameters:
            module_path (str): Full module path, e.g. 'src.poliastro.twobody.orbit.scalar'.
            class_name (str): Name of class to instantiate.
            *args: Positional arguments forwarded to class constructor.
            **kwargs: Keyword arguments forwarded to class constructor.

        Returns:
            dict: Unified status payload with instance object on success.
        """
        try:
            mod = self._modules.get(module_path) or self._import_module(module_path)
            if mod is None:
                return self._fail(
                    f"Module import failed: {module_path}",
                    hint="Verify repository source is present under the local 'source' directory.",
                )
            if not hasattr(mod, class_name):
                return self._fail(
                    f"Class '{class_name}' not found in module '{module_path}'.",
                    hint="Check class name spelling and module path.",
                )
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, message=f"Instance created: {module_path}.{class_name}")
        except Exception as exc:
            return self._fail(
                f"Failed to create instance for {module_path}.{class_name}",
                error=exc,
                hint="Review constructor arguments and required dependencies.",
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from a given module.

        Parameters:
            module_path (str): Full module path.
            function_name (str): Function name in target module.
            *args: Positional args for function.
            **kwargs: Keyword args for function.

        Returns:
            dict: Unified status payload with function result on success.
        """
        try:
            mod = self._modules.get(module_path) or self._import_module(module_path)
            if mod is None:
                return self._fail(
                    f"Module import failed: {module_path}",
                    hint="Check source path configuration and local repository contents.",
                )
            if not hasattr(mod, function_name):
                return self._fail(
                    f"Function '{function_name}' not found in module '{module_path}'.",
                    hint="Inspect module API and update function name accordingly.",
                )
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"Function call succeeded: {module_path}.{function_name}")
        except Exception as exc:
            return self._fail(
                f"Failed to call {module_path}.{function_name}",
                error=exc,
                hint="Validate parameters and ensure optional dependencies are installed.",
            )

    # -------------------------------------------------------------------------
    # Repository-oriented wrappers (high-value modules from analysis)
    # -------------------------------------------------------------------------
    def create_orbit_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an Orbit-related class instance from twobody orbit scalar module.

        Parameters:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status payload with instance.
        """
        return self.create_instance("src.poliastro.twobody.orbit.scalar", "Orbit", *args, **kwargs)

    def call_maneuver(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from src.poliastro.maneuver module.

        Parameters:
            function_name (str): Maneuver function to call.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload with result.
        """
        return self.call_function("src.poliastro.maneuver", function_name, *args, **kwargs)

    def call_ephem(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from src.poliastro.ephem module.

        Parameters:
            function_name (str): Ephemeris function name.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload.
        """
        return self.call_function("src.poliastro.ephem", function_name, *args, **kwargs)

    def call_io(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from src.poliastro.io module.

        Parameters:
            function_name (str): IO utility function.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload.
        """
        return self.call_function("src.poliastro.io", function_name, *args, **kwargs)

    def call_util(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from src.poliastro.util module.

        Parameters:
            function_name (str): Utility function name.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload.
        """
        return self.call_function("src.poliastro.util", function_name, *args, **kwargs)

    def call_izzo(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from Lambert IOD implementation module src.poliastro.iod.izzo.

        Parameters:
            function_name (str): Function name in izzo module.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload.
        """
        return self.call_function("src.poliastro.iod.izzo", function_name, *args, **kwargs)

    def call_vallado(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from IOD Vallado module src.poliastro.iod.vallado.

        Parameters:
            function_name (str): Function name in vallado module.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status payload.
        """
        return self.call_function("src.poliastro.iod.vallado", function_name, *args, **kwargs)

    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when import mode is partially unavailable.

        Returns:
            dict: Unified status payload with remediation instructions.
        """
        hints: List[str] = [
            "Ensure repository root contains the 'source/src/poliastro' package tree.",
            "Install required dependencies: numpy, astropy, scipy.",
            "Install optional dependencies if needed: matplotlib, plotly, numba, astroquery, jplephem, pandas.",
            "Verify runtime Python version is compatible with repository pyproject settings.",
        ]
        return self._ok(
            {
                "import_errors": self._import_errors,
                "guidance": hints,
                "fallback_mode": "blackbox-compatible",
            },
            message="Fallback guidance generated",
        )