# Whoosh MCP (Model Context Protocol) Service README

## 1) Project Introduction

This project exposes core Whoosh full-text search capabilities as an MCP (Model Context Protocol) service for AI/tooling workflows.  
It focuses on practical indexing and query operations:

- Create/open indexes
- Define schemas and analyzers
- Add/update/delete documents
- Parse user query strings
- Execute ranked search
- Sort/facet results
- Highlight snippets
- Provide spelling suggestions

Core Whoosh modules used include `whoosh.index`, `whoosh.fields`, `whoosh.writing`, `whoosh.searching`, `whoosh.qparser`, `whoosh.query`, `whoosh.scoring`, `whoosh.highlight`, `whoosh.sorting`, and `whoosh.spelling`.

---

## 2) Installation Method

### Requirements
- Python 3.x
- Standard library dependencies (no clearly required third-party runtime package identified from scanned metadata)

### Install from source
- Clone repository: `https://github.com/mchaput/whoosh`
- Install locally (editable): `pip install -e .`
- Or standard install: `pip install .`

### Verify
- Run tests (optional): `pytest`
- Import check: `import whoosh`

---

## 3) Quick Start

Typical MCP (Model Context Protocol) workflow:

1. Create or open an index (`whoosh.index.create_in`, `open_dir`)
2. Define schema (`whoosh.fields.Schema` + field types like `TEXT`, `ID`, `NUMERIC`)
3. Write documents (`IndexWriter` / `AsyncWriter` / `BufferedWriter`)
4. Parse query text (`QueryParser` / `MultifieldParser`)
5. Search (`Searcher.search`) with optional ranking (`BM25F`), sorting/faceting, highlighting
6. Return structured results to MCP (Model Context Protocol) clients

Main callable APIs:
- Index lifecycle: `create_in`, `open_dir`, `exists_in`
- Query parsing: `QueryParser`, `MultifieldParser`, `SimpleParser`
- Query objects: `Term`, `Phrase`, `Wildcard`, `FuzzyTerm`
- Scoring: `BM25F`, `TF_IDF`
- Results handling: `Results`, `Hit`
- Highlighting: `Highlighter` / `highlight`
- Sorting/faceting: `FieldFacet`, `ScoreFacet`, `MultiFacet`
- Spelling: `SpellChecker`, `ReaderCorrector`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `index.create`  
  Create a new index directory with a schema.

- `index.open`  
  Open an existing index.

- `index.exists`  
  Check whether an index exists at a path.

- `documents.add`  
  Add one or more documents and commit.

- `documents.update`  
  Update documents by unique key field(s).

- `documents.delete`  
  Delete documents by term/query.

- `query.parse`  
  Convert user query string into Whoosh query object.

- `search.execute`  
  Run query, return ranked hits, total count, optional pagination.

- `search.sort`  
  Execute search with sorting/facet options.

- `search.highlight`  
  Return highlighted snippets for matched fields.

- `spelling.suggest`  
  Return spelling corrections/suggestions from index terms.

- `maintenance.make_checkpoint`  
  Wrapper around `scripts/make_checkpoint.py` for checkpoint generation.

- `maintenance.read_checkpoint`  
  Wrapper around `scripts/read_checkpoint.py` for checkpoint inspection.

---

## 5) Common Issues and Notes

- Schema stability matters: changing field definitions after indexing can require reindexing.
- Writer lifecycle: always commit/close writers to avoid lock/file consistency issues.
- Concurrency: use `AsyncWriter`/`BufferedWriter` carefully in multi-threaded ingestion workloads.
- Query parser behavior: user-entered syntax can produce unexpected query trees; validate and sanitize inputs.
- Performance:
  - Prefer batch writes over frequent single-doc commits.
  - Tune analyzer choice and scoring model (`BM25F` is a common default).
  - Large indexes may need facet/sort design optimization.
- Environment:
  - Local filesystem permissions must allow index file creation and locking.
  - Keep Python runtime version consistent across indexing/search nodes.
- Dependency metadata in scan was incomplete; validate packaging/install behavior in your target environment.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/mchaput/whoosh
- Source package root: `src/whoosh/`
- Tests/examples: `tests/`, `benchmark/`, `stress/`
- Maintenance scripts:
  - `scripts/make_checkpoint.py`
  - `scripts/read_checkpoint.py`
- Original project README: `README.md` in repository root