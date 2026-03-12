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
    MCP Import Mode Adapter for the DeepChem repository.

    This adapter is designed to:
    - Prefer direct module import and invocation.
    - Gracefully fall back with actionable messages when optional dependencies are missing.
    - Provide a unified response format across all methods.

    Unified response format:
    {
        "status": "success" | "error",
        "mode": "import",
        "data": ...,
        "error": ...,
        "guidance": ...,
    }
    """

    # ============================================================
    # Initialization and internal utilities
    # ============================================================

    def __init__(self) -> None:
        """
        Initialize adapter state and import cache.
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}

    def _ok(self, data: Any = None, message: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "data": data,
            "message": message,
        }

    def _err(self, error: str, guidance: Optional[str] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "error": error,
            "guidance": guidance
            or "Verify source path, required dependencies, and module availability.",
        }

    def _import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import a module by full package path.

        Parameters
        ----------
        module_path: str
            Full Python module path, for example: 'deepchem.molnet.run_benchmark'

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary containing imported module in `data` on success.
        """
        if module_path in self._modules:
            return self._ok(self._modules[module_path], f"Module already loaded: {module_path}")

        try:
            module = __import__(module_path, fromlist=["*"])
            self._modules[module_path] = module
            return self._ok(module, f"Imported module: {module_path}")
        except Exception as e:
            msg = str(e)
            self._import_errors[module_path] = msg
            return self._err(
                error=f"Failed to import module '{module_path}': {msg}",
                guidance=(
                    "Ensure the repository source is available under the configured source path. "
                    "Install optional dependencies for DeepChem features (e.g., rdkit, torch, tensorflow, jax)."
                ),
            )

    def _call_attr(
        self, module_path: str, attr_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generic safe invoker for a callable attribute in a module.
        """
        mod_result = self._import_module(module_path)
        if mod_result["status"] != "success":
            return mod_result

        module = mod_result["data"]
        if not hasattr(module, attr_name):
            return self._err(
                error=f"Attribute '{attr_name}' not found in module '{module_path}'.",
                guidance="Check API version compatibility and available symbols in the repository.",
            )

        try:
            attr = getattr(module, attr_name)
            if callable(attr):
                value = attr(*args, **kwargs)
                return self._ok(value, f"Called {module_path}.{attr_name} successfully.")
            return self._ok(attr, f"Retrieved attribute {module_path}.{attr_name} successfully.")
        except Exception as e:
            return self._err(
                error=f"Execution failed for '{module_path}.{attr_name}': {e}",
                guidance=(
                    "Validate input parameters and ensure optional runtime dependencies are installed."
                ),
            )

    # ============================================================
    # Repository and environment diagnostics
    # ============================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Validate import readiness for key DeepChem modules and report status.

        Returns
        -------
        Dict[str, Any]
            Unified dictionary with module import checks and recommendations.
        """
        targets = [
            "deepchem",
            "deepchem.molnet.run_benchmark",
            "deepchem.molnet.run_benchmark_low_data",
            "deepchem.molnet.run_benchmark_models",
        ]
        report: List[Dict[str, Any]] = []
        for mod in targets:
            r = self._import_module(mod)
            report.append(
                {
                    "module": mod,
                    "status": r["status"],
                    "message": r.get("message"),
                    "error": r.get("error"),
                }
            )

        failed = [x for x in report if x["status"] != "success"]
        if failed:
            return self._err(
                error="One or more core module imports failed.",
                guidance=(
                    "Inspect 'data' in the response for per-module failures. "
                    "Install required basics: numpy, scipy, pandas, scikit-learn; "
                    "then add optional stacks as needed (rdkit/torch/tensorflow/jax)."
                ),
            ) | {"data": report}
        return self._ok(report, "All targeted modules imported successfully.")

    # ============================================================
    # DeepChem MolNet benchmark entry modules (from LLM analysis)
    # ============================================================

    def import_run_benchmark_module(self) -> Dict[str, Any]:
        """
        Import deepchem.molnet.run_benchmark module.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with the module object on success.
        """
        return self._import_module("deepchem.molnet.run_benchmark")

    def import_run_benchmark_low_data_module(self) -> Dict[str, Any]:
        """
        Import deepchem.molnet.run_benchmark_low_data module.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with the module object on success.
        """
        return self._import_module("deepchem.molnet.run_benchmark_low_data")

    def import_run_benchmark_models_module(self) -> Dict[str, Any]:
        """
        Import deepchem.molnet.run_benchmark_models module.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with the module object on success.
        """
        return self._import_module("deepchem.molnet.run_benchmark_models")

    def get_module_members(self, module_path: str) -> Dict[str, Any]:
        """
        List public members of a module for dynamic discovery.

        Parameters
        ----------
        module_path: str
            Full module path to inspect.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with public member names.
        """
        r = self._import_module(module_path)
        if r["status"] != "success":
            return r
        module = r["data"]
        try:
            members = [m for m in dir(module) if not m.startswith("_")]
            return self._ok({"module": module_path, "members": members})
        except Exception as e:
            return self._err(
                error=f"Failed to inspect module '{module_path}': {e}",
                guidance="Retry with a valid module path and ensure import succeeded.",
            )

    # ============================================================
    # Generic callable/class adapters to maximize import-mode usage
    # ============================================================

    def create_instance(
        self, module_path: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an instance of a class from a fully qualified module path.

        Parameters
        ----------
        module_path: str
            Full module path containing the class.
        class_name: str
            Name of the class to instantiate.
        *args, **kwargs:
            Initialization arguments forwarded to the class constructor.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with created instance on success.
        """
        r = self._import_module(module_path)
        if r["status"] != "success":
            return r
        module = r["data"]
        if not hasattr(module, class_name):
            return self._err(
                error=f"Class '{class_name}' not found in module '{module_path}'.",
                guidance="Use get_module_members to inspect available symbols.",
            )
        try:
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(instance, f"Instantiated {module_path}.{class_name} successfully.")
        except Exception as e:
            return self._err(
                error=f"Failed to instantiate '{module_path}.{class_name}': {e}",
                guidance="Check constructor parameters and dependency requirements.",
            )

    def call_function(
        self, module_path: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from a module by full path and function name.

        Parameters
        ----------
        module_path: str
            Full module path containing the function.
        function_name: str
            Function name to invoke.
        *args, **kwargs:
            Positional and keyword arguments for the function.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with function return value on success.
        """
        return self._call_attr(module_path, function_name, *args, **kwargs)

    # ============================================================
    # Fallback guidance
    # ============================================================

    def fallback_cli_guidance(self) -> Dict[str, Any]:
        """
        Provide non-executing CLI fallback guidance based on identified entry modules.

        Returns
        -------
        Dict[str, Any]
            Unified status dictionary with actionable commands.
        """
        commands = [
            "python -m deepchem.molnet.run_benchmark",
            "python -m deepchem.molnet.run_benchmark_low_data",
            "python -m deepchem.molnet.run_benchmark_models",
        ]
        return self._ok(
            {
                "commands": commands,
                "note": "Use CLI fallback when import-mode execution is blocked by missing optional dependencies.",
            },
            "CLI fallback guidance prepared.",
        )