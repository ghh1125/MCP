import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the qutip repository.

    Design goals:
    - Primary mode: import from repository source tree.
    - Fallback mode: graceful blackbox response when import/use is unavailable.
    - Unified return shape for all methods.
    - Modular organization for maintainability.

    Unified response format:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "blackbox",
        "action": "<method_name>",
        "data": <any>,
        "error": <str or None>,
        "guidance": <str or None>
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Core Utilities
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: List[str] = []
        self._init_imports()

    def _result(
        self,
        action: str,
        status: str,
        data: Any = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "action": action,
            "data": data,
            "error": error,
            "guidance": guidance,
        }

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._import_errors.append(f"{module_path}: {exc}")
            return None

    def _init_imports(self) -> None:
        candidates = [
            "qutip",
            "qutip.core",
            "qutip.core.operators",
            "qutip.core.states",
            "qutip.core.tensor",
            "qutip.core.expect",
            "qutip.core.gates",
            "qutip.solver.mesolve",
            "qutip.solver.sesolve",
            "qutip.solver.mcsolve",
            "qutip.solver.steadystate",
            "qutip.visualization",
            "qutip.wigner",
            "qutip.bloch",
            "qutip.random_objects",
            "qutip.entropy",
            "qutip.measurement",
            "qutip.tomography",
            "qutip.utilities",
        ]
        success_count = 0
        for mod in candidates:
            if self._safe_import(mod) is not None:
                success_count += 1

        if success_count == 0:
            self.mode = "blackbox"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._result(
            action="health",
            status="success" if self.mode == "import" else "fallback",
            data={
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
            },
            guidance=(
                None
                if self.mode == "import"
                else "Repository import failed. Verify that source/qutip exists and dependencies are installed: numpy, scipy, packaging."
            ),
        )

    # -------------------------------------------------------------------------
    # Module Management
    # -------------------------------------------------------------------------
    def get_module(self, module_path: str) -> Dict[str, Any]:
        """
        Dynamically retrieve or import a module from qutip source.
        """
        try:
            if module_path in self._modules:
                return self._result("get_module", "success", data={"module_path": module_path})
            mod = self._safe_import(module_path)
            if mod is None:
                return self._result(
                    "get_module",
                    "error",
                    error=f"Failed to import module: {module_path}",
                    guidance="Confirm module path and ensure repository source is available on sys.path.",
                )
            return self._result("get_module", "success", data={"module_path": module_path})
        except Exception as exc:
            return self._result(
                "get_module",
                "error",
                error=str(exc),
                guidance="Check module path and runtime environment.",
            )

    # -------------------------------------------------------------------------
    # Core Constructors and Functions
    # -------------------------------------------------------------------------
    def create_qobj(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a qutip.Qobj instance.

        Parameters:
        - *args, **kwargs: forwarded to qutip.Qobj constructor.
        """
        try:
            if self.mode != "import":
                return self._result(
                    "create_qobj",
                    "fallback",
                    error="Import mode unavailable.",
                    guidance="Install required dependencies and ensure qutip source is present.",
                )
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            obj = qutip_mod.Qobj(*args, **kwargs)
            return self._result("create_qobj", "success", data={"repr": repr(obj)})
        except Exception as exc:
            return self._result("create_qobj", "error", error=str(exc), guidance=traceback.format_exc())

    def call_basis(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            out = qutip_mod.basis(*args, **kwargs)
            return self._result("call_basis", "success", data={"repr": repr(out)})
        except Exception as exc:
            return self._result("call_basis", "error", error=str(exc), guidance="Validate dimensions and basis index.")

    def call_tensor(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            out = qutip_mod.tensor(*args, **kwargs)
            return self._result("call_tensor", "success", data={"repr": repr(out)})
        except Exception as exc:
            return self._result("call_tensor", "error", error=str(exc), guidance="Pass valid Qobj operands.")

    def call_expect(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            out = qutip_mod.expect(*args, **kwargs)
            return self._result("call_expect", "success", data={"value": out})
        except Exception as exc:
            return self._result("call_expect", "error", error=str(exc), guidance="Check operator/state compatibility.")

    # -------------------------------------------------------------------------
    # Solver Wrappers
    # -------------------------------------------------------------------------
    def call_mesolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call qutip.mesolve with pass-through arguments.
        """
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            res = qutip_mod.mesolve(*args, **kwargs)
            return self._result("call_mesolve", "success", data={"result_type": type(res).__name__})
        except Exception as exc:
            return self._result("call_mesolve", "error", error=str(exc), guidance="Validate Hamiltonian, state, and time list inputs.")

    def call_sesolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            res = qutip_mod.sesolve(*args, **kwargs)
            return self._result("call_sesolve", "success", data={"result_type": type(res).__name__})
        except Exception as exc:
            return self._result("call_sesolve", "error", error=str(exc), guidance="Use valid Schrödinger equation inputs.")

    def call_mcsolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            res = qutip_mod.mcsolve(*args, **kwargs)
            return self._result("call_mcsolve", "success", data={"result_type": type(res).__name__})
        except Exception as exc:
            return self._result("call_mcsolve", "error", error=str(exc), guidance="Check collapse operators and trajectory settings.")

    def call_steadystate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            res = qutip_mod.steadystate(*args, **kwargs)
            return self._result("call_steadystate", "success", data={"repr": repr(res)})
        except Exception as exc:
            return self._result("call_steadystate", "error", error=str(exc), guidance="Verify Liouvillian/Hamiltonian input.")

    # -------------------------------------------------------------------------
    # Visualization / Analysis Wrappers
    # -------------------------------------------------------------------------
    def create_bloch(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create qutip.Bloch visualization object.
        """
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            bloch_obj = qutip_mod.Bloch(*args, **kwargs)
            return self._result("create_bloch", "success", data={"repr": repr(bloch_obj)})
        except Exception as exc:
            return self._result("create_bloch", "error", error=str(exc), guidance="Install matplotlib for Bloch visualization.")

    def call_wigner(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            qutip_mod = self._modules.get("qutip") or importlib.import_module("qutip")
            out = qutip_mod.wigner(*args, **kwargs)
            return self._result("call_wigner", "success", data={"type": type(out).__name__})
        except Exception as exc:
            return self._result("call_wigner", "error", error=str(exc), guidance="Provide valid state and phase-space grids.")