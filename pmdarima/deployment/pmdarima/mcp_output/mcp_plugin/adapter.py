import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the pmdarima repository.

    This adapter attempts direct imports from the local `source` directory and exposes
    high-value APIs from the analyzed project with a unified response structure.

    Unified return schema:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "fallback",
        "message": str,
        "data": Any,
        "error": Optional[str],
        "traceback": Optional[str],
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._imports_ok = False
        self._import_errors: List[str] = []
        self._load_modules()

    def _resp(
        self,
        status: str,
        message: str,
        data: Any = None,
        error: Optional[str] = None,
        with_traceback: bool = False,
    ) -> Dict[str, Any]:
        tb = traceback.format_exc() if with_traceback and error else None
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
            "error": error,
            "traceback": tb,
        }

    def _load_modules(self) -> None:
        module_names = [
            "pmdarima",
            "pmdarima.arima",
            "pmdarima.arima.auto",
            "pmdarima.arima.arima",
            "pmdarima.arima.utils",
            "pmdarima.arima.seasonality",
            "pmdarima.arima.stationarity",
            "pmdarima.pipeline",
            "pmdarima.metrics",
            "pmdarima.model_selection",
            "pmdarima.model_selection._split",
            "pmdarima.model_selection._validation",
            "pmdarima.preprocessing",
            "pmdarima.preprocessing.endog.boxcox",
            "pmdarima.preprocessing.endog.log",
            "pmdarima.preprocessing.exog.dates",
            "pmdarima.preprocessing.exog.fourier",
            "pmdarima.datasets",
            "pmdarima.utils",
            "pmdarima.utils.array",
            "pmdarima.utils.visualization",
            "pmdarima.utils.wrapped",
        ]
        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors.append(f"{name}: {e}")

        self._imports_ok = len(self._import_errors) == 0
        if not self._imports_ok:
            self.mode = "fallback"

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import health and report loaded modules.

        Returns:
            Unified response with mode, loaded modules, and import errors if any.
        """
        return self._resp(
            "success" if self._imports_ok else "fallback",
            "Adapter initialized." if self._imports_ok else "Import mode unavailable; fallback enabled.",
            data={
                "imports_ok": self._imports_ok,
                "loaded_modules": sorted(list(self._modules.keys())),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
        )

    def _require_imports(self) -> Optional[Dict[str, Any]]:
        if self.mode != "import":
            return self._resp(
                "fallback",
                "Import mode is unavailable. Ensure repository dependencies are installed and C-extensions are build-ready.",
                data={"hint": "Install required deps: numpy, scipy, scikit-learn, pandas, statsmodels, joblib, Cython."},
            )
        return None

    # -------------------------------------------------------------------------
    # Core ARIMA API
    # -------------------------------------------------------------------------
    def create_arima(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an ARIMA estimator instance.

        Parameters:
            *args: Positional args passed to pmdarima.arima.ARIMA
            **kwargs: Keyword args such as order, seasonal_order, suppress_warnings, etc.

        Returns:
            Unified response with created ARIMA instance in data.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.arima"], "ARIMA")
            obj = cls(*args, **kwargs)
            return self._resp("success", "ARIMA instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create ARIMA instance.", error=str(e), with_traceback=True)

    def call_auto_arima(self, y: Any, X: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Fit and return an auto_arima model.

        Parameters:
            y: Endogenous time series.
            X: Optional exogenous variables.
            **kwargs: auto_arima parameters (seasonal, m, stepwise, trace, etc.).

        Returns:
            Unified response with fitted model.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            fn = getattr(self._modules["pmdarima.arima"], "auto_arima")
            model = fn(y, X=X, **kwargs)
            return self._resp("success", "auto_arima executed successfully.", data=model)
        except Exception as e:
            return self._resp("error", "auto_arima execution failed.", error=str(e), with_traceback=True)

    # -------------------------------------------------------------------------
    # Pipeline API
    # -------------------------------------------------------------------------
    def create_pipeline(self, steps: List[Tuple[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        Create a pmdarima pipeline.

        Parameters:
            steps: List of (name, transformer/estimator) tuples.
            **kwargs: Additional Pipeline constructor parameters.

        Returns:
            Unified response with pipeline instance.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.pipeline"], "Pipeline")
            pipe = cls(steps=steps, **kwargs)
            return self._resp("success", "Pipeline instance created.", data=pipe)
        except Exception as e:
            return self._resp("error", "Failed to create Pipeline.", error=str(e), with_traceback=True)

    # -------------------------------------------------------------------------
    # Model selection API
    # -------------------------------------------------------------------------
    def create_sliding_window_split(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create SlidingWindowForecastCV splitter.

        Parameters:
            *args, **kwargs: Passed to SlidingWindowForecastCV constructor.

        Returns:
            Unified response with splitter instance.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.model_selection"], "SlidingWindowForecastCV")
            obj = cls(*args, **kwargs)
            return self._resp("success", "SlidingWindowForecastCV instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create SlidingWindowForecastCV.", error=str(e), with_traceback=True)

    def create_rolling_window_split(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create RollingForecastCV splitter.

        Parameters:
            *args, **kwargs: Passed to RollingForecastCV constructor.

        Returns:
            Unified response with splitter instance.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.model_selection"], "RollingForecastCV")
            obj = cls(*args, **kwargs)
            return self._resp("success", "RollingForecastCV instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create RollingForecastCV.", error=str(e), with_traceback=True)

    def call_cross_validate(self, estimator: Any, y: Any, X: Any = None, cv: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Run pmdarima model cross-validation.

        Parameters:
            estimator: pmdarima-compatible estimator.
            y: Endogenous series.
            X: Optional exogenous matrix.
            cv: Cross-validator instance.
            **kwargs: Additional cross_validate kwargs.

        Returns:
            Unified response with CV results dictionary.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            fn = getattr(self._modules["pmdarima.model_selection"], "cross_validate")
            out = fn(estimator=estimator, y=y, X=X, cv=cv, **kwargs)
            return self._resp("success", "cross_validate executed successfully.", data=out)
        except Exception as e:
            return self._resp("error", "cross_validate execution failed.", error=str(e), with_traceback=True)

    # -------------------------------------------------------------------------
    # Preprocessing API
    # -------------------------------------------------------------------------
    def create_boxcox_endog_transformer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.preprocessing.endog.boxcox"], "BoxCoxEndogTransformer")
            obj = cls(*args, **kwargs)
            return self._resp("success", "BoxCoxEndogTransformer instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create BoxCoxEndogTransformer.", error=str(e), with_traceback=True)

    def create_log_endog_transformer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.preprocessing.endog.log"], "LogEndogTransformer")
            obj = cls(*args, **kwargs)
            return self._resp("success", "LogEndogTransformer instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create LogEndogTransformer.", error=str(e), with_traceback=True)

    def create_date_featurizer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.preprocessing.exog.dates"], "DateFeaturizer")
            obj = cls(*args, **kwargs)
            return self._resp("success", "DateFeaturizer instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create DateFeaturizer.", error=str(e), with_traceback=True)

    def create_fourier_featurizer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            cls = getattr(self._modules["pmdarima.preprocessing.exog.fourier"], "FourierFeaturizer")
            obj = cls(*args, **kwargs)
            return self._resp("success", "FourierFeaturizer instance created.", data=obj)
        except Exception as e:
            return self._resp("error", "Failed to create FourierFeaturizer.", error=str(e), with_traceback=True)

    # -------------------------------------------------------------------------
    # Datasets and utilities
    # -------------------------------------------------------------------------
    def call_dataset_loader(self, loader_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a dataset loader from pmdarima.datasets.

        Supported examples:
            load_airpassengers, load_wineind, load_lynx, load_sunspots, etc.

        Parameters:
            loader_name: Exact function name in pmdarima.datasets.
            *args, **kwargs: Passed to loader.

        Returns:
            Unified response with dataset output.
        """
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            mod = self._modules["pmdarima.datasets"]
            if not hasattr(mod, loader_name):
                return self._resp(
                    "error",
                    "Requested dataset loader not found.",
                    error=f"Unknown loader '{loader_name}'. Use an existing function from pmdarima.datasets.",
                )
            fn = getattr(mod, loader_name)
            out = fn(*args, **kwargs)
            return self._resp("success", f"{loader_name} executed successfully.", data=out)
        except Exception as e:
            return self._resp("error", f"{loader_name} execution failed.", error=str(e), with_traceback=True)

    def call_metric(self, metric_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fallback = self._require_imports()
        if fallback:
            return fallback
        try:
            mod = self._modules["pmdarima.metrics"]
            if not hasattr(mod, metric_name):
                return self._resp(
                    "error",
                    "Requested metric function not found.",
                    error=f"Unknown metric '{metric_name}'. Use a valid function from pmdarima.metrics.",
                )
            fn = getattr(mod, metric_name)
            out = fn(*args, **kwargs)
            return self._resp("success", f"{metric_name} executed successfully.", data=out)
        except Exception as e:
            return self._resp("error", f"{metric_name} execution failed.", error=str(e), with_traceback=True)