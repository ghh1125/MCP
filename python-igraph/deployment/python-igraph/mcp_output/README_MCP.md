# python-igraph MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides graph analytics capabilities powered by `python-igraph`.  
It is designed for LLM/tooling workflows that need fast graph creation, mutation, analysis, layout, summary, and file I/O.

Main capabilities:
- Build and edit graphs (vertices/edges, directed/undirected)
- Run core network analysis (connectivity, paths, centrality, communities, matching, flow)
- Generate graph summaries for inspection
- Read/write graphs in common formats
- Compute layouts for visualization pipelines

---

## 2) Installation Method

### Requirements
- Python 3.x
- `python-igraph` (includes igraph C core binding at runtime)

Optional (feature-dependent):
- `matplotlib` (plotting)
- `plotly` (interactive plotting)
- `pycairo` or `cairocffi` (Cairo backend)
- `texttable` (formatted summaries/tables)

### Install
- pip install python-igraph
- Optional extras:
  - pip install matplotlib plotly cairocffi texttable

If your MCP (Model Context Protocol) host is separate, also install your host runtime and register this service in host configuration.

---

## 3) Quick Start

### Minimal usage flow
- Import `igraph`
- Create a `Graph`
- Run analysis (e.g., degree, shortest paths, components)
- Return compact results to MCP (Model Context Protocol) clients

Example workflow:
1. `Graph.Erdos_Renyi(n=100, p=0.05)`
2. Compute:
   - vertex/edge counts
   - average degree
   - connected components
   - centrality metrics
3. Optionally call summary helpers (`summary`) for human-readable output
4. For visualization-oriented clients, compute layout (`layout_auto`/layout methods) and return coordinates

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoint design:

- `graph.create`
  - Create graph from edge list, adjacency data, or generators (Erdős-Rényi, etc.)

- `graph.mutate`
  - Add/remove vertices and edges, clear graph, update attributes

- `graph.analyze.basic`
  - Counts, degree stats, density, components, diameter, clustering coefficients

- `graph.analyze.paths`
  - Shortest paths/distances, reachability, path extraction

- `graph.analyze.centrality`
  - Betweenness, closeness, PageRank, eigenvector centrality

- `graph.analyze.community`
  - Community detection and membership output

- `graph.analyze.flow_matching`
  - Max flow / min cut / bipartite matching

- `graph.layout.compute`
  - Auto/manual layout generation; returns coordinate arrays

- `graph.summary`
  - Structured and textual graph/vertex/edge summaries

- `graph.io.read`
  - Load graph from supported file formats

- `graph.io.write`
  - Persist graph to file formats

- `service.health`
  - Runtime/dependency health check

---

## 5) Common Issues and Notes

- Binary/runtime dependency:
  - `python-igraph` depends on compiled components; use supported wheels for your platform.
- Plotting backends:
  - Missing `matplotlib`/`plotly`/Cairo packages will disable related drawing features.
- Large graphs:
  - Centrality/community algorithms can be expensive; add size guards and timeout limits in endpoints.
- Determinism:
  - Randomized algorithms/layouts should expose a seed parameter.
- Serialization:
  - Return compact JSON-friendly structures (lists, dicts, numeric arrays), not raw Python objects.
- Environment isolation:
  - Use virtual environments to avoid backend/version conflicts.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/igraph/python-igraph
- Official docs: https://igraph.org/python/
- API reference (`igraph` module, `Graph`, layouts, I/O): see official docs
- Examples (gallery in repo): `doc/examples_sphinx-gallery/`
- Changelog: `CHANGELOG.md` in repository