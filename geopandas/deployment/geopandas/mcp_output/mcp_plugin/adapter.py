import os
import sys
import traceback
import inspect
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for GeoPandas repository source integration.

    This adapter prioritizes direct source imports from the provided repository
    layout and falls back gracefully when optional dependencies are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._load_errors: Dict[str, str] = {}
        self._import_status = self._import_core_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if details:
            payload["details"] = details
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            module = __import__(module_path, fromlist=["*"])
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._load_errors[module_path] = f"{type(exc).__name__}: {exc}"
            return None

    def _import_core_modules(self) -> Dict[str, Any]:
        targets = [
            "geopandas",
            "geopandas.geoseries",
            "geopandas.geodataframe",
            "geopandas.array",
            "geopandas.tools",
            "geopandas.tools.clip",
            "geopandas.tools.overlay",
            "geopandas.tools.sjoin",
            "geopandas.tools.geocoding",
            "geopandas.tools.hilbert_curve",
            "geopandas.tools._random",
            "geopandas.io.file",
            "geopandas.io.arrow",
            "geopandas.io.sql",
            "geopandas.testing",
            "geopandas.datasets",
        ]
        for module_path in targets:
            self._import_module(module_path)

        if "geopandas" in self._modules:
            return self._ok(
                {
                    "imported_modules": sorted(self._modules.keys()),
                    "import_errors": self._load_errors,
                },
                message="Core modules imported with optional graceful degradation.",
            )
        return self._err(
            "Failed to import required core module 'geopandas'.",
            details="Ensure repository source exists under '<adapter_root>/source' and dependencies are installed.",
        )

    def _get_attr(self, module_path: str, attr: str) -> Any:
        module = self._modules.get(module_path)
        if module is None:
            module = self._import_module(module_path)
        if module is None:
            raise ImportError(
                f"Module '{module_path}' is unavailable. "
                f"Install missing dependencies or verify source path configuration."
            )
        if not hasattr(module, attr):
            raise AttributeError(
                f"Attribute '{attr}' not found in module '{module_path}'. "
                f"Check repository version compatibility."
            )
        return getattr(module, attr)

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            Unified status dictionary with loaded modules and load errors.
        """
        return self._ok(
            {
                "import_summary": self._import_status,
                "loaded_module_count": len(self._modules),
                "failed_module_count": len(self._load_errors),
                "failed_modules": self._load_errors,
            },
            message="Adapter health check completed.",
        )

    def list_capabilities(self) -> Dict[str, Any]:
        """
        List high-level capabilities exposed by this adapter.

        Returns:
            Unified status dictionary with available operation categories.
        """
        caps = [
            "GeoDataFrame/GeoSeries constructors",
            "I/O: file, parquet/arrow, SQL",
            "Spatial tools: clip, overlay, sjoin",
            "Utility tools: geocode, hilbert_distance, random_points",
            "Datasets access and testing helpers",
        ]
        return self._ok({"capabilities": caps}, message="Capabilities enumerated.")

    # -------------------------------------------------------------------------
    # GeoPandas top-level API
    # -------------------------------------------------------------------------
    def read_file(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.read_file with pass-through arguments."""
        try:
            fn = self._get_attr("geopandas", "read_file")
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="read_file executed.")
        except Exception as exc:
            return self._err("read_file failed.", details=f"{type(exc).__name__}: {exc}")

    def read_parquet(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.read_parquet with pass-through arguments."""
        try:
            fn = self._get_attr("geopandas", "read_parquet")
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="read_parquet executed.")
        except Exception as exc:
            return self._err(
                "read_parquet failed.",
                details=f"{type(exc).__name__}: {exc}. Install 'pyarrow' if missing.",
            )

    def read_feather(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.read_feather with pass-through arguments."""
        try:
            fn = self._get_attr("geopandas", "read_feather")
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="read_feather executed.")
        except Exception as exc:
            return self._err(
                "read_feather failed.",
                details=f"{type(exc).__name__}: {exc}. Install 'pyarrow' if missing.",
            )

    # -------------------------------------------------------------------------
    # Class instance methods
    # -------------------------------------------------------------------------
    def create_geodataframe(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate geopandas.geodataframe.GeoDataFrame.

        Parameters:
            *args, **kwargs: Constructor arguments for GeoDataFrame.

        Returns:
            Unified status dictionary containing the created instance.
        """
        try:
            cls = self._get_attr("geopandas.geodataframe", "GeoDataFrame")
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, message="GeoDataFrame instance created.")
        except Exception as exc:
            return self._err(
                "GeoDataFrame construction failed.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def create_geoseries(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate geopandas.geoseries.GeoSeries.

        Parameters:
            *args, **kwargs: Constructor arguments for GeoSeries.

        Returns:
            Unified status dictionary containing the created instance.
        """
        try:
            cls = self._get_attr("geopandas.geoseries", "GeoSeries")
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, message="GeoSeries instance created.")
        except Exception as exc:
            return self._err(
                "GeoSeries construction failed.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Tools functions
    # -------------------------------------------------------------------------
    def call_clip(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.tools.clip.clip."""
        try:
            fn = self._get_attr("geopandas.tools.clip", "clip")
            return self._ok({"result": fn(*args, **kwargs)}, message="clip executed.")
        except Exception as exc:
            return self._err("clip failed.", details=f"{type(exc).__name__}: {exc}")

    def call_overlay(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.tools.overlay.overlay."""
        try:
            fn = self._get_attr("geopandas.tools.overlay", "overlay")
            return self._ok({"result": fn(*args, **kwargs)}, message="overlay executed.")
        except Exception as exc:
            return self._err("overlay failed.", details=f"{type(exc).__name__}: {exc}")

    def call_sjoin(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.tools.sjoin.sjoin."""
        try:
            fn = self._get_attr("geopandas.tools.sjoin", "sjoin")
            return self._ok({"result": fn(*args, **kwargs)}, message="sjoin executed.")
        except Exception as exc:
            return self._err(
                "sjoin failed.",
                details=f"{type(exc).__name__}: {exc}. Install spatial index dependency (rtree or shapely STRtree support).",
            )

    def call_geocode(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.tools.geocoding.geocode."""
        try:
            fn = self._get_attr("geopandas.tools.geocoding", "geocode")
            return self._ok({"result": fn(*args, **kwargs)}, message="geocode executed.")
        except Exception as exc:
            return self._err(
                "geocode failed.",
                details=f"{type(exc).__name__}: {exc}. Install 'geopy' and provide a valid provider.",
            )

    def call_reverse_geocode(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.tools.geocoding.reverse_geocode."""
        try:
            fn = self._get_attr("geopandas.tools.geocoding", "reverse_geocode")
            return self._ok({"result": fn(*args, **kwargs)}, message="reverse_geocode executed.")
        except Exception as exc:
            return self._err(
                "reverse_geocode failed.",
                details=f"{type(exc).__name__}: {exc}. Install 'geopy' and validate input coordinates.",
            )

    # -------------------------------------------------------------------------
    # IO functions
    # -------------------------------------------------------------------------
    def call_read_postgis(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call geopandas.io.sql.read_postgis."""
        try:
            fn = self._get_attr("geopandas.io.sql", "read_postgis")
            return self._ok({"result": fn(*args, **kwargs)}, message="read_postgis executed.")
        except Exception as exc:
            return self._err(
                "read_postgis failed.",
                details=f"{type(exc).__name__}: {exc}. Ensure SQLAlchemy and a valid DB connection are provided.",
            )

    # -------------------------------------------------------------------------
    # Introspection helpers
    # -------------------------------------------------------------------------
    def describe_module(self, module_path: str) -> Dict[str, Any]:
        """
        Describe public callables in a module.

        Parameters:
            module_path: Full module import path (e.g., 'geopandas.tools.clip').

        Returns:
            Unified status dictionary with callable names and signatures.
        """
        try:
            module = self._modules.get(module_path) or self._import_module(module_path)
            if module is None:
                return self._err(
                    f"Module '{module_path}' could not be imported.",
                    details="Verify module path and dependency availability.",
                )
            callables_info: List[Dict[str, str]] = []
            for name in dir(module):
                if name.startswith("_"):
                    continue
                obj = getattr(module, name, None)
                if callable(obj):
                    try:
                        sig = str(inspect.signature(obj))
                    except Exception:
                        sig = "(signature unavailable)"
                    callables_info.append({"name": name, "signature": sig})
            return self._ok(
                {"module": module_path, "callables": callables_info},
                message="Module description generated.",
            )
        except Exception as exc:
            return self._err("describe_module failed.", details=f"{type(exc).__name__}: {exc}")

    def fallback_help(self) -> Dict[str, Any]:
        """
        Return actionable fallback guidance when imports fail.
        """
        guidance = [
            "Confirm repository source exists at '<adapter_root>/source'.",
            "Install required dependencies: numpy, pandas, shapely, pyproj.",
            "Install optional dependencies as needed: fiona/pyogrio, pyarrow, sqlalchemy, geopy, matplotlib, folium, rtree, scipy.",
            "Check Python version compatibility with the repository pyproject.toml.",
        ]
        if self._load_errors:
            return self._ok(
                {"guidance": guidance, "import_errors": self._load_errors},
                message="Fallback guidance provided for partial import failures.",
            )
        return self._ok({"guidance": guidance}, message="No import failures detected.")