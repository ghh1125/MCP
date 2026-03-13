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
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the CVXPY repository.

    This adapter prefers direct module imports from the local `source` directory,
    and provides graceful fallbacks with actionable guidance when import/runtime
    issues occur.

    Mode:
        - import: Uses in-repo Python modules directly.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as e:
            self._import_errors[module_path] = str(e)
            return None

    def _initialize_modules(self) -> None:
        targets = [
            "cvxpy",
            "cvxpy.utilities.cvxpy_upgrade",
            "tools.release_notes",
        ]
        for t in targets:
            self._import_module(t)

    def _get_module(self, module_path: str) -> Any:
        if module_path in self._modules:
            return self._modules[module_path]
        module = self._import_module(module_path)
        if module is None:
            raise ImportError(
                f"Unable to import module '{module_path}'. "
                f"Ensure repository source exists under '{source_path}' and dependencies are installed."
            )
        return module

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter readiness and report import diagnostics.

        Returns:
            Dict[str, Any]: Unified status dictionary with imported modules and failures.
        """
        try:
            return self._ok(
                {
                    "source_path": source_path,
                    "loaded_modules": sorted(self._modules.keys()),
                    "import_errors": self._import_errors,
                },
                "Adapter initialized.",
            )
        except Exception as e:
            return self._fail(
                "Health check failed.",
                e,
                "Inspect source path and dependency installation.",
            )

    # -------------------------------------------------------------------------
    # Core CVXPY module access
    # -------------------------------------------------------------------------
    def get_cvxpy_module(self) -> Dict[str, Any]:
        """
        Get the imported top-level CVXPY module object.

        Returns:
            Dict[str, Any]: Contains module metadata on success.
        """
        try:
            mod = self._get_module("cvxpy")
            return self._ok(
                {
                    "module": "cvxpy",
                    "version": getattr(mod, "__version__", None),
                    "file": getattr(mod, "__file__", None),
                },
                "CVXPY module loaded.",
            )
        except Exception as e:
            return self._fail(
                "Failed to load CVXPY module.",
                e,
                "Confirm local source checkout is available and Python dependencies are installed.",
            )

    def create_expression_variable(
        self,
        shape: Optional[Any] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a cvxpy.Variable instance.

        Parameters:
            shape: Variable shape (int, tuple, or None for scalar).
            name: Optional variable name.
            **kwargs: Additional cvxpy.Variable keyword arguments.

        Returns:
            Dict[str, Any]: Includes created object reference on success.
        """
        try:
            cp = self._get_module("cvxpy")
            var = cp.Variable(shape=shape, name=name, **kwargs) if shape is not None else cp.Variable(name=name, **kwargs)
            return self._ok({"object": var, "repr": repr(var)}, "Variable created.")
        except Exception as e:
            return self._fail(
                "Failed to create cvxpy.Variable.",
                e,
                "Check provided shape/kwargs and ensure CVXPY is importable.",
            )

    def create_expression_parameter(
        self,
        shape: Optional[Any] = None,
        value: Optional[Any] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a cvxpy.Parameter instance.

        Parameters:
            shape: Parameter shape.
            value: Optional initial value.
            name: Optional parameter name.
            **kwargs: Additional cvxpy.Parameter keyword arguments.

        Returns:
            Dict[str, Any]: Includes created parameter reference on success.
        """
        try:
            cp = self._get_module("cvxpy")
            param = cp.Parameter(shape=shape, name=name, **kwargs) if shape is not None else cp.Parameter(name=name, **kwargs)
            if value is not None:
                param.value = value
            return self._ok({"object": param, "repr": repr(param)}, "Parameter created.")
        except Exception as e:
            return self._fail(
                "Failed to create cvxpy.Parameter.",
                e,
                "Verify shape/value compatibility and CVXPY installation.",
            )

    def create_problem(
        self,
        objective: Any,
        constraints: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a cvxpy.Problem instance.

        Parameters:
            objective: cvxpy objective object, e.g., cp.Minimize(expr).
            constraints: Optional list of cvxpy constraints.

        Returns:
            Dict[str, Any]: Includes problem reference on success.
        """
        try:
            cp = self._get_module("cvxpy")
            prob = cp.Problem(objective, constraints or [])
            return self._ok({"object": prob, "repr": repr(prob)}, "Problem created.")
        except Exception as e:
            return self._fail(
                "Failed to create cvxpy.Problem.",
                e,
                "Ensure objective/constraints are valid CVXPY expressions.",
            )

    def solve_problem(
        self,
        problem: Any,
        solver: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Solve a cvxpy.Problem.

        Parameters:
            problem: cvxpy.Problem instance.
            solver: Optional solver name.
            **kwargs: Additional solver options.

        Returns:
            Dict[str, Any]: Contains solve status and objective value when available.
        """
        try:
            if solver:
                value = problem.solve(solver=solver, **kwargs)
            else:
                value = problem.solve(**kwargs)
            return self._ok(
                {
                    "problem_status": getattr(problem, "status", None),
                    "objective_value": value,
                },
                "Problem solved.",
            )
        except Exception as e:
            return self._fail(
                "Failed to solve problem.",
                e,
                "Install/configure an appropriate solver (e.g., SCS, ECOS, OSQP, Clarabel) and verify problem DCP compliance.",
            )

    # -------------------------------------------------------------------------
    # Utility script modules identified by analysis
    # -------------------------------------------------------------------------
    def get_cvxpy_upgrade_module(self) -> Dict[str, Any]:
        """
        Load and expose `cvxpy.utilities.cvxpy_upgrade` module metadata.

        Returns:
            Dict[str, Any]: Module load status and file location.
        """
        try:
            mod = self._get_module("cvxpy.utilities.cvxpy_upgrade")
            return self._ok(
                {"module": "cvxpy.utilities.cvxpy_upgrade", "file": getattr(mod, "__file__", None)},
                "cvxpy_upgrade module loaded.",
            )
        except Exception as e:
            return self._fail(
                "Failed to load cvxpy_upgrade module.",
                e,
                "Ensure source tree contains cvxpy.utilities.cvxpy_upgrade.",
            )

    def call_cvxpy_upgrade(
        self,
        args: Optional[List[str]] = None,
        use_subprocess: bool = False,
    ) -> Dict[str, Any]:
        """
        Invoke CVXPY migration helper utility.

        Parameters:
            args: CLI-style argument list for the utility.
            use_subprocess: If True, run as subprocess module call for CLI parity.

        Returns:
            Dict[str, Any]: Execution result and output details.
        """
        args = args or []
        try:
            if use_subprocess:
                cmd = [sys.executable, "-m", "cvxpy.utilities.cvxpy_upgrade"] + args
                completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
                status = "success" if completed.returncode == 0 else "error"
                return {
                    "status": status,
                    "mode": self.mode,
                    "message": "cvxpy_upgrade executed via subprocess.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }

            mod = self._get_module("cvxpy.utilities.cvxpy_upgrade")
            main_fn = getattr(mod, "main", None)
            if callable(main_fn):
                result = main_fn(args)
                return self._ok({"result": result}, "cvxpy_upgrade main executed.")
            return self._fail(
                "cvxpy_upgrade does not expose a callable main(args).",
                guidance="Use subprocess mode or inspect module API.",
            )
        except Exception as e:
            return self._fail(
                "Failed to execute cvxpy_upgrade.",
                e,
                "Try use_subprocess=True and validate provided arguments.",
            )

    def get_release_notes_module(self) -> Dict[str, Any]:
        """
        Load and expose `tools.release_notes` module metadata.

        Returns:
            Dict[str, Any]: Module load status and file location.
        """
        try:
            mod = self._get_module("tools.release_notes")
            return self._ok(
                {"module": "tools.release_notes", "file": getattr(mod, "__file__", None)},
                "release_notes module loaded.",
            )
        except Exception as e:
            return self._fail(
                "Failed to load release_notes module.",
                e,
                "Ensure source tree contains tools/release_notes.py.",
            )

    def call_release_notes(
        self,
        args: Optional[List[str]] = None,
        use_subprocess: bool = True,
    ) -> Dict[str, Any]:
        """
        Invoke release notes generation utility.

        Parameters:
            args: CLI-style argument list.
            use_subprocess: Preferred mode for script-like utilities.

        Returns:
            Dict[str, Any]: Execution output and exit diagnostics.
        """
        args = args or []
        try:
            if use_subprocess:
                cmd = [sys.executable, "-m", "tools.release_notes"] + args
                completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
                status = "success" if completed.returncode == 0 else "error"
                return {
                    "status": status,
                    "mode": self.mode,
                    "message": "release_notes executed via subprocess.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }

            mod = self._get_module("tools.release_notes")
            main_fn = getattr(mod, "main", None)
            if callable(main_fn):
                result = main_fn(args)
                return self._ok({"result": result}, "release_notes main executed.")
            return self._fail(
                "release_notes does not expose a callable main(args).",
                guidance="Use subprocess mode for script execution.",
            )
        except Exception as e:
            return self._fail(
                "Failed to execute release_notes utility.",
                e,
                "Use subprocess mode and verify repository tooling dependencies.",
            )