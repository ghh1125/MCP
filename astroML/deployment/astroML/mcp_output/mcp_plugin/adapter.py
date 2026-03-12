import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for astroML repository modules.

    This adapter:
    - Works in `import` mode by default.
    - Attempts direct module imports from source tree.
    - Falls back gracefully with actionable error messages.
    - Exposes generic utilities to instantiate classes and call functions.
    - Provides grouped convenience methods for discovered astroML packages.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repository = "astroML"
        self.packages = [
            "astroML",
            "astroML.classification",
            "astroML.clustering",
            "astroML.datasets",
            "astroML.density_estimation",
            "astroML.dimensionality",
            "astroML.linear_model",
            "astroML.plotting",
            "astroML.stats",
            "astroML.tests",
            "astroML.time_series",
            "astroML.utils",
        ]
        self.required_dependencies = [
            "numpy",
            "scipy",
            "sklearn",
            "matplotlib",
            "astropy",
        ]
        self.optional_dependencies = [
            "pandas",
            "pytest",
        ]
        self._module_cache: Dict[str, Any] = {}

    # -------------------------------------------------------------------------
    # Core response helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success", **extra: Any) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message, "data": data}
        if extra:
            payload.update(extra)
        return payload

    def _err(self, message: str, error: Optional[Exception] = None, **extra: Any) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = f"{type(error).__name__}: {error}"
        if extra:
            payload.update(extra)
        return payload

    # -------------------------------------------------------------------------
    # Environment and capability checks
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness, import feasibility, and dependency presence.

        Returns:
            Dict with status, dependency details, and package import summary.
        """
        dep_status = {}
        for dep in self.required_dependencies + self.optional_dependencies:
            try:
                importlib.import_module(dep)
                dep_status[dep] = True
            except Exception:
                dep_status[dep] = False

        package_results = {}
        for pkg in self.packages:
            result = self._import_module(pkg)
            package_results[pkg] = result["status"] == "success"

        return self._ok(
            data={
                "repository": self.repository,
                "mode": self.mode,
                "source_path": source_path,
                "dependencies": dep_status,
                "packages": package_results,
            },
            message="Health check completed",
        )

    def list_packages(self) -> Dict[str, Any]:
        """
        List discovered package groups from analysis.
        """
        return self._ok(data={"packages": self.packages}, message="Package list retrieved")

    # -------------------------------------------------------------------------
    # Import and introspection utilities
    # -------------------------------------------------------------------------
    def _import_module(self, module_path: str) -> Dict[str, Any]:
        if module_path in self._module_cache:
            return self._ok(data=self._module_cache[module_path], message=f"Module cached: {module_path}")
        try:
            module = importlib.import_module(module_path)
            self._module_cache[module_path] = module
            return self._ok(data=module, message=f"Imported module: {module_path}")
        except Exception as e:
            return self._err(
                message=(
                    f"Failed to import module '{module_path}'. "
                    "Ensure repository source is available under the configured source path "
                    "and required dependencies are installed."
                ),
                error=e,
                module=module_path,
            )

    def inspect_module(self, module_path: str) -> Dict[str, Any]:
        """
        Inspect a module and return discovered classes/functions.

        Args:
            module_path: Full module path (e.g., 'astroML.correlation').

        Returns:
            Dict with status and introspection data.
        """
        imported = self._import_module(module_path)
        if imported["status"] != "success":
            return imported
        module = imported["data"]
        try:
            classes = []
            functions = []
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    classes.append(name)
                elif inspect.isfunction(obj) and obj.__module__ == module.__name__:
                    functions.append(name)
            return self._ok(
                data={
                    "module": module_path,
                    "classes": sorted(classes),
                    "functions": sorted(functions),
                },
                message=f"Inspected module: {module_path}",
            )
        except Exception as e:
            return self._err("Failed to inspect module members.", e, module=module_path)

    def call_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call a function from a target astroML module.

        Args:
            module_path: Full module path.
            function_name: Function name to call.
            *args: Positional arguments passed to function.
            **kwargs: Keyword arguments passed to function.

        Returns:
            Dict with status and function result.
        """
        imported = self._import_module(module_path)
        if imported["status"] != "success":
            return imported
        module = imported["data"]
        if not hasattr(module, function_name):
            return self._err(
                message=(
                    f"Function '{function_name}' not found in '{module_path}'. "
                    "Call inspect_module() first to discover available functions."
                ),
                module=module_path,
                function=function_name,
            )
        try:
            func = getattr(module, function_name)
            if not callable(func):
                return self._err(
                    message=f"Attribute '{function_name}' in '{module_path}' is not callable.",
                    module=module_path,
                    function=function_name,
                )
            result = func(*args, **kwargs)
            return self._ok(
                data=result,
                message=f"Function '{module_path}.{function_name}' executed successfully",
            )
        except Exception as e:
            return self._err(
                message=(
                    f"Function call failed for '{module_path}.{function_name}'. "
                    "Check input argument shapes/types and required dependency versions."
                ),
                error=e,
                module=module_path,
                function=function_name,
            )

    def create_instance(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Instantiate a class from a target astroML module.

        Args:
            module_path: Full module path.
            class_name: Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            Dict with status and created instance.
        """
        imported = self._import_module(module_path)
        if imported["status"] != "success":
            return imported
        module = imported["data"]
        if not hasattr(module, class_name):
            return self._err(
                message=(
                    f"Class '{class_name}' not found in '{module_path}'. "
                    "Call inspect_module() first to discover available classes."
                ),
                module=module_path,
                class_name=class_name,
            )
        try:
            cls = getattr(module, class_name)
            if not inspect.isclass(cls):
                return self._err(
                    message=f"Attribute '{class_name}' in '{module_path}' is not a class.",
                    module=module_path,
                    class_name=class_name,
                )
            instance = cls(*args, **kwargs)
            return self._ok(
                data=instance,
                message=f"Class '{module_path}.{class_name}' instantiated successfully",
            )
        except Exception as e:
            return self._err(
                message=(
                    f"Class instantiation failed for '{module_path}.{class_name}'. "
                    "Review constructor parameters and dependency compatibility."
                ),
                error=e,
                module=module_path,
                class_name=class_name,
            )

    # -------------------------------------------------------------------------
    # Grouped package loaders
    # -------------------------------------------------------------------------
    def load_core(self) -> Dict[str, Any]:
        return self._import_module("astroML")

    def load_classification(self) -> Dict[str, Any]:
        return self._import_module("astroML.classification")

    def load_clustering(self) -> Dict[str, Any]:
        return self._import_module("astroML.clustering")

    def load_datasets(self) -> Dict[str, Any]:
        return self._import_module("astroML.datasets")

    def load_density_estimation(self) -> Dict[str, Any]:
        return self._import_module("astroML.density_estimation")

    def load_dimensionality(self) -> Dict[str, Any]:
        return self._import_module("astroML.dimensionality")

    def load_linear_model(self) -> Dict[str, Any]:
        return self._import_module("astroML.linear_model")

    def load_plotting(self) -> Dict[str, Any]:
        return self._import_module("astroML.plotting")

    def load_stats(self) -> Dict[str, Any]:
        return self._import_module("astroML.stats")

    def load_time_series(self) -> Dict[str, Any]:
        return self._import_module("astroML.time_series")

    def load_utils(self) -> Dict[str, Any]:
        return self._import_module("astroML.utils")

    # -------------------------------------------------------------------------
    # Convenience wrappers for representative module calls
    # -------------------------------------------------------------------------
    def call_from_module(
        self,
        module_path: str,
        function_name: str,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generic dispatcher for function calls.

        Args:
            module_path: Target full module path.
            function_name: Function to invoke.
            args: Optional positional arguments tuple.
            kwargs: Optional keyword argument dict.
        """
        args = args or ()
        kwargs = kwargs or {}
        return self.call_function(module_path, function_name, *args, **kwargs)

    def create_from_module(
        self,
        module_path: str,
        class_name: str,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generic dispatcher for class instantiation.

        Args:
            module_path: Target full module path.
            class_name: Class to instantiate.
            args: Optional positional constructor args.
            kwargs: Optional keyword constructor args.
        """
        args = args or ()
        kwargs = kwargs or {}
        return self.create_instance(module_path, class_name, *args, **kwargs)

    def discover_repository_api(self) -> Dict[str, Any]:
        """
        Inspect all known package groups and return aggregated classes/functions.
        """
        discovered: Dict[str, Dict[str, List[str]]] = {}
        errors: List[Dict[str, Any]] = []
        module_candidates = [
            "astroML",
            "astroML.correlation",
            "astroML.cosmology",
            "astroML.crossmatch",
            "astroML.filters",
            "astroML.fourier",
            "astroML.lumfunc",
            "astroML.resample",
            "astroML.sum_of_norms",
            "astroML.classification.gmm_bayes",
            "astroML.clustering.mst_clustering",
            "astroML.density_estimation.bayesian_blocks",
            "astroML.density_estimation.density_estimation",
            "astroML.density_estimation.empirical",
            "astroML.density_estimation.gauss_mixture",
            "astroML.density_estimation.histtools",
            "astroML.density_estimation.xdeconv",
            "astroML.dimensionality.iterative_pca",
            "astroML.linear_model.TLS",
            "astroML.linear_model.kernel_regression",
            "astroML.linear_model.linear_regression",
            "astroML.linear_model.linear_regression_errors",
            "astroML.plotting.ellipse",
            "astroML.plotting.hist_tools",
            "astroML.plotting.mcmc",
            "astroML.plotting.multiaxes",
            "astroML.plotting.regression",
            "astroML.plotting.scatter_contour",
            "astroML.plotting.settings",
            "astroML.plotting.tools",
            "astroML.stats._binned_statistic",
            "astroML.stats._point_statistics",
            "astroML.stats.random",
            "astroML.time_series.ACF",
            "astroML.time_series.generate",
            "astroML.time_series.periodogram",
            "astroML.utils.decorators",
            "astroML.utils.exceptions",
            "astroML.utils.utils",
        ]
        for module_path in module_candidates:
            info = self.inspect_module(module_path)
            if info["status"] == "success":
                discovered[module_path] = info["data"]
            else:
                errors.append(
                    {
                        "module": module_path,
                        "message": info.get("message"),
                        "error": info.get("error"),
                    }
                )
        return self._ok(
            data={"modules": discovered, "errors": errors},
            message="Repository API discovery completed",
        )