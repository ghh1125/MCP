import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, Callable

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for qpsolvers repository.

    This adapter attempts to import and expose key callable/class APIs from:
      - qpsolvers
      - qpsolvers.solve_qp / solve_problem / solve_ls / solve_unconstrained
      - qpsolvers.problem / problems / solution / active_set / utils / _internals
      - qpsolvers.conversions.*
      - qpsolvers.solvers.*
      - qpsolvers.unsupported.*

    All public methods return a unified dictionary format:
      {
        "status": "success" | "error",
        "mode": "import" | "fallback",
        ...
      }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize adapter in import mode and load target modules.

        Returns
        -------
        None
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _err(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        payload.update(kwargs)
        return payload

    def _safe_import_module(self, module_name: str) -> None:
        try:
            self._modules[module_name] = importlib.import_module(module_name)
        except Exception as e:
            self._import_errors[module_name] = f"{type(e).__name__}: {e}"

    def _initialize_imports(self) -> None:
        module_names = [
            "qpsolvers",
            "qpsolvers.solve_qp",
            "qpsolvers.solve_problem",
            "qpsolvers.solve_ls",
            "qpsolvers.solve_unconstrained",
            "qpsolvers.problem",
            "qpsolvers.problems",
            "qpsolvers.solution",
            "qpsolvers.active_set",
            "qpsolvers.utils",
            "qpsolvers._internals",
            "qpsolvers.conversions",
            "qpsolvers.conversions.combine_linear_box_inequalities",
            "qpsolvers.conversions.ensure_sparse_matrices",
            "qpsolvers.conversions.linear_from_box_inequalities",
            "qpsolvers.conversions.socp_from_qp",
            "qpsolvers.conversions.split_dual_linear_box",
            "qpsolvers.solvers",
            "qpsolvers.unsupported",
            "qpsolvers.unsupported.nppro_",
        ]
        for name in module_names:
            self._safe_import_module(name)

        if len(self._modules) == 0:
            self.mode = "fallback"

        # Collect symbols from imported modules
        for mod_name, mod in self._modules.items():
            try:
                for attr in dir(mod):
                    if attr.startswith("_"):
                        continue
                    obj = getattr(mod, attr)
                    key = f"{mod_name}.{attr}"
                    self._symbols[key] = obj
            except Exception:
                continue

    # -------------------------------------------------------------------------
    # Health and introspection
    # -------------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Check import status and adapter readiness.

        Returns
        -------
        dict
            Unified status dictionary including imported modules and any failures.
        """
        return self._ok(
            adapter="qpsolvers",
            imported_modules=sorted(self._modules.keys()),
            import_failures=self._import_errors,
            available_symbol_count=len(self._symbols),
            guidance=(
                "Install base dependencies: numpy, scipy. "
                "For specific solvers install optional packages (osqp, scs, ecos, cvxopt, etc.)."
            ),
        )

    def list_available_symbols(self, module_filter: str = "") -> Dict[str, Any]:
        """
        List available imported symbols.

        Parameters
        ----------
        module_filter : str, optional
            Filter symbols containing this module/path substring.

        Returns
        -------
        dict
            Unified status dictionary with symbol list.
        """
        symbols = sorted(self._symbols.keys())
        if module_filter:
            symbols = [s for s in symbols if module_filter in s]
        return self._ok(symbols=symbols, count=len(symbols))

    # -------------------------------------------------------------------------
    # Generic invocation utilities
    # -------------------------------------------------------------------------

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from an imported module.

        Parameters
        ----------
        module_path : str
            Full module path (e.g., 'qpsolvers.solve_qp').
        function_name : str
            Function name to call from the target module.
        *args : Any
            Positional arguments for function.
        **kwargs : Any
            Keyword arguments for function.

        Returns
        -------
        dict
            Unified status dictionary with function output or actionable error.
        """
        if self.mode != "import":
            return self._err(
                "Adapter is running in fallback mode. Import target repository into source/ and retry.",
                module_path=module_path,
                function_name=function_name,
            )

        mod = self._modules.get(module_path)
        if mod is None:
            return self._err(
                "Requested module is not available. Check import failures and dependency installation.",
                module_path=module_path,
                import_failures=self._import_errors,
            )
        fn = getattr(mod, function_name, None)
        if fn is None or not callable(fn):
            return self._err(
                "Requested function was not found or is not callable in the target module.",
                module_path=module_path,
                function_name=function_name,
            )
        try:
            result = fn(*args, **kwargs)
            return self._ok(module_path=module_path, function_name=function_name, result=result)
        except Exception as e:
            return self._err(
                "Function invocation failed. Verify argument shapes/types and solver backend availability.",
                module_path=module_path,
                function_name=function_name,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
            )

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from an imported module.

        Parameters
        ----------
        module_path : str
            Full module path.
        class_name : str
            Class name to instantiate.
        *args : Any
            Positional constructor args.
        **kwargs : Any
            Keyword constructor args.

        Returns
        -------
        dict
            Unified status dictionary with created instance.
        """
        if self.mode != "import":
            return self._err(
                "Adapter is running in fallback mode. Import target repository into source/ and retry.",
                module_path=module_path,
                class_name=class_name,
            )

        mod = self._modules.get(module_path)
        if mod is None:
            return self._err(
                "Requested module is not available. Check import failures and dependency installation.",
                module_path=module_path,
                import_failures=self._import_errors,
            )
        cls = getattr(mod, class_name, None)
        if cls is None or not inspect.isclass(cls):
            return self._err(
                "Requested class was not found in the target module.",
                module_path=module_path,
                class_name=class_name,
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(module_path=module_path, class_name=class_name, instance=instance)
        except Exception as e:
            return self._err(
                "Class instantiation failed. Verify constructor arguments and dependency availability.",
                module_path=module_path,
                class_name=class_name,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # qpsolvers primary API wrappers
    # -------------------------------------------------------------------------

    def call_solve_qp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call qpsolvers.solve_qp.solve_qp with full passthrough parameters."""
        return self.call_function("qpsolvers.solve_qp", "solve_qp", *args, **kwargs)

    def call_solve_problem(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call qpsolvers.solve_problem.solve_problem with full passthrough parameters."""
        return self.call_function("qpsolvers.solve_problem", "solve_problem", *args, **kwargs)

    def call_solve_ls(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call qpsolvers.solve_ls.solve_ls with full passthrough parameters."""
        return self.call_function("qpsolvers.solve_ls", "solve_ls", *args, **kwargs)

    def call_solve_unconstrained(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call qpsolvers.solve_unconstrained.solve_unconstrained with full passthrough parameters."""
        return self.call_function("qpsolvers.solve_unconstrained", "solve_unconstrained", *args, **kwargs)

    def call_available_solvers(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call qpsolvers.available_solvers if available."""
        return self.call_function("qpsolvers", "available_solvers", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Conversions wrappers
    # -------------------------------------------------------------------------

    def call_combine_linear_box_inequalities(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "qpsolvers.conversions.combine_linear_box_inequalities",
            "combine_linear_box_inequalities",
            *args,
            **kwargs,
        )

    def call_ensure_sparse_matrices(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "qpsolvers.conversions.ensure_sparse_matrices",
            "ensure_sparse_matrices",
            *args,
            **kwargs,
        )

    def call_linear_from_box_inequalities(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "qpsolvers.conversions.linear_from_box_inequalities",
            "linear_from_box_inequalities",
            *args,
            **kwargs,
        )

    def call_socp_from_qp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function("qpsolvers.conversions.socp_from_qp", "socp_from_qp", *args, **kwargs)

    def call_split_dual_linear_box(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "qpsolvers.conversions.split_dual_linear_box",
            "split_dual_linear_box",
            *args,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Class instance helpers for core modules
    # -------------------------------------------------------------------------

    def instance_problem(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate qpsolvers.problem.Problem if available."""
        return self.create_instance("qpsolvers.problem", "Problem", *args, **kwargs)

    def instance_solution(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate qpsolvers.solution.Solution if available."""
        return self.create_instance("qpsolvers.solution", "Solution", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dynamic access for all imported functions/classes (full coverage fallback)
    # -------------------------------------------------------------------------

    def call_by_symbol(self, symbol_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any imported callable by fully-qualified symbol path.

        Example
        -------
        symbol_path='qpsolvers.solvers.osqp_.osqp_solve_problem'
        """
        if self.mode != "import":
            return self._err(
                "Adapter is running in fallback mode. Import target repository into source/ and retry.",
                symbol_path=symbol_path,
            )
        obj = self._symbols.get(symbol_path)
        if obj is None:
            return self._err(
                "Symbol not found. Use list_available_symbols() to discover valid entries.",
                symbol_path=symbol_path,
            )
        if not callable(obj):
            return self._err(
                "Requested symbol exists but is not callable. Use get_symbol_info() for details.",
                symbol_path=symbol_path,
                symbol_type=str(type(obj)),
            )
        try:
            return self._ok(symbol_path=symbol_path, result=obj(*args, **kwargs))
        except Exception as e:
            return self._err(
                "Callable execution failed. Verify argument compatibility and optional solver dependencies.",
                symbol_path=symbol_path,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
            )

    def instance_by_symbol(self, symbol_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any imported class by fully-qualified symbol path.
        """
        if self.mode != "import":
            return self._err(
                "Adapter is running in fallback mode. Import target repository into source/ and retry.",
                symbol_path=symbol_path,
            )
        obj = self._symbols.get(symbol_path)
        if obj is None:
            return self._err(
                "Symbol not found. Use list_available_symbols() to discover valid entries.",
                symbol_path=symbol_path,
            )
        if not inspect.isclass(obj):
            return self._err(
                "Requested symbol exists but is not a class.",
                symbol_path=symbol_path,
                symbol_type=str(type(obj)),
            )
        try:
            return self._ok(symbol_path=symbol_path, instance=obj(*args, **kwargs))
        except Exception as e:
            return self._err(
                "Class instantiation failed. Verify constructor args and dependencies.",
                symbol_path=symbol_path,
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
            )

    def get_symbol_info(self, symbol_path: str) -> Dict[str, Any]:
        """
        Return metadata (type/doc/signature) for an imported symbol.
        """
        obj = self._symbols.get(symbol_path)
        if obj is None:
            return self._err("Symbol not found.", symbol_path=symbol_path)
        try:
            sig = str(inspect.signature(obj)) if callable(obj) else None
        except Exception:
            sig = None
        return self._ok(
            symbol_path=symbol_path,
            symbol_type=str(type(obj)),
            callable=callable(obj),
            is_class=inspect.isclass(obj),
            signature=sig,
            doc=(inspect.getdoc(obj) or "")[:2000],
        )