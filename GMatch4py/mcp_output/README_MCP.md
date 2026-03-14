# GMatch4py MCP (Model Context Protocol) Service README

## 1) Project Introduction

GMatch4py is a Python library for graph comparison and graph kernel computation.  
This MCP (Model Context Protocol) service wraps GMatch4py capabilities so LLM agents can:

- Compare two or more graphs
- Compute graph similarity/distance matrices
- Run graph edit distance (GED)-style matching workflows
- Generate kernel/embedding-ready outputs for downstream ML tasks

This is useful for structure-aware retrieval, clustering, anomaly detection, and graph classification pipelines.

---

## 2) Installation

### Requirements

From repository analysis, core dependencies are:

- numpy
- networkx
- scipy
- scikit-learn

Python package metadata is provided via `setup.py` and `requirements.txt`.

### Install from source

1. Clone the repository:
   git clone https://github.com/Jacobe2169/GMatch4py.git

2. Install dependencies:
   pip install -r requirements.txt

3. Install the package:
   pip install .

If you are integrating as an MCP (Model Context Protocol) service, also install your MCP runtime/SDK in the same environment.

---

## 3) Quick Start

### Python usage (library-level)

Typical usage pattern:

1. Build or load NetworkX graphs
2. Initialize a matcher/kernel object from `gmatch4py`
3. Compute pairwise distances/similarities
4. Return matrix/results to caller

Example flow (conceptual):

- Create graph list: `[g1, g2, g3, ...]`
- Call comparison method (for GED/kernel implementation)
- Receive NxN matrix for ranking, retrieval, or clustering

### MCP (Model Context Protocol) service usage

Typical service flow:

1. Client sends graphs (edge list / adjacency / labeled nodes)
2. Service validates and normalizes input
3. Service runs selected algorithm (GED/kernel)
4. Service returns:
   - score matrix
   - pairwise top matches
   - optional metadata (runtime, parameters)

---

## 4) Available Tools and Endpoints

Note: this repository does not expose a built-in CLI or MCP server entrypoint by default, so endpoints are typically defined by your wrapper layer. A practical MCP (Model Context Protocol) service should expose tools like:

### `health_check`
Returns service status, version, dependency availability.

### `list_algorithms`
Returns supported graph matching/kernel methods and required parameters.

### `compare_graph_pair`
Input: two graphs + algorithm settings  
Output: single similarity/distance score (+ optional alignment details).

### `compare_graph_batch`
Input: list of graphs + algorithm settings  
Output: pairwise matrix, optional nearest-neighbor list.

### `compute_kernel_matrix`
Input: graph set + kernel config  
Output: kernel/similarity matrix suitable for ML models.

### `embed_graphs` (optional)
Input: graph set + embedding config  
Output: vector representation per graph.

### `explain_score` (optional)
Input: graph pair + prior score context  
Output: human-readable explanation of similarity/difference drivers.

---

## 5) Common Issues and Notes

- No native MCP server included: you need a thin wrapper that maps MCP tools to `gmatch4py` calls.
- Dependency compatibility: use a clean virtual environment to avoid SciPy / scikit-learn version conflicts.
- Input format consistency: enforce a single graph schema (node IDs, labels, edge attributes).
- Performance: pairwise comparison scales roughly with graph count² for full matrices; use batching/caching for large sets.
- Reproducibility: pin versions in `requirements.txt`/lockfile and log algorithm parameters per request.
- Build concerns: package uses `setup.py`; if wheels fail, install compiler/build essentials and retry.

---

## 6) References

- Repository: https://github.com/Jacobe2169/GMatch4py
- Package metadata: `setup.py`
- Dependencies: `requirements.txt`
- Tests/examples:
  - `test/test.py`
  - `test/gmatch4py_performance_test.py`

If you are deploying this as an MCP (Model Context Protocol) service, keep service contracts (input schema, output schema, error model) documented alongside this README.