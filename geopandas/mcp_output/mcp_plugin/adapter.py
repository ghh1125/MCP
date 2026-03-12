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
    MCP Import-Mode adapter for the GeoPandas repository source tree.

    This adapter prefers direct module imports from the local repository source path.
    If imports fail, it gracefully degrades to fallback mode and returns actionable
    guidance in English.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._fallback_reason: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _err(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _import_module(self, module_path: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        try:
            mod = importlib.import_module(module_path)
            return True, mod, None
        except Exception as e:
            return False, None, f"{module_path}: {e}"

    def _initialize_imports(self) -> None:
        required_modules = [
            "geopandas",
            "geopandas.io.file",
            "geopandas.io.arrow",
            "geopandas.io.sql",
            "geopandas.tools.clip",
            "geopandas.tools.overlay",
            "geopandas.tools.sjoin",
            "geopandas.tools.geocoding",
            "geopandas.tools._random",
            "geopandas.tools.hilbert_curve",
        ]

        errors: List[str] = []
        for mod_path in required_modules:
            ok, mod, err = self._import_module(mod_path)
            if ok:
                self._modules[mod_path] = mod
            else:
                errors.append(err or f"Failed importing {mod_path}")

        if errors:
            self.mode = "fallback"
            self._fallback_reason = "; ".join(errors)

    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter and import health information.
        """
        if self.mode == "import":
            return self._ok(
                {
                    "imports_loaded": sorted(self._modules.keys()),
                    "fallback_reason": self._fallback_reason,
                },
                "Adapter initialized in import mode.",
            )
        return self._err(
            "Adapter running in fallback mode due to import failures.",
            guidance=(
                "Ensure repository source exists at the configured source path, and required "
                "dependencies are installed: numpy, pandas, shapely, pyproj. Optional features "
                "may require fiona/pyogrio/pyarrow/sqlalchemy/rtree/matplotlib/folium."
            ),
        )

    # -------------------------------------------------------------------------
    # Core constructors and IO wrappers
    # -------------------------------------------------------------------------
    def create_geoseries(self, data=None, index=None, crs=None, **kwargs) -> Dict[str, Any]:
        """
        Create a GeoSeries using geopandas.GeoSeries.

        Parameters:
            data: Geometry-like iterable or scalar.
            index: Optional index.
            crs: CRS definition.
            **kwargs: Forwarded to GeoSeries constructor.
        """
        if self.mode != "import":
            return self._err("GeoSeries creation unavailable in fallback mode.", guidance="Fix imports and retry.")
        try:
            gpd = self._modules["geopandas"]
            obj = gpd.GeoSeries(data=data, index=index, crs=crs, **kwargs)
            return self._ok(obj, "GeoSeries created.")
        except Exception as e:
            return self._err("Failed to create GeoSeries.", e)

    def create_geodataframe(self, data=None, geometry=None, crs=None, **kwargs) -> Dict[str, Any]:
        """
        Create a GeoDataFrame using geopandas.GeoDataFrame.

        Parameters:
            data: Tabular-like data.
            geometry: Geometry column or sequence.
            crs: CRS definition.
            **kwargs: Forwarded to GeoDataFrame constructor.
        """
        if self.mode != "import":
            return self._err("GeoDataFrame creation unavailable in fallback mode.", guidance="Fix imports and retry.")
        try:
            gpd = self._modules["geopandas"]
            obj = gpd.GeoDataFrame(data=data, geometry=geometry, crs=crs, **kwargs)
            return self._ok(obj, "GeoDataFrame created.")
        except Exception as e:
            return self._err("Failed to create GeoDataFrame.", e)

    def read_file(self, filename: str, **kwargs) -> Dict[str, Any]:
        """
        Read geospatial file with geopandas.read_file.
        """
        if self.mode != "import":
            return self._err("read_file unavailable in fallback mode.", guidance="Install optional IO deps like fiona or pyogrio.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.read_file(filename, **kwargs)
            return self._ok(out, "File read successfully.")
        except Exception as e:
            return self._err("Failed to read file.", e, "Verify path, driver support, and IO dependencies.")

    def read_parquet(self, path: str, **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("read_parquet unavailable in fallback mode.", guidance="Install pyarrow and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.read_parquet(path, **kwargs)
            return self._ok(out, "Parquet read successfully.")
        except Exception as e:
            return self._err("Failed to read parquet.", e, "Ensure pyarrow is available and file is valid.")

    def read_feather(self, path: str, **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("read_feather unavailable in fallback mode.", guidance="Install pyarrow and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.read_feather(path, **kwargs)
            return self._ok(out, "Feather read successfully.")
        except Exception as e:
            return self._err("Failed to read feather.", e)

    def read_postgis(self, sql: str, con: Any, geom_col: str = "geom", **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("read_postgis unavailable in fallback mode.", guidance="Install sqlalchemy/geoalchemy2/psycopg and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.read_postgis(sql=sql, con=con, geom_col=geom_col, **kwargs)
            return self._ok(out, "PostGIS query executed successfully.")
        except Exception as e:
            return self._err("Failed to read PostGIS.", e)

    # -------------------------------------------------------------------------
    # Tools wrappers
    # -------------------------------------------------------------------------
    def clip(self, gdf: Any, mask: Any, keep_geom_type: bool = False, sort: bool = False) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("clip unavailable in fallback mode.", guidance="Fix imports and geometry dependencies.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.clip(gdf, mask, keep_geom_type=keep_geom_type, sort=sort)
            return self._ok(out, "Clip operation completed.")
        except Exception as e:
            return self._err("Failed to execute clip.", e)

    def overlay(self, df1: Any, df2: Any, how: str = "intersection", keep_geom_type: Optional[bool] = None, make_valid: bool = True) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("overlay unavailable in fallback mode.", guidance="Fix imports and ensure valid geometries.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.overlay(df1, df2, how=how, keep_geom_type=keep_geom_type, make_valid=make_valid)
            return self._ok(out, "Overlay operation completed.")
        except Exception as e:
            return self._err("Failed to execute overlay.", e)

    def sjoin(self, left_df: Any, right_df: Any, how: str = "inner", predicate: str = "intersects", lsuffix: str = "left", rsuffix: str = "right", **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("sjoin unavailable in fallback mode.", guidance="Install spatial index backend (rtree/pygeos/shapely STRtree) and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.sjoin(left_df, right_df, how=how, predicate=predicate, lsuffix=lsuffix, rsuffix=rsuffix, **kwargs)
            return self._ok(out, "Spatial join completed.")
        except Exception as e:
            return self._err("Failed to execute spatial join.", e)

    def sjoin_nearest(self, left_df: Any, right_df: Any, how: str = "inner", max_distance: Optional[float] = None, distance_col: Optional[str] = None, exclusive: bool = False) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("sjoin_nearest unavailable in fallback mode.", guidance="Ensure spatial index capabilities and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.sjoin_nearest(
                left_df,
                right_df,
                how=how,
                max_distance=max_distance,
                distance_col=distance_col,
                exclusive=exclusive,
            )
            return self._ok(out, "Nearest spatial join completed.")
        except Exception as e:
            return self._err("Failed to execute nearest spatial join.", e)

    def geocode(self, strings: Any, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("geocode unavailable in fallback mode.", guidance="Install geocoding dependencies and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.tools.geocode(strings, provider=provider, **kwargs)
            return self._ok(out, "Geocoding completed.")
        except Exception as e:
            return self._err("Failed to geocode.", e)

    def reverse_geocode(self, points: Any, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err("reverse_geocode unavailable in fallback mode.", guidance="Install geocoding dependencies and fix imports.")
        try:
            gpd = self._modules["geopandas"]
            out = gpd.tools.reverse_geocode(points, provider=provider, **kwargs)
            return self._ok(out, "Reverse geocoding completed.")
        except Exception as e:
            return self._err("Failed to reverse geocode.", e)

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Dynamically call a function from an imported or importable module.
        """
        try:
            mod = self._modules.get(module_path)
            if mod is None:
                ok, mod, err = self._import_module(module_path)
                if not ok or mod is None:
                    return self._err("Failed to import requested module.", guidance=err)
                self._modules[module_path] = mod

            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found in module '{module_path}'.",
                    guidance="Check the module path and function name against repository source.",
                )

            result = fn(*args, **kwargs)
            return self._ok(result, f"Function '{module_path}.{function_name}' executed.")
        except Exception as e:
            return self._err(
                "Dynamic function call failed.",
                e,
                guidance=traceback.format_exc(limit=3),
            )