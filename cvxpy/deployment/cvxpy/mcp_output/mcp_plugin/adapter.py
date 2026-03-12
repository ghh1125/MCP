import os
import sys
import traceback
import importlib
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the cvxpy repository.

    Design goals:
    - Prefer direct module imports from the local `source` checkout.
    - Provide consistent return schema for all methods.
    - Expose repository-identified entry points and practical wrappers.
    - Gracefully degrade to fallback behavior if import is unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = {"status": status, "message": message}
        if data is not None:
            out["data"] = data
        if error is not None:
            out["error"] = error
        if guidance is not None:
            out["guidance"] = guidance
        return out

    def _safe_import(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as exc:
            self._import_errors[module_path] = f"{type(exc).__name__}: {exc}"

    def _initialize_modules(self) -> None:
        target_modules = [
            "cvxpy",
            "cvxpy.utilities.cvxpy_upgrade",
            "tools.release_notes",
        ]
        for module in target_modules:
            self._safe_import(module)

    def _is_import_ready(self, module_path: str) -> bool:
        return module_path in self._modules

    def _fallback(self, feature: str, details: Optional[str] = None) -> Dict[str, Any]:
        return self._result(
            status="error",
            message=f"Import-mode feature unavailable: {feature}.",
            error=details or self._import_errors.get(feature, "Module is not loaded."),
            guidance=(
                "Ensure repository source exists under the configured `source` path and "
                "dependencies are installed (required: numpy, scipy; optional solvers as needed)."
            ),
        )

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter readiness and summarize import status.

        Returns:
            Dict with status, loaded modules, and import errors.
        """
        ready = self._is_import_ready("cvxpy")
        return self._result(
            status="ok" if ready else "error",
            message="Adapter health check completed.",
            data={
                "mode": self.mode,
                "import_ready": ready,
                "loaded_modules": list(self._modules.keys()),
                "import_errors": self._import_errors,
            },
            guidance=None if ready else "Install required dependencies and verify source path wiring.",
        )

    # -------------------------------------------------------------------------
    # Module instance methods (identified classes/modules entry wrappers)
    # -------------------------------------------------------------------------
    def instance_cvxpy(self) -> Dict[str, Any]:
        """
        Return the imported `cvxpy` module instance.

        This is a module-level instance wrapper for downstream tooling that expects
        explicit instance construction methods.

        Returns:
            Unified result dict with module metadata.
        """
        module_path = "cvxpy"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)
        mod = self._modules[module_path]
        return self._result(
            status="ok",
            message="cvxpy module instance ready.",
            data={
                "module": module_path,
                "version": getattr(mod, "__version__", None),
                "file": getattr(mod, "__file__", None),
            },
        )

    def instance_cvxpy_upgrade_module(self) -> Dict[str, Any]:
        """
        Return the imported `cvxpy.utilities.cvxpy_upgrade` module instance.

        Returns:
            Unified result dict with module metadata.
        """
        module_path = "cvxpy.utilities.cvxpy_upgrade"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)
        mod = self._modules[module_path]
        return self._result(
            status="ok",
            message="cvxpy_upgrade module instance ready.",
            data={"module": module_path, "file": getattr(mod, "__file__", None)},
        )

    def instance_release_notes_module(self) -> Dict[str, Any]:
        """
        Return the imported `tools.release_notes` module instance.

        Returns:
            Unified result dict with module metadata.
        """
        module_path = "tools.release_notes"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)
        mod = self._modules[module_path]
        return self._result(
            status="ok",
            message="release_notes module instance ready.",
            data={"module": module_path, "file": getattr(mod, "__file__", None)},
        )

    # -------------------------------------------------------------------------
    # Identified CLI/function call methods
    # -------------------------------------------------------------------------
    def call_cvxpy_upgrade_cli(self, args: Optional[List[str]] = None, timeout: int = 120) -> Dict[str, Any]:
        """
        Execute the cvxpy upgrade helper via module invocation.

        Parameters:
            args: Optional command-line arguments passed to the module.
            timeout: Process timeout in seconds.

        Returns:
            Unified result dict with stdout/stderr and returncode.
        """
        cmd = [sys.executable, "-m", "cvxpy.utilities.cvxpy_upgrade"] + (args or [])
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=source_path,
            )
            status = "ok" if proc.returncode == 0 else "error"
            return self._result(
                status=status,
                message="Executed cvxpy upgrade module.",
                data={
                    "command": cmd,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
                guidance=None if proc.returncode == 0 else "Review stderr and adjust arguments or source compatibility.",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to execute cvxpy upgrade module.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Verify Python executable, module availability, and permissions.",
            )

    def call_release_notes_script(self, args: Optional[List[str]] = None, timeout: int = 120) -> Dict[str, Any]:
        """
        Execute the repository maintenance script `tools/release_notes.py`.

        Parameters:
            args: Optional CLI args passed to the script.
            timeout: Process timeout in seconds.

        Returns:
            Unified result dict with stdout/stderr and returncode.
        """
        script_path = os.path.join(source_path, "tools", "release_notes.py")
        cmd = [sys.executable, script_path] + (args or [])
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=source_path,
            )
            status = "ok" if proc.returncode == 0 else "error"
            return self._result(
                status=status,
                message="Executed release_notes script.",
                data={
                    "command": cmd,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
                guidance=None if proc.returncode == 0 else "Inspect script arguments and repository state.",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to execute release_notes script.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check script path under source/tools and Python runtime permissions.",
            )

    # -------------------------------------------------------------------------
    # Practical cvxpy import-mode feature wrappers
    # -------------------------------------------------------------------------
    def call_get_cvxpy_version(self) -> Dict[str, Any]:
        """
        Return CVXPY version and path from imported module.

        Returns:
            Unified result dict with version metadata.
        """
        module_path = "cvxpy"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)
        mod = self._modules[module_path]
        return self._result(
            status="ok",
            message="Retrieved cvxpy version.",
            data={
                "version": getattr(mod, "__version__", None),
                "module_file": getattr(mod, "__file__", None),
            },
        )

    def call_solve_problem(
        self,
        objective: str = "minimize",
        c: Optional[List[float]] = None,
        A: Optional[List[List[float]]] = None,
        b: Optional[List[float]] = None,
        solver: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Solve a simple linear optimization model using cvxpy.

        Model:
            minimize or maximize c^T x
            subject to A x <= b

        Parameters:
            objective: "minimize" or "maximize".
            c: Objective vector.
            A: Constraint matrix.
            b: Constraint RHS.
            solver: Optional solver name string recognized by cvxpy.

        Returns:
            Unified result dict containing solution details.
        """
        module_path = "cvxpy"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)

        try:
            cp = self._modules[module_path]
            c = c or [1.0, 1.0]
            A = A or [[1.0, 2.0], [3.0, 1.0]]
            b = b or [4.0, 6.0]

            x = cp.Variable(len(c))
            expr = sum(c[i] * x[i] for i in range(len(c)))
            obj = cp.Minimize(expr) if objective.lower() == "minimize" else cp.Maximize(expr)
            constraints = []
            for row, rhs in zip(A, b):
                constraints.append(sum(row[i] * x[i] for i in range(len(c))) <= rhs)

            problem = cp.Problem(obj, constraints)
            solve_kwargs = {}
            if solver:
                solve_kwargs["solver"] = solver
            value = problem.solve(**solve_kwargs)

            return self._result(
                status="ok",
                message="Problem solved.",
                data={
                    "objective": objective.lower(),
                    "optimal_value": value,
                    "status_text": problem.status,
                    "x_value": x.value.tolist() if x.value is not None else None,
                    "solver": solver,
                },
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to solve optimization problem.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Check dimensions of c, A, b and ensure an appropriate solver is installed.",
            )

    def call_list_available_solvers(self) -> Dict[str, Any]:
        """
        List currently available solvers reported by cvxpy.

        Returns:
            Unified result dict with solver names.
        """
        module_path = "cvxpy"
        if not self._is_import_ready(module_path):
            return self._fallback(module_path)
        try:
            cp = self._modules[module_path]
            solvers = cp.installed_solvers()
            return self._result(
                status="ok",
                message="Retrieved installed solvers.",
                data={"installed_solvers": solvers},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to list installed solvers.",
                error=f"{type(exc).__name__}: {exc}",
                guidance="Ensure optional solver backends are properly installed in the runtime environment.",
            )

    def call_import_status(self) -> Dict[str, Any]:
        """
        Return detailed import status for all tracked modules.

        Returns:
            Unified result dict with module-by-module state.
        """
        data = {
            "loaded": {k: True for k in self._modules.keys()},
            "failed": self._import_errors,
            "mode": self.mode,
            "source_path": source_path,
        }
        return self._result(status="ok", message="Import status collected.", data=data)

    # -------------------------------------------------------------------------
    # Generic dispatcher
    # -------------------------------------------------------------------------
    def call(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic operation dispatcher.

        Parameters:
            operation: Name of adapter method to invoke.
            kwargs: Method keyword arguments.

        Returns:
            Unified result dict.
        """
        try:
            fn = getattr(self, operation, None)
            if fn is None or not callable(fn):
                return self._result(
                    status="error",
                    message=f"Unknown operation: {operation}",
                    guidance="Use a valid adapter method name such as health_check, call_solve_problem, or call_import_status.",
                )
            return fn(**kwargs)
        except Exception as exc:
            return self._result(
                status="error",
                message="Unhandled adapter execution error.",
                error=f"{type(exc).__name__}: {exc}",
                data={"traceback": traceback.format_exc()},
                guidance="Inspect traceback and validate operation arguments.",
            )