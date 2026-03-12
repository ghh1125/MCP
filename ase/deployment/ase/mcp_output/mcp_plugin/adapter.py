import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-Mode adapter for the analyzed ASE repository snapshot.

    This adapter prioritizes direct Python imports from the local `source` tree and
    exposes wrapper methods for all identified classes/functions from analysis output.
    It also includes CLI fallback metadata and actionable error guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_all_targets()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _safe_import_module(self, module_path: str) -> Tuple[Optional[Any], Optional[str]]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod, None
        except Exception as exc:
            msg = (
                f"Failed to import module '{module_path}'. "
                f"Verify that repository source is present under '{source_path}' and "
                f"dependencies are installed (minimum: numpy). Details: {exc}"
            )
            self._import_errors[module_path] = msg
            return None, msg

    def _safe_import_symbol(self, module_path: str, symbol: str) -> Tuple[Optional[Any], Optional[str]]:
        mod, err = self._safe_import_module(module_path)
        if mod is None:
            return None, err
        try:
            obj = getattr(mod, symbol)
            key = f"{module_path}:{symbol}"
            self._symbols[key] = obj
            return obj, None
        except Exception as exc:
            msg = (
                f"Module '{module_path}' imported but symbol '{symbol}' is unavailable. "
                f"Check repository version compatibility. Details: {exc}"
            )
            self._import_errors[f"{module_path}:{symbol}"] = msg
            return None, msg

    def _load_all_targets(self) -> None:
        targets = [
            ("setup", "build_py"),
            ("doc.images", "setup"),
            ("doc.ext", "git_role"),
            ("doc.ext", "setup"),
            ("doc.ase.thermochemistry.thermochemistry", "output_to_string"),
            ("doc.ase.transport.transport_setup", "pos"),
            ("doc.ase.dft.dos", "MyCalc"),
            ("doc.ase.dft.bz", "bz_vertices"),
            ("doc.ase.dft.bz", "plot"),
            ("doc.ase.build.surface", "save"),
            ("doc.tutorials.ga.ga_basic_parameters", "combine_parameters"),
            ("doc.tutorials.ga.ga_basic_parameters", "jtg"),
        ]
        for module_path, symbol in targets:
            self._safe_import_symbol(module_path, symbol)

    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload with loaded modules/symbols and import errors.
        """
        ok = len(self._import_errors) == 0
        return self._result(
            "success" if ok else "partial",
            mode=self.mode,
            loaded_modules=sorted(self._modules.keys()),
            loaded_symbols=sorted(self._symbols.keys()),
            import_errors=self._import_errors,
            guidance=(
                "If imports fail, ensure local source path is correct and install required "
                "dependencies: python, numpy. Optional features may need scipy/matplotlib."
            ),
        )

    # -------------------------------------------------------------------------
    # Class instance methods
    # -------------------------------------------------------------------------
    def create_build_py_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate setup.build_py class discovered by analysis.

        Parameters:
            *args: Positional arguments forwarded to class constructor.
            **kwargs: Keyword arguments forwarded to class constructor.

        Returns:
            dict: status + instance or actionable error guidance.
        """
        key = "setup:build_py"
        cls = self._symbols.get(key)
        if cls is None:
            return self._result(
                "error",
                message=self._import_errors.get(
                    key,
                    "Class 'build_py' is not available. Verify the local repository source and retry.",
                ),
            )
        try:
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance, class_name="build_py")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to instantiate 'build_py'. Check constructor arguments. Details: {exc}",
                traceback=traceback.format_exc(),
            )

    def create_mycalc_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate doc.ase.dft.dos.MyCalc class.

        Parameters:
            *args: Positional arguments for MyCalc constructor.
            **kwargs: Keyword arguments for MyCalc constructor.

        Returns:
            dict: status + instance or clear error details.
        """
        key = "doc.ase.dft.dos:MyCalc"
        cls = self._symbols.get(key)
        if cls is None:
            return self._result(
                "error",
                message=self._import_errors.get(
                    key,
                    "Class 'MyCalc' is not available. Confirm repository version and source path.",
                ),
            )
        try:
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance, class_name="MyCalc")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to instantiate 'MyCalc'. Validate provided arguments. Details: {exc}",
                traceback=traceback.format_exc(),
            )

    # -------------------------------------------------------------------------
    # Function call methods
    # -------------------------------------------------------------------------
    def call_doc_images_setup(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.images:setup")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.images:setup", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"doc.images.setup failed: {exc}", traceback=traceback.format_exc())

    def call_doc_ext_git_role(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ext:git_role")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ext:git_role", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"doc.ext.git_role failed: {exc}", traceback=traceback.format_exc())

    def call_doc_ext_setup(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ext:setup")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ext:setup", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"doc.ext.setup failed: {exc}", traceback=traceback.format_exc())

    def call_output_to_string(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ase.thermochemistry.thermochemistry:output_to_string")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ase.thermochemistry.thermochemistry:output_to_string", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"output_to_string failed: {exc}", traceback=traceback.format_exc())

    def call_transport_pos(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ase.transport.transport_setup:pos")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ase.transport.transport_setup:pos", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"transport_setup.pos failed: {exc}", traceback=traceback.format_exc())

    def call_bz_vertices(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ase.dft.bz:bz_vertices")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ase.dft.bz:bz_vertices", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"bz_vertices failed: {exc}", traceback=traceback.format_exc())

    def call_bz_plot(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ase.dft.bz:plot")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ase.dft.bz:plot", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"bz.plot failed: {exc}", traceback=traceback.format_exc())

    def call_build_surface_save(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.ase.build.surface:save")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.ase.build.surface:save", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"build.surface.save failed: {exc}", traceback=traceback.format_exc())

    def call_combine_parameters(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.tutorials.ga.ga_basic_parameters:combine_parameters")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.tutorials.ga.ga_basic_parameters:combine_parameters", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"combine_parameters failed: {exc}", traceback=traceback.format_exc())

    def call_jtg(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get("doc.tutorials.ga.ga_basic_parameters:jtg")
        if fn is None:
            return self._result("error", message=self._import_errors.get("doc.tutorials.ga.ga_basic_parameters:jtg", "Function unavailable."))
        try:
            return self._result("success", data=fn(*args, **kwargs))
        except Exception as exc:
            return self._result("error", message=f"jtg failed: {exc}", traceback=traceback.format_exc())

    # -------------------------------------------------------------------------
    # CLI fallback metadata (non-executing helper)
    # -------------------------------------------------------------------------
    def cli_fallback_info(self) -> Dict[str, Any]:
        """
        Provide CLI fallback map based on analysis.

        Returns:
            dict: status + known CLI commands and guidance.
        """
        commands = [
            {"name": "ase", "module": "ase.cli.main"},
            {"name": "ase build", "module": "ase.cli.build"},
            {"name": "ase run", "module": "ase.cli.run"},
            {"name": "ase info", "module": "ase.cli.info"},
            {"name": "ase find", "module": "ase.cli.find"},
            {"name": "ase band-structure", "module": "ase.cli.band_structure"},
            {"name": "ase db", "module": "ase.db.cli"},
        ]
        return self._result(
            "success",
            mode=self.mode,
            fallback="cli",
            commands=commands,
            guidance="Use CLI fallback when specific import targets are unavailable due to environment or optional dependency constraints.",
        )