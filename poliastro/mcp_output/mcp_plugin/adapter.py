import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for poliastro repository.

    This adapter attempts direct imports from the in-repo source tree first
    and gracefully falls back with actionable messages if imports fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _fallback(self, message: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": message,
            "guidance": "Verify repository source is present under the expected 'source' path and required dependencies are installed.",
        }

    def _load_modules(self) -> None:
        module_names = [
            "poliastro",
            "poliastro.bodies",
            "poliastro.constants",
            "poliastro.ephem",
            "poliastro.io",
            "poliastro.maneuver",
            "poliastro.sensors",
            "poliastro.spacecraft",
            "poliastro.spheroid_location",
            "poliastro.util",
            "poliastro.earth",
            "poliastro.earth.util",
            "poliastro.earth.atmosphere",
            "poliastro.frames",
            "poliastro.iod.izzo",
            "poliastro.iod.vallado",
            "poliastro.plotting",
            "poliastro.plotting.misc",
            "poliastro.plotting.gabbard",
            "poliastro.plotting.porkchop",
            "poliastro.plotting.tisserand",
            "poliastro.threebody.flybys",
            "poliastro.threebody.restricted",
            "poliastro.threebody.soi",
            "poliastro.threebody.cr3bp_char_quant",
            "poliastro.twobody.angles",
            "poliastro.twobody.elements",
            "poliastro.twobody.events",
            "poliastro.twobody.mean_elements",
            "poliastro.twobody.sampling",
            "poliastro.twobody.states",
            "poliastro.twobody.orbit.scalar",
            "poliastro.twobody.orbit.creation",
            "poliastro.twobody.propagation",
            "poliastro.twobody.thrust",
        ]
        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as exc:
                self._import_errors[name] = f"{type(exc).__name__}: {exc}"

    def healthcheck(self) -> Dict[str, Any]:
        if not self._modules:
            return self._fallback("No modules were imported.")
        return self._ok(
            {
                "imported_count": len(self._modules),
                "failed_count": len(self._import_errors),
                "failed_modules": self._import_errors,
            },
            "Adapter initialized with import-mode module scan.",
        )

    # ---------------------------------------------------------------------
    # Generic module/class/function accessors
    # ---------------------------------------------------------------------
    def list_available_modules(self) -> Dict[str, Any]:
        return self._ok(
            {
                "available": sorted(self._modules.keys()),
                "failed": self._import_errors,
            }
        )

    def instantiate_class(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from a fully qualified poliastro module.

        Parameters:
        - module_path: Full module path (e.g., 'poliastro.spacecraft')
        - class_name: Class name in the module
        - *args, **kwargs: Constructor arguments
        """
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok({"module": module_path, "class": class_name, "instance": instance})
        except Exception as exc:
            return self._fail(
                f"Failed to instantiate class '{class_name}' from module '{module_path}'. "
                f"Check class name and constructor arguments.",
                exc,
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a fully qualified poliastro module.

        Parameters:
        - module_path: Full module path (e.g., 'poliastro.iod.izzo')
        - function_name: Function name in the module
        - *args, **kwargs: Function arguments
        """
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            fn = getattr(module, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"module": module_path, "function": function_name, "result": result})
        except Exception as exc:
            return self._fail(
                f"Failed to call function '{function_name}' from module '{module_path}'. "
                f"Validate function name and argument compatibility.",
                exc,
            )

    # ---------------------------------------------------------------------
    # High-level poliastro feature wrappers
    # ---------------------------------------------------------------------
    def create_orbit(self, creation_method: str = "from_classical", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an orbit using poliastro.twobody.orbit.scalar.Orbit classmethod.

        Parameters:
        - creation_method: Orbit classmethod name (e.g., from_classical, from_vectors)
        - *args, **kwargs: Parameters expected by selected classmethod
        """
        try:
            mod = self._modules.get("poliastro.twobody.orbit.scalar")
            if mod is None:
                return self._fallback("Orbit module not available for import mode.")
            Orbit = getattr(mod, "Orbit")
            method = getattr(Orbit, creation_method)
            orbit = method(*args, **kwargs)
            return self._ok({"orbit": orbit, "creation_method": creation_method})
        except Exception as exc:
            return self._fail(
                f"Failed to create orbit via '{creation_method}'. Ensure body, epoch, units, and orbital elements are valid.",
                exc,
            )

    def propagate_orbit(self, orbit: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Propagate an Orbit object using Orbit.propagate API.

        Parameters:
        - orbit: poliastro Orbit instance
        - *args, **kwargs: Arguments forwarded to orbit.propagate
        """
        try:
            propagated = orbit.propagate(*args, **kwargs)
            return self._ok({"orbit": propagated})
        except Exception as exc:
            return self._fail(
                "Failed to propagate orbit. Verify time-of-flight units and selected propagator arguments.",
                exc,
            )

    def create_maneuver(self, maneuver_method: str = "hohmann", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a maneuver using poliastro.maneuver.Maneuver classmethods.

        Parameters:
        - maneuver_method: Classmethod name (e.g., hohmann, bielliptic, lambert)
        - *args, **kwargs: Parameters for selected method
        """
        try:
            mod = self._modules.get("poliastro.maneuver")
            if mod is None:
                return self._fallback("Maneuver module not available for import mode.")
            Maneuver = getattr(mod, "Maneuver")
            method = getattr(Maneuver, maneuver_method)
            maneuver = method(*args, **kwargs)
            return self._ok({"maneuver": maneuver, "method": maneuver_method})
        except Exception as exc:
            return self._fail(
                f"Failed to build maneuver '{maneuver_method}'. Check orbit inputs and unit consistency.",
                exc,
            )

    def solve_lambert_izzo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            return self.call_function("poliastro.iod.izzo", "lambert", *args, **kwargs)
        except Exception as exc:
            return self._fail("Lambert Izzo solver execution failed.", exc)

    def solve_lambert_vallado(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            return self.call_function("poliastro.iod.vallado", "lambert", *args, **kwargs)
        except Exception as exc:
            return self._fail("Lambert Vallado solver execution failed.", exc)

    def get_ephem(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            mod = self._modules.get("poliastro.ephem")
            if mod is None:
                return self._fallback("Ephemerides module not available for import mode.")
            Ephem = getattr(mod, "Ephem")
            if hasattr(Ephem, "from_body"):
                obj = Ephem.from_body(*args, **kwargs)
                return self._ok({"ephem": obj, "constructor": "from_body"})
            return self._fallback("Ephem.from_body is unavailable in this source version.")
        except Exception as exc:
            return self._fail("Failed to compute ephemerides.", exc)

    def create_spacecraft(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.instantiate_class("poliastro.spacecraft", "Spacecraft", *args, **kwargs)

    def get_body(self, body_name: str) -> Dict[str, Any]:
        try:
            mod = self._modules.get("poliastro.bodies")
            if mod is None:
                return self._fallback("Bodies module not available for import mode.")
            body = getattr(mod, body_name)
            return self._ok({"body": body})
        except Exception as exc:
            return self._fail(
                f"Body '{body_name}' not found. Use valid symbols like Earth, Mars, Sun, Moon.",
                exc,
            )