import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for pyproj repository source modules.

    This adapter prefers direct import execution against local repository source code.
    If import is unavailable, methods return actionable fallback guidance and can route
    selected operations to CLI fallback suggestions.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._available = False
        self._import_errors: List[str] = []

        self.pyproj = None
        self.pyproj_aoi = None
        self.pyproj_crs = None
        self.pyproj_geod = None
        self.pyproj_proj = None
        self.pyproj_transformer = None
        self.pyproj_datadir = None
        self.pyproj_network = None
        self.pyproj_sync = None
        self.pyproj_show_versions = None
        self.pyproj_main = None

        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _err(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _import_module(self, module_path: str):
        try:
            return importlib.import_module(module_path)
        except Exception as e:
            self._import_errors.append(f"{module_path}: {e}")
            return None

    def _load_modules(self) -> None:
        self.pyproj = self._import_module("pyproj")
        self.pyproj_aoi = self._import_module("pyproj.aoi")
        self.pyproj_crs = self._import_module("pyproj.crs")
        self.pyproj_geod = self._import_module("pyproj.geod")
        self.pyproj_proj = self._import_module("pyproj.proj")
        self.pyproj_transformer = self._import_module("pyproj.transformer")
        self.pyproj_datadir = self._import_module("pyproj.datadir")
        self.pyproj_network = self._import_module("pyproj.network")
        self.pyproj_sync = self._import_module("pyproj.sync")
        self.pyproj_show_versions = self._import_module("pyproj._show_versions")
        self.pyproj_main = self._import_module("pyproj.__main__")
        self._available = self.pyproj is not None

    def health(self) -> Dict[str, Any]:
        """
        Return adapter and import health information.

        Returns:
            dict: Unified status with module availability and import diagnostics.
        """
        return self._ok(
            {
                "import_available": self._available,
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            "adapter health checked",
        )

    # -------------------------------------------------------------------------
    # Fallback and CLI guidance
    # -------------------------------------------------------------------------
    def cli_fallback_info(self) -> Dict[str, Any]:
        """
        Provide CLI fallback instructions when import mode is unavailable.

        Returns:
            dict: Unified status with actionable CLI command guidance.
        """
        return self._ok(
            {
                "recommended": "python -m pyproj",
                "description": "Inspect pyproj/PROJ runtime environment and utility output via module CLI.",
                "note": "Use this fallback when local import fails due to missing native PROJ runtime or build artifacts.",
            },
            "cli fallback guidance",
        )

    # -------------------------------------------------------------------------
    # pyproj top-level metadata and utilities
    # -------------------------------------------------------------------------
    def get_pyproj_info(self) -> Dict[str, Any]:
        """
        Get top-level pyproj package metadata.

        Returns:
            dict: Version and available top-level attributes.
        """
        if not self.pyproj:
            return self._err(
                "Failed to import pyproj package.",
                guidance="Ensure repository source is present under ./source and native PROJ dependencies are available.",
            )
        try:
            data = {
                "version": getattr(self.pyproj, "__version__", None),
                "proj_version_str": getattr(self.pyproj, "proj_version_str", None),
                "network_enabled": self.pyproj.network.is_network_enabled() if hasattr(self.pyproj, "network") else None,
            }
            return self._ok(data, "pyproj info retrieved")
        except Exception as e:
            return self._err("Unable to collect pyproj metadata.", e)

    def show_versions(self) -> Dict[str, Any]:
        """
        Execute pyproj version reporting utility.

        Returns:
            dict: Structured status and result details.
        """
        if not self.pyproj_show_versions:
            return self._err(
                "pyproj._show_versions module is unavailable.",
                guidance="Verify the local source tree includes pyproj/_show_versions.py.",
            )
        try:
            fn = getattr(self.pyproj_show_versions, "show_versions", None)
            if not callable(fn):
                return self._err("show_versions function not found in pyproj._show_versions.")
            result = fn()
            return self._ok(result, "show_versions executed")
        except Exception as e:
            return self._err("Failed to execute show_versions.", e)

    # -------------------------------------------------------------------------
    # AOI module
    # -------------------------------------------------------------------------
    def create_area_of_interest(
        self,
        west_lon_degree: float,
        south_lat_degree: float,
        east_lon_degree: float,
        north_lat_degree: float,
    ) -> Dict[str, Any]:
        """
        Create pyproj.aoi.AreaOfInterest instance.

        Args:
            west_lon_degree: Western longitude bound.
            south_lat_degree: Southern latitude bound.
            east_lon_degree: Eastern longitude bound.
            north_lat_degree: Northern latitude bound.

        Returns:
            dict: Contains created object on success.
        """
        if not self.pyproj_aoi:
            return self._err("pyproj.aoi module is unavailable.")
        try:
            cls = getattr(self.pyproj_aoi, "AreaOfInterest", None)
            if cls is None:
                return self._err("AreaOfInterest class not found in pyproj.aoi.")
            obj = cls(west_lon_degree, south_lat_degree, east_lon_degree, north_lat_degree)
            return self._ok({"object": obj}, "AreaOfInterest created")
        except Exception as e:
            return self._err("Failed to create AreaOfInterest.", e)

    # -------------------------------------------------------------------------
    # CRS module
    # -------------------------------------------------------------------------
    def create_crs(self, value: Any) -> Dict[str, Any]:
        """
        Create pyproj CRS from user input.

        Args:
            value: Any CRS-compatible input (EPSG code, proj string, WKT, dict, etc.).

        Returns:
            dict: Contains CRS object.
        """
        if not self.pyproj_crs:
            return self._err("pyproj.crs module is unavailable.")
        try:
            cls = getattr(self.pyproj_crs, "CRS", None)
            if cls is None:
                return self._err("CRS class not found in pyproj.crs.")
            obj = cls.from_user_input(value)
            return self._ok({"object": obj, "srs": obj.to_string()}, "CRS created")
        except Exception as e:
            return self._err("Failed to create CRS from input.", e)

    # -------------------------------------------------------------------------
    # Proj and Transformer
    # -------------------------------------------------------------------------
    def create_proj(self, projparams: Any = None, preserve_units: bool = True) -> Dict[str, Any]:
        """
        Create pyproj.Proj instance.

        Args:
            projparams: Projection definition input.
            preserve_units: Whether to preserve unit settings.

        Returns:
            dict: Contains Proj object.
        """
        if not self.pyproj_proj and not self.pyproj:
            return self._err("pyproj.proj module is unavailable.")
        try:
            cls = getattr(self.pyproj, "Proj", None) if self.pyproj else None
            if cls is None and self.pyproj_proj:
                cls = getattr(self.pyproj_proj, "Proj", None)
            if cls is None:
                return self._err("Proj class not found.")
            obj = cls(projparams=projparams, preserve_units=preserve_units)
            return self._ok({"object": obj, "srs": getattr(obj, "srs", None)}, "Proj created")
        except Exception as e:
            return self._err("Failed to create Proj.", e)

    def create_transformer(
        self,
        crs_from: Any,
        crs_to: Any,
        always_xy: bool = False,
    ) -> Dict[str, Any]:
        """
        Create pyproj Transformer instance from two CRS definitions.

        Args:
            crs_from: Source CRS input.
            crs_to: Target CRS input.
            always_xy: Force x,y axis order.

        Returns:
            dict: Contains Transformer object.
        """
        if not self.pyproj_transformer and not self.pyproj:
            return self._err("pyproj.transformer module is unavailable.")
        try:
            cls = getattr(self.pyproj, "Transformer", None) if self.pyproj else None
            if cls is None and self.pyproj_transformer:
                cls = getattr(self.pyproj_transformer, "Transformer", None)
            if cls is None:
                return self._err("Transformer class not found.")
            obj = cls.from_crs(crs_from, crs_to, always_xy=always_xy)
            return self._ok({"object": obj, "description": str(obj)}, "Transformer created")
        except Exception as e:
            return self._err("Failed to create Transformer.", e)

    def transform(
        self,
        crs_from: Any,
        crs_to: Any,
        x: Any,
        y: Any,
        z: Any = None,
        always_xy: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform coordinate transformation using a temporary Transformer.

        Args:
            crs_from: Source CRS.
            crs_to: Target CRS.
            x: X coordinate(s).
            y: Y coordinate(s).
            z: Optional Z coordinate(s).
            always_xy: Force x,y axis order.

        Returns:
            dict: Transformed coordinates.
        """
        created = self.create_transformer(crs_from=crs_from, crs_to=crs_to, always_xy=always_xy)
        if created["status"] != "success":
            return created
        try:
            transformer = created["data"]["object"]
            if z is None:
                tx, ty = transformer.transform(x, y)
                return self._ok({"x": tx, "y": ty}, "Transformation completed")
            tx, ty, tz = transformer.transform(x, y, z)
            return self._ok({"x": tx, "y": ty, "z": tz}, "3D transformation completed")
        except Exception as e:
            return self._err("Failed to transform coordinates.", e)

    # -------------------------------------------------------------------------
    # Geod module
    # -------------------------------------------------------------------------
    def create_geod(self, initstring: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Create pyproj.Geod instance.

        Args:
            initstring: Optional geodesic initialization string.
            **kwargs: Additional Geod constructor parameters.

        Returns:
            dict: Contains Geod object.
        """
        if not self.pyproj_geod and not self.pyproj:
            return self._err("pyproj.geod module is unavailable.")
        try:
            cls = getattr(self.pyproj, "Geod", None) if self.pyproj else None
            if cls is None and self.pyproj_geod:
                cls = getattr(self.pyproj_geod, "Geod", None)
            if cls is None:
                return self._err("Geod class not found.")
            obj = cls(initstring=initstring, **kwargs) if initstring is not None else cls(**kwargs)
            return self._ok({"object": obj}, "Geod created")
        except Exception as e:
            return self._err("Failed to create Geod.", e)

    # -------------------------------------------------------------------------
    # Data directory and network/sync utilities
    # -------------------------------------------------------------------------
    def get_data_dir(self) -> Dict[str, Any]:
        """
        Get current pyproj data directory.

        Returns:
            dict: Data directory path details.
        """
        if not self.pyproj_datadir:
            return self._err("pyproj.datadir module is unavailable.")
        try:
            fn = getattr(self.pyproj_datadir, "get_data_dir", None)
            if not callable(fn):
                return self._err("get_data_dir function not found.")
            return self._ok({"data_dir": fn()}, "Data directory retrieved")
        except Exception as e:
            return self._err("Failed to get data directory.", e)

    def set_data_dir(self, path: str) -> Dict[str, Any]:
        """
        Set pyproj data directory.

        Args:
            path: Filesystem path to PROJ data directory.

        Returns:
            dict: Operation result status.
        """
        if not self.pyproj_datadir:
            return self._err("pyproj.datadir module is unavailable.")
        try:
            fn = getattr(self.pyproj_datadir, "set_data_dir", None)
            if not callable(fn):
                return self._err("set_data_dir function not found.")
            fn(path)
            return self._ok({"data_dir": path}, "Data directory set")
        except Exception as e:
            return self._err("Failed to set data directory.", e)

    def is_network_enabled(self) -> Dict[str, Any]:
        """
        Check whether network access is enabled in pyproj.

        Returns:
            dict: Boolean network status.
        """
        if not self.pyproj_network:
            return self._err("pyproj.network module is unavailable.")
        try:
            fn = getattr(self.pyproj_network, "is_network_enabled", None)
            if not callable(fn):
                return self._err("is_network_enabled function not found.")
            return self._ok({"enabled": bool(fn())}, "Network status retrieved")
        except Exception as e:
            return self._err("Failed to get network status.", e)

    def set_network_enabled(self, active: bool = True) -> Dict[str, Any]:
        """
        Enable or disable pyproj network access.

        Args:
            active: True to enable network access, False to disable.

        Returns:
            dict: Updated network state.
        """
        if not self.pyproj_network:
            return self._err("pyproj.network module is unavailable.")
        try:
            fn = getattr(self.pyproj_network, "set_network_enabled", None)
            if not callable(fn):
                return self._err("set_network_enabled function not found.")
            fn(active=active)
            return self.is_network_enabled()
        except Exception as e:
            return self._err("Failed to set network status.", e)

    def sync_transformer_grids(self, **kwargs) -> Dict[str, Any]:
        """
        Invoke pyproj.sync transformation grid synchronization.

        Args:
            **kwargs: Keyword arguments passed to pyproj.sync module function(s).

        Returns:
            dict: Sync invocation result.
        """
        if not self.pyproj_sync:
            return self._err(
                "pyproj.sync module is unavailable.",
                guidance="Grid sync requires optional network-enabled environment and PROJ data support.",
            )
        try:
            candidates = ["sync", "main"]
            for name in candidates:
                fn = getattr(self.pyproj_sync, name, None)
                if callable(fn):
                    result = fn(**kwargs) if name == "sync" else fn([])
                    return self._ok({"result": result, "entry": name}, "Sync executed")
            return self._err("No callable sync entry found in pyproj.sync.")
        except Exception as e:
            return self._err("Failed to execute pyproj sync.", e)