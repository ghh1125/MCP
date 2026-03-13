import os
import sys
import importlib
import importlib.util
import importlib.machinery
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for backtrader repository integration.

    This adapter attempts direct module import first ("import" mode) and falls back
    to a file-based dynamic loader ("fallback_cli") when needed.

    Unified return format for all public methods:
    {
        "status": "success" | "error",
        "mode": "<current mode>",
        "message": "<human-readable summary>",
        "data": <optional payload>,
        "error": "<optional error details>"
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded_modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Core helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "message": message,
            "data": data,
        }

    def _err(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(error) if error else None,
        }

    def _safe_import(self, module_path: str) -> Tuple[Optional[Any], Optional[str]]:
        try:
            module = importlib.import_module(module_path)
            self._loaded_modules[module_path] = module
            return module, None
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None, str(exc)

    def _load_module_from_file(self, module_name: str, file_path: str) -> Tuple[Optional[Any], Optional[str]]:
        try:
            if not os.path.exists(file_path):
                return None, f"File not found: {file_path}. Verify repository extraction path and source directory."
            loader = importlib.machinery.SourceFileLoader(module_name, file_path)
            spec = importlib.util.spec_from_loader(module_name, loader)
            if spec is None:
                return None, f"Unable to create module spec for {module_name}."
            mod = importlib.util.module_from_spec(spec)
            loader.exec_module(mod)
            self._loaded_modules[module_name] = mod
            return mod, None
        except Exception as exc:
            return None, str(exc)

    def _initialize_imports(self) -> None:
        targets = [
            "backtrader.btrun.btrun",
            "tools.rewrite-data",
            "tools.yahoodownload",
            "contrib.utils.iqfeed-to-influxdb",
            "contrib.utils.influxdb-import",
            "contrib.samples.pair-trading.pair-trading",
            "samples.weekdays-filler.weekdaysfiller",
            "samples.weekdays-filler.weekdaysaligner",
        ]

        for mod in targets:
            self._safe_import(mod)

        if any(m not in self._loaded_modules for m in targets):
            self.mode = "fallback_cli"

    def get_health(self) -> Dict[str, Any]:
        """
        Return adapter health and module import diagnostics.

        Returns:
            dict: Unified status payload with import success/failure overview.
        """
        return self._ok(
            "Adapter health check completed.",
            data={
                "loaded_modules": list(self._loaded_modules.keys()),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
        )

    # -------------------------------------------------------------------------
    # backtrader.btrun.btrun
    # -------------------------------------------------------------------------
    def call_btrun(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute the built-in btrun command module.

        Args:
            argv (list, optional): Command-line style arguments. If omitted, module defaults are used.

        Returns:
            dict: Unified status with execution result or actionable error guidance.
        """
        try:
            module = self._loaded_modules.get("backtrader.btrun.btrun")
            if module is None:
                module, err = self._safe_import("backtrader.btrun.btrun")
                if module is None:
                    return self._err(
                        "Failed to import backtrader btrun module. Confirm source/backtrader is present and importable.",
                        Exception(err),
                    )

            if hasattr(module, "main"):
                result = module.main(argv) if argv is not None else module.main()
                return self._ok("btrun executed via main().", data={"result": result})

            return self._err(
                "btrun module does not expose main(). Use backtrader.btrun.btrun manually with repository-compatible arguments."
            )
        except Exception as exc:
            return self._err("btrun execution failed. Validate arguments and data file paths.", exc)

    # -------------------------------------------------------------------------
    # tools/rewrite-data.py
    # -------------------------------------------------------------------------
    def call_rewrite_data_parse_args(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Call parse_args from tools/rewrite-data.py.

        Args:
            args (list, optional): Argument vector for parser input.

        Returns:
            dict: Unified status with parser namespace/details.
        """
        try:
            mod = self._loaded_modules.get("tools.rewrite-data")
            if mod is None:
                path = os.path.join(source_path, "tools", "rewrite-data.py")
                mod, err = self._load_module_from_file("tools.rewrite_data_dynamic", path)
                if mod is None:
                    return self._err("Unable to load tools/rewrite-data.py for parse_args.", Exception(err))

            fn = getattr(mod, "parse_args", None)
            if fn is None:
                return self._err("parse_args not found in tools/rewrite-data.py. Confirm repository version compatibility.")
            res = fn(args) if args is not None else fn()
            return self._ok("rewrite-data parse_args executed.", data={"result": res})
        except Exception as exc:
            return self._err("rewrite-data parse_args failed. Check argument format.", exc)

    def call_rewrite_data_runstrat(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call runstrat from tools/rewrite-data.py.

        Args:
            *args: Positional arguments forwarded to runstrat.
            **kwargs: Keyword arguments forwarded to runstrat.

        Returns:
            dict: Unified status with execution output.
        """
        try:
            mod = self._loaded_modules.get("tools.rewrite-data")
            if mod is None:
                path = os.path.join(source_path, "tools", "rewrite-data.py")
                mod, err = self._load_module_from_file("tools.rewrite_data_dynamic", path)
                if mod is None:
                    return self._err("Unable to load tools/rewrite-data.py for runstrat.", Exception(err))

            fn = getattr(mod, "runstrat", None)
            if fn is None:
                return self._err("runstrat not found in tools/rewrite-data.py. Confirm repository version compatibility.")
            res = fn(*args, **kwargs)
            return self._ok("rewrite-data runstrat executed.", data={"result": res})
        except Exception as exc:
            return self._err("rewrite-data runstrat failed. Validate strategy/data parameters.", exc)

    # -------------------------------------------------------------------------
    # tools/yahoodownload.py
    # -------------------------------------------------------------------------
    def create_yahoo_download_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate YahooDownload from tools/yahoodownload.py.

        Args:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status with instantiated object.
        """
        try:
            mod = self._loaded_modules.get("tools.yahoodownload")
            if mod is None:
                mod, err = self._safe_import("tools.yahoodownload")
                if mod is None:
                    return self._err("Unable to import tools.yahoodownload.", Exception(err))

            cls = getattr(mod, "YahooDownload", None)
            if cls is None:
                return self._err("YahooDownload class not found in tools.yahoodownload.")
            inst = cls(*args, **kwargs)
            return self._ok("YahooDownload instance created.", data={"instance": inst})
        except Exception as exc:
            return self._err("Failed to create YahooDownload instance. Check constructor parameters.", exc)

    def call_yahoodownload_parse_args(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Call parse_args from tools/yahoodownload.py.

        Args:
            args (list, optional): Argument vector for parser input.

        Returns:
            dict: Unified status with parser output.
        """
        try:
            mod = self._loaded_modules.get("tools.yahoodownload")
            if mod is None:
                mod, err = self._safe_import("tools.yahoodownload")
                if mod is None:
                    return self._err("Unable to import tools.yahoodownload.", Exception(err))

            fn = getattr(mod, "parse_args", None)
            if fn is None:
                return self._err("parse_args not found in tools.yahoodownload.")
            res = fn(args) if args is not None else fn()
            return self._ok("yahoodownload parse_args executed.", data={"result": res})
        except Exception as exc:
            return self._err("yahoodownload parse_args failed. Verify CLI-style arguments.", exc)

    # -------------------------------------------------------------------------
    # contrib/utils/iqfeed-to-influxdb.py
    # -------------------------------------------------------------------------
    def create_iqfeed_tool_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate IQFeedTool from contrib/utils/iqfeed-to-influxdb.py.

        Args:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status with created instance.
        """
        try:
            mod = self._loaded_modules.get("contrib.utils.iqfeed-to-influxdb")
            if mod is None:
                path = os.path.join(source_path, "contrib", "utils", "iqfeed-to-influxdb.py")
                mod, err = self._load_module_from_file("contrib.utils.iqfeed_to_influxdb_dynamic", path)
                if mod is None:
                    return self._err("Unable to load contrib/utils/iqfeed-to-influxdb.py.", Exception(err))

            cls = getattr(mod, "IQFeedTool", None)
            if cls is None:
                return self._err("IQFeedTool class not found in contrib/utils/iqfeed-to-influxdb.py.")
            inst = cls(*args, **kwargs)
            return self._ok("IQFeedTool instance created.", data={"instance": inst})
        except Exception as exc:
            return self._err("Failed to create IQFeedTool instance. Validate required external service settings.", exc)

    # -------------------------------------------------------------------------
    # contrib/utils/influxdb-import.py
    # -------------------------------------------------------------------------
    def create_influxdb_tool_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate InfluxDBTool from contrib/utils/influxdb-import.py.

        Args:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status with created instance.
        """
        try:
            mod = self._loaded_modules.get("contrib.utils.influxdb-import")
            if mod is None:
                path = os.path.join(source_path, "contrib", "utils", "influxdb-import.py")
                mod, err = self._load_module_from_file("contrib.utils.influxdb_import_dynamic", path)
                if mod is None:
                    return self._err("Unable to load contrib/utils/influxdb-import.py.", Exception(err))

            cls = getattr(mod, "InfluxDBTool", None)
            if cls is None:
                return self._err("InfluxDBTool class not found in contrib/utils/influxdb-import.py.")
            inst = cls(*args, **kwargs)
            return self._ok("InfluxDBTool instance created.", data={"instance": inst})
        except Exception as exc:
            return self._err("Failed to create InfluxDBTool instance. Verify InfluxDB connection and credentials.", exc)

    # -------------------------------------------------------------------------
    # contrib/samples/pair-trading/pair-trading.py
    # -------------------------------------------------------------------------
    def create_pair_trading_strategy_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate PairTradingStrategy from contrib/samples/pair-trading/pair-trading.py.

        Args:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status with created strategy instance.
        """
        try:
            mod = self._loaded_modules.get("contrib.samples.pair-trading.pair-trading")
            if mod is None:
                path = os.path.join(source_path, "contrib", "samples", "pair-trading", "pair-trading.py")
                mod, err = self._load_module_from_file("contrib.samples.pair_trading_dynamic", path)
                if mod is None:
                    return self._err("Unable to load pair-trading sample module.", Exception(err))

            cls = getattr(mod, "PairTradingStrategy", None)
            if cls is None:
                return self._err("PairTradingStrategy class not found in pair-trading sample module.")
            inst = cls(*args, **kwargs)
            return self._ok("PairTradingStrategy instance created.", data={"instance": inst})
        except Exception as exc:
            return self._err("Failed to create PairTradingStrategy instance. Use Cerebro-managed instantiation for runtime use.", exc)

    def call_pair_trading_parse_args(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Call parse_args from pair-trading sample module.

        Args:
            args (list, optional): Parser argument list.

        Returns:
            dict: Unified status with parser result.
        """
        try:
            path = os.path.join(source_path, "contrib", "samples", "pair-trading", "pair-trading.py")
            mod, err = self._load_module_from_file("contrib.samples.pair_trading_dynamic", path)
            if mod is None:
                return self._err("Unable to load pair-trading sample for parse_args.", Exception(err))

            fn = getattr(mod, "parse_args", None)
            if fn is None:
                return self._err("parse_args not found in pair-trading sample module.")
            res = fn(args) if args is not None else fn()
            return self._ok("pair-trading parse_args executed.", data={"result": res})
        except Exception as exc:
            return self._err("pair-trading parse_args failed. Verify provided options.", exc)

    def call_pair_trading_runstrategy(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call runstrategy from pair-trading sample module.

        Args:
            *args: Positional arguments for runstrategy.
            **kwargs: Keyword arguments for runstrategy.

        Returns:
            dict: Unified status with run output.
        """
        try:
            path = os.path.join(source_path, "contrib", "samples", "pair-trading", "pair-trading.py")
            mod, err = self._load_module_from_file("contrib.samples.pair_trading_dynamic", path)
            if mod is None:
                return self._err("Unable to load pair-trading sample for runstrategy.", Exception(err))

            fn = getattr(mod, "runstrategy", None)
            if fn is None:
                return self._err("runstrategy not found in pair-trading sample module.")
            res = fn(*args, **kwargs)
            return self._ok("pair-trading runstrategy executed.", data={"result": res})
        except Exception as exc:
            return self._err("pair-trading runstrategy failed. Check data feeds and broker settings.", exc)

    # -------------------------------------------------------------------------
    # samples/weekdays-filler
    # -------------------------------------------------------------------------
    def create_weekdays_filler_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate WeekDaysFiller from samples/weekdays-filler/weekdaysfiller.py.

        Args:
            *args: Constructor positional arguments.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Unified status with created instance.
        """
        try:
            path = os.path.join(source_path, "samples", "weekdays-filler", "weekdaysfiller.py")
            mod, err = self._load_module_from_file("samples.weekdays_filler_dynamic", path)
            if mod is None:
                return self._err("Unable to load weekdaysfiller sample module.", Exception(err))

            cls = getattr(mod, "WeekDaysFiller", None)
            if cls is None:
                return self._err("WeekDaysFiller class not found in weekdaysfiller sample module.")
            inst = cls(*args, **kwargs)
            return self._ok("WeekDaysFiller instance created.", data={"instance": inst})
        except Exception as exc:
            return self._err("Failed to create WeekDaysFiller instance. Validate constructor inputs.", exc)

    def call_weekdaysaligner_parse_args(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Call parse_args from samples/weekdays-filler/weekdaysaligner.py.

        Args:
            args (list, optional): Parser argument list.

        Returns:
            dict: Unified status with parser namespace/output.
        """
        try:
            path = os.path.join(source_path, "samples", "weekdays-filler", "weekdaysaligner.py")
            mod, err = self._load_module_from_file("samples.weekdays_aligner_dynamic", path)
            if mod is None:
                return self._err("Unable to load weekdaysaligner sample module.", Exception(err))

            fn = getattr(mod, "parse_args", None)
            if fn is None:
                return self._err("parse_args not found in weekdaysaligner sample module.")
            res = fn(args) if args is not None else fn()
            return self._ok("weekdaysaligner parse_args executed.", data={"result": res})
        except Exception as exc:
            return self._err("weekdaysaligner parse_args failed. Review argument values.", exc)

    def call_weekdaysaligner_runstrat(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call runstrat from samples/weekdays-filler/weekdaysaligner.py.

        Args:
            *args: Positional args forwarded to runstrat.
            **kwargs: Keyword args forwarded to runstrat.

        Returns:
            dict: Unified status with strategy run result.
        """
        try:
            path = os.path.join(source_path, "samples", "weekdays-filler", "weekdaysaligner.py")
            mod, err = self._load_module_from_file("samples.weekdays_aligner_dynamic", path)
            if mod is None:
                return self._err("Unable to load weekdaysaligner sample module.", Exception(err))

            fn = getattr(mod, "runstrat", None)
            if fn is None:
                return self._err("runstrat not found in weekdaysaligner sample module.")
            res = fn(*args, **kwargs)
            return self._ok("weekdaysaligner runstrat executed.", data={"result": res})
        except Exception as exc:
            return self._err("weekdaysaligner runstrat failed. Verify feed and calendar options.", exc)