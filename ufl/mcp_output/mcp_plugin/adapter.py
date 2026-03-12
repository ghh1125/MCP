import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for FEniCS UFL repository.

    This adapter prioritizes direct source import from the mounted `source` directory.
    If import fails, it switches to a graceful fallback ("blackbox") mode and returns
    actionable English-only messages.

    Design notes:
    - The analysis result did not provide a concrete machine-readable list of exact
      classes/functions to bind one-by-one.
    - UFL exposes a broad public API primarily through `ufl` package exports.
    - To ensure robust and maintainable coverage, this adapter:
      1) imports the canonical package path (`ufl`)
      2) indexes discovered callables/types from `ufl` and key submodules
      3) provides generic invocation and construction methods
      4) includes explicit convenience wrappers for commonly used UFL APIs
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._errors: List[str] = []
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._classes: Dict[str, Any] = {}
        self._functions: Dict[str, Any] = {}
        self._initialize()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        err = str(error) if error else None
        if error:
            self._errors.append(f"{message}: {err}")
        result = {"status": "error", "mode": self.mode, "message": message}
        if err:
            result["error"] = err
        if hint:
            result["hint"] = hint
        return result

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as e:
            self._errors.append(f"Import failed for {module_path}: {e}")
            return None

    def _initialize(self) -> None:
        # Primary imports using full package path from repository structure.
        core_modules = [
            "ufl",
            "ufl.algorithms",
            "ufl.formoperators",
            "ufl.operators",
            "ufl.finiteelement",
            "ufl.functionspace",
            "ufl.measure",
        ]
        loaded = 0
        for m in core_modules:
            if self._import_module(m) is not None:
                loaded += 1

        if loaded == 0:
            self.mode = "blackbox"
            return

        self._index_symbols()

    def _index_symbols(self) -> None:
        """Index exported symbols from loaded modules for dynamic access."""
        for mod_name, mod in self._modules.items():
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                try:
                    obj = getattr(mod, name)
                except Exception:
                    continue
                fq = f"{mod_name}.{name}"
                self._symbols[fq] = obj
                if isinstance(obj, type):
                    self._classes[fq] = obj
                elif callable(obj):
                    self._functions[fq] = obj

    # -------------------------------------------------------------------------
    # Health and discovery
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter health and import mode.

        Returns:
            dict: Unified status dictionary with loaded modules and error summary.
        """
        if self.mode == "import":
            return self._ok(
                {
                    "loaded_modules": sorted(self._modules.keys()),
                    "indexed_functions": len(self._functions),
                    "indexed_classes": len(self._classes),
                    "errors": self._errors[-10:],
                },
                message="Adapter is ready in import mode.",
            )
        return self._fail(
            "Adapter is running in fallback mode.",
            hint="Ensure repository source is mounted at ../source and contains the `ufl` package.",
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List loaded module paths.

        Returns:
            dict: Module listing in unified format.
        """
        return self._ok({"modules": sorted(self._modules.keys())})

    def list_functions(self, prefix: Optional[str] = None, limit: int = 500) -> Dict[str, Any]:
        """
        List indexed callable symbols.

        Args:
            prefix: Optional fully-qualified prefix filter, e.g. 'ufl.'.
            limit: Max number of entries to return.

        Returns:
            dict: Matching function symbols.
        """
        items = sorted(self._functions.keys())
        if prefix:
            items = [x for x in items if x.startswith(prefix)]
        return self._ok({"functions": items[: max(1, limit)], "count": len(items)})

    def list_classes(self, prefix: Optional[str] = None, limit: int = 500) -> Dict[str, Any]:
        """
        List indexed class symbols.

        Args:
            prefix: Optional fully-qualified prefix filter.
            limit: Max number of entries to return.

        Returns:
            dict: Matching class symbols.
        """
        items = sorted(self._classes.keys())
        if prefix:
            items = [x for x in items if x.startswith(prefix)]
        return self._ok({"classes": items[: max(1, limit)], "count": len(items)})

    # -------------------------------------------------------------------------
    # Generic invocation APIs (comprehensive fallback for large UFL surface)
    # -------------------------------------------------------------------------
    def create_instance(self, qualified_class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance for any indexed class.

        Args:
            qualified_class_name: Full class path, e.g. 'ufl.finiteelement.FiniteElement'.
            *args: Positional args for class constructor.
            **kwargs: Keyword args for class constructor.

        Returns:
            dict: Instance creation result.
        """
        if self.mode != "import":
            return self._fail(
                "Cannot instantiate class in fallback mode.",
                hint="Fix imports and retry. Use health_check() for diagnostics.",
            )
        cls = self._classes.get(qualified_class_name)
        if cls is None:
            return self._fail(
                f"Class not found: {qualified_class_name}",
                hint="Call list_classes() to inspect available class names.",
            )
        try:
            obj = cls(*args, **kwargs)
            return self._ok({"class": qualified_class_name, "instance": obj})
        except Exception as e:
            return self._fail(
                f"Failed to instantiate class: {qualified_class_name}",
                e,
                hint="Verify constructor parameters and types.",
            )

    def call_function(self, qualified_function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any indexed function/callable.

        Args:
            qualified_function_name: Full function path, e.g. 'ufl.grad' or 'ufl.operators.grad'.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Function call result.
        """
        if self.mode != "import":
            return self._fail(
                "Cannot call function in fallback mode.",
                hint="Fix imports and retry. Use health_check() for diagnostics.",
            )
        fn = self._functions.get(qualified_function_name)
        if fn is None:
            return self._fail(
                f"Function not found: {qualified_function_name}",
                hint="Call list_functions() to inspect available function names.",
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok({"function": qualified_function_name, "result": result})
        except Exception as e:
            return self._fail(
                f"Failed to call function: {qualified_function_name}",
                e,
                hint="Check arguments against UFL API expectations.",
            )

    # -------------------------------------------------------------------------
    # Common UFL convenience methods
    # -------------------------------------------------------------------------
    def ufl_symbol(self, name: str) -> Dict[str, Any]:
        """
        Resolve symbol from top-level `ufl` module by name.

        Args:
            name: Symbol name exported by `ufl`.

        Returns:
            dict: Resolved symbol.
        """
        mod = self._modules.get("ufl")
        if mod is None:
            return self._fail("Top-level module `ufl` is not loaded.")
        try:
            sym = getattr(mod, name)
            return self._ok({"name": name, "symbol": sym})
        except Exception as e:
            return self._fail(
                f"Symbol not found in ufl: {name}",
                e,
                hint="Inspect available symbols using list_functions/list_classes.",
            )

    def ufl_call(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call top-level `ufl.<name>` if callable.

        Args:
            name: Top-level callable name in `ufl`.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Call result.
        """
        sym_res = self.ufl_symbol(name)
        if sym_res.get("status") != "success":
            return sym_res
        fn = sym_res["symbol"]
        if not callable(fn):
            return self._fail(
                f"Symbol `ufl.{name}` is not callable.",
                hint="Use ufl_symbol() to retrieve non-callable objects.",
            )
        try:
            return self._ok({"function": f"ufl.{name}", "result": fn(*args, **kwargs)})
        except Exception as e:
            return self._fail(
                f"Failed to call `ufl.{name}`.",
                e,
                hint="Validate argument shapes/types for UFL expressions.",
            )

    def get_last_errors(self, limit: int = 20) -> Dict[str, Any]:
        """
        Retrieve recent adapter errors for debugging.

        Args:
            limit: Number of latest errors to return.

        Returns:
            dict: Error list.
        """
        return self._ok({"errors": self._errors[-max(1, limit):]})

    def debug_trace(self) -> Dict[str, Any]:
        """
        Return a lightweight runtime diagnostics snapshot.

        Returns:
            dict: Mode, module count, symbol counts and last traceback if available.
        """
        try:
            return self._ok(
                {
                    "mode": self.mode,
                    "module_count": len(self._modules),
                    "symbol_count": len(self._symbols),
                    "function_count": len(self._functions),
                    "class_count": len(self._classes),
                }
            )
        except Exception as e:
            return self._fail("Failed to build diagnostics snapshot.", e, hint=traceback.format_exc())