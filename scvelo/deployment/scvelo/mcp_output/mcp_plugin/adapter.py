import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional, Callable

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the scvelo repository.

    This adapter dynamically imports scvelo modules from local source and exposes
    a rich set of wrapper methods that return a unified response dictionary.

    Response format:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "blackbox",
        "message": str,
        "data": Any,
        "error": str | None,
        "hint": str | None
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._module_cache: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._known_modules: List[str] = [
            "scvelo",
            "scvelo.core",
            "scvelo.datasets",
            "scvelo.inference",
            "scvelo.logging",
            "scvelo.plotting",
            "scvelo.preprocessing",
            "scvelo.tools",
            "scvelo.read_load",
            "scvelo.settings",
            "scvelo.utils",
        ]
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Any = None,
        error: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
            "error": error,
            "hint": hint,
        }

    def _initialize_modules(self) -> None:
        for mod in self._known_modules:
            try:
                self._module_cache[mod] = importlib.import_module(mod)
            except Exception as e:
                self._import_errors[mod] = str(e)

        if self._import_errors:
            self.mode = "blackbox"

    def _load_module(self, module_path: str):
        if module_path in self._module_cache:
            return self._module_cache[module_path]
        try:
            mod = importlib.import_module(module_path)
            self._module_cache[module_path] = mod
            return mod
        except Exception as e:
            self._import_errors[module_path] = str(e)
            return None

    def _resolve_attr(self, module_path: str, attr_name: str) -> Dict[str, Any]:
        mod = self._load_module(module_path)
        if mod is None:
            return self._result(
                "fallback",
                f"Module import failed: {module_path}",
                error=self._import_errors.get(module_path),
                hint="Check local repository source path and required dependencies.",
            )
        if not hasattr(mod, attr_name):
            return self._result(
                "error",
                f"Attribute not found: {module_path}.{attr_name}",
                error=f"{attr_name} is not available in {module_path}",
                hint="Call list_module_symbols() to inspect available functions.",
            )
        return self._result(
            "success",
            f"Resolved attribute {module_path}.{attr_name}",
            data=getattr(mod, attr_name),
        )

    def _safe_call(
        self,
        module_path: str,
        func_name: str,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:
        resolved = self._resolve_attr(module_path, func_name)
        if resolved["status"] != "success":
            return resolved
        fn = resolved["data"]
        if not callable(fn):
            return self._result(
                "error",
                f"Target is not callable: {module_path}.{func_name}",
                error="Resolved attribute is not a function or callable object.",
                hint="Verify API symbol type using inspect_symbol().",
            )
        try:
            output = fn(*args, **kwargs)
            return self._result(
                "success",
                f"Executed {module_path}.{func_name} successfully.",
                data=output,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Execution failed for {module_path}.{func_name}.",
                error=str(e),
                hint="Validate input types and required AnnData structure.",
            )

    # -------------------------------------------------------------------------
    # Adapter diagnostics and module management
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check import readiness and return adapter health details.

        Returns:
            dict: Unified status dictionary with imported modules and errors.
        """
        return self._result(
            "success" if self.mode == "import" else "fallback",
            "Adapter health evaluated.",
            data={
                "mode": self.mode,
                "imported_modules": sorted(list(self._module_cache.keys())),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            hint=(
                None
                if self.mode == "import"
                else "Install missing dependencies such as anndata, scanpy, numpy, scipy, pandas, matplotlib, scikit-learn, numba, h5py, joblib."
            ),
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List known scvelo modules handled by this adapter.
        """
        return self._result(
            "success",
            "Known modules listed.",
            data={"known_modules": self._known_modules},
        )

    def list_module_symbols(self, module_path: str) -> Dict[str, Any]:
        """
        List public symbols in a module.

        Args:
            module_path: Full module import path (e.g., 'scvelo.tools').

        Returns:
            dict: Unified response with public symbols.
        """
        mod = self._load_module(module_path)
        if mod is None:
            return self._result(
                "fallback",
                f"Cannot import module: {module_path}",
                error=self._import_errors.get(module_path),
                hint="Ensure optional dependencies for this submodule are available.",
            )
        symbols = [x for x in dir(mod) if not x.startswith("_")]
        return self._result(
            "success",
            f"Symbols listed for module: {module_path}",
            data={"symbols": symbols},
        )

    def inspect_symbol(self, module_path: str, symbol_name: str) -> Dict[str, Any]:
        """
        Inspect a symbol signature and docstring.

        Args:
            module_path: Module path.
            symbol_name: Symbol within module.

        Returns:
            dict: Signature and docstring if available.
        """
        resolved = self._resolve_attr(module_path, symbol_name)
        if resolved["status"] != "success":
            return resolved
        obj = resolved["data"]
        sig = None
        try:
            sig = str(inspect.signature(obj))
        except Exception:
            sig = "Signature unavailable"
        doc = inspect.getdoc(obj) or "No docstring available."
        return self._result(
            "success",
            f"Inspected symbol {module_path}.{symbol_name}.",
            data={"signature": sig, "doc": doc, "type": str(type(obj))},
        )

    # -------------------------------------------------------------------------
    # Generic execution interfaces
    # -------------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call an arbitrary function in a specified module.

        Args:
            module_path: Full module path.
            function_name: Function to execute.
            *args: Positional arguments passed to target function.
            **kwargs: Keyword arguments passed to target function.

        Returns:
            dict: Unified execution result.
        """
        return self._safe_call(module_path, function_name, *args, **kwargs)

    def create_instance(self, module_path: str, class_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Instantiate a class from a specified module.

        Args:
            module_path: Full module path.
            class_name: Class name to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified response containing instance object on success.
        """
        resolved = self._resolve_attr(module_path, class_name)
        if resolved["status"] != "success":
            return resolved
        cls = resolved["data"]
        if not inspect.isclass(cls):
            return self._result(
                "error",
                f"Target is not a class: {module_path}.{class_name}",
                error="Resolved attribute is not a class.",
                hint="Use call_function() for functions.",
            )
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                "success",
                f"Instantiated class {module_path}.{class_name}.",
                data=instance,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Failed to instantiate {module_path}.{class_name}.",
                error=str(e),
                hint="Verify constructor parameters and dependency availability.",
            )

    # -------------------------------------------------------------------------
    # High-utility wrappers for common scvelo APIs
    # -------------------------------------------------------------------------
    def scvelo_read(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo", "read", *args, **kwargs)

    def scvelo_read_loom(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo", "read_loom", *args, **kwargs)

    def scvelo_set_figure_params(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo", "set_figure_params", *args, **kwargs)

    def pp_filter_and_normalize(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.preprocessing", "filter_and_normalize", *args, **kwargs)

    def pp_moments(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.preprocessing", "moments", *args, **kwargs)

    def pp_neighbors(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.preprocessing", "neighbors", *args, **kwargs)

    def tl_velocity(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "velocity", *args, **kwargs)

    def tl_velocity_graph(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "velocity_graph", *args, **kwargs)

    def tl_velocity_embedding(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "velocity_embedding", *args, **kwargs)

    def tl_velocity_confidence(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "velocity_confidence", *args, **kwargs)

    def tl_recover_dynamics(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "recover_dynamics", *args, **kwargs)

    def tl_rank_velocity_genes(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "rank_velocity_genes", *args, **kwargs)

    def tl_velocity_pseudotime(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "velocity_pseudotime", *args, **kwargs)

    def tl_terminal_states(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "terminal_states", *args, **kwargs)

    def tl_transition_matrix(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.tools", "transition_matrix", *args, **kwargs)

    def pl_scatter(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.plotting", "scatter", *args, **kwargs)

    def pl_velocity_embedding(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.plotting", "velocity_embedding", *args, **kwargs)

    def pl_velocity_embedding_grid(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.plotting", "velocity_embedding_grid", *args, **kwargs)

    def pl_velocity_embedding_stream(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.plotting", "velocity_embedding_stream", *args, **kwargs)

    def pl_velocity_graph(self, *args, **kwargs) -> Dict[str, Any]:
        return self._safe_call("scvelo.plotting", "velocity_graph", *args, **kwargs)

    def datasets_call(self, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute any dataset helper from scvelo.datasets dynamically.

        Args:
            function_name: Dataset function name from scvelo.datasets.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified result.
        """
        return self._safe_call("scvelo.datasets", function_name, *args, **kwargs)