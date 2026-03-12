import os
import sys
import json
import traceback
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for the dedupe repository.

    This adapter tries to import and expose key modules/classes/functions from
    the local source tree (source/dedupe). If import fails, it gracefully falls
    back to "blackbox" mode with actionable guidance.
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Core
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._class_cache: Dict[str, Any] = {}

        self._module_targets = {
            "dedupe": "dedupe",
            "dedupe.api": "dedupe.api",
            "dedupe.blocking": "dedupe.blocking",
            "dedupe.branch_and_bound": "dedupe.branch_and_bound",
            "dedupe.canonical": "dedupe.canonical",
            "dedupe.canopy_index": "dedupe.canopy_index",
            "dedupe.clustering": "dedupe.clustering",
            "dedupe.convenience": "dedupe.convenience",
            "dedupe.core": "dedupe.core",
            "dedupe.datamodel": "dedupe.datamodel",
            "dedupe.index": "dedupe.index",
            "dedupe.labeler": "dedupe.labeler",
            "dedupe.levenshtein": "dedupe.levenshtein",
            "dedupe.predicate_functions": "dedupe.predicate_functions",
            "dedupe.predicates": "dedupe.predicates",
            "dedupe.serializer": "dedupe.serializer",
            "dedupe.tfidf": "dedupe.tfidf",
            "dedupe.training": "dedupe.training",
            "dedupe.variables": "dedupe.variables",
            "dedupe.variables.base": "dedupe.variables.base",
            "dedupe.variables.categorical_type": "dedupe.variables.categorical_type",
            "dedupe.variables.exact": "dedupe.variables.exact",
            "dedupe.variables.exists": "dedupe.variables.exists",
            "dedupe.variables.interaction": "dedupe.variables.interaction",
            "dedupe.variables.latlong": "dedupe.variables.latlong",
            "dedupe.variables.price": "dedupe.variables.price",
            "dedupe.variables.set": "dedupe.variables.set",
            "dedupe.variables.string": "dedupe.variables.string",
        }

        self._safe_import_all()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, hint: Optional[str] = None, exc: Optional[BaseException] = None) -> Dict[str, Any]:
        result = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            result["hint"] = hint
        if exc:
            result["error_type"] = type(exc).__name__
            result["error"] = str(exc)
        return result

    def _safe_import_all(self) -> None:
        for key, module_path in self._module_targets.items():
            try:
                self._modules[key] = importlib.import_module(module_path)
            except Exception as e:
                self._import_errors[key] = f"{type(e).__name__}: {e}"

        if "dedupe" not in self._modules:
            self.mode = "blackbox"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health, import status, and dependency guidance.
        """
        guidance = [
            "Ensure repository source is available at ../source relative to this adapter file.",
            "Install required deps: affinegap, categorical-distance, doublemetaphone, highered, numpy, simplecosine, haversine, BTrees, zope.index, dedupe-Levenshtein-search.",
            "If import still fails, use fallback mode outputs and validate environment compatibility (Python version, compiled wheels).",
        ]
        return self._ok(
            {
                "imported_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "guidance": guidance,
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # Dynamic invocation helpers
    # -------------------------------------------------------------------------
    def _get_module(self, module_key: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        mod = self._modules.get(module_key)
        if mod is None:
            return None, self._err(
                f"Module '{module_key}' is not available.",
                hint="Check dependency installation and source path configuration.",
            )
        return mod, None

    def _call_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module(module_key)
        if err:
            return err
        try:
            fn = getattr(mod, function_name)
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"{module_key}.{function_name} executed")
        except AttributeError as e:
            return self._err(
                f"Function '{function_name}' not found in module '{module_key}'.",
                hint="Use inspect_module() to list available callables.",
                exc=e,
            )
        except Exception as e:
            return self._err(
                f"Failed to execute function '{module_key}.{function_name}'.",
                hint="Validate parameter types and data structure.",
                exc=e,
            )

    def _create_instance(self, module_key: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod, err = self._get_module(module_key)
        if err:
            return err
        try:
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            cache_key = f"{module_key}.{class_name}"
            self._class_cache[cache_key] = instance
            return self._ok(
                {"class_name": class_name, "module": module_key, "cache_key": cache_key, "instance": instance},
                message=f"{module_key}.{class_name} instantiated",
            )
        except AttributeError as e:
            return self._err(
                f"Class '{class_name}' not found in module '{module_key}'.",
                hint="Use inspect_module() to discover available classes.",
                exc=e,
            )
        except Exception as e:
            return self._err(
                f"Failed to instantiate class '{module_key}.{class_name}'.",
                hint="Check constructor arguments and required dependencies.",
                exc=e,
            )

    def inspect_module(self, module_key: str) -> Dict[str, Any]:
        """
        Inspect a loaded module and return discovered classes/functions.
        """
        mod, err = self._get_module(module_key)
        if err:
            return err
        try:
            names = dir(mod)
            classes = []
            functions = []
            for name in names:
                obj = getattr(mod, name, None)
                if obj is None:
                    continue
                if isinstance(obj, type):
                    classes.append(name)
                elif callable(obj):
                    functions.append(name)
            return self._ok(
                {"module": module_key, "classes": sorted(set(classes)), "functions": sorted(set(functions))},
                message="module inspection complete",
            )
        except Exception as e:
            return self._err(
                f"Failed to inspect module '{module_key}'.",
                hint="Confirm module import integrity.",
                exc=e,
            )

    # -------------------------------------------------------------------------
    # Generic public entry points
    # -------------------------------------------------------------------------
    def call(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic function caller for any imported module function.

        Parameters:
        - module_key: Key from adapter module registry (e.g., 'dedupe.core')
        - function_name: Function name in that module
        - *args/**kwargs: Arguments forwarded to the target function
        """
        return self._call_function(module_key, function_name, *args, **kwargs)

    def instantiate(self, module_key: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic class instantiator for any imported module class.

        Parameters:
        - module_key: Key from adapter module registry (e.g., 'dedupe.api')
        - class_name: Class name in that module
        - *args/**kwargs: Constructor arguments
        """
        return self._create_instance(module_key, class_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dedupe API module wrappers
    # -------------------------------------------------------------------------
    def create_dedupe(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.Dedupe."""
        return self._create_instance("dedupe.api", "Dedupe", *args, **kwargs)

    def create_record_link(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.RecordLink."""
        return self._create_instance("dedupe.api", "RecordLink", *args, **kwargs)

    def create_static_dedupe(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.StaticDedupe."""
        return self._create_instance("dedupe.api", "StaticDedupe", *args, **kwargs)

    def create_static_record_link(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.StaticRecordLink."""
        return self._create_instance("dedupe.api", "StaticRecordLink", *args, **kwargs)

    def create_gazetteer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.Gazetteer."""
        return self._create_instance("dedupe.api", "Gazetteer", *args, **kwargs)

    def create_static_gazetteer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.api.StaticGazetteer."""
        return self._create_instance("dedupe.api", "StaticGazetteer", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Convenience function wrappers
    # -------------------------------------------------------------------------
    def convenience_console_label(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call dedupe.convenience.console_label."""
        return self._call_function("dedupe.convenience", "console_label", *args, **kwargs)

    def convenience_canonicalize(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call dedupe.convenience.canonicalize."""
        return self._call_function("dedupe.convenience", "canonicalize", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Serializer wrappers
    # -------------------------------------------------------------------------
    def serializer_read_training(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call dedupe.serializer.read_training."""
        return self._call_function("dedupe.serializer", "read_training", *args, **kwargs)

    def serializer_write_training(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Call dedupe.serializer.write_training."""
        return self._call_function("dedupe.serializer", "write_training", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Variables module class wrappers
    # -------------------------------------------------------------------------
    def create_variable_string(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.string.StringType."""
        return self._create_instance("dedupe.variables.string", "StringType", *args, **kwargs)

    def create_variable_exact(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.exact.ExactType."""
        return self._create_instance("dedupe.variables.exact", "ExactType", *args, **kwargs)

    def create_variable_exists(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.exists.ExistsType."""
        return self._create_instance("dedupe.variables.exists", "ExistsType", *args, **kwargs)

    def create_variable_set(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.set.SetType."""
        return self._create_instance("dedupe.variables.set", "SetType", *args, **kwargs)

    def create_variable_price(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.price.PriceType."""
        return self._create_instance("dedupe.variables.price", "PriceType", *args, **kwargs)

    def create_variable_latlong(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.latlong.LatLongType."""
        return self._create_instance("dedupe.variables.latlong", "LatLongType", *args, **kwargs)

    def create_variable_categorical(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.categorical_type.CategoricalType."""
        return self._create_instance("dedupe.variables.categorical_type", "CategoricalType", *args, **kwargs)

    def create_variable_interaction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Instantiate dedupe.variables.interaction.InteractionType."""
        return self._create_instance("dedupe.variables.interaction", "InteractionType", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Utility and fallback support
    # -------------------------------------------------------------------------
    def list_modules(self) -> Dict[str, Any]:
        """
        List target modules, import status, and errors.
        """
        status = {}
        for k in self._module_targets:
            status[k] = {
                "loaded": k in self._modules,
                "error": self._import_errors.get(k),
            }
        return self._ok({"modules": status}, message="module list generated")

    def fallback_help(self) -> Dict[str, Any]:
        """
        Provide actionable fallback guidance when running in blackbox mode.
        """
        msg = "Adapter is running in fallback mode; import-mode features are limited."
        return self._ok(
            {
                "is_fallback": self.mode != "import",
                "guidance": [
                    "Install missing native dependencies and retry initialization.",
                    "Validate that source path points to the unpacked repository root containing 'dedupe'.",
                    "Run health() and inspect import_errors for exact failure causes.",
                ],
            },
            message=msg,
        )

    def debug_trace(self) -> Dict[str, Any]:
        """
        Return a lightweight debug snapshot for troubleshooting adapter state.
        """
        try:
            snapshot = {
                "mode": self.mode,
                "source_path": source_path,
                "loaded_count": len(self._modules),
                "failed_count": len(self._import_errors),
                "failed_modules": self._import_errors,
            }
            return self._ok({"debug": snapshot}, message="debug snapshot ready")
        except Exception as e:
            return self._err(
                "Failed to generate debug trace.",
                hint="Inspect adapter initialization and environment permissions.",
                exc=e,
            )