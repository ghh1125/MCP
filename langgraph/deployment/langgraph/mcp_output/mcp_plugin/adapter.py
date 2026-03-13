import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for selected modules discovered in repository analysis.

    This adapter attempts direct imports from repository source paths and exposes
    stable wrapper methods with unified status dictionaries.

    Mode:
        - import: primary runtime mode using local source imports.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._errors: List[str] = []
        self._imports: Dict[str, Any] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
            "guidance": guidance,
        }

    def _load_modules(self) -> None:
        """
        Attempt to import all discovered modules/classes/functions using full package paths.
        Any failures are recorded and exposed via get_health().
        """
        targets = {
            "docs.generate_redirects": {
                "functions": ["generate_redirects"],
                "classes": [],
            },
            "libs.langgraph.langgraph.config": {
                "functions": ["get_config", "get_store", "get_stream_writer"],
                "classes": [],
            },
            "libs.langgraph.langgraph.warnings": {
                "functions": [],
                "classes": [
                    "LangGraphDeprecatedSinceV05",
                    "LangGraphDeprecatedSinceV10",
                    "LangGraphDeprecatedSinceV11",
                ],
            },
            "libs.langgraph.langgraph.types": {
                "functions": ["ensure_valid_checkpointer", "interrupt"],
                "classes": ["CacheKey", "CachePolicy", "CheckpointPayload"],
            },
        }

        all_ok = True
        for module_path, spec in targets.items():
            try:
                mod = importlib.import_module(module_path)
                self._imports[module_path] = {"module": mod, "functions": {}, "classes": {}}

                for fn_name in spec["functions"]:
                    fn_obj = getattr(mod, fn_name, None)
                    if callable(fn_obj):
                        self._imports[module_path]["functions"][fn_name] = fn_obj
                    else:
                        all_ok = False
                        self._errors.append(
                            f"Function '{fn_name}' not found in module '{module_path}'."
                        )

                for cls_name in spec["classes"]:
                    cls_obj = getattr(mod, cls_name, None)
                    if cls_obj is not None:
                        self._imports[module_path]["classes"][cls_name] = cls_obj
                    else:
                        all_ok = False
                        self._errors.append(
                            f"Class '{cls_name}' not found in module '{module_path}'."
                        )

            except Exception as exc:
                all_ok = False
                self._errors.append(
                    f"Failed to import module '{module_path}': {exc}. "
                    f"Ensure repository source is available at '{source_path}'."
                )

        self._loaded = all_ok

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def get_health(self) -> Dict[str, Any]:
        """
        Return adapter health including import status and actionable diagnostics.

        Returns:
            dict: Unified status dictionary with loaded modules and errors.
        """
        return self._result(
            status="ok" if self._loaded else "degraded",
            message="Adapter health check completed.",
            data={
                "loaded": self._loaded,
                "modules": list(self._imports.keys()),
                "errors": self._errors,
                "source_path": source_path,
            },
            guidance=(
                None
                if self._loaded
                else "Verify the local repository source layout and module paths, then retry."
            ),
        )

    # -------------------------------------------------------------------------
    # Internal callable resolver
    # -------------------------------------------------------------------------
    def _get_callable(self, module_path: str, kind: str, name: str) -> Any:
        if module_path not in self._imports:
            raise ImportError(f"Module '{module_path}' is not loaded.")
        entry = self._imports[module_path]
        bucket = entry.get(kind, {})
        if name not in bucket:
            raise AttributeError(f"{kind[:-1].capitalize()} '{name}' not available in '{module_path}'.")
        return bucket[name]

    # -------------------------------------------------------------------------
    # docs.generate_redirects module wrappers
    # -------------------------------------------------------------------------
    def call_generate_redirects(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call docs.generate_redirects.generate_redirects.

        Parameters:
            *args: Positional arguments forwarded to generate_redirects.
            **kwargs: Keyword arguments forwarded to generate_redirects.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "docs.generate_redirects"
        fn_name = "generate_redirects"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Called {module_path}.{fn_name} successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Check argument compatibility with the repository version.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # libs.langgraph.langgraph.config module wrappers
    # -------------------------------------------------------------------------
    def call_get_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call libs.langgraph.langgraph.config.get_config.

        Parameters:
            *args: Positional arguments forwarded to get_config.
            **kwargs: Keyword arguments forwarded to get_config.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "libs.langgraph.langgraph.config"
        fn_name = "get_config"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result("ok", f"Called {module_path}.{fn_name} successfully.", {"result": result})
        except Exception as exc:
            return self._result(
                "error",
                f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Validate runtime context and required LangGraph configuration state.",
                data={"traceback": traceback.format_exc()},
            )

    def call_get_store(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call libs.langgraph.langgraph.config.get_store.

        Parameters:
            *args: Positional arguments forwarded to get_store.
            **kwargs: Keyword arguments forwarded to get_store.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "libs.langgraph.langgraph.config"
        fn_name = "get_store"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result("ok", f"Called {module_path}.{fn_name} successfully.", {"result": result})
        except Exception as exc:
            return self._result(
                "error",
                f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Ensure store context exists before invocation.",
                data={"traceback": traceback.format_exc()},
            )

    def call_get_stream_writer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call libs.langgraph.langgraph.config.get_stream_writer.

        Parameters:
            *args: Positional arguments forwarded to get_stream_writer.
            **kwargs: Keyword arguments forwarded to get_stream_writer.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "libs.langgraph.langgraph.config"
        fn_name = "get_stream_writer"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result("ok", f"Called {module_path}.{fn_name} successfully.", {"result": result})
        except Exception as exc:
            return self._result(
                "error",
                f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Ensure stream context is initialized in the current execution scope.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # libs.langgraph.langgraph.types module wrappers
    # -------------------------------------------------------------------------
    def call_ensure_valid_checkpointer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call libs.langgraph.langgraph.types.ensure_valid_checkpointer.

        Parameters:
            *args: Positional arguments forwarded to ensure_valid_checkpointer.
            **kwargs: Keyword arguments forwarded to ensure_valid_checkpointer.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "libs.langgraph.langgraph.types"
        fn_name = "ensure_valid_checkpointer"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result("ok", f"Called {module_path}.{fn_name} successfully.", {"result": result})
        except Exception as exc:
            return self._result(
                "error",
                f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Pass a checkpointer object that matches the expected protocol.",
                data={"traceback": traceback.format_exc()},
            )

    def call_interrupt(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call libs.langgraph.langgraph.types.interrupt.

        Parameters:
            *args: Positional arguments forwarded to interrupt.
            **kwargs: Keyword arguments forwarded to interrupt.

        Returns:
            dict: Unified status dictionary with call result.
        """
        module_path = "libs.langgraph.langgraph.types"
        fn_name = "interrupt"
        try:
            fn = self._get_callable(module_path, "functions", fn_name)
            result = fn(*args, **kwargs)
            return self._result("ok", f"Called {module_path}.{fn_name} successfully.", {"result": result})
        except Exception as exc:
            return self._result(
                "error",
                f"Failed to call {module_path}.{fn_name}.",
                error=str(exc),
                guidance="Check interrupt payload format and runtime graph context.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Class instance constructors (warnings module)
    # -------------------------------------------------------------------------
    def instance_langgraph_deprecated_since_v05(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.warnings.LangGraphDeprecatedSinceV05.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance(
            "libs.langgraph.langgraph.warnings", "LangGraphDeprecatedSinceV05", *args, **kwargs
        )

    def instance_langgraph_deprecated_since_v10(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.warnings.LangGraphDeprecatedSinceV10.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance(
            "libs.langgraph.langgraph.warnings", "LangGraphDeprecatedSinceV10", *args, **kwargs
        )

    def instance_langgraph_deprecated_since_v11(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.warnings.LangGraphDeprecatedSinceV11.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance(
            "libs.langgraph.langgraph.warnings", "LangGraphDeprecatedSinceV11", *args, **kwargs
        )

    # -------------------------------------------------------------------------
    # Class instance constructors (types module)
    # -------------------------------------------------------------------------
    def instance_cache_key(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.types.CacheKey.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance("libs.langgraph.langgraph.types", "CacheKey", *args, **kwargs)

    def instance_cache_policy(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.types.CachePolicy.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance("libs.langgraph.langgraph.types", "CachePolicy", *args, **kwargs)

    def instance_checkpoint_payload(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of libs.langgraph.langgraph.types.CheckpointPayload.

        Parameters:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified status dictionary containing created instance.
        """
        return self._create_instance("libs.langgraph.langgraph.types", "CheckpointPayload", *args, **kwargs)

    def _create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            cls = self._get_callable(module_path, "classes", class_name)
            instance = cls(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Created instance of {module_path}.{class_name} successfully.",
                data={"instance": instance},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to create instance of {module_path}.{class_name}.",
                error=str(exc),
                guidance="Review constructor parameters and repository version compatibility.",
                data={"traceback": traceback.format_exc()},
            )