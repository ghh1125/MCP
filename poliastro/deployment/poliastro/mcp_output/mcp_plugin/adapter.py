import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for poliastro repository.

    This adapter prefers direct in-repo imports (mode='import') and provides
    graceful fallback responses when imports fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "message": message,
            "data": data,
        }

    def _fail(self, message: str, error: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error:
            payload["error"] = str(error)
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        guidance = (
            f"Import mode is unavailable for '{action}'. "
            "Verify repository source is mounted at '../source', and required dependencies "
            "are available: numpy, astropy, scipy. Optional features may require "
            "matplotlib, plotly, numba, astroquery, and jplephem."
        )
        return self._fail(guidance, self._import_error)

    def _initialize_imports(self) -> None:
        try:
            import poliastro.bodies as bodies
            import poliastro.constants as constants
            import poliastro.ephem as ephem
            import poliastro.frames as frames
            import poliastro.io as io_mod
            import poliastro.maneuver as maneuver
            import poliastro.sensors as sensors
            import poliastro.spacecraft as spacecraft
            import poliastro.util as util
            import poliastro.twobody as twobody
            import poliastro.twobody.angles as twobody_angles
            import poliastro.twobody.elements as twobody_elements
            import poliastro.twobody.orbit as twobody_orbit
            import poliastro.twobody.propagation as twobody_propagation
            import poliastro.iod.izzo as iod_izzo
            import poliastro.iod.vallado as iod_vallado
            import poliastro.threebody.flybys as threebody_flybys
            import poliastro.threebody.soi as threebody_soi

            self._modules = {
                "bodies": bodies,
                "constants": constants,
                "ephem": ephem,
                "frames": frames,
                "io": io_mod,
                "maneuver": maneuver,
                "sensors": sensors,
                "spacecraft": spacecraft,
                "util": util,
                "twobody": twobody,
                "twobody_angles": twobody_angles,
                "twobody_elements": twobody_elements,
                "twobody_orbit": twobody_orbit,
                "twobody_propagation": twobody_propagation,
                "iod_izzo": iod_izzo,
                "iod_vallado": iod_vallado,
                "threebody_flybys": threebody_flybys,
                "threebody_soi": threebody_soi,
            }
            self._loaded = True
        except Exception as exc:
            self._loaded = False
            self._import_error = str(exc)

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        if self._loaded:
            return self._ok(
                {
                    "import_ready": True,
                    "modules_loaded": sorted(self._modules.keys()),
                },
                "Adapter initialized in import mode.",
            )
        return self._fallback("health")

    # -------------------------------------------------------------------------
    # Class instance factories
    # -------------------------------------------------------------------------
    def create_orbit(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a poliastro.twobody.orbit.Orbit instance.

        Parameters:
            *args, **kwargs: Forwarded to Orbit constructor/factory usage.

        Returns:
            Unified status dictionary containing Orbit instance on success.
        """
        if not self._loaded:
            return self._fallback("create_orbit")
        try:
            Orbit = getattr(self._modules["twobody_orbit"], "Orbit")
            obj = Orbit(*args, **kwargs)
            return self._ok(obj, "Orbit instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create Orbit instance. Verify arguments match Orbit API.",
                str(exc),
            )

    def create_maneuver(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a poliastro.maneuver.Maneuver instance.

        Parameters:
            *args, **kwargs: Forwarded to Maneuver constructor.

        Returns:
            Unified status dictionary containing Maneuver instance on success.
        """
        if not self._loaded:
            return self._fallback("create_maneuver")
        try:
            Maneuver = getattr(self._modules["maneuver"], "Maneuver")
            obj = Maneuver(*args, **kwargs)
            return self._ok(obj, "Maneuver instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create Maneuver instance. Check impulse tuple formats.",
                str(exc),
            )

    def create_spacecraft(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a poliastro.spacecraft.Spacecraft instance.

        Parameters:
            *args, **kwargs: Forwarded to Spacecraft constructor.

        Returns:
            Unified status dictionary containing Spacecraft instance on success.
        """
        if not self._loaded:
            return self._fallback("create_spacecraft")
        try:
            Spacecraft = getattr(self._modules["spacecraft"], "Spacecraft")
            obj = Spacecraft(*args, **kwargs)
            return self._ok(obj, "Spacecraft instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create Spacecraft instance. Validate mass and area parameters.",
                str(exc),
            )

    # -------------------------------------------------------------------------
    # Functional wrappers (core capabilities from LLM/Deep analysis)
    # -------------------------------------------------------------------------
    def call_izzo_lambert(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Solve Lambert's problem using poliastro.iod.izzo.lambert.
        """
        if not self._loaded:
            return self._fallback("call_izzo_lambert")
        try:
            fn = getattr(self._modules["iod_izzo"], "lambert")
            return self._ok(fn(*args, **kwargs), "Izzo Lambert solution computed.")
        except Exception as exc:
            return self._fail(
                "Lambert solve failed. Check vectors, gravitational parameter, and epochs.",
                str(exc),
            )

    def call_vallado_lambert(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Solve Lambert's problem using poliastro.iod.vallado.lambert.
        """
        if not self._loaded:
            return self._fallback("call_vallado_lambert")
        try:
            fn = getattr(self._modules["iod_vallado"], "lambert")
            return self._ok(fn(*args, **kwargs), "Vallado Lambert solution computed.")
        except Exception as exc:
            return self._fail(
                "Vallado Lambert solve failed. Validate transfer geometry and time of flight.",
                str(exc),
            )

    def call_propagate(self, orbit: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Propagate orbit using Orbit.propagate API.

        Parameters:
            orbit: Orbit-like object exposing propagate().
            *args, **kwargs: Propagation parameters (time of flight, method, etc.).
        """
        if not self._loaded:
            return self._fallback("call_propagate")
        try:
            result = orbit.propagate(*args, **kwargs)
            return self._ok(result, "Orbit propagated.")
        except Exception as exc:
            return self._fail(
                "Propagation failed. Ensure orbit object is valid and method parameters are correct.",
                str(exc),
            )

    def call_body_lookup(self, body_name: str) -> Dict[str, Any]:
        """
        Retrieve a solar-system body object from poliastro.bodies module by name.

        Parameters:
            body_name: Exact body symbol/name (e.g., 'Earth', 'Mars', 'Sun').
        """
        if not self._loaded:
            return self._fallback("call_body_lookup")
        try:
            body = getattr(self._modules["bodies"], body_name)
            return self._ok(body, f"Body '{body_name}' found.")
        except Exception as exc:
            return self._fail(
                f"Body '{body_name}' not found. Use exact poliastro.bodies attribute names.",
                str(exc),
            )

    def call_time_range(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Wrapper for poliastro.util.time_range.
        """
        if not self._loaded:
            return self._fallback("call_time_range")
        try:
            fn = getattr(self._modules["util"], "time_range")
            return self._ok(fn(*args, **kwargs), "Time range generated.")
        except Exception as exc:
            return self._fail(
                "Failed to generate time range. Verify start/end/period arguments.",
                str(exc),
            )

    def call_flyby(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Wrapper for poliastro.threebody.flybys.compute_flyby (if available).
        """
        if not self._loaded:
            return self._fallback("call_flyby")
        try:
            fn = getattr(self._modules["threebody_flybys"], "compute_flyby")
            return self._ok(fn(*args, **kwargs), "Flyby computed.")
        except Exception as exc:
            return self._fail(
                "Flyby computation failed. Check incoming velocity, body parameters, and periapsis.",
                str(exc),
            )

    def call_soi(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Wrapper for poliastro.threebody.soi.laplace_radius (if available).
        """
        if not self._loaded:
            return self._fallback("call_soi")
        try:
            fn = getattr(self._modules["threebody_soi"], "laplace_radius")
            return self._ok(fn(*args, **kwargs), "Sphere of influence computed.")
        except Exception as exc:
            return self._fail(
                "SOI computation failed. Validate body and orbital distance parameters.",
                str(exc),
            )