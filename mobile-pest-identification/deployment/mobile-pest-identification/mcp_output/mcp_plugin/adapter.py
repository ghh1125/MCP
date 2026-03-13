import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for mobile-pest-identification.

    This adapter attempts to import project internals directly from the bundled source tree.
    If imports fail, it switches to a graceful fallback mode and returns actionable guidance.

    Unified response schema:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "fallback",
        "message": str,
        "data": Any,
        "error": Optional[str],
        "traceback": Optional[str]
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Initialization
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._imports_ready = False
        self._import_errors = []

        self._utils_module = None
        self._Detector = None
        self._PestDetector = None
        self._asklr = None
        self._custom_split = None

        self._load_imports()

    def _result(
        self,
        status: str,
        message: str,
        data: Any = None,
        error: Optional[str] = None,
        tb: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
            "error": error,
            "traceback": tb,
        }

    def _load_imports(self) -> None:
        try:
            # Full module path based on analysis: deployment.mobile-pest-identification.source.src.utils
            # Python module names cannot contain hyphens, so we attempt robust alternatives.
            candidates = [
                "deployment.mobile-pest-identification.source.src.utils",
                "deployment.mobile_pest_identification.source.src.utils",
                "src.utils",
            ]

            module = None
            last_exc = None
            for path in candidates:
                try:
                    module = importlib.import_module(path)
                    break
                except Exception as exc:
                    last_exc = exc
                    self._import_errors.append(f"Failed import: {path} -> {exc}")

            if module is None:
                raise ImportError(
                    "Could not import utils module from repository source. "
                    "Tried: " + ", ".join(candidates)
                ) from last_exc

            self._utils_module = module
            self._Detector = getattr(module, "Detector", None)
            self._PestDetector = getattr(module, "PestDetector", None)
            self._asklr = getattr(module, "asklr", None)
            self._custom_split = getattr(module, "custom_split", None)

            missing = []
            for name, obj in [
                ("Detector", self._Detector),
                ("PestDetector", self._PestDetector),
                ("asklr", self._asklr),
                ("custom_split", self._custom_split),
            ]:
                if obj is None:
                    missing.append(name)

            if missing:
                raise AttributeError(
                    f"Imported module but missing expected symbols: {', '.join(missing)}"
                )

            self._imports_ready = True
            self.mode = "import"
        except Exception as exc:
            self._imports_ready = False
            self.mode = "fallback"
            self._import_errors.append(str(exc))

    # -------------------------------------------------------------------------
    # Health / Status
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter readiness and diagnostic details.

        Returns:
            Dict[str, Any]: Unified status dictionary with import state and actionable guidance.
        """
        if self._imports_ready:
            return self._result(
                status="success",
                message="Adapter is ready in import mode.",
                data={
                    "imports_ready": True,
                    "available_symbols": [
                        "Detector",
                        "PestDetector",
                        "asklr",
                        "custom_split",
                    ],
                    "source_path": source_path,
                },
            )

        return self._result(
            status="fallback",
            message=(
                "Adapter is running in fallback mode because direct imports failed. "
                "Verify repository layout and Python dependencies from requirements.txt."
            ),
            data={
                "imports_ready": False,
                "source_path": source_path,
                "import_errors": self._import_errors,
                "guidance": [
                    "Ensure source/src/utils.py exists.",
                    "Install dependencies listed in requirements.txt.",
                    "Confirm runtime Python can access the source path.",
                ],
            },
            error="Import initialization failed.",
        )

    # -------------------------------------------------------------------------
    # Class Instance Methods
    # -------------------------------------------------------------------------
    def create_detector(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of Detector from src.utils.

        Parameters:
            *args: Positional arguments forwarded to Detector constructor.
            **kwargs: Keyword arguments forwarded to Detector constructor.

        Returns:
            Dict[str, Any]: Unified status dictionary with detector instance in data["instance"].
        """
        if not self._imports_ready:
            return self._result(
                status="fallback",
                message=(
                    "Detector is unavailable in fallback mode. "
                    "Resolve import issues and retry."
                ),
                data={"args": args, "kwargs": kwargs},
                error="Detector import not available.",
            )

        try:
            instance = self._Detector(*args, **kwargs)
            return self._result(
                status="success",
                message="Detector instance created successfully.",
                data={"instance": instance, "class": "Detector"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create Detector instance.",
                error=str(exc),
                tb=traceback.format_exc(),
            )

    def create_pest_detector(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of PestDetector from src.utils.

        Parameters:
            *args: Positional arguments forwarded to PestDetector constructor.
            **kwargs: Keyword arguments forwarded to PestDetector constructor.

        Returns:
            Dict[str, Any]: Unified status dictionary with pest detector instance in data["instance"].
        """
        if not self._imports_ready:
            return self._result(
                status="fallback",
                message=(
                    "PestDetector is unavailable in fallback mode. "
                    "Resolve import issues and retry."
                ),
                data={"args": args, "kwargs": kwargs},
                error="PestDetector import not available.",
            )

        try:
            instance = self._PestDetector(*args, **kwargs)
            return self._result(
                status="success",
                message="PestDetector instance created successfully.",
                data={"instance": instance, "class": "PestDetector"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="Failed to create PestDetector instance.",
                error=str(exc),
                tb=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Function Call Methods
    # -------------------------------------------------------------------------
    def call_asklr(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call asklr function from src.utils.

        Parameters:
            *args: Positional arguments for asklr.
            **kwargs: Keyword arguments for asklr.

        Returns:
            Dict[str, Any]: Unified status dictionary with function return value in data["result"].
        """
        if not self._imports_ready:
            return self._result(
                status="fallback",
                message=(
                    "asklr is unavailable in fallback mode. "
                    "Resolve import issues and verify dependencies before retrying."
                ),
                data={"args": args, "kwargs": kwargs},
                error="asklr import not available.",
            )

        try:
            result = self._asklr(*args, **kwargs)
            return self._result(
                status="success",
                message="asklr executed successfully.",
                data={"result": result, "function": "asklr"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="asklr execution failed.",
                error=str(exc),
                tb=traceback.format_exc(),
            )

    def call_custom_split(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call custom_split function from src.utils.

        Parameters:
            *args: Positional arguments for custom_split.
            **kwargs: Keyword arguments for custom_split.

        Returns:
            Dict[str, Any]: Unified status dictionary with function return value in data["result"].
        """
        if not self._imports_ready:
            return self._result(
                status="fallback",
                message=(
                    "custom_split is unavailable in fallback mode. "
                    "Resolve import issues and verify dataset paths before retrying."
                ),
                data={"args": args, "kwargs": kwargs},
                error="custom_split import not available.",
            )

        try:
            result = self._custom_split(*args, **kwargs)
            return self._result(
                status="success",
                message="custom_split executed successfully.",
                data={"result": result, "function": "custom_split"},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="custom_split execution failed.",
                error=str(exc),
                tb=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Generic Dispatcher
    # -------------------------------------------------------------------------
    def invoke(self, operation: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic dispatcher for adapter operations.

        Supported operations:
            - "health_check"
            - "create_detector"
            - "create_pest_detector"
            - "call_asklr"
            - "call_custom_split"

        Parameters:
            operation (str): Operation name.
            *args: Positional args forwarded to target method.
            **kwargs: Keyword args forwarded to target method.

        Returns:
            Dict[str, Any]: Unified status dictionary.
        """
        routing = {
            "health_check": self.health_check,
            "create_detector": self.create_detector,
            "create_pest_detector": self.create_pest_detector,
            "call_asklr": self.call_asklr,
            "call_custom_split": self.call_custom_split,
        }

        fn = routing.get(operation)
        if fn is None:
            return self._result(
                status="error",
                message="Unknown operation.",
                error=(
                    f"Operation '{operation}' is not supported. "
                    f"Supported operations: {', '.join(routing.keys())}"
                ),
            )

        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            return self._result(
                status="error",
                message="Operation failed unexpectedly.",
                error=str(exc),
                tb=traceback.format_exc(),
            )