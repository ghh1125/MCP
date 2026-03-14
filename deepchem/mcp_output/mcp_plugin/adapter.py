import os
import sys
import importlib
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for selected DeepChem repository modules.

    This adapter attempts to import and call concrete implementations discovered
    in repository analysis. It exposes:
    - Function wrappers for identified callable functions.
    - Class instance constructors for identified classes.
    - CLI fallback helpers when import path execution is not available.

    All methods return a unified dictionary with at least:
    {
        "status": "success" | "error" | "fallback",
        ...
    }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._class_instances: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._import_errors[module_path] = (
                f"Failed to import '{module_path}'. "
                f"Verify dependencies and source path. Details: {exc}"
            )
            return None

    def _load_modules(self) -> None:
        module_paths = [
            "datasets.construct_pdbbind_df",
            "docs.source.conf",
            "contrib.visualization.utils",
            "contrib.DeepMHC.bd13_datasets",
            "contrib.DeepMHC.deepmhc",
            "contrib.dragonn.models",
        ]
        for mp in module_paths:
            self._import_module(mp)

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import status.

        Returns:
            Dict with loaded modules and import errors.
        """
        return self._result(
            "success",
            mode=self.mode,
            loaded_modules=sorted(self._modules.keys()),
            import_errors=self._import_errors,
            guidance=(
                "Install optional scientific dependencies (e.g., rdkit, tensorflow, torch) "
                "if specific modules fail to import."
            ),
        )

    def _call_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        module = self._modules.get(module_path)
        if module is None:
            msg = self._import_errors.get(
                module_path,
                f"Module '{module_path}' is not available.",
            )
            return self._result(
                "fallback",
                error=msg,
                guidance=(
                    f"Cannot call '{function_name}' because import failed. "
                    "Check Python path and install missing dependencies."
                ),
            )
        fn = getattr(module, function_name, None)
        if fn is None:
            return self._result(
                "error",
                error=f"Function '{function_name}' not found in module '{module_path}'.",
                guidance="Verify repository version and function name.",
            )
        try:
            data = fn(*args, **kwargs)
            return self._result(
                "success",
                module=module_path,
                function=function_name,
                data=data,
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Function call failed: {exc}",
                guidance="Validate function parameters and input data format.",
            )

    def _create_instance(
        self,
        module_path: str,
        class_name: str,
        instance_key: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        module = self._modules.get(module_path)
        if module is None:
            msg = self._import_errors.get(
                module_path,
                f"Module '{module_path}' is not available.",
            )
            return self._result(
                "fallback",
                error=msg,
                guidance=(
                    f"Cannot instantiate '{class_name}' because import failed. "
                    "Check dependency installation."
                ),
            )
        cls = getattr(module, class_name, None)
        if cls is None:
            return self._result(
                "error",
                error=f"Class '{class_name}' not found in module '{module_path}'.",
                guidance="Verify repository version and class name.",
            )
        try:
            instance = cls(*args, **kwargs)
            key = instance_key or f"{module_path}.{class_name}"
            self._class_instances[key] = instance
            return self._result(
                "success",
                module=module_path,
                class_name=class_name,
                instance_key=key,
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Class instantiation failed: {exc}",
                guidance="Check constructor arguments and required runtime dependencies.",
            )

    # -------------------------------------------------------------------------
    # Functions: datasets.construct_pdbbind_df
    # -------------------------------------------------------------------------
    def call_construct_df(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call datasets.construct_pdbbind_df.construct_df.

        Parameters:
            *args: Positional arguments forwarded to construct_df.
            **kwargs: Keyword arguments forwarded to construct_df.

        Returns:
            Unified status dictionary with function output in 'data' on success.
        """
        return self._call_function("datasets.construct_pdbbind_df", "construct_df", *args, **kwargs)

    def call_extract_labels(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call datasets.construct_pdbbind_df.extract_labels.

        Parameters:
            *args: Positional arguments forwarded to extract_labels.
            **kwargs: Keyword arguments forwarded to extract_labels.

        Returns:
            Unified status dictionary with function output in 'data' on success.
        """
        return self._call_function("datasets.construct_pdbbind_df", "extract_labels", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Functions: docs.source.conf
    # -------------------------------------------------------------------------
    def call_linkcode_resolve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call docs.source.conf.linkcode_resolve.

        Parameters:
            *args: Positional arguments forwarded to linkcode_resolve.
            **kwargs: Keyword arguments forwarded to linkcode_resolve.

        Returns:
            Unified status dictionary with resolved link info in 'data' on success.
        """
        return self._call_function("docs.source.conf", "linkcode_resolve", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Functions: contrib.visualization.utils
    # -------------------------------------------------------------------------
    def call_combine_mdtraj(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.visualization.utils.combine_mdtraj.

        Parameters:
            *args: Positional arguments forwarded to combine_mdtraj.
            **kwargs: Keyword arguments forwarded to combine_mdtraj.

        Returns:
            Unified status dictionary containing result in 'data' on success.
        """
        return self._call_function("contrib.visualization.utils", "combine_mdtraj", *args, **kwargs)

    def call_convert_lines_to_mdtraj(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.visualization.utils.convert_lines_to_mdtraj.

        Parameters:
            *args: Positional arguments forwarded to convert_lines_to_mdtraj.
            **kwargs: Keyword arguments forwarded to convert_lines_to_mdtraj.

        Returns:
            Unified status dictionary containing result in 'data' on success.
        """
        return self._call_function("contrib.visualization.utils", "convert_lines_to_mdtraj", *args, **kwargs)

    def call_display_images(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.visualization.utils.display_images.

        Parameters:
            *args: Positional arguments forwarded to display_images.
            **kwargs: Keyword arguments forwarded to display_images.

        Returns:
            Unified status dictionary containing result in 'data' on success.
        """
        return self._call_function("contrib.visualization.utils", "display_images", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Functions: contrib.DeepMHC.bd13_datasets
    # -------------------------------------------------------------------------
    def call_featurize(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.DeepMHC.bd13_datasets.featurize.

        Parameters:
            *args: Positional arguments forwarded to featurize.
            **kwargs: Keyword arguments forwarded to featurize.

        Returns:
            Unified status dictionary containing featurized output in 'data' on success.
        """
        return self._call_function("contrib.DeepMHC.bd13_datasets", "featurize", *args, **kwargs)

    def call_load_bd2013_human(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.DeepMHC.bd13_datasets.load_bd2013_human.

        Parameters:
            *args: Positional arguments forwarded to load_bd2013_human.
            **kwargs: Keyword arguments forwarded to load_bd2013_human.

        Returns:
            Unified status dictionary with loaded dataset artifacts in 'data' on success.
        """
        return self._call_function("contrib.DeepMHC.bd13_datasets", "load_bd2013_human", *args, **kwargs)

    def call_to_one_hot_array(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call contrib.DeepMHC.bd13_datasets.to_one_hot_array.

        Parameters:
            *args: Positional arguments forwarded to to_one_hot_array.
            **kwargs: Keyword arguments forwarded to to_one_hot_array.

        Returns:
            Unified status dictionary with encoded array in 'data' on success.
        """
        return self._call_function("contrib.DeepMHC.bd13_datasets", "to_one_hot_array", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Classes: contrib.DeepMHC.deepmhc.DeepMHC
    # -------------------------------------------------------------------------
    def create_deepmhc(self, *args: Any, instance_key: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate contrib.DeepMHC.deepmhc.DeepMHC.

        Parameters:
            *args: Positional constructor args.
            instance_key: Optional storage key for later retrieval.
            **kwargs: Keyword constructor args.

        Returns:
            Unified status dictionary with 'instance_key' on success.
        """
        return self._create_instance(
            "contrib.DeepMHC.deepmhc",
            "DeepMHC",
            instance_key,
            *args,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Classes: contrib.dragonn.models
    # -------------------------------------------------------------------------
    def create_motif_score_rnn(self, *args: Any, instance_key: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate contrib.dragonn.models.MotifScoreRNN.

        Parameters:
            *args: Positional constructor args.
            instance_key: Optional storage key for later retrieval.
            **kwargs: Keyword constructor args.

        Returns:
            Unified status dictionary with 'instance_key' on success.
        """
        return self._create_instance(
            "contrib.dragonn.models",
            "MotifScoreRNN",
            instance_key,
            *args,
            **kwargs,
        )

    def create_gkmsvm(self, *args: Any, instance_key: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate contrib.dragonn.models.gkmSVM.

        Parameters:
            *args: Positional constructor args.
            instance_key: Optional storage key for later retrieval.
            **kwargs: Keyword constructor args.

        Returns:
            Unified status dictionary with 'instance_key' on success.
        """
        return self._create_instance(
            "contrib.dragonn.models",
            "gkmSVM",
            instance_key,
            *args,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Instance management
    # -------------------------------------------------------------------------
    def list_instances(self) -> Dict[str, Any]:
        """
        List cached class instances created by this adapter.

        Returns:
            Unified status dictionary containing instance keys.
        """
        return self._result("success", instances=sorted(self._class_instances.keys()))

    def call_instance_method(
        self,
        instance_key: str,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Invoke a method on a previously created instance.

        Parameters:
            instance_key: Key returned by create_* method.
            method_name: Target method name on the instance.
            *args: Positional arguments for the instance method.
            **kwargs: Keyword arguments for the instance method.

        Returns:
            Unified status dictionary with method result in 'data' on success.
        """
        inst = self._class_instances.get(instance_key)
        if inst is None:
            return self._result(
                "error",
                error=f"Instance '{instance_key}' not found.",
                guidance="Create the instance first using the matching create_* method.",
            )
        method = getattr(inst, method_name, None)
        if method is None or not callable(method):
            return self._result(
                "error",
                error=f"Method '{method_name}' not found on instance '{instance_key}'.",
                guidance="Check available methods with dir(instance).",
            )
        try:
            data = method(*args, **kwargs)
            return self._result("success", instance_key=instance_key, method=method_name, data=data)
        except Exception as exc:
            return self._result(
                "error",
                error=f"Instance method call failed: {exc}",
                guidance="Validate method parameters and ensure model state is initialized.",
            )

    # -------------------------------------------------------------------------
    # CLI fallback helpers
    # -------------------------------------------------------------------------
    def cli_run_benchmark(self, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Provide CLI fallback guidance for MolNet benchmark execution.

        Parameters:
            extra_args: Optional CLI args to append.

        Returns:
            Unified status dictionary with a suggested command.
        """
        cmd = ["python", "-m", "source.deepchem.molnet.run_benchmark"] + (extra_args or [])
        return self._result(
            "fallback",
            command=cmd,
            guidance=(
                "Use this command in a shell when import-mode execution is unavailable. "
                "Ensure dependencies are installed and run from project root."
            ),
        )

    def cli_run_benchmark_low_data(self, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Provide CLI fallback guidance for low-data benchmark workflow.

        Parameters:
            extra_args: Optional CLI args to append.

        Returns:
            Unified status dictionary with a suggested command.
        """
        cmd = ["python", "-m", "source.deepchem.molnet.run_benchmark_low_data"] + (extra_args or [])
        return self._result(
            "fallback",
            command=cmd,
            guidance="Run in shell as fallback. Verify low-data benchmark options before execution.",
        )

    def cli_run_example_benchmark(self, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Provide CLI fallback guidance for example benchmark runner.

        Parameters:
            extra_args: Optional CLI args to append.

        Returns:
            Unified status dictionary with a suggested command.
        """
        cmd = ["python", "-m", "source.examples.benchmark"] + (extra_args or [])
        return self._result(
            "fallback",
            command=cmd,
            guidance="This is a demo-oriented runner and may be less stable than core benchmark scripts.",
        )