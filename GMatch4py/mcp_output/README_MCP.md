# GMatch4py MCP (Model Context Protocol) Service README

## 1) Project Introduction

GMatch4py is a Python library for graph comparison, focused on graph edit distance (GED), graph kernels, and related embedding/matching utilities.  
This MCP (Model Context Protocol) service wraps core GMatch4py capabilities so LLM clients can compare graphs, compute similarity/distance signals, and use graph-matching outputs in downstream workflows.

Main capabilities:
- Graph similarity/distance computation
- GED-oriented matching workflows
- Kernel-based graph comparison
- Integration with NetworkX graph objects

---

## 2) Installation Method

### Requirements
- Python 3.x
- numpy
- scipy
- networkx
- Optional: matplotlib (for visualization)

### Install from source
1. Clone repository:
   - https://github.com/Jacobe2169/GMatch4py
2. Install dependencies:
   - pip install -r requirements.txt
3. Install package:
   - pip install .

If you are building native extensions, ensure your local C/C++ build toolchain is available.

---

## 3) Quick Start

### Basic Python usage (library side)
import networkx as nx
import gmatch4py as gm

g1 = nx.Graph()
g1.add_edges_from([(1, 2), (2, 3)])

g2 = nx.Graph()
g2.add_edges_from([(1, 2), (2, 4)])

# Example: choose a matcher/kernel from gmatch4py and compute similarity/distance
# (Exact class names may vary by version; inspect gm.* modules)
# matcher = gm.<SomeMatcherOrKernel>(...)
# result = matcher.compare([g1, g2], None)

print("Graphs loaded and ready for comparison.")

### MCP (Model Context Protocol) service usage pattern
- Start the MCP (Model Context Protocol) service host that exposes GMatch4py operations.
- Call service tools with:
  - Graph payload(s) (typically nodes/edges or serialized NetworkX-compatible format)
  - Algorithm selection (GED/kernel method)
  - Optional parameters (costs, normalization, etc.)
- Receive:
  - Distance/similarity matrix
  - Pairwise scores
  - Optional matching metadata

---

## 4) Available Tools and Endpoints List

Note: This repository does not define a built-in CLI or explicit HTTP endpoints. In MCP (Model Context Protocol) deployments, expose tools like the following:

- graph.compare
  - Compare two or more graphs and return similarity/distance outputs.
- graph.ged
  - Run graph edit distance-oriented matching with configurable costs.
- graph.kernel
  - Compute kernel-based similarity for graph sets.
- graph.batch_compare
  - Run pairwise comparisons for a batch and return matrix-form results.
- graph.validate
  - Validate graph input schema/format before computation.

Recommended input fields:
- graphs: list of graph objects (nodes/edges/attributes)
- method: GED or kernel method name
- options: algorithm-specific parameters
- return_metadata: boolean for detailed diagnostics

---

## 5) Common Issues and Notes

- Build/install issues:
  - If installation fails, verify compiler/build tools and matching Python headers are installed.
- Dependency mismatches:
  - Keep numpy/scipy/networkx versions consistent in your environment.
- Input format errors:
  - Ensure graph payloads are structurally valid and consistent across batch calls.
- Performance:
  - GED can be expensive on large/dense graphs; prefer batch sizing, caching, or kernel approximations when needed.
- Environment:
  - Use a virtual environment to avoid package conflicts.
- Testing:
  - Repository includes tests under `test/`; run them after installation to validate behavior.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/Jacobe2169/GMatch4py
- Existing project README (source of algorithm usage details):  
  https://github.com/Jacobe2169/GMatch4py/blob/master/README.md
- Python packaging files:
  - `requirements.txt`
  - `setup.py`
- Related dependency docs:
  - https://networkx.org/
  - https://numpy.org/
  - https://scipy.org/

If you are packaging this as an MCP (Model Context Protocol) service, add your host-specific transport/config docs (stdio/SSE/WebSocket), tool schemas, and example request/response payloads alongside this README.