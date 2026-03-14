import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the Scanpy repository.

    This adapter prioritizes direct Python imports and provides a graceful
    fallback path hint for CLI execution when import-mode fails.
    """

    # ---------------------------------------------------------------------
    # Lifecycle and module management
    # ---------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._load_modules()

    def _ok(self, data: Any = None, message: str = "ok") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _err(self, message: str, guidance: Optional[str] = None, details: Any = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if details is not None:
            payload["details"] = details
        return payload

    def _load_modules(self) -> None:
        try:
            self._modules["scanpy"] = importlib.import_module("scanpy")
            self._modules["scanpy.cli"] = importlib.import_module("scanpy.cli")
            self._modules["scanpy.datasets"] = importlib.import_module("scanpy.datasets")
            self._modules["scanpy.get"] = importlib.import_module("scanpy.get")
            self._modules["scanpy.pp"] = importlib.import_module("scanpy.pp")
            self._modules["scanpy.tl"] = importlib.import_module("scanpy.tl")
            self._modules["scanpy.pl"] = importlib.import_module("scanpy.pl")
            self._modules["scanpy.metrics"] = importlib.import_module("scanpy.metrics")
            self._modules["scanpy.queries"] = importlib.import_module("scanpy.queries")
            self._modules["scanpy.external"] = importlib.import_module("scanpy.external")
            self._modules["scanpy.readwrite"] = importlib.import_module("scanpy.readwrite")
        except Exception as exc:
            self._import_error = str(exc)

    def health(self) -> Dict[str, Any]:
        """
        Check whether import-mode is available.

        Returns:
            Unified status dictionary with loaded module list or actionable error.
        """
        if self._import_error:
            return self._err(
                "Import mode initialization failed.",
                guidance=(
                    "Verify repository source is mounted under the expected 'source' directory, "
                    "and install required dependencies such as numpy, scipy, pandas, anndata, h5py, "
                    "matplotlib, scikit-learn, numba, and networkx."
                ),
                details={"import_error": self._import_error, "fallback_cli": "python -m scanpy"},
            )
        return self._ok(
            data={"loaded_modules": sorted(self._modules.keys()), "fallback_cli": "python -m scanpy"},
            message="Import mode is ready.",
        )

    # ---------------------------------------------------------------------
    # Generic invocation helpers
    # ---------------------------------------------------------------------
    def _resolve_attr(self, module_key: str, attr_name: str) -> Any:
        if self._import_error:
            raise RuntimeError(
                "Import mode is unavailable. Call health() for diagnostics and fallback guidance."
            )
        mod = self._modules.get(module_key)
        if mod is None:
            raise ValueError(f"Module '{module_key}' is not loaded.")
        if not hasattr(mod, attr_name):
            raise AttributeError(f"Attribute '{attr_name}' not found in module '{module_key}'.")
        return getattr(mod, attr_name)

    def call(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from a loaded module by name.

        Parameters:
            module_key: Full module key, e.g. 'scanpy.pp', 'scanpy.tl', 'scanpy.datasets'.
            function_name: Callable attribute name in the module.
            *args, **kwargs: Positional and keyword parameters passed to the target function.

        Returns:
            Unified status dictionary containing function result or actionable error.
        """
        try:
            fn = self._resolve_attr(module_key, function_name)
            if not callable(fn):
                return self._err(
                    f"Attribute '{function_name}' in '{module_key}' is not callable.",
                    guidance="Choose a callable function name or use get_attr() for non-callables.",
                )
            return self._ok(data=fn(*args, **kwargs), message=f"Called {module_key}.{function_name}")
        except Exception as exc:
            return self._err(
                f"Failed to call {module_key}.{function_name}.",
                guidance="Check parameter names/types and ensure optional dependencies for the chosen method are installed.",
                details={"error": str(exc), "traceback": traceback.format_exc()},
            )

    def get_attr(self, module_key: str, attr_name: str) -> Dict[str, Any]:
        """
        Fetch any module attribute by name.

        Parameters:
            module_key: Full module key.
            attr_name: Attribute name to retrieve.

        Returns:
            Unified status dictionary with attribute value.
        """
        try:
            attr = self._resolve_attr(module_key, attr_name)
            return self._ok(data=attr, message=f"Retrieved {module_key}.{attr_name}")
        except Exception as exc:
            return self._err(
                f"Failed to retrieve {module_key}.{attr_name}.",
                guidance="Use list_module_attrs() to inspect available names.",
                details={"error": str(exc)},
            )

    def list_module_attrs(self, module_key: str, prefix: str = "") -> Dict[str, Any]:
        """
        List attributes available in a loaded module.

        Parameters:
            module_key: Full module key.
            prefix: Optional prefix filter.

        Returns:
            Unified status dictionary with sorted attribute names.
        """
        try:
            if self._import_error:
                raise RuntimeError(self._import_error)
            mod = self._modules.get(module_key)
            if mod is None:
                raise ValueError(f"Module '{module_key}' is not loaded.")
            names = sorted([n for n in dir(mod) if n.startswith(prefix)])
            return self._ok(data={"module": module_key, "attributes": names}, message="Listed module attributes.")
        except Exception as exc:
            return self._err(
                f"Failed to list attributes for {module_key}.",
                guidance="Call health() first and confirm module key correctness.",
                details={"error": str(exc)},
            )

    # ---------------------------------------------------------------------
    # Scanpy-focused convenience wrappers (import strategy primary, CLI fallback hint)
    # ---------------------------------------------------------------------
    def scanpy_cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute scanpy CLI entrypoint function if available.

        Parameters:
            argv: Optional CLI args list.

        Returns:
            Unified status dictionary.
        """
        try:
            cli_mod = self._modules["scanpy.cli"]
            if hasattr(cli_mod, "main") and callable(cli_mod.main):
                result = cli_mod.main(argv=argv) if argv is not None else cli_mod.main()
                return self._ok(data=result, message="scanpy.cli.main executed.")
            return self._err(
                "scanpy.cli.main is not available.",
                guidance="Use fallback CLI: python -m scanpy",
            )
        except Exception as exc:
            return self._err(
                "Failed to execute scanpy CLI main.",
                guidance="Try fallback CLI execution: python -m scanpy",
                details={"error": str(exc), "traceback": traceback.format_exc()},
            )

    def read(self, *args: Any, **kwargs: Any) -> Dict