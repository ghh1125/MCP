# NetworkX MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical graph analytics capabilities from NetworkX through MCP (Model Context Protocol) tools.  
It is designed for AI agents and developer workflows that need to:

- Build and transform graphs (`Graph`, `DiGraph`, `MultiGraph`, `MultiDiGraph`)
- Run shortest-path and connectivity analysis
- Compute centrality and detect communities
- Generate synthetic graphs for testing
- Import/export graph data (GraphML, GEXF, JSON node-link)
- Convert between NetworkX and NumPy/SciPy matrix formats

Repository: https://github.com/networkx/networkx

---

## 2) Installation Method

### Requirements
- Python >= 3.11
- NetworkX (from PyPI or local source)

### Minimal install
pip install networkx

### Recommended optional dependencies (feature-based)
- Numerical/matrix workflows: `numpy`, `scipy`
- Visualization: `matplotlib`
- DataFrame integration: `pandas`
- External graph formats/tools: `lxml`, `pygraphviz`, `pydot`

Example:
pip install networkx numpy scipy pandas matplotlib lxml pydot pygraphviz

---

## 3) Quick Start

### Create a graph and run shortest path
import networkx as nx
G = nx.erdos_renyi_graph(30, 0.08, seed=42)
path = nx.dijkstra_path(G, source=0, target=10)
dist = nx.dijkstra_path_length(G, source=0, target=10)

### Connectivity + centrality
is_conn = nx.is_connected(G)
components = list(nx.connected_components(G))
bc = nx.betweenness_centrality(G)

### Community detection
communities = nx.louvain_communities(G, seed=42)

### JSON-safe exchange
from networkx.readwrite import json_graph
payload = json_graph.node_link_data(G)
G2 = json_graph.node_link_graph(payload)

### Typical MCP (Model Context Protocol) tool-call flow
1. Send graph input (edge list / node-link JSON / file path).  
2. Call analysis tool (shortest path, centrality, communities, etc.).  
3. Receive structured JSON output (metrics, paths, component sets, partitions).  

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service surface:

- `graph.create`
  - Create empty or typed graphs (`Graph`, `DiGraph`, `MultiGraph`, `MultiDiGraph`).

- `graph.generate`
  - Generate synthetic graphs:
  - `erdos_renyi_graph`, `barabasi_albert_graph`, `watts_strogatz_graph`.

- `path.unweighted`
  - Unweighted path operations:
  - `single_source_shortest_path`, `single_target_shortest_path`,
    `all_pairs_shortest_path`, `bidirectional_shortest_path`.

- `path.weighted`
  - Weighted path operations:
  - `dijkstra_path`, `dijkstra_path_length`, `single_source_dijkstra`,
    `all_pairs_dijkstra`, `bellman_ford_path`, `floyd_warshall`.

- `analysis.connectivity`
  - `connected_components`, `is_connected`, `number_connected_components`.

- `analysis.centrality`
  - `betweenness_centrality`, `edge_betweenness_centrality`.

- `analysis.community`
  - `louvain_communities`, `louvain_partitions`.

- `io.graphml`
  - `read_graphml`, `write_graphml`.

- `io.gexf`
  - `read_gexf`, `write_gexf`.

- `io.json_nodelink`
  - `node_link_data`, `node_link_graph`.

- `convert.matrix`
  - `from_numpy_array`, `to_numpy_array`,
    `from_scipy_sparse_array`, `to_scipy_sparse_array`.

---

## 5) Common Issues and Notes

- Version compatibility:
  - Use Python 3.11+ to match current project requirements.

- Optional dependency errors:
  - Matrix/linear algebra features require NumPy/SciPy.
  - Some file formats/tools require `lxml`, `pydot`, or `pygraphviz`.

- Directed vs undirected:
  - Some algorithms require specific graph types; validate before execution.

- Performance:
  - Large graphs can be expensive for all-pairs paths, centrality, and community detection.
  - Prefer sampled/approximate or single-source variants for big datasets.

- Serialization:
  - For MCP (Model Context Protocol), prefer node-link JSON payloads for portability.

- Import feasibility/risk:
  - Analysis indicates high import feasibility and low intrusiveness risk.

---

## 6) Reference Links / Documentation

- NetworkX repository: https://github.com/networkx/networkx  
- NetworkX docs (main): https://networkx.org/documentation/stable/  
- Tutorial: https://networkx.org/documentation/stable/tutorial.html  
- API reference: https://networkx.org/documentation/stable/reference/index.html  
- GraphML reference in NetworkX: https://networkx.org/documentation/stable/reference/readwrite/graphml.html  
- GEXF reference in NetworkX: https://networkx.org/documentation/stable/reference/readwrite/gexf.html