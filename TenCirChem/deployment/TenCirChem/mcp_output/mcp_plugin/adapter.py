import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for TenCirChem.

    This adapter prefers direct Python imports from the local repository source tree.
    If imports fail, it degrades gracefully to fallback mode while returning unified
    status dictionaries for all operations.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode.

        Attributes:
            mode: Adapter execution mode. Default is "import".
            import_ok: True when core imports succeed.
            modules: Loaded module registry keyed by full module path.
            import_errors: List of import failures.
        """
        self.mode = "import"
        self.import_ok = False
        self.modules: Dict[str, Any] = {}
        self.import_errors: List[Dict[str, str]] = []
        self._load_modules()

    def _ok(self, **data: Any) -> Dict[str, Any]:
        return {"status": "ok", **data}

    def _error(self, message: str, **data: Any) -> Dict[str, Any]:
        return {"status": "error", "message": message, **data}

    def _fallback(self, action: str, guidance: str) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "mode": self.mode,
            "action": action,
            "message": "Import mode is unavailable. Use fallback execution.",
            "guidance": guidance,
            "import_errors": self.import_errors,
        }

    def _load_modules(self) -> None:
        module_names = [
            "tencirchem",
            "tencirchem.applications",
            "tencirchem.applications.vbe_lib",
            "tencirchem.constants",
            "tencirchem.dynamic",
            "tencirchem.dynamic.model",
            "tencirchem.dynamic.model.pyrazine",
            "tencirchem.dynamic.model.sbm",
            "tencirchem.dynamic.time_derivative",
            "tencirchem.dynamic.time_evolution",
            "tencirchem.dynamic.transform",
            "tencirchem.molecule",
            "tencirchem.static",
            "tencirchem.static.ci_utils",
            "tencirchem.static.engine_hea",
            "tencirchem.static.engine_ucc",
            "tencirchem.static.evolve_civector",
            "tencirchem.static.evolve_pyscf",
            "tencirchem.static.evolve_statevector",
            "tencirchem.static.evolve_tensornetwork",
            "tencirchem.static.hamiltonian",
            "tencirchem.static.hea",
            "tencirchem.static.kupccgsd",
            "tencirchem.static.puccd",
            "tencirchem.static.ucc",
            "tencirchem.static.uccsd",
            "tencirchem.utils",
            "tencirchem.utils.backend",
            "tencirchem.utils.circuit",
            "tencirchem.utils.misc",
            "tencirchem.utils.optimizer",
        ]
        loaded = 0
        for name in module_names:
            try:
                self.modules[name] = importlib.import_module(name)
                loaded += 1
            except Exception as e:
                self.import_errors.append({"module": name, "error": str(e)})
        self.import_ok = loaded > 0
        if not self.import_ok:
            self.mode = "blackbox"

    # -------------------------------------------------------------------------
    # Introspection utilities
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._ok(
            mode=self.mode,
            import_ok=self.import_ok,
            loaded_modules=sorted(list(self.modules.keys())),
            import_errors=self.import_errors,
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List all managed modules currently loaded by the adapter.
        """
        if not self.import_ok:
            return self._fallback(
                "list_modules",
                "Check local source path and dependency installation, then retry.",
            )
        return self._ok(modules=sorted(self.modules.keys()))

    def list_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        List public symbols from a loaded module.

        Args:
            module_name: Full module path, e.g. 'tencirchem.static.ucc'.

        Returns:
            Unified status dictionary with symbol metadata.
        """
        if not self.import_ok:
            return self._fallback(
                "list_symbols",
                "Enable import mode by fixing missing dependencies and source path.",
            )
        mod = self.modules.get(module_name)
        if mod is None:
            return self._error(
                "Module is not loaded.",
                module_name=module_name,
                available_modules=sorted(self.modules.keys()),
            )
        try:
            symbols = []
            for name, obj in inspect.getmembers(mod):
                if name.startswith("_"):
                    continue
                kind = (
                    "class"
                    if inspect.isclass(obj)
                    else "function"
                    if inspect.isfunction(obj)
                    else "object"
                )
                symbols.append({"name": name, "kind": kind})
            return self._ok(module_name=module_name, symbols=symbols)
        except Exception as e:
            return self._error(
                "Failed to inspect module symbols.",
                module_name=module_name,
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Generic class/function execution helpers
    # -------------------------------------------------------------------------
    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a managed module.

        Args:
            module_name: Full module path.
            class_name: Target class name.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary with instance and metadata.
        """
        if not self.import_ok:
            return self._fallback(
                "create_instance",
                "Install required dependencies (numpy, scipy, tensorcircuit, pyscf, openfermion) and retry.",
            )
        mod = self.modules.get(module_name)
        if mod is None:
            return self._error("Target module is not loaded.", module_name=module_name)
        try:
            cls = getattr(mod, class_name, None)
            if cls is None or not inspect.isclass(cls):
                return self._error(
                    "Class not found in target module.",
                    module_name=module_name,
                    class_name=class_name,
                )
            instance = cls(*args, **kwargs)
            return self._ok(
                module_name=module_name,
                class_name=class_name,
                instance=instance,
            )
        except Exception as e:
            return self._error(
                "Failed to create class instance.",
                module_name=module_name,
                class_name=class_name,
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    def call_function(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from a managed module.

        Args:
            module_name: Full module path.
            function_name: Target function name.
            *args: Positional function arguments.
            **kwargs: Keyword function arguments.

        Returns:
            Unified status dictionary with call result.
        """
        if not self.import_ok:
            return self._fallback(
                "call_function",
                "Verify repository source sync and Python dependency compatibility.",
            )
        mod = self.modules.get(module_name)
        if mod is None:
            return self._error("Target module is not loaded.", module_name=module_name)
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._error(
                    "Function not found or not callable in target module.",
                    module_name=module_name,
                    function_name=function_name,
                )
            result = fn(*args, **kwargs)
            return self._ok(
                module_name=module_name,
                function_name=function_name,
                result=result,
            )
        except Exception as e:
            return self._error(
                "Function call failed.",
                module_name=module_name,
                function_name=function_name,
                exception=str(e),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # High-level TenCirChem module wrappers
    # -------------------------------------------------------------------------
    def module_tencirchem(self) -> Dict[str, Any]:
        return self._module_info("tencirchem")

    def module_applications(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.applications")

    def module_vbe_lib(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.applications.vbe_lib")

    def module_constants(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.constants")

    def module_dynamic(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic")

    def module_dynamic_model(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.model")

    def module_dynamic_model_pyrazine(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.model.pyrazine")

    def module_dynamic_model_sbm(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.model.sbm")

    def module_time_derivative(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.time_derivative")

    def module_time_evolution(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.time_evolution")

    def module_transform(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.dynamic.transform")

    def module_molecule(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.molecule")

    def module_static(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static")

    def module_ci_utils(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.ci_utils")

    def module_engine_hea(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.engine_hea")

    def module_engine_ucc(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.engine_ucc")

    def module_evolve_civector(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.evolve_civector")

    def module_evolve_pyscf(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.evolve_pyscf")

    def module_evolve_statevector(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.evolve_statevector")

    def module_evolve_tensornetwork(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.evolve_tensornetwork")

    def module_hamiltonian(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.hamiltonian")

    def module_hea(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.hea")

    def module_kupccgsd(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.kupccgsd")

    def module_puccd(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.puccd")

    def module_ucc(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.ucc")

    def module_uccsd(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.static.uccsd")

    def module_utils(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.utils")

    def module_backend(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.utils.backend")

    def module_circuit(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.utils.circuit")

    def module_misc(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.utils.misc")

    def module_optimizer(self) -> Dict[str, Any]:
        return self._module_info("tencirchem.utils.optimizer")

    def _module_info(self, module_name: str) -> Dict[str, Any]:
        if not self.import_ok:
            return self._fallback(
                "module_info",
                "Ensure local repository source exists and dependencies are installed.",
            )
        mod = self.modules.get(module_name)
        if mod is None:
            return self._error("Module is not loaded.", module_name=module_name)
        try:
            doc = inspect.getdoc(mod)
            members = [n for n in dir(mod) if not n.startswith("_")]
            return self._ok(module_name=module_name, doc=doc, members=members)
        except Exception as e:
            return self._error(
                "Failed to retrieve module metadata.",
                module_name=module_name,
                exception=str(e),
            )