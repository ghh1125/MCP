import os
import sys
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the dateutil repository implementation under source/src/dateutil.

    This adapter attempts to import repository modules directly from the local source tree.
    If import fails, methods provide graceful fallback responses with actionable guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        data: Optional[Any] = None,
        message: str = "",
        error: str = "",
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"status": status}
        if message:
            payload["message"] = message
        if error:
            payload["error"] = error
        if data is not None:
            payload["data"] = data
        if meta is not None:
            payload["meta"] = meta
        return payload

    def _initialize_imports(self) -> None:
        module_names = [
            "src.dateutil",
            "src.dateutil.easter",
            "src.dateutil.parser",
            "src.dateutil.parser._parser",
            "src.dateutil.parser.isoparser",
            "src.dateutil.relativedelta",
            "src.dateutil.rrule",
            "src.dateutil.tz",
            "src.dateutil.tz.tz",
            "src.dateutil.tz.win",
            "src.dateutil.tzwin",
            "src.dateutil.utils",
            "src.dateutil.zoneinfo",
            "src.dateutil.zoneinfo.rebuild",
        ]
        for mod_name in module_names:
            try:
                self._modules[mod_name] = importlib.import_module(mod_name)
            except Exception as exc:
                self._import_errors[mod_name] = str(exc)

    def _get_module(self, module_name: str) -> Dict[str, Any]:
        mod = self._modules.get(module_name)
        if mod is not None:
            return self._result("success", data=mod)
        err = self._import_errors.get(module_name, "Unknown import error.")
        return self._result(
            "fallback",
            message=(
                f"Module '{module_name}' is unavailable in import mode. "
                "Verify repository source path and dependencies (e.g., six)."
            ),
            error=err,
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter initialization and import state.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        return self._result(
            "success" if not self._import_errors else "partial",
            data={
                "mode": self.mode,
                "loaded_modules": sorted(self._modules.keys()),
                "failed_modules": self._import_errors,
                "source_path": source_path,
            },
        )

    # -------------------------------------------------------------------------
    # dateutil.easter
    # -------------------------------------------------------------------------
    def call_easter(self, year: int, method: int = 3) -> Dict[str, Any]:
        """
        Compute Easter date for a given year.

        Parameters:
            year (int): Year for Easter calculation.
            method (int): Calculation method from dateutil.easter constants.

        Returns:
            dict: status + computed date or fallback/error information.
        """
        mod_res = self._get_module("src.dateutil.easter")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "easter")
            return self._result("success", data=fn(year, method))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to compute Easter: {exc}",
                message="Validate year and method inputs.",
            )

    # -------------------------------------------------------------------------
    # dateutil.parser
    # -------------------------------------------------------------------------
    def call_parse(self, timestr: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Parse a date/time string using dateutil parser.

        Parameters:
            timestr (str): Input date/time text.
            **kwargs: Additional parser keyword arguments.

        Returns:
            dict: status + parsed datetime or error.
        """
        mod_res = self._get_module("src.dateutil.parser")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "parse")
            return self._result("success", data=fn(timestr, **kwargs))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to parse datetime string: {exc}",
                message="Check input format and parser keyword arguments.",
            )

    def create_parserinfo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create parserinfo instance from parser internals.

        Parameters:
            *args: Positional arguments for parserinfo.
            **kwargs: Keyword arguments for parserinfo.

        Returns:
            dict: status + parserinfo instance or error.
        """
        mod_res = self._get_module("src.dateutil.parser._parser")
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["data"], "parserinfo")
            return self._result("success", data=cls(*args, **kwargs))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to create parserinfo: {exc}",
                message="Review parserinfo constructor arguments.",
            )

    def create_isoparser(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an ISO parser instance.

        Parameters:
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: status + isoparser instance or error.
        """
        mod_res = self._get_module("src.dateutil.parser.isoparser")
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["data"], "isoparser")
            return self._result("success", data=cls(*args, **kwargs))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to create isoparser: {exc}",
                message="Check isoparser constructor parameters.",
            )

    def call_isoparse(self, dt_str: str) -> Dict[str, Any]:
        """
        Parse ISO-8601 datetime string.

        Parameters:
            dt_str (str): ISO datetime text.

        Returns:
            dict: status + parsed datetime or error.
        """
        mod_res = self._get_module("src.dateutil.parser")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "isoparse")
            return self._result("success", data=fn(dt_str))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to parse ISO datetime: {exc}",
                message="Ensure the input follows ISO-8601 format.",
            )

    # -------------------------------------------------------------------------
    # dateutil.relativedelta
    # -------------------------------------------------------------------------
    def create_relativedelta(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create relativedelta instance.

        Parameters:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: status + relativedelta instance or error.
        """
        mod_res = self._get_module("src.dateutil.relativedelta")
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["data"], "relativedelta")
            return self._result("success", data=cls(*args, **kwargs))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to create relativedelta: {exc}",
                message="Check relativedelta arguments.",
            )

    # -------------------------------------------------------------------------
    # dateutil.rrule
    # -------------------------------------------------------------------------
    def create_rrule(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.rrule")
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["data"], "rrule")
            return self._result("success", data=cls(*args, **kwargs))
        except Exception as exc:
            return self._result("error", error=f"Failed to create rrule: {exc}")

    def create_rruleset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.rrule")
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["data"], "rruleset")
            return self._result("success", data=cls(*args, **kwargs))
        except Exception as exc:
            return self._result("error", error=f"Failed to create rruleset: {exc}")

    def call_rrulestr(self, s: str, **kwargs: Any) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.rrule")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "rrulestr")
            return self._result("success", data=fn(s, **kwargs))
        except Exception as exc:
            return self._result("error", error=f"Failed to parse RRULE string: {exc}")

    # -------------------------------------------------------------------------
    # dateutil.tz
    # -------------------------------------------------------------------------
    def call_gettz(self, name: Optional[str] = None) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.tz")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "gettz")
            return self._result("success", data=fn(name))
        except Exception as exc:
            return self._result("error", error=f"Failed to resolve timezone: {exc}")

    def call_datetime_exists(self, dt: Any, tz: Optional[Any] = None) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.tz")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "datetime_exists")
            return self._result("success", data=fn(dt, tz))
        except Exception as exc:
            return self._result("error", error=f"Failed to check datetime existence: {exc}")

    def call_datetime_ambiguous(self, dt: Any, tz: Optional[Any] = None) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.tz")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "datetime_ambiguous")
            return self._result("success", data=fn(dt, tz))
        except Exception as exc:
            return self._result("error", error=f"Failed to check datetime ambiguity: {exc}")

    def call_resolve_imaginary(self, dt: Any) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.tz")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "resolve_imaginary")
            return self._result("success", data=fn(dt))
        except Exception as exc:
            return self._result("error", error=f"Failed to resolve imaginary time: {exc}")

    # -------------------------------------------------------------------------
    # dateutil.utils
    # -------------------------------------------------------------------------
    def call_today(self, tzinfo: Optional[Any] = None) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.utils")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "today")
            return self._result("success", data=fn(tzinfo))
        except Exception as exc:
            return self._result("error", error=f"Failed to compute today(): {exc}")

    def call_within_delta(self, dt1: Any, dt2: Any, delta: Any) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.utils")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "within_delta")
            return self._result("success", data=fn(dt1, dt2, delta))
        except Exception as exc:
            return self._result("error", error=f"Failed to evaluate within_delta: {exc}")

    # -------------------------------------------------------------------------
    # dateutil.zoneinfo
    # -------------------------------------------------------------------------
    def call_get_zonefile_instance(self) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.zoneinfo")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "get_zonefile_instance")
            return self._result("success", data=fn())
        except Exception as exc:
            return self._result("error", error=f"Failed to get zonefile instance: {exc}")

    def call_gettz_zoneinfo(self, name: str) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.zoneinfo")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "gettz")
            return self._result("success", data=fn(name))
        except Exception as exc:
            return self._result("error", error=f"Failed to load zoneinfo timezone: {exc}")

    def call_rebuild_zoneinfo(self, filename: Optional[str] = None) -> Dict[str, Any]:
        mod_res = self._get_module("src.dateutil.zoneinfo.rebuild")
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["data"], "rebuild")
            if filename is None:
                return self._result("success", data=fn())
            return self._result("success", data=fn(filename))
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to rebuild zoneinfo data: {exc}",
                message="Provide a valid zoneinfo tarball path or run with default configuration.",
            )

    # -------------------------------------------------------------------------
    # Discovery helpers
    # -------------------------------------------------------------------------
    def list_available_modules(self) -> Dict[str, Any]:
        """
        List imported and failed modules for quick adapter introspection.

        Returns:
            dict: status with module availability details.
        """
        return self._result(
            "success",
            data={
                "available": sorted(self._modules.keys()),
                "failed": self._import_errors,
            },
        )

    def list_module_attributes(self, module_name: str, public_only: bool = True) -> Dict[str, Any]:
        """
        List attributes for an imported module.

        Parameters:
            module_name (str): Fully-qualified module name.
            public_only (bool): If True, omit private names starting with underscore.

        Returns:
            dict: status with attribute names or fallback/error details.
        """
        mod_res = self._get_module(module_name)
        if mod_res["status"] != "success":
            return mod_res
        try:
            names: List[str] = dir(mod_res["data"])
            if public_only:
                names = [n for n in names if not n.startswith("_")]
            return self._result("success", data=sorted(names))
        except Exception as exc:
            return self._result("error", error=f"Failed to inspect module attributes: {exc}")