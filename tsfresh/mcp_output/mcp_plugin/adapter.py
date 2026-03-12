import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for tsfresh repository.

    This adapter prefers direct Python imports from the local source tree and
    gracefully falls back to CLI-style guidance when imports are unavailable.
    All public methods return a unified dictionary payload with a `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
        }
        if error:
            payload["error"] = error
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _load_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"
            return None

    def _load_modules(self) -> None:
        module_paths = [
            "tsfresh",
            "tsfresh.convenience.bindings",
            "tsfresh.convenience.relevant_extraction",
            "tsfresh.feature_extraction.extraction",
            "tsfresh.feature_extraction.settings",
            "tsfresh.feature_selection.relevance",
            "tsfresh.feature_selection.selection",
            "tsfresh.feature_selection.significance_tests",
            "tsfresh.transformers.feature_augmenter",
            "tsfresh.transformers.feature_selector",
            "tsfresh.transformers.per_column_imputer",
            "tsfresh.transformers.relevant_feature_augmenter",
            "tsfresh.utilities.dataframe_functions",
            "tsfresh.utilities.distribution",
            "tsfresh.utilities.string_manipulation",
            "tsfresh.scripts.run_tsfresh",
            "tsfresh.scripts.measure_execution_time",
            "tsfresh.scripts.test_timing",
            "tsfresh.examples.driftbif_simulation",
            "tsfresh.examples.har_dataset",
            "tsfresh.examples.robot_execution_failures",
        ]
        for p in module_paths:
            self._load_module(p)

    def _get_module(self, module_path: str) -> Optional[Any]:
        return self._modules.get(module_path)

    def _resolve_callable(self, module_path: str, attr_name: str) -> Any:
        mod = self._get_module(module_path)
        if mod is None:
            raise ImportError(
                f"Module '{module_path}' is not available. "
                f"Import error: {self._import_errors.get(module_path, 'unknown')}"
            )
        if not hasattr(mod, attr_name):
            raise AttributeError(
                f"'{module_path}' has no attribute '{attr_name}'. "
                "Check library version compatibility."
            )
        return getattr(mod, attr_name)

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter health and import readiness.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        return self._result(
            status="ok" if "tsfresh" in self._modules else "degraded",
            message="Adapter health report generated.",
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "import_feasibility": 0.93,
                "intrusiveness_risk": "low",
                "complexity": "medium",
            },
            guidance=(
                "If core module imports fail, install required dependencies: "
                "numpy, pandas, scipy, statsmodels, scikit-learn, tqdm, requests, "
                "stumpy, cloudpickle, distributed."
            ),
        )

    # -------------------------------------------------------------------------
    # Core tsfresh API wrappers
    # -------------------------------------------------------------------------
    def call_extract_features(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Call tsfresh.feature_extraction.extraction.extract_features.

        Parameters:
            *args, **kwargs: Forwarded directly to extract_features.
                Common parameters include:
                - timeseries_container
                - default_fc_parameters
                - kind_to_fc_parameters
                - column_id / column_sort / column_kind / column_value
                - n_jobs, chunksize, disable_progressbar, etc.

        Returns:
            dict: status + extracted feature DataFrame in data['result'].
        """
        try:
            fn = self._resolve_callable(
                "tsfresh.feature_extraction.extraction", "extract_features"
            )
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message="extract_features executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to execute extract_features.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Verify input dataframe schema and required columns.",
            )

    def call_select_features(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Call tsfresh.feature_selection.selection.select_features.

        Parameters:
            *args, **kwargs: Forwarded to select_features.

        Returns:
            dict: status + selected feature DataFrame.
        """
        try:
            fn = self._resolve_callable("tsfresh.feature_selection.selection", "select_features")
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message="select_features executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to execute select_features.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Ensure target vector aligns with feature matrix indices.",
            )

    def call_extract_relevant_features(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Call tsfresh.convenience.relevant_extraction.extract_relevant_features.

        Parameters:
            *args, **kwargs: Forwarded to extract_relevant_features.

        Returns:
            dict: status + relevant extracted features.
        """
        try:
            fn = self._resolve_callable(
                "tsfresh.convenience.relevant_extraction", "extract_relevant_features"
            )
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message="extract_relevant_features executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to execute extract_relevant_features.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check timeseries and target inputs for consistency.",
            )

    # -------------------------------------------------------------------------
    # Settings / parameter classes
    # -------------------------------------------------------------------------
    def instance_minimal_fc_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Create instance of MinimalFCParameters.

        Parameters:
            **kwargs: Optional constructor keyword arguments.

        Returns:
            dict: status + class instance in data['instance'].
        """
        try:
            cls = self._resolve_callable("tsfresh.feature_extraction.settings", "MinimalFCParameters")
            obj = cls(**kwargs)
            return self._result(
                status="ok",
                message="MinimalFCParameters instance created.",
                data={"instance": obj},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to instantiate MinimalFCParameters.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Review constructor arguments for current tsfresh version.",
            )

    def instance_comprehensive_fc_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Create instance of ComprehensiveFCParameters.

        Parameters:
            **kwargs: Optional constructor keyword arguments.

        Returns:
            dict: status + class instance.
        """
        try:
            cls = self._resolve_callable("tsfresh.feature_extraction.settings", "ComprehensiveFCParameters")
            obj = cls(**kwargs)
            return self._result(
                status="ok",
                message="ComprehensiveFCParameters instance created.",
                data={"instance": obj},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to instantiate ComprehensiveFCParameters.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Use defaults if custom arguments are rejected.",
            )

    def instance_efficient_fc_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Create instance of EfficientFCParameters.

        Parameters:
            **kwargs: Optional constructor keyword arguments.

        Returns:
            dict: status + class instance.
        """
        try:
            cls = self._resolve_callable("tsfresh.feature_extraction.settings", "EfficientFCParameters")
            obj = cls(**kwargs)
            return self._result(
                status="ok",
                message="EfficientFCParameters instance created.",
                data={"instance": obj},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to instantiate EfficientFCParameters.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Try without custom args for maximum compatibility.",
            )

    # -------------------------------------------------------------------------
    # Transformer classes
    # -------------------------------------------------------------------------
    def instance_feature_augmenter(self, **kwargs) -> Dict[str, Any]:
        try:
            cls = self._resolve_callable("tsfresh.transformers.feature_augmenter", "FeatureAugmenter")
            return self._result("ok", "FeatureAugmenter instance created.", {"instance": cls(**kwargs)})
        except Exception as exc:
            return self._result("error", "Failed to instantiate FeatureAugmenter.", error=f"{type(exc).__name__}: {exc}")

    def instance_feature_selector(self, **kwargs) -> Dict[str, Any]:
        try:
            cls = self._resolve_callable("tsfresh.transformers.feature_selector", "FeatureSelector")
            return self._result("ok", "FeatureSelector instance created.", {"instance": cls(**kwargs)})
        except Exception as exc:
            return self._result("error", "Failed to instantiate FeatureSelector.", error=f"{type(exc).__name__}: {exc}")

    def instance_per_column_imputer(self, **kwargs) -> Dict[str, Any]:
        try:
            cls = self._resolve_callable("tsfresh.transformers.per_column_imputer", "PerColumnImputer")
            return self._result("ok", "PerColumnImputer instance created.", {"instance": cls(**kwargs)})
        except Exception as exc:
            return self._result("error", "Failed to instantiate PerColumnImputer.", error=f"{type(exc).__name__}: {exc}")

    def instance_relevant_feature_augmenter(self, **kwargs) -> Dict[str, Any]:
        try:
            cls = self._resolve_callable(
                "tsfresh.transformers.relevant_feature_augmenter", "RelevantFeatureAugmenter"
            )
            return self._result("ok", "RelevantFeatureAugmenter instance created.", {"instance": cls(**kwargs)})
        except Exception as exc:
            return self._result("error", "Failed to instantiate RelevantFeatureAugmenter.", error=f"{type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # Script / CLI fallback helpers
    # -------------------------------------------------------------------------
    def call_run_tsfresh_cli(self, argv: Optional[list] = None) -> Dict[str, Any]:
        try:
            mod = self._resolve_callable("tsfresh.scripts.run_tsfresh", "main")
            out = mod(argv) if argv is not None else mod()
            return self._result("ok", "run_tsfresh CLI entry executed.", {"result": out})
        except Exception as exc:
            return self._result(
                "error",
                "Failed to execute run_tsfresh CLI entry.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Use module execution: python -m tsfresh.scripts.run_tsfresh --help",
            )

    def call_measure_execution_time_cli(self, argv: Optional[list] = None) -> Dict[str, Any]:
        try:
            mod = self._resolve_callable("tsfresh.scripts.measure_execution_time", "main")
            out = mod(argv) if argv is not None else mod()
            return self._result("ok", "measure_execution_time executed.", {"result": out})
        except Exception as exc:
            return self._result(
                "error",
                "Failed to execute measure_execution_time.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Use module execution: python -m tsfresh.scripts.measure_execution_time",
            )

    def call_test_timing_cli(self, argv: Optional[list] = None) -> Dict[str, Any]:
        try:
            mod = self._resolve_callable("tsfresh.scripts.test_timing", "main")
            out = mod(argv) if argv is not None else mod()
            return self._result("ok", "test_timing executed.", {"result": out})
        except Exception as exc:
            return self._result(
                "error",
                "Failed to execute test_timing.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Use module execution: python -m tsfresh.scripts.test_timing",
            )

    # -------------------------------------------------------------------------
    # Generic execution interface
    # -------------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Generic function caller for any imported module function.

        Parameters:
            module_path: Full module path (without 'source.' prefix), e.g. 'tsfresh.feature_extraction.extraction'
            function_name: Callable name in that module.
            *args, **kwargs: Forwarded function arguments.

        Returns:
            dict: status + function return value.
        """
        try:
            fn = self._resolve_callable(module_path, function_name)
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"{module_path}.{function_name} executed successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to execute {module_path}.{function_name}.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Confirm function name and argument compatibility with current source version.",
            )

    def create_instance(self, module_path: str, class_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Generic class instantiator for imported modules.

        Parameters:
            module_path: Full module path (without 'source.' prefix).
            class_name: Class name in target module.
            *args, **kwargs: Constructor arguments.

        Returns:
            dict: status + instance object.
        """
        try:
            cls = self._resolve_callable(module_path, class_name)
            instance = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"{module_path}.{class_name} instantiated successfully.",
                data={"instance": instance},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to instantiate {module_path}.{class_name}.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Verify constructor parameters and dependency availability.",
            )