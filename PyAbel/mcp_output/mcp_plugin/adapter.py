import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for PyAbel repository source import.

    This adapter attempts to import PyAbel modules directly from local source code
    (under injected `source_path`) and exposes stable wrapper methods for core
    transform and tools functionality with unified status dictionaries.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Any = None, message: str = "ok", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data is not None:
            payload["data"] = data
        if extra:
            payload.update(extra)
        return payload

    def _err(self, message: str, exception: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if exception is not None:
            payload["error_type"] = type(exception).__name__
            payload["error"] = str(exception)
        return payload

    def _load_one(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[key] = None
            self._import_errors[key] = f"{module_path}: {exc}"

    def _load_modules(self) -> None:
        module_map = {
            "abel": "abel",
            "transform": "abel.transform",
            "basex": "abel.basex",
            "dasch": "abel.dasch",
            "daun": "abel.daun",
            "direct": "abel.direct",
            "hansenlaw": "abel.hansenlaw",
            "linbasex": "abel.linbasex",
            "nestorolsen": "abel.nestorolsen",
            "onion_bordas": "abel.onion_bordas",
            "rbasex": "abel.rbasex",
            "benchmark": "abel.benchmark",
            "tools_analytical": "abel.tools.analytical",
            "tools_center": "abel.tools.center",
            "tools_circularize": "abel.tools.circularize",
            "tools_io": "abel.tools.io",
            "tools_math": "abel.tools.math",
            "tools_polar": "abel.tools.polar",
            "tools_polynomial": "abel.tools.polynomial",
            "tools_symmetry": "abel.tools.symmetry",
            "tools_transform_pairs": "abel.tools.transform_pairs",
            "tools_vmi": "abel.tools.vmi",
        }
        for k, v in module_map.items():
            self._load_one(k, v)

    def _get_module(self, key: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        mod = self._modules.get(key)
        if mod is None:
            err = self._import_errors.get(key, "Module is unavailable.")
            return None, self._err(
                message=f"Import unavailable for module key '{key}'.",
                hint=f"Ensure source files are present under source_path and dependencies are installed. Details: {err}",
            )
        return mod, None

    def get_status(self) -> Dict[str, Any]:
        return self._ok(
            data={
                "loaded_modules": sorted([k for k, v in self._modules.items() if v is not None]),
                "failed_modules": self._import_errors,
                "source_path": source_path,
            }
        )

    # -------------------------------------------------------------------------
    # Core Transform Interface
    # -------------------------------------------------------------------------
    def transform(self, image: Any, method: str = "hansenlaw", direction: str = "inverse", **kwargs: Any) -> Dict[str, Any]:
        """
        Run abel.transform.Transform and return transformed image payload.

        Parameters:
            image: 2D array-like image.
            method: Transform method name (e.g., 'hansenlaw', 'basex', 'rbasex').
            direction: 'inverse' or 'forward'.
            **kwargs: Additional Transform kwargs from PyAbel.

        Returns:
            Unified status dictionary with transform result in `data`.
        """
        mod, err = self._get_module("transform")
        if err:
            return err
        try:
            obj = mod.Transform(image, method=method, direction=direction, **kwargs)
            out = {
                "transform": getattr(obj, "transform", None),
                "method": method,
                "direction": direction,
            }
            return self._ok(data=out, message="Transform executed.")
        except Exception as exc:
            return self._err("Failed to execute transform.", exception=exc, hint="Validate image shape and method-specific parameters.")

    # -------------------------------------------------------------------------
    # Method-specific wrappers
    # -------------------------------------------------------------------------
    def call_basex(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("basex")
        if err:
            return err
        try:
            fn = getattr(mod, "basex_transform", None)
            if fn is None:
                return self._err("Function 'basex_transform' not found in abel.basex.", hint="Check repository version compatibility.")
            return self._ok(data=fn(*args, **kwargs), message="BASEX function executed.")
        except Exception as exc:
            return self._err("BASEX execution failed.", exception=exc)

    def call_dasch(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("dasch")
        if err:
            return err
        try:
            for name in ("two_point_transform", "three_point_transform", "onion_peeling_transform"):
                if hasattr(mod, name):
                    pass
            return self._ok(data={"available": [n for n in dir(mod) if n.endswith("_transform")]}, message="Dasch module inspected.")
        except Exception as exc:
            return self._err("Dasch execution failed.", exception=exc)

    def call_daun(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("daun")
        if err:
            return err
        try:
            fn = getattr(mod, "daun_transform", None)
            if fn is None:
                return self._err("Function 'daun_transform' not found in abel.daun.", hint="Inspect available callables via module listing.")
            return self._ok(data=fn(*args, **kwargs), message="DAUN function executed.")
        except Exception as exc:
            return self._err("DAUN execution failed.", exception=exc)

    def call_direct(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("direct")
        if err:
            return err
        try:
            fn = getattr(mod, "direct_transform", None)
            if fn is None:
                return self._err("Function 'direct_transform' not found in abel.direct.")
            return self._ok(data=fn(*args, **kwargs), message="Direct transform executed.")
        except Exception as exc:
            return self._err("Direct transform failed.", exception=exc)

    def call_hansenlaw(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("hansenlaw")
        if err:
            return err
        try:
            fn = getattr(mod, "hansenlaw_transform", None)
            if fn is None:
                return self._err("Function 'hansenlaw_transform' not found in abel.hansenlaw.")
            return self._ok(data=fn(*args, **kwargs), message="Hansen-Law transform executed.")
        except Exception as exc:
            return self._err("Hansen-Law transform failed.", exception=exc)

    def call_linbasex(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("linbasex")
        if err:
            return err
        try:
            fn = getattr(mod, "linbasex_transform", None)
            if fn is None:
                return self._err("Function 'linbasex_transform' not found in abel.linbasex.")
            return self._ok(data=fn(*args, **kwargs), message="LinBASEX transform executed.")
        except Exception as exc:
            return self._err("LinBASEX transform failed.", exception=exc)

    def call_nestorolsen(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("nestorolsen")
        if err:
            return err
        try:
            fn = getattr(mod, "nestor_olsen_transform", None)
            if fn is None:
                return self._err("Function 'nestor_olsen_transform' not found in abel.nestorolsen.")
            return self._ok(data=fn(*args, **kwargs), message="Nestor-Olsen transform executed.")
        except Exception as exc:
            return self._err("Nestor-Olsen transform failed.", exception=exc)

    def call_onion_bordas(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("onion_bordas")
        if err:
            return err
        try:
            fn = getattr(mod, "onion_bordas_transform", None)
            if fn is None:
                return self._err("Function 'onion_bordas_transform' not found in abel.onion_bordas.")
            return self._ok(data=fn(*args, **kwargs), message="Onion-Bordas transform executed.")
        except Exception as exc:
            return self._err("Onion-Bordas transform failed.", exception=exc)

    def call_rbasex(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module("rbasex")
        if err:
            return err
        try:
            fn = getattr(mod, "rbasex_transform", None)
            if fn is None:
                return self._err("Function 'rbasex_transform' not found in abel.rbasex.")
            return self._ok(data=fn(*args, **kwargs), message="rBASEX transform executed.")
        except Exception as exc:
            return self._err("rBASEX transform failed.", exception=exc)

    # -------------------------------------------------------------------------
    # Tools wrappers
    # -------------------------------------------------------------------------
    def tools_module_api(self, module_key: str) -> Dict[str, Any]:
        mod, err = self._get_module(module_key)
        if err:
            return err
        try:
            public = [n for n in dir(mod) if not n.startswith("_")]
            return self._ok(data={"module": module_key, "public": public}, message="Module API listed.")
        except Exception as exc:
            return self._err("Failed to list module API.", exception=exc)

    def call_tools_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module(module_key)
        if err:
            return err
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' not found or not callable in module '{module_key}'.",
                    hint="Use tools_module_api() to inspect available functions.",
                )
            return self._ok(data=fn(*args, **kwargs), message=f"{module_key}.{function_name} executed.")
        except Exception as exc:
            return self._err("Tool function execution failed.", exception=exc)

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    def fallback_info(self) -> Dict[str, Any]:
        return self._ok(
            data={
                "mode": self.mode,
                "fallback": "blackbox",
                "guidance": "If imports fail, verify source_path and install required dependencies: numpy, scipy. Optional: matplotlib, setuptools.",
                "trace": traceback.format_exc(),
            },
            message="Fallback guidance provided.",
        )