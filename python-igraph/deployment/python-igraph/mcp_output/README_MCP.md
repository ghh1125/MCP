# python-igraph MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical graph analytics capabilities from `python-igraph` through MCP (Model Context Protocol) endpoints.  
It is designed for LLM/tooling workflows that need fast graph creation, transformation, analysis, community detection, layout generation, and safe serialization.

Main capabilities:
- Build graphs from tuples, dicts, files, or generators
- Run core analytics (connectivity, shortest paths, centrality, flow, components)
- Detect communities and return structured clustering outputs
- Export summaries and tabular-like representations for downstream agents
- Read/write common graph formats

---

## 2) Installation Method

### System/runtime requirements
- Python 3.9+ (recommended)
- `python-igraph` (includes bindings to igraph C core)
- `texttable` (required by python-igraph output formatting)

### Install minimal runtime
pip install python-igraph texttable

### Optional extras (depending on endpoints you expose)
pip install matplotlib plotly cairocffi numpy pandas scipy networkx

Notes:
- Cairo-based rendering may require OS-level Cairo libraries.
- If running in containers, prefer slim analytics-first images unless visualization is required.

---

## 3) Quick Start

### Service bootstrap (conceptual)
1. Start MCP (Model Context Protocol) server process.
2. Register graph services/endpoints (create/read/analyze/community/layout/export).
3. Route incoming tool calls to `igraph.Graph` APIs and wrapper helpers.

### Minimal usage flow
- Create graph from edge tuples
- Compute summary + basic metrics
- Run community detection
- Return JSON-safe result payload

Example call sequence:
1. `graph.create_from_tuple_list`
2. `graph.summary`
3. `graph.metrics.centrality`
4. `graph.community.multilevel`
5. `graph.export.dict_list`

---

## 4) Available Tools and Endpoints List

Recommended endpoint set for this repository:

- `graph.create_from_tuple_list`  
  Build graph from `(source, target)` tuples (+ optional attrs).

- `graph.create_from_dict_list`  
  Build graph from node/edge dictionaries.

- `graph.read_file`  
  Load graph from file via format dispatch (`igraph.io.files`).

- `graph.write_file`  
  Save graph to supported graph file formats.

- `graph.summary`  
  Return compact graph summary (`_get_graph_summary`).

- `graph.vertices.table`  
  Export vertex table-like structure (`_get_vertex_dataframe`-style output).

- `graph.edges.table`  
  Export edge table-like structure (`_get_edge_dataframe`-style output).

- `graph.metrics.basic`  
  Degree, components, density, diameter, transitivity, etc.

- `graph.paths.shortest`  
  Shortest path / distance queries.

- `graph.community.fastgreedy`  
  Fast greedy community detection.

- `graph.community.multilevel`  
  Louvain-style multilevel optimization.

- `graph.community.infomap`  
  Infomap community detection.

- `graph.community.walktrap`  
  Walktrap community detection.

- `graph.community.compare`  
  Compare clustering outputs (`_compare_communities`, split-join distance).

- `graph.layout.auto`  
  Auto layout coordinate generation (`_layout_auto`).

- `graph.layout.compute`  
  Explicit layout selection (`_layout`).

- `graph.export.tuple_list`  
  Serialize graph to tuple-list boundary format.

- `graph.export.dict_list`  
  Serialize graph to dict-list boundary format (MCP-safe payloads).

- `service.health`  
  Runtime check (imports, optional backend availability).

---

## 5) Common Issues and Notes

- **Binary/backend issues**: `python-igraph` relies on compiled components; use official wheels where possible.
- **Visualization dependencies**: Plot endpoints may fail if Cairo/Matplotlib/Plotly extras are missing.
- **Large graph performance**: Prefer summary/stat endpoints over full table exports for very large graphs.
- **Serialization size**: Dict-list exports can become large; add pagination or sampling endpoints.
- **Determinism**: Community/layout algorithms may involve randomness; expose seed parameters.
- **Environment parity**: Keep dev/prod Python and dependency versions aligned to avoid layout or IO differences.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/igraph/python-igraph
- python-igraph docs: https://igraph.org/python/
- API reference (Graph methods): https://igraph.org/python/doc/
- Project README: https://github.com/igraph/python-igraph/blob/main/README.md
- Changelog: https://github.com/igraph/python-igraph/blob/main/CHANGELOG.md