import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for facebookresearch/esm repository.

    This adapter prioritizes direct Python imports from the local source tree and
    provides CLI fallbacks for key script entry points when imports are unavailable.
    All public methods return a unified dictionary format with a mandatory `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._init_result = self._load_core_modules()

    # -------------------------------------------------------------------------
    # Internal Utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc(limit=3)
        return payload

    def _load_module(self, name: str) -> Tuple[bool, Any]:
        try:
            mod = importlib.import_module(name)
            self._modules[name] = mod
            return True, mod
        except Exception:
            return False, None

    def _load_core_modules(self) -> Dict[str, Any]:
        targets = [
            "esm",
            "esm.pretrained",
            "esm.data",
            "esm.model.esm1",
            "esm.model.esm2",
            "esm.model.msa_transformer",
            "esm.inverse_folding.util",
            "esm.inverse_folding.multichain_util",
            "esm.esmfold.v1.pretrained",
            "scripts.extract",
            "scripts.fold",
        ]
        loaded, failed = [], []
        for t in targets:
            ok, _ = self._load_module(t)
            (loaded if ok else failed).append(t)
        return self._ok(
            {
                "loaded_modules": loaded,
                "failed_modules": failed,
                "import_feasibility": 0.87,
                "intrusiveness_risk": "low",
                "complexity": "medium",
            },
            message="Adapter initialized with import mode and module preloading.",
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and report loaded module state.

        Returns:
            Dict[str, Any]: Unified status dictionary with loaded/failed module details.
        """
        return self._init_result

    def list_available_symbols(self, module_name: str) -> Dict[str, Any]:
        """
        List public symbols in an imported module.

        Args:
            module_name: Full module path (e.g., 'esm.pretrained').

        Returns:
            Dict[str, Any]: status + module symbol metadata.
        """
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)
            symbols = [n for n in dir(mod) if not n.startswith("_")]
            return self._ok({"module": module_name, "symbols": symbols})
        except Exception as e:
            return self._error(
                f"Failed to list symbols for module '{module_name}'.",
                hint="Verify module name and ensure repository dependencies are installed.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # ESM Core: model and pretrained
    # -------------------------------------------------------------------------
    def load_pretrained_model(self, loader_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Load a pretrained model using esm.pretrained dynamic loader function.

        Args:
            loader_name: Function name inside esm.pretrained (e.g., 'esm2_t33_650M_UR50D').
            *args: Positional args passed to loader.
            **kwargs: Keyword args passed to loader.

        Returns:
            Dict[str, Any]: status + model and alphabet on success.
        """
        try:
            mod = self._modules.get("esm.pretrained") or importlib.import_module("esm.pretrained")
            fn = getattr(mod, loader_name, None)
            if fn is None or not callable(fn):
                return self._error(
                    f"Pretrained loader '{loader_name}' was not found in esm.pretrained.",
                    hint="Use list_available_symbols('esm.pretrained') to find valid loader names.",
                )
            model, alphabet = fn(*args, **kwargs)
            return self._ok({"loader": loader_name, "model": model, "alphabet": alphabet})
        except Exception as e:
            return self._error(
                f"Failed to load pretrained model via '{loader_name}'.",
                hint="Check CUDA/torch environment and internet/cache availability if weights need download.",
                error=e,
            )

    def build_batch_converter(self, alphabet: Any, truncation_seq_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Create ESM batch converter from alphabet instance.

        Args:
            alphabet: Alphabet instance returned by pretrained loader.
            truncation_seq_length: Optional max sequence length.

        Returns:
            Dict[str, Any]: status + converter callable.
        """
        try:
            if not hasattr(alphabet, "get_batch_converter"):
                return self._error(
                    "Provided alphabet object does not support get_batch_converter().",
                    hint="Use alphabet returned by esm.pretrained loaders.",
                )
            converter = alphabet.get_batch_converter(truncation_seq_length=truncation_seq_length)
            return self._ok({"converter": converter})
        except Exception as e:
            return self._error(
                "Failed to create batch converter.",
                hint="Ensure the alphabet object is valid and compatible with installed esm version.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # Inverse Folding Utilities
    # -------------------------------------------------------------------------
    def call_inverse_folding_util(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from esm.inverse_folding.util.

        Args:
            function_name: Name of the target function in esm.inverse_folding.util.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            Dict[str, Any]: status + function call result.
        """
        try:
            mod = self._modules.get("esm.inverse_folding.util") or importlib.import_module("esm.inverse_folding.util")
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._error(
                    f"Function '{function_name}' not found in esm.inverse_folding.util.",
                    hint="Inspect available symbols via list_available_symbols('esm.inverse_folding.util').",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module": "esm.inverse_folding.util", "function": function_name, "result": result})
        except Exception as e:
            return self._error(
                f"Failed to call inverse folding util function '{function_name}'.",
                hint="Validate input tensor/structure types expected by the function.",
                error=e,
            )

    def call_multichain_util(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a function from esm.inverse_folding.multichain_util.

        Args:
            function_name: Name of target function.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            Dict[str, Any]: status + function result.
        """
        try:
            mod = self._modules.get("esm.inverse_folding.multichain_util") or importlib.import_module(
                "esm.inverse_folding.multichain_util"
            )
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._error(
                    f"Function '{function_name}' not found in esm.inverse_folding.multichain_util.",
                    hint="Use list_available_symbols('esm.inverse_folding.multichain_util').",
                )
            result = fn(*args, **kwargs)
            return self._ok({"module": "esm.inverse_folding.multichain_util", "function": function_name, "result": result})
        except Exception as e:
            return self._error(
                f"Failed to call multichain util function '{function_name}'.",
                hint="Ensure chain metadata and coordinate inputs are in expected format.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # ESMFold Utilities
    # -------------------------------------------------------------------------
    def load_esmfold_model(self, loader_name: str = "esmfold_v1", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Load ESMFold model via esm.esmfold.v1.pretrained dynamic loader.

        Args:
            loader_name: Function in esm.esmfold.v1.pretrained, default 'esmfold_v1'.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            Dict[str, Any]: status + model object.
        """
        try:
            mod = self._modules.get("esm.esmfold.v1.pretrained") or importlib.import_module("esm.esmfold.v1.pretrained")
            fn = getattr(mod, loader_name, None)
            if fn is None or not callable(fn):
                return self._error(
                    f"ESMFold loader '{loader_name}' not found in esm.esmfold.v1.pretrained.",
                    hint="Check available loader names using list_available_symbols('esm.esmfold.v1.pretrained').",
                )
            model = fn(*args, **kwargs)
            return self._ok({"loader": loader_name, "model": model})
        except Exception as e:
            return self._error(
                f"Failed to load ESMFold model via '{loader_name}'.",
                hint="Install optional ESMFold/OpenFold dependencies and verify torch/cuda compatibility.",
                error=e,
            )

    # -------------------------------------------------------------------------
    # CLI Fallback Wrappers for scripts
    # -------------------------------------------------------------------------
    def call_script_module(self, module_name: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a repository script module main entry (if available), as graceful fallback.

        Supported modules from analysis:
            - scripts.extract
            - scripts.fold

        Args:
            module_name: Full module path.
            argv: Optional argv-style list for parser-based main methods.

        Returns:
            Dict[str, Any]: status + execution metadata.
        """
        try:
            mod = self._modules.get(module_name) or importlib.import_module(module_name)

            if hasattr(mod, "main") and callable(mod.main):
                main_sig = inspect.signature(mod.main)
                if len(main_sig.parameters) == 0:
                    result = mod.main()
                else:
                    result = mod.main(argv if argv is not None else [])
                return self._ok({"module": module_name, "result": result}, message="Script module executed via import-mode main().")

            return self._error(
                f"Module '{module_name}' does not expose a callable main().",
                hint="Use subprocess fallback in host runtime: python -m <module> <args>.",
            )
        except Exception as e:
            return self._error(
                f"Failed to execute script module '{module_name}' in import mode.",
                hint="Try CLI fallback: python -m scripts.extract or python -m scripts.fold.",
                error=e,
            )

    def run_extract(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run embeddings extraction script through import-mode fallback.

        Args:
            argv: Command-style arguments for scripts.extract.main if supported.

        Returns:
            Dict[str, Any]: status + script execution result.
        """
        return self.call_script_module("scripts.extract", argv=argv)

    def run_fold(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run ESMFold prediction script through import-mode fallback.

        Args:
            argv: Command-style arguments for scripts.fold.main if supported.

        Returns:
            Dict[str, Any]: status + script execution result.
        """
        return self.call_script_module("scripts.fold", argv=argv)