import os
import sys
source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
sys.path.insert(0, source_path)

import traceback
from typing import Any, Dict, Optional


class Adapter:
    """
    MCP Import Mode Adapter for the vaderSentiment repository.

    This adapter attempts to import and expose core sentiment-analysis features
    from:
      - vaderSentiment.vaderSentiment

    It provides:
      - Import-mode execution when repository source is available.
      - Graceful fallback responses when import is unavailable.
      - Unified response payloads with a required 'status' field.
    """

    # -------------------------------------------------------------------------
    # Initialization and Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and load target module symbols.

        Attributes:
            mode (str): Operating mode. Fixed to "import" per requirements.
            available (bool): Whether import-mode features are available.
            import_error (Optional[str]): Import failure details if unavailable.
        """
        self.mode = "import"
        self.available = False
        self.import_error: Optional[str] = None

        self._SentimentIntensityAnalyzer = None
        self._make_lex_dict = None
        self._SentiText = None
        self._allcap_differential = None
        self._scalar_inc_dec = None
        self._negated = None
        self._normalize = None
        self._boost_ep_amplifier = None
        self._sift_sentiment_scores = None
        self._score_valence = None

        self._load_imports()

    def _load_imports(self) -> None:
        """Load full package-path imports from repository source with fallback."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._SentimentIntensityAnalyzer = SentimentIntensityAnalyzer

            # Optional utility-level symbols from the module (best-effort).
            try:
                from vaderSentiment.vaderSentiment import make_lex_dict
                self._make_lex_dict = make_lex_dict
            except Exception:
                self._make_lex_dict = None

            try:
                from vaderSentiment.vaderSentiment import SentiText
                self._SentiText = SentiText
            except Exception:
                self._SentiText = None

            try:
                from vaderSentiment.vaderSentiment import allcap_differential
                self._allcap_differential = allcap_differential
            except Exception:
                self._allcap_differential = None

            try:
                from vaderSentiment.vaderSentiment import scalar_inc_dec
                self._scalar_inc_dec = scalar_inc_dec
            except Exception:
                self._scalar_inc_dec = None

            try:
                from vaderSentiment.vaderSentiment import negated
                self._negated = negated
            except Exception:
                self._negated = None

            try:
                from vaderSentiment.vaderSentiment import normalize
                self._normalize = normalize
            except Exception:
                self._normalize = None

            try:
                from vaderSentiment.vaderSentiment import _amplify_ep as boost_ep_amplifier
                self._boost_ep_amplifier = boost_ep_amplifier
            except Exception:
                self._boost_ep_amplifier = None

            try:
                from vaderSentiment.vaderSentiment import _sift_sentiment_scores
                self._sift_sentiment_scores = _sift_sentiment_scores
            except Exception:
                self._sift_sentiment_scores = None

            try:
                from vaderSentiment.vaderSentiment import score_valence
                self._score_valence = score_valence
            except Exception:
                self._score_valence = None

            self.available = True
            self.import_error = None

        except Exception as exc:
            self.available = False
            self.import_error = (
                f"Failed to import vaderSentiment from local source. "
                f"Ensure repository files exist under source/. Root cause: {exc}"
            )

    # -------------------------------------------------------------------------
    # Unified Response Helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, error: Optional[str] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error:
            payload["error"] = error
        if hint:
            payload["hint"] = hint
        return payload

    def _import_unavailable(self) -> Dict[str, Any]:
        return self._fail(
            message="Import mode is unavailable.",
            error=self.import_error,
            hint="Verify source/vaderSentiment/vaderSentiment.py exists and dependencies are intact."
        )

    # -------------------------------------------------------------------------
    # Health and Capability Methods
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter and import-mode health.

        Returns:
            dict: Unified status payload with availability and import diagnostics.
        """
        if self.available:
            return self._ok(
                data={
                    "available": True,
                    "module": "vaderSentiment.vaderSentiment",
                    "class": "SentimentIntensityAnalyzer"
                },
                message="Adapter is ready in import mode."
            )
        return self._import_unavailable()

    # -------------------------------------------------------------------------
    # Class Instance Methods
    # -------------------------------------------------------------------------
    def create_sentiment_intensity_analyzer(
        self,
        lexicon_file: Optional[str] = None,
        emoji_lexicon: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an instance of SentimentIntensityAnalyzer.

        Parameters:
            lexicon_file (Optional[str]): Path to VADER lexicon file. If None, defaults are used.
            emoji_lexicon (Optional[str]): Path to emoji lexicon file. If None, defaults are used.

        Returns:
            dict:
                On success: {'status': 'success', 'data': {'instance': <object>}, ...}
                On error: unified error payload with actionable hint.
        """
        if not self.available or self._SentimentIntensityAnalyzer is None:
            return self._import_unavailable()

        try:
            kwargs = {}
            if lexicon_file is not None:
                kwargs["lexicon_file"] = lexicon_file
            if emoji_lexicon is not None:
                kwargs["emoji_lexicon"] = emoji_lexicon

            instance = self._SentimentIntensityAnalyzer(**kwargs) if kwargs else self._SentimentIntensityAnalyzer()
            return self._ok(data={"instance": instance}, message="SentimentIntensityAnalyzer instance created.")
        except Exception as exc:
            return self._fail(
                message="Failed to create SentimentIntensityAnalyzer instance.",
                error=str(exc),
                hint="Check lexicon file paths and file encoding."
            )

    # -------------------------------------------------------------------------
    # Core Public Function Calls
    # -------------------------------------------------------------------------
    def call_polarity_scores(
        self,
        text: str,
        analyzer: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Compute VADER sentiment scores for input text.

        Parameters:
            text (str): Input text to analyze.
            analyzer (Optional[Any]): Existing SentimentIntensityAnalyzer instance.
                                      If None, a new instance will be created.

        Returns:
            dict: Unified status payload containing sentiment scores:
                  {'neg': float, 'neu': float, 'pos': float, 'compound': float}
        """
        if not self.available or self._SentimentIntensityAnalyzer is None:
            return self._import_unavailable()

        try:
            if not isinstance(text, str):
                return self._fail(
                    message="Invalid input type for text.",
                    error="Parameter 'text' must be a string.",
                    hint="Pass plain text such as 'This is great!'."
                )

            inst = analyzer if analyzer is not None else self._SentimentIntensityAnalyzer()
            scores = inst.polarity_scores(text)
            return self._ok(data=scores, message="Sentiment scores computed successfully.")
        except Exception as exc:
            return self._fail(
                message="Failed to compute polarity scores.",
                error=str(exc),
                hint="Ensure text is non-empty and analyzer instance is valid."
            )

    # -------------------------------------------------------------------------
    # Optional/Internal Utility Calls (Best-Effort Exposure)
    # -------------------------------------------------------------------------
    def call_make_lex_dict(self) -> Dict[str, Any]:
        """
        Call module-level make_lex_dict function if available.

        Returns:
            dict: Unified status payload with lexicon dictionary or graceful fallback error.
        """
        if not self.available:
            return self._import_unavailable()
        if self._make_lex_dict is None:
            return self._fail(
                message="Function make_lex_dict is not publicly available in this module version.",
                hint="Use create_sentiment_intensity_analyzer and inspect instance.lexicon instead."
            )
        try:
            result = self._make_lex_dict()
            return self._ok(data=result, message="Lexicon dictionary generated.")
        except Exception as exc:
            return self._fail(message="Failed to call make_lex_dict.", error=str(exc))

    def call_normalize(self, score: float, alpha: float = 15.0) -> Dict[str, Any]:
        """
        Normalize a raw sentiment score using VADER normalize function, if available.

        Parameters:
            score (float): Raw sentiment score.
            alpha (float): Normalization alpha parameter.

        Returns:
            dict: Unified status payload with normalized score.
        """
        if not self.available:
            return self._import_unavailable()
        if self._normalize is None:
            return self._fail(
                message="Function normalize is not publicly available in this module version.",
                hint="Use call_polarity_scores for supported normalized compound score."
            )
        try:
            result = self._normalize(score, alpha=alpha)
            return self._ok(data={"normalized": result}, message="Score normalized.")
        except Exception as exc:
            return self._fail(message="Failed to call normalize.", error=str(exc))

    def diagnostics(self) -> Dict[str, Any]:
        """
        Provide adapter diagnostics and symbol availability report.

        Returns:
            dict: Unified status payload with internal availability details.
        """
        try:
            data = {
                "available": self.available,
                "import_error": self.import_error,
                "symbols": {
                    "SentimentIntensityAnalyzer": self._SentimentIntensityAnalyzer is not None,
                    "make_lex_dict": self._make_lex_dict is not None,
                    "SentiText": self._SentiText is not None,
                    "allcap_differential": self._allcap_differential is not None,
                    "scalar_inc_dec": self._scalar_inc_dec is not None,
                    "negated": self._negated is not None,
                    "normalize": self._normalize is not None,
                    "_amplify_ep": self._boost_ep_amplifier is not None,
                    "_sift_sentiment_scores": self._sift_sentiment_scores is not None,
                    "score_valence": self._score_valence is not None,
                },
            }
            return self._ok(data=data, message="Diagnostics collected.")
        except Exception as exc:
            return self._fail(
                message="Failed to collect diagnostics.",
                error=f"{exc}\n{traceback.format_exc()}",
                hint="Retry after verifying source integrity."
            )