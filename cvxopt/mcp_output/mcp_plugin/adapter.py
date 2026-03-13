import os
import sys
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for CVXOPT repository integration.

    This adapter is designed to:
    1) Load CVXOPT modules from the local repository source tree.
    2) Expose stable wrapper methods for identified functions/modules.
    3) Return unified dictionary responses with status metadata.
    4) Gracefully degrade to fallback mode if imports fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state and attempt import-based module loading.

        Attributes:
            mode (str): Adapter running mode ("import" or "fallback").
            imports_ok (bool): Whether core module imports succeeded.
            capabilities (dict): Available features detected at runtime.
            modules (dict): Loaded module references.
        """
        self.mode = "import"
        self.imports_ok = False
        self.modules: Dict[str, Any] = {}
        self.capabilities: Dict[str, Any] = {
            "normal": False,
            "uniform": False,
            "setseed": False,
            "modeling_max": False,
            "modeling_min": False,
            "solvers": False,
            "backends": {
                "glpk": False,
                "mosek": False,
                "dsdp": False,
                "gsl": False,
            },
        }

        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "ok") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, hint: Optional[str] = None, exception: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if hint:
            payload["hint"] = hint
        if exception is not None:
            payload["error_type"] = type(exception).__name__
            payload["error"] = str(exception)
        return payload

    def _load_modules(self) -> None:
        """
        Load CVXOPT repository modules using full package paths from analysis.

        Uses:
            - src.python.__init__ for normal/uniform/setseed
            - src.python.modeling for max/min
            - src.python.solvers for LP/QP/SOCP/SDP/CONELP/CONEQP/GP wrappers
            - optional modules for backend capability checks
        """
        try:
            import src.python.__init__ as cvxopt_init
            import src.python.modeling as cvxopt_modeling
            import src.python.solvers as cvxopt_solvers

            self.modules["cvxopt_init"] = cvxopt_init
            self.modules["cvxopt_modeling"] = cvxopt_modeling
            self.modules["cvxopt_solvers"] = cvxopt_solvers

            self.capabilities["normal"] = hasattr(cvxopt_init, "normal")
            self.capabilities["uniform"] = hasattr(cvxopt_init, "uniform")
            self.capabilities["setseed"] = hasattr(cvxopt_init, "setseed")
            self.capabilities["modeling_max"] = hasattr(cvxopt_modeling, "max")
            self.capabilities["modeling_min"] = hasattr(cvxopt_modeling, "min")
            self.capabilities["solvers"] = True

            # Optional backend detection
            try:
                import src.python.msk  # noqa: F401
                self.capabilities["backends"]["mosek"] = True
            except Exception:
                self.capabilities["backends"]["mosek"] = False

            try:
                import importlib
                glpk_mod = importlib.import_module("cvxopt.glpk")
                self.capabilities["backends"]["glpk"] = glpk_mod is not None
            except Exception:
                self.capabilities["backends"]["glpk"] = False

            self.imports_ok = True
            self.mode = "import"

        except Exception:
            self.imports_ok = False
            self.mode = "fallback"

    # -------------------------------------------------------------------------
    # Health and capabilities
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import/capability diagnostics.
        """
        if self.imports_ok:
            return self._ok(
                {
                    "imports_ok": True,
                    "capabilities": self.capabilities,
                    "source_path": source_path,
                },
                message="Adapter is ready in import mode.",
            )
        return self._err(
            "Import mode unavailable.",
            hint=(
                "Build CVXOPT native extensions in this repository context. "
                "If build is not possible, run in blackbox/container fallback mode."
            ),
        )

    # -------------------------------------------------------------------------
    # Identified functions from src.python.__init__
    # -------------------------------------------------------------------------
    def call_normal(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call src.python.__init__.normal(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to CVXOPT normal().
            **kwargs: Keyword arguments forwarded to CVXOPT normal().

        Returns:
            dict: Unified response with status and function result.
        """
        if not self.imports_ok:
            return self._err(
                "normal is unavailable in fallback mode.",
                hint="Ensure CVXOPT modules import successfully before calling random helpers.",
            )
        try:
            fn = self.modules["cvxopt_init"].normal
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="normal executed.")
        except Exception as e:
            return self._err(
                "Failed to execute normal.",
                hint="Verify argument types/shapes expected by CVXOPT normal().",
                exception=e,
            )

    def call_uniform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call src.python.__init__.uniform(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to CVXOPT uniform().
            **kwargs: Keyword arguments forwarded to CVXOPT uniform().

        Returns:
            dict: Unified response with status and function result.
        """
        if not self.imports_ok:
            return self._err(
                "uniform is unavailable in fallback mode.",
                hint="Ensure CVXOPT modules import successfully before calling random helpers.",
            )
        try:
            fn = self.modules["cvxopt_init"].uniform
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="uniform executed.")
        except Exception as e:
            return self._err(
                "Failed to execute uniform.",
                hint="Verify argument types/shapes expected by CVXOPT uniform().",
                exception=e,
            )

    def call_setseed(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call src.python.__init__.setseed(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to CVXOPT setseed().
            **kwargs: Keyword arguments forwarded to CVXOPT setseed().

        Returns:
            dict: Unified response with status and function result.
        """
        if not self.imports_ok:
            return self._err(
                "setseed is unavailable in fallback mode.",
                hint="Ensure CVXOPT modules import successfully before setting RNG seed.",
            )
        try:
            fn = self.modules["cvxopt_init"].setseed
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="setseed executed.")
        except Exception as e:
            return self._err(
                "Failed to execute setseed.",
                hint="Pass a valid integer seed supported by CVXOPT.",
                exception=e,
            )

    # -------------------------------------------------------------------------
    # Identified functions from src.python.modeling
    # -------------------------------------------------------------------------
    def call_modeling_max(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call src.python.modeling.max(*args, **kwargs).

        Parameters:
            *args: Modeling objects or numeric values accepted by CVXOPT DSL.
            **kwargs: Extra keyword parameters for modeling.max.

        Returns:
            dict: Unified response with status and function result.
        """
        if not self.imports_ok:
            return self._err(
                "modeling.max is unavailable in fallback mode.",
                hint="Enable import mode with built CVXOPT modules to use symbolic modeling.",
            )
        try:
            fn = self.modules["cvxopt_modeling"].max
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="modeling.max executed.")
        except Exception as e:
            return self._err(
                "Failed to execute modeling.max.",
                hint="Check that arguments are valid CVXOPT modeling expressions.",
                exception=e,
            )

    def call_modeling_min(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call src.python.modeling.min(*args, **kwargs).

        Parameters:
            *args: Modeling objects or numeric values accepted by CVXOPT DSL.
            **kwargs: Extra keyword parameters for modeling.min.

        Returns:
            dict: Unified response with status and function result.
        """
        if not self.imports_ok:
            return self._err(
                "modeling.min is unavailable in fallback mode.",
                hint="Enable import mode with built CVXOPT modules to use symbolic modeling.",
            )
        try:
            fn = self.modules["cvxopt_modeling"].min
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message="modeling.min executed.")
        except Exception as e:
            return self._err(
                "Failed to execute modeling.min.",
                hint="Check that arguments are valid CVXOPT modeling expressions.",
                exception=e,
            )

    # -------------------------------------------------------------------------
    # Solver wrappers (import strategy recommendation)
    # -------------------------------------------------------------------------
    def call_solver(self, solver_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic solver dispatcher for CVXOPT solvers module.

        Supported solver names include:
            lp, qp, socp, sdp, conelp, coneqp, gp

        Parameters:
            solver_name (str): Solver function name in src.python.solvers.
            *args: Positional arguments for the selected solver.
            **kwargs: Keyword arguments for the selected solver.

        Returns:
            dict: Unified response containing raw solver output when successful.
        """
        if not self.imports_ok:
            return self._err(
                "Solver calls are unavailable in fallback mode.",
                hint="Use a prebuilt container/blackbox executor for lp/qp as a fallback path.",
            )
        try:
            mod = self.modules["cvxopt_solvers"]
            if not hasattr(mod, solver_name):
                return self._err(
                    f"Unknown solver '{solver_name}'.",
                    hint="Use one of: lp, qp, socp, sdp, conelp, coneqp, gp.",
                )
            solver_fn = getattr(mod, solver_name)
            result = solver_fn(*args, **kwargs)
            return self._ok({"result": result, "solver": solver_name}, message=f"{solver_name} executed.")
        except Exception as e:
            return self._err(
                f"Failed to execute solver '{solver_name}'.",
                hint="Validate matrix dimensions/types and cone definitions.",
                exception=e,
            )

    # -------------------------------------------------------------------------
    # Fallback helper
    # -------------------------------------------------------------------------
    def fallback_plan(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when import mode cannot run.

        Returns:
            dict: Steps for blackbox/container fallback operation.
        """
        return self._ok(
            {
                "recommended_mode": "blackbox",
                "steps": [
                    "Build or use a prebuilt environment with CVXOPT native extensions.",
                    "Expose a minimal JSON API for lp/qp first for reliability.",
                    "Map JSON arrays to CVXOPT matrix/spmatrix in executor layer.",
                    "Return normalized output fields: status, objective, x, y, z, iterations.",
                ],
            },
            message="Fallback guidance generated.",
        )

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    def last_trace(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for debugging context.
        """
        return self._ok({"traceback": traceback.format_exc()}, message="Traceback snapshot generated.")