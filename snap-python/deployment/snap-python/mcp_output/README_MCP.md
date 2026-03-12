# snap-python MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes graph analytics capabilities built on top of the `snap-python` repository (Stanford SNAP bindings + `snapx` Pythonic API).  
It is designed for developer workflows where an LLM or client app needs to:

- Create/load graphs
- Run shortest path and connectivity analysis
- Compute community/centrality metrics
- Convert between Python data structures and graph objects

Main usable layers:

- `swig.snap` (high-performance SNAP bindings, broad algorithm coverage)
- `snapx` (NetworkX-like API wrapping SNAP-style behavior)

---

## 2) Installation Method

### Requirements

- Python 3.x
- `pip`
- Build toolchain for native extension (C/C++ compiler, SWIG-compatible environment) for `swig.snap` usage
- Optional: `networkx`, `numpy`, `scipy` for interoperability or specific algorithm paths

### Install

- Install from repository root:
  - `pip install .`
- Editable/dev install:
  - `pip install -e .`

If native build fails, you can still use pure Python `snapx` portions where applicable, but full SNAP performance/features require successful extension build.

---

## 3) Quick Start

### Basic graph + shortest path (snapx-style)

- Create graph with `snapx.classes.graph.Graph` or generators (`snapx.generators.classic.path_graph`)
- Use unweighted/weighted shortest path modules:
  - `snapx.algorithms.shortest_paths.unweighted.single_source_shortest_path`
  - `snapx.algorithms.shortest_paths.weighted.dijkstra_path`

### Core analysis functions (SNAP SWIG layer)

Typical high-value functions available in `snap` include:

- Connectivity: `GetWccs`, `GetSccs`, `IsConnected`, `GetMxWcc`
- Path/BFS: `GetBfsTree`, `GetShortPath`, `GetBfsEffDiam`
- Centrality: `GetDegreeCentr`, `GetClosenessCentr`, `GetBetweennessCentr`
- Community: `CommunityCNM`, `CommunityGirvanNewman`
- Generation: `GenRndGnm`, `GenPrefAttach`, `GenSmallWorld`, `GenRMat`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service surface (developer-oriented grouping):

- `graph.create`
  - Create empty/path/basic graphs (snapx generators, SNAP constructors)
- `graph.load`
  - Load edge lists / persisted graphs (`LoadEdgeList`, `*_Load`)
- `graph.convert`
  - Convert dict-of-dicts and Python structures (`to_snapx_graph`, `from_dict_of_dicts`)
- `analysis.connectivity`
  - Components and connectedness (`connected_components`, `GetWccs`, `GetSccs`)
- `analysis.shortest_path`
  - Unweighted + Dijkstra + all-pairs (`single_source_shortest_path`, `dijkstra_path`, `johnson`)
- `analysis.centrality`
  - Degree/closeness/betweenness/eigenvector variants
- `analysis.community`
  - CNM and Girvan-Newman community detection
- `analysis.stats`
  - Degree distributions, triads, clustering, diameter/ANF estimates
- `graph.relabel`
  - Node relabel operations (`relabel_nodes`, integer relabeling)

Note: Repository does not define a ready-made CLI endpoint set; expose these as MCP (Model Context Protocol) service methods in your host runtime.

---

## 5) Common Issues and Notes

- Native build friction:
  - Most installation issues come from missing compiler/SWIG toolchain.
- Mixed API layers:
  - `swig.snap` and `snapx` overlap conceptually; keep service contracts explicit about which backend each endpoint uses.
- Performance:
  - Prefer SWIG SNAP functions for large graphs and heavy analytics.
- Compatibility:
  - Some conversion paths may assume NetworkX-like inputs.
- Testing/examples:
  - Use `test/` and `examples/` as validation references for endpoint behavior and expected outputs.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/snap-stanford/snap-python
- Root docs: `README.md`, `troubleshooting.md`, `RELEASE.txt`
- SWIG notes: `swig/README.txt`
- Docker/environment help: `docker/README.md`
- Examples: `examples/`, `dev/examples/`
- Tests: `test/`, `dev/test/`