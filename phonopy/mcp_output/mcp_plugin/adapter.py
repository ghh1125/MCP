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
    MCP Import Mode Adapter for phonopy repository.

    This adapter prioritizes direct Python imports from repository source code and
    gracefully falls back to CLI execution guidance when import-mode operations fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        result = {"status": "success", "mode": self.mode, "message": message}
        if data:
            result.update(data)
        return result

    def _err(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if hint:
            payload["hint"] = hint
        return payload

    def _load_modules(self) -> None:
        module_names = [
            "phonopy",
            "phonopy.api_phonopy",
            "phonopy.api_gruneisen",
            "phonopy.api_qha",
            "phonopy.cui.load",
            "phonopy.cui.phonopy_script",
            "phonopy.scripts.phonopy",
            "phonopy.scripts.phonopy_load",
            "phonopy.scripts.phonopy_bandplot",
            "phonopy.scripts.phonopy_gruneisen",
            "phonopy.scripts.phonopy_gruneisenplot",
            "phonopy.scripts.phonopy_qha",
            "phonopy.scripts.phonopy_pdosplot",
            "phonopy.scripts.phonopy_propplot",
            "phonopy.scripts.phonopy_tdplot",
            "phonopy.scripts.phonopy_calc_convert",
            "phonopy.scripts.phonopy_qe_born",
            "phonopy.scripts.phonopy_vasp_born",
            "phonopy.scripts.phonopy_vasp_efe",
        ]
        for mod in module_names:
            try:
                self._modules[mod] = importlib.import_module(mod)
            except Exception as e:
                self._import_errors[mod] = str(e)

    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter import readiness and report available modules.

        Returns:
            dict: Unified status dictionary with loaded modules and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "import_ready": len(self._modules) > 0,
            },
            message="Adapter health check completed.",
        )

    # -------------------------------------------------------------------------
    # Core class factory methods
    # -------------------------------------------------------------------------
    def create_phonopy_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_phonopy.Phonopy.

        Parameters:
            *args: Positional arguments forwarded to Phonopy constructor.
            **kwargs: Keyword arguments forwarded to Phonopy constructor.

        Returns:
            dict: status + created object or error details.
        """
        try:
            mod = self._modules.get("phonopy.api_phonopy")
            if not mod or not hasattr(mod, "Phonopy"):
                return self._err(
                    "Phonopy class is not available in import mode.",
                    hint="Check local source integrity and required dependencies like numpy/spglib.",
                )
            instance = mod.Phonopy(*args, **kwargs)
            return self._ok({"instance": instance}, "Phonopy instance created.")
        except Exception as e:
            return self._err("Failed to create Phonopy instance.", e, "Verify constructor parameters and crystal inputs.")

    def create_gruneisen_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_gruneisen.PhonopyGruneisen.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: status + created object or error details.
        """
        try:
            mod = self._modules.get("phonopy.api_gruneisen")
            cls_name = "PhonopyGruneisen"
            if not mod or not hasattr(mod, cls_name):
                return self._err(
                    "PhonopyGruneisen class is not available in import mode.",
                    hint="Ensure gruneisen API is present in source and compatible with your version.",
                )
            instance = getattr(mod, cls_name)(*args, **kwargs)
            return self._ok({"instance": instance}, "PhonopyGruneisen instance created.")
        except Exception as e:
            return self._err("Failed to create PhonopyGruneisen instance.", e)

    def create_qha_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of phonopy.api_qha.PhonopyQHA.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: status + created object or error details.
        """
        try:
            mod = self._modules.get("phonopy.api_qha")
            cls_name = "PhonopyQHA"
            if not mod or not hasattr(mod, cls_name):
                return self._err(
                    "PhonopyQHA class is not available in import mode.",
                    hint="Ensure QHA API module is loaded and optional scientific dependencies are installed.",
                )
            instance = getattr(mod, cls_name)(*args, **kwargs)
            return self._ok({"instance": instance}, "PhonopyQHA instance created.")
        except Exception as e:
            return self._err("Failed to create PhonopyQHA instance.", e)

    # -------------------------------------------------------------------------
    # CLI-wrapper call methods (imported script modules)
    # -------------------------------------------------------------------------
    def _call_module_main(self, module_name: str, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            mod = self._modules.get(module_name)
            if not mod:
                return self._err(
                    f"Module '{module_name}' is not available in import mode.",
                    hint="Use CLI fallback or resolve import dependencies.",
                )

            if hasattr(mod, "main") and callable(mod.main):
                result = mod.main(argv if argv is not None else [])
                return self._ok({"result": result}, f"{module_name}.main executed.")
            if hasattr(mod, "run") and callable(mod.run):
                result = mod.run(argv if argv is not None else [])
                return self._ok({"result": result}, f"{module_name}.run executed.")

            return self._err(
                f"No callable entrypoint found in module '{module_name}'.",
                hint="Inspect module implementation for available callable functions.",
            )
        except SystemExit as e:
            return self._ok({"result": int(e.code) if e.code is not None else 0}, f"{module_name} exited via SystemExit.")
        except Exception as e:
            return self._err(f"Failed to execute module '{module_name}'.", e)

    def call_phonopy(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy", argv)

    def call_phonopy_load(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_load entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_load", argv)

    def call_phonopy_bandplot(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_bandplot entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_bandplot", argv)

    def call_phonopy_gruneisen(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_gruneisen entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_gruneisen", argv)

    def call_phonopy_gruneisenplot(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_gruneisenplot entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_gruneisenplot", argv)

    def call_phonopy_qha(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_qha entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_qha", argv)

    def call_phonopy_pdosplot(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_pdosplot entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_pdosplot", argv)

    def call_phonopy_propplot(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_propplot entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_propplot", argv)

    def call_phonopy_tdplot(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_tdplot entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_tdplot", argv)

    def call_phonopy_calc_convert(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_calc_convert entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_calc_convert", argv)

    def call_phonopy_qe_born(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_qe_born entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_qe_born", argv)

    def call_phonopy_vasp_born(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_vasp_born entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_vasp_born", argv)

    def call_phonopy_vasp_efe(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call phonopy.scripts.phonopy_vasp_efe entrypoint."""
        return self._call_module_main("phonopy.scripts.phonopy_vasp_efe", argv)

    # -------------------------------------------------------------------------
    # Fallback guidance
    # -------------------------------------------------------------------------
    def fallback_cli_guidance(self, command: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Provide actionable fallback command guidance when import mode is unavailable.

        Parameters:
            command: CLI command name, e.g., 'phonopy', 'phonopy-qha'.
            args: Optional list of command arguments.

        Returns:
            dict: status + composed command string and next-step guidance.
        """
        try:
            args = args or []
            cmd = " ".join([command] + args)
            return self._ok(
                {
                    "fallback_mode": "cli",
                    "suggested_command": cmd,
                    "guidance": "Run the suggested command in an environment with phonopy dependencies installed.",
                },
                "CLI fallback guidance generated.",
            )
        except Exception as e:
            return self._err("Failed to generate CLI fallback guidance.", e)