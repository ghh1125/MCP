import os
import sys
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
    MCP import-mode adapter for the biotite repository.

    This adapter attempts to import the repository package directly from the local
    `source` directory and exposes a consistent execution interface with unified
    response dictionaries.

    Design notes:
    - Primary mode: import
    - Fallback mode: blackbox (graceful guidance if import/call is unavailable)
    - Unified response format: {"status": "...", ...}
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state and attempt core imports.

        Attributes:
            mode (str): Current operation mode. "import" by default.
            package_name (str): Target repository package root.
            modules (dict): Cache of imported modules by fully-qualified path.
            errors (list): Collected import/call errors for diagnostics.
            available (bool): Whether core package import succeeded.
        """
        self.mode: str = "import"
        self.package_name: str = "biotite"
        self.modules: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.available: bool = False

        self._import_core_modules()

    def _ok(self, **payload: Any) -> Dict[str, Any]:
        payload.setdefault("status", "success")
        payload.setdefault("mode", self.mode)
        return payload

    def _fail(self, message: str, **payload: Any) -> Dict[str, Any]:
        payload.setdefault("status", "error")
        payload.setdefault("mode", self.mode)
        payload.setdefault("message", message)
        return payload

    def _import_module(self, module_path: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        """
        Import a module by fully-qualified path and cache it.

        Parameters:
            module_path (str): Fully-qualified Python module path.

        Returns:
            tuple: (success, module_or_none, error_or_none)
        """
        try:
            module = importlib.import_module(module_path)
            self.modules[module_path] = module
            return True, module, None
        except Exception as exc:
            err = f"Failed to import '{module_path}': {exc}"
            self.errors.append(err)
            return False, None, err

    def _import_core_modules(self) -> None:
        """
        Import a broad set of high-value repository modules based on analysis.
        """
        core_candidates = [
            "biotite",
            "biotite.sequence",
            "biotite.sequence.align",
            "biotite.sequence.io",
            "biotite.sequence.io.fasta",
            "biotite.sequence.io.fastq",
            "biotite.sequence.io.genbank",
            "biotite.sequence.io.gff",
            "biotite.structure",
            "biotite.structure.io",
            "biotite.structure.io.pdb",
            "biotite.structure.io.pdbx",
            "biotite.structure.io.mol",
            "biotite.database",
            "biotite.database.rcsb",
            "biotite.database.uniprot",
            "biotite.database.entrez",
            "biotite.database.pubchem",
            "biotite.application",
            "biotite.interface",
        ]
        success_count = 0
        for mod in core_candidates:
            ok, _, _ = self._import_module(mod)
            if ok:
                success_count += 1

        self.available = success_count > 0
        if not self.available:
            self.mode = "blackbox"

    # -------------------------------------------------------------------------
    # Status, diagnostics, and discovery
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload with mode, availability, and errors.
        """
        return self._ok(
            available=self.available,
            package=self.package_name,
            imported_modules=sorted(self.modules.keys()),
            error_count=len(self.errors),
            errors=self.errors[-20:],
            guidance=(
                "If imports fail, verify the repository is present under 'source/' "
                "and contains the 'biotite' package."
            ),
        )

    def list_modules(self) -> Dict[str, Any]:
        """
        List currently cached modules.

        Returns:
            dict: Unified status payload with module names.
        """
        return self._ok(modules=sorted(self.modules.keys()), count=len(self.modules))

    def list_public_members(self, module_path: str) -> Dict[str, Any]:
        """
        List public members for a given module.

        Parameters:
            module_path (str): Fully-qualified module path.

        Returns:
            dict: Unified status payload with public attributes.
        """
        ok, module, err = self._import_module(module_path)
        if not ok or module is None:
            return self._fail(
                f"Could not inspect module '{module_path}'.",
                detail=err,
                guidance="Check module path spelling and repository layout.",
            )
        members = [name for name in dir(module) if not name.startswith("_")]
        return self._ok(module=module_path, members=members, count=len(members))

    # -------------------------------------------------------------------------
    # Generic execution primitives (rich coverage fallback for unknown symbols)
    # -------------------------------------------------------------------------
    def call_function(
        self,
        module_path: str,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call a function from a module by name.

        Parameters:
            module_path (str): Fully-qualified module path.
            function_name (str): Public function name.
            *args: Positional arguments for function call.
            **kwargs: Keyword arguments for function call.

        Returns:
            dict: Unified status payload with function result.
        """
        if self.mode != "import":
            return self._fail(
                "Import mode is unavailable; running in fallback mode.",
                guidance="Fix source path/import errors and retry.",
            )
        ok, module, err = self._import_module(module_path)
        if not ok or module is None:
            return self._fail(
                f"Failed to import module '{module_path}'.",
                detail=err,
                guidance="Ensure the module exists and dependencies are installed.",
            )
        func = getattr(module, function_name, None)
        if func is None or not callable(func):
            return self._fail(
                f"Function '{function_name}' not found or not callable in '{module_path}'.",
                guidance="Use list_public_members() to discover valid call targets.",
            )
        try:
            result = func(*args, **kwargs)
            return self._ok(
                module=module_path,
                function=function_name,
                result=result,
            )
        except Exception as exc:
            return self._fail(
                f"Function call failed for '{module_path}.{function_name}'.",
                detail=str(exc),
                guidance="Validate argument types/shapes and optional dependency availability.",
            )

    def create_instance(
        self,
        module_path: str,
        class_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create an instance of a class from a module by name.

        Parameters:
            module_path (str): Fully-qualified module path.
            class_name (str): Public class name.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload with created instance.
        """
        if self.mode != "import":
            return self._fail(
                "Import mode is unavailable; running in fallback mode.",
                guidance="Fix source path/import errors and retry.",
            )
        ok, module, err = self._import_module(module_path)
        if not ok or module is None:
            return self._fail(
                f"Failed to import module '{module_path}'.",
                detail=err,
                guidance="Ensure the module exists and dependencies are installed.",
            )
        cls = getattr(module, class_name, None)
        if cls is None or not inspect.isclass(cls):
            return self._fail(
                f"Class '{class_name}' not found in '{module_path}'.",
                guidance="Use list_public_members() to discover valid class targets.",
            )
        try:
            instance = cls(*args, **kwargs)
            return self._ok(module=module_path, class_name=class_name, instance=instance)
        except Exception as exc:
            return self._fail(
                f"Failed to instantiate '{module_path}.{class_name}'.",
                detail=str(exc),
                guidance="Check constructor arguments and required optional dependencies.",
            )

    # -------------------------------------------------------------------------
    # Biotite-focused convenience methods (high-utility APIs)
    # -------------------------------------------------------------------------
    def create_sequence(self, sequence_text: str, seq_type: str = "protein") -> Dict[str, Any]:
        """
        Create a Biotite sequence object.

        Parameters:
            sequence_text (str): Raw sequence symbols.
            seq_type (str): One of {"protein", "nucleotide"}.

        Returns:
            dict: Unified status payload with sequence object.
        """
        module_path = "biotite.sequence"
        class_name = "ProteinSequence" if seq_type.lower() == "protein" else "NucleotideSequence"
        return self.create_instance(module_path, class_name, sequence_text)

    def load_fasta(self, path: str) -> Dict[str, Any]:
        """
        Read FASTA file via biotite.sequence.io.fasta.

        Parameters:
            path (str): Input FASTA file path.

        Returns:
            dict: Unified status payload with parsed file object.
        """
        return self.call_function("biotite.sequence.io.fasta", "FastaFile", path)

    def fetch_rcsb(self, pdb_id: str, file_format: str = "pdb") -> Dict[str, Any]:
        """
        Fetch structure file from RCSB using biotite.database.rcsb.download.

        Parameters:
            pdb_id (str): PDB identifier.
            file_format (str): Target format, e.g., "pdb", "cif", "bcif".

        Returns:
            dict: Unified status payload with download result.
        """
        return self.call_function(
            "biotite.database.rcsb.download",
            "fetch",
            pdb_id,
            format=file_format,
        )

    def pairwise_align(
        self,
        seq_a: Any,
        seq_b: Any,
        matrix_name: str = "BLOSUM62",
    ) -> Dict[str, Any]:
        """
        Run pairwise alignment using biotite.sequence.align facilities.

        Parameters:
            seq_a (Any): First Biotite sequence object.
            seq_b (Any): Second Biotite sequence object.
            matrix_name (str): Substitution matrix name.

        Returns:
            dict: Unified status payload with alignments.
        """
        matrix_resp = self.call_function(
            "biotite.sequence.align",
            "SubstitutionMatrix",
            seq_a.get_alphabet(),
            seq_b.get_alphabet(),
            matrix_name,
        )
        if matrix_resp.get("status") != "success":
            return matrix_resp
        matrix = matrix_resp["result"]
        return self.call_function(
            "biotite.sequence.align",
            "align_optimal",
            seq_a,
            seq_b,
            matrix,
        )