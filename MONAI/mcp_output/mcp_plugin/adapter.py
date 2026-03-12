import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for MONAI repository integration.

    This adapter prioritizes direct Python imports from the local `source` path and
    provides CLI fallback hints when imports are unavailable. All public methods
    return a unified dictionary with at least a `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _safe_import(self, key: str, module_path: str, attr_name: Optional[str] = None) -> None:
        try:
            module = __import__(module_path, fromlist=[attr_name] if attr_name else [])
            self._imports[key] = getattr(module, attr_name) if attr_name else module
        except Exception as exc:
            self._errors[key] = (
                f"Failed to import '{module_path}'"
                + (f".'{attr_name}'" if attr_name else "")
                + f": {exc}. Ensure repository source is present at '{source_path}' and dependencies are installed."
            )

    def _initialize_imports(self) -> None:
        self._safe_import("bundle_main", "monai.bundle.__main__")
        self._safe_import("auto3dseg_main", "monai.apps.auto3dseg.__main__")
        self._safe_import("nnunet_main", "monai.apps.nnunet.__main__")

    def _get_import(self, key: str) -> Dict[str, Any]:
        if key in self._imports:
            return self._result("success", object=self._imports[key], mode=self.mode)
        return self._result(
            "error",
            mode=self.mode,
            message=self._errors.get(
                key,
                f"Import key '{key}' is not available. Verify source path and optional dependencies.",
            ),
            fallback="Use CLI entrypoints if imports are unavailable.",
        )

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and imported module availability.

        Returns:
            Dict[str, Any]:
                {
                    "status": "success" | "partial" | "error",
                    "mode": "import",
                    "available": [...],
                    "failed": {...},
                    "guidance": str
                }
        """
        available = sorted(self._imports.keys())
        failed = dict(self._errors)
        if available and not failed:
            status = "success"
        elif available and failed:
            status = "partial"
        else:
            status = "error"
        return self._result(
            status,
            mode=self.mode,
            available=available,
            failed=failed,
            guidance=(
                "Install required dependencies (python>=3.9, torch, numpy) and optional MONAI extras "
                "if specific modules fail."
            ),
        )

    # -------------------------------------------------------------------------
    # Module accessors (instance methods for identified modules/classes scope)
    # -------------------------------------------------------------------------
    def get_bundle_main_module(self) -> Dict[str, Any]:
        """
        Get imported module object for MONAI Bundle CLI entrypoint.

        Returns:
            Dict[str, Any]:
                status plus module object under `object` if available.
        """
        return self._get_import("bundle_main")

    def get_auto3dseg_main_module(self) -> Dict[str, Any]:
        """
        Get imported module object for MONAI Auto3DSeg CLI entrypoint.

        Returns:
            Dict[str, Any]:
                status plus module object under `object` if available.
        """
        return self._get_import("auto3dseg_main")

    def get_nnunet_main_module(self) -> Dict[str, Any]:
        """
        Get imported module object for MONAI nnUNet CLI entrypoint.

        Returns:
            Dict[str, Any]:
                status plus module object under `object` if available.
        """
        return self._get_import("nnunet_main")

    # -------------------------------------------------------------------------
    # CLI-aligned call methods (function-equivalent wrappers)
    # -------------------------------------------------------------------------
    def call_bundle_cli(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute MONAI Bundle CLI via imported module when possible.

        Parameters:
            args (Optional[list]): Command-line style arguments. If None, defaults to [].

        Returns:
            Dict[str, Any]:
                Unified status dictionary with execution result or actionable fallback guidance.
        """
        args = args or []
        mod_res = self._get_import("bundle_main")
        if mod_res["status"] != "success":
            return self._result(
                "error",
                mode=self.mode,
                message=mod_res["message"],
                fallback="Run manually: python -m monai.bundle <args>",
            )
        try:
            module = mod_res["object"]
            if hasattr(module, "main") and callable(module.main):
                rc = module.main(args)
                return self._result("success", mode=self.mode, return_code=rc, entrypoint="python -m monai.bundle")
            return self._result(
                "error",
                mode=self.mode,
                message="Imported module does not expose a callable 'main(args)'.",
                fallback="Run manually: python -m monai.bundle <args>",
            )
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Bundle CLI execution failed: {exc}. Check argument syntax and required runtime dependencies.",
                fallback="Run manually: python -m monai.bundle <args>",
            )

    def call_auto3dseg_cli(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute MONAI Auto3DSeg CLI via imported module when possible.

        Parameters:
            args (Optional[list]): Command-line style arguments. If None, defaults to [].

        Returns:
            Dict[str, Any]:
                Unified status dictionary with execution result or fallback guidance.
        """
        args = args or []
        mod_res = self._get_import("auto3dseg_main")
        if mod_res["status"] != "success":
            return self._result(
                "error",
                mode=self.mode,
                message=mod_res["message"],
                fallback="Run manually: python -m monai.apps.auto3dseg <args>",
            )
        try:
            module = mod_res["object"]
            if hasattr(module, "main") and callable(module.main):
                rc = module.main(args)
                return self._result(
                    "success",
                    mode=self.mode,
                    return_code=rc,
                    entrypoint="python -m monai.apps.auto3dseg",
                )
            return self._result(
                "error",
                mode=self.mode,
                message="Imported module does not expose a callable 'main(args)'.",
                fallback="Run manually: python -m monai.apps.auto3dseg <args>",
            )
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                message=f"Auto3DSeg CLI execution failed: {exc}. Validate dataset/config paths and dependencies.",
                fallback="Run manually: python -m monai.apps.auto3dseg <args>",
            )

    def call_nnunet_cli(self, args: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute MONAI nnUNet CLI via imported module when possible.

        Parameters:
            args (Optional[list]): Command-line style arguments. If None, defaults to [].

        Returns:
            Dict[str, Any]:
                Unified status dictionary with execution result or fallback guidance.
        """
        args = args or []
        mod_res = self._get_import("nnunet_main")
        if mod_res["status"] != "success":
            return self._result(
                "error",
                mode=self.mode,
                message=mod_res["message"],
                fallback="Run manually: python -m monai.apps.nnunet <args>",
            )
        try:
            module = mod_res["object"]
            if hasattr(module, "main") and callable(module.main):
                rc = module.main(args)
                return self._result(
                    "success",
                    mode=self.mode,
                    return_code=rc,
                    entrypoint="python -m monai.apps.nnunet",
                )
            return self._result(
                "error",
                mode=self.mode,
                message="Imported module does not expose a callable 'main(args)'.",
                fallback="Run manually: python -m monai.apps.nnunet <args>",
            )
        except Exception as exc:
            return self._result(
                "error",
                mode=self.mode,
                message=f"nnUNet CLI execution failed: {exc}. Confirm nnUNet configuration and dependencies.",
                fallback="Run manually: python -m monai.apps.nnunet <args>",
            )