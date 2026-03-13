import os
import sys
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

import importlib


class Adapter:
    """
    MCP Import Mode Adapter for SymPy repository source integration.

    This adapter prioritizes importing implementation directly from repository source code.
    If imports fail, it automatically switches to fallback mode and returns actionable guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._last_error: Optional[str] = None
        self._initialize_modules()

    # ============================================================
    # Core helpers
    # ============================================================

    def _ok(self, data: Any = None, message: str = "ok", **extra: Any) -> Dict[str, Any]:
        res = {"status": "success", "mode": self.mode, "message": message, "data": data}
        if extra:
            res.update(extra)
        return res

    def _fail(self, message: str, guidance: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
        res = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            res["guidance"] = guidance
        if extra:
            res.update(extra)
        return res

    def _fallback(self, reason: str) -> None:
        self.mode = "fallback"
        self._last_error = reason

    def _safe_import(self, module_path: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        try:
            module = importlib.import_module(module_path)
            return True, module, None
        except Exception as exc:
            return False, None, f"{type(exc).__name__}: {exc}"

    def _initialize_modules(self) -> None:
        """
        Import key modules from repository source. Uses full paths inferred from analysis.
        """
        targets = {
            "sympy_root": "sympy",
            "interactive_session": "sympy.interactive.session",
            "solvers": "sympy.solvers.solvers",
            "solveset": "sympy.solvers.solveset",
            "integrals": "sympy.integrals.integrals",
            "printing_latex": "sympy.printing.latex",
            "printing_str": "sympy.printing.str",
            "parsing_sympy_parser": "sympy.parsing.sympy_parser",
            "matrices": "sympy.matrices",
            "core_symbol": "sympy.core.symbol",
            "core_sympify": "sympy.core.sympify",
        }

        failures = {}
        for key, mod_path in targets.items():
            ok, module, err = self._safe_import(mod_path)
            if ok and module is not None:
                self._modules[key] = module
            else:
                failures[mod_path] = err

        if failures:
            self._fallback("One or more imports failed.")
            self._modules["import_failures"] = failures

    # ============================================================
    # Status and diagnostics
    # ============================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import health and return diagnostics.

        Returns:
            Unified status dictionary containing current mode, loaded modules, and import failures.
        """
        failures = self._modules.get("import_failures", {})
        return self._ok(
            data={
                "loaded_modules": sorted([k for k in self._modules.keys() if k != "import_failures"]),
                "import_failures": failures,
                "last_error": self._last_error,
            },
            message="health check completed",
        )

    # ============================================================
    # Interactive session module methods
    # ============================================================

    def call_interactive_init_session(self, ipython: bool = False, pretty_print: bool = True) -> Dict[str, Any]:
        """
        Initialize a SymPy interactive session.

        Args:
            ipython: Whether to request IPython integration if available.
            pretty_print: Enable pretty printing output.

        Returns:
            Unified status dictionary with session initialization result.
        """
        if self.mode != "import":
            return self._fail(
                "Import mode is unavailable.",
                guidance="Verify source path and missing dependencies, then retry.",
            )
        try:
            mod = self._modules["interactive_session"]
            if not hasattr(mod, "init_session"):
                return self._fail(
                    "Function not found: sympy.interactive.session.init_session",
                    guidance="Check repository version compatibility.",
                )
            result = mod.init_session(ipython=ipython, pretty_print=pretty_print)
            return self._ok(data=result, message="interactive session initialized")
        except Exception as exc:
            return self._fail(
                f"Failed to initialize interactive session: {type(exc).__name__}: {exc}",
                guidance="Run in a standard terminal and ensure optional interactive dependencies are installed.",
            )

    # ============================================================
    # Core symbol / sympify methods
    # ============================================================

    def create_symbol(self, name: str, **assumptions: Any) -> Dict[str, Any]:
        """
        Create a symbolic variable using SymPy Symbol class.

        Args:
            name: Symbol name.
            assumptions: Optional SymPy assumptions (e.g., real=True, positive=True).

        Returns:
            Unified status dictionary with created Symbol instance.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            mod = self._modules["core_symbol"]
            Symbol = getattr(mod, "Symbol")
            obj = Symbol(name, **assumptions)
            return self._ok(data=obj, message="symbol created")
        except Exception as exc:
            return self._fail(
                f"Failed to create Symbol: {type(exc).__name__}: {exc}",
                guidance="Ensure symbol name is a valid string and assumptions are valid SymPy assumptions.",
            )

    def call_sympify(self, expression: Any, evaluate: bool = True) -> Dict[str, Any]:
        """
        Convert expression into a SymPy object using sympify.

        Args:
            expression: Input expression to convert.
            evaluate: Whether to evaluate during conversion.

        Returns:
            Unified status dictionary with SymPy expression.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            mod = self._modules["core_sympify"]
            sympify = getattr(mod, "sympify")
            obj = sympify(expression, evaluate=evaluate)
            return self._ok(data=obj, message="expression sympified")
        except Exception as exc:
            return self._fail(
                f"Failed to sympify expression: {type(exc).__name__}: {exc}",
                guidance="Provide a valid mathematical expression, number, or compatible object.",
            )

    # ============================================================
    # Parsing methods
    # ============================================================

    def call_parse_expr(self, expr: str, evaluate: bool = True) -> Dict[str, Any]:
        """
        Parse string expression into a SymPy expression.

        Args:
            expr: Expression string.
            evaluate: Whether parser should evaluate automatically.

        Returns:
            Unified status dictionary with parsed expression.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            mod = self._modules["parsing_sympy_parser"]
            parse_expr = getattr(mod, "parse_expr")
            out = parse_expr(expr, evaluate=evaluate)
            return self._ok(data=out, message="expression parsed")
        except Exception as exc:
            return self._fail(
                f"Failed to parse expression: {type(exc).__name__}: {exc}",
                guidance="Check expression syntax. Example: 'x**2 + 2*x + 1'.",
            )

    # ============================================================
    # Solver methods
    # ============================================================

    def call_solve(self, equation: Any, symbol: Any = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Solve algebraic equations using sympy.solvers.solvers.solve.

        Args:
            equation: Equation or expression.
            symbol: Optional target symbol(s).
            kwargs: Additional solve options.

        Returns:
            Unified status dictionary with solve result.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            solve = getattr(self._modules["solvers"], "solve")
            result = solve(equation, symbol, **kwargs) if symbol is not None else solve(equation, **kwargs)
            return self._ok(data=result, message="solve executed")
        except Exception as exc:
            return self._fail(
                f"Failed to solve equation: {type(exc).__name__}: {exc}",
                guidance="Provide a valid equation and symbol. Example: Eq(x**2-1, 0), x.",
            )

    def call_solveset(self, equation: Any, symbol: Any = None, domain: Any = None) -> Dict[str, Any]:
        """
        Solve equations as sets using sympy.solvers.solveset.solveset.

        Args:
            equation: Equation/expression.
            symbol: Symbol to solve for.
            domain: Optional domain set.

        Returns:
            Unified status dictionary with solveset result.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            solveset = getattr(self._modules["solveset"], "solveset")
            if symbol is None and domain is None:
                result = solveset(equation)
            elif domain is None:
                result = solveset(equation, symbol)
            else:
                result = solveset(equation, symbol, domain)
            return self._ok(data=result, message="solveset executed")
        except Exception as exc:
            return self._fail(
                f"Failed to run solveset: {type(exc).__name__}: {exc}",
                guidance="Provide a valid equation and symbol, and optional domain from sympy.sets.",
            )

    # ============================================================
    # Integration methods
    # ============================================================

    def call_integrate(self, expr: Any, *limits: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Integrate expression using sympy.integrals.integrals.integrate.

        Args:
            expr: Expression to integrate.
            limits: Integration limits/symbols.
            kwargs: Additional integration options.

        Returns:
            Unified status dictionary with integration result.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            integrate = getattr(self._modules["integrals"], "integrate")
            result = integrate(expr, *limits, **kwargs)
            return self._ok(data=result, message="integration executed")
        except Exception as exc:
            return self._fail(
                f"Failed to integrate expression: {type(exc).__name__}: {exc}",
                guidance="Provide a valid expression and limits, e.g. integrate(x**2, (x, 0, 1)).",
            )

    # ============================================================
    # Matrix/class instance methods
    # ============================================================

    def create_matrix(self, data: Any) -> Dict[str, Any]:
        """
        Create a SymPy Matrix instance from list-like input.

        Args:
            data: Nested list or matrix-compatible data.

        Returns:
            Unified status dictionary with Matrix instance.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            Matrix = getattr(self._modules["matrices"], "Matrix")
            m = Matrix(data)
            return self._ok(data=m, message="matrix created")
        except Exception as exc:
            return self._fail(
                f"Failed to create matrix: {type(exc).__name__}: {exc}",
                guidance="Provide rectangular list-like data, e.g. [[1,2],[3,4]].",
            )

    # ============================================================
    # Printing methods
    # ============================================================

    def call_latex(self, expr: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Convert expression to LaTeX using sympy.printing.latex.latex.

        Args:
            expr: SymPy expression.
            kwargs: Additional latex printer options.

        Returns:
            Unified status dictionary with LaTeX string.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            latex_fn = getattr(self._modules["printing_latex"], "latex")
            out = latex_fn(expr, **kwargs)
            return self._ok(data=out, message="latex generated")
        except Exception as exc:
            return self._fail(
                f"Failed to generate LaTeX: {type(exc).__name__}: {exc}",
                guidance="Pass a valid SymPy expression. You can convert inputs via call_sympify first.",
            )

    def call_sstr(self, expr: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Convert expression to SymPy string form using sympy.printing.str.sstr.

        Args:
            expr: SymPy expression.
            kwargs: Additional string printer options.

        Returns:
            Unified status dictionary with string output.
        """
        if self.mode != "import":
            return self._fail("Import mode is unavailable.", guidance="Fix imports and retry.")
        try:
            sstr_fn = getattr(self._modules["printing_str"], "sstr")
            out = sstr_fn(expr, **kwargs)
            return self._ok(data=out, message="string form generated")
        except Exception as exc:
            return self._fail(
                f"Failed to stringify expression: {type(exc).__name__}: {exc}",
                guidance="Pass a valid SymPy expression.",
            )