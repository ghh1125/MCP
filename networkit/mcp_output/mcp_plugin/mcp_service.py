import os
import sys
from typing import List, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

try:
    import networkit as nk
except Exception:
    nk = None


mcp = FastMCP("networkit_service")


def _require_networkit() -> None:
    if nk is None:
        raise ImportError(
            "networkit could not be imported. Ensure compiled NetworKit bindings are installed."
        )


@mcp.tool(name="graph_info", description="Return basic graph statistics for an edge list.")
def graph_info(
    edges: List[List[int]],
    weighted: bool = False,
    directed: bool = False,
) -> Dict[str, Any]:
    """
    Build a graph from an edge list and return core statistics.

    Parameters:
    - edges: List of edges. For unweighted mode, each edge is [u, v].
             For weighted mode, each edge is [u, v, w].
    - weighted: Whether to create a weighted graph.
    - directed: Whether to create a directed graph.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        _require_networkit()
        if not edges:
            return {"success": False, "result": None, "error": "edges cannot be empty"}

        max_node = 0
        for e in edges:
            if len(e) < 2:
                return {"success": False, "result": None, "error": "each edge must have at least 2 elements"}
            max_node = max(max_node, int(e[0]), int(e[1]))

        g = nk.graph.Graph(n=max_node + 1, weighted=weighted, directed=directed)
        for e in edges:
            u, v = int(e[0]), int(e[1])
            if weighted:
                if len(e) < 3:
                    return {"success": False, "result": None, "error": "weighted edges must be [u, v, w]"}
                w = float(e[2])
                g.addEdge(u, v, w)
            else:
                g.addEdge(u, v)

        result = {
            "number_of_nodes": g.numberOfNodes(),
            "number_of_edges": g.numberOfEdges(),
            "is_directed": g.isDirected(),
            "is_weighted": g.isWeighted(),
            "density": nk.graphtools.density(g),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="connected_components", description="Compute connected components for an undirected graph.")
def connected_components(edges: List[List[int]]) -> Dict[str, Any]:
    """
    Compute connected components from an undirected unweighted edge list.

    Parameters:
    - edges: List of [u, v] edges.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        _require_networkit()
        if not edges:
            return {"success": False, "result": None, "error": "edges cannot be empty"}

        max_node = max(max(int(e[0]), int(e[1])) for e in edges)
        g = nk.graph.Graph(n=max_node + 1, weighted=False, directed=False)
        for e in edges:
            g.addEdge(int(e[0]), int(e[1]))

        cc = nk.components.ConnectedComponents(g)
        cc.run()
        comp_map = cc.getComponents()
        result = {
            "number_of_components": len(comp_map),
            "component_sizes": [len(c) for c in comp_map],
            "components": comp_map,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="pagerank_centrality", description="Compute PageRank centrality scores.")
def pagerank_centrality(
    edges: List[List[int]],
    damping: float = 0.85,
    tol: float = 1e-6,
) -> Dict[str, Any]:
    """
    Compute PageRank scores on a directed graph.

    Parameters:
    - edges: List of [u, v] directed edges.
    - damping: Damping factor (usually 0.85).
    - tol: Convergence tolerance.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        _require_networkit()
        if not edges:
            return {"success": False, "result": None, "error": "edges cannot be empty"}

        max_node = max(max(int(e[0]), int(e[1])) for e in edges)
        g = nk.graph.Graph(n=max_node + 1, weighted=False, directed=True)
        for e in edges:
            g.addEdge(int(e[0]), int(e[1]))

        pr = nk.centrality.PageRank(g, damp=damping, tol=tol)
        pr.run()
        scores = pr.scores()
        result = {
            "scores": scores,
            "ranking": sorted(
                [{"node": i, "score": s} for i, s in enumerate(scores)],
                key=lambda x: x["score"],
                reverse=True,
            ),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="shortest_paths", description="Compute single-source shortest path distances.")
def shortest_paths(
    edges: List[List[int]],
    source: int,
    weighted: bool = False,
    directed: bool = False,
) -> Dict[str, Any]:
    """
    Compute shortest path distances from a source node.

    Parameters:
    - edges: Edge list. Unweighted: [u, v], weighted: [u, v, w].
    - source: Source node id.
    - weighted: Whether to use weighted shortest paths.
    - directed: Whether the graph is directed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        _require_networkit()
        if not edges:
            return {"success": False, "result": None, "error": "edges cannot be empty"}

        max_node = 0
        for e in edges:
            if len(e) < 2:
                return {"success": False, "result": None, "error": "each edge must have at least 2 elements"}
            max_node = max(max_node, int(e[0]), int(e[1]))

        if source < 0 or source > max_node:
            return {"success": False, "result": None, "error": "source out of range"}

        g = nk.graph.Graph(n=max_node + 1, weighted=weighted, directed=directed)
        for e in edges:
            u, v = int(e[0]), int(e[1])
            if weighted:
                if len(e) < 3:
                    return {"success": False, "result": None, "error": "weighted edges must be [u, v, w]"}
                g.addEdge(u, v, float(e[2]))
            else:
                g.addEdge(u, v)

        if weighted:
            algo = nk.distance.Dijkstra(g, source, storePaths=False)
        else:
            algo = nk.distance.BFS(g, source, storePaths=False)
        algo.run()
        distances = algo.getDistances()

        return {"success": True, "result": {"source": source, "distances": distances}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="louvain_communities", description="Detect communities using PLM/Louvain-style optimization.")
def louvain_communities(
    edges: List[List[int]],
    refine: bool = True,
    gamma: float = 1.0,
) -> Dict[str, Any]:
    """
    Detect communities using NetworKit PLM.

    Parameters:
    - edges: Undirected edge list [u, v].
    - refine: Whether to refine communities.
    - gamma: Resolution parameter.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        _require_networkit()
        if not edges:
            return {"success": False, "result": None, "error": "edges cannot be empty"}

        max_node = max(max(int(e[0]), int(e[1])) for e in edges)
        g = nk.graph.Graph(n=max_node + 1, weighted=False, directed=False)
        for e in edges:
            g.addEdge(int(e[0]), int(e[1]))

        plm = nk.community.PLM(g, refine=refine, gamma=gamma)
        plm.run()
        part = plm.getPartition()
        communities = [[] for _ in range(part.numberOfSubsets())]
        for u in g.iterNodes():
            cid = part.subsetOf(u)
            communities[cid].append(u)

        result = {
            "number_of_communities": part.numberOfSubsets(),
            "communities": communities,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()