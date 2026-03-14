import os
import sys

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)

from typing import Any, Dict, List, Optional


class Adapter:
    """
    MCP Import Mode Adapter for FEniCS UFL repository.

    This adapter prioritizes import-based execution against repository source code
    available under the local `source` directory. It provides robust fallback behavior
    if imports fail, and returns a unified response format for all methods.
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state, import mode, and module registry.
        """
        self.mode = "import"
        self._import_ok = False
        self._import_error: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._initialize_imports()

    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "ok", "mode": self.mode, "message": message, "data": data}

    def _error(
        self,
        message: str,
        error: Optional[Exception] = None,
        guidance: str = "Check repository source placement and Python dependencies.",
    ) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": str(error) if error else None,
            "guidance": guidance,
        }

    def _initialize_imports(self) -> None:
        """
        Attempt to import core UFL modules from repository source with graceful fallback.
        """
        try:
            import source.ufl as ufl_pkg
            import source.ufl.algorithms as algorithms_pkg
            import source.ufl.core as core_pkg
            import source.ufl.corealg as corealg_pkg
            import source.ufl.formatting as formatting_pkg
            import source.ufl.utils as utils_pkg

            self._modules["ufl"] = ufl_pkg
            self._modules["algorithms"] = algorithms_pkg
            self._modules["core"] = core_pkg
            self._modules["corealg"] = corealg_pkg
            self._modules["formatting"] = formatting_pkg
            self._modules["utils"] = utils_pkg

            self._import_ok = True
        except Exception as exc:
            self._import_ok = False
            self._import_error = str(exc)

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter and import health status.
        """
        return self._ok(
            data={
                "import_ready": self._import_ok,
                "import_error": self._import_error,
                "available_modules": sorted(self._modules.keys()),
                "dependencies": {
                    "required": ["python>=3.9", "numpy"],
                    "optional": ["pytest", "sphinx"],
                },
                "risk": {
                    "import_feasibility": 0.95,
                    "intrusiveness_risk": "low",
                    "complexity": "medium",
                },
            },
            message="adapter status",
        )

    def list_capabilities(self) -> Dict[str, Any]:
        """
        List capabilities exposed by this adapter.
        """
        capabilities = [
            "import source.ufl modules",
            "inspect module attributes",
            "create class instances dynamically",
            "invoke callable functions dynamically",
            "fallback guidance on import failures",
        ]
        return self._ok(data=capabilities, message="capabilities listed")

    # -------------------------------------------------------------------------
    # Generic dynamic class/function accessors
    # -------------------------------------------------------------------------
    def create_instance(
        self,
        module_key: str,
        class_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an instance of a class from a loaded module.

        Parameters:
        - module_key: Registry key from loaded modules (e.g., 'ufl', 'algorithms').
        - class_name: Name of class to instantiate.
        - args: Positional arguments list.
        - kwargs: Keyword arguments dictionary.

        Returns:
        Unified status dictionary containing instance metadata.
        """
        if not self._import_ok:
            return self._error(
                message="Import mode is unavailable.",
                guidance="Ensure source/ufl exists and includes importable Python package files.",
            )
        try:
            args = args or []
            kwargs = kwargs or {}
            module = self._modules.get(module_key)
            if module is None:
                return self._error(
                    message=f"Unknown module key: {module_key}",
                    guidance=f"Use one of: {', '.join(sorted(self._modules.keys()))}",
                )
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                data={
                    "module_key": module_key,
                    "class_name": class_name,
                    "instance_type": type(instance).__name__,
                    "repr": repr(instance),
                },
                message="instance created",
            )
        except AttributeError as exc:
            return self._error(
                message=f"Class not found: {class_name}",
                error=exc,
                guidance="Verify class name and module key, then inspect module attributes.",
            )
        except Exception as exc:
            return self._error(
                message="Failed to create class instance.",
                error=exc,
                guidance="Review constructor arguments and class requirements.",
            )

    def call_function(
        self,
        module_key: str,
        function_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call a function/callable by name from a loaded module.

        Parameters:
        - module_key: Registry key from loaded modules.
        - function_name: Callable attribute name.
        - args: Positional arguments list.
        - kwargs: Keyword arguments dictionary.

        Returns:
        Unified status dictionary containing function call result.
        """
        if not self._import_ok:
            return self._error(
                message="Import mode is unavailable.",
                guidance="Ensure local repository source is available under source/ and dependencies are installed.",
            )
        try:
            args = args or []
            kwargs = kwargs or {}
            module = self._modules.get(module_key)
            if module is None:
                return self._error(
                    message=f"Unknown module key: {module_key}",
                    guidance=f"Use one of: {', '.join(sorted(self._modules.keys()))}",
                )
            fn = getattr(module, function_name)
            if not callable(fn):
                return self._error(
                    message=f"Attribute is not callable: {function_name}",
                    guidance="Inspect module attributes and select a function or callable class.",
                )
            result = fn(*args, **kwargs)
            return self._ok(
                data={
                    "module_key": module_key,
                    "function_name": function_name,
                    "result": result,
                },
                message="function called",
            )
        except AttributeError as exc:
            return self._error(
                message=f"Function not found: {function_name}",
                error=exc,
                guidance="Verify function name against repository module exports.",
            )
        except Exception as exc:
            return self._error(
                message="Function call failed.",
                error=exc,
                guidance="Review input arguments and function signature.",
            )

    # -------------------------------------------------------------------------
    # UFL-focused helper methods (high-value import-mode workflow)
    # -------------------------------------------------------------------------
    def get_module_attributes(self, module_key: str) -> Dict[str, Any]:
        """
        Get public attributes of a loaded module.

        Parameters:
        - module_key: Registry key ('ufl', 'algorithms', 'core', 'corealg', 'formatting', 'utils').

        Returns:
        Unified status dictionary with sorted public attribute names.
        """
        if not self._import_ok:
            return self._error(
                message="Cannot inspect modules because imports are unavailable.",
                guidance="Resolve import errors first using get_status().",
            )
        module = self._modules.get(module_key)
        if module is None:
            return self._error(
                message=f"Unknown module key: {module_key}",
                guidance=f"Use one of: {', '.join(sorted(self._modules.keys()))}",
            )
        attrs = sorted([a for a in dir(module) if not a.startswith("_")])
        return self._ok(
            data={"module_key": module_key, "attributes": attrs},
            message="module attributes retrieved",
        )

    def evaluate_expression(self, expression: Any, mapping: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Attempt to evaluate a UFL expression if it provides an `evaluate` method.

        Parameters:
        - expression: UFL expression object.
        - mapping: Optional mapping used by expression evaluate methods.

        Returns:
        Unified status dictionary with evaluation result.
        """
        try:
            if expression is None:
                return self._error(
                    message="Expression is required.",
                    guidance="Provide a valid UFL expression object.",
                )
            if not hasattr(expression, "evaluate"):
                return self._error(
                    message="Provided object does not support evaluation.",
                    guidance="Pass an object with an evaluate() method.",
                )
            mapping = mapping or {}
            result = expression.evaluate(mapping)
            return self._ok(data={"result": result}, message="expression evaluated")
        except Exception as exc:
            return self._error(
                message="Expression evaluation failed.",
                error=exc,
                guidance="Check expression compatibility and evaluation context.",
            )

    def fallback_blackbox(self, task: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide graceful fallback guidance when import mode is unavailable.

        Parameters:
        - task: User task description.
        - payload: Optional task-specific input data.

        Returns:
        Unified status dictionary with fallback instructions.
        """
        return self._ok(
            data={
                "strategy": "blackbox",
                "task": task,
                "payload": payload or {},
                "note": "Import mode failed or is insufficient for this task.",
                "next_steps": [
                    "Verify source path and package structure.",
                    "Install required dependencies (numpy, Python>=3.9).",
                    "Retry import mode, then run task again.",
                ],
            },
            message="fallback guidance",
        )