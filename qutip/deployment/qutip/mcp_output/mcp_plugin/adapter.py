import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for the QuTiP source tree.

    This adapter prefers direct import from the local `source` directory and
    gracefully falls back to a non-import mode when unavailable.
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._errors: List[str] = []
        self.modules: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        self.classes: Dict[str, Any] = {}
        self._initialize()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Any] = None,
        hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = {"status": status, "message": message}
        if data is not None:
            result["data"] = data
        if hint:
            result["hint"] = hint
        if self._errors:
            result["errors"] = self._errors[-5:]
        return result

    def _initialize(self) -> None:
        target_modules = [
            "qutip",
            "qutip.about",
            "qutip.settings",
            "qutip.core.operators",
            "qutip.core.states",
            "qutip.core.tensor",
            "qutip.core.expect",
            "qutip.solver.mesolve",
            "qutip.solver.sesolve",
            "qutip.solver.mcsolve",
            "qutip.solver.steadystate",
            "qutip.wigner",
            "qutip.visualization",
            "qutip.measurement",
            "qutip.entropy",
            "qutip.random_objects",
            "qutip.core.qobj",
        ]

        for mod_name in target_modules:
            try:
                self.modules[mod_name] = importlib.import_module(mod_name)
            except Exception as exc:
                self._errors.append(f"Failed to import {mod_name}: {exc}")

        try:
            qutip = self.modules.get("qutip")
            if qutip is not None:
                # Common public API functions/classes in qutip.__init__.
                for name in [
                    "Qobj",
                    "basis",
                    "coherent",
                    "fock",
                    "destroy",
                    "create",
                    "qeye",
                    "sigmax",
                    "sigmay",
                    "sigmaz",
                    "tensor",
                    "expect",
                    "mesolve",
                    "sesolve",
                    "mcsolve",
                    "steadystate",
                    "wigner",
                    "rand_ket",
                    "rand_dm",
                    "entropy_vn",
                    "fidelity",
                ]:
                    if hasattr(qutip, name):
                        obj = getattr(qutip, name)
                        if isinstance(obj, type):
                            self.classes[name] = obj
                        else:
                            self.functions[name] = obj
        except Exception as exc:
            self._errors.append(f"Failed to map QuTiP API symbols: {exc}")

        self._loaded = bool(self.modules.get("qutip")) and len(self._errors) < len(target_modules)
        if not self._loaded:
            self.mode = "fallback"

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Report adapter health and import status.

        Returns:
            dict: Unified status payload.
        """
        if self._loaded:
            return self._result(
                "ok",
                "Adapter initialized in import mode.",
                data={
                    "mode": self.mode,
                    "loaded_modules": sorted(self.modules.keys()),
                    "available_functions": sorted(self.functions.keys()),
                    "available_classes": sorted(self.classes.keys()),
                },
            )
        return self._result(
            "degraded",
            "Adapter is running in fallback mode due to import failures.",
            data={"mode": self.mode},
            hint="Ensure local source tree exists and includes the qutip package under the source directory.",
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _require_symbol(self, name: str, symbol_type: str = "function") -> Dict[str, Any]:
        if not self._loaded:
            return self._result(
                "error",
                "Import mode is unavailable.",
                hint="Fix imports first: verify source path and repository contents.",
            )
        table = self.functions if symbol_type == "function" else self.classes
        if name not in table:
            return self._result(
                "error",
                f"Requested {symbol_type} '{name}' is not available.",
                hint=f"Check compatibility of the local qutip source with symbol '{name}'.",
            )
        return {"status": "ok", "symbol": table[name]}

    def _invoke_function(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        sym = self._require_symbol(name, "function")
        if sym.get("status") != "ok":
            return sym
        try:
            result = sym["symbol"](*args, **kwargs)
            return self._result("ok", f"Function '{name}' executed successfully.", data=result)
        except Exception as exc:
            return self._result(
                "error",
                f"Function '{name}' failed: {exc}",
                data={"traceback": traceback.format_exc(limit=3)},
                hint="Validate function arguments and object dimensions/types.",
            )

    def _instantiate_class(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        sym = self._require_symbol(name, "class")
        if sym.get("status") != "ok":
            return sym
        try:
            instance = sym["symbol"](*args, **kwargs)
            return self._result("ok", f"Class '{name}' instantiated successfully.", data=instance)
        except Exception as exc:
            return self._result(
                "error",
                f"Class '{name}' instantiation failed: {exc}",
                data={"traceback": traceback.format_exc(limit=3)},
                hint="Verify constructor arguments and compatibility with current QuTiP version.",
            )

    # -------------------------------------------------------------------------
    # Class instance methods
    # -------------------------------------------------------------------------
    def create_qobj_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a qutip.Qobj instance.

        Parameters:
            *args: Positional arguments forwarded to Qobj constructor.
            **kwargs: Keyword arguments forwarded to Qobj constructor.

        Returns:
            dict: Unified status payload containing the instance on success.
        """
        return self._instantiate_class("Qobj", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function call methods (mapped from identified API symbols)
    # -------------------------------------------------------------------------
    def call_basis(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("basis", *args, **kwargs)

    def call_coherent(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("coherent", *args, **kwargs)

    def call_fock(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("fock", *args, **kwargs)

    def call_destroy(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("destroy", *args, **kwargs)

    def call_create(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("create", *args, **kwargs)

    def call_qeye(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("qeye", *args, **kwargs)

    def call_sigmax(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("sigmax", *args, **kwargs)

    def call_sigmay(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("sigmay", *args, **kwargs)

    def call_sigmaz(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("sigmaz", *args, **kwargs)

    def call_tensor(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("tensor", *args, **kwargs)

    def call_expect(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("expect", *args, **kwargs)

    def call_mesolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("mesolve", *args, **kwargs)

    def call_sesolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("sesolve", *args, **kwargs)

    def call_mcsolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("mcsolve", *args, **kwargs)

    def call_steadystate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("steadystate", *args, **kwargs)

    def call_wigner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("wigner", *args, **kwargs)

    def call_rand_ket(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("rand_ket", *args, **kwargs)

    def call_rand_dm(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("rand_dm", *args, **kwargs)

    def call_entropy_vn(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("entropy_vn", *args, **kwargs)

    def call_fidelity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._invoke_function("fidelity", *args, **kwargs)