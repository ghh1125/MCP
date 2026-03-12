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
    MCP import-mode adapter for the Prophet repository.

    This adapter attempts to import and expose selected internal build/script
    utilities discovered from repository analysis:

    - python.setup:
        - classes: BDistWheelABINone, BuildExtCommand, BuildPyCommand
        - functions: build_cmdstan_model, build_models, get_backends_from_env

    - python.scripts.generate_holidays_file:
        - functions: generate_holidays_df, utf8_to_ascii

    The adapter is designed to be safe in environments where build-time
    dependencies (e.g., setuptools/cmdstan toolchain) may be unavailable.
    It provides graceful fallback responses with actionable guidance.
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt module loading.
        """
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._imports: Dict[str, Optional[Any]] = {}
        self._initialize_imports()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _initialize_imports(self) -> None:
        """
        Load modules and symbols required by this adapter.
        """
        try:
            setup_mod = importlib.import_module("python.setup")
            self._modules["python.setup"] = setup_mod
            self._imports["BDistWheelABINone"] = getattr(setup_mod, "BDistWheelABINone", None)
            self._imports["BuildExtCommand"] = getattr(setup_mod, "BuildExtCommand", None)
            self._imports["BuildPyCommand"] = getattr(setup_mod, "BuildPyCommand", None)
            self._imports["build_cmdstan_model"] = getattr(setup_mod, "build_cmdstan_model", None)
            self._imports["build_models"] = getattr(setup_mod, "build_models", None)
            self._imports["get_backends_from_env"] = getattr(setup_mod, "get_backends_from_env", None)
        except Exception:
            self._modules["python.setup"] = None
            self._imports["BDistWheelABINone"] = None
            self._imports["BuildExtCommand"] = None
            self._imports["BuildPyCommand"] = None
            self._imports["build_cmdstan_model"] = None
            self._imports["build_models"] = None
            self._imports["get_backends_from_env"] = None

        try:
            holidays_mod = importlib.import_module("python.scripts.generate_holidays_file")
            self._modules["python.scripts.generate_holidays_file"] = holidays_mod
            self._imports["generate_holidays_df"] = getattr(holidays_mod, "generate_holidays_df", None)
            self._imports["utf8_to_ascii"] = getattr(holidays_mod, "utf8_to_ascii", None)
        except Exception:
            self._modules["python.scripts.generate_holidays_file"] = None
            self._imports["generate_holidays_df"] = None
            self._imports["utf8_to_ascii"] = None

    def healthcheck(self) -> Dict[str, Any]:
        """
        Return adapter and import health status.

        Returns:
            dict: Unified status dictionary with mode, module availability, and symbol availability.
        """
        try:
            modules = {k: v is not None for k, v in self._modules.items()}
            symbols = {k: v is not None for k, v in self._imports.items()}
            return self._result(
                "success",
                mode=self.mode,
                import_strategy={"primary": "import", "fallback": "blackbox"},
                modules=modules,
                symbols=symbols,
                guidance=(
                    "If symbols are unavailable, ensure repository source is mounted under 'source/' "
                    "and that build dependencies are installed."
                ),
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Healthcheck failed: {exc}",
                traceback=traceback.format_exc(),
                guidance="Verify Python path setup and repository extraction integrity.",
            )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _require_symbol(self, name: str) -> Dict[str, Any]:
        symbol = self._imports.get(name)
        if symbol is None:
            return self._result(
                "fallback",
                error=f"Import unavailable for symbol '{name}'.",
                guidance=(
                    "Run in an environment with repository-local modules importable from 'source/', "
                    "and install required build/runtime dependencies."
                ),
            )
        return self._result("success", symbol=symbol)

    # -------------------------------------------------------------------------
    # Class instance factories (identified classes)
    # -------------------------------------------------------------------------

    def create_bdist_wheel_abi_none_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of python.setup.BDistWheelABINone.

        Parameters:
            *args: Positional arguments forwarded to class constructor.
            **kwargs: Keyword arguments forwarded to class constructor.

        Returns:
            dict: status + instance on success; fallback/error with guidance otherwise.
        """
        check = self._require_symbol("BDistWheelABINone")
        if check["status"] != "success":
            return check
        try:
            cls = check["symbol"]
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance, class_name="BDistWheelABINone")
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to instantiate BDistWheelABINone: {exc}",
                traceback=traceback.format_exc(),
                guidance="Pass constructor arguments compatible with setuptools command classes.",
            )

    def create_build_ext_command_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of python.setup.BuildExtCommand.

        Parameters:
            *args: Positional arguments for constructor.
            **kwargs: Keyword arguments for constructor.

        Returns:
            dict: status + instance or fallback/error payload.
        """
        check = self._require_symbol("BuildExtCommand")
        if check["status"] != "success":
            return check
        try:
            cls = check["symbol"]
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance, class_name="BuildExtCommand")
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to instantiate BuildExtCommand: {exc}",
                traceback=traceback.format_exc(),
                guidance="Provide a valid setuptools Distribution object if required by this command.",
            )

    def create_build_py_command_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of python.setup.BuildPyCommand.

        Parameters:
            *args: Positional arguments for constructor.
            **kwargs: Keyword arguments for constructor.

        Returns:
            dict: status + instance or fallback/error payload.
        """
        check = self._require_symbol("BuildPyCommand")
        if check["status"] != "success":
            return check
        try:
            cls = check["symbol"]
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance, class_name="BuildPyCommand")
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to instantiate BuildPyCommand: {exc}",
                traceback=traceback.format_exc(),
                guidance="Ensure setuptools build command prerequisites are satisfied.",
            )

    # -------------------------------------------------------------------------
    # Function wrappers (identified functions)
    # -------------------------------------------------------------------------

    def call_build_cmdstan_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call python.setup.build_cmdstan_model.

        Parameters:
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: status + result or fallback/error payload.
        """
        check = self._require_symbol("build_cmdstan_model")
        if check["status"] != "success":
            return check
        try:
            fn = check["symbol"]
            result = fn(*args, **kwargs)
            return self._result("success", result=result, function="build_cmdstan_model")
        except Exception as exc:
            return self._result(
                "error",
                error=f"build_cmdstan_model execution failed: {exc}",
                traceback=traceback.format_exc(),
                guidance=(
                    "Ensure CmdStan toolchain is installed and writable build directories are available."
                ),
            )

    def call_build_models(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call python.setup.build_models.

        Parameters:
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: status + result or fallback/error payload.
        """
        check = self._require_symbol("build_models")
        if check["status"] != "success":
            return check
        try:
            fn = check["symbol"]
            result = fn(*args, **kwargs)
            return self._result("success", result=result, function="build_models")
        except Exception as exc:
            return self._result(
                "error",
                error=f"build_models execution failed: {exc}",
                traceback=traceback.format_exc(),
                guidance="Install required C++/Stan build dependencies and retry.",
            )

    def call_get_backends_from_env(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call python.setup.get_backends_from_env.

        Parameters:
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: status + parsed backend info or fallback/error payload.
        """
        check = self._require_symbol("get_backends_from_env")
        if check["status"] != "success":
            return check
        try:
            fn = check["symbol"]
            result = fn(*args, **kwargs)
            return self._result("success", result=result, function="get_backends_from_env")
        except Exception as exc:
            return self._result(
                "error",
                error=f"get_backends_from_env execution failed: {exc}",
                traceback=traceback.format_exc(),
                guidance="Verify related environment variables and expected input format.",
            )

    def call_generate_holidays_df(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call python.scripts.generate_holidays_file.generate_holidays_df.

        Parameters:
            *args: Positional arguments for holiday generation function.
            **kwargs: Keyword arguments for holiday generation function.

        Returns:
            dict: status + generated DataFrame-like result or fallback/error payload.
        """
        check = self._require_symbol("generate_holidays_df")
        if check["status"] != "success":
            return check
        try:
            fn = check["symbol"]
            result = fn(*args, **kwargs)
            return self._result("success", result=result, function="generate_holidays_df")
        except Exception as exc:
            return self._result(
                "error",
                error=f"generate_holidays_df execution failed: {exc}",
                traceback=traceback.format_exc(),
                guidance="Check country codes, year ranges, and optional dependency availability.",
            )

    def call_utf8_to_ascii(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call python.scripts.generate_holidays_file.utf8_to_ascii.

        Parameters:
            *args: Positional arguments for text conversion function.
            **kwargs: Keyword arguments for text conversion function.

        Returns:
            dict: status + converted string or fallback/error payload.
        """
        check = self._require_symbol("utf8_to_ascii")
        if check["status"] != "success":
            return check
        try:
            fn = check["symbol"]
            result = fn(*args, **kwargs)
            return self._result("success", result=result, function="utf8_to_ascii")
        except Exception as exc:
            return self._result(
                "error",
                error=f"utf8_to_ascii execution failed: {exc}",
                traceback=traceback.format_exc(),
                guidance="Provide valid UTF-8 text input or sanitize invalid byte sequences.",
            )