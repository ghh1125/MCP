# graph-theory MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository can be exposed as an MCP (Model Context Protocol) service for graph algorithms and network optimization tasks.  
It provides a broad set of capabilities around:

- Graph modeling (`Graph`, `Graph3D`, `BasicGraph`)
- Pathfinding (BFS/DFS, shortest path, all paths)
- Network analysis (components, cycle checks, topological sort, DAG helpers)
- Flow and optimization (max flow, min-cost flow, assignment, transshipment, traffic scheduling, TSP)
- Optional visualization utilities (`plot_2d`, `plot_3d`)

It is best suited for AI-agent workflows that need callable graph-analysis services.

---

## 2) Installation Method

### Requirements
- Python 3.x
- Package is installed via `setup.py`
- Optional:
  - `matplotlib` for visualization features
  - `numpy` may be useful for optimization-heavy workloads

### Install
- `pip install .`
- For development/testing: `pip install -r test-requirements.txt`

---

## 3) Quick Start

Typical MCP (Model Context Protocol) service usage wraps library functions as callable services.

Example usage flow:
1. Create/load a graph with `Graph`
2. Add nodes/edges
3. Call algorithms such as:
   - `shortest_path(graph, start, end, avoids=None)`
   - `breadth_first_search(graph, start, end)`
   - `maximum_flow(graph, start, end)`
   - `topological_sort(graph, key=None)`

You can also use sample generators from `examples.graphs` (e.g., `grid`, `london_underground`) for quick testing.

---

## 4) Available Tools and Endpoints List

Below is a practical MCP (Model Context Protocol) service mapping you can expose.

### Core Graph Services
- `graph.create` → initialize `Graph` / `Graph3D`
- `graph.subgraph` → extract subgraph (`subgraph`)
- `graph.components` → connected components (`components`)
- `graph.network_size` → neighborhood size (`network_size`)

### Search & Path Services
- `path.shortest` → `shortest_path`
- `path.shortest_bidirectional` → `shortest_path_bidirectional`
- `path.distance_from_path` → `distance_from_path`
- `path.all` → `all_paths`
- `path.all_simple` → `all_simple_paths`
- `search.bfs` → `breadth_first_search`
- `search.dfs` → `depth_first_search`
- `search.degree_of_separation` → `degree_of_separation`

### Topology & Structure Services
- `graph.has_cycles` → `has_cycles`
- `graph.topological_sort` → `topological_sort`
- `graph.sources` → DAG source discovery (`sources`)
- `graph.phase_lines` → DAG layering (`phase_lines`)
- `graph.is_partite` → `is_partite`
- `graph.adjacency_matrix` → `adjacency_matrix`

### Flow & Optimization Services
- `flow.maximum` → `maximum_flow`
- `flow.max_flow_min_cut` → `maximum_flow_min_cut`
- `flow.min_cost` → `minimum_cost_flow_using_successive_shortest_path`
- `opt.assignment` → `ap_solver`
- `opt.wtap` → `wtap_solver`
- `opt.critical_path` → `critical_path`
- `opt.critical_path_slack` → `critical_path_minimize_for_slack`
- `opt.tsp_greedy` / `opt.tsp_bnb` / `opt.tsp_bruteforce` / `opt.tsp_2023`
- `opt.transshipment_schedule` → `schedule_rail_system` and related helpers
- `opt.traffic_jam_solver` → `jam_solver`

### Utility Services
- `graph.hash` → `graph_hash`
- `graph.flow_hash` → `flow_graph_hash`
- `graph.merkle_tree` → `merkle_tree`
- `graph.random_xy` → `random_xy_graph`
- `graph.xy_distance` → `xy_distance`
- `visual.plot_2d` / `visual.plot_3d` → plotting helpers

---

## 5) Common Issues and Notes

- No built-in CLI was detected; MCP (Model Context Protocol) service endpoints should be added by your service wrapper.
- `requirements.txt` is empty; rely on `setup.py` and optional manual installs (`matplotlib`, `numpy`) as needed.
- Some optimization tasks (TSP/traffic/transshipment/flow) can be computationally expensive on large graphs.
- For production services:
  - enforce input validation (node existence, capacities, costs, DAG assumptions),
  - set execution timeouts,
  - return structured errors for unsolved/infeasible cases.
- Visualization services may fail in headless environments unless backend configuration is handled.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/root-11/graph-theory
- Main package: `graph/`
- Examples: `examples/graphs.py`
- Tests (best behavior reference): `tests/`
- Original project README: `README.md` in repository root