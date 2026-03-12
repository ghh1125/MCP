import os
import sys
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the Pyro repository.

    This adapter is designed for library-first usage, with graceful fallback behavior
    when import-time dependencies are unavailable. It exposes practical, high-value
    methods aligned with the repository analysis:
    - Settings and global state utilities
    - Core primitives (sample/param/factor/plate)
    - Inference utilities (SVI/MCMC/Predictive)
    - Distribution and poutine access helpers
    - Diagnostics and health checks

    All public methods return a unified dictionary:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "fallback",
        ...
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _safe_import(self, name: str) -> Optional[Any]:
        try:
            module = importlib.import_module(name)
            self._modules[name] = module
            return module
        except Exception as exc:
            self._modules[name] = None
            self._errors[name] = str(exc)
            return None

    def _load_modules(self) -> None:
        target_modules = [
            "pyro",
            "pyro.settings",
            "pyro.primitives",
            "pyro.infer",
            "pyro.infer.mcmc",
            "pyro.distributions",
            "pyro.optim",
            "pyro.poutine",
            "pyro.ops",
            "pyro.nn",
            "pyro.params",
        ]
        for name in target_modules:
            self._safe_import(name)

        if self._modules.get("pyro") is None:
            self.mode = "fallback"

    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            Dict with current mode, loaded modules, and import errors.
        """
        loaded = {k: v is not None for k, v in self._modules.items()}
        return self._result("success", loaded_modules=loaded, import_errors=self._errors)

    # -------------------------------------------------------------------------
    # Generic invocation utility
    # -------------------------------------------------------------------------
    def call_module_attr(self, module_name: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call an attribute from a module.

        Parameters:
            module_name: Full module path, e.g. 'pyro.infer'
            attr_name: Attribute/function/class name in that module.
            *args/**kwargs: Forwarded call arguments.

        Returns:
            Unified status dict containing call result or actionable error.
        """
        if self.mode != "import":
            return self._result(
                "fallback",
                message="Import mode unavailable. Install required dependencies such as torch, numpy, opt_einsum, and tqdm.",
            )
        try:
            module = self._modules.get(module_name) or self._safe_import(module_name)
            if module is None:
                return self._result(
                    "error",
                    message=f"Failed to import module '{module_name}'. Verify local source path and dependencies.",
                    error=self._errors.get(module_name, "Unknown import error."),
                )
            target = getattr(module, attr_name)
            value = target(*args, **kwargs) if callable(target) else target
            return self._result("success", module=module_name, attribute=attr_name, result=value)
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to call '{module_name}.{attr_name}'. Check argument types and required runtime state.",
                error=str(exc),
            )

    # -------------------------------------------------------------------------
    # Pyro settings and runtime controls
    # -------------------------------------------------------------------------
    def set_rng_seed(self, seed: int) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result("fallback", message="Pyro is not importable. Ensure torch and pyro source are available.")
        try:
            pyro = self._modules["pyro"]
            pyro.set_rng_seed(seed)
            return self._result("success", seed=seed)
        except Exception as exc:
            return self._result("error", message="Unable to set RNG seed.", error=str(exc))

    def clear_param_store(self) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result("fallback", message="Pyro import unavailable; cannot clear parameter store.")
        try:
            pyro = self._modules["pyro"]
            pyro.clear_param_store()
            return self._result("success", message="Parameter store cleared.")
        except Exception as exc:
            return self._result("error", message="Failed to clear parameter store.", error=str(exc))

    def enable_validation(self, is_validate: bool = True) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result("fallback", message="Pyro import unavailable; validation setting cannot be changed.")
        try:
            pyro = self._modules["pyro"]
            pyro.enable_validation(is_validate)
            return self._result("success", validation_enabled=is_validate)
        except Exception as exc:
            return self._result("error", message="Failed to update validation setting.", error=str(exc))

    # -------------------------------------------------------------------------
    # Primitives wrappers
    # -------------------------------------------------------------------------
    def call_sample(self, name: str, fn: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            primitives = self._modules.get("pyro.primitives") or self._safe_import("pyro.primitives")
            if primitives is None:
                return self._result("fallback", message="Cannot import pyro.primitives. Ensure torch is installed.")
            result = primitives.sample(name, fn, *args, **kwargs)
            return self._result("success", result=result)
        except Exception as exc:
            return self._result("error", message="Failed to execute pyro.sample.", error=str(exc))

    def call_param(self, name: str, init_tensor: Any = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            primitives = self._modules.get("pyro.primitives") or self._safe_import("pyro.primitives")
            if primitives is None:
                return self._result("fallback", message="Cannot import pyro.primitives. Check dependencies.")
            result = primitives.param(name, init_tensor, *args, **kwargs)
            return self._result("success", result=result)
        except Exception as exc:
            return self._result("error", message="Failed to execute pyro.param.", error=str(exc))

    # -------------------------------------------------------------------------
    # Inference constructors (class instance methods)
    # -------------------------------------------------------------------------
    def instance_svi(self, model: Any, guide: Any, optim: Any, loss: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            infer = self._modules.get("pyro.infer") or self._safe_import("pyro.infer")
            if infer is None or not hasattr(infer, "SVI"):
                return self._result("fallback", message="SVI is unavailable. Confirm pyro.infer import succeeds.")
            obj = infer.SVI(model=model, guide=guide, optim=optim, loss=loss, **kwargs)
            return self._result("success", instance=obj)
        except Exception as exc:
            return self._result("error", message="Failed to create SVI instance.", error=str(exc))

    def instance_predictive(self, model: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            infer = self._modules.get("pyro.infer") or self._safe_import("pyro.infer")
            if infer is None or not hasattr(infer, "Predictive"):
                return self._result("fallback", message="Predictive is unavailable. Verify pyro.infer import and dependencies.")
            obj = infer.Predictive(model, **kwargs)
            return self._result("success", instance=obj)
        except Exception as exc:
            return self._result("error", message="Failed to create Predictive instance.", error=str(exc))

    def instance_mcmc(self, kernel: Any, num_samples: int, **kwargs: Any) -> Dict[str, Any]:
        try:
            mcmc_mod = self._modules.get("pyro.infer.mcmc") or self._safe_import("pyro.infer.mcmc")
            if mcmc_mod is None or not hasattr(mcmc_mod, "MCMC"):
                return self._result("fallback", message="MCMC unavailable. Ensure pyro.infer.mcmc dependencies are met.")
            obj = mcmc_mod.MCMC(kernel=kernel, num_samples=num_samples, **kwargs)
            return self._result("success", instance=obj)
        except Exception as exc:
            return self._result("error", message="Failed to create MCMC instance.", error=str(exc))

    def instance_nuts(self, model: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            mcmc_mod = self._modules.get("pyro.infer.mcmc") or self._safe_import("pyro.infer.mcmc")
            if mcmc_mod is None or not hasattr(mcmc_mod, "NUTS"):
                return self._result("fallback", message="NUTS unavailable. Check torch installation and Pyro source path.")
            obj = mcmc_mod.NUTS(model, **kwargs)
            return self._result("success", instance=obj)
        except Exception as exc:
            return self._result("error", message="Failed to create NUTS instance.", error=str(exc))