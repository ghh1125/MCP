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
    Import-mode adapter for the SunPy repository.

    This adapter attempts to import SunPy from the local `source` directory and exposes
    practical high-level methods that map to core repository functionality discovered
    during analysis (time parsing/ranges, map loading, timeseries loading, Fido search/fetch,
    and key solar coordinate/physics helpers).

    All public methods return a unified dictionary format:
    {
        "status": "success" | "error" | "fallback",
        ...
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._load_modules()

    def _ok(self, **payload: Any) -> Dict[str, Any]:
        data = {"status": "success"}
        data.update(payload)
        return data

    def _err(self, message: str, guidance: Optional[str] = None, **payload: Any) -> Dict[str, Any]:
        data = {"status": "error", "message": message}
        if guidance:
            data["guidance"] = guidance
        data.update(payload)
        return data

    def _fallback(self, message: str, guidance: Optional[str] = None, **payload: Any) -> Dict[str, Any]:
        data = {"status": "fallback", "message": message}
        if guidance:
            data["guidance"] = guidance
        data.update(payload)
        return data

    def _load_modules(self) -> None:
        try:
            import sunpy  # full path from source root
            import sunpy.map
            import sunpy.time
            import sunpy.timeseries
            import sunpy.net
            import sunpy.net.fido_factory
            import sunpy.coordinates
            import sunpy.coordinates.sun
            import sunpy.physics.differential_rotation

            self._modules = {
                "sunpy": sunpy,
                "sunpy.map": sunpy.map,
                "sunpy.time": sunpy.time,
                "sunpy.timeseries": sunpy.timeseries,
                "sunpy.net": sunpy.net,
                "sunpy.net.fido_factory": sunpy.net.fido_factory,
                "sunpy.coordinates": sunpy.coordinates,
                "sunpy.coordinates.sun": sunpy.coordinates.sun,
                "sunpy.physics.differential_rotation": sunpy.physics.differential_rotation,
            }
            self._import_error = None
        except Exception as exc:
            self._modules = {}
            self._import_error = str(exc)

    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter import status.

        Returns:
            dict: Unified status with mode, loaded module list, and import diagnostics.
        """
        if self._modules:
            return self._ok(mode=self.mode, loaded_modules=sorted(self._modules.keys()))
        return self._fallback(
            message="Import mode unavailable because local SunPy modules could not be loaded.",
            guidance=(
                "Verify repository source is available under '<plugin_root>/source' and includes "
                "the 'sunpy' package. Check dependency availability: numpy, astropy, packaging."
            ),
            mode=self.mode,
            import_error=self._import_error,
        )

    # -------------------------------------------------------------------------
    # Time utilities (sunpy.time)
    # -------------------------------------------------------------------------
    def call_parse_time(self, time_input: Any, format: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Parse a time input using sunpy.time.parse_time.

        Args:
            time_input: Input accepted by SunPy time parser (str, datetime, astropy Time, etc.).
            format: Optional explicit format passed through to parser.
            **kwargs: Additional parser keyword arguments.

        Returns:
            dict: Unified status with parsed `astropy.time.Time` object on success.
        """
        if "sunpy.time" not in self._modules:
            return self._fallback(
                message="sunpy.time is not available in import mode.",
                guidance="Run health_check() and resolve import/dependency issues before calling parse_time.",
            )
        try:
            fn = self._modules["sunpy.time"].parse_time
            result = fn(time_input, format=format, **kwargs) if format else fn(time_input, **kwargs)
            return self._ok(result=result)
        except Exception as exc:
            return self._err(
                message=f"Failed to parse time input: {exc}",
                guidance="Ensure the input time format is valid and compatible with SunPy/Astropy.",
            )

    def instance_timerange(self, a: Any = None, b: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of sunpy.time.timerange.TimeRange.

        Args:
            a: Start value or pair-like input accepted by TimeRange.
            b: End value or duration depending on constructor usage.
            **kwargs: Additional constructor args.

        Returns:
            dict: Unified status with TimeRange instance on success.
        """
        if "sunpy.time" not in self._modules:
            return self._fallback(
                message="sunpy.time is not available in import mode.",
                guidance="Run health_check() and confirm local source/dependencies.",
            )
        try:
            cls = self._modules["sunpy.time"].TimeRange
            obj = cls(a, b, **kwargs) if b is not None else cls(a, **kwargs)
            return self._ok(instance=obj)
        except Exception as exc:
            return self._err(
                message=f"Failed to create TimeRange instance: {exc}",
                guidance="Provide valid start/end inputs or valid constructor arguments.",
            )

    # -------------------------------------------------------------------------
    # Map utilities (sunpy.map)
    # -------------------------------------------------------------------------
    def instance_map(self, data: Any, header: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a map object via sunpy.map.Map factory.

        Args:
            data: File path, array, or supported map input.
            header: Optional metadata/header when constructing from raw array data.
            **kwargs: Additional map factory arguments.

        Returns:
            dict: Unified status with map instance on success.
        """
        if "sunpy.map" not in self._modules:
            return self._fallback(
                message="sunpy.map is not available in import mode.",
                guidance="Install optional dependencies for map workflows and verify source path.",
            )
        try:
            map_factory = self._modules["sunpy.map"].Map
            obj = map_factory(data, header, **kwargs) if header is not None else map_factory(data, **kwargs)
            return self._ok(instance=obj)
        except Exception as exc:
            return self._err(
                message=f"Failed to create map instance: {exc}",
                guidance="Check input FITS path/data-array validity and metadata consistency.",
            )

    # -------------------------------------------------------------------------
    # TimeSeries utilities (sunpy.timeseries)
    # -------------------------------------------------------------------------
    def instance_timeseries(self, source: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a TimeSeries object via sunpy.timeseries.TimeSeries factory.

        Args:
            source: Input accepted by TimeSeries factory (file path, URL result, etc.).
            **kwargs: Additional factory options.

        Returns:
            dict: Unified status with TimeSeries instance on success.
        """
        if "sunpy.timeseries" not in self._modules:
            return self._fallback(
                message="sunpy.timeseries is not available in import mode.",
                guidance="Confirm optional dependencies (e.g., pandas) and local source integrity.",
            )
        try:
            factory = self._modules["sunpy.timeseries"].TimeSeries
            obj = factory(source, **kwargs)
            return self._ok(instance=obj)
        except Exception as exc:
            return self._err(
                message=f"Failed to create TimeSeries instance: {exc}",
                guidance="Check source path/content and ensure required extras are installed.",
            )

    # -------------------------------------------------------------------------
    # Network/Fido utilities (sunpy.net)
    # -------------------------------------------------------------------------
    def instance_fido(self) -> Dict[str, Any]:
        """
        Return the Fido client facade from sunpy.net.

        Returns:
            dict: Unified status with Fido facade on success.
        """
        if "sunpy.net" not in self._modules:
            return self._fallback(
                message="sunpy.net is not available in import mode.",
                guidance="Confirm network-related optional dependencies and import availability.",
            )
        try:
            fido = self._modules["sunpy.net"].Fido
            return self._ok(instance=fido)
        except Exception as exc:
            return self._err(
                message=f"Failed to access Fido facade: {exc}",
                guidance="Verify sunpy.net import and compatibility of dependencies.",
            )

    def call_fido_search(self, *query_attrs: Any) -> Dict[str, Any]:
        """
        Execute a Fido search with provided query attributes.

        Args:
            *query_attrs: SunPy attr objects, e.g. attrs.Time(...), attrs.Instrument(...).

        Returns:
            dict: Unified status with search results on success.
        """
        if "sunpy.net" not in self._modules:
            return self._fallback(
                message="sunpy.net is not available in import mode.",
                guidance="Resolve import issues before performing remote searches.",
            )
        try:
            result = self._modules["sunpy.net"].Fido.search(*query_attrs)
            return self._ok(result=result)
        except Exception as exc:
            return self._err(
                message=f"Fido search failed: {exc}",
                guidance="Confirm query attrs are valid and network access is available.",
            )

    def call_fido_fetch(self, search_result: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Fetch files from a Fido search result.

        Args:
            search_result: Result returned by Fido.search.
            **kwargs: Additional fetch options (path, max_conn, progress, etc.).

        Returns:
            dict: Unified status with fetch response on success.
        """
        if "sunpy.net" not in self._modules:
            return self._fallback(
                message="sunpy.net is not available in import mode.",
                guidance="Resolve import issues before attempting fetch.",
            )
        try:
            fetched = self._modules["sunpy.net"].Fido.fetch(search_result, **kwargs)
            return self._ok(result=fetched)
        except Exception as exc:
            return self._err(
                message=f"Fido fetch failed: {exc}",
                guidance="Check download path permissions, network connectivity, and fetch arguments.",
            )

    # -------------------------------------------------------------------------
    # Coordinates / solar helpers
    # -------------------------------------------------------------------------
    def call_solar_angular_radius(self, time: Any = "now") -> Dict[str, Any]:
        """
        Compute the apparent solar angular radius at a given time.

        Args:
            time: Time input accepted by SunPy coordinate helpers.

        Returns:
            dict: Unified status with angular radius quantity on success.
        """
        if "sunpy.coordinates.sun" not in self._modules:
            return self._fallback(
                message="sunpy.coordinates.sun is not available in import mode.",
                guidance="Ensure astropy and sunpy coordinate modules are importable.",
            )
        try:
            fn = self._modules["sunpy.coordinates.sun"].angular_radius
            value = fn(time=time)
            return self._ok(result=value)
        except Exception as exc:
            return self._err(
                message=f"Failed to compute solar angular radius: {exc}",
                guidance="Provide a valid time input or use default 'now'.",
            )

    # -------------------------------------------------------------------------
    # Physics helpers
    # -------------------------------------------------------------------------
    def call_diff_rot(self, duration: Any, latitude: Any, rot_type: str = "howard", frame_time: str = "sidereal") -> Dict[str, Any]:
        """
        Compute solar differential rotation using SunPy physics helper.

        Args:
            duration: Time duration quantity (e.g., astropy.units day/hour quantity).
            latitude: Latitude quantity/array in angular units.
            rot_type: Rotation model (e.g., 'howard', 'snodgrass', 'allen', 'rigid').
            frame_time: 'sidereal' or 'synodic'.

        Returns:
            dict: Unified status with rotation result on success.
        """
        if "sunpy.physics.differential_rotation" not in self._modules:
            return self._fallback(
                message="sunpy.physics.differential_rotation is not available in import mode.",
                guidance="Ensure sunpy physics module and unit dependencies are installed.",
            )
        try:
            fn = self._modules["sunpy.physics.differential_rotation"].diff_rot
            result = fn(duration=duration, latitude=latitude, rot_type=rot_type, frame_time=frame_time)
            return self._ok(result=result)
        except Exception as exc:
            return self._err(
                message=f"Differential rotation computation failed: {exc}",
                guidance="Validate duration/latitude units and model arguments.",
            )