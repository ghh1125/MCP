import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the sktime repository.

    This adapter focuses on robust, low-intrusion runtime integration:
    - Attempts direct imports from repository code available under `source/`
    - Exposes practical high-value constructors/calls inferred from analysis
    - Provides consistent structured responses with status and diagnostics
    - Falls back gracefully when optional dependencies are missing
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._bootstrap_imports()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
            "guidance": guidance,
        }

    def _safe_import(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"

    def _bootstrap_imports(self) -> None:
        core_modules = [
            "sktime",
            "sktime.registry",
            "sktime.forecasting.naive",
            "sktime.forecasting.arima",
            "sktime.forecasting.ets",
            "sktime.forecasting.exp_smoothing",
            "sktime.forecasting.theta",
            "sktime.datasets",
            "sktime.performance_metrics.forecasting",
            "sktime.split",
            "sktime.transformations.series.boxcox",
            "sktime.transformations.series.difference",
            "sktime.classification.dummy",
            "sktime.regression.dummy",
            "sktime.clustering.k_means",
            "sktime.detection.dummy",
        ]
        for mod in core_modules:
            self._safe_import(mod)

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status dictionary including loaded module count and
            import failures with actionable guidance.
        """
        if self._import_errors:
            return self._result(
                status="degraded",
                message="Adapter initialized with partial imports.",
                data={
                    "loaded_modules": sorted(self._modules.keys()),
                    "failed_imports": self._import_errors,
                },
                guidance=(
                    "Install optional dependencies required by the failed modules "
                    "or restrict calls to successfully loaded components."
                ),
            )
        return self._result(
            status="ok",
            message="Adapter initialized successfully.",
            data={"loaded_modules": sorted(self._modules.keys())},
        )

    # -------------------------------------------------------------------------
    # Registry / discovery
    # -------------------------------------------------------------------------
    def list_estimators(self, estimator_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        List estimators via sktime registry.

        Args:
            estimator_types: Optional list of scitype strings to filter estimators.

        Returns:
            dict: Status with estimator names or error diagnostics.
        """
        try:
            reg = importlib.import_module("sktime.registry")
            all_estimators = getattr(reg, "all_estimators", None)
            if all_estimators is None:
                return self._result(
                    status="error",
                    message="Registry API not available.",
                    guidance="Ensure sktime.registry exposes all_estimators in this repository version.",
                )
            result = all_estimators(estimator_types=estimator_types) if estimator_types else all_estimators()
            return self._result(
                status="ok",
                message="Estimators listed successfully.",
                data={"estimators": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to list estimators.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Verify repository version compatibility and optional dependencies.",
            )

    # -------------------------------------------------------------------------
    # Dataset access functions
    # -------------------------------------------------------------------------
    def call_load_airline(self) -> Dict[str, Any]:
        """
        Call `sktime.datasets.load_airline`.

        Returns:
            dict: Loaded time series or actionable error details.
        """
        try:
            mod = importlib.import_module("sktime.datasets")
            fn = getattr(mod, "load_airline")
            y = fn()
            return self._result(status="ok", message="Dataset loaded.", data={"y": y})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to load airline dataset.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check dataset packaging in source and pandas dependency availability.",
            )

    def call_load_longley(self) -> Dict[str, Any]:
        try:
            mod = importlib.import_module("sktime.datasets")
            fn = getattr(mod, "load_longley")
            out = fn()
            return self._result(status="ok", message="Dataset loaded.", data={"dataset": out})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to load longley dataset.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Ensure forecasting dataset loaders are available in current repository snapshot.",
            )

    # -------------------------------------------------------------------------
    # Forecaster class instance methods
    # -------------------------------------------------------------------------
    def instance_naive_forecaster(self, strategy: str = "last", sp: int = 1) -> Dict[str, Any]:
        """
        Create an instance of `sktime.forecasting.naive.NaiveForecaster`.

        Args:
            strategy: Forecasting strategy (e.g., 'last', 'mean', 'drift').
            sp: Seasonal periodicity.

        Returns:
            dict: Status and created estimator instance.
        """
        try:
            mod = importlib.import_module("sktime.forecasting.naive")
            cls = getattr(mod, "NaiveForecaster")
            obj = cls(strategy=strategy, sp=sp)
            return self._result(status="ok", message="NaiveForecaster instance created.", data={"instance": obj})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create NaiveForecaster.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Validate arguments and ensure sktime forecasting module imports cleanly.",
            )

    def instance_auto_arima(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of `sktime.forecasting.arima.AutoARIMA`.

        Args:
            **kwargs: Constructor parameters forwarded to AutoARIMA.

        Returns:
            dict: Status and created estimator instance.
        """
        try:
            mod = importlib.import_module("sktime.forecasting.arima")
            cls = getattr(mod, "AutoARIMA")
            obj = cls(**kwargs)
            return self._result(status="ok", message="AutoARIMA instance created.", data={"instance": obj})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create AutoARIMA.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Install optional dependency pmdarima and retry.",
            )

    def instance_theta_forecaster(self, **kwargs: Any) -> Dict[str, Any]:
        try:
            mod = importlib.import_module("sktime.forecasting.theta")
            cls = getattr(mod, "ThetaForecaster")
            obj = cls(**kwargs)
            return self._result(status="ok", message="ThetaForecaster instance created.", data={"instance": obj})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create ThetaForecaster.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check statsmodels availability and parameter validity.",
            )

    # -------------------------------------------------------------------------
    # Metrics and split utilities
    # -------------------------------------------------------------------------
    def call_mean_absolute_percentage_error(self, y_true: Any, y_pred: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call `sktime.performance_metrics.forecasting.mean_absolute_percentage_error`.

        Args:
            y_true: Ground-truth values.
            y_pred: Predicted values.
            **kwargs: Additional metric parameters.

        Returns:
            dict: Status and metric value.
        """
        try:
            mod = importlib.import_module("sktime.performance_metrics.forecasting")
            fn = getattr(mod, "mean_absolute_percentage_error")
            value = fn(y_true, y_pred, **kwargs)
            return self._result(status="ok", message="MAPE computed.", data={"value": value})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to compute MAPE.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Ensure y_true and y_pred are aligned and coercible to supported sktime formats.",
            )

    def call_temporal_train_test_split(self, y: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            mod = importlib.import_module("sktime.split")
            fn = getattr(mod, "temporal_train_test_split")
            split = fn(y, **kwargs)
            return self._result(status="ok", message="Temporal split completed.", data={"split": split})
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to perform temporal train/test split.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Validate forecasting index type and split configuration parameters.",
            )

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic function caller for any importable module function.

        Args:
            module_path: Full module path (e.g., 'sktime.datasets').
            function_name: Function symbol to call from module.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Status and call result or structured error.
        """
        try:
            module = importlib.import_module(module_path)
            fn = getattr(module, function_name, None)
            if fn is None or not callable(fn):
                return self._result(
                    status="error",
                    message="Function not found.",
                    guidance="Check module path and function name for this repository version.",
                )
            result = fn(*args, **kwargs)
            return self._result(status="ok", message="Function call succeeded.", data={"result": result})
        except Exception as exc:
            return self._result(
                status="error",
                message="Function call failed.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Inspect arguments and dependency requirements for the target function.",
            )

    def instance_class(self, module_path: str, class_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic class instantiation helper for import-mode usage.

        Args:
            module_path: Full module path containing the class.
            class_name: Class symbol to instantiate.
            **kwargs: Constructor keyword arguments.

        Returns:
            dict: Status and created object or structured error details.
        """
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name, None)
            if cls is None:
                return self._result(
                    status="error",
                    message="Class not found.",
                    guidance="Verify class name and module path against repository source.",
                )
            obj = cls(**kwargs)
            return self._result(status="ok", message="Class instance created.", data={"instance": obj})
        except Exception as exc:
            return self._result(
                status="error",
                message="Class instantiation failed.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check constructor parameters and install any optional dependencies.",
            )

    def debug_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for adapter-level diagnostics.

        Returns:
            dict: Status and traceback string. Useful for MCP orchestration debug.
        """
        return self._result(
            status="ok",
            message="Traceback snapshot generated.",
            data={"traceback": traceback.format_exc()},
        )