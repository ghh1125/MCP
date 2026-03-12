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
    Import-mode adapter for the flair repository.

    This adapter prioritizes direct import/use of repository modules and provides
    graceful fallback responses when imports or runtime execution fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module registry
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._module_map = {
            "flair.__init__": "flair",
            "flair.data": "flair.data",
            "flair.tokenization": "flair.tokenization",
            "flair.datasets": "flair.datasets",
            "flair.embeddings": "flair.embeddings",
            "flair.models": "flair.models",
            "flair.nn": "flair.nn",
            "flair.trainers": "flair.trainers",
            "flair.trainers.trainer": "flair.trainers.trainer",
            "flair.training_utils": "flair.training_utils",
            "flair.file_utils": "flair.file_utils",
            "flair.inference_utils": "flair.inference_utils",
            "flair.visual": "flair.visual",
            "examples.ner.run_ner": "examples.ner.run_ner",
            "examples.multi_gpu.run_multi_gpu": "examples.multi_gpu.run_multi_gpu",
        }
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _load_modules(self) -> None:
        for key, module_path in self._module_map.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._import_errors[key] = (
                    f"Failed to import '{module_path}'. "
                    f"Ensure repository source exists under '{source_path}' and dependencies are installed. "
                    f"Original error: {exc}"
                )

    def health_check(self) -> Dict[str, Any]:
        return self._result(
            "success" if not self._import_errors else "partial",
            mode=self.mode,
            imported_modules=list(self._modules.keys()),
            failed_modules=self._import_errors,
            guidance=(
                "Install required dependencies (torch, transformers, tqdm, numpy, scikit-learn, deprecated, segtok, "
                "matplotlib, janome, langdetect, lxml, gdown, sqlitedict, mpld3) and verify source path."
            ),
        )

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def _get_module(self, key: str) -> Dict[str, Any]:
        module = self._modules.get(key)
        if module is None:
            return self._result(
                "error",
                message=self._import_errors.get(
                    key,
                    f"Module '{key}' is unavailable. Confirm local source checkout and dependencies.",
                ),
                mode=self.mode,
            )
        return self._result("success", module=module)

    def _safe_call(self, fn: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            value = fn(*args, **kwargs)
            return self._result("success", data=value)
        except Exception as exc:
            return self._result(
                "error",
                message=(
                    f"Function call failed: {exc}. Check parameter values and dependency/runtime compatibility."
                ),
                traceback=traceback.format_exc(),
                mode=self.mode,
            )

    def _safe_instantiate(self, cls: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            instance = cls(*args, **kwargs)
            return self._result("success", data=instance)
        except Exception as exc:
            return self._result(
                "error",
                message=(
                    f"Class instantiation failed: {exc}. Verify constructor arguments and model/resource availability."
                ),
                traceback=traceback.format_exc(),
                mode=self.mode,
            )

    # -------------------------------------------------------------------------
    # Flair core classes
    # -------------------------------------------------------------------------
    def create_sentence(self, text: str, use_tokenizer: Any = True, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Create flair.data.Sentence instance.

        Parameters:
        - text: Input text.
        - use_tokenizer: Tokenizer flag/callable accepted by Flair.
        - language_code: Optional language code.

        Returns:
        Unified status dictionary containing the instance or error details.
        """
        m = self._get_module("flair.data")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "Sentence", None)
        if cls is None:
            return self._result("error", message="Sentence class not found in flair.data.", mode=self.mode)
        return self._safe_instantiate(cls, text, use_tokenizer=use_tokenizer, language_code=language_code)

    def create_token(self, text: str, head_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create flair.data.Token instance.

        Parameters:
        - text: Token text.
        - head_id: Optional head index for dependency structures.
        """
        m = self._get_module("flair.data")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "Token", None)
        if cls is None:
            return self._result("error", message="Token class not found in flair.data.", mode=self.mode)
        kwargs = {}
        if head_id is not None:
            kwargs["head_id"] = head_id
        return self._safe_instantiate(cls, text, **kwargs)

    def create_corpus(self, train: Any = None, dev: Any = None, test: Any = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create flair.data.Corpus instance.

        Parameters:
        - train/dev/test: Split datasets accepted by Flair.
        - name: Optional corpus name.
        """
        m = self._get_module("flair.data")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "Corpus", None)
        if cls is None:
            return self._result("error", message="Corpus class not found in flair.data.", mode=self.mode)
        return self._safe_instantiate(cls, train, dev, test, name=name)

    # -------------------------------------------------------------------------
    # Model classes
    # -------------------------------------------------------------------------
    def create_sequence_tagger(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create flair.models.SequenceTagger instance with forwarded constructor args.
        """
        m = self._get_module("flair.models")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "SequenceTagger", None)
        if cls is None:
            return self._result("error", message="SequenceTagger class not found in flair.models.", mode=self.mode)
        return self._safe_instantiate(cls, *args, **kwargs)

    def create_text_classifier(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create flair.models.TextClassifier instance with forwarded constructor args.
        """
        m = self._get_module("flair.models")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "TextClassifier", None)
        if cls is None:
            return self._result("error", message="TextClassifier class not found in flair.models.", mode=self.mode)
        return self._safe_instantiate(cls, *args, **kwargs)

    def create_model_trainer(self, model: Any, corpus: Any, optimizer: Any = None) -> Dict[str, Any]:
        """
        Create flair.trainers.ModelTrainer instance.

        Parameters:
        - model: Flair model instance.
        - corpus: Flair corpus instance.
        - optimizer: Optional optimizer class/instance.
        """
        m = self._get_module("flair.trainers")
        if m["status"] != "success":
            return m
        cls = getattr(m["module"], "ModelTrainer", None)
        if cls is None:
            return self._result("error", message="ModelTrainer class not found in flair.trainers.", mode=self.mode)
        if optimizer is None:
            return self._safe_instantiate(cls, model, corpus)
        return self._safe_instantiate(cls, model, corpus, optimizer=optimizer)

    # -------------------------------------------------------------------------
    # Function-style calls
    # -------------------------------------------------------------------------
    def run_ner_script_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call examples.ner.run_ner main entry if available.

        Parameters:
        - argv: Optional argument list. If unsupported by target main(), call without args.
        """
        m = self._get_module("examples.ner.run_ner")
        if m["status"] != "success":
            return m
        main_fn = getattr(m["module"], "main", None)
        if main_fn is None:
            return self._result(
                "error",
                message="examples.ner.run_ner.main not found. This script may not expose a callable entry.",
                mode=self.mode,
            )
        if argv is None:
            return self._safe_call(main_fn)
        try:
            return self._safe_call(main_fn, argv)
        except Exception:
            return self._safe_call(main_fn)

    def run_multi_gpu_script_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Call examples.multi_gpu.run_multi_gpu main entry if available.
        """
        m = self._get_module("examples.multi_gpu.run_multi_gpu")
        if m["status"] != "success":
            return m
        main_fn = getattr(m["module"], "main", None)
        if main_fn is None:
            return self._result(
                "error",
                message="examples.multi_gpu.run_multi_gpu.main not found. This script may not expose a callable entry.",
                mode=self.mode,
            )
        if argv is None:
            return self._safe_call(main_fn)
        try:
            return self._safe_call(main_fn, argv)
        except Exception:
            return self._safe_call(main_fn)

    # -------------------------------------------------------------------------
    # Utility wrappers
    # -------------------------------------------------------------------------
    def list_module_attributes(self, module_key: str, public_only: bool = True) -> Dict[str, Any]:
        """
        List attributes exported by a loaded module key.

        Parameters:
        - module_key: One of internal keys from module registry.
        - public_only: If True, exclude private names.
        """
        m = self._get_module(module_key)
        if m["status"] != "success":
            return m
        names = dir(m["module"])
        if public_only:
            names = [n for n in names if not n.startswith("_")]
        return self._result("success", data=names, mode=self.mode)

    def get_import_report(self) -> Dict[str, Any]:
        """
        Return import success/failure report for all managed modules.
        """
        return self._result(
            "success",
            mode=self.mode,
            loaded={k: v.__name__ for k, v in self._modules.items()},
            failed=self._import_errors,
        )