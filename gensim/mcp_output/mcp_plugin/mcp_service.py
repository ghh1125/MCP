import os
import sys
from typing import Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from gensim import downloader, utils
from gensim.corpora.dictionary import Dictionary
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models.fasttext import FastText
from gensim.models.keyedvectors import KeyedVectors
from gensim.models.ldamodel import LdaModel
from gensim.models.phrases import Phrases, Phraser
from gensim.models.tfidfmodel import TfidfModel
from gensim.models.word2vec import Word2Vec
from gensim.parsing.preprocessing import preprocess_string
from gensim.similarities.docsim import MatrixSimilarity
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.scripts.word2vec2tensor import word2vec2tensor

mcp = FastMCP("gensim_service")


@mcp.tool(name="preprocess_text", description="Preprocess raw text into normalized tokens.")
def preprocess_text(text: str) -> Dict:
    """
    Preprocess raw text using gensim parsing utilities.

    Parameters:
        text: Input raw text.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        tokens = preprocess_string(text)
        return {"success": True, "result": tokens, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="build_dictionary", description="Build a gensim dictionary from tokenized documents.")
def build_dictionary(documents: List[List[str]]) -> Dict:
    """
    Create a Dictionary from tokenized documents.

    Parameters:
        documents: List of tokenized documents.

    Returns:
        Dictionary with basic dictionary stats.
    """
    try:
        dct = Dictionary(documents)
        result = {
            "num_docs": dct.num_docs,
            "num_pos": dct.num_pos,
            "num_nnz": dct.num_nnz,
            "num_tokens": len(dct),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="train_word2vec", description="Train a Word2Vec model and return sample vectors.")
def train_word2vec(
    sentences: List[List[str]],
    vector_size: int = 100,
    window: int = 5,
    min_count: int = 1,
    epochs: int = 5,
) -> Dict:
    """
    Train a Word2Vec model from tokenized sentences.

    Parameters:
        sentences: Tokenized sentences.
        vector_size: Embedding dimension.
        window: Context window size.
        min_count: Minimum token frequency.
        epochs: Number of training epochs.

    Returns:
        Dictionary with vocabulary size and a few vector previews.
    """
    try:
        model = Word2Vec(
            sentences=sentences,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=1,
            epochs=epochs,
        )
        words = model.wv.index_to_key[:5]
        preview = {w: model.wv[w][:5].tolist() for w in words}
        return {
            "success": True,
            "result": {"vocab_size": len(model.wv), "vector_preview": preview},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="train_fasttext", description="Train a FastText model and return sample vectors.")
def train_fasttext(
    sentences: List[List[str]],
    vector_size: int = 100,
    window: int = 5,
    min_count: int = 1,
    epochs: int = 5,
) -> Dict:
    """
    Train a FastText model from tokenized sentences.

    Parameters:
        sentences: Tokenized sentences.
        vector_size: Embedding dimension.
        window: Context window size.
        min_count: Minimum token frequency.
        epochs: Number of training epochs.

    Returns:
        Dictionary with vocabulary size and sample vectors.
    """
    try:
        model = FastText(
            sentences=sentences,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=1,
            epochs=epochs,
        )
        words = model.wv.index_to_key[:5]
        preview = {w: model.wv[w][:5].tolist() for w in words}
        return {
            "success": True,
            "result": {"vocab_size": len(model.wv), "vector_preview": preview},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="train_doc2vec", description="Train a Doc2Vec model on tokenized documents.")
def train_doc2vec(
    documents: List[List[str]],
    vector_size: int = 50,
    window: int = 5,
    min_count: int = 1,
    epochs: int = 20,
) -> Dict:
    """
    Train a Doc2Vec model.

    Parameters:
        documents: Tokenized documents.
        vector_size: Embedding dimension.
        window: Context window size.
        min_count: Minimum token frequency.
        epochs: Number of epochs.

    Returns:
        Dictionary with document count and first doc vector preview.
    """
    try:
        tagged_docs = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(documents)]
        model = Doc2Vec(
            documents=tagged_docs,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=1,
            epochs=epochs,
        )
        first_vec = model.dv["0"][:5].tolist() if len(tagged_docs) > 0 else []
        return {
            "success": True,
            "result": {"num_documents": len(tagged_docs), "first_doc_vector_preview": first_vec},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="train_tfidf", description="Train TF-IDF model and transform corpus.")
def train_tfidf(documents: List[List[str]]) -> Dict:
    """
    Train a TF-IDF model from tokenized documents.

    Parameters:
        documents: Tokenized documents.

    Returns:
        Dictionary with transformed corpus preview.
    """
    try:
        dct = Dictionary(documents)
        bow_corpus = [dct.doc2bow(doc) for doc in documents]
        tfidf = TfidfModel(bow_corpus)
        transformed = [tfidf[doc] for doc in bow_corpus]
        preview = transformed[:3]
        return {"success": True, "result": {"num_docs": len(transformed), "preview": preview}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="train_lda", description="Train an LDA topic model and return top words.")
def train_lda(
    documents: List[List[str]],
    num_topics: int = 5,
    passes: int = 5,
    random_state: int = 42,
) -> Dict:
    """
    Train an LDA model from tokenized documents.

    Parameters:
        documents: Tokenized documents.
        num_topics: Number of topics.
        passes: Number of corpus passes.
        random_state: Random seed.

    Returns:
        Dictionary with discovered topics.
    """
    try:
        dct = Dictionary(documents)
        corpus = [dct.doc2bow(doc) for doc in documents]
        lda = LdaModel(corpus=corpus, id2word=dct, num_topics=num_topics, passes=passes, random_state=random_state)
        topics = lda.print_topics(num_topics=num_topics, num_words=10)
        return {"success": True, "result": topics, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="build_phrases", description="Detect phrases (bigrams) in tokenized sentences.")
def build_phrases(sentences: List[List[str]], min_count: int = 2, threshold: float = 10.0) -> Dict:
    """
    Train phrase detection model and apply it.

    Parameters:
        sentences: Tokenized sentences.
        min_count: Minimum count for phrase candidates.
        threshold: Phrase scoring threshold.

    Returns:
        Dictionary with transformed sentence preview.
    """
    try:
        phrases_model = Phrases(sentences, min_count=min_count, threshold=threshold)
        phraser = Phraser(phrases_model)
        transformed = [phraser[s] for s in sentences[:5]]
        return {"success": True, "result": transformed, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="compute_similarity_index", description="Build similarity index and score query document.")
def compute_similarity_index(documents: List[List[str]], query: List[str]) -> Dict:
    """
    Create a BoW similarity index and score one query document.

    Parameters:
        documents: Tokenized reference documents.
        query: Tokenized query document.

    Returns:
        Dictionary with similarity scores.
    """
    try:
        dct = Dictionary(documents)
        corpus = [dct.doc2bow(doc) for doc in documents]
        index = MatrixSimilarity(corpus, num_features=len(dct))
        query_bow = dct.doc2bow(query)
        sims = index[query_bow].tolist()
        return {"success": True, "result": sims, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="convert_glove_to_word2vec", description="Convert GloVe vectors file to word2vec format.")
def convert_glove_to_word2vec(glove_input_path: str, word2vec_output_path: str) -> Dict:
    """
    Convert GloVe format file to word2vec text format.

    Parameters:
        glove_input_path: Path to input GloVe file.
        word2vec_output_path: Path to output word2vec file.

    Returns:
        Dictionary with conversion status.
    """
    try:
        num_lines, num_dims = glove2word2vec(glove_input_path, word2vec_output_path)
        return {
            "success": True,
            "result": {"num_lines": int(num_lines), "num_dimensions": int(num_dims)},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="export_word2vec_to_tensorboard", description="Export word2vec model vectors for TensorBoard projector.")
def export_word2vec_to_tensorboard(model_path: str, output_prefix: str, binary: bool = False) -> Dict:
    """
    Export vectors and metadata from a word2vec file for TensorBoard.

    Parameters:
        model_path: Path to word2vec model file.
        output_prefix: Output file prefix.
        binary: Whether input model is in binary format.

    Returns:
        Dictionary with output file paths.
    """
    try:
        model = KeyedVectors.load_word2vec_format(model_path, binary=binary)
        word2vec2tensor(model, output_prefix)
        return {
            "success": True,
            "result": {
                "tensor_path": f"{output_prefix}_tensor.tsv",
                "metadata_path": f"{output_prefix}_metadata.tsv",
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="list_gensim_datasets", description="List available datasets/models in gensim downloader.")
def list_gensim_datasets(name_filter: Optional[str] = None) -> Dict:
    """
    List available resources from gensim-data index.

    Parameters:
        name_filter: Optional substring filter.

    Returns:
        Dictionary with matched dataset/model names.
    """
    try:
        info = downloader.info()
        names = list(info.get("models", {}).keys()) + list(info.get("corpora", {}).keys())
        if name_filter:
            names = [n for n in names if name_filter.lower() in n.lower()]
        return {"success": True, "result": sorted(names), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="tokenize_text", description="Tokenize text using gensim simple_preprocess.")
def tokenize_text(text: str, deacc: bool = True, min_len: int = 2, max_len: int = 15) -> Dict:
    """
    Tokenize text into lowercase tokens.

    Parameters:
        text: Input text.
        deacc: Remove accent marks and punctuation.
        min_len: Minimum token length.
        max_len: Maximum token length.

    Returns:
        Dictionary with token list.
    """
    try:
        tokens = utils.simple_preprocess(text, deacc=deacc, min_len=min_len, max_len=max_len)
        return {"success": True, "result": tokens, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp