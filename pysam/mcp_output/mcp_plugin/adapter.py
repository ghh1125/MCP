import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for pysam repository modules.

    This adapter prioritizes direct import execution from local source checkout and
    gracefully degrades to fallback mode when import/runtime constraints are unmet.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._init_imports()

    # =========================================================================
    # Internal Utilities
    # =========================================================================
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _safe_exec(self, fn, *args, **kwargs) -> Dict[str, Any]:
        try:
            data = fn(*args, **kwargs)
            return self._result("success", data=data)
        except Exception as exc:
            return self._result(
                "error",
                error=str(exc),
                guidance="Verify pysam native extensions are built and available under source/pysam.",
                traceback=traceback.format_exc(),
            )

    def _try_import(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None

    def _init_imports(self) -> None:
        """
        Attempt importing all identified repository modules from local source path.
        """
        targets = [
            "pysam",
            "pysam.samtools",
            "pysam.bcftools",
            "pysam.utils",
            "pysam.Pileup",
            "pysam.version",
        ]
        for module_path in targets:
            self._try_import(module_path)

        self._loaded = "pysam" in self._modules
        if not self._loaded:
            self.mode = "fallback"

    # =========================================================================
    # Status / Diagnostics
    # =========================================================================
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.

        Returns:
            dict: Unified status payload including mode, loaded modules, and import errors.
        """
        return self._result(
            "success" if self._loaded else "degraded",
            loaded=self._loaded,
            loaded_modules=list(self._modules.keys()),
            import_errors=self._import_errors,
            guidance=(
                "If degraded, compile/install local pysam extensions from source and retry."
                if not self._loaded
                else "Adapter is ready."
            ),
        )

    # =========================================================================
    # Core pysam module access
    # =========================================================================
    def get_pysam_module(self) -> Dict[str, Any]:
        """
        Return basic metadata from imported pysam module.

        Returns:
            dict: status + module/version metadata.
        """
        if "pysam" not in self._modules:
            return self._result(
                "error",
                error="pysam module is not available.",
                guidance="Build pysam C extensions in source tree or provide compatible binary artifacts.",
            )

        def _impl():
            pysam_mod = self._modules["pysam"]
            return {
                "module": "pysam",
                "version": getattr(pysam_mod, "__version__", None),
                "file": getattr(pysam_mod, "__file__", None),
                "attributes_sample": sorted([a for a in dir(pysam_mod) if not a.startswith("_")])[:50],
            }

        return self._safe_exec(_impl)

    # =========================================================================
    # samtools wrappers (pysam.samtools)
    # =========================================================================
    def samtools_call(self, command: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a samtools subcommand via pysam.samtools dynamic dispatcher.

        Args:
            command: Subcommand name (for example: 'view', 'sort', 'index', etc.).
            *args: Positional arguments forwarded to the subcommand.
            **kwargs: Keyword arguments forwarded to the subcommand.

        Returns:
            dict: status + execution output or error details.
        """
        mod = self._modules.get("pysam.samtools")
        if mod is None:
            return self._result(
                "error",
                error="pysam.samtools is unavailable.",
                guidance="Ensure pysam is compiled with bundled/linked samtools components.",
            )

        def _impl():
            fn = getattr(mod, command, None)
            if fn is None:
                raise AttributeError(
                    f"samtools command '{command}' not found. Inspect available commands with list_samtools_commands()."
                )
            return fn(*args, **kwargs)

        return self._safe_exec(_impl)

    def list_samtools_commands(self) -> Dict[str, Any]:
        """
        List callable samtools-like commands exposed by pysam.samtools.

        Returns:
            dict: status + command names.
        """
        mod = self._modules.get("pysam.samtools")
        if mod is None:
            return self._result(
                "error",
                error="pysam.samtools is unavailable.",
                guidance="Import/build issues detected. Run health_check() for details.",
            )

        def _impl():
            names = []
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                obj = getattr(mod, name, None)
                if callable(obj):
                    names.append(name)
            return sorted(names)

        return self._safe_exec(_impl)

    # =========================================================================
    # bcftools wrappers (pysam.bcftools)
    # =========================================================================
    def bcftools_call(self, command: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a bcftools subcommand via pysam.bcftools dynamic dispatcher.

        Args:
            command: Subcommand name (for example: 'view', 'query', etc.).
            *args: Positional arguments forwarded to the subcommand.
            **kwargs: Keyword arguments forwarded to the subcommand.

        Returns:
            dict: status + execution output or error details.
        """
        mod = self._modules.get("pysam.bcftools")
        if mod is None:
            return self._result(
                "error",
                error="pysam.bcftools is unavailable.",
                guidance="Ensure pysam is built with bcftools components.",
            )

        def _impl():
            fn = getattr(mod, command, None)
            if fn is None:
                raise AttributeError(
                    f"bcftools command '{command}' not found. Inspect available commands with list_bcftools_commands()."
                )
            return fn(*args, **kwargs)

        return self._safe_exec(_impl)

    def list_bcftools_commands(self) -> Dict[str, Any]:
        """
        List callable bcftools-like commands exposed by pysam.bcftools.

        Returns:
            dict: status + command names.
        """
        mod = self._modules.get("pysam.bcftools")
        if mod is None:
            return self._result(
                "error",
                error="pysam.bcftools is unavailable.",
                guidance="Import/build issues detected. Run health_check() for details.",
            )

        def _impl():
            names = []
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                obj = getattr(mod, name, None)
                if callable(obj):
                    names.append(name)
            return sorted(names)

        return self._safe_exec(_impl)

    # =========================================================================
    # Version / metadata helpers
    # =========================================================================
    def get_version_info(self) -> Dict[str, Any]:
        """
        Collect version metadata from pysam.version and pysam root module.

        Returns:
            dict: status + discovered version fields.
        """
        def _impl():
            info: Dict[str, Any] = {}
            root = self._modules.get("pysam")
            ver_mod = self._modules.get("pysam.version")
            if root is not None:
                info["pysam___version__"] = getattr(root, "__version__", None)
            if ver_mod is not None:
                for key in dir(ver_mod):
                    if key.startswith("_"):
                        continue
                    info[key] = getattr(ver_mod, key)
            return info

        return self._safe_exec(_impl)

    # =========================================================================
    # Generic module call support for full feature coverage
    # =========================================================================
    def call_module_function(
        self,
        module_path: str,
        function_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generic function invoker for imported pysam modules.

        Args:
            module_path: Full module path (for example: 'pysam.utils').
            function_name: Function to call within the module.
            args: Optional positional args list.
            kwargs: Optional keyword args dict.

        Returns:
            dict: status + function return payload or descriptive error.
        """
        args = args or []
        kwargs = kwargs or {}

        if module_path not in self._modules:
            mod = self._try_import(module_path)
            if mod is None:
                return self._result(
                    "error",
                    error=f"Module '{module_path}' could not be imported.",
                    guidance="Check module path and ensure compiled dependencies are present.",
                    import_error=self._import_errors.get(module_path),
                )

        mod = self._modules[module_path]

        def _impl():
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                raise AttributeError(
                    f"Function '{function_name}' not found or not callable in module '{module_path}'."
                )
            return fn(*args, **kwargs)

        return self._safe_exec(_impl)