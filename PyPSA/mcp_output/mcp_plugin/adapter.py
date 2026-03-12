import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for PyPSA repository-backed module loading.

    This adapter prioritizes importing the repository implementation from the local
    `source` directory and provides a graceful fallback response if imports fail.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._available = False
        self._import_errors: List[str] = []

        self.pypsa = None
        self.Network = None
        self.Collection = None
        self.examples = None
        self.option_context = None
        self.get_option = None
        self.set_option = None

        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status, "mode": self.mode}
        data.update(kwargs)
        return data

    def _load_modules(self) -> None:
        try:
            import pypsa  # full package path resolved from source/
            from pypsa import Collection, Network, examples
            from pypsa._options import get_option, option_context, set_option

            self.pypsa = pypsa
            self.Network = Network
            self.Collection = Collection
            self.examples = examples
            self.option_context = option_context
            self.get_option = get_option
            self.set_option = set_option
            self._available = True
        except Exception as exc:
            self._available = False
            self._import_errors.append(str(exc))

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter and import readiness.

        Returns:
            dict: Unified status dictionary with availability and diagnostics.
        """
        if self._available:
            version = getattr(self.pypsa, "__version__", "unknown")
            return self._result(
                "success",
                available=True,
                version=version,
                message="PyPSA modules imported successfully from local source.",
            )
        return self._result(
            "error",
            available=False,
            message="Import mode is unavailable. Verify source path and repository files.",
            errors=self._import_errors,
            actionable_guidance=[
                "Ensure the repository is present under the expected source directory.",
                "Confirm Python version satisfies project requirement (>=3.10).",
                "Install required dependencies: numpy, pandas, scipy, xarray, linopy, deprecation, validators.",
            ],
        )

    # -------------------------------------------------------------------------
    # Core object constructors
    # -------------------------------------------------------------------------
    def create_network(self, import_name: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a PyPSA Network instance.

        Args:
            import_name: Optional network file/path or identifier passed to constructor.
            **kwargs: Additional keyword arguments forwarded to `pypsa.Network`.

        Returns:
            dict: status and created object or error details.
        """
        if not self._available or self.Network is None:
            return self._result(
                "error",
                message="Network creation is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            if import_name is None:
                obj = self.Network(**kwargs)
            else:
                obj = self.Network(import_name=import_name, **kwargs)
            return self._result("success", data=obj)
        except Exception as exc:
            return self._result(
                "error",
                message="Failed to create Network instance.",
                error=str(exc),
                actionable_guidance="Check constructor parameters and data path validity.",
            )

    def create_collection(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a PyPSA Collection instance.

        Args:
            **kwargs: Constructor arguments forwarded to `pypsa.Collection`.

        Returns:
            dict: status and created object or error details.
        """
        if not self._available or self.Collection is None:
            return self._result(
                "error",
                message="Collection creation is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            obj = self.Collection(**kwargs)
            return self._result("success", data=obj)
        except Exception as exc:
            return self._result(
                "error",
                message="Failed to create Collection instance.",
                error=str(exc),
                actionable_guidance="Validate initialization parameters for Collection.",
            )

    # -------------------------------------------------------------------------
    # Options management
    # -------------------------------------------------------------------------
    def get_option_value(self, key: str) -> Dict[str, Any]:
        """
        Retrieve a PyPSA option value.

        Args:
            key: Option key string.

        Returns:
            dict: status with option value or error details.
        """
        if not self._available or self.get_option is None:
            return self._result(
                "error",
                message="Option retrieval is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            value = self.get_option(key)
            return self._result("success", key=key, value=value)
        except Exception as exc:
            return self._result(
                "error",
                message="Failed to retrieve option.",
                error=str(exc),
                actionable_guidance="Use a valid option key defined by PyPSA options.",
            )

    def set_option_value(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Set a PyPSA option value.

        Args:
            key: Option key string.
            value: Value to set.

        Returns:
            dict: status with confirmation or error details.
        """
        if not self._available or self.set_option is None:
            return self._result(
                "error",
                message="Option update is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            self.set_option(key, value)
            return self._result("success", key=key, value=value)
        except Exception as exc:
            return self._result(
                "error",
                message="Failed to set option.",
                error=str(exc),
                actionable_guidance="Verify option key and value type compatibility.",
            )

    # -------------------------------------------------------------------------
    # Examples module access
    # -------------------------------------------------------------------------
    def call_examples_attr(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a callable attribute from `pypsa.examples` dynamically.

        Args:
            name: Function/attribute name in `pypsa.examples`.
            *args: Positional arguments to pass if callable.
            **kwargs: Keyword arguments to pass if callable.

        Returns:
            dict: status with returned data or error details.
        """
        if not self._available or self.examples is None:
            return self._result(
                "error",
                message="Examples access is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            attr = getattr(self.examples, name)
            if callable(attr):
                out = attr(*args, **kwargs)
                return self._result("success", name=name, data=out)
            return self._result("success", name=name, data=attr)
        except AttributeError:
            return self._result(
                "error",
                message=f"Attribute '{name}' does not exist in pypsa.examples.",
                actionable_guidance="Inspect pypsa.examples for available members.",
            )
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to execute pypsa.examples attribute '{name}'.",
                error=str(exc),
            )

    # -------------------------------------------------------------------------
    # Generic module call utilities
    # -------------------------------------------------------------------------
    def call_pypsa_function(self, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically call a callable exposed at top-level `pypsa`.

        Args:
            func_name: Function name on the `pypsa` module.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: status with call result or error details.
        """
        if not self._available or self.pypsa is None:
            return self._result(
                "error",
                message="Top-level call is unavailable because imports failed.",
                errors=self._import_errors,
            )
        try:
            target = getattr(self.pypsa, func_name)
            if not callable(target):
                return self._result(
                    "error",
                    message=f"Attribute '{func_name}' is not callable.",
                    actionable_guidance="Use a valid callable symbol from pypsa.",
                )
            result = target(*args, **kwargs)
            return self._result("success", function=func_name, data=result)
        except AttributeError:
            return self._result(
                "error",
                message=f"Function '{func_name}' not found in pypsa.",
                actionable_guidance="Check pypsa.__init__ exports for available names.",
            )
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to execute function '{func_name}'.",
                error=str(exc),
            )