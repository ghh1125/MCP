import os
import sys
from typing import Dict, List, Optional

from fastmcp import FastMCP

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

import igraph as ig


mcp = FastMCP("python_igraph_service")


@mcp.tool(
    name="create_graph",
    description="Create a graph with configurable directedness and optional edges.",
)
def create_graph(
    directed: bool = False,
    num_vertices: int = 0,
    edges: Optional[List[List[int]]] = None,
) -> Dict:
    """
    Create an igraph Graph and return a compact summary.

    Parameters:
    - directed: Whether the graph is directed.
    - num_vertices: Number of vertices to initialize.
    - edges: Optional edge list as [[u, v], ...].

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph(n=num_vertices, directed=directed)
        if edges:
            normalized_edges = [(int(e[0]), int(e[1])) for e in edges]
            g.add_edges(normalized_edges)
        return {
            "success": True,
            "result": {
                "vcount": g.vcount(),
                "ecount": g.ecount(),
                "is_directed": g.is_directed(),
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="erdos_renyi_graph",
    description="Generate an Erdős–Rényi random graph and return summary metrics.",
)
def erdos_renyi_graph(
    n: int,
    p: float,
    directed: bool = False,
    loops: bool = False,
) -> Dict:
    """
    Generate an Erdős–Rényi graph G(n, p).

    Parameters:
    - n: Number of vertices.
    - p: Probability of edge creation.
    - directed: Whether to generate a directed graph.
    - loops: Whether self-loops are allowed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph.Erdos_Renyi(n=n, p=p, directed=directed, loops=loops)
        return {
            "success": True,
            "result": {
                "vcount": g.vcount(),
                "ecount": g.ecount(),
                "density": g.density(loops=loops),
                "is_connected": g.is_connected(mode="weak" if directed else "strong")
                if g.vcount() > 0
                else True,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="graph_summary",
    description="Build a graph from an edge list and compute core structural summary statistics.",
)
def graph_summary(
    edges: List[List[int]],
    directed: bool = False,
    num_vertices: Optional[int] = None,
) -> Dict:
    """
    Create a graph from edges and return structural summary.

    Parameters:
    - edges: Edge list as [[u, v], ...].
    - directed: Whether the graph is directed.
    - num_vertices: Optional vertex count override.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        edge_tuples = [(int(u), int(v)) for u, v in edges]
        g = ig.Graph(
            n=num_vertices if num_vertices is not None else 0,
            edges=edge_tuples,
            directed=directed,
        )
        result = {
            "vcount": g.vcount(),
            "ecount": g.ecount(),
            "is_directed": g.is_directed(),
            "is_simple": g.is_simple(),
            "density": g.density(loops=False),
            "diameter": g.diameter(directed=directed, unconn=True)
            if g.vcount() > 0
            else 0,
            "average_path_length": g.average_path_length(
                directed=directed, unconn=True
            )
            if g.vcount() > 1
            else 0.0,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="shortest_path",
    description="Compute shortest path and distance between two vertices.",
)
def shortest_path(
    edges: List[List[int]],
    source: int,
    target: int,
    directed: bool = False,
    num_vertices: Optional[int] = None,
) -> Dict:
    """
    Compute shortest path between source and target vertices.

    Parameters:
    - edges: Edge list as [[u, v], ...].
    - source: Source vertex id.
    - target: Target vertex id.
    - directed: Whether graph is directed.
    - num_vertices: Optional vertex count override.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph(
            n=num_vertices if num_vertices is not None else 0,
            edges=[(int(u), int(v)) for u, v in edges],
            directed=directed,
        )
        vertices_path = g.get_shortest_paths(source, to=target, output="vpath")[0]
        distance = g.distances(source=[source], target=[target])[0][0]
        return {
            "success": True,
            "result": {"path": vertices_path, "distance": distance},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="centrality_metrics",
    description="Compute degree, betweenness, and pagerank centrality for all vertices.",
)
def centrality_metrics(
    edges: List[List[int]],
    directed: bool = False,
    num_vertices: Optional[int] = None,
) -> Dict:
    """
    Compute centrality metrics from an edge list.

    Parameters:
    - edges: Edge list as [[u, v], ...].
    - directed: Whether graph is directed.
    - num_vertices: Optional vertex count override.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph(
            n=num_vertices if num_vertices is not None else 0,
            edges=[(int(u), int(v)) for u, v in edges],
            directed=directed,
        )
        result = {
            "degree": g.degree(mode="all"),
            "betweenness": g.betweenness(directed=directed),
            "pagerank": g.pagerank(directed=directed),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="connected_components",
    description="Compute connected components (or weak/strong components for directed graphs).",
)
def connected_components(
    edges: List[List[int]],
    directed: bool = False,
    mode: str = "weak",
    num_vertices: Optional[int] = None,
) -> Dict:
    """
    Compute graph connected components.

    Parameters:
    - edges: Edge list as [[u, v], ...].
    - directed: Whether graph is directed.
    - mode: Component mode for directed graphs: 'weak' or 'strong'.
    - num_vertices: Optional vertex count override.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph(
            n=num_vertices if num_vertices is not None else 0,
            edges=[(int(u), int(v)) for u, v in edges],
            directed=directed,
        )
        comp_mode = mode if directed else "weak"
        comps = g.connected_components(mode=comp_mode)
        result = {
            "count": len(comps),
            "sizes": comps.sizes(),
            "membership": comps.membership,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="community_detection",
    description="Run Louvain community detection on a weighted/unweighted graph.",
)
def community_detection(
    edges: List[List[int]],
    weights: Optional[List[float]] = None,
    directed: bool = False,
    num_vertices: Optional[int] = None,
) -> Dict:
    """
    Run Louvain community detection.

    Parameters:
    - edges: Edge list as [[u, v], ...].
    - weights: Optional edge weights aligned with edges.
    - directed: Whether graph is directed.
    - num_vertices: Optional vertex count override.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        g = ig.Graph(
            n=num_vertices if num_vertices is not None else 0,
            edges=[(int(u), int(v)) for u, v in edges],
            directed=directed,
        )
        if weights is not None:
            if len(weights) != g.ecount():
                return {
                    "success": False,
                    "result": None,
                    "error": "weights length must match number of edges",
                }
            g.es["weight"] = [float(w) for w in weights]
            clustering = g.community_multilevel(weights=g.es["weight"])
        else:
            clustering = g.community_multilevel()
        return {
            "success": True,
            "result": {
                "membership": clustering.membership,
                "sizes": clustering.sizes(),
                "modularity": clustering.modularity,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()