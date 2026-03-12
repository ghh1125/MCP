import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, List, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Adapter for deepTools in import-first mode with graceful fallback to CLI execution.

    This adapter targets modules identified in the analysis:
    - deeptools.bamCoverage
    - deeptools.bamCompare
    - deeptools.computeMatrix
    - deeptools.computeMatrixOperations
    - deeptools.plotHeatmap
    - deeptools.plotProfile
    - deeptools.multiBamSummary
    - deeptools.multiBigwigSummary
    - deeptools.plotCorrelation
    - deeptools.plotPCA
    - deeptools.plotCoverage
    - deeptools.plotFingerprint
    - deeptools.plotEnrichment
    - deeptools.estimateReadFiltering
    - deeptools.alignmentSieve
    - deeptools.bigwigCompare
    - deeptools.bigwigAverage
    - deeptools.computeGCBias
    - deeptools.correctGCBias
    - deeptools.bamPEFragmentSize
    """

    # -------------------------------------------------------------------------
    # Initialization and module registry
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Dict[str, Any]] = {}
        self._module_map: Dict[str, str] = {
            "bamCoverage": "deeptools.bamCoverage",
            "bamCompare": "deeptools.bamCompare",
            "computeMatrix": "deeptools.computeMatrix",
            "computeMatrixOperations": "deeptools.computeMatrixOperations",
            "plotHeatmap": "deeptools.plotHeatmap",
            "plotProfile": "deeptools.plotProfile",
            "multiBamSummary": "deeptools.multiBamSummary",
            "multiBigwigSummary": "deeptools.multiBigwigSummary",
            "plotCorrelation": "deeptools.plotCorrelation",
            "plotPCA": "deeptools.plotPCA",
            "plotCoverage": "deeptools.plotCoverage",
            "plotFingerprint": "deeptools.plotFingerprint",
            "plotEnrichment": "deeptools.plotEnrichment",
            "estimateReadFiltering": "deeptools.estimateReadFiltering",
            "alignmentSieve": "deeptools.alignmentSieve",
            "bigwigCompare": "deeptools.bigwigCompare",
            "bigwigAverage": "deeptools.bigwigAverage",
            "computeGCBias": "deeptools.computeGCBias",
            "correctGCBias": "deeptools.correctGCBias",
            "bamPEFragmentSize": "deeptools.bamPEFragmentSize",
        }
        self._load_all_modules()

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

    def _load_module(self, tool_name: str, module_path: str) -> None:
        try:
            module = importlib.import_module(module_path)
            self._modules[tool_name] = {
                "imported": True,
                "module": module,
                "module_path": module_path,
                "error": None,
            }
        except Exception as e:
            self._modules[tool_name] = {
                "imported": False,
                "module": None,
                "module_path": module_path,
                "error": f"{type(e).__name__}: {e}",
            }

    def _load_all_modules(self) -> None:
        for tool_name, module_path in self._module_map.items():
            self._load_module(tool_name, module_path)

    # -------------------------------------------------------------------------
    # Introspection and health
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter and import readiness status.

        Returns:
            Unified status dictionary with per-module import state.
        """
        imported = {k: v["imported"] for k, v in self._modules.items()}
        failed = {k: v["error"] for k, v in self._modules.items() if not v["imported"]}
        status = "success" if all(imported.values()) else "partial_success"
        message = (
            "All modules imported successfully."
            if status == "success"
            else "Some modules failed to import. CLI fallback is available."
        )
        return self._result(
            status=status,
            message=message,
            data={"imports": imported, "failed": failed},
            guidance=(
                "Verify local source tree under 'source/deeptools' and required dependencies "
                "(numpy, scipy, matplotlib, pysam, pyBigWig)."
                if failed
                else None
            ),
        )

    def list_tools(self) -> Dict[str, Any]:
        """
        List supported deepTools commands and their module paths.
        """
        data = []
        for name, path in self._module_map.items():
            meta = self._modules.get(name, {})
            data.append(
                {
                    "tool": name,
                    "module_path": path,
                    "imported": meta.get("imported", False),
                    "error": meta.get("error"),
                }
            )
        return self._result(status="success", message="Supported tools listed.", data={"tools": data})

    # -------------------------------------------------------------------------
    # Core invocation helpers
    # -------------------------------------------------------------------------
    def _build_argv(self, kwargs: Dict[str, Any]) -> List[str]:
        argv: List[str] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            flag = f"--{key.replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    argv.append(flag)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    argv.append(flag)
                    argv.append(str(item))
            else:
                argv.append(flag)
                argv.append(str(value))
        return argv

    def _find_callable(self, module: Any) -> Tuple[Optional[str], Optional[Any]]:
        preferred = ["main", "run", "parseArguments", "process_args"]
        for name in preferred:
            fn = getattr(module, name, None)
            if callable(fn):
                return name, fn
        for name, obj in inspect.getmembers(module):
            if callable(obj) and name.lower() in {"main", "run"}:
                return name, obj
        return None, None

    def _invoke_module(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        meta = self._modules.get(tool_name)
        if not meta:
            return self._result(
                status="error",
                message=f"Unknown tool: {tool_name}.",
                error="ToolNotRegistered",
                guidance="Call list_tools() to view available tools.",
            )

        if meta["imported"] and meta["module"] is not None:
            module = meta["module"]
            fn_name, fn = self._find_callable(module)
            if not fn:
                return self._result(
                    status="error",
                    message=f"No callable entry point found for {tool_name}.",
                    error="EntryPointNotFound",
                    guidance="Inspect module for a callable main/run function or use CLI fallback.",
                )
            try:
                argv = self._build_argv(kwargs)
                try:
                    result = fn(argv)
                except TypeError:
                    result = fn()
                return self._result(
                    status="success",
                    message=f"{tool_name} executed via import mode.",
                    data={
                        "tool": tool_name,
                        "module": meta["module_path"],
                        "entry_point": fn_name,
                        "argv": argv,
                        "result": result,
                    },
                )
            except SystemExit as e:
                code = int(getattr(e, "code", 0) or 0)
                if code == 0:
                    return self._result(
                        status="success",
                        message=f"{tool_name} finished (SystemExit 0).",
                        data={"tool": tool_name, "exit_code": code},
                    )
                return self._result(
                    status="error",
                    message=f"{tool_name} exited with non-zero status.",
                    error=f"SystemExit({code})",
                    guidance="Validate command arguments and input file paths.",
                )
            except Exception as e:
                return self._result(
                    status="error",
                    message=f"{tool_name} failed during import-mode execution.",
                    error=f"{type(e).__name__}: {e}",
                    data={"traceback": traceback.format_exc()},
                    guidance="Check argument names and values; verify required dependencies are installed.",
                )

        return self._result(
            status="fallback",
            message=f"{tool_name} import unavailable; CLI fallback suggested.",
            error=meta.get("error"),
            guidance=(
                f"Run command-line tool '{tool_name}' directly in an environment where deepTools is installed, "
                "or fix local imports under source/deeptools."
            ),
        )

    # -------------------------------------------------------------------------
    # Tool methods (one per identified command)
    # -------------------------------------------------------------------------
    def bamCoverage(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute deeptools.bamCoverage."""
        return self._invoke_module("bamCoverage", **kwargs)

    def bamCompare(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute deeptools.bamCompare."""
        return self._invoke_module("bamCompare", **kwargs)

    def computeMatrix(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute deeptools.computeMatrix."""
        return self._invoke_module("computeMatrix", **kwargs)

    def computeMatrixOperations(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute deeptools.computeMatrixOperations."""
        return self._invoke_module("computeMatrixOperations", **kwargs)

    def plotHeatmap(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute deeptools.plotHeatmap."""
        return self._