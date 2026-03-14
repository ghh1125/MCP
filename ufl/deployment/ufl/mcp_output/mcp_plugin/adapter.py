import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for FEniCS UFL repository.

    This adapter attempts direct import-based integration first and gracefully
    falls back to a non-import mode when runtime constraints prevent loading.
    """

    # ---------------------------------------------------------------------
    # Lifecycle / Initialization
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize the adapter.

        Attributes:
            mode (str): Adapter mode, fixed to "import" as requested.
            available (bool): Whether import mode is currently operational.
            modules (dict): Loaded module objects keyed by full package path.
            errors (list): Import and runtime errors captured during setup.
        """
        self.mode: str = "import"
        self.available: bool = False
        self.modules: Dict[str, Any] = {}
        self.errors: List[str] = []
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Load high-value UFL modules discovered from repository analysis.
        """
        module_names = [
            "deployment.ufl.source.ufl",
            "deployment.ufl.source.ufl.algorithms",
            "deployment.ufl.source.ufl.algorithms.analysis",
            "deployment.ufl.source.ufl.algorithms.apply_derivatives",
            "deployment.ufl.source.ufl.algorithms.compute_form_data",
            "deployment.ufl.source.ufl.algorithms.domain_analysis",
            "deployment.ufl.source.ufl.algorithms.estimate_degrees",
            "deployment.ufl.source.ufl.algorithms.expand_indices",
            "deployment.ufl.source.ufl.algorithms.formsplitter",
            "deployment.ufl.source.ufl.algorithms.formtransformations",
            "deployment.ufl.source.ufl.algorithms.map_integrands",
            "deployment.ufl.source.ufl.algorithms.replace",
            "deployment.ufl.source.ufl.algorithms.signature",
            "deployment.ufl.source.ufl.cell",
            "deployment.ufl.source.ufl.constant",
            "deployment.ufl.source.ufl.coefficient",
            "deployment.ufl.source.ufl.finiteelement",
            "deployment.ufl.source.ufl.form",
            "deployment.ufl.source.ufl.formoperators",
            "deployment.ufl.source.ufl.functionspace",
            "deployment.ufl.source.ufl.geometry",
            "deployment.ufl.source.ufl.measure",
            "deployment.ufl.source.ufl.operators",
            "deployment.ufl.source.ufl.tensoralgebra",
            "deployment.ufl.source.ufl.tensors",
            "deployment.ufl.source.ufl.variable",
        ]

        loaded = 0
        for name in module_names:
            try:
                self.modules[name] = importlib.import_module(name)
                loaded += 1
            except Exception as exc:
                self.errors.append(f"Failed to import {name}: {exc}")

        self.available = loaded > 0

    # ---------------------------------------------------------------------
    # Unified response helpers
    # ---------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _fail(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": (
                f"Import mode is unavailable for action '{action}'. "
                f"Check source path and repository layout at: {source_path}. "
                "Ensure deployment.ufl.source package exists and is importable."
            ),
            "errors": self.errors,
        }

    # ---------------------------------------------------------------------
    # Status / diagnostics
    # ---------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Run adapter health checks.

        Returns:
            dict: Unified status dictionary including loaded modules and import errors.
        """
        return self._ok(
            data={
                "available": self.available,
                "loaded_module_count": len(self.modules),
                "loaded_modules": sorted(self.modules.keys()),
                "import_errors": self.errors,
                "python_version": sys.version,
                "source_path": source_path,
            },
            message="Adapter health report generated.",
        )

    # ---------------------------------------------------------------------
    # Dynamic module / symbol management
    # ---------------------------------------------------------------------
    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Dynamically import a module by full package path.

        Args:
            module_path: Full import path, e.g. 'deployment.ufl.source.ufl.form'.

        Returns:
            dict: Unified status with module metadata.
        """
        try:
            mod = importlib.import_module(module_path)
            self.modules[module_path] = mod
            self.available = True
            return self._ok(
                data={"module": module_path, "attributes": len(dir(mod))},
                message=f"Module imported: {module_path}",
            )
        except Exception as exc:
            return self._fail(
                f"Unable to import module '{module_path}'. Verify package path and dependencies.",
                exc,
            )

    def get_symbol(self, module_path: str, symbol_name: str) -> Dict[str, Any]:
        """
        Fetch a symbol (class/function/constant) from a loaded module.

        Args:
            module_path: Full module path.
            symbol_name: Attribute name to retrieve.

        Returns:
            dict: Unified status with symbol type and callable info.
        """
        try:
            if module_path not in self.modules:
                mod_result = self.import_module(module_path)
                if mod_result["status"] != "success":
                    return mod_result
            mod = self.modules[module_path]
            if not hasattr(mod, symbol_name):
                return self._fail(
                    f"Symbol '{symbol_name}' not found in module '{module_path}'.",
                    None,
                )
            sym = getattr(mod, symbol_name)
            return self._ok(
                data={
                    "module": module_path,
                    "symbol": symbol_name,
                    "type": type(sym).__name__,
                    "callable": callable(sym),
                },
                message="Symbol resolved successfully.",
            )
        except Exception as exc:
            return self._fail("Failed to resolve symbol.", exc)

    # ---------------------------------------------------------------------
    # Generic class/function invocation
    # ---------------------------------------------------------------------
    def create_instance(
        self, module_path: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Instantiate a class from a given module.

        Args:
            module_path: Full module import path.
            class_name: Class name to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status with instance repr and type.
        """
        if not self.available and not self.modules:
            return self._fallback("create_instance")
        try:
            symbol_result = self.get_symbol(module_path, class_name)
            if symbol_result["status"] != "success":
                return symbol_result
            cls = getattr(self.modules[module_path], class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                data={
                    "module": module_path,
                    "class": class_name,
                    "instance_type": type(instance).__name__,
                    "instance_repr": repr(instance),
                },
                message="Class instance created successfully.",
            )
        except Exception as exc:
            return self._fail(
                f"Failed to instantiate class '{class_name}' from '{module_path}'.",
                exc,
            )

    def call_function(
        self, module_path: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function from a given module.

        Args:
            module_path: Full module import path.
            function_name: Function name to call.
            *args: Positional call arguments.
            **kwargs: Keyword call arguments.

        Returns:
            dict: Unified status with call result.
        """
        if not self.available and not self.modules:
            return self._fallback("call_function")
        try:
            symbol_result = self.get_symbol(module_path, function_name)
            if symbol_result["status"] != "success":
                return symbol_result
            fn = getattr(self.modules[module_path], function_name)
            if not callable(fn):
                return self._fail(
                    f"Symbol '{function_name}' in '{module_path}' is not callable.",
                    None,
                )
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "module": module_path,
                    "function": function_name,
                    "result_type": type(result).__name__,
                    "result": result,
                },
                message="Function called successfully.",
            )
        except Exception as exc:
            return self._fail(
                f"Failed to call function '{function_name}' from '{module_path}'.",
                exc,
            )

    # ---------------------------------------------------------------------
    # UFL-specific convenience methods (high-value coverage from analysis)
    # ---------------------------------------------------------------------
    def create_cell(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.cell", "Cell", *args, **kwargs)

    def create_constant(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.constant", "Constant", *args, **kwargs)

    def create_coefficient(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.coefficient", "Coefficient", *args, **kwargs)

    def create_finite_element(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.finiteelement", "FiniteElement", *args, **kwargs)

    def create_function_space(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.functionspace", "FunctionSpace", *args, **kwargs)

    def create_measure(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.measure", "Measure", *args, **kwargs)

    def create_variable(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_instance("deployment.ufl.source.ufl.variable", "Variable", *args, **kwargs)

    def compute_form_data(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "deployment.ufl.source.ufl.algorithms.compute_form_data",
            "compute_form_data",
            *args,
            **kwargs,
        )

    def estimate_total_polynomial_degree(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "deployment.ufl.source.ufl.algorithms.estimate_degrees",
            "estimate_total_polynomial_degree",
            *args,
            **kwargs,
        )

    def expand_indices(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "deployment.ufl.source.ufl.algorithms.expand_indices",
            "expand_indices",
            *args,
            **kwargs,
        )

    def replace(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "deployment.ufl.source.ufl.algorithms.replace",
            "replace",
            *args,
            **kwargs,
        )

    def compute_signature(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_function(
            "deployment.ufl.source.ufl.algorithms.signature",
            "compute_expression_signature",
            *args,
            **kwargs,
        )