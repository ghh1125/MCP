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
    Import-mode adapter for the GeoPandas repository source package.

    This adapter prioritizes direct imports from the local source tree:
    - deployment.geopandas.source.geopandas

    It provides:
    - module loading and health checks
    - wrappers for key constructors and commonly used functions
    - graceful fallback responses when import is unavailable
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._load_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._initialize()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode}
        if data:
            out.update(data)
        return out

    def _fail(self, message: str, guidance: Optional[str] = None, error: Optional[str] = None) -> Dict[str, Any]:
        out = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if guidance:
            out["guidance"] = guidance
        if error:
            out["error"] = error
        return out

    def _fallback(self, action: str) -> Dict[str, Any]:
        return self._fail(
            message=f"Import mode is not available for action '{action}'.",
            guidance=(
                "Verify the repository source is present under the expected 'source' directory, "
                "and ensure required dependencies are installed: python>=3.11, numpy, pandas, "
                "shapely, pyproj, packaging."
            ),
            error=self._load_error,
        )

    def _initialize(self) -> None:
        """
        Load GeoPandas modules and key symbols from local source package paths.
        """
        try:
            base_pkg = "deployment.geopandas.source.geopandas"

            self._modules["geopandas"] = importlib.import_module(base_pkg)
            self._modules["geopandas_io_file"] = importlib.import_module(f"{base_pkg}.io.file")
            self._modules["geopandas_io_arrow"] = importlib.import_module(f"{base_pkg}.io.arrow")
            self._modules["geopandas_io_sql"] = importlib.import_module(f"{base_pkg}.io.sql")
            self._modules["geopandas_tools"] = importlib.import_module(f"{base_pkg}.tools")
            self._modules["geopandas_tools_clip"] = importlib.import_module(f"{base_pkg}.tools.clip")
            self._modules["geopandas_tools_overlay"] = importlib.import_module(f"{base_pkg}.tools.overlay")
            self._modules["geopandas_tools_sjoin"] = importlib.import_module(f"{base_pkg}.tools.sjoin")
            self._modules["geopandas_tools_geocoding"] = importlib.import_module(f"{base_pkg}.tools.geocoding")
            self._modules["geopandas_tools_hilbert"] = importlib.import_module(f"{base_pkg}.tools.hilbert_curve")
            self._modules["geopandas_tools_random"] = importlib.import_module(f"{base_pkg}.tools._random")
            self._modules["geopandas_show_versions"] = importlib.import_module(f"{base_pkg}.tools._show_versions")

            gpd = self._modules["geopandas"]
            self._symbols["GeoDataFrame"] = getattr(gpd, "GeoDataFrame", None)
            self._symbols["GeoSeries"] = getattr(gpd, "GeoSeries", None)
            self._symbols["read_file"] = getattr(gpd, "read_file", None)
            self._symbols["read_parquet"] = getattr(gpd, "read_parquet", None)
            self._symbols["read_feather"] = getattr(gpd, "read_feather", None)
            self._symbols["read_postgis"] = getattr(gpd, "read_postgis", None)
            self._symbols["sjoin"] = getattr(gpd, "sjoin", None)
            self._symbols["overlay"] = getattr(gpd, "overlay", None)
            self._symbols["clip"] = getattr(gpd, "clip", None)
            self._symbols["points_from_xy"] = getattr(gpd, "points_from_xy", None)
            self._symbols["datasets"] = getattr(gpd, "datasets", None)

            self._loaded = True
            self._load_error = None
        except Exception as exc:
            self._loaded = False
            self._load_error = f"{exc.__class__.__name__}: {exc}"

    def _call(self, fn: Any, action: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if not self._loaded:
            return self._fallback(action)
        if fn is None:
            return self._fail(
                message=f"Function for action '{action}' is not available.",
                guidance="Check the repository version and exported API symbols.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok({"action": action, "result": result})
        except Exception as exc:
            return self._fail(
                message=f"Execution failed for action '{action}'.",
                guidance="Validate parameters, input data paths, CRS values, and optional dependency availability.",
                error=f"{exc.__class__.__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.
        """
        if self._loaded:
            return self._ok(
                {
                    "loaded": True,
                    "modules": sorted(list(self._modules.keys())),
                    "available_symbols": sorted([k for k, v in self._symbols.items() if v is not None]),
                }
            )
        return self._fallback("health")

    def show_versions(self) -> Dict[str, Any]:
        """
        Return version diagnostics using geopandas.tools._show_versions.
        """
        if not self._loaded:
            return self._fallback("show_versions")
        try:
            mod = self._modules.get("geopandas_show_versions")
            fn = getattr(mod, "show_versions", None)