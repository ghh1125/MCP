import os
import sys
import importlib
import inspect
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for RDKit repository modules discovered via analysis.

    This adapter attempts direct module imports first ("import" mode). If imports fail,
    it gracefully falls back to "fallback" mode and returns actionable guidance.
    All public methods return a unified dictionary payload with a required `status` field.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    # ==========================================================================
    # Core utilities
    # ==========================================================================

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
            "error": error,
            "guidance": guidance,
        }

    def _import_module(self, module_path: str) -> Optional[Any]:
        try:
            module = importlib.import_module(module_path)
            self._modules[module_path] = module
            return module
        except Exception as exc:
            self._modules[module_path] = None
            self._import_errors[module_path] = (
                f"Failed to import '{module_path}': {exc}"
            )
            return None

    def _load_modules(self) -> None:
        target_modules = [
            "Regress.Scripts.new_timings",
            "Web.RDExtras.MolImage",
            "Web.RDExtras.MolDepict",
            "Projects.DbCLI.CreateDb",
            "Projects.DbCLI.SearchDb",
            "Code.DataManip.MetricMatrixCalc.Wrap.testMatricCalc",
            "Code.DataStructs.Wrap.testBV",
            "Code.DataStructs.Wrap.testSparseIntVect",
            "rdkit.Chem.FeatFinderCLI",
            "Contrib.MolVS.molvs_cli",
        ]
        for module_path in target_modules:
            self._import_module(module_path)

        if all(self._modules.get(m) is None for m in target_modules):
            self.mode = "fallback"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter import health status.

        Returns:
            dict: Unified status dict including loaded modules and import errors.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        failed = {k: e for k, e in self._import_errors.items()}
        return self._result(
            status="ok" if loaded else "degraded",
            message="Adapter health check completed.",
            data={"loaded_modules": loaded, "failed_modules": failed},
            guidance=(
                "If critical modules failed, ensure C++ extension-backed RDKit build artifacts "
                "are available under the source tree and required runtime deps are installed."
            ),
        )

    def _call_function(
        self, module_path: str, func_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        module = self._modules.get(module_path)
        if module is None:
            return self._result(
                status="error",
                message=f"Module '{module_path}' is not available.",
                error=self._import_errors.get(module_path, "Unknown import failure."),
                guidance=(
                    "Verify repository source path injection and local build artifacts. "
                    "For RDKit modules, ensure compiled extensions and numpy are available."
                ),
            )
        try:
            func = getattr(module, func_name, None)
            if func is None or not callable(func):
                available = [n for n, o in inspect.getmembers(module) if callable(o)]
                return self._result(
                    status="error",
                    message=f"Function '{func_name}' not found in '{module_path}'.",
                    error="Missing callable in target module.",
                    data={"available_callables_sample": available[:25]},
                    guidance="Check function name spelling and module version compatibility.",
                )
            result = func(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Function '{func_name}' executed successfully.",
                data=result,
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Function '{func_name}' execution failed.",
                error=str(exc),
                guidance=(
                    "Validate arguments and required environment. "
                    "If the callable depends on RDKit backend libs, ensure they are compiled."
                ),
            )

    # ==========================================================================
    # Regress.Scripts.new_timings
    # ==========================================================================

    def call_new_timings_data(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Regress.Scripts.new_timings.data.

        Parameters:
            *args: Positional arguments forwarded to data().
            **kwargs: Keyword arguments forwarded to data().

        Returns:
            dict: Unified status response with callable result or actionable error.
        """
        return self._call_function("Regress.Scripts.new_timings", "data", *args, **kwargs)

    # ==========================================================================
    # Web.RDExtras.MolImage
    # ==========================================================================

    def call_molimage_gif(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Web.RDExtras.MolImage.gif.

        Parameters:
            *args: Positional arguments for gif().
            **kwargs: Keyword arguments for gif().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Web.RDExtras.MolImage", "gif", *args, **kwargs)

    def call_molimage_svg(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Web.RDExtras.MolImage.svg.

        Parameters:
            *args: Positional arguments for svg().
            **kwargs: Keyword arguments for svg().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Web.RDExtras.MolImage", "svg", *args, **kwargs)

    # ==========================================================================
    # Web.RDExtras.MolDepict
    # ==========================================================================

    def call_moldepict_page(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Web.RDExtras.MolDepict.page.

        Parameters:
            *args: Positional arguments for page().
            **kwargs: Keyword arguments for page().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Web.RDExtras.MolDepict", "page", *args, **kwargs)

    # ==========================================================================
    # Projects.DbCLI.CreateDb
    # ==========================================================================

    def call_createdb_createdb(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Projects.DbCLI.CreateDb.CreateDb.

        Parameters:
            *args: Positional arguments for CreateDb().
            **kwargs: Keyword arguments for CreateDb().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Projects.DbCLI.CreateDb", "CreateDb", *args, **kwargs)

    def call_createdb_initparser(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Projects.DbCLI.CreateDb.initParser.

        Parameters:
            *args: Positional arguments for initParser().
            **kwargs: Keyword arguments for initParser().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Projects.DbCLI.CreateDb", "initParser", *args, **kwargs)

    # ==========================================================================
    # Projects.DbCLI.SearchDb
    # ==========================================================================

    def call_searchdb_get_mols_from_sdfile(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Projects.DbCLI.SearchDb.GetMolsFromSDFile.

        Parameters:
            *args: Positional arguments for GetMolsFromSDFile().
            **kwargs: Keyword arguments for GetMolsFromSDFile().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Projects.DbCLI.SearchDb", "GetMolsFromSDFile", *args, **kwargs)

    def call_searchdb_get_mols_from_smiles_file(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Projects.DbCLI.SearchDb.GetMolsFromSmilesFile.

        Parameters:
            *args: Positional arguments for GetMolsFromSmilesFile().
            **kwargs: Keyword arguments for GetMolsFromSmilesFile().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Projects.DbCLI.SearchDb", "GetMolsFromSmilesFile", *args, **kwargs)

    def call_searchdb_get_neighbor_lists(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Projects.DbCLI.SearchDb.GetNeighborLists.

        Parameters:
            *args: Positional arguments for GetNeighborLists().
            **kwargs: Keyword arguments for GetNeighborLists().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Projects.DbCLI.SearchDb", "GetNeighborLists", *args, **kwargs)

    # ==========================================================================
    # Code.DataManip.MetricMatrixCalc.Wrap.testMatricCalc
    # ==========================================================================

    def call_testmatriccalc_feq(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Code.DataManip.MetricMatrixCalc.Wrap.testMatricCalc.feq.

        Parameters:
            *args: Positional arguments for feq().
            **kwargs: Keyword arguments for feq().

        Returns:
            dict: Unified status response.
        """
        return self._call_function(
            "Code.DataManip.MetricMatrixCalc.Wrap.testMatricCalc", "feq", *args, **kwargs
        )

    # ==========================================================================
    # Code.DataStructs.Wrap.testBV
    # ==========================================================================

    def call_testbv_feq(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Code.DataStructs.Wrap.testBV.feq.

        Parameters:
            *args: Positional arguments for feq().
            **kwargs: Keyword arguments for feq().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Code.DataStructs.Wrap.testBV", "feq", *args, **kwargs)

    # ==========================================================================
    # Code.DataStructs.Wrap.testSparseIntVect
    # ==========================================================================

    def call_testsparseintvect_feq(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Code.DataStructs.Wrap.testSparseIntVect.feq.

        Parameters:
            *args: Positional arguments for feq().
            **kwargs: Keyword arguments for feq().

        Returns:
            dict: Unified status response.
        """
        return self._call_function("Code.DataStructs.Wrap.testSparseIntVect", "feq", *args, **kwargs)

    # ==========================================================================
    # CLI-oriented helper wrappers (from analysis)
    # ==========================================================================

    def call_featfindercli_module(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute rdkit.Chem.FeatFinderCLI entry-style behavior if available.

        Parameters:
            argv: Optional argument list. If omitted, module defaults are used.

        Returns:
            dict: Unified status response.
        """
        module_path = "rdkit.Chem.FeatFinderCLI"
        module = self._modules.get(module_path)
        if module is None:
            return self._result(
                status="error",
                message="FeatFinderCLI module is unavailable.",
                error=self._import_errors.get(module_path, "Unknown import failure."),
                guidance="Confirm RDKit Python modules and compiled backends are importable.",
            )
        try:
            if hasattr(module, "main") and callable(module.main):
                result = module.main(argv) if argv is not None else module.main()
                return self._result("ok", "FeatFinderCLI executed.", data=result)
            return self._result(
                status="error",
                message="No callable main() found in FeatFinderCLI.",
                guidance="Inspect module API and call exported functions directly.",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="FeatFinderCLI execution failed.",
                error=str(exc),
                guidance="Check CLI arguments and required feature definition inputs.",
            )

    def call_molvs_cli_module(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute Contrib.MolVS.molvs_cli entry-style behavior if available.

        Parameters:
            argv: Optional argument list for CLI-like execution.

        Returns:
            dict: Unified status response.
        """
        module_path = "Contrib.MolVS.molvs_cli"
        module = self._modules.get(module_path)
        if module is None:
            return self._result(
                status="error",
                message="molvs_cli module is unavailable.",
                error=self._import_errors.get(module_path, "Unknown import failure."),
                guidance="Ensure Contrib modules exist in source path and dependencies are installed.",
            )
        try:
            if hasattr(module, "main") and callable(module.main):
                result = module.main(argv) if argv is not None else module.main()
                return self._result("ok", "molvs_cli executed.", data=result)
            return self._result(
                status="error",
                message="No callable main() found in molvs_cli.",
                guidance="Inspect module for alternate callable entry points.",
            )
        except Exception as exc:
            return self._result(
                status="error",
                message="molvs_cli execution failed.",
                error=str(exc),
                guidance="Validate CLI arguments and molecule input format.",
            )