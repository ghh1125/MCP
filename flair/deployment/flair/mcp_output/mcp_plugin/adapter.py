import os
import sys
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
    MCP Import Mode Adapter for the Flair repository.

    This adapter prioritizes direct imports from the local `source` tree and provides
    structured, unified responses for all operations.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._module_cache: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}

        self._known_modules: List[str] = [
            "flair",
            "flair.data",
            "flair.datasets",
            "flair.embeddings",
            "flair.models",
            "flair.nn",
            "flair.trainers",
            "flair.visual",
            "examples.ner.run_ner",
            "examples.multi_gpu.run_multi_gpu",
        ]

        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if hint:
            payload["hint"] = hint
        return payload

    def _initialize_imports(self) -> None:
        for module_name in self._known_modules:
            try:
                self._module_cache[module_name] = importlib.import_module(module_name)
            except Exception as e:
                self._import_errors[module_name] = str(e)

    def _get_module(self, module_name: str) -> Any:
        if module_name in self._module_cache:
            return self._module_cache[module_name]
        try:
            module = importlib.import_module(module_name)
            self._module_cache[module_name] = module
            return module
        except Exception as e:
            self._import_errors[module_name] = str(e)
            raise

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import availability.

        Returns:
            Unified dictionary with status, loaded modules, and import failures.
        """
        return self._ok(
            data={
                "loaded_modules": sorted(list(self._module_cache.keys())),
                "failed_modules": self._import_errors,
                "source_path": source_path,
            },
            message="Adapter initialized with import mode diagnostics.",
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List known target modules and current import status.

        Returns:
            Unified dictionary with module metadata.
        """
        results = []
        for name in self._known_modules:
            results.append(
                {
                    "module": name,
                    "loaded": name in self._module_cache,
                    "error": self._import_errors.get(name),
                }
            )
        return self._ok(data={"modules": results}, message="Module status listed.")

    # -------------------------------------------------------------------------
    # Generic invocation APIs
    # -------------------------------------------------------------------------
    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a module.

        Args:
            module_name: Full module path (e.g., 'flair.data').
            class_name: Class name inside the module.
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            Unified dictionary containing instance metadata and object reference.
        """
        try:
            module = self._get_module(module_name)
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                data={
                    "module": module_name,
                    "class": class_name,
                    "instance": instance,
                    "instance_type": str(type(instance)),
                },
                message=f"Instance created for {module_name}.{class_name}.",
            )
        except Exception as e:
            return self._fail(
                message=f"Failed to create instance for {module_name}.{class_name}.",
                error=e,
                hint="Verify class name, constructor arguments, and optional dependencies.",
            )

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a module.

        Args:
            module_name: Full module path (e.g., 'flair').
            function_name: Function name inside the module.
            *args: Positional arguments for function call.
            **kwargs: Keyword arguments for function call.

        Returns:
            Unified dictionary containing function output.
        """
        try:
            module = self._get_module(module_name)
            func = getattr(module, function_name)
            result = func(*args, **kwargs)
            return self._ok(
                data={
                    "module": module_name,
                    "function": function_name,
                    "result": result,
                },
                message=f"Function called: {module_name}.{function_name}.",
            )
        except Exception as e:
            return self._fail(
                message=f"Failed to call function {module_name}.{function_name}.",
                error=e,
                hint="Check function name, parameters, and runtime dependencies.",
            )

    # -------------------------------------------------------------------------
    # Flair-focused convenience wrappers
    # -------------------------------------------------------------------------
    def create_sentence(self, text: str, use_tokenizer: bool = True) -> Dict[str, Any]:
        """
        Create a Flair Sentence instance.

        Args:
            text: Raw text to wrap in flair.data.Sentence.
            use_tokenizer: Whether Flair should tokenize input text.

        Returns:
            Unified dictionary with created Sentence object.
        """
        try:
            data_mod = self._get_module("flair.data")
            sentence = data_mod.Sentence(text, use_tokenizer=use_tokenizer)
            return self._ok(data={"sentence": sentence}, message="Sentence created successfully.")
        except Exception as e:
            return self._fail(
                message="Failed to create Sentence.",
                error=e,
                hint="Ensure flair.data is importable and input text is valid.",
            )

    def load_model(self, model_class_module: str, model_class_name: str, model_path_or_name: str) -> Dict[str, Any]:
        """
        Load a Flair model via classmethod `load`.

        Args:
            model_class_module: Module path containing model class (e.g., 'flair.models').
            model_class_name: Model class name with `load` classmethod.
            model_path_or_name: Model alias or file path.

        Returns:
            Unified dictionary containing loaded model object.
        """
        try:
            module = self._get_module(model_class_module)
            model_cls = getattr(module, model_class_name)
            model = model_cls.load(model_path_or_name)
            return self._ok(
                data={"model": model, "model_class": model_class_name},
                message=f"Model loaded: {model_class_name} from '{model_path_or_name}'.",
            )
        except Exception as e:
            return self._fail(
                message="Failed to load model.",
                error=e,
                hint="Confirm model class supports `.load()` and required weights are available.",
            )

    def run_example_ner(self) -> Dict[str, Any]:
        """
        Execute example NER entrypoint module if callable API is available.

        Returns:
            Unified dictionary with invocation result or guidance.
        """
        try:
            mod = self._get_module("examples.ner.run_ner")
            if hasattr(mod, "main"):
                result = mod.main()
                return self._ok(data={"result": result}, message="NER example executed via main().")
            return self._ok(
                data={"module": "examples.ner.run_ner"},
                message="NER module imported. No main() function found; run as script if needed.",
            )
        except Exception as e:
            return self._fail(
                message="Failed to run NER example module.",
                error=e,
                hint="Try executing `python -m examples.ner.run_ner` with proper environment.",
            )

    def run_example_multi_gpu(self) -> Dict[str, Any]:
        """
        Execute example multi-GPU entrypoint module if callable API is available.

        Returns:
            Unified dictionary with invocation result or guidance.
        """
        try:
            mod = self._get_module("examples.multi_gpu.run_multi_gpu")
            if hasattr(mod, "main"):
                result = mod.main()
                return self._ok(data={"result": result}, message="Multi-GPU example executed via main().")
            return self._ok(
                data={"module": "examples.multi_gpu.run_multi_gpu"},
                message="Multi-GPU module imported. No main() function found; run as script if needed.",
            )
        except Exception as e:
            return self._fail(
                message="Failed to run multi-GPU example module.",
                error=e,
                hint="Try executing `python -m examples.multi_gpu.run_multi_gpu` with distributed setup.",
            )