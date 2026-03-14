# graph-theory MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps the `graph-theory` Python library to expose practical graph algorithms as callable service tools.

It is designed for:
- Pathfinding (shortest path, all paths, BFS/DFS)
- Network analysis (components, degree of separation, cycle detection)
- Optimization (max flow, min-cost flow, assignment, TSP, critical path)
- Graph utilities (adjacency matrix, hashing, random graph generation, topology checks)
- Optional visualization helpers (2D/3D plotting)

Repository: https://github.com/root-11/graph-theory

---

## 2) Installation Method

### Requirements
- Python 3.x
- `setuptools`
- Optional: `matplotlib`, `numpy`, `scipy` (for plotting / scientific workflows)

### Install
- From PyPI (if published):
  pip install graph-theory
- From source:
  git clone https://github.com/root-11/graph-theory.git  
  cd graph-theory  
  pip install -e .

### For development/testing
- Install test deps:
  pip install -r test-requirements.txt
- Run tests:
  pytest

---

## 3) Quick Start

Install and import core APIs in your MCP (Model Context Protocol) service runtime:

from graph.core import Graph
from graph.shortest_path import shortest_path
from graph.max_flow import maximum_flow
from graph.topological_sort import topological_sort

Build a graph and run common operations:

g = Graph()
# add nodes/edges according to library API, then:
path = shortest_path(g, start="A", end="B", avoids=None)
flow = maximum_flow(g, start="S", end="T")
order = topological_sort(g, key=None)

Useful additional examples:
- BFS/DFS: `breadth_first_search`, `depth_first_search`
- All paths: `all_paths`, `all_simple_paths`
- Network checks: `has_cycles`, `components`, `is_partite`
- Optimization: `ap_solver`, `minimum_cost_flow_using_successive_shortest_path`, `tsp_greedy`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service tools mapped to library functions:

- `shortest_path` — shortest route between two nodes
- `shortest_path_bidirectional` — bidirectional shortest path search
- `all_pairs_shortest_paths` — shortest paths for all node pairs
- `all_paths` — enumerate all paths between start/end
- `all_simple_paths` — enumerate simple (no repeated node) paths
- `breadth_first_search` / `depth_first_search` — traversal/search
- `has_cycles` / `cycle` — cycle detection and extraction
- `topological_sort` — topological ordering for DAGs
- `components` — connected components
- `degree_of_separation` / `distance_map` — distance analysis
- `maximum_flow` / `maximum_flow_min_cut` — flow and cut analysis
- `minimum_cost_flow_using_successive_shortest_path` — min-cost flow
- `ap_solver` / `wtap_solver` — assignment and WTAP solvers
- `critical_path` / `critical_path_minimize_for_slack` — project scheduling analysis
- `tsp_greedy`, `tsp_branch_and_bound`, `tsp_2023`, `brute_force` — TSP solvers
- `adjacency_matrix` — graph-to-matrix conversion
- `is_partite`, `sources`, `phase_lines` — graph topology helpers
- `graph_hash`, `flow_graph_hash`, `merkle_tree` — hashing/integrity helpers
- `random_xy_graph` — random spatial graph generator
- `plot_2d`, `plot_3d` — optional visualization endpoints

---

## 5) Common Issues and Notes

- No built-in CLI entry points were detected; expose functions through your MCP (Model Context Protocol) service layer directly.
- Some algorithms (e.g., all paths, brute-force TSP) can be expensive on large graphs.
- Ensure optional plotting/scientific packages are installed before using visualization or numeric-heavy workflows.
- Keep graph size constraints and timeouts in your service definitions (especially for combinatorial solvers).
- Use caching for repeated shortest-path or flow queries in production workloads.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/root-11/graph-theory
- Source package: `graph/`
- Examples: `examples/graphs.py`
- Tests (usage patterns): `tests/`
- Original README in repo: `README.md`