import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for python-igraph repository.

    This adapter attempts to import project modules directly from the local source tree.
    It provides:
    - module-level health checks
    - safe wrappers around key runtime functionality
    - graceful fallback responses when imports are unavailable
    """

    # =========================
    # Initialization & Utilities
    # =========================

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: str = "", error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if guidance:
            payload["guidance"] = guidance
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = str(error)
        return payload

    def _load_modules(self) -> None:
        targets = {
            "igraph": "igraph",
            "igraph_app_shell": "igraph.app.shell",
            "igraph_drawing_matplotlib_graph": "igraph.drawing.matplotlib.graph",
            "igraph_drawing_plotly_graph": "igraph.drawing.plotly.graph",
            "igraph_drawing_cairo_graph": "igraph.drawing.cairo.graph",
        }
        for key, module_path in targets.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter and import health status.

        Returns:
            dict: Unified status dictionary containing loaded modules and import errors.
        """
        loaded = sorted(self._modules.keys())
        return self._ok(
            {
                "loaded_modules": loaded,
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            message="adapter initialized",
        )

    # =========================
    # Fallback & Guards
    # =========================

    def _require(self, key: str, module_hint: str) -> Optional[Dict[str, Any]]:
        if key not in self._modules:
            details = self._import_errors.get(key, "module not loaded")
            return self._err(
                message=f"Required module '{module_hint}' is unavailable.",
                guidance=(
                    "Ensure the repository source exists under the configured 'source' directory, "
                    "and required runtime dependencies are installed. Verify compiled igraph backend availability."
                ),
                error=RuntimeError(details),
            )
        return None

    # =========================
    # Core igraph constructors
    # =========================

    def instance_graph(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an igraph.Graph instance.

        Parameters:
            *args: Positional arguments forwarded to igraph.Graph(...)
            **kwargs: Keyword arguments forwarded to igraph.Graph(...)

        Returns:
            dict: status + graph metadata, and graph object under 'instance'.
        """
        pre = self._require("igraph", "igraph")
        if pre:
            return pre
        try:
            Graph = getattr(self._modules["igraph"], "Graph")
            g = Graph(*args, **kwargs)
            return self._ok(
                {
                    "instance": g,
                    "vertex_count": g.vcount(),
                    "edge_count": g.ecount(),
                    "is_directed": g.is_directed(),
                },
                message="Graph instance created",
            )
        except Exception as exc:
            return self._err("Failed to create Graph instance.", "Check Graph constructor arguments.", exc)

    def instance_configuration(self) -> Dict[str, Any]:
        """
        Create an igraph.Configuration instance.

        Returns:
            dict: status + configuration object.
        """
        pre = self._require("igraph", "igraph")
        if pre:
            return pre
        try:
            Configuration = getattr(self._modules["igraph"], "Configuration", None)
            if Configuration is None:
                return self._err(
                    "Configuration class not found in igraph module.",
                    "Verify repository version exports Configuration in igraph.__init__.",
                )
            cfg = Configuration.instance() if hasattr(Configuration, "instance") else Configuration()
            return self._ok({"instance": cfg}, message="Configuration instance created")
        except Exception as exc:
            return self._err("Failed to create Configuration instance.", "Check igraph runtime installation.", exc)

    # =========================
    # Core graph operations
    # =========================

    def call_graph_factory(self, factory_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a Graph factory/class method dynamically (e.g., Erdos_Renyi, Ring, Full, Tree, etc.).

        Parameters:
            factory_name (str): Name of igraph.Graph class method.
            *args, **kwargs: Passed to selected factory.

        Returns:
            dict: status + graph metadata + graph object.
        """
        pre = self._require("igraph", "igraph")
        if pre:
            return pre
        try:
            Graph = getattr(self._modules["igraph"], "Graph")
            if not hasattr(Graph, factory_name):
                return self._err(
                    f"Graph factory '{factory_name}' is not available.",
                    "Use a valid Graph class method name from your repository version.",
                )
            fn = getattr(Graph, factory_name)
            g = fn(*args, **kwargs)
            return self._ok(
                {
                    "graph": g,
                    "factory": factory_name,
                    "vertex_count": g.vcount(),
                    "edge_count": g.ecount(),
                    "is_directed": g.is_directed(),
                },
                message="Graph factory call executed",
            )
        except Exception as exc:
            return self._err(
                f"Failed to execute Graph factory '{factory_name}'.",
                "Validate factory arguments and method name.",
                exc,
            )

    def call_graph_method(self, graph: Any, method_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any method on an existing Graph instance safely.

        Parameters:
            graph: igraph.Graph instance.
            method_name (str): Target method to invoke.
            *args, **kwargs: Forwarded to graph method.

        Returns:
            dict: status + method result.
        """
        try:
            if graph is None:
                return self._err("Graph instance is required.", "Provide a valid igraph.Graph object.")
            if not hasattr(graph, method_name):
                return self._err(
                    f"Graph method '{method_name}' does not exist.",
                    "Check method spelling and repository API compatibility.",
                )
            result = getattr(graph, method_name)(*args, **kwargs)
            return self._ok({"result": result, "method": method_name}, message="Graph method executed")
        except Exception as exc:
            return self._err(
                f"Failed to execute graph method '{method_name}'.",
                "Inspect argument types and graph state before retrying.",
                exc,
            )

    # =========================
    # Drawing backends (optional)
    # =========================

    def call_plot(self, graph: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call igraph.plot(...) helper.

        Parameters:
            graph: igraph.Graph instance.
            *args, **kwargs: plotting parameters (backend-specific).

        Returns:
            dict: status + plot object/result when available.
        """
        pre = self._require("igraph", "igraph")
        if pre:
            return pre
        try:
            plot_fn = getattr(self._modules["igraph"], "plot")
            out = plot_fn(graph, *args, **kwargs)
            return self._ok({"result": out}, message="Plot executed")
        except Exception as exc:
            return self._err(
                "Failed to plot graph.",
                "Install optional drawing dependencies (matplotlib, plotly, or cairo backend) and verify parameters.",
                exc,
            )

    # =========================
    # CLI-like component wrapper
    # =========================

    def call_shell_main(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Attempt to invoke igraph.app.shell main-like entry.

        Parameters:
            argv (list[str] | None): Optional argument vector.

        Returns:
            dict: status + execution result.
        """
        pre = self._require("igraph_app_shell", "igraph.app.shell")
        if pre:
            return pre
        try:
            mod = self._modules["igraph_app_shell"]
            # Best-effort entry resolution
            for candidate in ("main", "run", "start"):
                if hasattr(mod, candidate):
                    fn = getattr(mod, candidate)
                    result = fn(argv) if argv is not None else fn()
                    return self._ok(
                        {"entry": candidate, "result": result},
                        message="Shell entry executed",
                    )
            return self._err(
                "No callable shell entry point found.",
                "Expected one of: main, run, start in igraph.app.shell.",
            )
        except Exception as exc:
            return self._err(
                "Failed to execute igraph shell module.",
                "Review shell module API and pass compatible arguments.",
                exc,
            )

    # =========================
    # Generic dynamic access
    # =========================

    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically import a module and call a function by name.

        Parameters:
            module_path (str): Full import path under repository source (e.g., 'igraph.io.files').
            function_name (str): Function to call.
            *args, **kwargs: Arguments for function call.

        Returns:
            dict: status + function call result.
        """
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, function_name):
                return self._err(
                    f"Function '{function_name}' not found in module '{module_path}'.",
                    "Verify module path and exported symbol name.",
                )
            fn = getattr(module, function_name)
            result = fn(*args, **kwargs)
            return self._ok(
                {
                    "module": module_path,
                    "function": function_name,
                    "result": result,
                },
                message="Dynamic function call executed",
            )
        except Exception as exc:
            return self._err(
                f"Failed to call '{function_name}' from '{module_path}'.",
                "Check dependency availability and function arguments.",
                exc,
            )

    def call_module_class(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically import a module and instantiate a class by name.

        Parameters:
            module_path (str): Full import path under repository source.
            class_name (str): Class to instantiate.
            *args, **kwargs: Constructor arguments.

        Returns:
            dict: status + class instance.
        """
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, class_name):
                return self._err(
                    f"Class '{class_name}' not found in module '{module_path}'.",
                    "Verify class name and module export.",
                )
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                {
                    "module": module_path,
                    "class": class_name,
                    "instance": instance,
                },
                message="Dynamic class instantiation executed",
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate '{class_name}' from '{module_path}'.",
                "Validate constructor arguments and module dependencies.",
                exc,
            )

    # =========================
    # Diagnostics
    # =========================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Provide detailed diagnostics for troubleshooting import-mode execution.

        Returns:
            dict: status + traceback-safe environment summary.
        """
        try:
            return self._ok(
                {
                    "python_executable": sys.executable,
                    "python_version": sys.version,
                    "sys_path_head": sys.path[:5],
                    "source_path_exists": os.path.isdir(source_path),
                    "loaded_modules": list(self._modules.keys()),
                    "import_errors": self._import_errors,
                },
                message="Diagnostics collected",
            )
        except Exception as exc:
            return self._err(
                "Failed to collect diagnostics.",
                "Retry in a clean environment and verify file-system permissions.",
                exc,
            )

    def last_exception_trace(self, error: Exception) -> Dict[str, Any]:
        """
        Convert an exception into a unified trace payload.

        Parameters:
            error (Exception): Exception object.

        Returns:
            dict: status + concise traceback information.
        """
        try:
            tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            return self._ok({"traceback": tb}, message="Traceback captured")
        except Exception as exc:
            return self._err(
                "Failed to serialize traceback.",
                "Pass a valid Exception instance.",
                exc,
            )