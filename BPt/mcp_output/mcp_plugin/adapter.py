import os
import sys
import traceback
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the BPt repository.

    This adapter attempts direct imports from the local source tree and exposes
    safe wrapper methods with unified status dictionaries.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._loaded = False
        self._import_error: Optional[str] = None
        self._traceback: Optional[str] = None
        self._modules: Dict[str, Any] = {}
        self._load_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Any = None, message: str = "success", **extra: Any) -> Dict[str, Any]:
        out = {"status": "success", "mode": self.mode, "message": message, "data": data}
        out.update(extra)
        return out

    def _fail(self, message: str, **extra: Any) -> Dict[str, Any]:
        out = {"status": "error", "mode": self.mode, "message": message, "data": None}
        out.update(extra)
        return out

    def _ensure_loaded(self) -> Optional[Dict[str, Any]]:
        if self._loaded:
            return None
        guidance = (
            "Import mode is unavailable. Ensure repository source exists under the expected "
            "'source' directory and required dependencies are installed: "
            "numpy, pandas, scikit-learn, scipy, joblib. Optional: matplotlib, seaborn, "
            "lightgbm, nevergrad, nilearn, xgboost."
        )
        return self._fail(
            "Failed to import BPt modules.",
            guidance=guidance,
            import_error=self._import_error,
            traceback=self._traceback,
        )

    def _load_imports(self) -> None:
        try:
            import BPt  # noqa: F401
            import BPt.main.funcs as main_funcs
            import BPt.main.eval as main_eval
            import BPt.main.compare as main_compare
            import BPt.main.CV as main_cv
            import BPt.dataset.dataset as dataset_module
            import BPt.util as util_module

            self._modules["BPt"] = BPt
            self._modules["main_funcs"] = main_funcs
            self._modules["main_eval"] = main_eval
            self._modules["main_compare"] = main_compare
            self._modules["main_cv"] = main_cv
            self._modules["dataset_module"] = dataset_module
            self._modules["util_module"] = util_module

            self._loaded = True
        except Exception as e:
            self._loaded = False
            self._import_error = str(e)
            self._traceback = traceback.format_exc()

    # -------------------------------------------------------------------------
    # Health / status
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.
        """
        if self._loaded:
            return self._ok(
                {
                    "loaded": True,
                    "import_strategy": "import",
                    "fallback": "blackbox",
                    "import_feasibility": 0.9,
                    "complexity": "medium",
                    "intrusiveness_risk": "low",
                }
            )
        return self._fail(
            "Adapter not loaded.",
            loaded=False,
            import_error=self._import_error,
            traceback=self._traceback,
        )

    # -------------------------------------------------------------------------
    # Top-level BPt module wrappers (functions)
    # -------------------------------------------------------------------------
    def call_evaluate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.evaluate(*args, **kwargs).

        Parameters:
            *args: Positional arguments accepted by BPt.evaluate.
            **kwargs: Keyword arguments accepted by BPt.evaluate.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            result = self._modules["BPt"].evaluate(*args, **kwargs)
            return self._ok(result, "BPt.evaluate executed")
        except Exception as e:
            return self._fail("BPt.evaluate failed.", error=str(e), traceback=traceback.format_exc())

    def call_cross_val_score(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.cross_val_score(*args, **kwargs).
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            result = self._modules["BPt"].cross_val_score(*args, **kwargs)
            return self._ok(result, "BPt.cross_val_score executed")
        except Exception as e:
            return self._fail("BPt.cross_val_score failed.", error=str(e), traceback=traceback.format_exc())

    def call_cross_validate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.cross_validate(*args, **kwargs).
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            result = self._modules["BPt"].cross_validate(*args, **kwargs)
            return self._ok(result, "BPt.cross_validate executed")
        except Exception as e:
            return self._fail("BPt.cross_validate failed.", error=str(e), traceback=traceback.format_exc())

    def call_get_estimator(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.get_estimator(*args, **kwargs).
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            result = self._modules["BPt"].get_estimator(*args, **kwargs)
            return self._ok(result, "BPt.get_estimator executed")
        except Exception as e:
            return self._fail("BPt.get_estimator failed.", error=str(e), traceback=traceback.format_exc())

    def call_compare_dict_from_existing(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.compare_dict_from_existing(*args, **kwargs).
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            result = self._modules["BPt"].compare_dict_from_existing(*args, **kwargs)
            return self._ok(result, "BPt.compare_dict_from_existing executed")
        except Exception as e:
            return self._fail(
                "BPt.compare_dict_from_existing failed.",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Class instance builders
    # -------------------------------------------------------------------------
    def create_dataset(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create BPt Dataset instance.

        Parameters:
            *args: Constructor positional args for BPt.Dataset.
            **kwargs: Constructor keyword args for BPt.Dataset.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            cls = self._modules["BPt"].Dataset
            instance = cls(*args, **kwargs)
            return self._ok(instance, "BPt.Dataset instance created")
        except Exception as e:
            return self._fail("Failed to create BPt.Dataset.", error=str(e), traceback=traceback.format_exc())

    def create_cv(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create BPt CV instance.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            cls = self._modules["BPt"].CV
            instance = cls(*args, **kwargs)
            return self._ok(instance, "BPt.CV instance created")
        except Exception as e:
            return self._fail("Failed to create BPt.CV.", error=str(e), traceback=traceback.format_exc())

    def create_model_pipeline(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create BPt ModelPipeline instance.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            cls = self._modules["BPt"].ModelPipeline
            instance = cls(*args, **kwargs)
            return self._ok(instance, "BPt.ModelPipeline instance created")
        except Exception as e:
            return self._fail(
                "Failed to create BPt.ModelPipeline.",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    def create_problem_spec(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create BPt ProblemSpec instance.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            cls = self._modules["BPt"].ProblemSpec
            instance = cls(*args, **kwargs)
            return self._ok(instance, "BPt.ProblemSpec instance created")
        except Exception as e:
            return self._fail(
                "Failed to create BPt.ProblemSpec.",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Utility wrappers
    # -------------------------------------------------------------------------
    def call_is_array_like(self, obj: Any) -> Dict[str, Any]:
        """
        Call BPt.util.is_array_like(obj).

        Parameters:
            obj: Object to evaluate.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            fn = self._modules["util_module"].is_array_like
            result = fn(obj)
            return self._ok(result, "BPt.util.is_array_like executed")
        except Exception as e:
            return self._fail("BPt.util.is_array_like failed.", error=str(e), traceback=traceback.format_exc())

    def call_save_docx_table(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call BPt.util.save_docx_table(*args, **kwargs).

        Parameters:
            *args, **kwargs: Passed directly to utility function.
        """
        err = self._ensure_loaded()
        if err:
            return err
        try:
            fn = self._modules["util_module"].save_docx_table
            result = fn(*args, **kwargs)
            return self._ok(result, "BPt.util.save_docx_table executed")
        except Exception as e:
            return self._fail("BPt.util.save_docx_table failed.", error=str(e), traceback=traceback.format_exc())