import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the flair repository.

    This adapter prioritizes importing and executing repository code directly from the local
    source tree. If imports are unavailable, it gracefully degrades to a fallback mode and
    returns actionable guidance in English.

    Notes:
    - Analysis did not provide explicit entry-point functions/classes to map 1:1.
    - This adapter therefore exposes robust module-level operations for the core Flair package,
      including dynamic class instantiation and method invocation.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._import_ok = False
        self._errors: List[str] = []
        self._modules: Dict[str, Any] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _initialize_imports(self) -> None:
        """
        Try importing known core modules from the repository using full package paths.
        Falls back cleanly if unavailable.
        """
        module_paths = [
            "deployment.flair.source.flair",
            "deployment.flair.source.flair.data",
            "deployment.flair.source.flair.models",
            "deployment.flair.source.flair.embeddings",
            "deployment.flair.source.flair.datasets",
            "deployment.flair.source.flair.trainers",
            "deployment.flair.source.flair.training_utils",
        ]
        ok_count = 0
        for path in module_paths:
            try:
                self._modules[path] = importlib.import_module(path)
                ok_count += 1
            except Exception as e:
                self._errors.append(f"Failed to import '{path}': {e}")

        self._import_ok = ok_count > 0
        if not self._import_ok:
            self.mode = "fallback"

    def _require_import_mode(self) -> Optional[Dict[str, Any]]:
        if not self._import_ok:
            return self._result(
                "error",
                mode=self.mode,
                message=(
                    "Import mode is unavailable. Ensure the repository source is present at "
                    f"'{source_path}' and verify package path resolution."
                ),
                errors=self._errors,
                action="Check filesystem layout, then retry initialization.",
            )
        return None

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter health, mode, and module import summary.
        """
        return self._result(
            "success" if self._import_ok else "error",
            mode=self.mode,
            import_ok=self._import_ok,
            loaded_modules=list(self._modules.keys()),
            errors=self._errors,
        )

    def list_loaded_modules(self) -> Dict[str, Any]:
        """
        List successfully loaded module paths.
        """
        check = self._require_import_mode()
        if check:
            return check
        return self._result("success", modules=list(self._modules.keys()), mode=self.mode)

    # -------------------------------------------------------------------------
    # Generic module/class/function operations
    # -------------------------------------------------------------------------
    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import a module dynamically by full path.

        Parameters:
            module_path: Fully qualified module path, e.g. 'deployment.flair.source.flair.data'
        """
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            self._import_ok = True
            self.mode = "import"
            return self._result("success", module=module_path, mode=self.mode)
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                module=module_path,
                message=f"Module import failed: {e}",
                action="Verify module path and source tree integrity.",
                traceback=traceback.format_exc(),
            )

    def get_class(self, module_path: str, class_name: str) -> Dict[str, Any]:
        """
        Retrieve a class object from a module.

        Parameters:
            module_path: Fully qualified module path.
            class_name: Target class name.
        """
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return self._result("success", class_name=class_name, module=module_path, class_ref=cls)
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Unable to resolve class '{class_name}' from '{module_path}': {e}",
                action="Confirm class name and module path, then retry.",
                traceback=traceback.format_exc(),
            )

    def create_instance(
        self,
        module_path: str,
        class_name: str,
        init_args: Optional[List[Any]] = None,
        init_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an instance of a class discovered at runtime.

        Parameters:
            module_path: Fully qualified module path.
            class_name: Class name to instantiate.
            init_args: Positional args for __init__.
            init_kwargs: Keyword args for __init__.
        """
        init_args = init_args or []
        init_kwargs = init_kwargs or {}
        try:
            class_info = self.get_class(module_path, class_name)
            if class_info.get("status") != "success":
                return class_info
            cls = class_info["class_ref"]
            instance = cls(*init_args, **init_kwargs)
            return self._result(
                "success",
                mode=self.mode,
                module=module_path,
                class_name=class_name,
                instance=instance,
            )
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Instance creation failed for '{class_name}': {e}",
                action="Review constructor signature and provided arguments.",
                traceback=traceback.format_exc(),
            )

    def call_function(
        self,
        module_path: str,
        function_name: str,
        call_args: Optional[List[Any]] = None,
        call_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call a function from a module.

        Parameters:
            module_path: Fully qualified module path.
            function_name: Function to execute.
            call_args: Positional arguments.
            call_kwargs: Keyword arguments.
        """
        call_args = call_args or []
        call_kwargs = call_kwargs or {}
        try:
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            fn = getattr(module, function_name)
            result = fn(*call_args, **call_kwargs)
            return self._result(
                "success",
                mode=self.mode,
                module=module_path,
                function=function_name,
                result=result,
            )
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Function call failed for '{function_name}': {e}",
                action="Check function name and arguments, then retry.",
                traceback=traceback.format_exc(),
            )

    def call_instance_method(
        self,
        instance: Any,
        method_name: str,
        call_args: Optional[List[Any]] = None,
        call_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call a method on an instance.

        Parameters:
            instance: Target object instance.
            method_name: Method to invoke.
            call_args: Positional arguments.
            call_kwargs: Keyword arguments.
        """
        call_args = call_args or []
        call_kwargs = call_kwargs or {}
        try:
            method = getattr(instance, method_name)
            result = method(*call_args, **call_kwargs)
            return self._result(
                "success",
                mode=self.mode,
                method=method_name,
                result=result,
            )
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Instance method call failed for '{method_name}': {e}",
                action="Validate instance type, method name, and method arguments.",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Flair-focused convenience methods
    # -------------------------------------------------------------------------
    def get_flair_version(self) -> Dict[str, Any]:
        """
        Retrieve Flair version from the imported package.
        """
        candidates = [
            "deployment.flair.source.flair",
        ]
        for mod in candidates:
            try:
                module = self._modules.get(mod) or importlib.import_module(mod)
                version = getattr(module, "__version__", None)
                return self._result("success", mode=self.mode, module=mod, version=version)
            except Exception:
                continue
        return self._result(
            "error",
            mode=self.mode,
            message="Unable to read Flair version.",
            action="Ensure the flair package is importable from the source directory.",
        )

    def create_sentence(self, text: str) -> Dict[str, Any]:
        """
        Create a Sentence object using flair.data.Sentence.

        Parameters:
            text: Raw text content.
        """
        return self.create_instance(
            module_path="deployment.flair.source.flair.data",
            class_name="Sentence",
            init_args=[text],
            init_kwargs={},
        )

    def load_sequence_tagger(self, model_name_or_path: str) -> Dict[str, Any]:
        """
        Load SequenceTagger via classmethod .load() from flair.models.

        Parameters:
            model_name_or_path: Model identifier or local path.
        """
        try:
            module_path = "deployment.flair.source.flair.models"
            module = self._modules.get(module_path) or importlib.import_module(module_path)
            cls = getattr(module, "SequenceTagger")
            model = cls.load(model_name_or_path)
            return self._result(
                "success",
                mode=self.mode,
                module=module_path,
                class_name="SequenceTagger",
                model=model,
            )
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Failed to load SequenceTagger: {e}",
                action="Confirm model name/path and required dependencies (torch, transformers).",
                traceback=traceback.format_exc(),
            )

    def predict_with_model(self, model: Any, sentence_or_sentences: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Run model prediction for Flair model objects exposing .predict().

        Parameters:
            model: Loaded Flair model.
            sentence_or_sentences: Sentence or list of Sentence objects.
            kwargs: Additional predict options.
        """
        try:
            model.predict(sentence_or_sentences, **kwargs)
            return self._result("success", mode=self.mode, message="Prediction completed.")
        except Exception as e:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Prediction failed: {e}",
                action="Ensure input objects are valid Flair data types and model is loaded.",
                traceback=traceback.format_exc(),
            )