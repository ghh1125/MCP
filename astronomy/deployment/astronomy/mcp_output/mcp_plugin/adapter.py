import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for cosinekitty/astronomy repository.

    This adapter attempts direct imports from repository-local modules discovered by analysis.
    It exposes:
    - Dedicated "instance_*" methods for discovered classes.
    - Dedicated "call_*" methods for discovered functions.
    - Unified return dictionaries with a `status` field.
    - Graceful fallback behavior when imports are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules = {}
        self._import_errors = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "ok", "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _error(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        payload.update(kwargs)
        return payload

    def _fallback(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": "fallback", "mode": self.mode, "message": message}
        payload.update(kwargs)
        return payload

    def _load_modules(self) -> None:
        targets = [
            "generate.patch_readme",
            "generate.patch_version_numbers",
            "generate.checksum",
            "generate.check_internal_links",
            "generate.test",
        ]
        for mod in targets:
            try:
                self._modules[mod] = importlib.import_module(mod)
            except Exception as ex:
                self._import_errors[mod] = f"{type(ex).__name__}: {ex}"

    def _get_attr(self, module_name: str, attr_name: str) -> Tuple[Optional[Any], Optional[str]]:
        mod = self._modules.get(module_name)
        if mod is None:
            err = self._import_errors.get(
                module_name,
                f"Module '{module_name}' is not loaded. Ensure repository source path is correct.",
            )
            return None, err
        if not hasattr(mod, attr_name):
            return None, (
                f"Attribute '{attr_name}' not found in '{module_name}'. "
                "Verify repository version compatibility."
            )
        return getattr(mod, attr_name), None

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter import status and discovered module availability.
        """
        return self._ok(
            loaded_modules=sorted(self._modules.keys()),
            import_errors=self._import_errors,
            source_path=source_path,
        )

    # -------------------------------------------------------------------------
    # Class instance methods (discovered classes in generate.test)
    # -------------------------------------------------------------------------
    def instance_bary_state_func(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of generate.test.BaryStateFunc.

        Parameters:
        - *args: Positional arguments forwarded to the class constructor.
        - **kwargs: Keyword arguments forwarded to the class constructor.

        Returns:
        - dict: Unified status payload with created instance on success.
        """
        cls, err = self._get_attr("generate.test", "BaryStateFunc")
        if err:
            return self._fallback(
                f"Cannot instantiate BaryStateFunc: {err}. "
                "Run in repository root and ensure 'generate/test.py' is importable."
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(class_name="BaryStateFunc", instance=instance)
        except Exception as ex:
            return self._error(
                "Failed to instantiate BaryStateFunc.",
                exception=f"{type(ex).__name__}: {ex}",
                traceback=traceback.format_exc(),
            )

    def instance_helio_state_func(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of generate.test.HelioStateFunc.

        Parameters:
        - *args: Positional arguments forwarded to the class constructor.
        - **kwargs: Keyword arguments forwarded to the class constructor.

        Returns:
        - dict: Unified status payload with created instance on success.
        """
        cls, err = self._get_attr("generate.test", "HelioStateFunc")
        if err:
            return self._fallback(
                f"Cannot instantiate HelioStateFunc: {err}. "
                "Check local source checkout and import path configuration."
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(class_name="HelioStateFunc", instance=instance)
        except Exception as ex:
            return self._error(
                "Failed to instantiate HelioStateFunc.",
                exception=f"{type(ex).__name__}: {ex}",
                traceback=traceback.format_exc(),
            )

    def instance_jpl_state_record(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of generate.test.JplStateRecord.

        Parameters:
        - *args: Positional arguments forwarded to the class constructor.
        - **kwargs: Keyword arguments forwarded to the class constructor.

        Returns:
        - dict: Unified status payload with created instance on success.
        """
        cls, err = self._get_attr("generate.test", "JplStateRecord")
        if err:
            return self._fallback(
                f"Cannot instantiate JplStateRecord: {err}. "
                "Ensure repository files are present and unchanged."
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(class_name="JplStateRecord", instance=instance)
        except Exception as ex:
            return self._error(
                "Failed to instantiate JplStateRecord.",
                exception=f"{type(ex).__name__}: {ex}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Function call methods (discovered core functions)
    # -------------------------------------------------------------------------
    def call_patch_readme(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.patch_readme", "PatchReadme")
        if err:
            return self._fallback(f"Cannot call PatchReadme: {err}")
        return self._safe_call(func, "PatchReadme", args, kwargs)

    def call_patch(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.patch_version_numbers", "Patch")
        if err:
            return self._fallback(f"Cannot call Patch: {err}")
        return self._safe_call(func, "Patch", args, kwargs)

    def call_patch_version_numbers(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.patch_version_numbers", "PatchVersionNumbers")
        if err:
            return self._fallback(f"Cannot call PatchVersionNumbers: {err}")
        return self._safe_call(func, "PatchVersionNumbers", args, kwargs)

    def call_checksum(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.checksum", "Checksum")
        if err:
            return self._fallback(f"Cannot call Checksum: {err}")
        return self._safe_call(func, "Checksum", args, kwargs)

    def call_find_bogus_links(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.check_internal_links", "FindBogusLinks")
        if err:
            return self._fallback(f"Cannot call FindBogusLinks: {err}")
        return self._safe_call(func, "FindBogusLinks", args, kwargs)

    def call_find_broken_links(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.check_internal_links", "FindBrokenLinks")
        if err:
            return self._fallback(f"Cannot call FindBrokenLinks: {err}")
        return self._safe_call(func, "FindBrokenLinks", args, kwargs)

    def call_aberration(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.test", "Aberration")
        if err:
            return self._fallback(f"Cannot call Aberration: {err}")
        return self._safe_call(func, "Aberration", args, kwargs)

    def call_angle_diff(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.test", "AngleDiff")
        if err:
            return self._fallback(f"Cannot call AngleDiff: {err}")
        return self._safe_call(func, "AngleDiff", args, kwargs)

    def call_arcmin_pos_error(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        func, err = self._get_attr("generate.test", "ArcminPosError")
        if err:
            return self._fallback(f"Cannot call ArcminPosError: {err}")
        return self._safe_call(func, "ArcminPosError", args, kwargs)

    # -------------------------------------------------------------------------
    # Generic invocation utilities
    # -------------------------------------------------------------------------
    def _safe_call(self, func: Any, name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return self._ok(function=name, result=result)
        except TypeError as ex:
            sig = None
            try:
                sig = str(inspect.signature(func))
            except Exception:
                sig = "Unavailable"
            return self._error(
                f"Invalid arguments for {name}.",
                exception=f"{type(ex).__name__}: {ex}",
                expected_signature=sig,
                guidance="Check parameter count/types and retry with matching arguments.",
            )
        except Exception as ex:
            return self._error(
                f"Execution failed for {name}.",
                exception=f"{type(ex).__name__}: {ex}",
                traceback=traceback.format_exc(),
            )