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
    MCP Import-Mode adapter for the CVXOPT repository.

    This adapter prioritizes direct module imports from the repository source tree.
    If import fails (e.g., compiled extensions are unavailable), it falls back to
    a graceful blackbox mode with actionable guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode}
        if data:
            result.update(data)
        return result

    def _err(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "error": message}
        if guidance:
            result["guidance"] = guidance
        return result

    def _load_modules(self) -> None:
        try:
            import python as cvxopt_package
            import python.solvers as solvers
            import python.modeling as modeling
            import python.coneprog as coneprog
            import python.cvxprog as cvxprog
            import python.misc as misc
            import python.msk as msk
            import python.printing as printing
            import python.info as info

            self._modules = {
                "cvxopt_package": cvxopt_package,
                "solvers": solvers,
                "modeling": modeling,
                "coneprog": coneprog,
                "cvxprog": cvxprog,
                "misc": misc,
                "msk": msk,
                "printing": printing,
                "info": info,
            }
            self.mode = "import"
        except Exception as exc:
            self.mode = "blackbox"
            self._import_error = str(exc)

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter health and import status.

        Returns:
            dict: Unified status payload containing mode and module availability.
        """
        if self.mode == "import":
            return self._ok(
                {
                    "message": "CVXOPT modules loaded successfully from source.",
                    "modules": sorted(self._modules.keys()),
                }
            )
        return self._err(
            "Import mode is unavailable due to module import failure.",
            guidance=(
                "Ensure CVXOPT compiled extensions are built and runtime dependencies "
                "(NumPy, BLAS/LAPACK, optional GLPK/DSDP/GSL/MOSEK) are available. "
                f"Original import error: {self._import_error}"
            ),
        )

    # -------------------------------------------------------------------------
    # Package-level constructors / utilities
    # -------------------------------------------------------------------------
    def create_matrix(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create a dense matrix using python.matrix."""
        if self.mode != "import":
            return self._err("matrix creation is not available in fallback mode.")
        try:
            matrix_ctor = getattr(self._modules["cvxopt_package"], "matrix")
            return self._ok({"result": matrix_ctor(*args, **kwargs)})
        except Exception as exc:
            return self._err("Failed to create matrix.", guidance=str(exc))

    def create_spmatrix(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Create a sparse matrix using python.spmatrix."""
        if self.mode != "import":
            return self._err("spmatrix creation is not available in fallback mode.")
        try:
            spmatrix_ctor = getattr(self._modules["cvxopt_package"], "spmatrix")
            return self._ok({"result": spmatrix_ctor(*args, **kwargs)})
        except Exception as exc:
            return self._err("Failed to create sparse matrix.", guidance=str(exc))

    # -------------------------------------------------------------------------
    # Solvers module wrappers
    # -------------------------------------------------------------------------
    def call_lp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call linear programming solver: python.solvers.lp."""
        return self._call_solver_func("lp", *args, **kwargs)

    def call_qp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call quadratic programming solver: python.solvers.qp."""
        return self._call_solver_func("qp", *args, **kwargs)

    def call_socp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call second-order cone programming solver: python.solvers.socp."""
        return self._call_solver_func("socp", *args, **kwargs)

    def call_sdp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call semidefinite programming solver: python.solvers.sdp."""
        return self._call_solver_func("sdp", *args, **kwargs)

    def call_conelp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call cone LP solver: python.solvers.conelp."""
        return self._call_solver_func("conelp", *args, **kwargs)

    def call_coneqp(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call cone QP solver: python.solvers.coneqp."""
        return self._call_solver_func("coneqp", *args, **kwargs)

    def _call_solver_func(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err(
                f"Solver function '{name}' is not available in fallback mode.",
                guidance="Build CVXOPT extension modules and verify numerical backends.",
            )
        try:
            fn = getattr(self._modules["solvers"], name)
            return self._ok({"result": fn(*args, **kwargs)})
        except AttributeError:
            return self._err(
                f"Solver function '{name}' not found.",
                guidance="Check CVXOPT version and available solver interfaces.",
            )
        except Exception as exc:
            return self._err(f"Solver '{name}' execution failed.", guidance=str(exc))

    # -------------------------------------------------------------------------
    # Modeling module wrappers
    # -------------------------------------------------------------------------
    def modeling_variable(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate modeling.variable."""
        return self._instantiate_modeling("variable", *args, **kwargs)

    def modeling_op(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate modeling.op."""
        return self._instantiate_modeling("op", *args, **kwargs)

    def modeling_max(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call modeling.max."""
        return self._call_modeling_func("max", *args, **kwargs)

    def modeling_min(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call modeling.min."""
        return self._call_modeling_func("min", *args, **kwargs)

    def modeling_sum(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call modeling.sum."""
        return self._call_modeling_func("sum", *args, **kwargs)

    def modeling_dot(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call modeling.dot."""
        return self._call_modeling_func("dot", *args, **kwargs)

    def _instantiate_modeling(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err(f"Modeling class '{name}' is not available in fallback mode.")
        try:
            cls = getattr(self._modules["modeling"], name)
            return self._ok({"result": cls(*args, **kwargs)})
        except AttributeError:
            return self._err(f"Modeling class '{name}' not found.")
        except Exception as exc:
            return self._err(f"Failed to instantiate modeling class '{name}'.", guidance=str(exc))

    def _call_modeling_func(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.mode != "import":
            return self._err(f"Modeling function '{name}' is not available in fallback mode.")
        try:
            fn = getattr(self._modules["modeling"], name)
            return self._ok({"result": fn(*args, **kwargs)})
        except AttributeError:
            return self._err(f"Modeling function '{name}' not found.")
        except Exception as exc:
            return self._err(f"Modeling function '{name}' failed.", guidance=str(exc))

    # -------------------------------------------------------------------------
    # Generic module execution for full feature access
    # -------------------------------------------------------------------------
    def call_module_attr(self, module: str, attr: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dispatcher to call any attribute from loaded modules.

        Args:
            module: One of loaded module keys (e.g., 'solvers', 'modeling', 'coneprog').
            attr: Function or callable attribute name to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status payload with execution result or error details.
        """
        if self.mode != "import":
            return self._err(
                "Generic module dispatch is not available in fallback mode.",
                guidance="Resolve import issues and rebuild CVXOPT from source.",
            )
        if module not in self._modules:
            return self._err(
                f"Unknown module '{module}'.",
                guidance=f"Available modules: {sorted(self._modules.keys())}",
            )
        try:
            target = getattr(self._modules[module], attr)
            if callable(target):
                return self._ok({"result": target(*args, **kwargs)})
            return self._ok({"result": target})
        except AttributeError:
            return self._err(
                f"Attribute '{attr}' not found in module '{module}'.",
                guidance="Inspect module members and verify API availability.",
            )
        except Exception as exc:
            return self._err(
                f"Execution failed for '{module}.{attr}'.",
                guidance=str(exc),
            )