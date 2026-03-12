# Deep Searcher MCP (Model Context Protocol) Service README

## 1) Project Introduction

Deep Searcher is a configurable RAG/deep-retrieval framework that supports:
- Multi-step search agents (`DeepSearch`, `ChainOfRAG`, `NaiveRAG`)
- Offline ingestion (load/split/embed/index documents)
- Online query (retrieve + generate answers)
- Pluggable providers for LLMs, embeddings, vector databases, file loaders, and web crawlers

This MCP (Model Context Protocol) service wraps these capabilities into practical service endpoints so developers can integrate ingestion and query workflows into AI applications with minimal custom orchestration.

---

## 2) Installation Method

### Requirements
- Python 3.10+
- `pip`
- A configured vector DB + embedding + LLM provider

### Install
- `pip install deepsearcher` (if using published package)
- or clone repository and install locally:
  - `pip install -e .`

### Configure
- Copy/edit `deepsearcher/config.yaml`
- Set provider credentials via environment variables (examples):
  - OpenAI / Anthropic / Gemini / Bedrock / Ollama / etc.
  - Qdrant / Milvus / Azure AI Search / Oracle vector stack
- Install optional provider SDKs only for the backends you use.

---

## 3) Quick Start

### Minimal workflow
1. Load configuration
2. Run offline ingestion (`offline_load`) for local files or crawled content
3. Run online query (`online_query`) for user questions

Example flow (conceptual):
- Initialize `Configuration`
- Call `offline_load(...)` to index corpus
- Call `online_query(...)` to get final answer + retrieved context

Recommended first path:
- Use `NaiveRAG` for baseline simplicity
- Move to `DeepSearch` or `ChainOfRAG` for more advanced multi-hop reasoning

You can also run via CLI entry (`deepsearcher`) or `python main.py` depending on deployment style.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `health_check`
  - Verify service status and active backend connectivity.

- `config_validate`
  - Validate YAML/provider configuration before ingestion/query.

- `ingest_offline`
  - Wrapper over `offline_load`; ingests files/web data into vector DB.

- `query_online`
  - Wrapper over `online_query`; retrieves and generates answer for a query.

- `agent_run_deep_search`
  - Execute `DeepSearch` agent for multi-step retrieval and synthesis.

- `agent_run_chain_of_rag`
  - Execute `ChainOfRAG` iterative retrieval-reasoning flow.

- `agent_run_naive_rag`
  - Execute `NaiveRAG` low-latency baseline flow.

- `list_providers`
  - Return available LLM/embedding/vector DB/file loader/web crawler backends.

- `index_stats`
  - Return collection/index metadata (document count, dimensions, status).

- `reindex_collection`
  - Rebuild embeddings/index for a selected collection.

---

## 5) Common Issues and Notes

- Provider mismatch: Ensure embedding dimension matches vector DB index schema.
- Missing optional dependencies: Install only the SDKs for enabled backends.
- Credential issues: Most runtime failures are API key/endpoint/region misconfiguration.
- Throughput/latency:
  - Use batching for ingestion
  - Tune chunk size/splitter strategy
  - Start with `NaiveRAG` if latency is critical
- Crawler dependencies (`firecrawl`, `crawl4ai`, `docling`, `jina`) are optional and may require extra setup.
- For production MCP (Model Context Protocol) service deployment, add:
  - request timeouts
  - retries/circuit breakers
  - structured logging
  - per-provider rate limiting

---

## 6) Reference Links / Documentation

- Repository: https://github.com/zilliztech/deep-searcher
- Main docs index: `docs/index.md`
- Configuration docs:
  - `docs/configuration/llm.md`
  - `docs/configuration/embedding.md`
  - `docs/configuration/vector_db.md`
  - `docs/configuration/file_loader.md`
  - `docs/configuration/web_crawler.md`
- Usage docs:
  - `docs/usage/quick_start.md`
  - `docs/usage/cli.md`
- Examples:
  - `examples/basic_example.py`
  - `examples/load_local_file_using_unstructured.py`
  - `examples/load_website_using_firecrawl.py`
- Evaluation:
  - `evaluation/README.md`