import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the gensim repository.

    This adapter prefers direct imports from the local source tree and provides
    graceful error-handling with consistent dictionary responses.
    """

    # -------------------------------------------------------------------------
    # Initialization & Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: str = "", details: str = "") -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "guidance": guidance or "Verify repository source path and required dependencies.",
            "details": details,
        }

    def _load_modules(self) -> None:
        module_names = {
            "glove2word2vec": "gensim.scripts.glove2word2vec",
            "word2vec2tensor": "gensim.scripts.word2vec2tensor",
            "word2vec_standalone": "gensim.scripts.word2vec_standalone",
            "segment_wiki": "gensim.scripts.segment_wiki",
            "make_wikicorpus": "gensim.scripts.make_wikicorpus",
            "downloader": "gensim.downloader",
        }
        for key, mod_name in module_names.items():
            try:
                self._modules[key] = importlib.import_module(mod_name)
            except Exception as exc:
                self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter import health and availability of key modules.

        Returns:
            dict: Unified status dictionary with loaded modules and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(list(self._modules.keys())),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            message="health check completed",
        )

    # -------------------------------------------------------------------------
    # Script Wrappers: gensim.scripts.glove2word2vec
    # -------------------------------------------------------------------------
    def call_glove2word2vec(self, glove_input_file: str, word2vec_output_file: str) -> Dict[str, Any]:
        """
        Convert vectors from GloVe format to word2vec text format.

        Parameters:
            glove_input_file (str): Path to input GloVe file.
            word2vec_output_file (str): Output file path for converted vectors.

        Returns:
            dict: status, return value and metadata.
        """
        mod = self._modules.get("glove2word2vec")
        if not mod:
            return self._err(
                "Module gensim.scripts.glove2word2vec is unavailable.",
                "Ensure local source is present and dependencies (numpy, scipy, smart_open) are installed.",
                self._import_errors.get("glove2word2vec", ""),
            )
        try:
            fn = getattr(mod, "glove2word2vec", None)
            if fn is None:
                return self._err(
                    "Function glove2word2vec was not found in gensim.scripts.glove2word2vec.",
                    "Check repository version compatibility and script implementation.",
                )
            result = fn(glove_input_file, word2vec_output_file)
            return self._ok({"result": result}, "conversion completed")
        except Exception as exc:
            return self._err(
                "Failed to convert GloVe vectors.",
                "Validate file paths and file encoding; confirm readable input and writable output.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Script Wrappers: gensim.scripts.word2vec2tensor
    # -------------------------------------------------------------------------
    def call_word2vec2tensor(
        self,
        model_path: str,
        output_path: str,
        binary: bool = False,
    ) -> Dict[str, Any]:
        """
        Export word2vec embeddings to TensorBoard-compatible tensor and metadata files.

        Parameters:
            model_path (str): Path to word2vec model/vectors file.
            output_path (str): Directory or output prefix used by the script logic.
            binary (bool): Whether input vectors are binary word2vec format.

        Returns:
            dict: status and execution details.
        """
        mod = self._modules.get("word2vec2tensor")
        if not mod:
            return self._err(
                "Module gensim.scripts.word2vec2tensor is unavailable.",
                "Ensure local source is present and dependencies are installed.",
                self._import_errors.get("word2vec2tensor", ""),
            )
        try:
            run = getattr(mod, "word2vec2tensor", None) or getattr(mod, "run", None)
            if run is None:
                return self._err(
                    "No callable export function found in gensim.scripts.word2vec2tensor.",
                    "Inspect script for available API functions in this repository version.",
                )
            result = run(model_path, output_path, binary=binary)
            return self._ok({"result": result}, "tensor export completed")
        except TypeError:
            try:
                result = run(model_path, output_path)
                return self._ok({"result": result}, "tensor export completed (without binary argument)")
            except Exception as exc:
                return self._err(
                    "Failed to export vectors to TensorBoard format.",
                    "Check input model path and output directory permissions.",
                    f"{type(exc).__name__}: {exc}",
                )
        except Exception as exc:
            return self._err(
                "Failed to export vectors to TensorBoard format.",
                "Check input model path and output directory permissions.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Script Wrappers: gensim.scripts.word2vec_standalone
    # -------------------------------------------------------------------------
    def call_word2vec_standalone(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute standalone word2vec script entry logic if exposed as import-callable API.

        Parameters:
            argv (list[str], optional): CLI-like argument list for underlying function.

        Returns:
            dict: status and function execution results.
        """
        mod = self._modules.get("word2vec_standalone")
        if not mod:
            return self._err(
                "Module gensim.scripts.word2vec_standalone is unavailable.",
                "Ensure local source is present and dependencies are installed.",
                self._import_errors.get("word2vec_standalone", ""),
            )
        try:
            fn = getattr(mod, "main", None) or getattr(mod, "run", None)
            if fn is None:
                return self._err(
                    "No callable main/run function found in gensim.scripts.word2vec_standalone.",
                    "Use CLI fallback externally if this script only supports __main__ execution.",
                )
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "word2vec standalone execution completed")
        except Exception as exc:
            return self._err(
                "Failed to execute word2vec_standalone.",
                "Pass valid arguments and confirm training data paths in argv.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Script Wrappers: gensim.scripts.segment_wiki
    # -------------------------------------------------------------------------
    def call_segment_wiki(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute Wikipedia segmentation/preprocessing script via import-callable interface.

        Parameters:
            argv (list[str], optional): CLI-like arguments for script main function.

        Returns:
            dict: status and execution result.
        """
        mod = self._modules.get("segment_wiki")
        if not mod:
            return self._err(
                "Module gensim.scripts.segment_wiki is unavailable.",
                "Ensure local source is present and dependencies are installed.",
                self._import_errors.get("segment_wiki", ""),
            )
        try:
            fn = getattr(mod, "main", None) or getattr(mod, "run", None)
            if fn is None:
                return self._err(
                    "No callable main/run function found in gensim.scripts.segment_wiki.",
                    "Use CLI fallback externally if this script only supports direct execution.",
                )
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "wiki segmentation execution completed")
        except Exception as exc:
            return self._err(
                "Failed to execute segment_wiki.",
                "Verify Wikipedia dump paths and output parameters.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Script Wrappers: gensim.scripts.make_wikicorpus
    # -------------------------------------------------------------------------
    def call_make_wikicorpus(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute wiki corpus builder script via import-callable interface.

        Parameters:
            argv (list[str], optional): CLI-like argument list.

        Returns:
            dict: status and execution details.
        """
        mod = self._modules.get("make_wikicorpus")
        if not mod:
            return self._err(
                "Module gensim.scripts.make_wikicorpus is unavailable.",
                "Ensure local source is present and dependencies are installed.",
                self._import_errors.get("make_wikicorpus", ""),
            )
        try:
            fn = getattr(mod, "main", None) or getattr(mod, "run", None)
            if fn is None:
                return self._err(
                    "No callable main/run function found in gensim.scripts.make_wikicorpus.",
                    "Use CLI fallback externally if this script only supports direct execution.",
                )
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "wikicorpus build execution completed")
        except Exception as exc:
            return self._err(
                "Failed to execute make_wikicorpus.",
                "Verify input dump path, output path, and available disk space.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Utility Wrappers: gensim.downloader
    # -------------------------------------------------------------------------
    def call_downloader_info(self, name: Optional[str] = None, show_only_latest: bool = True) -> Dict[str, Any]:
        """
        Query gensim-data metadata.

        Parameters:
            name (str, optional): Specific dataset/model name. If None, returns full index.
            show_only_latest (bool): Whether to show only latest versions where supported.

        Returns:
            dict: status and metadata.
        """
        mod = self._modules.get("downloader")
        if not mod:
            return self._err(
                "Module gensim.downloader is unavailable.",
                "Ensure local source is present and requests/smart_open dependencies are available.",
                self._import_errors.get("downloader", ""),
            )
        try:
            fn = getattr(mod, "info", None)
            if fn is None:
                return self._err(
                    "Function info was not found in gensim.downloader.",
                    "Check repository version compatibility.",
                )
            result = fn(name=name, show_only_latest=show_only_latest) if name is not None else fn(show_only_latest=show_only_latest)
            return self._ok({"result": result}, "downloader info retrieved")
        except Exception as exc:
            return self._err(
                "Failed to retrieve downloader info.",
                "Check network availability if remote index fetch is required.",
                f"{type(exc).__name__}: {exc}",
            )

    def call_downloader_load(self, name: str, return_path: bool = False) -> Dict[str, Any]:
        """
        Load or download a dataset/model from gensim-data.

        Parameters:
            name (str): Dataset or model name.
            return_path (bool): Whether to return local path instead of loaded object.

        Returns:
            dict: status and loaded object metadata/path.
        """
        mod = self._modules.get("downloader")
        if not mod:
            return self._err(
                "Module gensim.downloader is unavailable.",
                "Ensure local source is present and downloader dependencies are installed.",
                self._import_errors.get("downloader", ""),
            )
        try:
            fn = getattr(mod, "load", None)
            if fn is None:
                return self._err(
                    "Function load was not found in gensim.downloader.",
                    "Check repository version compatibility.",
                )
            result = fn(name, return_path=return_path)
            return self._ok({"result": result}, "downloader load completed")
        except Exception as exc:
            return self._err(
                "Failed to load requested resource via downloader.",
                "Confirm resource name and network/cache directory permissions.",
                f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Generic Fallback Executor
    # -------------------------------------------------------------------------
    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic function executor for any loaded module.

        Parameters:
            module_key (str): Internal module key loaded by this adapter.
            function_name (str): Function to invoke from that module.
            *args: Positional arguments for target function.
            **kwargs: Keyword arguments for target function.

        Returns:
            dict: unified status response with execution output.
        """
        mod = self._modules.get(module_key)
        if not mod:
            return self._err(
                f"Module '{module_key}' is unavailable.",
                "Run health_check() and fix missing imports before calling this function.",
                self._import_errors.get(module_key, ""),
            )
        try:
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    f"Function '{function_name}' is not available in module '{module_key}'.",
                    "Check function name and repository version; inspect module attributes.",
                )
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, f"{module_key}.{function_name} executed")
        except Exception as exc:
            return self._err(
                f"Execution failed for {module_key}.{function_name}.",
                "Validate input parameters and dependency availability.",
                f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            )