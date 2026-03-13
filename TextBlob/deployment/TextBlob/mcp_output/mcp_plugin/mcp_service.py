import os
import sys
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from textblob import TextBlob
from textblob.blob import Word, WordList
from textblob.classifiers import NaiveBayesClassifier
from textblob.download_corpora import download_all as _download_all_corpora
from textblob.download_corpora import download_lite as _download_lite_corpora

mcp = FastMCP("textblob_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="analyze_text", description="Run comprehensive NLP analysis on input text.")
def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text using TextBlob core features.

    Parameters:
    - text: Input text to analyze.

    Returns:
    - Standard response dictionary with:
      - success: Whether execution succeeded.
      - result: Analysis output including tokens, noun phrases, tags, sentiment, and ngrams.
      - error: Error message if execution failed.
    """
    try:
        blob = TextBlob(text)
        result = {
            "raw": str(blob),
            "words": [str(w) for w in blob.words],
            "sentences": [str(s) for s in blob.sentences],
            "noun_phrases": list(blob.noun_phrases),
            "pos_tags": [(w, t) for w, t in blob.tags],
            "sentiment": {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
            },
            "ngrams_2": [[str(x) for x in ng] for ng in blob.ngrams(n=2)],
            "ngrams_3": [[str(x) for x in ng] for ng in blob.ngrams(n=3)],
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="correct_text", description="Spell-correct input text.")
def correct_text(text: str) -> Dict[str, Any]:
    """
    Correct spelling in text.

    Parameters:
    - text: Input text.

    Returns:
    - Standard response dictionary with corrected text.
    """
    try:
        corrected = str(TextBlob(text).correct())
        return _ok({"corrected_text": corrected})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="translate_text", description="Translate text to a target language.")
def translate_text(text: str, to_language: str = "en", from_language: Optional[str] = None) -> Dict[str, Any]:
    """
    Translate text using TextBlob translation support.

    Parameters:
    - text: Input text.
    - to_language: Destination language code.
    - from_language: Optional source language code.

    Returns:
    - Standard response dictionary with translated text.
    """
    try:
        blob = TextBlob(text)
        translated = blob.translate(to=to_language, from_lang=from_language)
        return _ok({"translated_text": str(translated)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="detect_language", description="Detect language of input text.")
def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect language for the provided text.

    Parameters:
    - text: Input text.

    Returns:
    - Standard response dictionary with detected language code.
    """
    try:
        lang = TextBlob(text).detect_language()
        return _ok({"language": lang})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="word_insights", description="Get lexical insights for a single word.")
def word_insights(word: str) -> Dict[str, Any]:
    """
    Compute lexical features for a single word.

    Parameters:
    - word: Input word.

    Returns:
    - Standard response dictionary with singularize/pluralize/lemmatize/stem/definitions/synsets.
    """
    try:
        w = Word(word)
        synsets = []
        for syn in w.synsets:
            synsets.append(
                {
                    "name": syn.name(),
                    "definition": syn.definition(),
                    "examples": list(syn.examples()),
                    "lemmas": [l.name() for l in syn.lemmas()],
                }
            )
        result = {
            "word": word,
            "singularize": str(w.singularize()),
            "pluralize": str(w.pluralize()),
            "lemmatize": str(w.lemmatize()),
            "stem": str(w.stem()),
            "spellcheck": [(cand, conf) for cand, conf in w.spellcheck()],
            "definitions": list(w.definitions),
            "synsets": synsets,
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="sentiment_assessments", description="Get sentiment polarity/subjectivity and sentence-level assessments.")
def sentiment_assessments(text: str) -> Dict[str, Any]:
    """
    Provide global and sentence-level sentiment.

    Parameters:
    - text: Input text.

    Returns:
    - Standard response dictionary with overall and per-sentence sentiment scores.
    """
    try:
        blob = TextBlob(text)
        sentence_scores: List[Dict[str, Any]] = []
        for s in blob.sentences:
            sentence_scores.append(
                {
                    "sentence": str(s),
                    "polarity": s.sentiment.polarity,
                    "subjectivity": s.sentiment.subjectivity,
                }
            )
        return _ok(
            {
                "overall": {
                    "polarity": blob.sentiment.polarity,
                    "subjectivity": blob.sentiment.subjectivity,
                },
                "sentences": sentence_scores,
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="train_naive_bayes", description="Train and evaluate a Naive Bayes text classifier.")
def train_naive_bayes(
    train_data: List[Tuple[str, str]],
    test_data: Optional[List[Tuple[str, str]]] = None
) -> Dict[str, Any]:
    """
    Train a NaiveBayesClassifier and optionally evaluate it.

    Parameters:
    - train_data: Labeled examples [(text, label), ...].
    - test_data: Optional labeled test examples [(text, label), ...].

    Returns:
    - Standard response dictionary with class labels and optional accuracy.
    """
    try:
        clf = NaiveBayesClassifier(train_data)
        result: Dict[str, Any] = {
            "labels": list(clf.labels()),
        }
        if test_data:
            result["accuracy"] = float(clf.accuracy(test_data))
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="classify_text_nb", description="Classify text using ad-hoc Naive Bayes training data.")
def classify_text_nb(train_data: List[Tuple[str, str]], text: str) -> Dict[str, Any]:
    """
    Train a NaiveBayesClassifier from provided data and classify one text.

    Parameters:
    - train_data: Labeled examples [(text, label), ...].
    - text: Text to classify.

    Returns:
    - Standard response dictionary with predicted label and probability distribution.
    """
    try:
        clf = NaiveBayesClassifier(train_data)
        prob = clf.prob_classify(text)
        dist = {label: float(prob.prob(label)) for label in clf.labels()}
        return _ok({"label": clf.classify(text), "probabilities": dist})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="download_corpora", description="Download TextBlob/NTLK corpora (full or lite).")
def download_corpora(lite: bool = True) -> Dict[str, Any]:
    """
    Download required corpora for TextBlob features.

    Parameters:
    - lite: If True, download reduced corpora set; otherwise download full set.

    Returns:
    - Standard response dictionary with completion status.
    """
    try:
        if lite:
            _download_lite_corpora()
            mode = "lite"
        else:
            _download_all_corpora()
            mode = "full"
        return _ok({"downloaded": True, "mode": mode})
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()