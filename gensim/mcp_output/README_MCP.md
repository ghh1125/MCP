# Gensim MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps key Gensim capabilities for NLP/ML workflows, focusing on:

- Streaming corpora and dictionary management
- Embedding training and loading (Word2Vec, Doc2Vec, FastText, KeyedVectors)
- Topic modeling (LDA, LSI, TF-IDF, coherence scoring)
- Similarity search (cosine, sparse, soft-cosine, WMD)
- Text preprocessing helpers
- Dataset/model loading via `gensim.downloader`
- Utility script access (format conversion, wiki preprocessing)

It is designed for developer-facing automation where an MCP (Model Context Protocol) client needs reliable, scriptable text modeling operations.

---

## 2) Installation Method

### Requirements

Core dependencies:

- numpy
- scipy
- smart_open

Common optional dependencies (feature-specific):

- pyemd (WMD)
- annoy / nmslib (ANN similarity backends)
- scikit-learn
- Cython
- POT
- requests

### Install

- Basic:
  - `pip install gensim`
- With useful extras in your environment:
  - `pip install numpy scipy smart_open requests scikit-learn`
- If building from source repo:
  - `pip install -e .`

Recommended Python environment: isolated virtualenv/conda, up-to-date pip/setuptools/wheel.

---

## 3) Quick Start

### Load a pretrained model/dataset

Use `gensim.downloader.info()` to inspect resources and `gensim.downloader.load()` to fetch vectors/corpora for immediate use.

### Train embeddings

Create tokenized sentences and train:

- `Word2Vec` for word embeddings
- `Doc2Vec` for document embeddings
- `FastText` for subword-aware embeddings

Then use `KeyedVectors` APIs for fast inference-time similarity and analogy operations.

### Topic modeling flow

Typical pipeline:

1. Build `Dictionary`
2. Convert documents to BoW
3. Train `TfidfModel` / `LdaModel` / `LsiModel`
4. Evaluate topics with `CoherenceModel`

### Similarity retrieval

Use `Similarity`, `MatrixSimilarity`, or `SparseMatrixSimilarity` for index-based retrieval; use `SoftCosineSimilarity`/`WmdSimilarity` for richer semantic matching when dependencies allow.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `preprocess_text`
  - Uses parsing helpers such as `preprocess_string`, stopword/punctuation/numeric stripping, stemming.
- `build_dictionary`
  - Creates/updates `Dictionary` from tokenized documents.
- `serialize_corpus_mm`
  - Stores/loads Matrix Market corpora via `MmCorpus`.
- `train_word2vec`
  - Trains `Word2Vec` model and returns save path/metadata.
- `train_doc2vec`
  - Trains `Doc2Vec` with tagged documents.
- `train_fasttext`
  - Trains `FastText` for OOV-friendly vectors.
- `load_keyedvectors`
  - Loads vectors for inference-only usage.
- `train_lda`
  - Trains `LdaModel` (or multicore variant where configured).
- `train_lsi`
  - Trains `LsiModel`.
- `train_tfidf`
  - Trains `TfidfModel`.
- `compute_coherence`
  - Evaluates topic quality via `CoherenceModel`.
- `build_similarity_index`
  - Builds similarity index (`Similarity`/`MatrixSimilarity`/`SparseMatrixSimilarity`).
- `query_similarity`
  - Runs nearest-neighbor/search queries against built index.
- `downloader_info`
  - Exposes `gensim.downloader.info()`.
- `downloader_load`
  - Exposes `gensim.downloader.load()` for datasets/models.

Script-style service operations (optional):

- `glove_to_word2vec` (`gensim.scripts.glove2word2vec`)
- `word2vec_to_tensorboard` (`gensim.scripts.word2vec2tensor`)
- `segment_wiki`
- `make_wikicorpus`
- `word2vec_standalone`

---

## 5) Common Issues and Notes

- SciPy/NumPy binary compatibility:
  - If import errors occur, recreate env and reinstall pinned compatible versions.
- Large memory usage:
  - Prefer streaming corpora (`TextCorpus` patterns), incremental training, and inference-only `KeyedVectors`.
- Optional feature failures:
  - WMD requires `pyemd`; ANN backends need `annoy`/`nmslib`.
- Performance:
  - Use multicore training where available (`LdaMulticore`, Word2Vec workers).
  - Persist intermediate artifacts (dictionary, corpus, vectors, indexes) to avoid retraining.
- Reproducibility:
  - Fix random seeds and record versions/hyperparameters in endpoint outputs.
- Wikipedia/data preprocessing:
  - Use dedicated script services for large dumps; expect long runtimes and significant disk usage.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/RaRe-Technologies/gensim
- Official docs/tutorials: https://radimrehurek.com/gensim/
- API entry points:
  - `gensim.downloader`
  - `gensim.corpora.Dictionary`
  - `gensim.models` (Word2Vec, Doc2Vec, FastText, LDA/LSI/TF-IDF, CoherenceModel)
  - `gensim.similarities`
- Changelog: `CHANGELOG.md` in repository
- Contribution guide: `CONTRIBUTING.md` in repository