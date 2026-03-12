import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for TextBlob.

    This adapter prioritizes direct Python imports from the local source tree.
    If imports fail, it gracefully falls back to CLI guidance for corpus download.
    All public methods return a unified response dictionary with a `status` field.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt to load core modules.

        Returns:
            None
        """
        self.mode = "import"
        self._loaded = False
        self._import_errors: List[str] = []

        self._mod_textblob = None
        self._mod_blob = None
        self._mod_classifiers = None
        self._mod_tokenizers = None
        self._mod_np_extractors = None
        self._mod_taggers = None
        self._mod_parsers = None
        self._mod_sentiments = None
        self._mod_formats = None
        self._mod_inflect = None
        self._mod_translate = None
        self._mod_download_corpora = None

        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        modules = [
            "textblob",
            "textblob.blob",
            "textblob.classifiers",
            "textblob.tokenizers",
            "textblob.np_extractors",
            "textblob.taggers",
            "textblob.parsers",
            "textblob.sentiments",
            "textblob.formats",
            "textblob.inflect",
            "textblob.translate",
            "textblob.download_corpora",
        ]

        for mod_name in modules:
            try:
                mod = importlib.import_module(mod_name)
                setattr(self, f"_mod_{mod_name.replace('.', '_')}", mod)
            except Exception as e:
                self._import_errors.append(f"{mod_name}: {e}")

        self._mod_textblob = getattr(self, "_mod_textblob", None)
        self._mod_blob = getattr(self, "_mod_textblob_blob", None)
        self._mod_classifiers = getattr(self, "_mod_textblob_classifiers", None)
        self._mod_tokenizers = getattr(self, "_mod_textblob_tokenizers", None)
        self._mod_np_extractors = getattr(self, "_mod_textblob_np_extractors", None)
        self._mod_taggers = getattr(self, "_mod_textblob_taggers", None)
        self._mod_parsers = getattr(self, "_mod_textblob_parsers", None)
        self._mod_sentiments = getattr(self, "_mod_textblob_sentiments", None)
        self._mod_formats = getattr(self, "_mod_textblob_formats", None)
        self._mod_inflect = getattr(self, "_mod_textblob_inflect", None)
        self._mod_translate = getattr(self, "_mod_textblob_translate", None)
        self._mod_download_corpora = getattr(self, "_mod_textblob_download_corpora", None)

        self._loaded = self._mod_textblob is not None and self._mod_blob is not None

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter health and import readiness.

        Returns:
            dict: Unified response with import readiness and actionable guidance.
        """
        if self._loaded:
            return self._ok(
                {
                    "loaded": True,
                    "import_errors": self._import_errors,
                    "available_modules": [
                        m for m in [
                            "textblob",
                            "textblob.blob",
                            "textblob.classifiers",
                            "textblob.tokenizers",
                            "textblob.np_extractors",
                            "textblob.taggers",
                            "textblob.parsers",
                            "textblob.sentiments",
                            "textblob.formats",
                            "textblob.inflect",
                            "textblob.translate",
                            "textblob.download_corpora",
                        ] if importlib.util.find_spec(m) is not None
                    ],
                },
                message="Adapter is healthy and import mode is active.",
            )
        return self._err(
            "Import mode is not fully available.",
            guidance=(
                "Ensure source code is present under the expected 'source' directory, "
                "and install runtime dependency 'nltk'. "
                "Then run: python -m textblob.download_corpora"
            ),
            details="; ".join(self._import_errors) if self._import_errors else None,
        )

    # -------------------------------------------------------------------------
    # Core Object Constructors (Class instance methods)
    # -------------------------------------------------------------------------
    def create_textblob(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a textblob.blob.TextBlob instance.

        Parameters:
            text (str): Input text content.
            **kwargs: Additional keyword arguments forwarded to TextBlob constructor.

        Returns:
            dict: status + created object or error details.
        """
        if not self._mod_blob:
            return self._err("textblob.blob is unavailable.", guidance="Run health_check() and verify imports.")
        try:
            cls = getattr(self._mod_blob, "TextBlob")
            obj = cls(text, **kwargs)
            return self._ok({"object": obj}, message="TextBlob instance created.")
        except Exception as e:
            return self._err("Failed to create TextBlob instance.", details=str(e))

    def create_sentence(self, sentence: str, **kwargs: Any) -> Dict[str, Any]:
        if not self._mod_blob:
            return self._err("textblob.blob is unavailable.")
        try:
            cls = getattr(self._mod_blob, "Sentence")
            obj = cls(sentence, **kwargs)
            return self._ok({"object": obj}, message="Sentence instance created.")
        except Exception as e:
            return self._err("Failed to create Sentence instance.", details=str(e))

    def create_word(self, word: str, **kwargs: Any) -> Dict[str, Any]:
        if not self._mod_blob:
            return self._err("textblob.blob is unavailable.")
        try:
            cls = getattr(self._mod_blob, "Word")
            obj = cls(word, **kwargs)
            return self._ok({"object": obj}, message="Word instance created.")
        except Exception as e:
            return self._err("Failed to create Word instance.", details=str(e))

    def create_blobber(self, **kwargs: Any) -> Dict[str, Any]:
        if not self._mod_blob:
            return self._err("textblob.blob is unavailable.")
        try:
            cls = getattr(self._mod_blob, "Blobber")
            obj = cls(**kwargs)
            return self._ok({"object": obj}, message="Blobber instance created.")
        except Exception as e:
            return self._err("Failed to create Blobber instance.", details=str(e))

    # -------------------------------------------------------------------------
    # Core NLP Operations
    # -------------------------------------------------------------------------
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Run common TextBlob NLP operations on input text.

        Parameters:
            text (str): Input text.

        Returns:
            dict: status + tokens, tags, noun_phrases, sentiment, polarity, subjectivity.
        """
        try:
            created = self.create_textblob(text)
            if created["status"] != "success":
                return created
            blob = created["object"]
            return self._ok(
                {
                    "words": [str(w) for w in blob.words],
                    "sentences": [str(s) for s in blob.sentences],
                    "noun_phrases": list(blob.noun_phrases),
                    "tags": list(blob.tags),
                    "sentiment": {"polarity": blob.sentiment.polarity, "subjectivity": blob.sentiment.subjectivity},
                },
                message="Text analysis complete.",
            )
        except Exception as e:
            return self._err("Failed to analyze text.", details=str(e))

    def detect_language(self, text: str) -> Dict[str, Any]:
        try:
            created = self.create_textblob(text)
            if created["status"] != "success":
                return created
            lang = created["object"].detect_language()
            return self._ok({"language": lang}, message="Language detection complete.")
        except Exception as e:
            return self._err(
                "Language detection failed.",
                guidance="This may require internet access and external service availability.",
                details=str(e),
            )

    def translate_text(self, text: str, to: str = "en", from_lang: Optional[str] = None) -> Dict[str, Any]:
        try:
            created = self.create_textblob(text)
            if created["status"] != "success":
                return created
            translated = created["object"].translate(from_lang=from_lang, to=to)
            return self._ok({"translated_text": str(translated)}, message="Translation complete.")
        except Exception as e:
            return self._err(
                "Translation failed.",
                guidance="Ensure internet access is available and retry later.",
                details=str(e),
            )

    # -------------------------------------------------------------------------
    # Tokenization / Parsing / Tagging / Sentiment Components
    # -------------------------------------------------------------------------
    def tokenize_words(self, text: str) -> Dict[str, Any]:
        try:
            if not self._mod_tokenizers:
                return self._err("textblob.tokenizers is unavailable.")
            fn = getattr(self._mod_tokenizers, "word_tokenize")
            return self._ok({"tokens": list(fn(text))}, message="Word tokenization complete.")
        except Exception as e:
            return self._err("Word tokenization failed.", details=str(e))

    def tokenize_sentences(self, text: str) -> Dict[str, Any]:
        try:
            if not self._mod_tokenizers:
                return self._err("textblob.tokenizers is unavailable.")
            fn = getattr(self._mod_tokenizers, "sent_tokenize")
            return self._ok({"sentences": list(fn(text))}, message="Sentence tokenization complete.")
        except Exception as e:
            return self._err("Sentence tokenization failed.", details=str(e))

    # -------------------------------------------------------------------------
    # Classifier Support
    # -------------------------------------------------------------------------
    def create_naive_bayes_classifier(self, train_set: List[Tuple[str, str]]) -> Dict[str, Any]:
        try:
            if not self._mod_classifiers:
                return self._err("textblob.classifiers is unavailable.")
            cls = getattr(self._mod_classifiers, "NaiveBayesClassifier")
            obj = cls(train_set)
            return self._ok({"object": obj}, message="NaiveBayesClassifier instance created.")
        except Exception as e:
            return self._err("Failed to create NaiveBayesClassifier.", details=str(e))

    def classify_with_naive_bayes(self, train_set: List[Tuple[str, str]], text: str) -> Dict[str, Any]:
        try:
            created = self.create_naive_bayes_classifier(train_set)
            if created["status"] != "success":
                return created
            clf = created["object"]
            label = clf.classify(text)
            prob_dist = clf.prob_classify(text)
            probs = {lbl: prob_dist.prob(lbl) for lbl in prob_dist.samples()}
            return self._ok({"label": label, "probabilities": probs}, message="Classification complete.")
        except Exception as e:
            return self._err("Classification failed.", details=str(e))

    # -------------------------------------------------------------------------
    # Corpora / CLI Fallback
    # -------------------------------------------------------------------------
    def download_corpora(self, lite: bool = False) -> Dict[str, Any]:
        """
        Download TextBlob/NLTK corpora via import mode when possible.
        Falls back to CLI guidance if import path is unavailable.

        Parameters:
            lite (bool): Whether to run lite corpus download path if supported.

        Returns:
            dict: status + execution metadata or fallback guidance.
        """
        try:
            if self._mod_download_corpora:
                if lite and hasattr(self._mod_download_corpora, "download_lite"):
                    self._mod_download_corpora.download_lite()
                elif hasattr(self._mod_download_corpora, "download_all"):
                    self._mod_download_corpora.download_all()
                elif hasattr(self._mod_download_corpora, "main"):
                    self._mod_download_corpora.main()
                else:
                    return self._err(
                        "No callable download function found in textblob.download_corpora.",
                        guidance="Run CLI: python -m textblob.download_corpora",
                    )
                return self._ok(message="Corpora download invoked successfully.")
            return self._err(
                "Import for textblob.download_corpora is unavailable.",
                guidance="Run CLI fallback: python -m textblob.download_corpora",
            )
        except Exception as e:
            return self._err(
                "Corpora download failed.",
                guidance="Try CLI fallback: python -m textblob.download_corpora",
                details=str(e),
            )

    # -------------------------------------------------------------------------
    # Generic Invocation Utilities
    # -------------------------------------------------------------------------
    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from a TextBlob module path.

        Parameters:
            module_path (str): Full module path (e.g., 'textblob.tokenizers').
            function_name (str): Function name in module.
            *args: Positional args for function.
            **kwargs: Keyword args for function.

        Returns:
            dict: status + result or detailed error.
        """
        try:
            mod = importlib.import_module(module_path)
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"Called {module_path}.{function_name} successfully.")
        except Exception as e:
            return self._err(
                f"Failed to call function {module_path}.{function_name}.",
                guidance="Verify module path, function name, and arguments.",
                details=f"{e}\n{traceback.format_exc()}",
            )