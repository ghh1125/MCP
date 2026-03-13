import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from pymatgen.core import Structure
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDEntry
from pymatgen.analysis.reaction_calculator import Reaction
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.analysis.local_env import CrystalNN
from pymatgen.analysis.diffraction.xrd import XRDCalculator

mcp = FastMCP("pymatgen_core_service")


@mcp.tool(
    name="parse_structure_from_cif",
    description="Parse a crystal structure from CIF text and return basic metadata.",
)
def parse_structure_from_cif(cif_text: str) -> dict[str, Any]:
    """
    Parse CIF text into a pymatgen Structure.

    Parameters:
        cif_text: Full CIF file content as a string.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        structure = Structure.from_str(cif_text, fmt="cif")
        result = {
            "formula": structure.composition.reduced_formula,
            "num_sites": len(structure),
            "lattice": structure.lattice.matrix.tolist(),
            "species": [str(site.specie) for site in structure],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="structure_match",
    description="Compare two structures and report whether they match under symmetry/tolerance rules.",
)
def structure_match(
    structure_a_cif: str,
    structure_b_cif: str,
    ltol: float = 0.2,
    stol: float = 0.3,
    angle_tol: float = 5.0,
    primitive_cell: bool = True,
    scale: bool = True,
) -> dict[str, Any]:
    """
    Check if two CIF structures are equivalent using StructureMatcher.

    Parameters:
        structure_a_cif: CIF text for first structure.
        structure_b_cif: CIF text for second structure.
        ltol: Fractional length tolerance.
        stol: Site tolerance (normalized).
        angle_tol: Angle tolerance in degrees.
        primitive_cell: Whether to reduce to primitive cell before matching.
        scale: Whether to allow volume scaling.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        s1 = Structure.from_str(structure_a_cif, fmt="cif")
        s2 = Structure.from_str(structure_b_cif, fmt="cif")
        matcher = StructureMatcher(
            ltol=ltol,
            stol=stol,
            angle_tol=angle_tol,
            primitive_cell=primitive_cell,
            scale=scale,
        )
        is_match = matcher.fit(s1, s2)
        return {"success": True, "result": {"match": bool(is_match)}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="analyze_local_environment",
    description="Compute local coordination environment for a site using CrystalNN.",
)
def analyze_local_environment(
    structure_cif: str,
    site_index: int,
) -> dict[str, Any]:
    """
    Analyze nearest-neighbor environment for one site.

    Parameters:
        structure_cif: CIF text for the structure.
        site_index: Zero-based index of the target site.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        structure = Structure.from_str(structure_cif, fmt="cif")
        if site_index < 0 or site_index >= len(structure):
            raise IndexError("site_index out of bounds")
        cnn = CrystalNN()
        nn_info = cnn.get_nn_info(structure, site_index)
        neighbors = []
        for item in nn_info:
            neighbors.append(
                {
                    "site_index": int(item["site_index"]),
                    "species": str(item["site"].specie),
                    "weight": float(item.get("weight", 1.0)),
                }
            )
        return {
            "success": True,
            "result": {"site_index": site_index, "neighbors": neighbors},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="simulate_xrd_pattern",
    description="Simulate an XRD pattern from a CIF structure.",
)
def simulate_xrd_pattern(
    structure_cif: str,
    two_theta_min: float = 0.0,
    two_theta_max: float = 90.0,
    wavelength: str = "CuKa",
) -> dict[str, Any]:
    """
    Generate XRD peak positions and intensities.

    Parameters:
        structure_cif: CIF text for the structure.
        two_theta_min: Minimum 2-theta angle.
        two_theta_max: Maximum 2-theta angle.
        wavelength: X-ray wavelength label accepted by pymatgen (e.g., CuKa).

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        structure = Structure.from_str(structure_cif, fmt="cif")
        calc = XRDCalculator(wavelength=wavelength)
        pattern = calc.get_pattern(structure, two_theta_range=(two_theta_min, two_theta_max))
        result = {
            "x": [float(v) for v in pattern.x],
            "y": [float(v) for v in pattern.y],
            "hkls": [[dict(h) for h in hkl_group] for hkl_group in pattern.hkls],
            "d_hkls": [float(v) for v in pattern.d_hkls],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="balance_reaction",
    description="Balance a chemical reaction from reactant and product formulas.",
)
def balance_reaction(
    reactants: list[str],
    products: list[str],
) -> dict[str, Any]:
    """
    Balance a reaction using pymatgen Reaction.

    Parameters:
        reactants: List of reactant formula strings.
        products: List of product formula strings.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        rxn = Reaction(reactants, products)
        coeffs = [float(c) for c in rxn.coeffs]
        return {
            "success": True,
            "result": {
                "balanced_reaction": str(rxn),
                "coefficients": coeffs,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="phase_diagram_stability",
    description="Compute phase diagram and energy above hull for target composition.",
)
def phase_diagram_stability(
    entries: list[dict[str, float]],
    target_formula: str,
) -> dict[str, Any]:
    """
    Build phase diagram from entries and evaluate target composition stability.

    Parameters:
        entries: List of dicts each with keys: formula (str), energy (float).
        target_formula: Reduced formula to evaluate against hull.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        pd_entries: list[PDEntry] = []
        for item in entries:
            formula = str(item["formula"])
            energy = float(item["energy"])
            pd_entries.append(PDEntry(formula, energy))
        pd = PhaseDiagram(pd_entries)

        target_candidates = [e for e in pd_entries if e.composition.reduced_formula == target_formula]
        if not target_candidates:
            raise ValueError(f"Target formula '{target_formula}' not found in entries")

        target_entry = min(target_candidates, key=lambda e: e.energy_per_atom)
        ehull = float(pd.get_e_above_hull(target_entry))
        decomp = pd.get_decomp_and_e_above_hull(target_entry)[0]
        decomposition = {k.composition.reduced_formula: float(v) for k, v in decomp.items()}

        return {
            "success": True,
            "result": {
                "target_formula": target_formula,
                "energy_above_hull": ehull,
                "decomposition": decomposition,
                "is_stable": ehull <= 1e-8,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()