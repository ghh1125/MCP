import os
import sys
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for Biopython core I/O and alignment surfaces.

    This adapter targets the analyzed modules:
    - source.Bio.SeqIO -> Bio.SeqIO
    - source.Bio.AlignIO -> Bio.AlignIO
    - source.Bio.Align -> Bio.Align

    It provides:
    - Dedicated class instance factory methods for identified classes:
      PairwiseAligner, Alignment, Alignments
    - Dedicated function-call methods for identified functions:
      parse, read, write (for SeqIO / AlignIO / Align)
    - Unified dictionary response format with status field
    - Graceful fallback when import fails
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt module imports.

        Attributes:
            mode (str): Always "import" for this adapter.
            available (bool): True if core imports succeeded.
            import_error (Optional[str]): Captured import error if unavailable.
        """
        self.mode = "import"
        self.available = False
        self.import_error: Optional[str] = None

        self._seqio = None
        self._alignio = None
        self._align = None

        self._import_modules()

    def _import_modules(self) -> None:
        """Attempt importing required modules and classes from repository source tree."""
        try:
            import Bio.SeqIO as seqio_module
            import Bio.AlignIO as alignio_module
            import Bio.Align as align_module

            self._seqio = seqio_module
            self._alignio = alignio_module
            self._align = align_module
            self.available = True
            self.import_error = None
        except Exception as exc:
            self.available = False
            self.import_error = (
                f"Import failed. Ensure repository source is present under '{source_path}' "
                f"and compatible dependencies are installed. Details: {exc}"
            )

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        """Create unified result dictionary."""
        payload = {"status": status, "mode": self.mode}
        payload.update(kwargs)
        return payload

    def _ensure_available(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check adapter availability and return fallback error payload when unavailable."""
        if not self.available:
            return False, self._result(
                "error",
                message=self.import_error
                or "Adapter imports are unavailable. Verify source path and dependencies.",
                actionable_guidance=(
                    "Confirm the 'source' directory exists, includes Bio package, and retry. "
                    "If needed, install optional dependencies required by target format."
                ),
            )
        return True, None

    # -------------------------------------------------------------------------
    # Health and capability methods
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import status.
        """
        if self.available:
            return self._result(
                "ok",
                available=True,
                modules=["Bio.SeqIO", "Bio.AlignIO", "Bio.Align"],
            )
        return self._result(
            "error",
            available=False,
            message=self.import_error,
        )

    # -------------------------------------------------------------------------
    # Class instance factory methods (identified classes from Bio.Align)
    # -------------------------------------------------------------------------
    def create_pairwise_aligner(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a Bio.Align.PairwiseAligner instance.

        Parameters:
            **kwargs: Attributes to set on the newly created aligner, e.g.
                mode="local", match_score=2.0, mismatch_score=-1.0,
                open_gap_score=-0.5, extend_gap_score=-0.1

        Returns:
            dict: Unified status payload with aligner instance under 'instance' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            cls = getattr(self._align, "PairwiseAligner")
            obj = cls()
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return self._result("ok", instance=obj, class_name="PairwiseAligner")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to create PairwiseAligner: {exc}",
                actionable_guidance="Validate aligner parameter names and values.",
            )

    def create_alignment(self, sequences: Any = None, coordinates: Any = None) -> Dict[str, Any]:
        """
        Create a Bio.Align.Alignment instance.

        Parameters:
            sequences: Sequence-like inputs expected by Bio.Align.Alignment.
            coordinates: Optional coordinates array-like object.

        Returns:
            dict: Unified status payload with alignment instance under 'instance' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            cls = getattr(self._align, "Alignment")
            if sequences is not None and coordinates is not None:
                obj = cls(sequences, coordinates)
            elif sequences is not None:
                obj = cls(sequences)
            else:
                obj = cls()
            return self._result("ok", instance=obj, class_name="Alignment")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to create Alignment: {exc}",
                actionable_guidance=(
                    "Provide valid sequences and optional coordinates matching Bio.Align.Alignment expectations."
                ),
            )

    def create_alignments(self, iterable: Any = None) -> Dict[str, Any]:
        """
        Create a Bio.Align.Alignments instance.

        Parameters:
            iterable: Optional iterable of alignment objects.

        Returns:
            dict: Unified status payload with alignments instance under 'instance' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            cls = getattr(self._align, "Alignments")
            obj = cls(iterable) if iterable is not None else cls()
            return self._result("ok", instance=obj, class_name="Alignments")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to create Alignments: {exc}",
                actionable_guidance="Ensure iterable elements are valid alignment objects.",
            )

    # -------------------------------------------------------------------------
    # SeqIO function wrappers: parse/read/write
    # -------------------------------------------------------------------------
    def seqio_parse(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.SeqIO.parse.

        Parameters:
            handle: File path, handle, or text stream.
            format (str): Sequence file format (e.g., 'fasta', 'genbank').
            **kwargs: Extra parser options forwarded to Bio.SeqIO.parse.

        Returns:
            dict: status='ok' with iterator under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._seqio.parse(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.SeqIO", function="parse")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.SeqIO.parse failed: {exc}",
                actionable_guidance="Verify input handle/path and format string.",
            )

    def seqio_read(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.SeqIO.read.

        Parameters:
            handle: File path, handle, or text stream containing exactly one record.
            format (str): Sequence file format.
            **kwargs: Extra options forwarded to Bio.SeqIO.read.

        Returns:
            dict: status='ok' with record under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._seqio.read(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.SeqIO", function="read")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.SeqIO.read failed: {exc}",
                actionable_guidance="Ensure exactly one record exists in input for read().",
            )

    def seqio_write(self, sequences: Any, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.SeqIO.write.

        Parameters:
            sequences: SeqRecord or iterable of SeqRecord objects.
            handle: Output file path or writable handle.
            format (str): Output format.
            **kwargs: Extra options forwarded to Bio.SeqIO.write.

        Returns:
            dict: status='ok' with count under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._seqio.write(sequences, handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.SeqIO", function="write")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.SeqIO.write failed: {exc}",
                actionable_guidance="Validate sequence objects, output handle, and format.",
            )

    # -------------------------------------------------------------------------
    # AlignIO function wrappers: parse/read/write
    # -------------------------------------------------------------------------
    def alignio_parse(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.AlignIO.parse.

        Parameters:
            handle: File path, handle, or text stream.
            format (str): Alignment format (e.g., 'clustal', 'stockholm', 'phylip').
            **kwargs: Extra parser options.

        Returns:
            dict: status='ok' with iterator under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._alignio.parse(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.AlignIO", function="parse")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.AlignIO.parse failed: {exc}",
                actionable_guidance="Check alignment input source and specified format.",
            )

    def alignio_read(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.AlignIO.read.

        Parameters:
            handle: Input file path or handle containing one alignment.
            format (str): Alignment format.
            **kwargs: Extra options.

        Returns:
            dict: status='ok' with alignment object under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._alignio.read(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.AlignIO", function="read")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.AlignIO.read failed: {exc}",
                actionable_guidance="Ensure input contains exactly one alignment.",
            )

    def alignio_write(self, alignments: Any, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.AlignIO.write.

        Parameters:
            alignments: Alignment object or iterable of alignments.
            handle: Output file path or writable handle.
            format (str): Alignment output format.
            **kwargs: Extra options.

        Returns:
            dict: status='ok' with write count under 'result' on success.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._alignio.write(alignments, handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.AlignIO", function="write")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.AlignIO.write failed: {exc}",
                actionable_guidance="Validate alignment objects and output destination.",
            )

    # -------------------------------------------------------------------------
    # Align function wrappers: parse/read/write
    # -------------------------------------------------------------------------
    def align_parse(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.Align.parse.

        Parameters:
            handle: Alignment input source.
            format (str): Format supported by Bio.Align parser.
            **kwargs: Additional parser options.

        Returns:
            dict: status='ok' with iterator or alignment stream under 'result'.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._align.parse(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.Align", function="parse")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.Align.parse failed: {exc}",
                actionable_guidance="Verify format and input compatibility with Bio.Align.",
            )

    def align_read(self, handle: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.Align.read.

        Parameters:
            handle: Input source containing a single alignment item.
            format (str): Expected alignment format.
            **kwargs: Additional read options.

        Returns:
            dict: status='ok' with alignment object under 'result'.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._align.read(handle, format, **kwargs)
            return self._result("ok", result=result, module="Bio.Align", function="read")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.Align.read failed: {exc}",
                actionable_guidance="Ensure a single valid alignment is present in the input.",
            )

    def align_write(self, alignments: Any, target: Any, format: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Call Bio.Align.write.

        Parameters:
            alignments: Alignment or iterable of alignments.
            target: Output destination path or handle.
            format (str): Output format.
            **kwargs: Additional write options.

        Returns:
            dict: status='ok' with write result under 'result'.
        """
        ok, err = self._ensure_available()
        if not ok:
            return err
        try:
            result = self._align.write(alignments, target, format, **kwargs)
            return self._result("ok", result=result, module="Bio.Align", function="write")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Bio.Align.write failed: {exc}",
                actionable_guidance="Check output target permissions and alignment object validity.",
            )