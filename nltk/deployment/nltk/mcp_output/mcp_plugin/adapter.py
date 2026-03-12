import os
import sys
import importlib
import inspect
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the NLTK repository.

    This adapter prioritizes direct Python imports and function calls from the local
    repository source tree. If import is unavailable, it provides graceful fallback
    guidance via status dictionaries.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._load_state = self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success"}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "message": message}
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _load_module(self, dotted_name: str) -> Dict[str, Any]:
        try:
            mod = importlib.import_module(dotted_name)
            self._modules[dotted_name] = mod
            return self._ok({"module": dotted_name})
        except Exception as e:
            return self._err(
                f"Failed to import module '{dotted_name}': {e}",
                "Ensure repository source is present under the configured 'source' path and dependencies are installed.",
            )

    def _load_modules(self) -> Dict[str, Any]:
        modules = [
            "nltk.toolbox",
            "nltk.grammar",
            "nltk.text",
            "nltk.probability",
            "nltk.collocations",
            "nltk.featstruct",
            "nltk.corpus",
            "tools.global_replace",
            "tools.find_deprecated",
        ]
        results = {}
        for name in modules:
            results[name] = self._load_module(name)
        return self._ok({"imports": results})

    def _get_attr(self, module_name: str, attr_name: str) -> Dict[str, Any]:
        module = self._modules.get(module_name)
        if module is None:
            imp = self._load_module(module_name)
            if imp.get("status") != "success":
                return imp
            module = self._modules.get(module_name)

        if module is None:
            return self._err(
                f"Module '{module_name}' is unavailable.",
                "Check source path setup and module files.",
            )

        if not hasattr(module, attr_name):
            return self._err(
                f"Attribute '{attr_name}' not found in module '{module_name}'.",
                "Verify repository version and target API compatibility.",
            )

        return self._ok({"attribute": getattr(module, attr_name)})

    def health_check(self) -> Dict[str, Any]:
        """
        Verify adapter readiness and report import health.

        Returns:
            dict: Unified status dict including current mode and module import results.
        """
        return self._ok({"mode": self.mode, "load_state": self._load_state})

    # -------------------------------------------------------------------------
    # Functions from tools.global_replace
    # -------------------------------------------------------------------------
    def call_tools_global_replace_update(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call tools.global_replace.update(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to update.
            **kwargs: Keyword arguments forwarded to update.

        Returns:
            dict: status + result or structured error.
        """
        getter = self._get_attr("tools.global_replace", "update")
        if getter["status"] != "success":
            return getter
        fn = getter["attribute"]
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for tools.global_replace.update: {e}",
                "Check argument types and repository file access permissions.",
            )

    # -------------------------------------------------------------------------
    # Functions from tools.find_deprecated
    # -------------------------------------------------------------------------
    def call_tools_find_deprecated_find_class(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call tools.find_deprecated.find_class(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to find_class.
            **kwargs: Keyword arguments forwarded to find_class.

        Returns:
            dict: status + result or structured error.
        """
        getter = self._get_attr("tools.find_deprecated", "find_class")
        if getter["status"] != "success":
            return getter
        fn = getter["attribute"]
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for tools.find_deprecated.find_class: {e}",
                "Validate input paths and class name patterns.",
            )

    def call_tools_find_deprecated_find_deprecated_defs(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call tools.find_deprecated.find_deprecated_defs(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to find_deprecated_defs.
            **kwargs: Keyword arguments forwarded to find_deprecated_defs.

        Returns:
            dict: status + result or structured error.
        """
        getter = self._get_attr("tools.find_deprecated", "find_deprecated_defs")
        if getter["status"] != "success":
            return getter
        fn = getter["attribute"]
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for tools.find_deprecated.find_deprecated_defs: {e}",
                "Ensure target files are readable and valid Python sources.",
            )

    def call_tools_find_deprecated_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call tools.find_deprecated.main(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to main.
            **kwargs: Keyword arguments forwarded to main.

        Returns:
            dict: status + result or structured error.
        """
        getter = self._get_attr("tools.find_deprecated", "main")
        if getter["status"] != "success":
            return getter
        fn = getter["attribute"]
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for tools.find_deprecated.main: {e}",
                "If this function expects CLI context, provide compatible arguments.",
            )

    # -------------------------------------------------------------------------
    # Demo functions from NLTK modules
    # -------------------------------------------------------------------------
    def call_nltk_toolbox_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.toolbox.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.toolbox", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.toolbox.demo: {e}",
                "Some demos require specific local files or corpora; verify data availability.",
            )

    def call_nltk_grammar_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.grammar.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.grammar", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.grammar.demo: {e}",
                "Check function arguments and grammar-related dependencies.",
            )

    def call_nltk_text_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.text.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.text", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.text.demo: {e}",
                "This demo may require installed corpora; run nltk downloader if needed.",
            )

    def call_nltk_probability_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.probability.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.probability", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.probability.demo: {e}",
                "Confirm any required example data is available.",
            )

    def call_nltk_collocations_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.collocations.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.collocations", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.collocations.demo: {e}",
                "Install required corpora and verify tokenizer resources.",
            )

    def call_nltk_featstruct_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.featstruct.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.featstruct", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.featstruct.demo: {e}",
                "Validate arguments and ensure compatibility with current NLTK version.",
            )

    def call_nltk_corpus_demo(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call nltk.corpus.demo(*args, **kwargs).
        """
        getter = self._get_attr("nltk.corpus", "demo")
        if getter["status"] != "success":
            return getter
        try:
            result = getter["attribute"](*args, **kwargs)
            return self._ok({"result": result})
        except Exception as e:
            return self._err(
                f"Call failed for nltk.corpus.demo: {e}",
                "Download missing corpora using the downloader module.",
            )

    # -------------------------------------------------------------------------
    # CLI-oriented fallbacks
    # -------------------------------------------------------------------------
    def fallback_cli_nltk(self) -> Dict[str, Any]:
        """
        Provide guidance for CLI fallback: python -m nltk.

        Returns:
            dict: status and actionable guidance.
        """
        return self._ok(
            {
                "mode": "cli_fallback",
                "command": "python -m nltk",
                "note": "Use this when import mode fails or when interactive CLI behavior is needed.",
            }
        )

    def fallback_cli_downloader(self) -> Dict[str, Any]:
        """
        Provide guidance for CLI fallback: python -m nltk.downloader.

        Returns:
            dict: status and actionable guidance.
        """
        return self._ok(
            {
                "mode": "cli_fallback",
                "command": "python -m nltk.downloader",
                "note": "Use this to install corpora/models required by many NLTK APIs and demos.",
            }
        )

    # -------------------------------------------------------------------------
    # Introspection utility
    # -------------------------------------------------------------------------
    def list_available_calls(self) -> Dict[str, Any]:
        """
        List adapter call methods for MCP routing/discovery.

        Returns:
            dict: status and method names.
        """
        try:
            methods = [
                name
                for name, member in inspect.getmembers(self, predicate=inspect.ismethod)
                if name.startswith("call_") or name.startswith("fallback_")
            ]
            return self._ok({"methods": methods, "mode": self.mode})
        except Exception as e:
            return self._err(
                f"Failed to enumerate methods: {e}",
                "Retry after ensuring adapter initialization completed successfully.",
            )