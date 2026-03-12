import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Callable

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for uber/causalml.

    This adapter prefers direct imports from repository source code under `source/`.
    If imports fail, it gracefully degrades into fallback mode while returning
    actionable English error messages.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode, "message": message}
        if data:
            out.update(data)
        return out

    def _err(self, message: str, suggestion: Optional[str] = None, exc: Optional[Exception] = None) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message}
        if suggestion:
            out["suggestion"] = suggestion
        if exc is not None:
            out["error_type"] = type(exc).__name__
            out["details"] = str(exc)
        return out

    def _fallback(self, feature: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": "fallback",
            "message": f"Feature '{feature}' is unavailable because required module import failed.",
            "suggestion": "Verify repository source is present in ./source and install dependencies: numpy pandas scipy scikit-learn statsmodels matplotlib.",
        }

    def _safe_call(self, fn: Callable, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as exc:
            return self._err(
                "Execution failed.",
                "Check input shapes/types and ensure optional dependencies are installed for this feature.",
                exc,
            )

    def _import_module(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as exc:
            self._errors[module_path] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        module_list = [
            "causalml.dataset",
            "causalml.features",
            "causalml.feature_selection.filters",
            "causalml.inference.meta.base",
            "causalml.inference.meta.drlearner",
            "causalml.inference.meta.rlearner",
            "causalml.inference.meta.slearner",
            "causalml.inference.meta.tlearner",
            "causalml.inference.meta.tmle",
            "causalml.inference.meta.xlearner",
            "causalml.inference.meta.explainer",
            "causalml.inference.iv.drivlearner",
            "causalml.inference.iv.iv_regression",
            "causalml.inference.tree.causal.causalforest",
            "causalml.inference.tree.causal.causaltree",
            "causalml.inference.tree.plot",
            "causalml.inference.tree.utils",
            "causalml.inference.tf.dragonnet",
            "causalml.inference.tf.utils",
            "causalml.inference.torch.cevae",
            "causalml.match",
            "causalml.metrics.classification",
            "causalml.metrics.regression",
            "causalml.metrics.sensitivity",
            "causalml.metrics.visualize",
            "causalml.optimize.pns",
            "causalml.optimize.policylearner",
            "causalml.optimize.unit_selection",
            "causalml.optimize.value_optimization",
            "causalml.optimize.utils",
            "causalml.propensity",
        ]
        for mp in module_list:
            self._import_module(mp)
        if not self._modules:
            self.mode = "fallback"

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload containing loaded and failed modules.
        """
        return self._ok(
            {
                "loaded_modules": sorted(list(self._modules.keys())),
                "failed_modules": self._errors,
                "import_success_ratio": 0.0
                if (len(self._modules) + len(self._errors)) == 0
                else len(self._modules) / (len(self._modules) + len(self._errors)),
            },
            "Adapter initialized.",
        )

    # -------------------------------------------------------------------------
    # Generic class/function gateways (comprehensive and maintainable)
    # -------------------------------------------------------------------------
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a fully-qualified module path.

        Parameters:
            module_path (str): Full module path, e.g. 'causalml.inference.meta.xlearner'.
            class_name (str): Class name inside module.
            *args: Positional args for class constructor.
            **kwargs: Keyword args for class constructor.

        Returns:
            dict: status/result or actionable error details.
        """
        mod = self._modules.get(module_path)
        if mod is None:
            return self._fallback(f"{module_path}.{class_name}")
        try:
            cls = getattr(mod, class_name)
            obj = cls(*args, **kwargs)
            return self._ok({"instance": obj}, f"Instantiated {module_path}.{class_name}.")
        except Exception as exc:
            return self._err(
                f"Could not instantiate {module_path}.{class_name}.",
                "Confirm class name and constructor parameters.",
                exc,
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a module-level function from a fully-qualified module path.

        Parameters:
            module_path (str): Full module path, e.g. 'causalml.metrics.regression'.
            function_name (str): Function name inside module.
            *args: Positional args for the function.
            **kwargs: Keyword args for the function.

        Returns:
            dict: status/result or actionable error details.
        """
        mod = self._modules.get(module_path)
        if mod is None:
            return self._fallback(f"{module_path}.{function_name}")
        try:
            fn = getattr(mod, function_name)
            return self._safe_call(fn, *args, **kwargs)
        except Exception as exc:
            return self._err(
                f"Could not resolve {module_path}.{function_name}.",
                "Check function name in the repository version being used.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Dedicated high-value wrappers from analysis (classes)
    # -------------------------------------------------------------------------
    def create_base_s_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.meta.slearner", "BaseSLearner", *args, **kwargs)

    def create_base_t_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.meta.tlearner", "BaseTLearner", *args, **kwargs)

    def create_base_x_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.meta.xlearner", "BaseXLearner", *args, **kwargs)

    def create_base_r_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.meta.rlearner", "BaseRLearner", *args, **kwargs)

    def create_base_dr_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.meta.drlearner", "BaseDRLearner", *args, **kwargs)

    def create_causal_tree_regressor(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.tree.causal.causaltree", "CausalTreeRegressor", *args, **kwargs)

    def create_causal_random_forest_regressor(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.inference.tree.causal.causalforest", "CausalRandomForestRegressor", *args, **kwargs)

    def create_policy_learner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("causalml.optimize.policylearner", "PolicyLearner", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dedicated high-value wrappers from analysis (functions)
    # -------------------------------------------------------------------------
    def estimate_propensity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("causalml.propensity", "compute_propensity_score", *args, **kwargs)

    def match(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("causalml.match", "match", *args, **kwargs)

    def pns(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("causalml.optimize.pns", "get_pns_bounds", *args, **kwargs)

    def value_optimization(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("causalml.optimize.value_optimization", "get_treatment_costs", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Optional dependency checks (tensorflow/torch/xgboost/lightgbm/shap)
    # -------------------------------------------------------------------------
    def check_optional_dependencies(self) -> Dict[str, Any]:
        """
        Check availability of optional dependencies used by advanced modules.
        """
        optional = ["xgboost", "lightgbm", "shap", "tensorflow", "torch", "pydotplus", "seaborn"]
        availability = {}
        for pkg in optional:
            try:
                importlib.import_module(pkg)
                availability[pkg] = True
            except Exception:
                availability[pkg] = False
        return self._ok({"optional_dependencies": availability})