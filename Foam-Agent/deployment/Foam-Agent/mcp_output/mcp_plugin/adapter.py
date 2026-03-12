import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for Foam-Agent MCP plugin integration.

    This adapter prioritizes direct Python imports and provides graceful fallback
    guidance for CLI execution when imports fail or runtime dependencies are missing.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._load_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        guidance: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
            "error": error,
            "guidance": guidance or [],
        }

    def _load_one(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
            self._load_errors.pop(key, None)
        except Exception as exc:
            self._modules[key] = None
            self._load_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_modules(self) -> None:
        # Full package paths mapped from analysis (source prefix removed by sys.path rule).
        self._load_one("init_database", "init_database")
        self._load_one("foambench_main", "foambench_main")
        self._load_one("faiss_tutorials_structure", "database.script.faiss_tutorials_structure")
        self._load_one("faiss_tutorials_details", "database.script.faiss_tutorials_details")
        self._load_one("start_mcp", "src.mcp.start_mcp")
        self._load_one("src_main", "src.main")
        self._load_one("app", "app")

    def health(self) -> Dict[str, Any]:
        """
        Report adapter and module import health.

        Returns:
            dict: Unified status dictionary with loaded modules and import errors.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        failed = {k: v for k, v in self._load_errors.items()}
        if failed:
            return self._result(
                status="partial",
                message="Adapter initialized with partial module availability.",
                data={"loaded_modules": loaded, "failed_modules": failed},
                guidance=[
                    "Install project dependencies from environment.yml.",
                    "Ensure Python version is 3.10 or higher.",
                    "Verify system-level OpenFOAM and optional runtime tools are installed.",
                ],
            )
        return self._result(
            status="ok",
            message="Adapter initialized successfully. All target modules are importable.",
            data={"loaded_modules": loaded},
        )

    # -------------------------------------------------------------------------
    # Utility execution helpers
    # -------------------------------------------------------------------------
    def _invoke(self, module_key: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                status="fallback",
                message=f"Module '{module_key}' is not importable in import mode.",
                error=self._load_errors.get(module_key, "Unknown import failure."),
                guidance=self._fallback_guidance(module_key),
            )
        fn = getattr(mod, func_name, None)
        if fn is None:
            return self._result(
                status="error",
                message=f"Function '{func_name}' is not available in module '{module_key}'.",
                guidance=[
                    "Verify repository version and function name.",
                    "Run health() to inspect loaded modules.",
                ],
            )
        try:
            result = fn(*args, **kwargs)
            return self._result(
                status="ok",
                message=f"Executed {module_key}.{func_name} successfully.",
                data={"result": result},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Execution failed for {module_key}.{func_name}.",
                error=f"{type(exc).__name__}: {exc}",
                data={"traceback": traceback.format_exc()},
                guidance=[
                    "Check input arguments and runtime environment variables.",
                    "Confirm optional dependencies (OpenFOAM, FAISS, OpenAI, Slurm tools) are available.",
                ],
            )

    def _fallback_guidance(self, module_key: str) -> List[str]:
        mapping = {
            "start_mcp": ["Use CLI fallback: python src/mcp/start_mcp.py"],
            "src_main": ["Use CLI fallback: python src/main.py"],
            "app": ["Use CLI fallback: python app.py"],
            "init_database": ["Use CLI fallback: python init_database.py"],
            "foambench_main": ["Use CLI fallback: python foambench_main.py"],
        }
        return mapping.get(module_key, ["Use CLI fallback by running the corresponding script directly."])

    # -------------------------------------------------------------------------
    # init_database module wrappers
    # -------------------------------------------------------------------------
    def init_database_run_command(self, command: str) -> Dict[str, Any]:
        """
        Execute init_database.run_command.

        Args:
            command: Shell command to execute as expected by the upstream function.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("init_database", "run_command", command)

    def init_database_parse_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute init_database.parse_args.

        Args:
            args: Optional CLI-style argument list. If None, upstream defaults are used.

        Returns:
            dict: Unified status dictionary containing parsed arguments object.
        """
        if args is None:
            return self._invoke("init_database", "parse_args")
        return self._invoke("init_database", "parse_args", args)

    def init_database_main(self) -> Dict[str, Any]:
        """
        Execute init_database.main to initialize/refresh database assets.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("init_database", "main")

    # -------------------------------------------------------------------------
    # foambench_main module wrappers
    # -------------------------------------------------------------------------
    def foambench_run_command(self, command: str) -> Dict[str, Any]:
        """
        Execute foambench_main.run_command.

        Args:
            command: Shell command string.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("foambench_main", "run_command", command)

    def foambench_parse_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute foambench_main.parse_args.

        Args:
            args: Optional argument list.

        Returns:
            dict: Unified status dictionary with parser output.
        """
        if args is None:
            return self._invoke("foambench_main", "parse_args")
        return self._invoke("foambench_main", "parse_args", args)

    def foambench_main(self) -> Dict[str, Any]:
        """
        Execute foambench_main.main benchmark pipeline entrypoint.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("foambench_main", "main")

    # -------------------------------------------------------------------------
    # database.script.faiss_tutorials_structure wrappers
    # -------------------------------------------------------------------------
    def faiss_structure_tokenize(self, text: str) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_structure.tokenize.

        Args:
            text: Input text to tokenize.

        Returns:
            dict: Unified status dictionary with tokenization output.
        """
        return self._invoke("faiss_tutorials_structure", "tokenize", text)

    def faiss_structure_extract_field(self, data: Any, field: str) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_structure.extract_field.

        Args:
            data: Parsed record or structure object expected by upstream function.
            field: Field name to extract.

        Returns:
            dict: Unified status dictionary with extracted field content.
        """
        return self._invoke("faiss_tutorials_structure", "extract_field", data, field)

    def faiss_structure_main(self) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_structure.main.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("faiss_tutorials_structure", "main")

    # -------------------------------------------------------------------------
    # database.script.faiss_tutorials_details wrappers
    # -------------------------------------------------------------------------
    def faiss_details_tokenize(self, text: str) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_details.tokenize.

        Args:
            text: Input text to tokenize.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("faiss_tutorials_details", "tokenize", text)

    def faiss_details_extract_field(self, data: Any, field: str) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_details.extract_field.

        Args:
            data: Input structured content.
            field: Target field key to extract.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("faiss_tutorials_details", "extract_field", data, field)

    def faiss_details_main(self) -> Dict[str, Any]:
        """
        Execute faiss_tutorials_details.main.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("faiss_tutorials_details", "main")

    # -------------------------------------------------------------------------
    # Entrypoint wrappers derived from CLI analysis
    # -------------------------------------------------------------------------
    def start_mcp(self) -> Dict[str, Any]:
        """
        Execute MCP server startup entrypoint from src.mcp.start_mcp.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("start_mcp", "main")

    def run_src_main(self) -> Dict[str, Any]:
        """
        Execute primary orchestration entrypoint from src.main.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("src_main", "main")

    def run_app(self) -> Dict[str, Any]:
        """
        Execute top-level app entrypoint from app.py.

        Returns:
            dict: Unified status dictionary.
        """
        return self._invoke("app", "main")