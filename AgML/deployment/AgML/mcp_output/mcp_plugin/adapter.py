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
    Import-mode MCP adapter for AgML.

    This adapter is designed for low-intrusion integration:
    - Prefers direct imports from repository source.
    - Uses lazy imports for heavy/optional dependencies.
    - Returns unified dictionary responses with `status`.
    - Provides graceful fallback guidance when import/runtime failures occur.
    """

    # =========================================================================
    # Initialization and module registry
    # =========================================================================

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._register_core_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, error: Optional[Exception] = None, hint: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc(limit=3)
        if hint:
            payload["hint"] = hint
        return payload

    def _safe_import(self, module_path: str, alias: Optional[str] = None) -> None:
        key = alias or module_path
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as e:
            self._import_errors[key] = str(e)

    def _register_core_modules(self) -> None:
        # Core high-value modules (per analysis: metadata/data-loader first).
        module_paths = [
            "agml",
            "agml.data.public",
            "agml.data.metadata",
            "agml.data.loader",
            "agml.data.multi_loader",
            "agml.data.builder",
            "agml.data.exporters.yolo",
            "agml.data.exporters.tensorflow",
            "agml.models",
            "agml.models.benchmarks",
            "agml.viz",
            "agml.utils.downloads",
            "agml.utils.io",
            "agml.backend.config",
        ]
        for p in module_paths:
            self._safe_import(p)

    # =========================================================================
    # Adapter health and environment
    # =========================================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and import health.

        Returns:
            dict: Unified status payload with loaded modules and import failures.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            message="Adapter initialized.",
        )

    def get_import_strategy(self) -> Dict[str, Any]:
        """
        Return import strategy details inferred from analysis.

        Returns:
            dict: Strategy metadata and operational guardrails.
        """
        return self._ok(
            {
                "primary": "import",
                "fallback": "blackbox",
                "guardrails": [
                    "Lazy-import heavy optional dependencies.",
                    "Read-only default for metadata operations.",
                    "Explicit opt-in for write/network operations.",
                    "Structured error reporting for missing dependencies.",
                ],
            }
        )

    # =========================================================================
    # Dataset discovery and metadata (Phase 1)
    # =========================================================================

    def list_public_datasets(self) -> Dict[str, Any]:
        """
        List public datasets exposed by AgML.

        Returns:
            dict: status + datasets list (if available).
        """
        try:
            m = self._modules.get("agml.data.public")
            if m is None:
                self._safe_import("agml.data.public")
                m = self._modules.get("agml.data.public")
            if m is None:
                return self._err(
                    "Could not import agml.data.public.",
                    hint="Verify repository source path and optional dependencies.",
                )

            candidates = ["public_data_sources", "list_datasets", "list_public_datasets"]
            for name in candidates:
                fn = getattr(m, name, None)
                if callable(fn):
                    return self._ok({"datasets": fn()}, message=f"Datasets loaded via {name}.")
            return self._err(
                "No known dataset-listing function found in agml.data.public.",
                hint="Check AgML version compatibility and available API symbols.",
            )
        except Exception as e:
            return self._err("Failed to list public datasets.", e)

    def get_dataset_metadata(self, dataset_name: str) -> Dict[str, Any]:
        """
        Fetch metadata for a single dataset.

        Args:
            dataset_name (str): Dataset identifier.

        Returns:
            dict: status + metadata details.
        """
        try:
            m = self._modules.get("agml.data.metadata")
            if m is None:
                self._safe_import("agml.data.metadata")
                m = self._modules.get("agml.data.metadata")
            if m is None:
                return self._err(
                    "Could not import agml.data.metadata.",
                    hint="Ensure source code is present and importable.",
                )

            candidates = ["DatasetMetadata", "get_dataset_metadata", "load_dataset_metadata"]
            cls = getattr(m, "DatasetMetadata", None)
            if cls is not None:
                obj = cls(dataset_name)
                meta = {}
                for attr in ["name", "num_images", "ml_task", "classes", "location", "citation"]:
                    if hasattr(obj, attr):
                        meta[attr] = getattr(obj, attr)
                meta["repr"] = repr(obj)
                return self._ok({"dataset_name": dataset_name, "metadata": meta}, "Metadata loaded via DatasetMetadata.")

            for name in candidates[1:]:
                fn = getattr(m, name, None)
                if callable(fn):
                    return self._ok({"dataset_name": dataset_name, "metadata": fn(dataset_name)}, f"Metadata loaded via {name}.")

            return self._err(
                "No supported metadata accessor was found.",
                hint="Inspect agml.data.metadata for API changes.",
            )
        except Exception as e:
            return self._err("Failed to retrieve dataset metadata.", e)

    def validate_dataset_name(self, dataset_name: str) -> Dict[str, Any]:
        """
        Validate whether a dataset name exists in AgML public datasets.

        Args:
            dataset_name (str): Candidate dataset name.

        Returns:
            dict: status + validity result.
        """
        listed = self.list_public_datasets()
        if listed.get("status") != "success":
            return listed
        datasets = listed.get("datasets", [])
        is_valid = dataset_name in datasets if isinstance(datasets, list) else False
        return self._ok(
            {"dataset_name": dataset_name, "is_valid": is_valid},
            "Validation complete.",
        )

    def show_dataset_splits(self, dataset_name: str) -> Dict[str, Any]:
        """
        Show split information (if available) for a dataset.

        Args:
            dataset_name (str): Dataset identifier.

        Returns:
            dict: status + split summary.
        """
        try:
            meta_result = self.get_dataset_metadata(dataset_name)
            if meta_result.get("status") != "success":
                return meta_result
            metadata = meta_result.get("metadata", {})
            split_keys = ["splits", "train", "val", "test", "num_train", "num_val", "num_test"]
            split_summary = {k: metadata.get(k) for k in split_keys if k in metadata}
            return self._ok({"dataset_name": dataset_name, "splits": split_summary}, "Split summary generated.")
        except Exception as e:
            return self._err("Failed to show dataset splits.", e)

    # =========================================================================
    # Loader and export operations (Phase 2)
    # =========================================================================

    def instantiate_loader(self, dataset_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate an AgML data loader for a dataset.

        Args:
            dataset_name (str): Dataset identifier.
            **kwargs: Additional loader constructor options.

        Returns:
            dict: status + lightweight loader summary.
        """
        try:
            m = self._modules.get("agml.data.loader")
            if m is None:
                self._safe_import("agml.data.loader")
                m = self._modules.get("agml.data.loader")
            if m is None:
                return self._err(
                    "Could not import agml.data.loader.",
                    hint="Verify source import path and required dependencies.",
                )

            cls = getattr(m, "AgMLDataLoader", None)
            if cls is None:
                return self._err(
                    "AgMLDataLoader class not found.",
                    hint="Check AgML version and loader API naming.",
                )

            loader = cls(dataset_name, **kwargs)
            summary = {"type": type(loader).__name__, "dataset_name": dataset_name, "repr": repr(loader)}
            return self._ok({"loader_summary": summary}, "Loader instantiated.")
        except Exception as e:
            return self._err("Failed to instantiate loader.", e)

    def sample_batch_summary(self, dataset_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Build a dataset loader and summarize one sample/batch.

        Args:
            dataset_name (str): Dataset identifier.
            **kwargs: Loader options.

        Returns:
            dict: status + sample structure summary.
        """
        try:
            inst = self.instantiate_loader(dataset_name, **kwargs)
            if inst.get("status") != "success":
                return inst

            m = self._modules.get("agml.data.loader")
            cls = getattr(m, "AgMLDataLoader", None)
            loader = cls(dataset_name, **kwargs)

            try:
                sample = next(iter(loader))
            except Exception:
                sample = None

            return self._ok(
                {
                    "dataset_name": dataset_name,
                    "sample_type": type(sample).__name__ if sample is not None else "None",
                    "sample_repr": repr(sample)[:1000] if sample is not None else None,
                },
                "Batch/sample summary generated.",
            )
        except Exception as e:
            return self._err("Failed to summarize sample batch.", e)

    def export_dataset_format(self, dataset_name: str, export_format: str, output_dir: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Export dataset to a target format where available.

        Args:
            dataset_name (str): Dataset identifier.
            export_format (str): Target format, e.g. 'yolo' or 'tensorflow'.
            output_dir (str): Destination directory path.
            **kwargs: Export-specific options.

        Returns:
            dict: status + export operation details.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            export_format = export_format.strip().lower()

            if export_format == "yolo":
                m = self._modules.get("agml.data.exporters.yolo")
                if m is None:
                    self._safe_import("agml.data.exporters.yolo")
                    m = self._modules.get("agml.data.exporters.yolo")
            elif export_format in {"tf", "tensorflow"}:
                m = self._modules.get("agml.data.exporters.tensorflow")
                if m is None:
                    self._safe_import("agml.data.exporters.tensorflow")
                    m = self._modules.get("agml.data.exporters.tensorflow")
            else:
                return self._err(
                    f"Unsupported export format: {export_format}.",
                    hint="Use 'yolo' or 'tensorflow'.",
                )

            if m is None:
                return self._err(
                    f"Exporter module for '{export_format}' could not be imported.",
                    hint="Install optional dependencies required by the exporter.",
                )

            exported = False
            for fn_name in ["export", "export_dataset", "convert"]:
                fn = getattr(m, fn_name, None)
                if callable(fn):
                    fn(dataset_name=dataset_name, output_dir=output_dir, **kwargs)
                    exported = True
                    break

            if not exported:
                return self._err(
                    "No supported export function found in exporter module.",
                    hint="Inspect exporter API symbols in current AgML version.",
                )

            return self._ok(
                {
                    "dataset_name": dataset_name,
                    "export_format": export_format,
                    "output_dir": output_dir,
                },
                "Dataset export completed.",
            )
        except Exception as e:
            return self._err("Failed to export dataset.", e)

    # =========================================================================
    # Model discovery and lightweight wrappers (Phase 3)
    # =========================================================================

    def model_catalog_discovery(self) -> Dict[str, Any]:
        """
        Discover available model symbols from AgML model modules.

        Returns:
            dict: status + discovered classes/functions.
        """
        try:
            m = self._modules.get("agml.models")
            if m is None:
                self._safe_import("agml.models")
                m = self._modules.get("agml.models")
            if m is None:
                return self._err("Could not import agml.models.")

            names = [n for n in dir(m) if not n.startswith("_")]
            return self._ok({"model_symbols": names}, "Model catalog discovered.")
        except Exception as e:
            return self._err("Failed to discover model catalog.", e)

    def lightweight_inference_wrapper(self, model_callable_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a lightweight inference call against a resolved callable path.

        Args:
            model_callable_path (str): Fully qualified callable path (e.g., 'agml.models.tools.some_fn').
            *args: Positional args passed to callable.
            **kwargs: Keyword args passed to callable.

        Returns:
            dict: status + inference result representation.
        """
        try:
            if "." not in model_callable_path:
                return self._err(
                    "model_callable_path must be a fully qualified module path.",
                    hint="Example: agml.models.tools.some_function",
                )
            module_name, attr_name = model_callable_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            fn = getattr(module, attr_name, None)
            if not callable(fn):
                return self._err(
                    f"Resolved attribute is not callable: {model_callable_path}",
                    hint="Provide a callable function path.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result_type": type(result).__name__, "result_repr": repr(result)[:1000]}, "Inference call completed.")
        except Exception as e:
            return self._err("Failed to execute lightweight inference wrapper.", e)

    # =========================================================================
    # Generic class/function utility methods
    # =========================================================================

    def create_instance(self, class_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from fully qualified path.

        Args:
            class_path (str): Fully qualified class path.
            *args: Constructor args.
            **kwargs: Constructor kwargs.

        Returns:
            dict: status + instance representation.
        """
        try:
            module_name, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                {
                    "class_path": class_path,
                    "instance_type": type(instance).__name__,
                    "instance_repr": repr(instance)[:1000],
                },
                "Class instance created.",
            )
        except Exception as e:
            return self._err("Failed to create class instance.", e)

    def call_function(self, function_path: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from fully qualified path.

        Args:
            function_path (str): Fully qualified function path.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: status + function result representation.
        """
        try:
            module_name, function_name = function_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            fn = getattr(module, function_name)
            if not callable(fn):
                return self._err(
                    f"Target is not callable: {function_path}",
                    hint="Pass a valid function path.",
                )
            result = fn(*args, **kwargs)
            return self._ok(
                {
                    "function_path": function_path,
                    "result_type": type(result).__name__,
                    "result_repr": repr(result)[:1000],
                },
                "Function call succeeded.",
            )
        except Exception as e:
            return self._err("Failed to call function.", e)