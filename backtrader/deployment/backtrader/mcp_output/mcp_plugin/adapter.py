import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the backtrader repository.

    This adapter prioritizes direct imports from repository source code and provides
    graceful fallbacks when optional modules are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _load_optional(self, key: str, import_path: str) -> None:
        try:
            module = __import__(import_path, fromlist=["*"])
            self._modules[key] = module
        except Exception as exc:
            self._modules[key] = None
            self._import_errors[key] = (
                f"Failed to import '{import_path}'. "
                f"Install or enable required optional dependency. Details: {exc}"
            )

    def _load_modules(self) -> None:
        self._load_optional("backtrader", "backtrader")
        self._load_optional("cerebro_mod", "backtrader.cerebro")
        self._load_optional("strategy_mod", "backtrader.strategy")
        self._load_optional("broker_mod", "backtrader.broker")
        self._load_optional("feeds_mod", "backtrader.feeds")
        self._load_optional("analyzers_mod", "backtrader.analyzers")
        self._load_optional("indicators_mod", "backtrader.indicators")
        self._load_optional("observers_mod", "backtrader.observers")
        self._load_optional("sizers_mod", "backtrader.sizers")
        self._load_optional("stores_mod", "backtrader.stores")
        self._load_optional("signals_mod", "backtrader.signals")
        self._load_optional("btrun_mod", "backtrader.btrun.btrun")

    def _require(self, key: str) -> Optional[Any]:
        mod = self._modules.get(key)
        if mod is None:
            return None
        return mod

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate import-mode readiness and return diagnostic status.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        loaded = {k: (v is not None) for k, v in self._modules.items()}
        status = "ok" if any(loaded.values()) else "error"
        return self._result(
            status,
            loaded_modules=loaded,
            import_errors=self._import_errors,
            guidance="Ensure repository source exists under the configured source path.",
        )

    # -------------------------------------------------------------------------
    # Core class factories
    # -------------------------------------------------------------------------
    def create_cerebro(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a backtrader.cerebro.Cerebro instance.

        Parameters:
            **kwargs: Keyword arguments passed directly to Cerebro constructor.

        Returns:
            dict: status, instance or error guidance.
        """
        mod = self._require("cerebro_mod")
        if mod is None or not hasattr(mod, "Cerebro"):
            return self._result(
                "error",
                error="Cerebro class is unavailable.",
                guidance=self._import_errors.get(
                    "cerebro_mod",
                    "Verify backtrader.cerebro is present in repository source.",
                ),
            )
        try:
            instance = mod.Cerebro(**kwargs)
            return self._result("ok", instance=instance, class_name="backtrader.cerebro.Cerebro")
        except Exception as exc:
            return self._result("error", error=f"Failed to create Cerebro: {exc}")

    def create_strategy(self, strategy_class_name: str = "Strategy", **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a strategy class from backtrader.strategy module.

        Parameters:
            strategy_class_name: Class name to instantiate (default: Strategy).
            **kwargs: Constructor parameters for the strategy class.

        Returns:
            dict: status and created instance when possible.
        """
        mod = self._require("strategy_mod")
        if mod is None:
            return self._result(
                "error",
                error="Strategy module is unavailable.",
                guidance=self._import_errors.get("strategy_mod", "Check backtrader.strategy import path."),
            )
        cls = getattr(mod, strategy_class_name, None)
        if cls is None:
            return self._result(
                "error",
                error=f"Strategy class '{strategy_class_name}' not found.",
                guidance="Use a valid class from backtrader.strategy.",
            )
        try:
            instance = cls(**kwargs)
            return self._result("ok", instance=instance, class_name=f"backtrader.strategy.{strategy_class_name}")
        except Exception as exc:
            return self._result("error", error=f"Failed to instantiate strategy class: {exc}")

    def create_broker_base(self, class_name: str = "BrokerBase", **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a broker class from backtrader.broker.

        Parameters:
            class_name: Broker class name in backtrader.broker.
            **kwargs: Constructor args for selected broker class.

        Returns:
            dict: status and broker instance or actionable error.
        """
        mod = self._require("broker_mod")
        if mod is None:
            return self._result(
                "error",
                error="Broker module is unavailable.",
                guidance=self._import_errors.get("broker_mod", "Check backtrader.broker source module."),
            )
        cls = getattr(mod, class_name, None)
        if cls is None:
            return self._result(
                "error",
                error=f"Broker class '{class_name}' not found.",
                guidance="Inspect backtrader.broker for valid class names.",
            )
        try:
            instance = cls(**kwargs)
            return self._result("ok", instance=instance, class_name=f"backtrader.broker.{class_name}")
        except Exception as exc:
            return self._result("error", error=f"Failed to instantiate broker class: {exc}")

    # -------------------------------------------------------------------------
    # CLI-related methods from analysis
    # -------------------------------------------------------------------------
    def call_btrun(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute backtrader CLI entrypoint from backtrader.btrun.btrun.

        Parameters:
            argv: Optional argument list. If omitted, uses current process args behavior.

        Returns:
            dict: status with return code/result or error details.
        """
        mod = self._require("btrun_mod")
        if mod is None:
            return self._result(
                "error",
                error="btrun CLI module is unavailable.",
                guidance=self._import_errors.get("btrun_mod", "Ensure backtrader.btrun.btrun exists."),
            )
        try:
            if hasattr(mod, "main"):
                result = mod.main(argv) if argv is not None else mod.main()
                return self._result("ok", result=result, entrypoint="backtrader.btrun.btrun.main")
            return self._result(
                "error",
                error="No main entrypoint found in btrun module.",
                guidance="Use a module version exposing main(argv).",
            )
        except SystemExit as exc:
            return self._result("ok", result=getattr(exc, "code", 0), note="CLI exited via SystemExit.")
        except Exception as exc:
            return self._result("error", error=f"Failed to execute btrun: {exc}")

    # -------------------------------------------------------------------------
    # Generic module accessors for broad repository coverage
    # -------------------------------------------------------------------------
    def get_module(self, module_key: str) -> Dict[str, Any]:
        """
        Retrieve a loaded module object by adapter key.

        Parameters:
            module_key: One of internal module keys, e.g., 'feeds_mod', 'indicators_mod'.

        Returns:
            dict: status and module object when available.
        """
        module = self._modules.get(module_key)
        if module is None:
            return self._result(
                "error",
                error=f"Module key '{module_key}' is not available.",
                guidance=self._import_errors.get(module_key, "Call health_check() for diagnostics."),
            )
        return self._result("ok", module=module, module_key=module_key)

    def create_from_module(self, module_key: str, class_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class from a previously loaded module.

        Parameters:
            module_key: Internal loaded module key.
            class_name: Class name inside that module.
            **kwargs: Constructor args.

        Returns:
            dict: status and instance.
        """
        module = self._modules.get(module_key)
        if module is None:
            return self._result(
                "error",
                error=f"Module '{module_key}' is unavailable.",
                guidance=self._import_errors.get(module_key, "Verify optional dependencies and source path."),
            )
        cls = getattr(module, class_name, None)
        if cls is None:
            return self._result(
                "error",
                error=f"Class '{class_name}' not found in module '{module_key}'.",
                guidance="Use get_module() and inspect available attributes.",
            )
        try:
            instance = cls(**kwargs)
            return self._result("ok", instance=instance, module_key=module_key, class_name=class_name)
        except Exception as exc:
            return self._result("error", error=f"Failed to instantiate '{class_name}': {exc}")

    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from a loaded module by name.

        Parameters:
            module_key: Internal module key.
            function_name: Callable attribute name.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: status and function return value.
        """
        module = self._modules.get(module_key)
        if module is None:
            return self._result(
                "error",
                error=f"Module '{module_key}' is unavailable.",
                guidance=self._import_errors.get(module_key, "Check import diagnostics with health_check()."),
            )
        fn = getattr(module, function_name, None)
        if fn is None or not callable(fn):
            return self._result(
                "error",
                error=f"Function '{function_name}' not found or not callable in '{module_key}'.",
                guidance="Inspect module attributes before invoking.",
            )
        try:
            value = fn(*args, **kwargs)
            return self._result("ok", result=value, module_key=module_key, function_name=function_name)
        except Exception as exc:
            return self._result("error", error=f"Function call failed: {exc}")