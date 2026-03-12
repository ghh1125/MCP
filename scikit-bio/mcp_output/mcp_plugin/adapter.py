import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Callable

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for scikit-bio repository.

    This adapter prioritizes importing real implementations from the local
    repository source tree. If imports fail, it provides graceful fallback
    responses with actionable guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_modules()

    # =========================================================================
    # Internal Utilities
    # =========================================================================
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = str(error)
        if hint:
            payload["hint"] = hint
        return payload

    def _fallback(self, operation: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": f"Import unavailable for operation '{operation}'.",
            "hint": (
                "Verify repository source exists under '<plugin_root>/source', "
                "ensure Python dependencies are installed (numpy, scipy, pandas), "
                "and confirm this runtime can import 'skbio'."
            ),
            "import_errors": self._import_errors,
        }

    def _safe_call(self, fn: Callable[..., Any], operation: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = fn(**kwargs)
            return self._ok({"result": result}, message=f"{operation} executed")
        except Exception as e:
            return self._error(
                f"Execution failed for '{operation}'.",
                error=e,
                hint="Check input argument types and values for this operation.",
            )

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as e:
            self._import_errors[module_path] = f"{type(e).__name__}: {e}"
            return None

    def _initialize_modules(self) -> None:
        target_modules = [
            "skbio",
            "skbio.alignment",
            "skbio.binaries",
            "skbio.diversity",
            "skbio.embedding",
            "skbio.io",
            "skbio.metadata",
            "skbio.sequence",
            "skbio.stats",
            "skbio.table",
            "skbio.tree",
            "skbio.util",
        ]
        for m in target_modules:
            self._import_module(m)

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import health and module readiness.

        Returns:
            dict: Unified status dictionary including loaded modules and errors.
        """
        loaded = sorted(self._modules.keys())
        return self._ok(
            {
                "loaded_modules": loaded,
                "loaded_count": len(loaded),
                "import_error_count": len(self._import_errors),
                "import_errors": self._import_errors,
            },
            message="Adapter health check complete",
        )

    # =========================================================================
    # Top-level skbio convenience wrappers
    # =========================================================================
    def call_skbio_read(self, file: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call skbio.read using repository implementation.

        Args:
            file: Path, file handle, or supported input object.
            **kwargs: Forwarded to skbio.read.

        Returns:
            dict: Unified status payload with read result.
        """
        mod = self._modules.get("skbio")
        if not mod or not hasattr(mod, "read"):
            return self._fallback("skbio.read")
        return self._safe_call(getattr(mod, "read"), "skbio.read", file=file, **kwargs)

    def call_skbio_write(self, obj: Any, into: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call skbio.write using repository implementation.

        Args:
            obj: Object to serialize.
            into: Destination path or file-like object.
            **kwargs: Forwarded to skbio.write.

        Returns:
            dict: Unified status payload.
        """
        mod = self._modules.get("skbio")
        if not mod or not hasattr(mod, "write"):
            return self._fallback("skbio.write")
        return self._safe_call(getattr(mod, "write"), "skbio.write", obj=obj, into=into, **kwargs)

    # =========================================================================
    # Generic module/class/function adapters
    # =========================================================================
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a given module.

        Args:
            module_path: Full import path (e.g., 'skbio.sequence').
            class_name: Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        mod = self._modules.get(module_path) or self._import_module(module_path)
        if mod is None:
            return self._fallback(f"{module_path}.{class_name}")
        if not hasattr(mod, class_name):
            return self._error(
                f"Class '{class_name}' not found in module '{module_path}'.",
                hint="Check class name spelling and module path from repository exports.",
            )
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, message=f"Instance created: {module_path}.{class_name}")
        except Exception as e:
            return self._error(
                f"Failed to instantiate '{module_path}.{class_name}'.",
                error=e,
                hint="Validate constructor arguments against class signature.",
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a given module dynamically.

        Args:
            module_path: Full import path (e.g., 'skbio.stats').
            function_name: Function name to invoke.
            *args: Positional args for the function.
            **kwargs: Keyword args for the function.

        Returns:
            dict: Unified status payload with function result.
        """
        mod = self._modules.get(module_path) or self._import_module(module_path)
        if mod is None:
            return self._fallback(f"{module_path}.{function_name}")
        if not hasattr(mod, function_name):
            return self._error(
                f"Function '{function_name}' not found in module '{module_path}'.",
                hint="Check function name spelling and whether it is publicly exported.",
            )
        fn = getattr(mod, function_name)
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"Function called: {module_path}.{function_name}")
        except Exception as e:
            return self._error(
                f"Failed calling '{module_path}.{function_name}'.",
                error=e,
                hint="Inspect function arguments and data compatibility.",
            )

    # =========================================================================
    # Package-specific convenience entrypoints (based on discovered structure)
    # =========================================================================
    def module_info(self, module_path: str) -> Dict[str, Any]:
        """
        Return basic metadata for a loaded/importable module.

        Args:
            module_path: Full module path.

        Returns:
            dict: Status and metadata including exported attributes.
        """
        mod = self._modules.get(module_path) or self._import_module(module_path)
        if mod is None:
            return self._fallback(module_path)
        try:
            attrs = [a for a in dir(mod) if not a.startswith("_")]
            return self._ok(
                {
                    "module": module_path,
                    "attribute_count": len(attrs),
                    "attributes": attrs,
                },
                message=f"Module info retrieved: {module_path}",
            )
        except Exception as e:
            return self._error(
                f"Failed to inspect module '{module_path}'.",
                error=e,
                hint="Try a valid, importable module path from the repository.",
            )

    def list_supported_packages(self) -> Dict[str, Any]:
        """
        List package groups identified by repository analysis.

        Returns:
            dict: Unified status payload containing package paths.
        """
        packages = [
            "skbio",
            "skbio.alignment",
            "skbio.binaries",
            "skbio.diversity",
            "skbio.embedding",
            "skbio.io",
            "skbio.metadata",
            "skbio.sequence",
            "skbio.stats",
            "skbio.table",
            "skbio.tree",
            "skbio.util",
        ]
        return self._ok({"packages": packages}, message="Supported packages listed")

    def debug_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback snapshot for debugging context.

        Returns:
            dict: Unified status payload with traceback string.
        """
        tb = traceback.format_exc()
        return self._ok({"traceback": tb}, message="Traceback snapshot generated")