import os
import sys
import inspect
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the causalml source package.

    Design goals:
    - Prefer direct imports from local source tree.
    - Gracefully degrade to fallback mode when imports fail.
    - Expose practical constructors/callers for major modules.
    - Return a unified dictionary response schema with `status`.
    """

    # =========================
    # Lifecycle and state
    # =========================
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Any = None, message: str = "success", **extra: Any) -> Dict[str, Any]:
        out = {"status": "ok", "mode": self.mode, "message": message, "data": data}
        out.update(extra)
        return out

    def _error(self, message: str, actionable: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message}
        if actionable:
            out["actionable"] = actionable
        out.update(extra)
        return out

    def _fallback(self, message: str, actionable: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
        out = {"status": "fallback", "mode": self.mode, "message": message}
        if actionable:
            out["actionable"] = actionable
        out.update(extra)
        return out

    def _load_modules(self) -> None:
        module_names = [
            "causalml",
            "causalml.dataset",
            "causalml.dataset.classification",
            "causalml.dataset.regression",
            "causalml.dataset.semiSynthetic",
            "causalml.dataset.synthetic",
            "causalml.feature_selection.filters",
            "causalml.features",
            "causalml.inference.iv.drivlearner",
            "causalml.inference.iv.iv_regression",
            "causalml.inference.meta.base",
            "causalml.inference.meta.drlearner",
            "causalml.inference.meta.explainer",
            "causalml.inference.meta.rlearner",
            "causalml.inference.meta.slearner",
            "causalml.inference.meta.tlearner",
            "causalml.inference.meta.tmle",
            "causalml.inference.meta.utils",
            "causalml.inference.meta.xlearner",
            "causalml.inference.tf.dragonnet",
            "causalml.inference.tf.utils",
            "causalml.inference.torch.cevae",
            "causalml.inference.tree._tree._classes",
            "causalml.inference.tree.causal._tree",
            "causalml.inference.tree.causal.causalforest",
            "causalml.inference.tree.causal.causaltree",
            "causalml.inference.tree.plot",
            "causalml.inference.tree.utils",
            "causalml.match",
            "causalml.metrics.classification",
            "causalml.metrics.regression",
            "causalml.metrics.sensitivity",
            "causalml.metrics.visualize",
            "causalml.optimize.pns",
            "causalml.optimize.policylearner",
            "causalml.optimize.unit_selection",
            "causalml.optimize.utils",
            "causalml.optimize.value_optimization",
            "causalml.propensity",
        ]
        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors[name] = str(e)

        if self._import_errors:
            self.mode = "fallback"

    # =========================
    # Introspection utilities
    # =========================
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._ok(
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "failed_modules": self._import_errors,
                "import_success_count": len(self._modules),
                "import_failure_count": len(self._import_errors),
            },
            message="adapter initialized",
        )

    def list_module_members(self, module_path: str, public_only: bool = True) -> Dict[str, Any]:
        """
        List members for a loaded module.

        Parameters:
        - module_path: Full module path (e.g., causalml.inference.meta.slearner)
        - public_only: Hide private members prefixed with underscore when True
        """
        mod = self._modules.get(module_path)
        if mod is None:
            return self._error(
                f"Module not loaded: {module_path}",
                actionable="Check get_status() and install missing dependencies.",
                failed_modules=self._import_errors,
            )
        members = []
        for name, obj in inspect.getmembers(mod):
            if public_only and name.startswith("_"):
                continue
            kind = "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else "other"
            members.append({"name": name, "kind": kind})
        return self._ok(data=members, message=f"members listed for {module_path}")

    # =========================
    # Generic class/function bridge
    # =========================
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from the specified module.
        """
        mod = self._modules.get(module_path)
        if mod is None:
            return self._fallback(
                f"Cannot create instance because module is unavailable: {module_path}",
                actionable="Install required optional dependencies and retry.",
                failed_modules=self._import_errors,
            )
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                data={"module": module_path, "class": class_name, "instance": instance},
                message="instance created",
            )
        except AttributeError:
            return self._error(
                f"Class not found: {class_name} in {module_path}",
                actionable="Call list_module_members(module_path) to discover valid classes.",
            )
        except Exception as e:
            return self._error(
                f"Failed to instantiate {class_name}: {e}",
                actionable="Verify constructor arguments and dependency versions.",
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from the specified module.
        """
        mod = self._modules.get(module_path)
        if mod is None:
            return self._fallback(
                f"Cannot call function because module is unavailable: {module_path}",
                actionable="Install required optional dependencies and retry.",
                failed_modules=self._import_errors,
            )
        try:
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok(
                data={"module": module_path, "function": function_name, "result": result},
                message="function executed",
            )
        except AttributeError:
            return self._error(
                f"Function not found: {function_name} in {module_path}",
                actionable="Call list_module_members(module_path) to discover valid functions.",
            )
        except Exception as e:
            return self._error(
                f"Failed to execute {function_name}: {e}",
                actionable="Verify function parameters and input types.",
            )

    # =========================
    # Dedicated constructors by functional area
    # =========================
    def new_meta_learner(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a meta-learner class from supported modules:
        drlearner, rlearner, slearner, tlearner, xlearner, tmle.
        """
        candidates = [
            "causalml.inference.meta.drlearner",
            "causalml.inference.meta.rlearner",
            "causalml.inference.meta.slearner",
            "causalml.inference.meta.tlearner",
            "causalml.inference.meta.xlearner",
            "causalml.inference.meta.tmle",
            "causalml.inference.meta.base",
        ]
        for module_path in candidates:
            if module_path in self._modules:
                try:
                    cls = getattr(self._modules[module_path], class_name)
                    return self._ok(
                        data={"instance": cls(*args, **kwargs), "module": module_path, "class": class_name},
                        message="meta learner created",
                    )
                except AttributeError:
                    continue
                except Exception as e:
                    return self._error(
                        f"Failed to instantiate meta learner {class_name}: {e}",
                        actionable="Check constructor arguments for the selected learner.",
                    )
        return self._fallback(
            f"Meta learner class not available: {class_name}",
            actionable="Inspect available classes via list_module_members for meta modules.",
            failed_modules=self._import_errors,
        )

    def new_iv_learner(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate an IV learner class from iv modules.
        """
        for module_path in ["causalml.inference.iv.drivlearner", "causalml.inference.iv.iv_regression"]:
            if module_path in self._modules:
                try:
                    cls = getattr(self._modules[module_path], class_name)
                    return self._ok(
                        data={"instance": cls(*args, **kwargs), "module": module_path, "class": class_name},
                        message="iv learner created",
                    )
                except AttributeError:
                    continue
                except Exception as e:
                    return self._error(
                        f"Failed to instantiate IV learner {class_name}: {e}",
                        actionable="Check IV learner constructor parameters.",
                    )
        return self._fallback(
            f"IV learner class not available: {class_name}",
            actionable="List members in IV modules and ensure optional dependencies are installed.",
            failed_modules=self._import_errors,
        )

    def new_tree_model(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate tree-based uplift/causal model classes from tree modules.
        """
        candidates = [
            "causalml.inference.tree.causal.causalforest",
            "causalml.inference.tree.causal.causaltree",
            "causalml.inference.tree._tree._classes",
            "causalml.inference.tree.causal._tree",
        ]
        for module_path in candidates:
            if module_path in self._modules:
                try:
                    cls = getattr(self._modules[module_path], class_name)
                    return self._ok(
                        data={"instance": cls(*args, **kwargs), "module": module_path, "class": class_name},
                        message="tree model created",
                    )
                except AttributeError:
                    continue
                except Exception as e:
                    return self._error(
                        f"Failed to instantiate tree model {class_name}: {e}",
                        actionable="Validate model hyperparameters and dataset schema.",
                    )
        return self._fallback(
            f"Tree model class not available: {class_name}",
            actionable="Use list_module_members on tree modules to find available classes.",
            failed_modules=self._import_errors,
        )

    def new_policy_model(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate policy/value optimization classes.
        """
        candidates = [
            "causalml.optimize.policylearner",
            "causalml.optimize.unit_selection",
            "causalml.optimize.value_optimization",
            "causalml.optimize.pns",
        ]
        for module_path in candidates:
            if module_path in self._modules:
                try:
                    cls = getattr(self._modules[module_path], class_name)
                    return self._ok(
                        data={"instance": cls(*args, **kwargs), "module": module_path, "class": class_name},
                        message="policy optimization class created",
                    )
                except AttributeError:
                    continue
                except Exception as e:
                    return self._error(
                        f"Failed to instantiate policy class {class_name}: {e}",
                        actionable="Verify optimization inputs and class constructor parameters.",
                    )
        return self._fallback(
            f"Policy optimization class not available: {class_name}",
            actionable="Inspect optimize modules for available classes.",
            failed_modules=self._import_errors,
        )

    # =========================
    # Dedicated function callers by module group
    # =========================
    def call_dataset(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call dataset generation/utility function across dataset modules.
        """
        for module_path in [
            "causalml.dataset",
            "causalml.dataset.classification",
            "causalml.dataset.regression",
            "causalml.dataset.semiSynthetic",
            "causalml.dataset.synthetic",
        ]:
            if module_path in self._modules and hasattr(self._modules[module_path], function_name):
                return self.call_function(module_path, function_name, *args, **kwargs)
        return self._fallback(
            f"Dataset function not found: {function_name}",
            actionable="List members for dataset modules and use a valid function name.",
        )

    def call_metrics(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call metric/evaluation/visualization function across metrics modules.
        """
        for module_path in [
            "causalml.metrics.classification",
            "causalml.metrics.regression",
            "causalml.metrics.sensitivity",
            "causalml.metrics.visualize",
        ]:
            if module_path in self._modules and hasattr(self._modules[module_path], function_name):
                return self.call_function(module_path, function_name, *args, **kwargs)
        return self._fallback(
            f"Metrics function not found: {function_name}",
            actionable="List metric module members and choose a valid function.",
        )

    def call_optimize(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call optimization helper function across optimize modules.
        """
        for module_path in [
            "causalml.optimize.utils",
            "causalml.optimize.unit_selection",
            "causalml.optimize.value_optimization",
            "causalml.optimize.pns",
            "causalml.optimize.policylearner",
        ]:
            if module_path in self._modules and hasattr(self._modules[module_path], function_name):
                return self.call_function(module_path, function_name, *args, **kwargs)
        return self._fallback(
            f"Optimization function not found: {function_name}",
            actionable="Inspect optimize modules and call an existing public function.",
        )

    def call_propensity(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call propensity-related function.
        """
        module_path = "causalml.propensity"
        if module_path not in self._modules:
            return self._fallback(
                "Propensity module is unavailable.",
                actionable="Install required dependencies and verify local source integrity.",
                failed_modules=self._import_errors,
            )
        return self.call_function(module_path, function_name, *args, **kwargs)

    def call_match(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call matching-related function.
        """
        module_path = "causalml.match"
        if module_path not in self._modules:
            return self._fallback(
                "Match module is unavailable.",
                actionable="Install required dependencies and verify local source integrity.",
                failed_modules=self._import_errors,
            )
        return self.call_function(module_path, function_name, *args, **kwargs)