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
    MCP Import-Mode adapter for the Biopython repository.

    This adapter attempts direct module imports from the local `source` directory.
    If import mode is unavailable, methods return actionable fallback guidance.
    All public methods return a unified dictionary with a `status` field.
    """

    # -------------------------------------------------------------------------
    # Initialization and module registry
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._module_paths: Dict[str, str] = {
            "entrez": "Bio.Entrez",
            "medline": "Bio.Medline",
            "seqio": "Bio.SeqIO",
            "alignio": "Bio.AlignIO",
            "phylo": "Bio.Phylo",
            "pdb": "Bio.PDB",
            "blast_ncbiwww": "Bio.Blast.NCBIWWW",
            "blast_ncbixml": "Bio.Blast.NCBIXML",
            "pairwise2": "Bio.pairwise2",
            "motifs": "Bio.motifs",
            "kegg_rest": "Bio.KEGG.REST",
            "expassy": "Bio.ExPASy",
            "swissprot": "Bio.SwissProt",
        }
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status}
        data.update(kwargs)
        return data

    def _load_modules(self) -> None:
        failed = {}
        for key, path in self._module_paths.items():
            try:
                self._modules[key] = importlib.import_module(path)
            except Exception as exc:
                failed[key] = {
                    "module": path,
                    "error": str(exc),
                }
        if failed:
            self.mode = "fallback"
            self._import_errors = failed
        else:
            self._import_errors = {}

    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter status and module import diagnostics.
        """
        return self._result(
            "success",
            mode=self.mode,
            loaded_modules=sorted(self._modules.keys()),
            import_errors=self._import_errors,
            guidance=(
                "If mode is fallback, ensure repository source is available at '<plugin_root>/source' "
                "and that optional dependencies (e.g., numpy) are installed."
            ),
        )

    # -------------------------------------------------------------------------
    # Internal guards
    # -------------------------------------------------------------------------

    def _require_module(self, key: str) -> Dict[str, Any]:
        if self.mode != "import" or key not in self._modules:
            return self._result(
                "error",
                message=f"Module '{self._module_paths.get(key, key)}' is not available in import mode.",
                guidance=(
                    "Verify source path injection and local repository checkout. "
                    "Then retry adapter initialization."
                ),
            )
        return self._result("success", module=self._modules[key])

    # -------------------------------------------------------------------------
    # Entrez / Medline
    # -------------------------------------------------------------------------

    def entrez_set_email(self, email: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Configure Entrez credentials.

        Parameters:
            email: Contact email required by NCBI.
            api_key: Optional NCBI API key.

        Returns:
            Unified status dictionary.
        """
        try:
            chk = self._require_module("entrez")
            if chk["status"] != "success":
                return chk
            mod = chk["module"]
            mod.email = email
            if api_key:
                mod.api_key = api_key
            return self._result("success", configured=True, email=email, api_key_set=bool(api_key))
        except Exception as exc:
            return self._result("error", message=str(exc), traceback=traceback.format_exc())

    def entrez_esearch(self, db: str, term: str, retmax: int = 20) -> Dict[str, Any]:
        try:
            chk = self._require_module("entrez")
            if chk["status"] != "success":
                return chk
            e = chk["module"]
            handle = e.esearch(db=db, term=term, retmax=retmax)
            data = e.read(handle)
            handle.close()
            return self._result("success", data=data)
        except Exception as exc:
            return self._result(
                "error",
                message=f"Entrez esearch failed: {exc}",
                guidance="Ensure network connectivity and valid Entrez email/API key configuration.",
            )

    def medline_parse_records(self, text_path: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("medline")
            if chk["status"] != "success":
                return chk
            med = chk["module"]
            with open(text_path, "r", encoding="utf-8") as f:
                records = list(med.parse(f))
            return self._result("success", count=len(records), records=records)
        except Exception as exc:
            return self._result("error", message=f"Medline parse failed: {exc}")

    # -------------------------------------------------------------------------
    # Sequence I/O
    # -------------------------------------------------------------------------

    def seqio_parse(self, file_path: str, fmt: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("seqio")
            if chk["status"] != "success":
                return chk
            seqio = chk["module"]
            records = list(seqio.parse(file_path, fmt))
            return self._result("success", count=len(records), records=records)
        except Exception as exc:
            return self._result(
                "error",
                message=f"SeqIO parse failed: {exc}",
                guidance="Check file path and format (e.g., fasta, genbank, fastq).",
            )

    def seqio_write(self, records: List[Any], file_path: str, fmt: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("seqio")
            if chk["status"] != "success":
                return chk
            seqio = chk["module"]
            written = seqio.write(records, file_path, fmt)
            return self._result("success", written=written, output=file_path)
        except Exception as exc:
            return self._result("error", message=f"SeqIO write failed: {exc}")

    # -------------------------------------------------------------------------
    # Alignment I/O and pairwise alignment
    # -------------------------------------------------------------------------

    def alignio_read(self, file_path: str, fmt: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("alignio")
            if chk["status"] != "success":
                return chk
            alignio = chk["module"]
            aln = alignio.read(file_path, fmt)
            return self._result("success", alignment=aln, length=getattr(aln, "get_alignment_length", lambda: None)())
        except Exception as exc:
            return self._result("error", message=f"AlignIO read failed: {exc}")

    def pairwise2_globalxx(self, seq_a: str, seq_b: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("pairwise2")
            if chk["status"] != "success":
                return chk
            p2 = chk["module"]
            alignments = p2.align.globalxx(seq_a, seq_b)
            return self._result("success", count=len(alignments), alignments=alignments)
        except Exception as exc:
            return self._result("error", message=f"Pairwise alignment failed: {exc}")

    # -------------------------------------------------------------------------
    # BLAST
    # -------------------------------------------------------------------------

    def blast_qblast(self, program: str, database: str, sequence: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            chk = self._require_module("blast_ncbiwww")
            if chk["status"] != "success":
                return chk
            ncbiwww = chk["module"]
            handle = ncbiwww.qblast(program, database, sequence, **kwargs)
            xml = handle.read()
            handle.close()
            return self._result("success", xml=xml)
        except Exception as exc:
            return self._result(
                "error",
                message=f"qblast failed: {exc}",
                guidance="Check internet access and NCBI service limits. Retry with smaller query.",
            )

    def blast_parse_xml_file(self, xml_file: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("blast_ncbixml")
            if chk["status"] != "success":
                return chk
            ncbixml = chk["module"]
            with open(xml_file, "r", encoding="utf-8") as f:
                records = list(ncbixml.parse(f))
            return self._result("success", count=len(records), records=records)
        except Exception as exc:
            return self._result("error", message=f"BLAST XML parse failed: {exc}")

    # -------------------------------------------------------------------------
    # Phylogenetics
    # -------------------------------------------------------------------------

    def phylo_read(self, file_path: str, fmt: str = "newick") -> Dict[str, Any]:
        try:
            chk = self._require_module("phylo")
            if chk["status"] != "success":
                return chk
            phylo = chk["module"]
            tree = phylo.read(file_path, fmt)
            return self._result("success", tree=tree)
        except Exception as exc:
            return self._result("error", message=f"Phylo read failed: {exc}")

    # -------------------------------------------------------------------------
    # PDB
    # -------------------------------------------------------------------------

    def pdb_parse_structure(self, structure_id: str, pdb_file: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("pdb")
            if chk["status"] != "success":
                return chk
            pdb_mod = chk["module"]
            parser = pdb_mod.PDBParser(QUIET=True)
            structure = parser.get_structure(structure_id, pdb_file)
            return self._result("success", structure=structure)
        except Exception as exc:
            return self._result("error", message=f"PDB parse failed: {exc}")

    # -------------------------------------------------------------------------
    # Motifs / KEGG / ExPASy / SwissProt
    # -------------------------------------------------------------------------

    def motifs_create(self, instances: List[str]) -> Dict[str, Any]:
        try:
            chk = self._require_module("motifs")
            if chk["status"] != "success":
                return chk
            motifs = chk["module"]
            motif = motifs.create(instances)
            return self._result("success", motif=motif)
        except Exception as exc:
            return self._result("error", message=f"Motif creation failed: {exc}")

    def kegg_list(self, database: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("kegg_rest")
            if chk["status"] != "success":
                return chk
            rest = chk["module"]
            handle = rest.kegg_list(database)
            text = handle.read()
            handle.close()
            return self._result("success", data=text)
        except Exception as exc:
            return self._result("error", message=f"KEGG list failed: {exc}")

    def expasy_get_prosite_raw(self, prosite_id: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("expassy")
            if chk["status"] != "success":
                return chk
            expasy = chk["module"]
            handle = expasy.get_prosite_raw(prosite_id)
            text = handle.read()
            handle.close()
            return self._result("success", data=text)
        except Exception as exc:
            return self._result("error", message=f"ExPASy request failed: {exc}")

    def swissprot_parse(self, file_path: str) -> Dict[str, Any]:
        try:
            chk = self._require_module("swissprot")
            if chk["status"] != "success":
                return chk
            sp = chk["module"]
            with open(file_path, "r", encoding="utf-8") as f:
                records = list(sp.parse(f))
            return self._result("success", count=len(records), records=records)
        except Exception as exc:
            return self._result("error", message=f"SwissProt parse failed: {exc}")