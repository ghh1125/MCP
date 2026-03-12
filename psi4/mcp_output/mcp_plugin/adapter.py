import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for the Psi4 repository.

    This adapter prioritizes importing and invoking project-local modules from the repository source tree.
    It provides:
    - Unified status-return dictionaries
    - Graceful fallback guidance when import/runtime fails
    - Clear module grouping and method boundaries
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data is not None:
            payload["data"] = data
        return payload

    def _err(self, message: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _initialize_modules(self) -> None:
        targets = {
            "psi4.run_psi4": "psi4 runtime entry module",
            "conda.psi4_path_advisor": "path advisor utility module",
        }

        # psi4.run_psi4
        try:
            import psi4.run_psi4 as run_psi4  # full package path
            self._modules["psi4.run_psi4"] = run_psi4
        except Exception as exc:
            self._import_errors["psi4.run_psi4"] = str(exc)

        # conda/psi4-path-advisor.py uses a hyphen and cannot be imported directly as module name.
        # Attempt robust loading via importlib from explicit file path.
        try:
            import importlib.util

            advisor_file = os.path.join(source_path, "conda", "psi4-path-advisor.py")
            if os.path.isfile(advisor_file):
                spec = importlib.util.spec_from_file_location("conda.psi4_path_advisor", advisor_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._modules["conda.psi4_path_advisor"] = module
                else:
                    self._import_errors["conda.psi4_path_advisor"] = "Unable to build import spec for advisor script."
            else:
                self._import_errors["conda.psi4_path_advisor"] = f"Advisor script not found: {advisor_file}"
        except Exception as exc:
            self._import_errors["conda.psi4_path_advisor"] = str(exc)

    def health(self) -> Dict[str, Any]:
        """
        Report import health and module availability.

        Returns:
            Dict with status, available modules, and captured import errors.
        """
        return self._ok(
            "Adapter health check completed.",
            data={
                "available_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "import_feasibility": 0.42,
                "intrusiveness_risk": "medium",
                "complexity": "complex",
            },
        )

    # -------------------------------------------------------------------------
    # Psi4 runtime module wrappers (psi4.run_psi4)
    # -------------------------------------------------------------------------
    def psi4_run_module_info(self) -> Dict[str, Any]:
        """
        Introspect the psi4.run_psi4 module and expose callable symbols.

        Returns:
            Unified status dictionary with module metadata.
        """
        mod = self._modules.get("psi4.run_psi4")
        if mod is None:
            return self._err(
                "Failed to import psi4.run_psi4.",
                guidance="Build/install Psi4 core extensions and ensure source/psi4 is importable.",
            )
        callables = [name for name in dir(mod) if callable(getattr(mod, name, None))]
        return self._ok("psi4.run_psi4 module loaded.", data={"callables": sorted(callables)})

    def psi4_run_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from psi4.run_psi4.

        Parameters:
            function_name: Name of the function in psi4.run_psi4.
            *args: Positional arguments for the target function.
            **kwargs: Keyword arguments for the target function.

        Returns:
            Unified status dictionary with result or actionable error guidance.
        """
        mod = self._modules.get("psi4.run_psi4")
        if mod is None:
            return self._err(
                "psi4.run_psi4 is unavailable.",
                guidance="Compile Psi4 and verify runtime shared libraries are discoverable.",
            )
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found in psi4.run_psi4.",
                    guidance="Call psi4_run_module_info() to list available callables.",
                )
            result = fn(*args, **kwargs)
            return self._ok(f"Function '{function_name}' executed successfully.", data={"result": result})
        except Exception as exc:
            return self._err(
                f"Execution failed for psi4.run_psi4.{function_name}: {exc}",
                guidance="Check function signature, required Psi4 runtime environment, and input validity.",
            )

    # -------------------------------------------------------------------------
    # Path advisor utility wrappers (conda/psi4-path-advisor.py)
    # -------------------------------------------------------------------------
    def path_advisor_module_info(self) -> Dict[str, Any]:
        """
        Introspect the conda path advisor utility module and expose callable symbols.

        Returns:
            Unified status dictionary with callable listing.
        """
        mod = self._modules.get("conda.psi4_path_advisor")
        if mod is None:
            return self._err(
                "Failed to load conda.psi4_path_advisor.",
                guidance="Ensure source/conda/psi4-path-advisor.py exists and is readable.",
            )
        callables = [name for name in dir(mod) if callable(getattr(mod, name, None))]
        return self._ok("conda.psi4_path_advisor module loaded.", data={"callables": sorted(callables)})

    def path_advisor_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from the path advisor utility.

        Parameters:
            function_name: Function name exposed by conda.psi4_path_advisor.
            *args: Positional arguments for the target function.
            **kwargs: Keyword arguments for the target function.

        Returns:
            Unified status dictionary with invocation result or guidance.
        """
        mod = self._modules.get("conda.psi4_path_advisor")
        if mod is None:
            return self._err(
                "Path advisor utility is unavailable.",
                guidance="Use CLI fallback by executing source/conda/psi4-path-advisor.py directly.",
            )
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found in conda.psi4_path_advisor.",
                    guidance="Call path_advisor_module_info() to inspect available callables.",
                )
            result = fn(*args, **kwargs)
            return self._ok(f"Function '{function_name}' executed successfully.", data={"result": result})
        except Exception as exc:
            return self._err(
                f"Execution failed for conda.psi4_path_advisor.{function_name}: {exc}",
                guidance="Validate arguments and environment assumptions expected by advisor utilities.",
            )

    # -------------------------------------------------------------------------
    # Fallback and orchestration utilities
    # -------------------------------------------------------------------------
    def cli_fallback_suggestions(self) -> Dict[str, Any]:
        """
        Provide fallback execution suggestions when import mode is partially unavailable.

        Returns:
            Unified status dictionary with practical CLI alternatives.
        """
        suggestions: List[str] = [
            "Run Psi4 entrypoint directly: python -m psi4.run_psi4 --help",
            "Run path advisor script directly: python source/conda/psi4-path-advisor.py --help",
            "If import fails, build Psi4 native components and ensure shared libraries are on runtime paths.",
        ]
        return self._ok("CLI fallback suggestions generated.", data={"suggestions": suggestions})