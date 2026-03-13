# Whoosh MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the **Whoosh** full-text search library and exposes practical search/index capabilities through MCP (Model Context Protocol).

Main goals:
- Create and open indexes
- Define schemas and field types
- Add/update/delete documents
- Run parsed queries and structured queries
- Return ranked results, sorting/faceting, highlighting, and spelling suggestions

Repository analyzed: https://github.com/mchaput/whoosh

---

## 2) Installation

### Requirements
- Python 3.x
- `setuptools` (packaging/install)
- Optional: `PyStemmer` (faster stemming in some analyzers)

### Install commands
- Install from PyPI:
  `pip install whoosh`
- Or from source repository:
  `pip install .`

Notes:
- No dedicated `pyproject.toml` was detected in this scan; `setup.py` / `setup.cfg` are present.
- This project is primarily an import-first library (no explicit console entry points detected).

---

## 3) Quick Start

### Minimal flow
1. Create schema (`whoosh.fields.Schema`, `TEXT`, `ID`, etc.)
2. Create index (`whoosh.index.create_in`)
3. Write documents (`ix.writer().add_document(...)`)
4. Search (`ix.searcher().search(...)`)

### Typical core APIs
- Index management: `whoosh.index.create_in`, `open_dir`, `exists_in`
- Writing: `whoosh.writing.IndexWriter`, `BufferedWriter`, `AsyncWriter`
- Query parsing: `whoosh.qparser.QueryParser`, `MultifieldParser`
- Searching: `whoosh.searching.Searcher`, `Results`
- Scoring: `whoosh.scoring.BM25F`, `TF_IDF`
- Sorting/faceting: `whoosh.sorting.FieldFacet`, `Facets`
- Highlighting: `whoosh.highlight.Highlighter`
- Spelling correction: `whoosh.spelling.Corrector` and related classes

---

## 4) Available Tools and Endpoints

Since this repository is a library, MCP (Model Context Protocol) endpoints are typically defined by your wrapper service. Recommended endpoint set:

- `index.create`
  - Create a new index directory with schema.
- `index.open`
  - Open an existing index.
- `index.exists`
  - Check if index exists.
- `documents.add`
  - Add one or many documents.
- `documents.update`
  - Update documents by unique field.
- `documents.delete`
  - Delete by term/query.
- `documents.commit`
  - Commit pending writer changes.
- `search.query`
  - Parse query string and return ranked hits.
- `search.advanced`
  - Execute structured query objects, filters, limits.
- `search.sort`
  - Run search with sortable fields/facets.
- `search.highlight`
  - Return snippets with matched terms highlighted.
- `spelling.suggest`
  - Return correction suggestions for terms/query text.
- `index.optimize` (optional)
  - Force segment merge/optimization when needed.
- `health.ping`
  - Basic service liveness/readiness check.

---

## 5) Common Issues and Notes

- **Locking / concurrent writes**: use one writer per index at a time; prefer `AsyncWriter`/`BufferedWriter` patterns in high-throughput scenarios.
- **Schema stability**: changing schema on existing data can cause compatibility issues; plan migrations carefully.
- **Performance**:
  - Batch writes and commit strategically.
  - Use appropriate analyzers (stemming/stopwords) for your language.
  - Enable sorting/faceting fields explicitly when needed.
- **Memory vs file storage**: file-backed indexes are standard; RAM/memory codecs can help tests and some workloads.
- **Query complexity**: wildcard/fuzzy/regex queries can be expensive on large indexes.
- **Optional dependencies**: stemming speed/behavior may vary if optional stemmer libraries are installed.

---

## 6) References

- Upstream repository: https://github.com/mchaput/whoosh
- Package metadata/build files: `setup.py`, `setup.cfg`
- Core source package: `src/whoosh/`
- Tests for usage patterns: `tests/`
- Existing project README: `README.md`