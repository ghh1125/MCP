import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the Pyomo repository.

    This adapter prioritizes direct Python imports from the local repository source
    and provides a graceful CLI fallback when import-based execution is unavailable.
    All public methods return a unified dictionary format with a mandatory `status` field.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        targets = {
            "pyomo.environ": "Core modeling API",
            "pyomo.scripting.pyomo_main": "Primary CLI entry module",
            "pyomo.opt": "Solver factory and optimization interfaces",
            "pyomo.dataportal.DataPortal": "DataPortal support",
            "pyomo.core": "Core components package",
        }
        for module_name in targets:
            try:
                self._modules[module_name] = importlib.import_module(module_name)
            except Exception as exc:
                self._import_errors[module_name] = f"{type(exc).__name__}: {exc}"

    # -------------------------------------------------------------------------
    # Internal Utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: str = "", details: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _module_available(self, module_name: str) -> bool:
        return module_name in self._modules

    # -------------------------------------------------------------------------
    # Health / Diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import availability.

        Returns:
            dict: Unified status payload containing loaded modules and import errors.
        """
        try:
            return self._ok(
                {
                    "loaded_modules": sorted(self._modules.keys()),
                    "import_errors": self._import_errors,
                    "import_ready": self._module_available("pyomo.environ"),
                    "cli_ready": self._module_available("pyomo.scripting.pyomo_main"),
                }
            )
        except Exception:
            return self._err(
                "Health check failed.",
                guidance="Inspect adapter environment and Python path configuration.",
                details=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Core Import-Mode Methods
    # -------------------------------------------------------------------------
    def create_concrete_model(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Pyomo ConcreteModel instance via import mode.

        Parameters:
            name (str, optional): Optional model name.

        Returns:
            dict: status, model, and metadata.
        """
        if not self._module_available("pyomo.environ"):
            return self._err(
                "Import mode is unavailable for pyomo.environ.",
                guidance="Ensure repository source is present under the configured source path, or use CLI fallback methods.",
                details=self._import_errors.get("pyomo.environ"),
            )
        try:
            pyo = self._modules["pyomo.environ"]
            model = pyo.ConcreteModel(name=name) if name else pyo.ConcreteModel()
            return self._ok({"model": model, "model_type": "ConcreteModel"})
        except Exception:
            return self._err(
                "Failed to create ConcreteModel.",
                guidance="Verify Pyomo core imports and environment consistency.",
                details=traceback.format_exc(),
            )

    def create_abstract_model(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Pyomo AbstractModel instance.

        Parameters:
            name (str, optional): Optional model name.

        Returns:
            dict: status, model, and metadata.
        """
        if not self._module_available("pyomo.environ"):
            return self._err(
                "Import mode is unavailable for pyomo.environ.",
                guidance="Check source path insertion and local module integrity.",
                details=self._import_errors.get("pyomo.environ"),
            )
        try:
            pyo = self._modules["pyomo.environ"]
            model = pyo.AbstractModel(name=name) if name else pyo.AbstractModel()
            return self._ok({"model": model, "model_type": "AbstractModel"})
        except Exception:
            return self._err(
                "Failed to create AbstractModel.",
                guidance="Confirm Pyomo base modules are importable.",
                details=traceback.format_exc(),
            )

    def create_solver(self, solver_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a solver instance using Pyomo SolverFactory.

        Parameters:
            solver_name (str): Solver identifier (e.g., 'glpk', 'cbc', 'gurobi').
            **kwargs: Additional SolverFactory keyword arguments.

        Returns:
            dict: status and solver object.
        """
        if not self._module_available("pyomo.environ"):
            return self._err(
                "SolverFactory is unavailable because pyomo.environ failed to import.",
                guidance="Resolve import errors or use CLI execution as fallback.",
                details=self._import_errors.get("pyomo.environ"),
            )
        try:
            pyo = self._modules["pyomo.environ"]
            solver = pyo.SolverFactory(solver_name, **kwargs)
            if solver is None:
                return self._err(
                    f"SolverFactory returned None for solver '{solver_name}'.",
                    guidance="Check solver name spelling and plugin availability in the local environment.",
                )
            return self._ok({"solver": solver, "solver_name": solver_name})
        except Exception:
            return self._err(
                f"Failed to create solver '{solver_name}'.",
                guidance="Ensure solver dependencies are installed and visible to this interpreter.",
                details=traceback.format_exc(),
            )

    def solve_model(
        self,
        model: Any,
        solver_name: str = "glpk",
        solver_options: Optional[Dict[str, Any]] = None,
        tee: bool = False,
    ) -> Dict[str, Any]:
        """
        Solve a Pyomo model in import mode.

        Parameters:
            model (Any): A Pyomo model instance.
            solver_name (str): Solver id for SolverFactory.
            solver_options (dict, optional): Options passed to solver.options.
            tee (bool): Stream solver output if supported.

        Returns:
            dict: status, solver results, and termination details when available.
        """
        try:
            solver_resp = self.create_solver(solver_name)
            if solver_resp["status"] != "success":
                return solver_resp
            solver = solver_resp["solver"]

            if solver_options:
                for k, v in solver_options.items():
                    solver.options[k] = v

            results = solver.solve(model, tee=tee)
            termination = None
            solver_status = None
            try:
                solver_status = str(results.solver.status)
                termination = str(results.solver.termination_condition)
            except Exception:
                pass

            return self._ok(
                {
                    "results": results,
                    "solver_status": solver_status,
                    "termination_condition": termination,
                }
            )
        except Exception:
            return self._err(
                "Model solve failed.",
                guidance="Validate model formulation and solver availability. Use health_check() for diagnostics.",
                details=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # CLI Fallback Methods
    # -------------------------------------------------------------------------
    def run_pyomo_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the Pyomo CLI entry point through pyomo.scripting.pyomo_main.

        Parameters:
            argv (list[str], optional): Argument list excluding executable name.

        Returns:
            dict: status and return code.
        """
        if not self._module_available("pyomo.scripting.pyomo_main"):
            return self._err(
                "CLI fallback module pyomo.scripting.pyomo_main is unavailable.",
                guidance="Ensure local source includes pyomo.scripting.pyomo_main and that source path is correct.",
                details=self._import_errors.get("pyomo.scripting.pyomo_main"),
            )
        try:
            mod = self._modules["pyomo.scripting.pyomo_main"]
            args = argv or []
            if hasattr(mod, "main"):
                rc = mod.main(args=args)
                return self._ok({"return_code": rc, "argv": args})
            return self._err(
                "CLI module loaded but no callable 'main' was found.",
                guidance="Check compatibility with the current Pyomo version layout.",
            )
        except Exception:
            return self._err(
                "Failed to execute Pyomo CLI fallback.",
                guidance="Verify CLI arguments and module compatibility.",
                details=traceback.format_exc(),
            )