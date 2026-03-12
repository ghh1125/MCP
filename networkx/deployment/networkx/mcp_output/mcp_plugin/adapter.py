import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for selected NetworkX functionality discovered by analysis.

    This adapter:
    - Runs in import mode by default.
    - Attempts direct imports from repository source code under `source/`.
    - Provides graceful fallback responses when imports are unavailable.
    - Returns a unified dictionary response format for all public methods.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._available = False
        self._import_error: Optional[str] = None

        self._from_numpy_array = None
        self._to_numpy_array = None
        self._from_scipy_sparse_array = None

        self._load_imports()

    # -------------------------------------------------------------------------
    # Internal module management
    # -------------------------------------------------------------------------
    def _load_imports(self) -> None:
        """
        Load target functions from the analyzed module path.

        Target module from analysis:
        - source.networkx.convert_matrix
        Effective import path (after source path injection):
        - networkx.convert_matrix
        """
        try:
            from networkx.convert_matrix import (
                from_numpy_array,
                to_numpy_array,
                from_scipy_sparse_array,
            )

            self._from_numpy_array = from_numpy_array
            self._to_numpy_array = to_numpy_array
            self._from_scipy_sparse_array = from_scipy_sparse_array
            self._available = True
            self._import_error = None
        except Exception as exc:
            self._available = False
            self._import_error = str(exc)

    def _ok(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, error: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error:
            payload["error"] = error
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        guidance = (
            "Import mode is unavailable. Ensure repository source is present at "
            f"'{source_path}', verify Python >= 3.11, and optional dependencies "
            "(numpy/scipy) are installed for matrix conversions."
        )
        return self._fail(
            message=f"Cannot execute '{action}' because required imports failed.",
            error=f"{self._import_error or 'Unknown import error'}. {guidance}",
        )

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import diagnostics.

        Returns:
            dict: Unified status dictionary with import availability and error details.
        """
        if self._available:
            return self._ok(
                data={
                    "import_available": True,
                    "module": "networkx.convert_matrix",
                    "functions": [
                        "from_numpy_array",
                        "to_numpy_array",
                        "from_scipy_sparse_array",
                    ],
                },
                message="Adapter is ready in import mode.",
            )
        return self._fail(
            message="Adapter is running but imports are unavailable.",
            error=self._import_error or "Unknown import error.",
        )

    # -------------------------------------------------------------------------
    # Function wrappers: networkx.convert_matrix
    # -------------------------------------------------------------------------
    def call_from_numpy_array(
        self,
        A: Any,
        parallel_edges: bool = False,
        create_using: Any = None,
        edge_attr: str = "weight",
        nodelist: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Build a NetworkX graph from a NumPy 2D array.

        Parameters:
            A: numpy.ndarray-like
                Input adjacency matrix.
            parallel_edges: bool, default=False
                If True and create_using is a multigraph, matrix entries may represent parallel edges.
            create_using: Graph constructor or graph instance, optional
                Graph type to create (e.g., nx.Graph, nx.DiGraph, nx.MultiGraph).
            edge_attr: str, default="weight"
                Edge attribute name used to store matrix values.
            nodelist: iterable, optional
                Node labels corresponding to matrix rows/columns.

        Returns:
            dict: Unified status dictionary with created graph in `data`.
        """
        if not self._available or self._from_numpy_array is None:
            return self._fallback("from_numpy_array")
        try:
            graph = self._from_numpy_array(
                A,
                parallel_edges=parallel_edges,
                create_using=create_using,
                edge_attr=edge_attr,
                nodelist=nodelist,
            )
            return self._ok(data=graph, message="Graph created from NumPy array.")
        except Exception as exc:
            return self._fail(
                message="Failed to create graph from NumPy array.",
                error=f"Check array shape/type and optional parameters. Details: {exc}",
            )

    def call_to_numpy_array(
        self,
        G: Any,
        nodelist: Optional[Any] = None,
        dtype: Any = None,
        order: Optional[str] = None,
        multigraph_weight: Any = sum,
        weight: str = "weight",
        nonedge: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Convert a NetworkX graph to a NumPy 2D array.

        Parameters:
            G: networkx.Graph-like
                Input graph.
            nodelist: iterable, optional
                Node order to use for rows/columns.
            dtype: numpy dtype, optional
                Desired output dtype.
            order: {'C', 'F'}, optional
                Memory order.
            multigraph_weight: callable, default=sum
                Reducer for parallel edge weights in multigraphs.
            weight: str, default='weight'
                Edge attribute used as numeric value.
            nonedge: float, default=0.0
                Fill value for non-edges.

        Returns:
            dict: Unified status dictionary with resulting NumPy array in `data`.
        """
        if not self._available or self._to_numpy_array is None:
            return self._fallback("to_numpy_array")
        try:
            arr = self._to_numpy_array(
                G,
                nodelist=nodelist,
                dtype=dtype,
                order=order,
                multigraph_weight=multigraph_weight,
                weight=weight,
                nonedge=nonedge,
            )
            return self._ok(data=arr, message="NumPy array generated from graph.")
        except Exception as exc:
            return self._fail(
                message="Failed to convert graph to NumPy array.",
                error=f"Validate graph object and conversion parameters. Details: {exc}",
            )

    def call_from_scipy_sparse_array(
        self,
        A: Any,
        parallel_edges: bool = False,
        create_using: Any = None,
        edge_attribute: str = "weight",
    ) -> Dict[str, Any]:
        """
        Build a NetworkX graph from a SciPy sparse array/matrix.

        Parameters:
            A: scipy.sparse array/matrix
                Input sparse adjacency structure.
            parallel_edges: bool, default=False
                Whether sparse entries may encode parallel edge multiplicity for multigraph targets.
            create_using: Graph constructor or graph instance, optional
                Graph type to create.
            edge_attribute: str, default='weight'
                Edge attribute name for sparse values.

        Returns:
            dict: Unified status dictionary with created graph in `data`.
        """
        if not self._available or self._from_scipy_sparse_array is None:
            return self._fallback("from_scipy_sparse_array")
        try:
            graph = self._from_scipy_sparse_array(
                A,
                parallel_edges=parallel_edges,
                create_using=create_using,
                edge_attribute=edge_attribute,
            )
            return self._ok(data=graph, message="Graph created from SciPy sparse array.")
        except Exception as exc:
            return self._fail(
                message="Failed to create graph from SciPy sparse array.",
                error=f"Ensure scipy is installed and sparse input is valid. Details: {exc}",
            )