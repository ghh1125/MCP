import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode Adapter for GStools.

    This adapter prefers direct imports from repository source code and falls back
    gracefully when optional dependencies or modules are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status, "mode": self.mode}
        data.update(kwargs)
        return data

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        return self._result("ok", **kwargs)

    def _error(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        return self._result("error", message=message, **kwargs)

    def _load_module(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
            self._import_errors.pop(key, None)
        except Exception as exc:
            self._modules[key] = None
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        module_map = {
            "gstools_root": "gstools",
            "covmodel": "gstools.covmodel",
            "field": "gstools.field",
            "krige": "gstools.krige",
            "normalizer": "gstools.normalizer",
            "random": "gstools.random",
            "tools": "gstools.tools",
            "transform": "gstools.transform",
            "variogram": "gstools.variogram",
            "covmodel_models": "gstools.covmodel.models",
            "covmodel_fit": "gstools.covmodel.fit",
            "field_srf": "gstools.field.srf",
            "field_cond_srf": "gstools.field.cond_srf",
            "field_pgs": "gstools.field.pgs",
            "krige_methods": "gstools.krige.methods",
            "normalizer_methods": "gstools.normalizer.methods",
            "random_rng": "gstools.random.rng",
            "transform_array": "gstools.transform.array",
            "transform_field": "gstools.transform.field",
            "variogram_variogram": "gstools.variogram.variogram",
            "variogram_binning": "gstools.variogram.binning",
            "tools_export": "gstools.tools.export",
            "tools_geometric": "gstools.tools.geometric",
            "tools_misc": "gstools.tools.misc",
            "tools_special": "gstools.tools.special",
        }
        for key, module_path in module_map.items():
            self._load_module(key, module_path)

    def _get_module(self, key: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        module = self._modules.get(key)
        if module is None:
            err = self._import_errors.get(key, "Unknown import failure.")
            return None, self._error(
                f"Module '{key}' is unavailable in import mode.",
                guidance="Ensure repository source is present under ./source and required dependencies are installed (numpy, scipy).",
                import_error=err,
            )
        return module, None

    def _get_attr(self, module_key: str, attr_name: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        module, err = self._get_module(module_key)
        if err:
            return None, err
        try:
            return getattr(module, attr_name), None
        except Exception as exc:
            return None, self._error(
                f"Attribute '{attr_name}' not found in module '{module_key}'.",
                guidance="Check GStools version compatibility or update adapter mappings.",
                import_error=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import health and report loaded/unavailable modules.

        Returns:
            dict: Unified status dictionary with loaded module keys and errors.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        failed = {k: e for k, e in self._import_errors.items()}
        status = "ok" if not failed else "partial"
        return self._result(status, loaded_modules=loaded, failed_modules=failed)

    # -------------------------------------------------------------------------
    # Root-level factory and utility methods
    # -------------------------------------------------------------------------
    def create_covmodel(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a covariance model instance from gstools.covmodel.models.

        Args:
            class_name: Name of the covariance model class (e.g., 'Gaussian', 'Exponential').
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: status, instance (on success), or message with guidance (on failure).
        """
        cls, err = self._get_attr("covmodel_models", class_name)
        if err:
            return err
        try:
            instance = cls(*args, **kwargs)
            return self._ok(instance=instance, class_name=class_name)
        except Exception as exc:
            return self._error(
                f"Failed to instantiate covariance model '{class_name}'.",
                guidance="Verify constructor arguments and parameter names expected by the selected model.",
                details=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def create_field_class(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a field-related class instance from gstools.field submodules.

        Supported common classes include SRF, CondSRF, and PGS where available.

        Args:
            class_name: Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status dictionary.
        """
        for mod_key in ("field_srf", "field_cond_srf", "field_pgs", "field"):
            cls, err = self._get_attr(mod_key, class_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                instance = cls(*args, **kwargs)
                return self._ok(instance=instance, class_name=class_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to instantiate field class '{class_name}'.",
                    guidance="Check model object type and domain/grid arguments for the selected field class.",
                    details=f"{type(exc).__name__}: {exc}",
                    traceback=traceback.format_exc(),
                )
        return self._error(
            f"Field class '{class_name}' is unavailable.",
            guidance="Confirm the class exists in gstools.field modules and matches your installed source version.",
        )

    def create_krige_class(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a kriging class instance from gstools.krige.methods.

        Args:
            class_name: Kriging class name (e.g., 'Ordinary', 'Simple', 'Universal').
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status dictionary with created instance when successful.
        """
        cls, err = self._get_attr("krige_methods", class_name)
        if err:
            return err
        try:
            return self._ok(instance=cls(*args, **kwargs), class_name=class_name)
        except Exception as exc:
            return self._error(
                f"Failed to instantiate kriging class '{class_name}'.",
                guidance="Validate conditioning points, values, and covariance model arguments.",
                details=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )

    def create_normalizer(self, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a normalizer class instance from gstools.normalizer.methods.

        Args:
            class_name: Normalizer class name.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status dictionary.
        """
        cls, err = self._get_attr("normalizer_methods", class_name)
        if err:
            return err
        try:
            return self._ok(instance=cls(*args, **kwargs), class_name=class_name)
        except Exception as exc:
            return self._error(
                f"Failed to instantiate normalizer '{class_name}'.",
                guidance="Check provided transformation parameters and expected data domain.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Generic function dispatchers (full coverage strategy)
    # -------------------------------------------------------------------------
    def call_covmodel_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from gstools.covmodel.fit or gstools.covmodel.tools if available.

        Args:
            function_name: Function name to call.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status dictionary with result.
        """
        for mod_key in ("covmodel_fit", "covmodel"):
            fn, err = self._get_attr(mod_key, function_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                return self._ok(result=fn(*args, **kwargs), function_name=function_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to execute covmodel function '{function_name}'.",
                    guidance="Confirm argument shapes and parameter ranges.",
                    details=f"{type(exc).__name__}: {exc}",
                    traceback=traceback.format_exc(),
                )
        return self._error(
            f"Covmodel function '{function_name}' is unavailable.",
            guidance="Verify function name and GStools version compatibility.",
        )

    def call_variogram_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from gstools.variogram.variogram or gstools.variogram.binning.

        Args:
            function_name: Target function name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status dictionary.
        """
        for mod_key in ("variogram_variogram", "variogram_binning", "variogram"):
            fn, err = self._get_attr(mod_key, function_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                return self._ok(result=fn(*args, **kwargs), function_name=function_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to execute variogram function '{function_name}'.",
                    guidance="Validate input coordinates/values and optional binning parameters.",
                    details=f"{type(exc).__name__}: {exc}",
                )
        return self._error(
            f"Variogram function '{function_name}' is unavailable.",
            guidance="Ensure this function exists in gstools.variogram for your source revision.",
        )

    def call_transform_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from gstools.transform.array or gstools.transform.field.

        Args:
            function_name: Target transformation function name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: Unified status dictionary.
        """
        for mod_key in ("transform_array", "transform_field", "transform"):
            fn, err = self._get_attr(mod_key, function_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                return self._ok(result=fn(*args, **kwargs), function_name=function_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to execute transform function '{function_name}'.",
                    guidance="Check value ranges and function-specific required parameters.",
                    details=f"{type(exc).__name__}: {exc}",
                )
        return self._error(
            f"Transform function '{function_name}' is unavailable.",
            guidance="Confirm transform API name for this GStools version.",
        )

    def call_tools_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a utility function from gstools.tools submodules.

        Search order: export, geometric, misc, special, tools root.

        Args:
            function_name: Utility function name.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status dictionary with execution result.
        """
        for mod_key in ("tools_export", "tools_geometric", "tools_misc", "tools_special", "tools"):
            fn, err = self._get_attr(mod_key, function_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                return self._ok(result=fn(*args, **kwargs), function_name=function_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to execute tools function '{function_name}'.",
                    guidance="Validate inputs and ensure optional third-party dependencies are installed if required.",
                    details=f"{type(exc).__name__}: {exc}",
                )
        return self._error(
            f"Tools function '{function_name}' is unavailable.",
            guidance="Check function name and submodule location in gstools.tools.",
        )

    def call_random_function(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call function from gstools.random.rng or gstools.random.

        Args:
            function_name: RNG helper function name.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            dict: Unified status dictionary.
        """
        for mod_key in ("random_rng", "random"):
            fn, err = self._get_attr(mod_key, function_name)
            if err and "not found" in err.get("message", "").lower():
                continue
            if err:
                continue
            try:
                return self._ok(result=fn(*args, **kwargs), function_name=function_name, module=mod_key)
            except Exception as exc:
                return self._error(
                    f"Failed to execute random function '{function_name}'.",
                    guidance="Check random generator settings, seed values, and argument types.",
                    details=f"{type(exc).__name__}: {exc}",
                )
        return self._error(
            f"Random function '{function_name}' is unavailable.",
            guidance="Confirm the function exists in gstools.random APIs.",
        )

    # -------------------------------------------------------------------------
    # High-level convenience operations
    # -------------------------------------------------------------------------
    def generate_spatial_random_field(
        self,
        model_class: str,
        model_kwargs: Optional[Dict[str, Any]] = None,
        srf_kwargs: Optional[Dict[str, Any]] = None,
        call_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end convenience pipeline:
        1) Instantiate covariance model
        2) Instantiate SRF
        3) Call SRF with provided generation args

        Args:
            model_class: Covariance model class name in gstools.covmodel.models.
            model_kwargs: Constructor kwargs for covariance model.
            srf_kwargs: Constructor kwargs for SRF(model, ...). Model is injected.
            call_kwargs: Keyword args for SRF.__call__ generation.

        Returns:
            dict: status with generated field result and created objects.
        """
        model_kwargs = model_kwargs or {}
        srf_kwargs = srf_kwargs or {}
        call_kwargs = call_kwargs or {}

        model_res = self.create_covmodel(model_class, **model_kwargs)
        if model_res["status"] != "ok":
            return model_res
        model = model_res["instance"]

        srf_cls, err = self._get_attr("field_srf", "SRF")
        if err:
            return err

        try:
            srf = srf_cls(model, **srf_kwargs)
            field = srf(**call_kwargs)
            return self._ok(model=model, srf=srf, field=field)
        except Exception as exc:
            return self._error(
                "Failed to generate spatial random field.",
                guidance="Check model parameters, domain coordinates, and optional generator configuration.",
                details=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )