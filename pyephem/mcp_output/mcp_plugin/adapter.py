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
    Import-mode adapter for the pyephem repository.

    This adapter attempts to import local repository modules from the configured `source` path.
    It exposes wrapper methods for discovered classes and functions from analysis results, with
    unified return payloads and graceful fallback behavior when import is unavailable.
    """

    def __init__(self) -> None:
        """
        Initialize adapter state and import runtime modules/classes.

        Attributes:
            mode (str): Adapter mode, always set to "import".
            available (bool): Whether core imports succeeded.
            import_error (Optional[str]): Import failure details, if any.
        """
        self.mode = "import"
        self.available = False
        self.import_error: Optional[str] = None

        # Imported symbols (initialized lazily/safely)
        self._ephem = None
        self._stars = None
        self._cities = None

        self._AlwaysUpError = None
        self._Ariel = None
        self._Callisto = None

        self._import_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data is not None:
            payload["data"] = data
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if error is not None:
            payload["error"] = str(error)
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        return self._err(
            message=f"Import mode unavailable for action '{action}'.",
            guidance=(
                "Ensure repository sources exist under the local 'source' directory and that "
                "the PyEphem C extension is built for your Python environment."
            ),
        )

    def _import_modules(self) -> None:
        """
        Import analyzed modules and symbols using repository-local package paths.

        Uses full package paths discovered in analysis:
        - ephem.__init__ (module: ephem)
        - ephem.stars
        - ephem.cities
        """
        try:
            import ephem as ephem_module
            import ephem.stars as stars_module
            import ephem.cities as cities_module

            self._ephem = ephem_module
            self._stars = stars_module
            self._cities = cities_module

            self._AlwaysUpError = getattr(ephem_module, "AlwaysUpError", None)
            self._Ariel = getattr(ephem_module, "Ariel", None)
            self._Callisto = getattr(ephem_module, "Callisto", None)

            self.available = True
            self.import_error = None
        except Exception as exc:
            self.available = False
            self.import_error = str(exc)

    # -------------------------------------------------------------------------
    # Module management
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import status.

        Returns:
            dict: Unified status dictionary with availability details.
        """
        if self.available:
            return self._ok(
                {
                    "available": True,
                    "import_error": None,
                    "modules": ["ephem", "ephem.stars", "ephem.cities"],
                },
                message="Adapter is ready in import mode.",
            )
        return self._err(
            message="Adapter initialization failed.",
            guidance=(
                "Verify the local source path and build/install requirements for the PyEphem "
                "extension module before retrying."
            ),
            error=Exception(self.import_error) if self.import_error else None,
        )

    # -------------------------------------------------------------------------
    # Class instance factories
    # -------------------------------------------------------------------------
    def create_always_up_error(self, message: str = "Body is always above the horizon.") -> Dict[str, Any]:
        """
        Create an instance of ephem.AlwaysUpError.

        Args:
            message (str): Exception message payload.

        Returns:
            dict: status + data(instance) or error details.
        """
        if not self.available:
            return self._fallback("create_always_up_error")
        try:
            if self._AlwaysUpError is None:
                return self._err(
                    "Class 'AlwaysUpError' is not available in imported ephem module.",
                    guidance="Check your PyEphem version and ensure class symbols are exported.",
                )
            inst = self._AlwaysUpError(message)
            return self._ok({"instance": inst, "class": "AlwaysUpError"})
        except Exception as exc:
            return self._err(
                "Failed to create AlwaysUpError instance.",
                guidance="Ensure constructor arguments are valid for this runtime version.",
                error=exc,
            )

    def create_ariel(self) -> Dict[str, Any]:
        """
        Create an instance of ephem.Ariel.

        Returns:
            dict: status + data(instance) or error details.
        """
        if not self.available:
            return self._fallback("create_ariel")
        try:
            if self._Ariel is None:
                return self._err(
                    "Class 'Ariel' is not available in imported ephem module.",
                    guidance="Check your PyEphem build and symbol exports.",
                )
            inst = self._Ariel()
            return self._ok({"instance": inst, "class": "Ariel"})
        except Exception as exc:
            return self._err(
                "Failed to create Ariel instance.",
                guidance="Ensure the underlying ephem extension is correctly built and loadable.",
                error=exc,
            )

    def create_callisto(self) -> Dict[str, Any]:
        """
        Create an instance of ephem.Callisto.

        Returns:
            dict: status + data(instance) or error details.
        """
        if not self.available:
            return self._fallback("create_callisto")
        try:
            if self._Callisto is None:
                return self._err(
                    "Class 'Callisto' is not available in imported ephem module.",
                    guidance="Check your PyEphem build and symbol exports.",
                )
            inst = self._Callisto()
            return self._ok({"instance": inst, "class": "Callisto"})
        except Exception as exc:
            return self._err(
                "Failed to create Callisto instance.",
                guidance="Ensure the underlying ephem extension is correctly built and loadable.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Function wrappers: ephem module
    # -------------------------------------------------------------------------
    def call_ephem_city(self, name: str) -> Dict[str, Any]:
        """
        Call ephem.city(name) to retrieve a predefined city observer.

        Args:
            name (str): City name recognized by PyEphem's city database.

        Returns:
            dict: status + data(observer) or error details.
        """
        if not self.available:
            return self._fallback("call_ephem_city")
        try:
            fn = getattr(self._ephem, "city", None)
            if fn is None:
                return self._err(
                    "Function 'ephem.city' is unavailable.",
                    guidance="Use 'call_cities_city' as an alternative from ephem.cities.",
                )
            observer = fn(name)
            return self._ok({"observer": observer, "city": name})
        except Exception as exc:
            return self._err(
                "Failed to call ephem.city.",
                guidance="Use a valid city name or inspect available city datasets in ephem.cities.",
                error=exc,
            )

    def call_describe_riset_search(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call ephem.describe_riset_search(*args, **kwargs).

        This helper describes rise/set search behavior in PyEphem internals.
        Signature may vary by version; this adapter forwards all args/kwargs.

        Args:
            *args: Positional arguments for ephem.describe_riset_search.
            **kwargs: Keyword arguments for ephem.describe_riset_search.

        Returns:
            dict: status + data(result) or error details.
        """
        if not self.available:
            return self._fallback("call_describe_riset_search")
        try:
            fn = getattr(self._ephem, "describe_riset_search", None)
            if fn is None:
                return self._err(
                    "Function 'ephem.describe_riset_search' is unavailable.",
                    guidance="Confirm your PyEphem version includes this helper.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as exc:
            return self._err(
                "Failed to call ephem.describe_riset_search.",
                guidance="Check function arguments against your installed source version.",
                error=exc,
            )

    def call_holiday(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call ephem.holiday(*args, **kwargs).

        The exact signature can vary by source version; this method forwards arguments directly.

        Args:
            *args: Positional arguments for ephem.holiday.
            **kwargs: Keyword arguments for ephem.holiday.

        Returns:
            dict: status + data(result) or error details.
        """
        if not self.available:
            return self._fallback("call_holiday")
        try:
            fn = getattr(self._ephem, "holiday", None)
            if fn is None:
                return self._err(
                    "Function 'ephem.holiday' is unavailable.",
                    guidance="Verify your local repository version exports 'holiday'.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as exc:
            return self._err(
                "Failed to call ephem.holiday.",
                guidance="Review argument format and retry with valid date/holiday parameters.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # Function wrappers: ephem.stars and ephem.cities
    # -------------------------------------------------------------------------
    def call_stars_star(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call ephem.stars.star(name, *args, **kwargs) to retrieve a star object.

        Args:
            name (str): Star name from PyEphem star catalog.
            *args: Additional positional args (version-dependent).
            **kwargs: Additional keyword args (version-dependent).

        Returns:
            dict: status + data(star object) or error details.
        """
        if not self.available:
            return self._fallback("call_stars_star")
        try:
            fn = getattr(self._stars, "star", None)
            if fn is None:
                return self._err(
                    "Function 'ephem.stars.star' is unavailable.",
                    guidance="Ensure ephem.stars is present in repository sources.",
                )
            star_obj = fn(name, *args, **kwargs)
            return self._ok({"star": star_obj, "name": name})
        except Exception as exc:
            return self._err(
                "Failed to call ephem.stars.star.",
                guidance="Use a valid star name defined in the internal star catalog.",
                error=exc,
            )

    def call_cities_city(self, name: str) -> Dict[str, Any]:
        """
        Call ephem.cities.city(name) to retrieve a city observer object.

        Args:
            name (str): City name from the city dataset.

        Returns:
            dict: status + data(observer) or error details.
        """
        if not self.available:
            return self._fallback("call_cities_city")
        try:
            fn = getattr(self._cities, "city", None)
            if fn is None:
                return self._err(
                    "Function 'ephem.cities.city' is unavailable.",
                    guidance="Ensure ephem.cities module is correctly imported.",
                )
            observer = fn(name)
            return self._ok({"observer": observer, "city": name})
        except Exception as exc:
            return self._err(
                "Failed to call ephem.cities.city.",
                guidance="Use a valid city name supported by the cities module.",
                error=exc,
            )