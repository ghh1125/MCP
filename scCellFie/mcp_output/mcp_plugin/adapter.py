import os
import sys
import importlib
import inspect
from typing import Any, Callable, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for scCellFie MCP plugin integration.

    This adapter attempts to import all known repository modules and exposes
    dynamic invokers to call module-level functions and instantiate classes.
    It is designed to be resilient when optional dependencies are missing.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_name = "scCellFie"
        self.base_package = "sccellfie"
        self._modules: Dict[str, Any] = {}
        self._functions: Dict[str, Callable[..., Any]] = {}
        self._classes: Dict[str, type] = {}
        self._import_errors: Dict[str, str] = {}

        self._target_modules = [
            "sccellfie",
            "sccellfie.communication.colocalization_scoring",
            "sccellfie.communication.traditional_scoring",
            "sccellfie.datasets.database",
            "sccellfie.datasets.gene_info",
            "sccellfie.datasets.toy_inputs",
            "sccellfie.expression.aggregation",
            "sccellfie.expression.smoothing",
            "sccellfie.expression.thresholds",
            "sccellfie.external.tensor",
            "sccellfie.external.tf_idf",
            "sccellfie.gene_score",
            "sccellfie.io.load_data",
            "sccellfie.io.save_data",
            "sccellfie.metabolic_task",
            "sccellfie.plotting.communication",
            "sccellfie.plotting.differential_results",
            "sccellfie.plotting.distributions",
            "sccellfie.plotting.plot_utils",
            "sccellfie.plotting.radial_plot",
            "sccellfie.plotting.spatial",
            "sccellfie.preprocessing.adata_utils",
            "sccellfie.preprocessing.database_manipulation",
            "sccellfie.preprocessing.gpr_rules",
            "sccellfie.preprocessing.matrix_utils",
            "sccellfie.preprocessing.prepare_inputs",
            "sccellfie.reaction_activity",
            "sccellfie.reports.summary",
            "sccellfie.sccellfie_pipeline",
            "sccellfie.spatial.assortativity",
            "sccellfie.spatial.hotspots",
            "sccellfie.spatial.knn_network",
            "sccellfie.spatial.neighborhood",
            "sccellfie.stats.differential_analysis",
            "sccellfie.stats.gam_analysis",
            "sccellfie.stats.markers_from_task",
        ]

        self._initialize_imports()

    # ---------------------------------------------------------------------
    # Core status helpers
    # ---------------------------------------------------------------------
    def _ok(self, **data: Any) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode}
        out.update(data)
        return out

    def _fail(self, message: str, **data: Any) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message}
        out.update(data)
        return out

    def _initialize_imports(self) -> None:
        for module_name in self._target_modules:
            try:
                module = importlib.import_module(module_name)
                self._modules[module_name] = module
                self._register_members(module_name, module)
            except Exception as exc:
                self._import_errors[module_name] = (
                    f"Failed to import '{module_name}': {exc}. "
                    "Install missing dependencies and verify Python version compatibility."
                )

    def _register_members(self, module_name: str, module: Any) -> None:
        try:
            for name, obj in inspect.getmembers(module):
                if name.startswith("_"):
                    continue
                if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                    self._functions[f"{module_name}.{name}"] = obj
                elif inspect.isclass(obj) and obj.__module__ == module.__name__:
                    self._classes[f"{module_name}.{name}"] = obj
        except Exception:
            # Best-effort registration; no hard failure
            pass

    # ---------------------------------------------------------------------
    # Discovery / management API
    # ---------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter import health and loaded symbols.

        Returns:
            dict: Unified status payload with loaded modules, functions, classes, and import errors.
        """
        return self._ok(
            repository=self.repo_name,
            loaded_modules=sorted(self._modules.keys()),
            loaded_module_count=len(self._modules),
            function_count=len(self._functions),
            class_count=len(self._classes),
            import_errors=self._import_errors,
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List all target, loaded, and failed modules.

        Returns:
            dict: Unified status payload with module inventory details.
        """
        return self._ok(
            target_modules=self._target_modules,
            loaded_modules=sorted(self._modules.keys()),
            failed_modules=sorted(self._import_errors.keys()),
        )

    def list_functions(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List discovered module-level functions.

        Args:
            module_name: Optional fully qualified module name filter.

        Returns:
            dict: Unified status payload with function list.
        """
        try:
            keys = sorted(self._functions.keys())
            if module_name:
                keys = [k for k in keys if k.startswith(f"{module_name}.")]
            return self._ok(functions=keys, count=len(keys))
        except Exception as exc:
            return self._fail(
                f"Could not list functions: {exc}. Ensure module name is a valid full path."
            )

    def list_classes(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List discovered classes.

        Args:
            module_name: Optional fully qualified module name filter.

        Returns:
            dict: Unified status payload with class list.
        """
        try:
            keys = sorted(self._classes.keys())
            if module_name:
                keys = [k for k in keys if k.startswith(f"{module_name}.")]
            return self._ok(classes=keys, count=len(keys))
        except Exception as exc:
            return self._fail(
                f"Could not list classes: {exc}. Ensure module name is a valid full path."
            )

    # ---------------------------------------------------------------------
    # Dynamic invocation API (full coverage for all discovered symbols)
    # ---------------------------------------------------------------------
    def call_function(self, function_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a discovered function by full path.

        Args:
            function_path: Full function path, e.g. 'sccellfie.gene_score.some_function'.
            *args: Positional arguments for function call.
            **kwargs: Keyword arguments for function call.

        Returns:
            dict: Unified status payload with call result or actionable error.
        """
        if function_path not in self._functions:
            return self._fail(
                f"Function '{function_path}' is not available. "
                "Use list_functions() to inspect callable options."
            )
        try:
            result = self._functions[function_path](*args, **kwargs)
            return self._ok(function=function_path, result=result)
        except Exception as exc:
            return self._fail(
                f"Function call failed for '{function_path}': {exc}. "
                "Check argument types, required dependencies, and input data format."
            )

    def instantiate_class(self, class_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a discovered class by full path.

        Args:
            class_path: Full class path, e.g. 'sccellfie.reports.summary.SomeClass'.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload with instance or actionable error.
        """
        if class_path not in self._classes:
            return self._fail(
                f"Class '{class_path}' is not available. "
                "Use list_classes() to inspect available class constructors."
            )
        try:
            instance = self._classes[class_path](*args, **kwargs)
            return self._ok(class_name=class_path, instance=instance)
        except Exception as exc:
            return self._fail(
                f"Class instantiation failed for '{class_path}': {exc}. "
                "Check constructor parameters and required runtime dependencies."
            )

    # ---------------------------------------------------------------------
    # Module-specific call helpers (organized by functional area)
    # ---------------------------------------------------------------------
    def call_module_function(
        self, module_name: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from a specific module with separate module/function names.

        Args:
            module_name: Fully qualified module path from scCellFie.
            function_name: Function name within the module.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status payload with result or error details.
        """
        function_path = f"{module_name}.{function_name}"
        return self.call_function(function_path, *args, **kwargs)

    def instantiate_module_class(
        self, module_name: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Instantiate a class from a specific module with separate module/class names.

        Args:
            module_name: Fully qualified module path from scCellFie.
            class_name: Class name in module.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        class_path = f"{module_name}.{class_name}"
        return self.instantiate_class(class_path, *args, **kwargs)

    # ---------------------------------------------------------------------
    # Graceful fallback utilities
    # ---------------------------------------------------------------------
    def fallback_help(self) -> Dict[str, Any]:
        """
        Provide guidance when import mode is partially unavailable.

        Returns:
            dict: Unified status payload containing dependency and remediation guidance.
        """
        guidance = [
            "Install required dependencies: numpy, pandas, scipy, anndata, scanpy, networkx, matplotlib, seaborn, statsmodels.",
            "Install optional dependencies for extended features: squidpy, scikit-learn, umap-learn, plotly.",
            "Verify source path points to the repository 'source' directory.",
            "Check Python version compatibility with package requirements.",
        ]
        return self._ok(
            message="Import mode guidance",
            failed_imports=self._import_errors,
            guidance=guidance,
        )