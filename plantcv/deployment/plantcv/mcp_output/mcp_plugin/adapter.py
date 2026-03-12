import os
import sys
import importlib
from typing import Any, Callable, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the PlantCV repository.

    This adapter prefers direct Python imports and provides graceful fallback
    guidance to CLI entry points when imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._load_state: Dict[str, bool] = {}
        self._initialize_modules()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        out = {"status": status}
        out.update(kwargs)
        return out

    def _initialize_modules(self) -> None:
        module_names = {
            "parallel_cli": "plantcv.parallel.cli",
            "learn_cli": "plantcv.learn.cli",
            "utils_cli": "plantcv.utils.cli",
        }
        for key, mod_name in module_names.items():
            try:
                self._modules[key] = importlib.import_module(mod_name)
                self._load_state[key] = True
            except Exception:
                self._modules[key] = None
                self._load_state[key] = False

    def _call(
        self,
        module_key: str,
        attr_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                "fallback",
                mode=self.mode,
                message=(
                    f"Import failed for module '{module_key}'. "
                    f"Install repository dependencies and retry. "
                    f"You may run the corresponding CLI command as fallback."
                ),
                actionable_guidance=[
                    "Ensure source path is correct and contains the repository code.",
                    "Install required dependencies such as numpy, opencv-python, scikit-image, scipy, matplotlib, pandas.",
                    "Use the CLI entry point for this feature if import mode is unavailable.",
                ],
            )

        fn: Optional[Callable[..., Any]] = getattr(mod, attr_name, None)
        if fn is None:
            return self._result(
                "error",
                mode=self.mode,
                message=(
                    f"Function '{attr_name}' was not found in module '{mod.__name__}'. "
                    f"Check repository version compatibility."
                ),
            )

        try:
            value = fn(*args, **kwargs)
            return self._result(
                "success",
                mode=self.mode,
                module=mod.__name__,
                function=attr_name,
                result=value,
            )
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                module=mod.__name__,
                function=attr_name,
                message=(
                    "Function execution failed. Verify input arguments and dependency setup."
                ),
                error=str(exc),
            )

    # ---------------------------------------------------------------------
    # Health / capability
    # ---------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter readiness and module import state.
        """
        ready = any(self._load_state.values())
        return self._result(
            "success" if ready else "fallback",
            mode=self.mode,
            imports=self._load_state,
            message=(
                "At least one module is importable."
                if ready
                else "No target modules could be imported. Use CLI fallback."
            ),
            cli_fallbacks=[
                "plantcv.parallel.cli:main",
                "plantcv.learn.cli:main",
                "plantcv.utils.cli:main",
            ],
        )

    # ---------------------------------------------------------------------
    # plantcv.parallel.cli
    # ---------------------------------------------------------------------
    def call_parallel_cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call plantcv.parallel.cli.main.

        Parameters:
            argv: Optional CLI-style argument list. If the upstream function
                  does not accept parameters, call without argv.

        Returns:
            Unified status dictionary.
        """
        if argv is None:
            return self._call("parallel_cli", "main")
        try:
            return self._call("parallel_cli", "main", argv)
        except Exception:
            return self._call("parallel_cli", "main")

    # ---------------------------------------------------------------------
    # plantcv.learn.cli
    # ---------------------------------------------------------------------
    def call_learn_cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call plantcv.learn.cli.main.

        Parameters:
            argv: Optional CLI-style argument list.

        Returns:
            Unified status dictionary.
        """
        if argv is None:
            return self._call("learn_cli", "main")
        try:
            return self._call("learn_cli", "main", argv)
        except Exception:
            return self._call("learn_cli", "main")

    # ---------------------------------------------------------------------
    # plantcv.utils.cli
    # ---------------------------------------------------------------------
    def call_utils_cli_main(self, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Call plantcv.utils.cli.main.

        Parameters:
            argv: Optional CLI-style argument list.

        Returns:
            Unified status dictionary.
        """
        if argv is None:
            return self._call("utils_cli", "main")
        try:
            return self._call("utils_cli", "main", argv)
        except Exception:
            return self._call("utils_cli", "main")