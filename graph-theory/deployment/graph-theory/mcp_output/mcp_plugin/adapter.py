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
    Import-mode adapter for the graph-theory repository.

    This adapter attempts direct imports from the local `source` directory and provides:
    - Unified status dictionaries for all calls
    - Safe fallback behavior when imports or calls fail
    - Module management helpers
    - Generic function/class invocation for broad repository coverage
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._module_names: List[str] = [
            "examples.graphs",
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
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _ok(self, data: Any = None, message: str = "success", **extra: Any) -> Dict[str, Any]:
        result = {"status": "success", "message": message, "data": data}
        result.update(extra)
        return result

    def _err(self, message: str, **extra: Any) -> Dict[str, Any]:
        result = {"status": "error", "message": message}
        result.update(extra)
        return result

    def _load_modules(self) -> None:
        for name in self._module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors[name] = str(e)

    def _get_module(self, module_name: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        mod = self._modules.get(module_name)
        if mod is None:
            if module_name in self._import_errors:
                return None, self._err(
                    f"Module '{module_name}' is unavailable.",
                    guidance=(
                        "Check local source integrity and dependencies. "
                        "If module needs optional packages (e.g., matplotlib/numpy), install them."
                    ),
                    import_error=self._import_errors[module_name],
                )
            return None, self._err(
                f"Module '{module_name}' was not loaded.",
                guidance="Verify module name and ensure it exists under source path.",
            )
        return mod, None

    def _resolve_callable(self, module_name: str, attr_name: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        mod, err = self._get_module(module_name)
        if err:
            return None, err
        if not hasattr(mod, attr_name):
            return None, self._err(
                f"Attribute '{attr_name}' not found in module '{module_name}'.",
                guidance="Use list_module_symbols to inspect available names before calling.",
            )
        obj = getattr(mod, attr_name)
        if not callable(obj):
            return None, self._err(
                f"Attribute '{attr_name}' in module '{module_name}' is not callable.",
                guidance="Use get_attribute for constants/variables, or call a callable symbol.",
                attribute_type=type(obj).__name__,
            )
        return obj, None

    # -------------------------------------------------------------------------
    # Module management
    # -------------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._ok(
            data={
                "mode": self.mode,
                "loaded_modules": sorted(self._modules.keys()),
                "failed_modules": self._import_errors,
                "source_path": source_path,
            },
            message="adapter health report generated",
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List all configured modules and import status.
        """
        data = []
        for m in self._module_names:
            data.append(
                {
                    "module": m,
                    "loaded": m in self._modules,
                    "error": self._import_errors.get(m),
                }
            )
        return self._ok(data=data, message="module status listed")

    def list_module_symbols(self, module_name: str, public_only: bool = True) -> Dict[str, Any]:
        """
        List symbols in a module.

        Parameters:
        - module_name: Full module path from repository (e.g., 'graph.core').
        - public_only: If True, hide names starting with underscore.
        """
        mod, err = self._get_module(module_name)
        if err:
            return err
        names = dir(mod)
        if public_only:
            names = [n for n in names if not n.startswith("_")]
        return self._ok(data=sorted(names), module=module_name, message="module symbols listed")

    def get_attribute(self, module_name: str, attr_name: str) -> Dict[str, Any]:
        """
        Return non-callable attribute from a module.

        Useful for constants such as version values.
        """
        mod, err = self._get_module(module_name)
        if err:
            return err
        if not hasattr(mod, attr_name):
            return self._err(
                f"Attribute '{attr_name}' not found in module '{module_name}'.",
                guidance="Use list_module_symbols to inspect available names.",
            )
        val = getattr(mod, attr_name)
        return self._ok(
            data={"repr": repr(val), "type": type(val).__name__, "value": val},
            module=module_name,
            attribute=attr_name,
            message="attribute fetched",
        )

    # -------------------------------------------------------------------------
    # Generic invocation APIs (full coverage fallback)
    # -------------------------------------------------------------------------

    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a repository module.

        Parameters:
        - module_name: Full module path (e.g., 'graph.core')
        - class_name: Class symbol name in that module
        - *args, **kwargs: Constructor arguments

        Returns:
        - Unified dictionary with status and instance metadata.
        """
        cls, err = self._resolve_callable(module_name, class_name)
        if err:
            return err
        if not inspect.isclass(cls):
            return self._err(
                f"Symbol '{class_name}' in module '{module_name}' is not a class.",
                guidance="Use call_function for functions or verify symbol type with list_module_symbols.",
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(
                data=instance,
                instance_type=type(instance).__name__,
                module=module_name,
                class_name=class_name,
                message="instance created",
            )
        except Exception as e:
            return self._err(
                f"Failed to instantiate '{module_name}.{class_name}'.",
                guidance="Validate constructor arguments and required dependencies.",
                error=str(e),
            )

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a repository module.

        Parameters:
        - module_name: Full module path (e.g., 'graph.shortest_path')
        - function_name: Function symbol name in that module
        - *args, **kwargs: Function arguments

        Returns:
        - Unified dictionary with call result.
        """
        fn, err = self._resolve_callable(module_name, function_name)
        if err:
            return err
        if inspect.isclass(fn):
            return self._err(
                f"Symbol '{function_name}' in module '{module_name}' is a class, not a function.",
                guidance="Use create_instance for class construction.",
            )
        try:
            out = fn(*args, **kwargs)
            return self._ok(
                data=out,
                module=module_name,
                function=function_name,
                message="function call completed",
            )
        except Exception as e:
            return self._err(
                f"Function call failed for '{module_name}.{function_name}'.",
                guidance="Check argument types/shapes and repository function contract.",
                error=str(e),
            )

    # -------------------------------------------------------------------------
    # Repository-oriented convenience wrappers
    # -------------------------------------------------------------------------

    def create_graph_class(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a graph class instance by searching common graph modules.

        Search order:
        graph.core, graph.base, graph.hash_methods, graph.finite_state_machine
        """
        search_modules = ["graph.core", "graph.base", "graph.hash_methods", "graph.finite_state_machine"]
        for m in search_modules:
            mod, _ = self._get_module(m)
            if mod and hasattr(mod, class_name) and inspect.isclass(getattr(mod, class_name)):
                return self.create_instance(m, class_name, *args, **kwargs)
        return self._err(
            f"Graph class '{class_name}' not found in common modules.",
            guidance="Call create_instance with explicit module path after list_module_symbols inspection.",
        )

    def run_algorithm(self, module_name: str, algorithm_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute an algorithm function in a specific module.
        """
        return self.call_function(module_name, algorithm_name, *args, **kwargs)

    def get_version(self) -> Dict[str, Any]:
        """
        Retrieve version metadata from graph.version.
        """
        mod, err = self._get_module("graph.version")
        if err:
            return err
        candidates = ["__version__", "VERSION", "version"]
        payload = {}
        for c in candidates:
            if hasattr(mod, c):
                payload[c] = getattr(mod, c)
        if not payload:
            return self._err(
                "No version symbol found in 'graph.version'.",
                guidance="Inspect graph.version symbols using list_module_symbols.",
            )
        return self._ok(data=payload, message="version metadata fetched")

    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide fallback guidance when import mode is partially unavailable.
        """
        return self._ok(
            data={
                "mode": self.mode,
                "failed_modules": self._import_errors,
                "recommendations": [
                    "Install optional dependencies for advanced modules (matplotlib, numpy).",
                    "Ensure source path is correct and contains the repository files.",
                    "Use list_modules and list_module_symbols to find available APIs.",
                    "Use generic call_function/create_instance when exact API signatures are unknown.",
                ],
            },
            message="fallback guidance prepared",
        )