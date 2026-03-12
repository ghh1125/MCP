# NetworKit MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository provides a high-performance graph analytics backend (NetworKit) that can be exposed as an MCP (Model Context Protocol) service layer for LLM/tooling workflows.

Primary service capabilities:
- Large-scale graph analytics (centrality, community detection, components, distances, flow, matching, sparsification, etc.)
- Graph algebra/spectral utilities (`adjacencyMatrix`, `laplacianMatrix`, eigen/SVD helpers)
- Interoperability services (NetworkX adapters, visualization bridges)
- Optional Gephi streaming/export services
- Profiling/benchmark services for algorithm performance experiments

NetworKit is implemented in C++ with Python bindings, optimized for performance on large graphs.

---

## 2) Installation Method

### Prerequisites
- Python 3.x
- `pip`
- Build toolchain for native extensions (if installing from source)
- Recommended scientific stack: `numpy` (required), `scipy`/`matplotlib`/`networkx`/`pandas` (optional, feature-dependent)

### Install from PyPI (recommended)
- pip install networkit

### Install from source (repository)
- pip install -r requirements.txt
- pip install .

If local compilation fails, ensure C/C++ compiler toolchain and CMake-compatible environment are available.

---

## 3) Quick Start

### Basic import and graph creation
- import networkit as nk
- G = nk.Graph(5, weighted=False, directed=False)
- G.addEdge(0, 1)
- G.addEdge(1, 2)

### Run a core algorithm (example: connected components)
- cc = nk.components.ConnectedComponents(G)
- cc.run()
- count = cc.numberOfComponents()

### Use algebraic helpers
- from networkit import algebraic
- A = algebraic.adjacencyMatrix(G)
- L = algebraic.laplacianMatrix(G)

### Convert between NetworKit and NetworkX
- from networkit import nxadapter
- nx_g = nxadapter.nk2nx(G)
- nk_g = nxadapter.nx2nk(nx_g)

### Run tests (sanity check)
- pytest
- python -m notebooks.test_notebooks

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints based on repository modules:

- `graph.create`  
  Create/load graph objects for downstream analysis.

- `graph.convert.nx2nk` / `graph.convert.nk2nx`  
  Convert graphs between NetworkX and NetworKit (`networkit.nxadapter`).

- `analysis.components`  
  Connected components and related structure analysis.

- `analysis.centrality`  
  Centrality measures for node importance.

- `analysis.community`  
  Community detection and partitioning routines.

- `analysis.distance`  
  Shortest-path and distance-based metrics.

- `analysis.flow` / `analysis.matching`  
  Flow and matching algorithms.

- `analysis.coloring`  
  Coloring utilities (`getColoring`, `isProperColoring`).

- `algebraic.matrix.adjacency` / `algebraic.matrix.laplacian`  
  Matrix generation and spectral preprocessing (`networkit.algebraic`).

- `algebraic.spectral.eigen` / `algebraic.spectral.svd`  
  Eigenvector/SVD helper services.

- `viz.plot`  
  Basic plotting helpers (`networkit.plot`).

- `viz.bridge.networkx` / `viz.bridge.igraph` / `viz.bridge.graphtool`  
  Export to other graph ecosystems (`networkit.vizbridges`).

- `gephi.stream.event` / `gephi.export.csv`  
  Gephi streaming and CSV export helpers (`networkit.gephi.*`).

- `profiling.run` / `profiling.stats` / `profiling.plot`  
  Benchmark execution, statistical summaries, and performance charts (`networkit.profiling.*`).

---

## 5) Common Issues and Notes

- Native extension dependency: NetworKit relies on compiled components; source installs may fail without a proper compiler toolchain.
- Optional dependencies: some features require extra libraries (`scipy`, `matplotlib`, `networkx`, `pandas`).
- Gephi features: require a running external Gephi service for streaming clients.
- Performance guidance:
  - Prefer NetworKit graph-native workflows over repeated cross-library conversion.
  - Reuse loaded graphs and algorithm objects where possible.
  - Use profiling services for parameter tuning and runtime validation.
- Testing:
  - Use `pytest` for core coverage.
  - Notebook checks are available via `python -m notebooks.test_notebooks`.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/networkit/networkit
- Main README: `README.md` in repository root
- Changelog: `CHANGES.md`
- Contribution guide: `CONTRIBUTING.md`
- Build/config files: `pyproject.toml`, `setup.py`, root `CMakeLists.txt`
- Input data examples: `input/README.md`
- Binary graph format notes: `networkit/cpp/io/NetworkitBinaryGraph.md`
- License: `License.txt`