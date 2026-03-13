import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the dalle-mini repository.

    This adapter attempts direct imports from the repository source tree and exposes
    high-level helper methods around discovered runnable modules and core components.
    All methods return a unified dictionary format with a required 'status' field.
    """

    # -------------------------------------------------------------------------
    # Initialization and internal utilities
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_targets()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        res = {
            "status": status,
            "mode": self.mode,
            "message": message,
        }
        if data is not None:
            res["data"] = data
        if error is not None:
            res["error"] = error
        if guidance is not None:
            res["guidance"] = guidance
        return res

    def _safe_import(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_targets(self) -> None:
        targets = {
            "train_script": "deployment.dalle-mini.source.tools.train.train",
            "gradio_app": "deployment.dalle-mini.source.app.gradio.app",
            "gradio_backend": "deployment.dalle-mini.source.app.gradio.backend",
            "streamlit_app": "deployment.dalle-mini.source.app.streamlit.app",
            "streamlit_backend": "deployment.dalle-mini.source.app.streamlit.backend",
            "dalle_init": "source.src.dalle_mini.__init__",
            "dalle_data": "source.src.dalle_mini.data",
            "model_init": "source.src.dalle_mini.model.__init__",
            "model_configuration": "source.src.dalle_mini.model.configuration",
            "model_modeling": "source.src.dalle_mini.model.modeling",
            "model_partitions": "source.src.dalle_mini.model.partitions",
            "model_processor": "source.src.dalle_mini.model.processor",
            "model_text": "source.src.dalle_mini.model.text",
            "model_tokenizer": "source.src.dalle_mini.model.tokenizer",
            "model_utils": "source.src.dalle_mini.model.utils",
            "shampoo_distributed": "deployment.dalle-mini.source.tools.train.scalable_shampoo.distributed_shampoo",
            "shampoo_quantization": "deployment.dalle-mini.source.tools.train.scalable_shampoo.quantization_utils",
            "shampoo_sm3": "deployment.dalle-mini.source.tools.train.scalable_shampoo.sm3",
            "shampoo_sym_matrices": "deployment.dalle-mini.source.tools.train.scalable_shampoo.symmetric_matrices.symmetric_matrices",
        }
        for key, mod in targets.items():
            self._safe_import(key, mod)

    def health_check(self) -> Dict[str, Any]:
        """
        Return import health summary and actionable troubleshooting guidance.
        """
        imported = sorted(self._modules.keys())
        failed = dict(self._import_errors)
        if failed:
            return self._result(
                status="partial",
                message="Some modules failed to import.",
                data={"imported": imported, "failed": failed},
                guidance=(
                    "Install repository dependencies first (jax, flax, transformers, numpy, Pillow, datasets, tokenizers), "
                    "then retry. If app modules fail, install optional gradio/streamlit."
                ),
            )
        return self._result(
            status="ok",
            message="All target modules imported successfully.",
            data={"imported": imported, "failed": failed},
        )

    # -------------------------------------------------------------------------
    # Module instance accessors
    # -------------------------------------------------------------------------

    def instance_train_script(self) -> Dict[str, Any]:
        return self._instance_by_key("train_script")

    def instance_gradio_app(self) -> Dict[str, Any]:
        return self._instance_by_key("gradio_app")

    def instance_gradio_backend(self) -> Dict[str, Any]:
        return self._instance_by_key("gradio_backend")

    def instance_streamlit_app(self) -> Dict[str, Any]:
        return self._instance_by_key("streamlit_app")

    def instance_streamlit_backend(self) -> Dict[str, Any]:
        return self._instance_by_key("streamlit_backend")

    def instance_dalle_init(self) -> Dict[str, Any]:
        return self._instance_by_key("dalle_init")

    def instance_dalle_data(self) -> Dict[str, Any]:
        return self._instance_by_key("dalle_data")

    def instance_model_init(self) -> Dict[str, Any]:
        return self._instance_by_key("model_init")

    def instance_model_configuration(self) -> Dict[str, Any]:
        return self._instance_by_key("model_configuration")

    def instance_model_modeling(self) -> Dict[str, Any]:
        return self._instance_by_key("model_modeling")

    def instance_model_partitions(self) -> Dict[str, Any]:
        return self._instance_by_key("model_partitions")

    def instance_model_processor(self) -> Dict[str, Any]:
        return self._instance_by_key("model_processor")

    def instance_model_text(self) -> Dict[str, Any]:
        return self._instance_by_key("model_text")

    def instance_model_tokenizer(self) -> Dict[str, Any]:
        return self._instance_by_key("model_tokenizer")

    def instance_model_utils(self) -> Dict[str, Any]:
        return self._instance_by_key("model_utils")

    def instance_shampoo_distributed(self) -> Dict[str, Any]:
        return self._instance_by_key("shampoo_distributed")

    def instance_shampoo_quantization(self) -> Dict[str, Any]:
        return self._instance_by_key("shampoo_quantization")

    def instance_shampoo_sm3(self) -> Dict[str, Any]:
        return self._instance_by_key("shampoo_sm3")

    def instance_shampoo_sym_matrices(self) -> Dict[str, Any]:
        return self._instance_by_key("shampoo_sym_matrices")

    def _instance_by_key(self, key: str) -> Dict[str, Any]:
        mod = self._modules.get(key)
        if mod is None:
            err = self._import_errors.get(key, "Module not imported.")
            return self._result(
                status="error",
                message=f"Module instance unavailable: {key}",
                error=err,
                guidance="Run health_check() and resolve dependency/import issues.",
            )
        return self._result(
            status="ok",
            message=f"Module instance retrieved: {key}",
            data={"module": mod.__name__},
        )

    # -------------------------------------------------------------------------
    # Generic function and class invokers
    # -------------------------------------------------------------------------

    def call_function(
        self,
        module_key: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call a function from an imported target module.

        Parameters:
        - module_key: Internal module key from adapter target list.
        - function_name: Name of the callable function inside the module.
        - args/kwargs: Positional and keyword arguments to pass.

        Returns:
        Unified status dictionary containing function output or error details.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                status="error",
                message=f"Module not available: {module_key}",
                error=self._import_errors.get(module_key, "Unknown module key."),
                guidance="Use health_check() to verify import state.",
            )
        try:
            fn = getattr(mod, function_name)
        except AttributeError:
            return self._result(
                status="error",
                message=f"Function not found: {function_name}",
                error=f"{function_name} is not defined in {mod.__name__}",
                guidance="Inspect module attributes via inspect_module().",
            )
        try:
            output = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Function executed: {mod.__name__}.{function_name}",
                data={"result": output},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Function execution failed: {function_name}",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Validate runtime dependencies and function arguments.",
            )

    def create_class_instance(
        self,
        module_key: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Instantiate a class from an imported target module.

        Parameters:
        - module_key: Internal module key from adapter target list.
        - class_name: Class name to instantiate.
        - args/kwargs: Constructor arguments.

        Returns:
        Unified status dictionary with constructed object metadata.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                status="error",
                message=f"Module not available: {module_key}",
                error=self._import_errors.get(module_key, "Unknown module key."),
                guidance="Use health_check() to verify import state.",
            )
        try:
            cls = getattr(mod, class_name)
        except AttributeError:
            return self._result(
                status="error",
                message=f"Class not found: {class_name}",
                error=f"{class_name} is not defined in {mod.__name__}",
                guidance="Inspect module attributes via inspect_module().",
            )
        try:
            obj = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Class instantiated: {mod.__name__}.{class_name}",
                data={"class": class_name, "module": mod.__name__, "object_repr": repr(obj)},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Class instantiation failed: {class_name}",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Verify constructor parameters and required backend packages.",
            )

    def inspect_module(self, module_key: str) -> Dict[str, Any]:
        """
        List public attributes of an imported module to help discover available APIs.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                status="error",
                message=f"Module not available: {module_key}",
                error=self._import_errors.get(module_key, "Unknown module key."),
                guidance="Use health_check() and fix import issues first.",
            )
        try:
            attrs = [a for a in dir(mod) if not a.startswith("_")]
            return self._result(
                status="ok",
                message=f"Module inspection successful: {mod.__name__}",
                data={"module": mod.__name__, "attributes": attrs},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Module inspection failed.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Retry after ensuring module imports are stable.",
            )

    # -------------------------------------------------------------------------
    # Script-style entrypoint wrappers
    # -------------------------------------------------------------------------

    def run_train_script_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_main("train_script", *args, **kwargs)

    def run_gradio_app_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_main("gradio_app", *args, **kwargs)

    def run_streamlit_app_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_main("streamlit_app", *args, **kwargs)

    def _call_main(self, module_key: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                status="error",
                message=f"Entrypoint module unavailable: {module_key}",
                error=self._import_errors.get(module_key, "Import failed."),
                guidance="Install missing dependencies and retry.",
            )
        if not hasattr(mod, "main"):
            return self._result(
                status="fallback",
                message=f"No main() found in {mod.__name__}.",
                guidance=(
                    "This repository module may be script-driven without an exposed main function. "
                    "Use call_function() with discovered functions from inspect_module()."
                ),
            )
        try:
            out = mod.main(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Executed main() in {mod.__name__}",
                data={"result": out},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"main() execution failed in {mod.__name__}",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check runtime environment (JAX/Flax/Transformers) and function arguments.",
            )