import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the pyfolio repository.

    This adapter attempts direct import of repository modules from the local `source` directory.
    It exposes dedicated wrappers for discovered classes and functions from analysis results,
    with unified return payloads and graceful fallback behavior.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state and attempt imports.

        Attributes:
            mode (str): Current execution mode. "import" by default; may switch to "blackbox".
            modules (dict): Loaded module objects keyed by full module path.
            symbols (dict): Loaded symbols keyed by "module:symbol".
            import_errors (dict): Import failures with actionable messages.
        """
        self.mode = "import"
        self.modules: Dict[str, Any] = {}
        self.symbols: Dict[str, Any] = {}
        self.import_errors: Dict[str, str] = {}

        self._load_modules_and_symbols()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, exc: Optional[BaseException] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        err = {"status": "error", "mode": self.mode, "message": message}
        if exc is not None:
            err["error"] = str(exc)
            err["traceback"] = traceback.format_exc()
        if guidance:
            err["guidance"] = guidance
        return err

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self.modules[module_path] = mod
            return mod
        except Exception as e:
            self.import_errors[module_path] = (
                f"Failed to import '{module_path}'. Verify repository source is available under "
                f"'{source_path}' and required dependencies are installed."
            )
            self.import_errors[f"{module_path}.__exception__"] = str(e)
            return None

    def _load_symbol(self, module_path: str, symbol_name: str) -> None:
        mod = self.modules.get(module_path)
        key = f"{module_path}:{symbol_name}"
        if mod is None:
            self.import_errors[key] = f"Cannot resolve symbol '{symbol_name}' because module '{module_path}' is not loaded."
            return
        try:
            self.symbols[key] = getattr(mod, symbol_name)
        except Exception as e:
            self.import_errors[key] = (
                f"Failed to load symbol '{symbol_name}' from '{module_path}'. "
                f"Ensure this repository version contains the symbol."
            )
            self.import_errors[f"{key}.__exception__"] = str(e)

    def _load_modules_and_symbols(self) -> None:
        # Main discovered module from analysis
        self._import_module("pyfolio.versioneer")

        # Load discovered classes and functions
        for cls in ["NotThisMethod", "VersioneerBadRootError", "VersioneerConfig"]:
            self._load_symbol("pyfolio.versioneer", cls)
        for fn in ["do_setup", "do_vcs_install", "get_cmdclass"]:
            self._load_symbol("pyfolio.versioneer", fn)

        # Switch mode on import failure
        if self.import_errors:
            self.mode = "blackbox"

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter import health and current mode.

        Returns:
            dict: Unified status payload including loaded modules, symbols, and import errors.
        """
        return self._ok(
            data={
                "loaded_modules": sorted(self.modules.keys()),
                "loaded_symbols": sorted(self.symbols.keys()),
                "import_errors": self.import_errors,
            },
            message="Health check completed.",
        )

    # -------------------------------------------------------------------------
    # Fallback helpers
    # -------------------------------------------------------------------------
    def _fallback(self, target: str) -> Dict[str, Any]:
        return self._err(
            message=f"'{target}' unavailable in import mode. Adapter is running in fallback mode.",
            guidance=(
                "Check local source path, pin dependencies (numpy, pandas, scipy, matplotlib, seaborn, empyrical), "
                "and ensure the repository version exposes the requested symbol."
            ),
        )

    # -------------------------------------------------------------------------
    # Class instance methods (discovered classes)
    # -------------------------------------------------------------------------
    def create_not_this_method(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of pyfolio.versioneer.NotThisMethod.

        Parameters:
            *args: Positional arguments forwarded to constructor.
            **kwargs: Keyword arguments forwarded to constructor.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        key = "pyfolio.versioneer:NotThisMethod"
        cls = self.symbols.get(key)
        if cls is None:
            return self._fallback("NotThisMethod")
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, "NotThisMethod instance created.")
        except Exception as e:
            return self._err("Failed to instantiate NotThisMethod.", e, "Review constructor arguments.")

    def create_versioneer_bad_root_error(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of pyfolio.versioneer.VersioneerBadRootError.

        Parameters:
            *args: Positional arguments forwarded to constructor.
            **kwargs: Keyword arguments forwarded to constructor.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        key = "pyfolio.versioneer:VersioneerBadRootError"
        cls = self.symbols.get(key)
        if cls is None:
            return self._fallback("VersioneerBadRootError")
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, "VersioneerBadRootError instance created.")
        except Exception as e:
            return self._err("Failed to instantiate VersioneerBadRootError.", e, "Review constructor arguments.")

    def create_versioneer_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of pyfolio.versioneer.VersioneerConfig.

        Parameters:
            *args: Positional arguments forwarded to constructor.
            **kwargs: Keyword arguments forwarded to constructor.

        Returns:
            dict: Unified status payload with instance or error details.
        """
        key = "pyfolio.versioneer:VersioneerConfig"
        cls = self.symbols.get(key)
        if cls is None:
            return self._fallback("VersioneerConfig")
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, "VersioneerConfig instance created.")
        except Exception as e:
            return self._err("Failed to instantiate VersioneerConfig.", e, "Review constructor arguments.")

    # -------------------------------------------------------------------------
    # Function call methods (discovered functions)
    # -------------------------------------------------------------------------
    def call_do_setup(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call pyfolio.versioneer.do_setup.

        Parameters:
            *args: Positional arguments for do_setup.
            **kwargs: Keyword arguments for do_setup.

        Returns:
            dict: Unified status payload including function return value.
        """
        key = "pyfolio.versioneer:do_setup"
        fn = self.symbols.get(key)
        if fn is None:
            return self._fallback("do_setup")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "do_setup executed.")
        except Exception as e:
            return self._err("Failed to execute do_setup.", e, "Validate arguments and repository state.")

    def call_do_vcs_install(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call pyfolio.versioneer.do_vcs_install.

        Parameters:
            *args: Positional arguments for do_vcs_install.
            **kwargs: Keyword arguments for do_vcs_install.

        Returns:
            dict: Unified status payload including function return value.
        """
        key = "pyfolio.versioneer:do_vcs_install"
        fn = self.symbols.get(key)
        if fn is None:
            return self._fallback("do_vcs_install")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "do_vcs_install executed.")
        except Exception as e:
            return self._err("Failed to execute do_vcs_install.", e, "Validate VCS context and arguments.")

    def call_get_cmdclass(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call pyfolio.versioneer.get_cmdclass.

        Parameters:
            *args: Positional arguments for get_cmdclass.
            **kwargs: Keyword arguments for get_cmdclass.

        Returns:
            dict: Unified status payload including function return value.
        """
        key = "pyfolio.versioneer:get_cmdclass"
        fn = self.symbols.get(key)
        if fn is None:
            return self._fallback("get_cmdclass")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "get_cmdclass executed.")
        except Exception as e:
            return self._err("Failed to execute get_cmdclass.", e, "Validate arguments and setup context.")