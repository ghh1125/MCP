import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for repository: root-11/graph-theory

    This adapter dynamically imports available modules from the local source tree and exposes:
    - class instantiation methods
    - function invocation methods
    - module discovery and health checks

    All public methods return a unified dictionary:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "fallback",
        ...payload...
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._module_registry = self._build_module_registry()
        self._modules: Dict[str, Any] = {}
        self._load_errors: Dict[str, str] = {}
        self._discover_and_import_modules()

    # -------------------------------------------------------------------------
    # Internal Utilities
    # -------------------------------------------------------------------------

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        base = {"status": "success", "mode": self.mode}
        base.update(kwargs)
        return base

    def _fallback(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        base = {"status": "fallback", "mode": "fallback", "message": message}
        base.update(kwargs)
        return base

    def _err(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> Dict[str, Any]:
        base = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            base["error"] = str(error)
        base.update(kwargs)
        return base

    def _build_module_registry(self) -> List[str]:
        return [
            "graph.adjacency_matrix",
            "graph.all_pairs_shortest_path",
            "graph.all_paths",
            "graph.all_simple_paths",
            "graph.assignment_problem",
            "graph.base",
            "graph.bfs",
            "graph.core",
            "graph.critical_path",
            "graph.cycle",
            "graph.dag",
            "graph.degree_of_separation",
            "graph.dfs",
            "graph.distance_map",
            "graph.finite_state_machine",
            "graph.hash_methods",
            "graph.max_flow",
            "graph.max_flow_min_cut",
            "graph.maximum_flow_min_cut",
            "graph.min_cost_flow",
            "graph.minmax",
            "graph.minsum",
            "graph.partite",
            "graph.random",
            "graph.shortest_path",
            "graph.shortest_tree_all_pairs",
            "graph.topological_sort",
            "graph.traffic_scheduling_problem",
            "graph.transshipment_problem",
            "graph.tsp",
            "graph.visuals",
            "graph.version",
        ]

    def _discover_and_import_modules(self) -> None:
        for mod_name in self._module_registry:
            try:
                self._modules[mod_name] = importlib.import_module(mod_name)
            except Exception as e:
                self._load_errors[mod_name] = str(e)

        if not self._modules:
            self.mode = "fallback"

    def _get_module(self, module_name: str) -> Any:
        return self._modules.get(module_name)

    def _call_symbol(self, module_name: str, symbol_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        module = self._get_module(module_name)
        if module is None:
            if self.mode == "fallback":
                return self._fallback(
                    f"Module '{module_name}' is unavailable. Verify source path and dependencies, then retry.",
                    module=module_name,
                    symbol=symbol_name,
                )
            return self._err(
                f"Module '{module_name}' failed to import. Check installation and optional dependencies.",
                module=module_name,
                symbol=symbol_name,
                load_error=self._load_errors.get(module_name),
            )

        symbol = getattr(module, symbol_name, None)
        if symbol is None:
            return self._err(
                f"Symbol '{symbol_name}' not found in module '{module_name}'. Use inspect_module_symbols for discovery.",
                module=module_name,
                symbol=symbol_name,
            )

        try:
            result = symbol(*args, **kwargs)
            return self._ok(module=module_name, symbol=symbol_name, result=result)
        except Exception as e:
            return self._err(
                f"Execution failed for '{module_name}.{symbol_name}'. Validate parameters and graph object types.",
                error=e,
                module=module_name,
                symbol=symbol_name,
            )

    def _instantiate_symbol(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        module = self._get_module(module_name)
        if module is None:
            if self.mode == "fallback":
                return self._fallback(
                    f"Module '{module_name}' is unavailable. Verify source path and dependencies, then retry.",
                    module=module_name,
                    symbol=class_name,
                )
            return self._err(
                f"Module '{module_name}' failed to import. Check installation and optional dependencies.",
                module=module_name,
                symbol=class_name,
                load_error=self._load_errors.get(module_name),
            )

        cls = getattr(module, class_name, None)
        if cls is None or not inspect.isclass(cls):
            return self._err(
                f"Class '{class_name}' not found in module '{module_name}'. Use inspect_module_symbols for discovery.",
                module=module_name,
                symbol=class_name,
            )

        try:
            instance = cls(*args, **kwargs)
            return self._ok(module=module_name, symbol=class_name, instance=instance)
        except Exception as e:
            return self._err(
                f"Instantiation failed for '{module_name}.{class_name}'. Validate constructor arguments.",
                error=e,
                module=module_name,
                symbol=class_name,
            )

    # -------------------------------------------------------------------------
    # Health / Discovery
    # -------------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness, import mode, and module import status.

        Returns:
            dict: Unified status dictionary with loaded modules and import failures.
        """
        return self._ok(
            adapter="graph-theory",
            loaded_count=len(self._modules),
            failed_count=len(self._load_errors),
            loaded_modules=sorted(self._modules.keys()),
            failed_modules=self._load_errors,
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List all configured target modules and their import status.

        Returns:
            dict: Registry and status split into loaded and failed.
        """
        return self._ok(
            configured_modules=self._module_registry,
            loaded_modules=sorted(self._modules.keys()),
            failed_modules=self._load_errors,
        )

    def inspect_module_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        Inspect callable functions and classes for a module.

        Args:
            module_name (str): Full module path, e.g. 'graph.shortest_path'.

        Returns:
            dict: Functions/classes discovered in the module.
        """
        module = self._get_module(module_name)
        if module is None:
            return self._err(
                f"Module '{module_name}' is not loaded. Call list_modules to inspect availability.",
                module=module_name,
                load_error=self._load_errors.get(module_name),
            )

        functions = []
        classes = []
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            if inspect.isfunction(obj):
                functions.append(name)
            elif inspect.isclass(obj) and obj.__module__ == module.__name__:
                classes.append(name)

        return self._ok(module=module_name, functions=functions, classes=classes)

    # -------------------------------------------------------------------------
    # Generic Invocation APIs (full coverage fallback for all module symbols)
    # -------------------------------------------------------------------------

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from a loaded graph.* module.

        Args:
            module_name (str): Full module path, e.g. 'graph.bfs'.
            function_name (str): Function name in module.
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: Unified status with function result.
        """
        return self._call_symbol(module_name, function_name, *args, **kwargs)

    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class from a loaded graph.* module.

        Args:
            module_name (str): Full module path, e.g. 'graph.core'.
            class_name (str): Class name in module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status with created instance.
        """
        return self._instantiate_symbol(module_name, class_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dedicated Module Methods
    # -------------------------------------------------------------------------

    def call_graph_adjacency_matrix(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.adjacency_matrix", function_name, *args, **kwargs)

    def call_graph_all_pairs_shortest_path(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.all_pairs_shortest_path", function_name, *args, **kwargs)

    def call_graph_all_paths(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.all_paths", function_name, *args, **kwargs)

    def call_graph_all_simple_paths(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.all_simple_paths", function_name, *args, **kwargs)

    def call_graph_assignment_problem(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.assignment_problem", function_name, *args, **kwargs)

    def call_graph_base(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.base", function_name, *args, **kwargs)

    def call_graph_bfs(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.bfs", function_name, *args, **kwargs)

    def call_graph_core(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.core", function_name, *args, **kwargs)

    def call_graph_critical_path(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.critical_path", function_name, *args, **kwargs)

    def call_graph_cycle(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.cycle", function_name, *args, **kwargs)

    def call_graph_dag(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.dag", function_name, *args, **kwargs)

    def call_graph_degree_of_separation(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.degree_of_separation", function_name, *args, **kwargs)

    def call_graph_dfs(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.dfs", function_name, *args, **kwargs)

    def call_graph_distance_map(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.distance_map", function_name, *args, **kwargs)

    def call_graph_finite_state_machine(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.finite_state_machine", function_name, *args, **kwargs)

    def call_graph_hash_methods(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.hash_methods", function_name, *args, **kwargs)

    def call_graph_max_flow(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.max_flow", function_name, *args, **kwargs)

    def call_graph_max_flow_min_cut(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.max_flow_min_cut", function_name, *args, **kwargs)

    def call_graph_maximum_flow_min_cut(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.maximum_flow_min_cut", function_name, *args, **kwargs)

    def call_graph_min_cost_flow(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.min_cost_flow", function_name, *args, **kwargs)

    def call_graph_minmax(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.minmax", function_name, *args, **kwargs)

    def call_graph_minsum(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.minsum", function_name, *args, **kwargs)

    def call_graph_partite(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.partite", function_name, *args, **kwargs)

    def call_graph_random(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.random", function_name, *args, **kwargs)

    def call_graph_shortest_path(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.shortest_path", function_name, *args, **kwargs)

    def call_graph_shortest_tree_all_pairs(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.shortest_tree_all_pairs", function_name, *args, **kwargs)

    def call_graph_topological_sort(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.topological_sort", function_name, *args, **kwargs)

    def call_graph_traffic_scheduling_problem(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.traffic_scheduling_problem", function_name, *args, **kwargs)

    def call_graph_transshipment_problem(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.transshipment_problem", function_name, *args, **kwargs)

    def call_graph_tsp(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.tsp", function_name, *args, **kwargs)

    def call_graph_visuals(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.visuals", function_name, *args, **kwargs)

    def call_graph_version(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("graph.version", function_name, *args, **kwargs)