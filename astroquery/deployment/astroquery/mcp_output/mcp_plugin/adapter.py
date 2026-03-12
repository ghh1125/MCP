import os
import sys
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


# =========================
# Full-path imports (import mode)
# =========================
IMPORT_ERRORS: List[str] = []

try:
    from astroquery.simbad.core import SimbadClass
except Exception as e:
    SimbadClass = None
    IMPORT_ERRORS.append(f"Failed to import astroquery.simbad.core:SimbadClass: {e}")

try:
    from astroquery.vizier.core import VizierClass
except Exception as e:
    VizierClass = None
    IMPORT_ERRORS.append(f"Failed to import astroquery.vizier.core:VizierClass: {e}")

try:
    from astroquery.mast.observations import ObservationsClass
except Exception as e:
    ObservationsClass = None
    IMPORT_ERRORS.append(f"Failed to import astroquery.mast.observations:ObservationsClass: {e}")

try:
    from astroquery.utils.tap.core import Tap, TapPlus
except Exception as e:
    Tap = None
    TapPlus = None
    IMPORT_ERRORS.append(f"Failed to import astroquery.utils.tap.core:Tap/TapPlus: {e}")

try:
    from astroquery.gaia.core import GaiaClass
except Exception as e:
    GaiaClass = None
    IMPORT_ERRORS.append(f"Failed to import astroquery.gaia.core:GaiaClass: {e}")


