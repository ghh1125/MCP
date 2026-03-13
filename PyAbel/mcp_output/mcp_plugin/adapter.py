import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the PyAbel repository.

    This adapter prefers direct in-repo imports from the configured `source` path.
    If import fails, methods return graceful fallback responses with actionable guidance.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        module_names = [
            "abel",
            "abel.transform",
            "abel.basex",
            "abel.dasch",
            "abel.daun",
            "abel.direct",
            "abel.hansenlaw",
            "abel.linbasex",
            "abel.nestorolsen",
            "abel.onion_bordas",
            "abel.rbasex",
            "abel.benchmark",
            "abel.tools",
            "abel.tools.analytical",
            "abel.tools.center",
            "abel.tools.circularize",
            "abel.tools.io",
            "abel.tools.math",
            "abel.tools.polar",
            "abel.tools.polynomial",
            "abel.tools.symmetry",
            "abel.tools.transform_pairs",
            "abel.tools.vmi",
        ]

        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as exc:
                self._import_errors[name] = f"{type(exc).__name__}: {exc}"

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "import_errors": self._import_errors,
        }

    def _fail(self, message: str, error: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "error": f"{type(error).__name__}: {error}" if error else None,
            "guidance": guidance or "Verify repository source path and dependency availability (numpy, scipy).",
            "import_errors": self._import_errors,
        }
        return payload

    def _fallback(self, feature: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "message": f"Feature '{feature}' is unavailable in import mode due to missing module/function.",
            "guidance": "Ensure the source tree is present under ../source and required dependencies are installed.",
            "import_errors": self._import_errors,
        }

    def _resolve(self, module_name: str, attr_name: str) -> Tuple[Optional[Any], Optional[str]]:
        module = self._modules.get(module_name)
        if module is None:
            return None, f"Module '{module_name}' not imported."
        obj = getattr(module, attr_name, None)
        if obj is None:
            return None, f"Attribute '{attr_name}' not found in '{module_name}'."
        return obj, None

    # -------------------------------------------------------------------------
    # Health / diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health, import status, and import-mode readiness details.
        """
        return self._ok(
            data={
                "loaded_modules": sorted(list(self._modules.keys())),
                "failed_modules": self._import_errors,
                "import_feasibility": 0.93,
                "intrusiveness_risk": "low",
                "complexity": "medium",
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # High-level Abel transform APIs
    # -------------------------------------------------------------------------
    def transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call abel.transform.Transform constructor.

        Parameters:
            *args, **kwargs: Forwarded to abel.transform.Transform

        Returns:
            Unified status dictionary with created object (non-serialized reference).
        """
        cls, err = self._resolve("abel.transform", "Transform")
        if err:
            return self._fallback("abel.transform.Transform")
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"object": instance}, "Transform instance created")
        except Exception as exc:
            return self._fail("Failed to create Transform instance.", exc, "Check input image shape and method parameters.")

    # -------------------------------------------------------------------------
    # Method-specific transform wrappers
    # -------------------------------------------------------------------------
    def basex_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.basex", "basex_transform")
        if err:
            return self._fallback("abel.basex.basex_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "BASEX transform completed")
        except Exception as exc:
            return self._fail("BASEX transform failed.", exc, "Validate basis settings and numeric input arrays.")

    def daun_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.daun", "daun_transform")
        if err:
            return self._fallback("abel.daun.daun_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "Daun transform completed")
        except Exception as exc:
            return self._fail("Daun transform failed.", exc, "Check regularization options and input radius/image consistency.")

    def direct_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.direct", "direct_transform")
        if err:
            return self._fallback("abel.direct.direct_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "Direct transform completed")
        except Exception as exc:
            return self._fail("Direct transform failed.", exc, "Ensure monotonic radial grid and valid interpolation settings.")

    def hansenlaw_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.hansenlaw", "hansenlaw_transform")
        if err:
            return self._fallback("abel.hansenlaw.hansenlaw_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "Hansen-Law transform completed")
        except Exception as exc:
            return self._fail("Hansen-Law transform failed.", exc, "Verify image dimensions and recursion-compatible parameters.")

    def linbasex_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.linbasex", "linbasex_transform")
        if err:
            return self._fallback("abel.linbasex.linbasex_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "LinBasex transform completed")
        except Exception as exc:
            return self._fail("LinBasex transform failed.", exc, "Check angular basis configuration and image centering.")

    def onion_bordas_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.onion_bordas", "onion_bordas_transform")
        if err:
            return self._fallback("abel.onion_bordas.onion_bordas_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "Onion Bordas transform completed")
        except Exception as exc:
            return self._fail("Onion Bordas transform failed.", exc, "Check image symmetry and projection assumptions.")

    def rbasex_transform(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve("abel.rbasex", "rbasex_transform")
        if err:
            return self._fallback("abel.rbasex.rbasex_transform")
        try:
            return self._ok({"result": fn(*args, **kwargs)}, "rBasex transform completed")
        except Exception as exc:
            return self._fail("rBasex transform failed.", exc, "Validate radial limits, regularization, and data shape.")

    def dasch_methods(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        module = self._modules.get("abel.dasch")
        if module is None:
            return self._fallback("abel.dasch")
        try:
            methods = [name for name in dir(module) if not name.startswith("_")]
            return self._ok({"available": methods}, "Dasch module symbols listed")
        except Exception as exc:
            return self._fail("Failed to inspect Dasch module.", exc)

    # -------------------------------------------------------------------------
    # Tools module generic dispatcher
    # -------------------------------------------------------------------------
    def call_tool_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function under abel.tools.* dynamically.

        Parameters:
            module_name: Full module path, e.g., 'abel.tools.center'
            function_name: Function name in the module
            *args, **kwargs: Forwarded call arguments
        """
        module = self._modules.get(module_name)
        if module is None:
            return self._fallback(f"{module_name}.{function_name}")
        fn = getattr(module, function_name, None)
        if fn is None or not callable(fn):
            return self._fail(
                f"Function '{function_name}' not found or not callable in '{module_name}'.",
                guidance="Inspect module symbols via inspect_module_symbols().",
            )
        try:
            return self._ok({"result": fn(*args, **kwargs)}, f"{module_name}.{function_name} completed")
        except Exception as exc:
            return self._fail(f"Execution failed for {module_name}.{function_name}.", exc)

    def inspect_module_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        Return public symbols for a loaded module to support full function utilization.
        """
        module = self._modules.get(module_name)
        if module is None:
            return self._fallback(module_name)
        try:
            public_symbols = [s for s in dir(module) if not s.startswith("_")]
            return self._ok({"symbols": public_symbols}, f"Symbols listed for {module_name}")
        except Exception as exc:
            return self._fail(f"Failed to inspect symbols in {module_name}.", exc)

    # -------------------------------------------------------------------------
    # Repository-aware convenience methods
    # -------------------------------------------------------------------------
    def benchmark(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        module = self._modules.get("abel.benchmark")
        if module is None:
            return self._fallback("abel.benchmark")
        try:
            if hasattr(module, "benchmark"):
                return self._ok({"result": getattr(module, "benchmark")(*args, **kwargs)}, "Benchmark completed")
            return self._ok({"symbols": [s for s in dir(module) if not s.startswith("_")]}, "Benchmark module loaded")
        except Exception as exc:
            return self._fail("Benchmark execution failed.", exc)

    def raw_call(self, module_name: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Low-level call entry point for any imported module attribute.
        If attribute is callable, it is called; otherwise, value is returned.
        """
        module = self._modules.get(module_name)
        if module is None:
            return self._fallback(f"{module_name}.{attr_name}")
        try:
            obj = getattr(module, attr_name)
        except Exception as exc:
            return self._fail(f"Attribute '{attr_name}' not found in '{module_name}'.", exc)

        try:
            if callable(obj):
                return self._ok({"result": obj(*args, **kwargs)}, f"{module_name}.{attr_name} called")
            return self._ok({"value": obj}, f"{module_name}.{attr_name} retrieved")
        except Exception as exc:
            return self._fail(f"Failed calling '{module_name}.{attr_name}'.", exc, traceback.format_exc())