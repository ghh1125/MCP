import os
import sys
import runpy
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the borisdayma/dalle-mini repository.

    This adapter focuses on:
    - Safe imports from repository modules
    - Lazy loading with graceful fallback
    - Exposing practical methods for known entry points and core modules
    - Unified response format for all method calls
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._module_map = {
            "dalle_init": "dalle_mini.__init__",
            "data": "dalle_mini.data",
            "model_init": "dalle_mini.model.__init__",
            "configuration": "dalle_mini.model.configuration",
            "modeling": "dalle_mini.model.modeling",
            "partitions": "dalle_mini.model.partitions",
            "processor": "dalle_mini.model.processor",
            "text": "dalle_mini.model.text",
            "tokenizer": "dalle_mini.model.tokenizer",
            "utils": "dalle_mini.model.utils",
            "gradio_app": "app.gradio.app",
            "gradio_backend": "app.gradio.backend",
            "streamlit_app": "app.streamlit.app",
            "streamlit_backend": "app.streamlit.backend",
            "train_script_module_style": "tools.train.train",
        }

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, **data: Any) -> Dict[str, Any]:
        payload = {"status": "success"}
        payload.update(data)
        return payload

    def _err(self, message: str, **data: Any) -> Dict[str, Any]:
        payload = {"status": "error", "error": message}
        payload.update(data)
        return payload

    def _import_module(self, key: str) -> Dict[str, Any]:
        if key not in self._module_map:
            return self._err(
                f"Unknown module key '{key}'. Check available module keys via get_capabilities()."
            )
        if key in self._modules:
            return self._ok(module_key=key, module=self._modules[key], cached=True)

        module_path = self._module_map[key]
        try:
            module = importlib.import_module(module_path)
            self._modules[key] = module
            return self._ok(module_key=key, module=module, cached=False)
        except Exception as exc:
            tb = traceback.format_exc()
            self._import_errors[key] = f"{exc}\n{tb}"
            return self._err(
                f"Failed to import module '{module_path}'. Ensure repository dependencies are installed and compatible.",
                module_key=key,
                module_path=module_path,
                details=str(exc),
            )

    def _get_attr_callable(self, module_key: str, func_name: str) -> Dict[str, Any]:
        mod_res = self._import_module(module_key)
        if mod_res["status"] != "success":
            return mod_res

        module = mod_res["module"]
        if not hasattr(module, func_name):
            return self._err(
                f"Function '{func_name}' not found in module '{self._module_map[module_key]}'.",
                module_key=module_key,
                function=func_name,
            )

        target = getattr(module, func_name)
        if not callable(target):
            return self._err(
                f"Attribute '{func_name}' exists but is not callable in module '{self._module_map[module_key]}'.",
                module_key=module_key,
                function=func_name,
            )
        return self._ok(callable=target, module_key=module_key, function=func_name)

    def _get_attr_class(self, module_key: str, class_name: str) -> Dict[str, Any]:
        mod_res = self._import_module(module_key)
        if mod_res["status"] != "success":
            return mod_res

        module = mod_res["module"]
        if not hasattr(module, class_name):
            return self._err(
                f"Class '{class_name}' not found in module '{self._module_map[module_key]}'.",
                module_key=module_key,
                class_name=class_name,
            )

        cls = getattr(module, class_name)
        if not isinstance(cls, type):
            return self._err(
                f"Attribute '{class_name}' exists but is not a class in module '{self._module_map[module_key]}'.",
                module_key=module_key,
                class_name=class_name,
            )
        return self._ok(cls=cls, module_key=module_key, class_name=class_name)

    # -------------------------------------------------------------------------
    # Adapter metadata and health
    # -------------------------------------------------------------------------
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return adapter capabilities derived from analysis.

        Returns:
            Dict[str, Any]: Unified status response including supported modules,
            known CLI entry points, dependencies, and risk profile.
        """
        return self._ok(
            mode=self.mode,
            import_strategy={"primary": "import", "fallback": "import", "confidence": 0.9},
            modules=list(self._module_map.values()),
            cli_commands=[
                "python tools/train/train.py",
                "streamlit run app/streamlit/app.py",
                "python app/gradio/app.py",
            ],
            dependencies={
                "required": [
                    "jax",
                    "flax",
                    "transformers",
                    "numpy",
                    "Pillow",
                    "datasets",
                    "sentencepiece",
                    "tokenizers",
                ],
                "optional": [
                    "gradio",
                    "streamlit",
                    "wandb",
                    "scalable-shampoo related training extras",
                    "torch (possibly indirect/tooling)",
                ],
            },
            risk={
                "import_feasibility": 0.56,
                "intrusiveness_risk": "medium",
                "complexity": "complex",
            },
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a lightweight import health check of core modules.

        Returns:
            Dict[str, Any]: Unified status with per-module import results.
        """
        checks = {}
        failures = 0
        for key in ["dalle_init", "data", "configuration", "modeling", "processor", "text", "utils"]:
            res = self._import_module(key)
            checks[key] = {
                "status": res["status"],
                "module_path": self._module_map[key],
                "error": res.get("error"),
                "details": res.get("details"),
            }
            if res["status"] != "success":
                failures += 1

        if failures:
            return self._err(
                "One or more core modules failed to import. Install missing dependencies and verify Python/JAX compatibility.",
                checks=checks,
                failure_count=failures,
            )
        return self._ok(checks=checks, failure_count=0)

    # -------------------------------------------------------------------------
    # Generic module/function/class access
    # -------------------------------------------------------------------------
    def import_module(self, module_key: str) -> Dict[str, Any]:
        """
        Import a known repository module by logical key.

        Args:
            module_key (str): Key in internal module map (see get_capabilities()).

        Returns:
            Dict[str, Any]: Unified status with module metadata.
        """
        res = self._import_module(module_key)
        if res["status"] != "success":
            return res
        module = res["module"]
        return self._ok(
            module_key=module_key,
            module_path=self._module_map[module_key],
            module_name=getattr(module, "__name__", None),
            cached=res.get("cached", False),
        )

    def call_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a known module dynamically.

        Args:
            module_key (str): Internal module key.
            function_name (str): Target function name.
            *args: Positional arguments for function.
            **kwargs: Keyword arguments for function.

        Returns:
            Dict[str, Any]: Unified status with function result.
        """
        target_res = self._get_attr_callable(module_key, function_name)
        if target_res["status"] != "success":
            return target_res
        try:
            result = target_res["callable"](*args, **kwargs)
            return self._ok(
                module_key=module_key,
                function=function_name,
                result=result,
            )
        except Exception as exc:
            return self._err(
                f"Function call failed for '{function_name}'. Review input arguments and dependency/runtime requirements.",
                module_key=module_key,
                function=function_name,
                details=str(exc),
            )

    def create_instance(self, module_key: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class from a known module dynamically.

        Args:
            module_key (str): Internal module key.
            class_name (str): Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            Dict[str, Any]: Unified status with created instance.
        """
        cls_res = self._get_attr_class(module_key, class_name)
        if cls_res["status"] != "success":
            return cls_res
        try:
            instance = cls_res["cls"](*args, **kwargs)
            return self._ok(
                module_key=module_key,
                class_name=class_name,
                instance=instance,
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate class '{class_name}'. Verify constructor parameters and environment dependencies.",
                module_key=module_key,
                class_name=class_name,
                details=str(exc),
            )

    # -------------------------------------------------------------------------
    # Repository entrypoint methods
    # -------------------------------------------------------------------------
    def run_train_script(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute tools/train/train.py as a script entrypoint.

        Args:
            argv (Optional[List[str]]): CLI arguments excluding script name.
                Example: ["--help"] or training flags expected by the script.

        Returns:
            Dict[str, Any]: Unified status with execution metadata.
        """
        script_rel = os.path.join("tools", "train", "train.py")
        script_abs = os.path.join(source_path, script_rel)
        if not os.path.exists(script_abs):
            return self._err(
                "Training script not found. Ensure repository is extracted under the expected source directory.",
                script_path=script_abs,
            )
        old_argv = sys.argv[:]
        try:
            sys.argv = [script_abs] + (argv or [])
            runpy.run_path(script_abs, run_name="__main__")
            return self._ok(
                script=script_rel,
                argv=argv or [],
                message="Training script executed.",
            )
        except SystemExit as exc:
            code = getattr(exc, "code", 0)
            if code in (0, None):
                return self._ok(
                    script=script_rel,
                    argv=argv or [],
                    message="Training script exited cleanly.",
                    exit_code=code,
                )
            return self._err(
                "Training script exited with a non-zero status.",
                script=script_rel,
                argv=argv or [],
                exit_code=code,
            )
        except Exception as exc:
            return self._err(
                "Training script execution failed. Verify runtime dependencies (JAX/Flax/Transformers) and script arguments.",
                script=script_rel,
                argv=argv or [],
                details=str(exc),
            )
        finally:
            sys.argv = old_argv

    def run_gradio_app(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute app/gradio/app.py as a script entrypoint.

        Args:
            argv (Optional[List[str]]): Optional CLI args passed to script.

        Returns:
            Dict[str, Any]: Unified status with execution metadata.
        """
        script_rel = os.path.join("app", "gradio", "app.py")
        script_abs = os.path.join(source_path, script_rel)
        if not os.path.exists(script_abs):
            return self._err(
                "Gradio app script not found. Ensure repository files are present.",
                script_path=script_abs,
            )
        old_argv = sys.argv[:]
        try:
            sys.argv = [script_abs] + (argv or [])
            runpy.run_path(script_abs, run_name="__main__")
            return self._ok(script=script_rel, argv=argv or [], message="Gradio app executed.")
        except Exception as exc:
            return self._err(
                "Failed to run Gradio app. Install optional dependency 'gradio' and verify model/runtime setup.",
                script=script_rel,
                argv=argv or [],
                details=str(exc),
            )
        finally:
            sys.argv = old_argv

    def run_streamlit_app(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute app/streamlit/app.py as a script entrypoint.

        Args:
            argv (Optional[List[str]]): Optional CLI args passed to script.

        Returns:
            Dict[str, Any]: Unified status with execution metadata.
        """
        script_rel = os.path.join("app", "streamlit", "app.py")
        script_abs = os.path.join(source_path, script_rel)
        if not os.path.exists(script_abs):
            return self._err(
                "Streamlit app script not found. Ensure repository files are present.",
                script_path=script_abs,
            )
        old_argv = sys.argv[:]
        try:
            sys.argv = [script_abs] + (argv or [])
            runpy.run_path(script_abs, run_name="__main__")
            return self._ok(script=script_rel, argv=argv or [], message="Streamlit app executed.")
        except Exception as exc:
            return self._err(
                "Failed to run Streamlit app. Install optional dependency 'streamlit' and verify runtime setup.",
                script=script_rel,
                argv=argv or [],
                details=str(exc),
            )
        finally:
            sys.argv = old_argv

    # -------------------------------------------------------------------------
    # Module-specific convenience methods
    # -------------------------------------------------------------------------
    def load_data_module(self) -> Dict[str, Any]:
        return self.import_module("data")

    def load_configuration_module(self) -> Dict[str, Any]:
        return self.import_module("configuration")

    def load_modeling_module(self) -> Dict[str, Any]:
        return self.import_module("modeling")

    def load_processor_module(self) -> Dict[str, Any]:
        return self.import_module("processor")

    def load_text_module(self) -> Dict[str, Any]:
        return self.import_module("text")

    def load_tokenizer_module(self) -> Dict[str, Any]:
        return self.import_module("tokenizer")

    def load_utils_module(self) -> Dict[str, Any]:
        return self.import_module("utils")