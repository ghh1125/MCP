import os
import sys
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for SciPy repository source.

    This adapter is designed to import and call SciPy APIs from the local
    repository source tree (mounted under `source/`) rather than from an
    externally installed package.

    Design goals:
    - Import-mode first, graceful fallback when imports fail.
    - Unified response envelope for every public method.
    - Clear module-level wrappers for commonly used SciPy subpackages.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._init_modules()

    # -------------------------------------------------------------------------
    # Core helpers
    # -------------------------------------------------------------------------
    def _result(
        self,
        status: str,
        data: Optional[Any] = None,
        message: str = "",
        error: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "data": data,
            "message": message,
            "error": error,
            "meta": meta or {},
        }

    def _safe_import(self, module_path: str) -> None:
        try:
            self._modules[module_path] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[module_path] = None
            self._errors[module_path] = (
                f"Failed to import '{module_path}'. Ensure source tree is complete and build "
                f"artifacts are available for compiled extensions. Details: {exc}"
            )

    def _init_modules(self) -> None:
        module_paths = [
            "scipy",
            "scipy.cluster",
            "scipy.constants",
            "scipy.datasets",
            "scipy.differentiate",
            "scipy.fft",
            "scipy.fftpack",
            "scipy.integrate",
            "scipy.interpolate",
            "scipy.io",
            "scipy.linalg",
            "scipy.misc",
            "scipy.ndimage",
            "scipy.odr",
            "scipy.optimize",
            "scipy.signal",
            "scipy.sparse",
            "scipy.spatial",
            "scipy.special",
            "scipy.stats",
        ]
        for path in module_paths:
            self._safe_import(path)

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter/module import health.

        Returns:
            dict: Unified response with imported modules and import failures.
        """
        imported = [k for k, v in self._modules.items() if v is not None]
        failed = {k: v for k, v in self._errors.items()}
        status = "success" if not failed else "partial_success"
        msg = (
            "All configured modules imported successfully."
            if not failed
            else "Some modules failed to import. Review error details and ensure compiled SciPy extensions are built."
        )
        return self._result(
            status=status,
            data={"imported": imported, "failed": list(failed.keys())},
            message=msg,
            meta={"errors": failed, "mode": self.mode, "source_path": source_path},
        )

    def _call(self, module_path: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._modules.get(module_path)
        if mod is None:
            err = self._errors.get(
                module_path,
                f"Module '{module_path}' is unavailable. Run health_check() and verify local source/build setup.",
            )
            return self._result("fallback", None, "Import mode unavailable for requested module.", err)

        try:
            func = getattr(mod, func_name)
        except AttributeError:
            return self._result(
                "error",
                None,
                "Requested function is not available in module.",
                f"Function '{func_name}' not found in '{module_path}'. Verify SciPy version and API name.",
            )

        try:
            out = func(*args, **kwargs)
            return self._result("success", out, f"{module_path}.{func_name} executed successfully.")
        except Exception as exc:
            return self._result(
                "error",
                None,
                "Function execution failed.",
                f"Execution error in '{module_path}.{func_name}': {exc}",
            )

    # -------------------------------------------------------------------------
    # Generic invocation
    # -------------------------------------------------------------------------
    def call(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dynamic caller for any imported module function.

        Args:
            module_path: Fully qualified module path, e.g. 'scipy.optimize'.
            function_name: Function symbol name to call from the module.
            *args: Positional arguments forwarded to the target function.
            **kwargs: Keyword arguments forwarded to the target function.

        Returns:
            dict: Unified status dictionary with data/error fields.
        """
        return self._call(module_path, function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # SciPy top-level helpers
    # -------------------------------------------------------------------------
    def scipy_show_config(self) -> Dict[str, Any]:
        return self._call("scipy", "show_config")

    # -------------------------------------------------------------------------
    # Submodule convenience methods (function-focused wrappers)
    # -------------------------------------------------------------------------
    def fft_fft(self, x: Any, n: Optional[int] = None, axis: int = -1, norm: Optional[str] = None) -> Dict[str, Any]:
        return self._call("scipy.fft", "fft", x, n=n, axis=axis, norm=norm)

    def integrate_quad(self, func: Any, a: float, b: float, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.integrate", "quad", func, a, b, **kwargs)

    def interpolate_interp1d(self, x: Any, y: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.interpolate", "interp1d", x, y, **kwargs)

    def linalg_solve(self, a: Any, b: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.linalg", "solve", a, b, **kwargs)

    def optimize_minimize(self, fun: Any, x0: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.optimize", "minimize", fun, x0, **kwargs)

    def signal_find_peaks(self, x: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.signal", "find_peaks", x, **kwargs)

    def sparse_csr_matrix(self, arg1: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call("scipy.sparse", "csr_matrix", arg1, **kwargs)

    def spatial_distance_cdist(self, xa: Any, xb: Any, metric: str = "euclidean", **kwargs: Any) -> Dict[str, Any]:
        mod = "scipy.spatial"
        if self._modules.get(mod) is None:
            return self._result(
                "fallback",
                None,
                "Import mode unavailable for spatial module.",
                self._errors.get(mod, "Module not available."),
            )
        try:
            distance = getattr(self._modules[mod], "distance")
            out = distance.cdist(xa, xb, metric=metric, **kwargs)
            return self._result("success", out, "scipy.spatial.distance.cdist executed successfully.")
        except Exception as exc:
            return self._result("error", None, "Function execution failed.", f"cdist error: {exc}")

    def special_erf(self, x: Any) -> Dict[str, Any]:
        return self._call("scipy.special", "erf", x)

    def stats_norm_cdf(self, x: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = "scipy.stats"
        if self._modules.get(mod) is None:
            return self._result(
                "fallback",
                None,
                "Import mode unavailable for stats module.",
                self._errors.get(mod, "Module not available."),
            )
        try:
            norm = getattr(self._modules[mod], "norm")
            out = norm.cdf(x, **kwargs)
            return self._result("success", out, "scipy.stats.norm.cdf executed successfully.")
        except Exception as exc:
            return self._result("error", None, "Function execution failed.", f"norm.cdf error: {exc}")