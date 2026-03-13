import os
import sys
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for TextBlob.

    This adapter prefers direct Python imports from the repository source tree and
    falls back to actionable guidance when runtime dependencies (for example NLTK
    corpora) are missing.

    Unified return format used by all methods:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import",
        "data": ...,
        "error": ...,
        "guidance": ...
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._imports_ready: bool = False
        self._import_error: Optional[str] = None
        self._load_modules()

    def _ok(self, data: Any = None) -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "data": data}

    def _err(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "error": message,
            "guidance": guidance
            or "Check dependency installation and required NLTK corpora availability.",
        }

    def _fallback(self, message: str, guidance: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "error": message,
            "guidance": guidance,
        }

    def _load_modules(self) -> None:
        try:
            import importlib

            # Core package imports using full repository package paths (without "source." prefix)
            self._modules["textblob"] = importlib.import_module("src.textblob")
            self._modules["blob"] = importlib.import_module("src.textblob.blob")
            self._modules["classifiers"] = importlib.import_module("src.textblob.classifiers")
            self._modules["tokenizers"] = importlib.import_module("src.textblob.tokenizers")
            self._modules["sentiments"] = importlib.import_module("src.textblob.sentiments")
            self._modules["taggers"] = importlib.import_module("src.textblob.taggers")
            self._modules["parsers"] = importlib.import_module("src.textblob.parsers")
            self._modules["np_extractors"] = importlib.import_module("src.textblob.np_extractors")
            self._modules["formats"] = importlib.import_module("src.textblob.formats")
            self._modules["translate"] = importlib.import_module("src.textblob.translate")
            self._modules["download_corpora"] = importlib.import_module("src.textblob.download_corpora")
            self._imports_ready = True
        except Exception as exc:
            self._imports_ready = False
            self._import_error = str(exc)

    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter import readiness.

        Returns:
            Dict with import status and available modules.
        """
        if not self._imports_ready:
            return self._fallback(
                f"Import mode initialization failed: {self._import_error}",
                "Ensure repository source exists under ./source and required dependency 'nltk' is installed.",
            )
        return self._ok(
            {
                "imports_ready": True,
                "modules": sorted(self._modules.keys()),
                "recommended_cli": [
                    "python -m textblob.download_corpora",
                    "python -m textblob.download_corpora lite",
                ],
            }
        )

    # -------------------------------------------------------------------------
    # Corpus / setup helpers
    # -------------------------------------------------------------------------
    def call_download_corpora(self, lite: bool = False) -> Dict[str, Any]:
        """
        Download TextBlob corpora via repository implementation.

        Args:
            lite: If True, download reduced corpus set equivalent to
                  'python -m textblob.download_corpora lite'.

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._fallback(
                "download_corpora module is unavailable in import mode.",
                "Run: python -m textblob.download_corpora (or append 'lite') in a prepared runtime.",
            )
        try:
            mod = self._modules["download_corpora"]
            if lite and hasattr(mod, "download_lite"):
                mod.download_lite()
            elif hasattr(mod, "download_all"):
                mod.download_all()
            elif hasattr(mod, "main"):
                # Best-effort fallback to module CLI entry.
                mod.main(["lite"] if lite else [])
            else:
                return self._err(
                    "No callable download entry found.",
                    "Use CLI fallback: python -m textblob.download_corpora [lite].",
                )
            return self._ok({"lite": lite, "message": "Corpora download requested."})
        except Exception as exc:
            return self._fallback(
                f"Corpora download failed: {exc}",
                "Verify network access and NLTK data write permissions, then retry.",
            )

    # -------------------------------------------------------------------------
    # Core object constructors (instance methods for classes)
    # -------------------------------------------------------------------------
    def instance_textblob(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a TextBlob instance.

        Args:
            text: Input text.
            **kwargs: Optional TextBlob constructor args (tokenizer, np_extractor, pos_tagger, analyzer, parser, classifier).

        Returns:
            Dict with created object metadata.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.", "Call health_check and fix import issues first.")
        try:
            cls = getattr(self._modules["blob"], "TextBlob")
            obj = cls(text, **kwargs)
            return self._ok({"type": "TextBlob", "object": obj, "string": str(obj)})
        except Exception as exc:
            return self._err(f"Failed to create TextBlob: {exc}", "Ensure required corpora are downloaded.")

    def instance_sentence(self, sentence: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a Sentence instance.

        Args:
            sentence: Sentence text.
            **kwargs: Optional constructor args.

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            cls = getattr(self._modules["blob"], "Sentence")
            obj = cls(sentence, **kwargs)
            return self._ok({"type": "Sentence", "object": obj, "string": str(obj)})
        except Exception as exc:
            return self._err(f"Failed to create Sentence: {exc}")

    def instance_word(self, word: str) -> Dict[str, Any]:
        """
        Create a Word instance.

        Args:
            word: Token value.

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            cls = getattr(self._modules["blob"], "Word")
            obj = cls(word)
            return self._ok({"type": "Word", "object": obj, "string": str(obj)})
        except Exception as exc:
            return self._err(f"Failed to create Word: {exc}")

    def instance_blobber(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a Blobber factory instance.

        Args:
            **kwargs: Blobber constructor args (tokenizer, pos_tagger, np_extractor, analyzer, parser, classifier).

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            cls = getattr(self._modules["blob"], "Blobber")
            obj = cls(**kwargs)
            return self._ok({"type": "Blobber", "object": obj})
        except Exception as exc:
            return self._err(f"Failed to create Blobber: {exc}")

    # -------------------------------------------------------------------------
    # Functional wrappers
    # -------------------------------------------------------------------------
    def call_detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language for input text using TextBlob implementation.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary with detected language code.
        """
        try:
            tb_res = self.instance_textblob(text)
            if tb_res["status"] != "success":
                return tb_res
            obj = tb_res["data"]["object"]
            lang = obj.detect_language()
            return self._ok({"language": lang})
        except Exception as exc:
            return self._fallback(
                f"Language detection failed: {exc}",
                "This feature may require external service availability; check network access and retry.",
            )

    def call_translate(self, text: str, to: str = "en", from_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text.

        Args:
            text: Source text.
            to: Target language code.
            from_lang: Optional source language code.

        Returns:
            Unified status dictionary with translated text.
        """
        try:
            tb_res = self.instance_textblob(text)
            if tb_res["status"] != "success":
                return tb_res
            obj = tb_res["data"]["object"]
            translated = obj.translate(from_lang=from_lang, to=to) if from_lang else obj.translate(to=to)
            return self._ok({"translated_text": str(translated), "to": to, "from": from_lang})
        except Exception as exc:
            return self._fallback(
                f"Translation failed: {exc}",
                "Check internet connectivity and translation service access; then retry.",
            )

    def call_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Compute sentiment polarity and subjectivity.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary with sentiment metrics.
        """
        try:
            tb_res = self.instance_textblob(text)
            if tb_res["status"] != "success":
                return tb_res
            s = tb_res["data"]["object"].sentiment
            return self._ok({"polarity": s.polarity, "subjectivity": s.subjectivity})
        except Exception as exc:
            return self._err(f"Sentiment analysis failed: {exc}", "Install corpora and verify TextBlob analyzer setup.")

    def call_pos_tags(self, text: str) -> Dict[str, Any]:
        """
        Get POS tags.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary with POS tags.
        """
        try:
            tb_res = self.instance_textblob(text)
            if tb_res["status"] != "success":
                return tb_res
            tags = tb_res["data"]["object"].tags
            return self._ok({"tags": list(tags)})
        except Exception as exc:
            return self._err(f"POS tagging failed: {exc}", "Download required NLTK corpora and retry.")

    def call_noun_phrases(self, text: str) -> Dict[str, Any]:
        """
        Extract noun phrases.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary with noun phrases.
        """
        try:
            tb_res = self.instance_textblob(text)
            if tb_res["status"] != "success":
                return tb_res
            nps = list(tb_res["data"]["object"].noun_phrases)
            return self._ok({"noun_phrases": nps})
        except Exception as exc:
            return self._err(f"Noun phrase extraction failed: {exc}", "Ensure corpora for NP extraction are installed.")

    def call_tokenize_words(self, text: str) -> Dict[str, Any]:
        """
        Tokenize text into words using repository tokenizer path.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            fn = getattr(self._modules["tokenizers"], "word_tokenize")
            return self._ok({"tokens": list(fn(text))})
        except Exception as exc:
            return self._err(f"Word tokenization failed: {exc}")

    def call_tokenize_sentences(self, text: str) -> Dict[str, Any]:
        """
        Tokenize text into sentences using repository tokenizer path.

        Args:
            text: Input text.

        Returns:
            Unified status dictionary.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            fn = getattr(self._modules["tokenizers"], "sent_tokenize")
            return self._ok({"sentences": list(fn(text))})
        except Exception as exc:
            return self._err(f"Sentence tokenization failed: {exc}")

    # -------------------------------------------------------------------------
    # Classifier support
    # -------------------------------------------------------------------------
    def instance_naive_bayes_classifier(self, train_set: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Create and train a NaiveBayesClassifier.

        Args:
            train_set: List of (text, label) tuples.

        Returns:
            Unified status dictionary with classifier object.
        """
        if not self._imports_ready:
            return self._err("Imports are not ready.")
        try:
            cls = getattr(self._modules["classifiers"], "NaiveBayesClassifier")
            obj = cls(train_set)
            return self._ok({"type": "NaiveBayesClassifier", "object": obj})
        except Exception as exc:
            return self._err(f"Failed to create NaiveBayesClassifier: {exc}")

    def call_classifier_classify(self, classifier: Any, text: str) -> Dict[str, Any]:
        """
        Classify text with a provided classifier instance.

        Args:
            classifier: A TextBlob-compatible classifier instance.
            text: Text to classify.

        Returns:
            Unified status dictionary with predicted label.
        """
        try:
            label = classifier.classify(text)
            return self._ok({"label": label})
        except Exception as exc:
            return self._err(f"Classification failed: {exc}", "Provide a trained TextBlob classifier instance.")

    # -------------------------------------------------------------------------
    # Generic safe executor
    # -------------------------------------------------------------------------
    def call(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic operation dispatcher for MCP integration.

        Supported operations:
            - health_check
            - download_corpora
            - download_corpora_lite
            - sentiment
            - pos_tags
            - noun_phrases
            - tokenize_words
            - tokenize_sentences
            - detect_language
            - translate

        Args:
            operation: Operation name.
            **kwargs: Operation parameters.

        Returns:
            Unified status dictionary.
        """
        ops = {
            "health_check": lambda: self.health_check(),
            "download_corpora": lambda: self.call_download_corpora(lite=False),
            "download_corpora_lite": lambda: self.call_download_corpora(lite=True),
            "sentiment": lambda: self.call_sentiment(kwargs.get("text", "")),
            "pos_tags": lambda: self.call_pos_tags(kwargs.get("text", "")),
            "noun_phrases": lambda: self.call_noun_phrases(kwargs.get("text", "")),
            "tokenize_words": lambda: self.call_tokenize_words(kwargs.get("text", "")),
            "tokenize_sentences": lambda: self.call_tokenize_sentences(kwargs.get("text", "")),
            "detect_language": lambda: self.call_detect_language(kwargs.get("text", "")),
            "translate": lambda: self.call_translate(
                text=kwargs.get("text", ""),
                to=kwargs.get("to", "en"),
                from_lang=kwargs.get("from_lang"),
            ),
        }
        if operation not in ops:
            return self._err(
                f"Unsupported operation: {operation}",
                f"Supported operations: {', '.join(sorted(ops.keys()))}",
            )
        try:
            return ops[operation]()
        except Exception as exc:
            return self._err(f"Operation execution failed: {exc}")