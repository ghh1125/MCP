import os
import sys
import traceback
import inspect
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the Analyze-stroke repository.

    This adapter provides:
    - Safe dynamic imports for repository modules/classes/functions
    - Per-class instance management
    - Per-function call wrappers
    - Graceful fallback guidance if imports fail
    - Unified dictionary response format with `status`
    """

    # -------------------------------------------------------------------------
    # Initialization and module loading
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_errors: List[str] = []
        self._modules: Dict[str, Any] = {}
        self._instances: Dict[str, Any] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, guidance: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "message": message}
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        try:
            import causal_module
            import data_loader
            import dim_reduction
            import feature_selection
            import main
            import models
            import plot_utils
            import run_all_causal
            import run_all_causal_wo_draw
            import test_env

            self._modules = {
                "causal_module": causal_module,
                "data_loader": data_loader,
                "dim_reduction": dim_reduction,
                "feature_selection": feature_selection,
                "main": main,
                "models": models,
                "plot_utils": plot_utils,
                "run_all_causal": run_all_causal,
                "run_all_causal_wo_draw": run_all_causal_wo_draw,
                "test_env": test_env,
            }
            self._loaded = True
        except Exception as exc:
            self._loaded = False
            self._import_errors.append(str(exc))
            self._import_errors.append(traceback.format_exc())

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and imported module status.

        Returns:
            dict: Unified status payload with import diagnostics.
        """
        if self._loaded:
            return self._ok(
                {
                    "mode": self.mode,
                    "loaded_modules": sorted(self._modules.keys()),
                    "import_errors": self._import_errors,
                },
                message="Adapter is ready in import mode.",
            )
        return self._error(
            "Adapter failed to import one or more repository modules.",
            guidance=(
                "Verify that repository source files exist under the expected source path and "
                "all dependencies are installed. You can run 'python test_env.py' in the source directory."
            ),
            details="\n".join(self._import_errors[-2:]) if self._import_errors else None,
        )

    # -------------------------------------------------------------------------
    # Generic helpers
    # -------------------------------------------------------------------------
    def _ensure_loaded(self) -> Optional[Dict[str, Any]]:
        if not self._loaded:
            return self._error(
                "Repository modules are not loaded.",
                guidance=(
                    "Check source path injection and install required dependencies "
                    "(numpy, pandas, scikit-learn, matplotlib, seaborn, and causal-related libraries)."
                ),
                details="\n".join(self._import_errors[-2:]) if self._import_errors else None,
            )
        return None

    def _create_instance(self, module_key: str, class_name: str, instance_key: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        err = self._ensure_loaded()
        if err:
            return err
        try:
            module = self._modules[module_key]
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            self._instances[instance_key] = instance
            return self._ok(
                {
                    "instance_key": instance_key,
                    "class_name": class_name,
                    "module": module_key,
                },
                message=f"{class_name} instance created.",
            )
        except Exception as exc:
            return self._error(
                f"Failed to create instance for {class_name}.",
                guidance="Check constructor arguments and repository dependency availability.",
                details=str(exc),
            )

    def _call_function(self, module_key: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        err = self._ensure_loaded()
        if err:
            return err
        try:
            func = getattr(self._modules[module_key], func_name)
            result = func(*args, **kwargs)
            return self._ok(
                {
                    "module": module_key,
                    "function": func_name,
                    "result": result,
                },
                message=f"{func_name} executed.",
            )
        except Exception as exc:
            return self._error(
                f"Failed to execute function {func_name}.",
                guidance="Validate function arguments against repository expectations.",
                details=str(exc),
            )

    def _call_instance_method(self, instance_key: str, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        err = self._ensure_loaded()
        if err:
            return err
        if instance_key not in self._instances:
            return self._error(
                f"Instance '{instance_key}' is not initialized.",
                guidance="Create the instance first using the corresponding create_* method.",
            )
        try:
            instance = self._instances[instance_key]
            method = getattr(instance, method_name)
            result = method(*args, **kwargs)
            return self._ok(
                {
                    "instance_key": instance_key,
                    "method": method_name,
                    "result": result,
                },
                message=f"Method {method_name} executed.",
            )
        except Exception as exc:
            return self._error(
                f"Failed to execute method {method_name} on instance {instance_key}.",
                guidance="Check method name and arguments. Use inspect_instance_methods for discovery.",
                details=str(exc),
            )

    # -------------------------------------------------------------------------
    # Class instance creators (from analysis classes)
    # -------------------------------------------------------------------------
    def create_dimension_analyzer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a DimensionAnalyzer instance.

        Parameters:
            *args: Positional constructor arguments for dim_reduction.DimensionAnalyzer.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("dim_reduction", "DimensionAnalyzer", "dimension_analyzer", *args, **kwargs)

    def create_feature_selection_analyzer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a FeatureSelectionAnalyzer instance.

        Parameters:
            *args: Positional constructor arguments for feature_selection.FeatureSelectionAnalyzer.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("feature_selection", "FeatureSelectionAnalyzer", "feature_selection_analyzer", *args, **kwargs)

    def create_model_manager(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a ModelManager instance.

        Parameters:
            *args: Positional constructor arguments for models.ModelManager.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("models", "ModelManager", "model_manager", *args, **kwargs)

    def create_data_loader(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a DataLoader instance.

        Parameters:
            *args: Positional constructor arguments for data_loader.DataLoader.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("data_loader", "DataLoader", "data_loader", *args, **kwargs)

    def create_causal_analyzer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a CausalAnalyzer instance.

        Parameters:
            *args: Positional constructor arguments for causal_module.CausalAnalyzer.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("causal_module", "CausalAnalyzer", "causal_analyzer", *args, **kwargs)

    def create_dual_logger(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create and store a DualLogger instance.

        Parameters:
            *args: Positional constructor arguments for main.DualLogger.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Status payload with instance metadata.
        """
        return self._create_instance("main", "DualLogger", "dual_logger", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Identified top-level function wrappers
    # -------------------------------------------------------------------------
    def call_check_environment(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call test_env.check_environment.

        Parameters:
            *args: Positional arguments for check_environment.
            **kwargs: Keyword arguments for check_environment.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("test_env", "check_environment", *args, **kwargs)

    def call_add_offset_labels(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call plot_utils.add_offset_labels.

        Parameters:
            *args: Positional arguments for add_offset_labels.
            **kwargs: Keyword arguments for add_offset_labels.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("plot_utils", "add_offset_labels", *args, **kwargs)

    def call_draw_effect_chart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call plot_utils.draw_effect_chart.

        Parameters:
            *args: Positional arguments for draw_effect_chart.
            **kwargs: Keyword arguments for draw_effect_chart.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("plot_utils", "draw_effect_chart", *args, **kwargs)

    def call_draw_pvalue_chart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call plot_utils.draw_pvalue_chart.

        Parameters:
            *args: Positional arguments for draw_pvalue_chart.
            **kwargs: Keyword arguments for draw_pvalue_chart.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("plot_utils", "draw_pvalue_chart", *args, **kwargs)

    def call_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call main.main as the primary pipeline entry.

        Parameters:
            *args: Positional arguments for main.main.
            **kwargs: Keyword arguments for main.main.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("main", "main", *args, **kwargs)

    def call_parse_log_output(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call run_all_causal.parse_log_output.

        Parameters:
            *args: Positional arguments for parse_log_output.
            **kwargs: Keyword arguments for parse_log_output.

        Returns:
            dict: Execution status and function result.
        """
        return self._call_function("run_all_causal", "parse_log_output", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Generic instance interaction utilities
    # -------------------------------------------------------------------------
    def call_dimension_analyzer_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("dimension_analyzer", method_name, *args, **kwargs)

    def call_feature_selection_analyzer_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("feature_selection_analyzer", method_name, *args, **kwargs)

    def call_model_manager_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("model_manager", method_name, *args, **kwargs)

    def call_data_loader_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("data_loader", method_name, *args, **kwargs)

    def call_causal_analyzer_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("causal_analyzer", method_name, *args, **kwargs)

    def call_dual_logger_method(self, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_instance_method("dual_logger", method_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Introspection and fallback guidance
    # -------------------------------------------------------------------------
    def inspect_instance_methods(self, instance_key: str) -> Dict[str, Any]:
        """
        List callable public methods for a stored instance.

        Parameters:
            instance_key (str): Stored instance identifier.

        Returns:
            dict: Status payload with method list.
        """
        err = self._ensure_loaded()
        if err:
            return err
        if instance_key not in self._instances:
            return self._error(
                f"Instance '{instance_key}' does not exist.",
                guidance="Create an instance first, then inspect methods.",
            )
        try:
            obj = self._instances[instance_key]
            methods = []
            for name, member in inspect.getmembers(obj, predicate=callable):
                if not name.startswith("_"):
                    methods.append(name)
            return self._ok({"instance_key": instance_key, "methods": methods}, message="Methods inspected.")
        except Exception as exc:
            return self._error(
                "Failed to inspect instance methods.",
                guidance="Check that the instance is valid and fully initialized.",
                details=str(exc),
            )

    def cli_fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable CLI fallback commands when import mode is not available.

        Returns:
            dict: Status payload with fallback command suggestions.
        """
        commands = [
            "python test_env.py",
            "python main.py",
            "python run_all_causal.py",
            "python run_all_causal_wo_draw.py",
        ]
        return self._ok(
            {
                "fallback_mode": "cli",
                "commands": commands,
                "note": "Run commands from the repository source directory.",
            },
            message="CLI fallback guidance generated.",
        )