import os
import sys
from typing import List, Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from flair.data import Sentence
from flair.models import SequenceTagger, TextClassifier
from flair.embeddings import TransformerWordEmbeddings, TransformerDocumentEmbeddings

mcp = FastMCP("flair_mcp_service")


@mcp.tool(
    name="load_sequence_tagger",
    description="Load a Flair sequence tagging model by name or path."
)
def load_sequence_tagger(model_name_or_path: str) -> Dict[str, Any]:
    """
    Load a sequence tagger model.

    Parameters:
        model_name_or_path: Flair model key (e.g., 'ner') or local model path.

    Returns:
        Dict with success/result/error.
    """
    try:
        model = SequenceTagger.load(model_name_or_path)
        result = {
            "model_class": model.__class__.__name__,
            "tag_type": getattr(model, "tag_type", None),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="predict_sequence_tags",
    description="Run sequence tagging prediction on one or more texts."
)
def predict_sequence_tags(
    model_name_or_path: str,
    texts: List[str],
    mini_batch_size: int = 32
) -> Dict[str, Any]:
    """
    Predict token-level/span-level labels for input texts.

    Parameters:
        model_name_or_path: Flair sequence tagger model key or path.
        texts: Input texts to tag.
        mini_batch_size: Batch size used during prediction.

    Returns:
        Dict with success/result/error.
    """
    try:
        model = SequenceTagger.load(model_name_or_path)
        sentences = [Sentence(t) for t in texts]
        model.predict(sentences, mini_batch_size=mini_batch_size)

        output = []
        for s in sentences:
            labels = []
            for label in s.get_labels():
                labels.append(
                    {
                        "value": label.value,
                        "score": float(label.score),
                        "data_point": str(label.data_point),
                    }
                )
            tokens = [{"text": token.text} for token in s]
            output.append({"text": s.to_original_text(), "tokens": tokens, "labels": labels})

        return {"success": True, "result": output, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="load_text_classifier",
    description="Load a Flair text classification model by name or path."
)
def load_text_classifier(model_name_or_path: str) -> Dict[str, Any]:
    """
    Load a text classifier model.

    Parameters:
        model_name_or_path: Flair classifier model key or local path.

    Returns:
        Dict with success/result/error.
    """
    try:
        model = TextClassifier.load(model_name_or_path)
        result = {
            "model_class": model.__class__.__name__,
            "label_type": getattr(model, "label_type", None),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="predict_text_class",
    description="Run text classification prediction on one or more texts."
)
def predict_text_class(
    model_name_or_path: str,
    texts: List[str],
    mini_batch_size: int = 32
) -> Dict[str, Any]:
    """
    Predict document labels for input texts.

    Parameters:
        model_name_or_path: Flair text classifier model key or path.
        texts: Input documents.
        mini_batch_size: Batch size used during prediction.

    Returns:
        Dict with success/result/error.
    """
    try:
        model = TextClassifier.load(model_name_or_path)
        sentences = [Sentence(t) for t in texts]
        model.predict(sentences, mini_batch_size=mini_batch_size)

        output = []
        for s in sentences:
            labels = [{"value": l.value, "score": float(l.score)} for l in s.labels]
            output.append({"text": s.to_original_text(), "labels": labels})

        return {"success": True, "result": output, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="embed_tokens_with_transformer",
    description="Generate token embeddings using Flair TransformerWordEmbeddings."
)
def embed_tokens_with_transformer(
    model_name: str,
    text: str,
    layers: str = "-1",
    subtoken_pooling: str = "first",
    use_context: bool = True
) -> Dict[str, Any]:
    """
    Embed tokens from a single sentence using transformer word embeddings.

    Parameters:
        model_name: Hugging Face model name/path.
        text: Input text to embed.
        layers: Transformer layers selection (Flair format).
        subtoken_pooling: Pooling method for subtokens.
        use_context: Whether to enable context for embeddings.

    Returns:
        Dict with success/result/error.
    """
    try:
        emb = TransformerWordEmbeddings(
            model=model_name,
            layers=layers,
            subtoken_pooling=subtoken_pooling,
            use_context=use_context,
        )
        sentence = Sentence(text)
        emb.embed(sentence)

        result = []
        for token in sentence:
            vector = token.embedding.detach().cpu().tolist()
            result.append({"token": token.text, "embedding_dim": len(vector), "embedding": vector})

        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="embed_document_with_transformer",
    description="Generate document embedding using Flair TransformerDocumentEmbeddings."
)
def embed_document_with_transformer(
    model_name: str,
    text: str,
    layers: str = "-1",
    fine_tune: bool = False
) -> Dict[str, Any]:
    """
    Embed a full document/sentence with transformer document embeddings.

    Parameters:
        model_name: Hugging Face model name/path.
        text: Input text.
        layers: Transformer layers selection (Flair format).
        fine_tune: Whether the embedding is configured for fine-tuning.

    Returns:
        Dict with success/result/error.
    """
    try:
        emb = TransformerDocumentEmbeddings(
            model=model_name,
            layers=layers,
            fine_tune=fine_tune,
        )
        sentence = Sentence(text)
        emb.embed(sentence)

        vector = sentence.embedding.detach().cpu().tolist()
        result = {"embedding_dim": len(vector), "embedding": vector}
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="sentence_tokenize_basic",
    description="Create Flair Sentence objects and return tokenization details."
)
def sentence_tokenize_basic(
    texts: List[str],
    use_tokenizer: bool = True
) -> Dict[str, Any]:
    """
    Tokenize texts with Flair Sentence and return token details.

    Parameters:
        texts: Input texts.
        use_tokenizer: Whether Flair should tokenize text internally.

    Returns:
        Dict with success/result/error.
    """
    try:
        output = []
        for t in texts:
            s = Sentence(t, use_tokenizer=use_tokenizer)
            tokens = [{"text": tok.text, "start_position": tok.start_position} for tok in s]
            output.append({"text": s.to_original_text(), "tokens": tokens})
        return {"success": True, "result": output, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp