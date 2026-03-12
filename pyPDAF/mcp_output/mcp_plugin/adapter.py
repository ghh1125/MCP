import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the pyPDAF repository.

    This adapter attempts to import and expose core pyPDAF modules and selected
    callable utilities with robust error handling and consistent return format.

    Unified return schema:
    {
        "status": "success" | "error" | "fallback",
        "message": str,
        "data": Any (optional),
        "error": str (optional),
        "traceback": str (optional),
        "mode": "import"
    }
    """

    # -------------------------------------------------------------------------
    # Initialization and module registry
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and prepare module registry.
        """
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._module_map = {
            "pyPDAF": "pyPDAF",
            "pyPDAF_core": "pyPDAF.__init__",
            "PDAF": "pyPDAF.PDAF",
            "PDAF3": "pyPDAF.PDAF3",
            "PDAFlocal": "pyPDAF.PDAFlocal",
            "PDAFlocalomi": "pyPDAF.PDAFlocalomi",
            "PDAFomi": "pyPDAF.PDAFomi",
            "docstring_pkg": "tool.docstring",
            "docstrings": "tool.docstring.docstrings",
            "pdaf_assimilate_docstrings": "tool.docstring.pdaf_assimilate_docstrings",
            "pdaf_diag_docstrings": "tool.docstring.pdaf_diag_docstrings",
            "pdaf_put_state_docstrings": "tool.docstring.pdaf_put_state_docstrings",
            "pdaflocal_assimilate_docstrings": "tool.docstring.pdaflocal_assimilate_docstrings",
            "pdaflocalomi_assimilate_docstrings": "tool.docstring.pdaflocalomi_assimilate_docstrings",
            "pdaflocalomi_put_state_docstrings": "tool.docstring.pdaflocalomi_put_state_docstrings",
            "pdafomi_assimilate_docstrings": "tool.docstring.pdafomi_assimilate_docstrings",
            "pdafomi_put_state_docstrings": "tool.docstring.pdafomi_put_state_docstrings",
            "compare_subroutines": "tool.compare_subroutines",
            "get_decls": "tool.get_decls",
            "get_decls_cb": "tool.get_decls_cb",
            "write_binding": "tool.write_binding",
            "write_cb_pxd": "tool.write_cb_pxd",
            "write_cb_pyx": "tool.write_cb_pyx",
            "write_pdaf_pxd": "tool.write_pdaf_pxd",
            "write_pdaf_pyx": "tool.write_pdaf_pyx",
        }

        self._bootstrap_imports()

    def _result(
        self,
        status: str,
        message: str,
        data: Any = None,
        error: Optional[str] = None,
        tb: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = {"status": status, "message": message, "mode": self.mode}
        if data is not None:
            result["data"] = data
        if error:
            result["error"] = error
        if tb:
            result["traceback"] = tb
        return result

    def _bootstrap_imports(self) -> None:
        for key, module_path in self._module_map.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as exc:
                self._modules[key] = None
                self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import status.

        Returns:
            dict: Unified status dictionary with loaded and failed modules.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        failed = {k: self._import_errors[k] for k, v in self._modules.items() if v is None}
        if failed:
            return self._result(
                "fallback",
                "Partial import success. Some modules are unavailable; check 'data.failed' and install build/runtime dependencies (numpy, mpi4py, compiled PDAF backend).",
                data={"loaded": loaded, "failed": failed},
            )
        return self._result("success", "All mapped modules imported successfully.", data={"loaded": loaded})

    # -------------------------------------------------------------------------
    # Generic module and symbol access
    # -------------------------------------------------------------------------
    def get_module(self, module_key: str) -> Dict[str, Any]:
        """
        Get imported module object by registry key.

        Args:
            module_key: Internal module key from the adapter registry.

        Returns:
            dict: Unified status dictionary with module object if available.
        """
        if module_key not in self._modules:
            return self._result(
                "error",
                f"Unknown module key '{module_key}'. Use health_check() to inspect available keys.",
            )
        module_obj = self._modules[module_key]
        if module_obj is None:
            return self._result(
                "fallback",
                f"Module '{module_key}' is not available in import mode.",
                error=self._import_errors.get(module_key, "Unknown import error."),
            )
        return self._result("success", f"Module '{module_key}' retrieved.", data=module_obj)

    def call_module_function(
        self,
        module_key: str,
        function_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call a function from a registered module.

        Args:
            module_key: Internal module key.
            function_name: Name of the callable attribute inside the module.
            args: Positional arguments list.
            kwargs: Keyword arguments dictionary.

        Returns:
            dict: Unified status dictionary with call result.
        """
        args = args or []
        kwargs = kwargs or {}

        mod_resp = self.get_module(module_key)
        if mod_resp["status"] != "success":
            return mod_resp

        module_obj = mod_resp["data"]
        if not hasattr(module_obj, function_name):
            return self._result(
                "error",
                f"Function '{function_name}' was not found in module '{module_key}'. Verify symbol name and repository version.",
            )
        fn = getattr(module_obj, function_name)
        if not callable(fn):
            return self._result(
                "error",
                f"Attribute '{function_name}' in module '{module_key}' is not callable.",
            )
        try:
            output = fn(*args, **kwargs)
            return self._result(
                "success",
                f"Function '{function_name}' executed successfully from '{module_key}'.",
                data=output,
            )
        except Exception as exc:
            return self._result(
                "error",
                f"Function '{function_name}' execution failed. Check argument compatibility and backend availability.",
                error=f"{type(exc).__name__}: {exc}",
                tb=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # pyPDAF package instance methods (module-focused as classes not explicitly identified)
    # -------------------------------------------------------------------------
    def instance_pyPDAF(self) -> Dict[str, Any]:
        """Return pyPDAF top-level module instance."""
        return self.get_module("pyPDAF")

    def instance_PDAF(self) -> Dict[str, Any]:
        """Return pyPDAF.PDAF module instance."""
        return self.get_module("PDAF")

    def instance_PDAF3(self) -> Dict[str, Any]:
        """Return pyPDAF.PDAF3 module instance."""
        return self.get_module("PDAF3")

    def instance_PDAFlocal(self) -> Dict[str, Any]:
        """Return pyPDAF.PDAFlocal module instance."""
        return self.get_module("PDAFlocal")

    def instance_PDAFlocalomi(self) -> Dict[str, Any]:
        """Return pyPDAF.PDAFlocalomi module instance."""
        return self.get_module("PDAFlocalomi")

    def instance_PDAFomi(self) -> Dict[str, Any]:
        """Return pyPDAF.PDAFomi module instance."""
        return self.get_module("PDAFomi")

    # -------------------------------------------------------------------------
    # Tooling module instance methods
    # -------------------------------------------------------------------------
    def instance_docstrings(self) -> Dict[str, Any]:
        """Return tool.docstring.docstrings module instance."""
        return self.get_module("docstrings")

    def instance_compare_subroutines(self) -> Dict[str, Any]:
        """Return tool.compare_subroutines module instance."""
        return self.get_module("compare_subroutines")

    def instance_get_decls(self) -> Dict[str, Any]:
        """Return tool.get_decls module instance."""
        return self.get_module("get_decls")

    def instance_get_decls_cb(self) -> Dict[str, Any]:
        """Return tool.get_decls_cb module instance."""
        return self.get_module("get_decls_cb")

    def instance_write_binding(self) -> Dict[str, Any]:
        """Return tool.write_binding module instance."""
        return self.get_module("write_binding")

    def instance_write_cb_pxd(self) -> Dict[str, Any]:
        """Return tool.write_cb_pxd module instance."""
        return self.get_module("write_cb_pxd")

    def instance_write_cb_pyx(self) -> Dict[str, Any]:
        """Return tool.write_cb_pyx module instance."""
        return self.get_module("write_cb_pyx")

    def instance_write_pdaf_pxd(self) -> Dict[str, Any]:
        """Return tool.write_pdaf_pxd module instance."""
        return self.get_module("write_pdaf_pxd")

    def instance_write_pdaf_pyx(self) -> Dict[str, Any]:
        """Return tool.write_pdaf_pyx module instance."""
        return self.get_module("write_pdaf_pyx")

    # -------------------------------------------------------------------------
    # Generic execution helpers for pyPDAF-oriented modules
    # -------------------------------------------------------------------------
    def call_pdaf(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from pyPDAF.PDAF."""
        return self.call_module_function("PDAF", function_name, list(args), kwargs)

    def call_pdaf3(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from pyPDAF.PDAF3."""
        return self.call_module_function("PDAF3", function_name, list(args), kwargs)

    def call_pdaflocal(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from pyPDAF.PDAFlocal."""
        return self.call_module_function("PDAFlocal", function_name, list(args), kwargs)

    def call_pdaflocalomi(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from pyPDAF.PDAFlocalomi."""
        return self.call_module_function("PDAFlocalomi", function_name, list(args), kwargs)

    def call_pdafomi(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call a function from pyPDAF.PDAFomi."""
        return self.call_module_function("PDAFomi", function_name, list(args), kwargs)

    # -------------------------------------------------------------------------
    # Docstring and codegen helper calls
    # -------------------------------------------------------------------------
    def call_docstrings(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.docstring.docstrings."""
        return self.call_module_function("docstrings", function_name, list(args), kwargs)

    def call_compare_subroutines(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.compare_subroutines."""
        return self.call_module_function("compare_subroutines", function_name, list(args), kwargs)

    def call_get_decls(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.get_decls."""
        return self.call_module_function("get_decls", function_name, list(args), kwargs)

    def call_get_decls_cb(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.get_decls_cb."""
        return self.call_module_function("get_decls_cb", function_name, list(args), kwargs)

    def call_write_binding(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.write_binding."""
        return self.call_module_function("write_binding", function_name, list(args), kwargs)

    def call_write_cb_pxd(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.write_cb_pxd."""
        return self.call_module_function("write_cb_pxd", function_name, list(args), kwargs)

    def call_write_cb_pyx(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.write_cb_pyx."""
        return self.call_module_function("write_cb_pyx", function_name, list(args), kwargs)

    def call_write_pdaf_pxd(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.write_pdaf_pxd."""
        return self.call_module_function("write_pdaf_pxd", function_name, list(args), kwargs)

    def call_write_pdaf_pyx(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call function from tool.write_pdaf_pyx."""
        return self.call_module_function("write_pdaf_pyx", function_name, list(args), kwargs)

    # -------------------------------------------------------------------------
    # Fallback and diagnostics
    # -------------------------------------------------------------------------
    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide actionable troubleshooting guidance when import mode is degraded.
        """
        guidance = [
            "Ensure Python dependencies are installed: numpy, mpi4py.",
            "Build or provide compiled PDAF backend libraries required by pyPDAF wrappers.",
            "If using developer tooling, install optional build/test dependencies such as cython and pytest.",
            "Verify that the repository 'source' directory is present and readable at runtime.",
            "Run health_check() to identify exactly which module imports failed.",
        ]
        return self._result("success", "Fallback guidance generated.", data=guidance)