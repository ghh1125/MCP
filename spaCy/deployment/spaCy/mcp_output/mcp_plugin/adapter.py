import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for spaCy source integration.

    This adapter prioritizes direct imports from the local repository source tree.
    If imports fail, it gracefully falls back and returns actionable error guidance.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_error: Optional[str] = None

        self._spacy_module = None
        self._cli_download = None
        self._cli_train = None
        self._cli_evaluate = None
        self._cli_convert = None
        self._cli_package = None
        self._cli_debug_data = None
        self._cli_debug_config = None
        self._cli_debug_model = None
        self._cli_init_config = None
        self._cli_init_pipeline = None
        self._cli_validate = None
        self._cli_info = None

        self._initialize_imports()

    def _initialize_imports(self) -> None:
        try:
            import source.spacy as spacy_module
            import source.spacy.cli.download as cli_download
            import source.spacy.cli.train as cli_train
            import source.spacy.cli.evaluate as cli_evaluate
            import source.spacy.cli.convert as cli_convert
            import source.spacy.cli.package as cli_package
            import source.spacy.cli.debug_data as cli_debug_data
            import source.spacy.cli.debug_config as cli_debug_config
            import source.spacy.cli.debug_model as cli_debug_model
            import source.spacy.cli.init_config as cli_init_config
            import source.spacy.cli.init_pipeline as cli_init_pipeline
            import source.spacy.cli.validate as cli_validate
            import source.spacy.cli.info as cli_info

            self._spacy_module = spacy_module
            self._cli_download = cli_download
            self._cli_train = cli_train
            self._cli_evaluate = cli_evaluate
            self._cli_convert = cli_convert
            self._cli_package = cli_package
            self._cli_debug_data = cli_debug_data
            self._cli_debug_config = cli_debug_config
            self._cli_debug_model = cli_debug_model
            self._cli_init_config = cli_init_config
            self._cli_init_pipeline = cli_init_pipeline
            self._cli_validate = cli_validate
            self._cli_info = cli_info

            self._loaded = True
        except Exception as e:
            self._loaded = False
            self._import_error = str(e)

    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _guard_imports(self) -> Optional[Dict[str, Any]]:
        if self._loaded:
            return None
        return self._fail(
            "Import mode is unavailable because repository modules could not be loaded.",
            guidance=(
                "Verify that the local source directory exists and contains the spaCy repository "
                "under 'source/spacy'. Check Python version compatibility and dependencies."
                + (f" Original import error: {self._import_error}" if self._import_error else "")
            ),
        )

    # -------------------------------------------------------------------------
    # Core API wrappers (from source.spacy.__init__)
    # -------------------------------------------------------------------------
    def call_load(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Load a spaCy pipeline by name or path.

        Parameters:
        - name: Model package name or model path.
        - **kwargs: Additional arguments forwarded to source.spacy.load().

        Returns:
        - Unified status dictionary with loaded Language object in data.
        """
        err = self._guard_imports()
        if err:
            return err
        try:
            nlp = self._spacy_module.load(name, **kwargs)
            return self._ok(data=nlp, message="Pipeline loaded successfully.")
        except Exception as e:
            return self._fail(
                f"Failed to load pipeline '{name}': {e}",
                guidance="Ensure the model/package exists and is compatible with this spaCy source version.",
            )

    def call_blank(self, lang: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a blank spaCy language object.

        Parameters:
        - lang: Language code (e.g., 'en', 'de', 'fr').
        - **kwargs: Additional arguments forwarded to source.spacy.blank().

        Returns:
        - Unified status dictionary with Language object in data.
        """
        err = self._guard_imports()
        if err:
            return err
        try:
            nlp = self._spacy_module.blank(lang, **kwargs)
            return self._ok(data=nlp, message="Blank language pipeline created successfully.")
        except Exception as e:
            return self._fail(
                f"Failed to create blank language '{lang}': {e}",
                guidance="Check that the language code is supported in the local spaCy source tree.",
            )

    # -------------------------------------------------------------------------
    # CLI command wrappers (module-level command entry functions)
    # -------------------------------------------------------------------------
    def call_download(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_download, "download", *args, **kwargs)

    def call_train(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_train, "train", *args, **kwargs)

    def call_evaluate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_evaluate, "evaluate", *args, **kwargs)

    def call_convert(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_convert, "convert", *args, **kwargs)

    def call_package(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_package, "package", *args, **kwargs)

    def call_debug_data(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_debug_data, "debug_data", *args, **kwargs)

    def call_debug_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_debug_config, "debug_config", *args, **kwargs)

    def call_debug_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_debug_model, "debug_model", *args, **kwargs)

    def call_init_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_init_config, "init_config", *args, **kwargs)

    def call_init_pipeline(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_init_pipeline, "init_pipeline", *args, **kwargs)

    def call_validate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_validate, "validate", *args, **kwargs)

    def call_info(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_cli_module(self._cli_info, "info", *args, **kwargs)

    def _call_cli_module(self, module: Any, label: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a CLI module function by searching for likely entry function names.

        Strategy:
        1) Try function matching module label (e.g., train, evaluate, download).
        2) Fallback to common names: main, app, cli.
        """
        err = self._guard_imports()
        if err:
            return err

        if module is None:
            return self._fail(
                f"CLI module '{label}' is not available.",
                guidance="Check that the corresponding source.spacy.cli module exists and imports correctly.",
            )

        candidate_names = [label, "main", "app", "cli"]
        try:
            for fn_name in candidate_names:
                fn = getattr(module, fn_name, None)
                if callable(fn):
                    result = fn(*args, **kwargs)
                    return self._ok(data=result, message=f"CLI '{label}' executed successfully.")
            return self._fail(
                f"No callable entry point found for CLI module '{label}'.",
                guidance="Inspect the module and call the exported function name explicitly.",
            )
        except Exception as e:
            return self._fail(
                f"CLI '{label}' execution failed: {e}",
                guidance="Validate command arguments and file paths. For training/evaluation, verify config and corpus assets.",
            )