class Adapter:
    """
    MCP Import-mode adapter for selected astroquery clients.

    Covered modules/classes based on analysis:
    - astroquery.simbad.core:SimbadClass
    - astroquery.vizier.core:VizierClass
    - astroquery.mast.observations:ObservationsClass
    - astroquery.utils.tap.core:Tap
    - astroquery.utils.tap.core:TapPlus
    - astroquery.gaia.core:GaiaClass

    Design goals:
    - Thin wrapper over upstream classes (composition, no inheritance).
    - Unified return format: {"status": "...", ...}
    - Graceful fallback when imports fail.
    - JSON-safe serialization for common outputs.
    """

    # =========================
    # Lifecycle / core utilities
    # =========================

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter.

        Parameters:
            config: Optional dict for adapter-level settings.
                Supported keys:
                - timeout (int|float): preferred timeout for compatible clients.
                - row_limit (int): preferred max rows for compatible clients.
                - polling_interval (int|float): async job polling delay.
        """
        self.mode = "import"
        self.config = config or {}
        self._instances: Dict[str, Any] = {}

    def health(self) -> Dict[str, Any]:
        """
        Report import readiness and basic adapter status.

        Returns:
            Unified status dictionary with module import diagnostics.
        """
        available = {
            "SimbadClass": SimbadClass is not None,
            "VizierClass": VizierClass is not None,
            "ObservationsClass": ObservationsClass is not None,
            "Tap": Tap is not None,
            "TapPlus": TapPlus is not None,
            "GaiaClass": GaiaClass is not None,
        }
        return {
            "status": "ok" if any(available.values()) else "error",
            "mode": self.mode,
            "available": available,
            "import_errors": IMPORT_ERRORS,
            "guidance": (
                "Ensure repository source is available at the configured source_path "
                "and required dependencies (astropy, numpy, requests, pyvo, etc.) are installed."
            ),
        }

    def _fallback(self, action: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "action": action,
            "error": "Import mode is unavailable for requested client.",
            "guidance": (
                "Verify source path wiring and Python dependencies. "
                "Then call health() to inspect missing imports."
            ),
        }

    def _ok(self, action: str, data: Any = None, **extra: Any) -> Dict[str, Any]:
        payload = {"status": "ok", "mode": self.mode, "action": action}
        if data is not None:
            payload["data"] = self._serialize(data)
        payload.update(extra)
        return payload

    def _err(self, action: str, exc: Exception) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "action": action,
            "error": str(exc),
            "guidance": "Review parameters and network/auth requirements; inspect traceback for details.",
            "traceback": traceback.format_exc(limit=5),
        }

    def _serialize(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {str(k): self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [self._serialize(v) for v in obj]
        if hasattr(obj, "to_pandas"):
            try:
                return obj.to_pandas().to_dict(orient="records")
            except Exception:
                pass
        if hasattr(obj, "to_table"):
            try:
                t = obj.to_table()
                return {name: self._serialize(t[name].tolist()) for name in t.colnames}
            except Exception:
                pass
        if hasattr(obj, "colnames") and hasattr(obj, "__getitem__"):
            try:
                return {name: self._serialize(obj[name].tolist()) for name in obj.colnames}
            except Exception:
                pass
        if hasattr(obj, "__dict__"):
            try:
                return {k: self._serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
            except Exception:
                pass
        return str(obj)

    # =========================
    # Instance management
    # =========================

    def create_simbad_instance(self, cache: bool = True) -> Dict[str, Any]:
        """Create and store a SimbadClass instance."""
        action = "create_simbad_instance"
        if SimbadClass is None:
            return self._fallback(action)
        try:
            inst = SimbadClass()
            if hasattr(inst, "cache"):
                inst.cache = cache
            self._instances["simbad"] = inst
            return self._ok(action, {"instance_key": "simbad"})
        except Exception as e:
            return self._err(action, e)

    def create_vizier_instance(self, columns: Optional[List[str]] = None, row_limit: Optional[int] = None) -> Dict[str, Any]:
        """Create and store a VizierClass instance with optional columns and row limit."""
        action = "create_vizier_instance"
        if VizierClass is None:
            return self._fallback(action)
        try:
            inst = VizierClass(columns=columns or ["*"])
            if row_limit is None:
                row_limit = self.config.get("row_limit")
            if row_limit is not None and hasattr(inst, "ROW_LIMIT"):
                inst.ROW_LIMIT = int(row_limit)
            self._instances["vizier"] = inst
            return self._ok(action, {"instance_key": "vizier"})
        except Exception as e:
            return self._err(action, e)

    def create_observations_instance(self) -> Dict[str, Any]:
        """Create and store an ObservationsClass instance."""
        action = "create_observations_instance"
        if ObservationsClass is None:
            return self._fallback(action)
        try:
            inst = ObservationsClass()
            self._instances["observations"] = inst
            return self._ok(action, {"instance_key": "observations"})
        except Exception as e:
            return self._err(action, e)

    def create_tap_instance(self, url: str, use_plus: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Create and store Tap or TapPlus instance for ADQL workflows."""
        action = "create_tap_instance"
        try:
            cls = TapPlus if use_plus else Tap
            if cls is None:
                return self._fallback(action)
            inst = cls(url=url, **kwargs)
            self._instances["tap"] = inst
            return self._ok(action, {"instance_key": "tap", "class": cls.__name__})
        except Exception as e:
            return self._err(action, e)

    def create_gaia_instance(self) -> Dict[str, Any]:
        """Create and store GaiaClass instance."""
        action = "create_gaia_instance"
        if GaiaClass is None:
            return self._fallback(action)
        try:
            inst = GaiaClass()
            self._instances["gaia"] = inst
            return self._ok(action, {"instance_key": "gaia"})
        except Exception as e:
            return self._err(action, e)

    # =========================
    # SIMBAD tools
    # =========================

    def simbad_query_object(self, object_name: str) -> Dict[str, Any]:
        """Query SIMBAD by object name."""
        action = "simbad_query_object"
        if SimbadClass is None:
            return self._fallback(action)
        try:
            inst = self._instances.get("simbad") or SimbadClass()
            result = inst.query_object(object_name)
            return self._ok(action, result)
        except Exception as e:
            return self._err(action, e)

    # =========================
    # VizieR tools
    # =========================

    def vizier_query_object(self, object_name: str, catalog: Optional[str] = None) -> Dict[str, Any]:
        """Query VizieR by object name and optional catalog."""
        action = "vizier_query_object"
        if VizierClass is None:
            return self._fallback(action)
        try:
            inst = self._instances.get("vizier") or VizierClass(columns=["*"])
            result = inst.query_object(object_name, catalog=catalog)
            return self._ok(action, result)
        except Exception as e:
            return self._err(action, e)

    # =========================
    # MAST Observations tools
    # =========================

    def mast_query_criteria(self, **criteria: Any) -> Dict[str, Any]:
        """Query MAST observations using criteria kwargs."""
        action = "mast_query_criteria"
        if ObservationsClass is None:
            return self._fallback(action)
        try:
            inst = self._instances.get("observations") or ObservationsClass()
            result = inst.query_criteria(**criteria)
            return self._ok(action, result)
        except Exception as e:
            return self._err(action, e)

    # =========================
    # TAP / ADQL tools
    # =========================

    def tap_launch_job(self, query: str, dump_to_file: bool = False, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run synchronous TAP query on stored tap instance."""
        action = "tap_launch_job"
        try:
            inst = self._instances.get("tap")
            if inst is None:
                return self._fallback(action)
            job = inst.launch_job(query=query, dump_to_file=dump_to_file, output_file=output_file)
            return self._ok(action, {"jobid": getattr(job, "jobid", None), "results": getattr(job, "get_results", lambda: None)()})
        except Exception as e:
            return self._err(action, e)

    def tap_launch_job_async(self, query: str, dump_to_file: bool = False, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run asynchronous TAP query on stored tap instance."""
        action = "tap_launch_job_async"
        try:
            inst = self._instances.get("tap")
            if inst is None:
                return self._fallback(action)
            job = inst.launch_job_async(query=query, dump_to_file=dump_to_file, output_file=output_file)
            return self._ok(action, {"jobid": getattr(job, "jobid", None)})
        except Exception as e:
            return self._err(action, e)

    # =========================
    # Gaia tools
    # =========================

    def gaia_launch_job(self, query: str) -> Dict[str, Any]:
        """Run Gaia synchronous ADQL query."""
        action = "gaia_launch_job"
        if GaiaClass is None:
            return self._fallback(action)
        try:
            inst = self._instances.get("gaia") or GaiaClass()
            job = inst.launch_job(query)
            return self._ok(action, {"jobid": getattr(job, "jobid", None), "results": job.get_results()})
        except Exception as e:
            return self._err(action, e)

    def gaia_launch_job_async(self, query: str) -> Dict[str, Any]:
        """Run Gaia asynchronous ADQL query."""
        action = "gaia_launch_job_async"
        if GaiaClass is None:
            return self._fallback(action)
        try:
            inst = self._instances.get("gaia") or GaiaClass()
            job = inst.launch_job_async(query)
            return self._ok(action, {"jobid": getattr(job, "jobid", None)})
        except Exception as e:
            return self._err(action, e)