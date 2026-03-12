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
    Import-mode MCP adapter for the auto-sklearn repository.

    This adapter uses direct imports from the local source tree and exposes
    high-value, stable library entry points discovered from repository analysis.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        result = {"status": "ok", "mode": self.mode, "message": message}
        if data:
            result.update(data)
        return result

    def _error(self, message: str, guidance: str, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message, "guidance": guidance}
        if details:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        module_names = [
            "autosklearn",
            "autosklearn.classification",
            "autosklearn.regression",
            "autosklearn.estimators",
            "autosklearn.metrics",
            "autosklearn.automl",
            "autosklearn.util.dependencies",
            "autosklearn.util.logging_",
            "autosklearn.util.data",
            "autosklearn.evaluation",
            "autosklearn.pipeline.classification",
            "autosklearn.pipeline.regression",
            "autosklearn.experimental.askl2",
            "autosklearn.experimental.selector",
        ]
        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors[name] = f"{type(e).__name__}: {e}"

    def _get_module(self, module_name: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        mod = self._modules.get(module_name)
        if mod is None:
            err = self._import_errors.get(module_name, "Unknown import failure")
            return None, self._error(
                message=f"Module import failed: {module_name}",
                guidance=(
                    "Ensure all required dependencies are installed and the local source directory exists "
                    "at the configured path. Verify Python version compatibility for auto-sklearn."
                ),
                details=err,
            )
        return mod, None

    def _instantiate_class(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module(module_name)
        if err:
            return err
        try:
            cls = getattr(mod, class_name)
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj, "class": class_name, "module": module_name}, f"{class_name} instantiated")
        except Exception as e:
            return self._error(
                message=f"Failed to instantiate class {class_name}",
                guidance="Check constructor parameters and dependency availability.",
                details=f"{type(e).__name__}: {e}",
            )

    def _call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module(module_name)
        if err:
            return err
        try:
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result, "function": function_name, "module": module_name}, f"{function_name} executed")
        except Exception as e:
            return self._error(
                message=f"Failed to execute function {function_name}",
                guidance="Validate arguments and confirm the function exists in the current auto-sklearn version.",
                details=f"{type(e).__name__}: {e}",
            )

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Perform an adapter health check.

        Returns:
            dict: Unified status payload including imported modules and import failures.
        """
        if self._import_errors:
            return self._error(
                message="Adapter initialized with partial import failures.",
                guidance="Install missing dependencies and re-run initialization for full functionality.",
                details=str(self._import_errors),
            )
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_failures": self._import_errors,
            },
            "All configured modules imported successfully.",
        )

    def get_repository_summary(self) -> Dict[str, Any]:
        """
        Return repository-level summary inferred from analysis metadata.

        Returns:
            dict: Summary including dependency posture and import strategy.
        """
        return self._ok(
            {
                "repository": "https://github.com/automl/auto-sklearn",
                "import_strategy": "import",
                "complexity": "complex",
                "intrusiveness_risk": "medium",
                "notes": "Library-first repository; no stable packaged CLI entrypoint identified.",
            }
        )

    # -------------------------------------------------------------------------
    # Class factory methods (high-value entry points)
    # -------------------------------------------------------------------------
    def create_autosklearn_classifier(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create autosklearn.estimators.AutoSklearnClassifier.

        Parameters:
            *args: Positional constructor args passed to AutoSklearnClassifier.
            **kwargs: Keyword constructor args, e.g. time_left_for_this_task, per_run_time_limit.

        Returns:
            dict: Unified status with instantiated object.
        """
        return self._instantiate_class("autosklearn.estimators", "AutoSklearnClassifier", *args, **kwargs)

    def create_autosklearn_regressor(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create autosklearn.estimators.AutoSklearnRegressor.

        Parameters:
            *args: Positional constructor args.
            **kwargs: Keyword constructor args for AutoSklearnRegressor.

        Returns:
            dict: Unified status with instantiated object.
        """
        return self._instantiate_class("autosklearn.estimators", "AutoSklearnRegressor", *args, **kwargs)

    def create_automl(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create autosklearn.automl.AutoML object.

        Parameters:
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status with instantiated object.
        """
        return self._instantiate_class("autosklearn.automl", "AutoML", *args, **kwargs)

    def create_askl2_classifier(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create autosklearn.experimental.askl2.AutoSklearn2Classifier object.

        Parameters:
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status with instantiated object.
        """
        return self._instantiate_class("autosklearn.experimental.askl2", "AutoSklearn2Classifier", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function call methods (selected stable utilities)
    # -------------------------------------------------------------------------
    def call_show_versions(self) -> Dict[str, Any]:
        """
        Call autosklearn.util.dependencies.show_versions().

        Returns:
            dict: Unified status with environment/dependency version report.
        """
        return self._call_function("autosklearn.util.dependencies", "show_versions")

    def call_get_logger(self, name: str) -> Dict[str, Any]:
        """
        Call autosklearn.util.logging_.get_logger(name).

        Parameters:
            name (str): Logger name.

        Returns:
            dict: Unified status with logger instance.
        """
        return self._call_function("autosklearn.util.logging_", "get_logger", name)

    # -------------------------------------------------------------------------
    # Generic invocation API for extensibility
    # -------------------------------------------------------------------------
    def call_module_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from an already-imported module.

        Parameters:
            module_name (str): Fully qualified module path, e.g. autosklearn.metrics.
            function_name (str): Function attribute to call.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            dict: Unified status with function output.
        """
        return self._call_function(module_name, function_name, *args, **kwargs)

    def create_module_class_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class from an already-imported module.

        Parameters:
            module_name (str): Fully qualified module path.
            class_name (str): Class attribute to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status with created object.
        """
        return self._instantiate_class(module_name, class_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Fallback-safe guidance
    # -------------------------------------------------------------------------
    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when import mode is partially unavailable.

        Returns:
            dict: Unified status with guidance steps.
        """
        if not self._import_errors:
            return self._ok({"guidance_steps": []}, "Import mode is fully operational.")
        return self._error(
            message="Import mode is degraded.",
            guidance=(
                "1) Install required dependencies (numpy, scipy, scikit-learn, pandas, ConfigSpace, smac, dask, distributed). "
                "2) Ensure local repository source is present under the expected 'source' folder. "
                "3) Recreate environment matching auto-sklearn supported Python versions. "
                "4) Re-run adapter initialization."
            ),
            details=str(self._import_errors),
        )