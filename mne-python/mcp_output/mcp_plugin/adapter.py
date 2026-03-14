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
    Import-mode adapter for the mne-python MCP plugin integration.

    This adapter prioritizes Python imports and provides a graceful CLI fallback
    pathway when import-based execution is unavailable.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state, import registry, and module availability.

        Attributes:
            mode: Adapter execution mode, fixed to "import".
            package_root: Root import path for repository package.
            modules: Loaded module cache keyed by logical name.
            available: Boolean import readiness state.
            warnings: List of non-fatal issues detected during initialization.
        """
        self.mode = "import"
        self.package_root = "mne"
        self.modules: Dict[str, Any] = {}
        self.available = False
        self.warnings: List[str] = []
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Attempt to import core and command modules identified by analysis.

        This method captures and stores import exceptions so the adapter can
        continue operating in graceful fallback mode.
        """
        targets = {
            "mne": "mne",
            "commands": "mne.commands",
        }

        loaded = 0
        for key, mod_path in targets.items():
            try:
                self.modules[key] = importlib.import_module(mod_path)
                loaded += 1
            except Exception as exc:
                self.modules[key] = None
                self.warnings.append(
                    f"Failed to import '{mod_path}'. Verify local source checkout and dependencies. Detail: {exc}"
                )
        self.available = loaded > 0

    # -------------------------------------------------------------------------
    # Unified response helpers
    # -------------------------------------------------------------------------
    def _ok(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "success", "message": message, "data": data or {}}

    def _fail(
        self,
        message: str,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"status": "error", "message": message, "data": data or {}}
        if error:
            payload["error"] = error
        if guidance:
            payload["guidance"] = guidance
        return payload

    def _fallback(
        self,
        action: str,
        reason: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "message": f"Import mode unavailable for '{action}'.",
            "reason": reason,
            "guidance": (
                "Ensure repository source is present under the configured 'source' directory and "
                "install required dependencies (numpy, scipy, matplotlib, packaging, pooch, tqdm). "
                "If import still fails, use the CLI fallback via the 'mne' command."
            ),
            "data": extra or {},
        }

    # -------------------------------------------------------------------------
    # Health / Introspection
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import diagnostics.

        Returns:
            Dict with status, mode, import availability, and warning details.
        """
        return self._ok(
            "Adapter health check completed.",
            {
                "mode": self.mode,
                "available": self.available,
                "loaded_modules": {k: bool(v) for k, v in self.modules.items()},
                "warnings": self.warnings,
            },
        )

    def list_known_packages(self) -> Dict[str, Any]:
        """
        Return package namespaces discovered during analysis.

        Returns:
            Dict containing analyzed package names for discovery/debugging.
        """
        packages = [
            "deployment.mne-python.source",
            "mcp_output.mcp_plugin",
            "source.mne",
            "source.mne._fiff",
            "source.mne.beamformer",
            "source.mne.channels",
            "source.mne.commands",
            "source.mne.data",
            "source.mne.datasets",
            "source.mne.decoding",
            "source.mne.export",
            "source.mne.forward",
            "source.mne.gui",
            "source.mne.html_templates",
            "source.mne.inverse_sparse",
            "source.mne.io",
            "source.mne.minimum_norm",
            "source.mne.preprocessing",
            "source.mne.report",
            "source.mne.simulation",
            "source.mne.source_space",
            "source.mne.stats",
            "source.mne.tests",
            "source.mne.time_frequency",
            "source.mne.utils",
            "source.mne.viz",
        ]
        return self._ok("Known package list prepared.", {"packages": packages})

    # -------------------------------------------------------------------------
    # Module management
    # -------------------------------------------------------------------------
    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Dynamically import an MNE module using full package path.

        Args:
            module_path: Absolute module path (e.g., 'mne.io', 'mne.preprocessing').

        Returns:
            Unified status dictionary with module import result.
        """
        try:
            mod = importlib.import_module(module_path)
            self.modules[module_path] = mod
            return self._ok("Module imported successfully.", {"module_path": module_path})
        except Exception as exc:
            return self._fail(
                "Module import failed.",
                error=str(exc),
                guidance="Confirm module path and dependency installation.",
                data={"module_path": module_path},
            )

    def get_module_attributes(self, module_path: str, limit: int = 200) -> Dict[str, Any]:
        """
        Enumerate public attributes for a module to support function discovery.

        Args:
            module_path: Full module path.
            limit: Maximum number of attributes to return.

        Returns:
            Unified status dictionary containing exported attribute names.
        """
        try:
            mod = self.modules.get(module_path) or importlib.import_module(module_path)
            attrs = [a for a in dir(mod) if not a.startswith("_")]
            return self._ok(
                "Module attributes fetched.",
                {"module_path": module_path, "attributes": attrs[: max(1, limit)]},
            )
        except Exception as exc:
            return self._fail(
                "Could not inspect module attributes.",
                error=str(exc),
                guidance="Import the module first and verify it is available in local source.",
                data={"module_path": module_path},
            )

    # -------------------------------------------------------------------------
    # Core MNE call surface
    # -------------------------------------------------------------------------
    def call_mne_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from the top-level mne module by name.

        Args:
            function_name: Name of the function in module 'mne'.
            *args: Positional arguments forwarded to the target function.
            **kwargs: Keyword arguments forwarded to the target function.

        Returns:
            Unified status dictionary with execution result or actionable failure.
        """
        if not self.modules.get("mne"):
            return self._fallback("call_mne_function", "Top-level module 'mne' is not importable.")

        try:
            target = getattr(self.modules["mne"], function_name, None)
            if target is None or not callable(target):
                return self._fail(
                    "Requested MNE function was not found.",
                    guidance="Use get_module_attributes('mne') to discover available callables.",
                    data={"function_name": function_name},
                )
            result = target(*args, **kwargs)
            return self._ok(
                "MNE function executed successfully.",
                {"function_name": function_name, "result": result},
            )
        except Exception as exc:
            return self._fail(
                "MNE function execution failed.",
                error=str(exc),
                guidance="Validate function arguments and data formats expected by MNE.",
                data={"function_name": function_name, "traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # CLI wrapper (fallback-friendly)
    # -------------------------------------------------------------------------
    def call_mne_cli(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the primary MNE command-line wrapper from imported command module.

        Args:
            argv: Optional list of CLI-like arguments. If omitted, attempts default call.

        Returns:
            Unified status dictionary with invocation status and hints.
        """
        commands_mod = self.modules.get("commands")
        if not commands_mod:
            return self._fallback("call_mne_cli", "Module 'mne.commands' is not importable.")

        try:
            entry_candidates = ["main", "run", "command_main"]
            entry = None
            for name in entry_candidates:
                fn = getattr(commands_mod, name, None)
                if callable(fn):
                    entry = fn
                    break

            if entry is None:
                return self._fail(
                    "No callable CLI entry point found in mne.commands.",
                    guidance="Inspect mne.commands module attributes and map the correct callable.",
                    data={"checked_candidates": entry_candidates},
                )

            if argv is None:
                out = entry()
            else:
                out = entry(argv)

            return self._ok(
                "MNE CLI wrapper executed.",
                {"argv": argv or [], "result": out, "entry_point": entry.__name__},
            )
        except TypeError:
            try:
                out = entry()  # type: ignore[misc]
                return self._ok(
                    "MNE CLI wrapper executed with default signature.",
                    {"argv": argv or [], "result": out, "entry_point": entry.__name__},  # type: ignore[union-attr]
                )
            except Exception as exc:
                return self._fail(
                    "MNE CLI invocation failed.",
                    error=str(exc),
                    guidance="Pass valid subcommands/arguments or verify command module compatibility.",
                    data={"traceback": traceback.format_exc()},
                )
        except Exception as exc:
            return self._fail(
                "MNE CLI invocation failed.",
                error=str(exc),
                guidance="Check installed optional dependencies and command arguments.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Class instantiation helper (generic, analysis-driven)
    # -------------------------------------------------------------------------
    def create_instance(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Instantiate a class from a target module path.

        Args:
            module_path: Full module path containing the class.
            class_name: Class name to instantiate.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary with instantiated object handle.
        """
        try:
            mod = self.modules.get(module_path) or importlib.import_module(module_path)
            cls = getattr(mod, class_name, None)
            if cls is None:
                return self._fail(
                    "Class not found in module.",
                    guidance="Use get_module_attributes(module_path) to verify class exports.",
                    data={"module_path": module_path, "class_name": class_name},
                )
            instance = cls(*args, **kwargs)
            return self._ok(
                "Class instantiated successfully.",
                {"module_path": module_path, "class_name": class_name, "instance": instance},
            )
        except Exception as exc:
            return self._fail(
                "Class instantiation failed.",
                error=str(exc),
                guidance="Verify constructor arguments and required dependencies for this class.",
                data={"module_path": module_path, "class_name": class_name, "traceback": traceback.format_exc()},
            )