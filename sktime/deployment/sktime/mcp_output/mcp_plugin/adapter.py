import os
import sys
import traceback
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the sktime repository.

    This adapter prioritizes direct in-repo imports and provides a graceful fallback
    mode when imports are unavailable or partially broken in the runtime environment.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = {}
        self._errors = {}
        self._init_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"status": status, "message": message}
        if data is not None:
            payload["data"] = data
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _safe_import(self, import_path: str, attr: Optional[str] = None) -> Tuple[bool, Any, str]:
        try:
            module = __import__(import_path, fromlist=[attr] if attr else [])
            if attr:
                if not hasattr(module, attr):
                    return False, None, f"Attribute '{attr}' not found in '{import_path}'."
                return True, getattr(module, attr), ""
            return True, module, ""
        except Exception as e:
            return False, None, f"Failed to import '{import_path}': {e}"

    def _init_imports(self) -> None:
        """
        Import selected high-value modules/classes/functions inferred from analysis.
        """
        targets = {
            "show_versions": ("sktime.utils._maint._show_versions", "show_versions"),
            "all_estimators": ("sktime.registry", "all_estimators"),
            "load_airline": ("sktime.datasets.forecasting.airline", "load_airline"),
            "load_lynx": ("sktime.datasets.forecasting.lynx", "load_lynx"),
            "NaiveForecaster": ("sktime.forecasting.naive", "NaiveForecaster"),
            "temporal_train_test_split": ("sktime.split", "temporal_train_test_split"),
            "ForecastingHorizon": ("sktime.forecasting.base", "ForecastingHorizon"),
            "make_reduction": ("sktime.forecasting.compose", "make_reduction"),
            "ExponentTransformer": ("sktime.transformations.series.exponent", "ExponentTransformer"),
            "BoxCoxTransformer": ("sktime.transformations.series.boxcox", "BoxCoxTransformer"),
            "make_pipeline": ("sktime.pipeline", "make_pipeline"),
            "mean_absolute_percentage_error": (
                "sktime.performance_metrics.forecasting",
                "mean_absolute_percentage_error",
            ),
        }

        failures = 0
        for key, (mod, attr) in targets.items():
            ok, obj, err = self._safe_import(mod, attr)
            if ok:
                self._loaded[key] = obj
            else:
                self._errors[key] = err
                failures += 1

        if failures > 0 and failures == len(targets):
            self.mode = "fallback"

    def _require(self, key: str) -> Tuple[bool, Any, Dict[str, Any]]:
        if self.mode != "import":
            return False, None, self._result(
                "error",
                "Adapter is running in fallback mode.",
                guidance="Ensure repository source path is mounted and dependencies are installed.",
            )
        if key not in self._loaded:
            msg = self._errors.get(key, f"Component '{key}' is unavailable.")
            return False, None, self._result(
                "error",
                msg,
                guidance="Install optional dependencies required by sktime and retry.",
            )
        return True, self._loaded[key], {}

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        return self._result(
            "success",
            "Adapter status retrieved.",
            data={
                "mode": self.mode,
                "loaded_components": sorted(self._loaded.keys()),
                "failed_components": self._errors,
            },
        )

    def show_versions(self) -> Dict[str, Any]:
        ok, fn, err = self._require("show_versions")
        if not ok:
            return err
        try:
            info = fn()
            return self._result("success", "Version information collected.", data={"versions": info})
        except Exception:
            return self._result(
                "error",
                "Failed to collect version information.",
                data={"traceback": traceback.format_exc()},
                guidance="Verify core dependencies (numpy, pandas, scipy, scikit-learn) are importable.",
            )

    # -------------------------------------------------------------------------
    # Registry / discovery
    # -------------------------------------------------------------------------
    def list_estimators(self, estimator_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        List sktime estimators from the registry.

        Parameters:
        - estimator_types: optional list of estimator type filters.

        Returns:
        - Unified status dictionary with estimator metadata.
        """
        ok, fn, err = self._require("all_estimators")
        if not ok:
            return err
        try:
            kwargs = {}
            if estimator_types:
                kwargs["estimator_types"] = estimator_types
            estimators = fn(**kwargs)
            serial = [str(e) for e in estimators]
            return self._result("success", "Estimators listed.", data={"count": len(serial), "items": serial})
        except Exception:
            return self._result(
                "error",
                "Failed to list estimators.",
                data={"traceback": traceback.format_exc()},
                guidance="Check estimator filter names and installed optional dependencies.",
            )

    # -------------------------------------------------------------------------
    # Dataset loaders
    # -------------------------------------------------------------------------
    def load_airline(self) -> Dict[str, Any]:
        ok, fn, err = self._require("load_airline")
        if not ok:
            return err
        try:
            y = fn()
            return self._result("success", "Airline dataset loaded.", data={"type": str(type(y)), "length": len(y)})
        except Exception:
            return self._result("error", "Failed to load airline dataset.", data={"traceback": traceback.format_exc()})

    def load_lynx(self) -> Dict[str, Any]:
        ok, fn, err = self._require("load_lynx")
        if not ok:
            return err
        try:
            y = fn()
            return self._result("success", "Lynx dataset loaded.", data={"type": str(type(y)), "length": len(y)})
        except Exception:
            return self._result("error", "Failed to load lynx dataset.", data={"traceback": traceback.format_exc()})

    # -------------------------------------------------------------------------
    # Class instance methods
    # -------------------------------------------------------------------------
    def instance_naive_forecaster(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of sktime.forecasting.naive.NaiveForecaster.

        Parameters:
        - **kwargs: constructor arguments for NaiveForecaster.

        Returns:
        - Unified status dictionary containing instance metadata.
        """
        ok, cls, err = self._require("NaiveForecaster")
        if not ok:
            return err
        try:
            obj = cls(**kwargs)
            return self._result(
                "success",
                "NaiveForecaster instance created.",
                data={"class": obj.__class__.__name__, "module": obj.__class__.__module__, "params": kwargs},
            )
        except Exception:
            return self._result(
                "error",
                "Failed to create NaiveForecaster instance.",
                data={"traceback": traceback.format_exc()},
                guidance="Validate constructor parameters against sktime NaiveForecaster signature.",
            )

    def instance_forecasting_horizon(self, values: Any, is_relative: bool = True) -> Dict[str, Any]:
        ok, cls, err = self._require("ForecastingHorizon")
        if not ok:
            return err
        try:
            obj = cls(values, is_relative=is_relative)
            return self._result(
                "success",
                "ForecastingHorizon instance created.",
                data={"class": obj.__class__.__name__, "is_relative": is_relative, "values": list(values)},
            )
        except Exception:
            return self._result(
                "error",
                "Failed to create ForecastingHorizon instance.",
                data={"traceback": traceback.format_exc()},
                guidance="Use array-like forecast horizon values and correct relative/absolute mode.",
            )

    def instance_exponent_transformer(self, **kwargs: Any) -> Dict[str, Any]:
        ok, cls, err = self._require("ExponentTransformer")
        if not ok:
            return err
        try:
            obj = cls(**kwargs)
            return self._result("success", "ExponentTransformer instance created.", data={"params": kwargs})
        except Exception:
            return self._result("error", "Failed to create ExponentTransformer.", data={"traceback": traceback.format_exc()})

    def instance_boxcox_transformer(self, **kwargs: Any) -> Dict[str, Any]:
        ok, cls, err = self._require("BoxCoxTransformer")
        if not ok:
            return err
        try:
            obj = cls(**kwargs)
            return self._result("success", "BoxCoxTransformer instance created.", data={"params": kwargs})
        except Exception:
            return self._result("error", "Failed to create BoxCoxTransformer.", data={"traceback": traceback.format_exc()})

    # -------------------------------------------------------------------------
    # Function call methods
    # -------------------------------------------------------------------------
    def call_temporal_train_test_split(self, y: Any, **kwargs: Any) -> Dict[str, Any]:
        ok, fn, err = self._require("temporal_train_test_split")
        if not ok:
            return err
        try:
            split = fn(y, **kwargs)
            return self._result(
                "success",
                "Temporal train-test split completed.",
                data={"parts": len(split), "types": [str(type(p)) for p in split]},
            )
        except Exception:
            return self._result(
                "error",
                "Failed to perform temporal train-test split.",
                data={"traceback": traceback.format_exc()},
                guidance="Provide valid time-indexed series and compatible split arguments.",
            )

    def call_make_reduction(self, estimator: Any, strategy: str = "recursive", window_length: int = 10, **kwargs: Any) -> Dict[str, Any]:
        ok, fn, err = self._require("make_reduction")
        if not ok:
            return err
        try:
            forecaster = fn(estimator=estimator, strategy=strategy, window_length=window_length, **kwargs)
            return self._result(
                "success",
                "Reduction forecaster created.",
                data={"class": forecaster.__class__.__name__, "strategy": strategy, "window_length": window_length},
            )
        except Exception:
            return self._result(
                "error",
                "Failed to create reduction forecaster.",
                data={"traceback": traceback.format_exc()},
                guidance="Check estimator compatibility with sktime make_reduction.",
            )

    def call_make_pipeline(self, *steps: Any) -> Dict[str, Any]:
        ok, fn, err = self._require("make_pipeline")
        if not ok:
            return err
        try:
            pipe = fn(*steps)
            return self._result(
                "success",
                "Pipeline created.",
                data={"class": pipe.__class__.__name__, "n_steps": len(steps)},
            )
        except Exception:
            return self._result(
                "error",
                "Failed to create pipeline.",
                data={"traceback": traceback.format_exc()},
                guidance="Ensure all steps implement compatible sktime estimator interfaces.",
            )

    def call_mean_absolute_percentage_error(self, y_true: Any, y_pred: Any, **kwargs: Any) -> Dict[str, Any]:
        ok, fn, err = self._require("mean_absolute_percentage_error")
        if not ok:
            return err
        try:
            score = fn(y_true, y_pred, **kwargs)
            return self._result("success", "MAPE computed.", data={"score": float(score)})
        except Exception:
            return self._result(
                "error",
                "Failed to compute MAPE.",
                data={"traceback": traceback.format_exc()},
                guidance="Ensure y_true and y_pred are aligned and numeric.",
            )

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def call_component(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call any loaded callable component by registered name.
        """
        if name not in self._loaded:
            return self._result(
                "error",
                f"Component '{name}' is not loaded.",
                guidance="Check adapter status and use a valid component name.",
            )
        target = self._loaded[name]
        if not callable(target):
            return self._result("error", f"Component '{name}' is not callable.")
        try:
            out = target(*args, **kwargs)
            return self._result("success", f"Component '{name}' executed.", data={"output_type": str(type(out)), "output": out})
        except Exception:
            return self._result(
                "error",
                f"Execution failed for component '{name}'.",
                data={"traceback": traceback.format_exc()},
                guidance="Validate input arguments against the callable signature.",
            )

    def describe_component(self, name: str) -> Dict[str, Any]:
        if name not in self._loaded:
            return self._result("error", f"Component '{name}' is not loaded.")
        obj = self._loaded[name]
        try:
            sig = str(inspect.signature(obj)) if callable(obj) else None
            doc = inspect.getdoc(obj)
            return self._result(
                "success",
                f"Component '{name}' described.",
                data={"type": str(type(obj)), "signature": sig, "doc": doc},
            )
        except Exception:
            return self._result("error", f"Failed to describe component '{name}'.", data={"traceback": traceback.format_exc()})