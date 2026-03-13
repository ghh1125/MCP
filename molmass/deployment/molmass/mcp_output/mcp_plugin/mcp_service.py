import os
import sys
from typing import Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from molmass.molmass import Formula, from_string, analyze
from molmass.elements import ELEMENTS

mcp = FastMCP("molmass_service")


@mcp.tool(
    name="parse_formula",
    description="Parse a chemical formula string into a canonical representation.",
)
def parse_formula(formula: str) -> Dict[str, Any]:
    """
    Parse a chemical formula string and return normalized/canonical details.

    Parameters:
        formula: Chemical formula string, e.g. 'C8H10N4O2'.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: parsed formula details when successful
        - error: error message when unsuccessful
    """
    try:
        parsed = from_string(formula)
        f = Formula(parsed)
        result = {
            "input": formula,
            "parsed": parsed,
            "expanded": f.expanded,
            "atoms": int(f.atoms),
            "formula": str(f.formula),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="formula_mass",
    description="Compute molecular mass properties for a chemical formula.",
)
def formula_mass(formula: str) -> Dict[str, Any]:
    """
    Compute average and monoisotopic mass information for a chemical formula.

    Parameters:
        formula: Chemical formula string.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: mass-related properties
        - error: error message when unsuccessful
    """
    try:
        f = Formula(from_string(formula))
        result = {
            "formula": str(f.formula),
            "empirical": str(f.empirical),
            "atoms": int(f.atoms),
            "mass": float(f.mass),
            "isotope_mass": float(f.isotope.mass),
            "isotope_abundance": float(f.isotope.abundance),
            "nominal_mass": int(f.isotope.massnumber),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="formula_composition",
    description="Get elemental composition for a chemical formula.",
)
def formula_composition(formula: str, isotopic: bool = True) -> Dict[str, Any]:
    """
    Return elemental composition entries for a formula.

    Parameters:
        formula: Chemical formula string.
        isotopic: Whether to include isotopic composition detail when available.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: list of composition rows
        - error: error message when unsuccessful
    """
    try:
        f = Formula(from_string(formula))
        comp = f.composition(isotopic=isotopic)
        rows = []
        for item in comp.astuple():
            symbol, count, mass, fraction = item
            rows.append(
                {
                    "symbol": symbol,
                    "count": int(count),
                    "mass": float(mass),
                    "fraction": float(fraction),
                }
            )
        return {"success": True, "result": rows, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="formula_spectrum",
    description="Calculate mass distribution (spectrum) for a chemical formula.",
)
def formula_spectrum(formula: str, min_fraction: float = 1e-12) -> Dict[str, Any]:
    """
    Calculate isotopic mass spectrum for a chemical formula.

    Parameters:
        formula: Chemical formula string.
        min_fraction: Minimum fraction threshold for peaks included by backend behavior.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: peak list and related summary
        - error: error message when unsuccessful
    """
    try:
        f = Formula(from_string(formula))
        spectrum = f.spectrum(min_fraction=min_fraction)
        peaks = []
        for mass_number, peak in spectrum.items():
            peaks.append(
                {
                    "mass_number": int(mass_number),
                    "mass": float(peak.mass),
                    "fraction": float(peak.fraction),
                    "intensity": float(peak.intensity),
                    "mz": float(peak.mz),
                }
            )
        result = {
            "formula": str(f.formula),
            "peak_count": len(peaks),
            "peaks": peaks,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="analyze_formula_text",
    description="Run molmass textual analysis report for a formula.",
)
def analyze_formula_text(formula: str, maxatoms: int = 512) -> Dict[str, Any]:
    """
    Generate the standard textual analysis output produced by molmass.

    Parameters:
        formula: Chemical formula string.
        maxatoms: Maximum number of atoms allowed during analysis.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: text report string
        - error: error message when unsuccessful
    """
    try:
        report = analyze(formula, maxatoms=maxatoms)
        return {"success": True, "result": report, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="get_element",
    description="Fetch periodic table metadata for an element by symbol.",
)
def get_element(symbol: str) -> Dict[str, Any]:
    """
    Retrieve element metadata from molmass periodic table data.

    Parameters:
        symbol: Element symbol, e.g. 'C', 'H', 'Na'.

    Returns:
        A dictionary with:
        - success: bool indicating operation status
        - result: selected element properties
        - error: error message when unsuccessful
    """
    try:
        normalized = symbol.strip().capitalize()
        element = ELEMENTS[normalized]
        isotopes = []
        for mass_number, iso in element.isotopes.items():
            isotopes.append(
                {
                    "mass_number": int(mass_number),
                    "mass": float(iso.mass),
                    "abundance": float(iso.abundance),
                    "charge": int(iso.charge),
                }
            )
        result = {
            "symbol": str(element.symbol),
            "name": str(element.name),
            "number": int(element.number),
            "group": int(element.group),
            "period": int(element.period),
            "block": str(element.block),
            "series": int(element.series),
            "mass": float(element.mass),
            "isotopes": isotopes,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()