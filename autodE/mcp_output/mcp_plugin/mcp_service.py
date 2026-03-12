import os
import sys
from typing import List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import autode as ade
from autode.species.molecule import Molecule
from autode.reactions.reaction import Reaction
from autode.values import Energy
from autode.wrappers.methods import get_hmethod, get_lmethod

mcp = FastMCP("autode_service")


@mcp.tool(
    name="autode_version",
    description="Get installed autodE package version information",
)
def autode_version() -> dict:
    """
    Return autodE version metadata.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        version = getattr(ade, "__version__", "unknown")
        return {"success": True, "result": {"version": version}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="build_molecule_from_smiles",
    description="Construct a Molecule from a SMILES string",
)
def build_molecule_from_smiles(name: str, smiles: str, charge: int = 0, mult: int = 1) -> dict:
    """
    Build a molecule object from SMILES and return basic metadata.

    Args:
        name: Molecule label.
        smiles: SMILES string.
        charge: Net molecular charge.
        mult: Spin multiplicity.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        mol = Molecule(name=name, smiles=smiles, charge=charge, mult=mult)
        n_atoms = len(mol.atoms) if mol.atoms is not None else 0
        return {
            "success": True,
            "result": {
                "name": mol.name,
                "charge": mol.charge,
                "mult": mol.mult,
                "n_atoms": n_atoms,
                "formula": getattr(mol, "formula", None),
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="molecule_single_point",
    description="Run a single-point energy calculation for a molecule from SMILES",
)
def molecule_single_point(
    name: str,
    smiles: str,
    method_name: str = "xtb",
    charge: int = 0,
    mult: int = 1,
) -> dict:
    """
    Compute a single-point energy for a molecule.

    Args:
        name: Molecule name.
        smiles: Input SMILES.
        method_name: Electronic structure method keyword (e.g., xtb, orca).
        charge: Molecular charge.
        mult: Spin multiplicity.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        mol = Molecule(name=name, smiles=smiles, charge=charge, mult=mult)
        method = get_lmethod(method_name)
        mol.single_point(method=method)
        energy = str(mol.energy) if getattr(mol, "energy", None) is not None else None
        return {
            "success": True,
            "result": {"name": mol.name, "method": method_name, "energy": energy},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="molecule_optimise",
    description="Optimise molecular geometry from SMILES with selected method",
)
def molecule_optimise(
    name: str,
    smiles: str,
    method_name: str = "xtb",
    charge: int = 0,
    mult: int = 1,
) -> dict:
    """
    Run geometry optimisation for a molecule.

    Args:
        name: Molecule name.
        smiles: Input SMILES.
        method_name: Method keyword for optimisation.
        charge: Molecular charge.
        mult: Spin multiplicity.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        mol = Molecule(name=name, smiles=smiles, charge=charge, mult=mult)
        method = get_lmethod(method_name)
        mol.optimise(method=method)
        return {
            "success": True,
            "result": {
                "name": mol.name,
                "method": method_name,
                "optimised": True,
                "energy": str(mol.energy) if getattr(mol, "energy", None) is not None else None,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="reaction_profile",
    description="Create and evaluate a reaction profile from reactant/product SMILES lists",
)
def reaction_profile(
    name: str,
    reactant_smiles: List[str],
    product_smiles: List[str],
    method_name: str = "xtb",
    solvent: Optional[str] = None,
) -> dict:
    """
    Build a reaction and calculate a profile.

    Args:
        name: Reaction name.
        reactant_smiles: List of reactant SMILES.
        product_smiles: List of product SMILES.
        method_name: Method keyword for reaction calculations.
        solvent: Optional implicit solvent name.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        reactants = [Molecule(name=f"r{i}", smiles=s) for i, s in enumerate(reactant_smiles, start=1)]
        products = [Molecule(name=f"p{i}", smiles=s) for i, s in enumerate(product_smiles, start=1)]
        rxn = Reaction(*reactants, *products, name=name, solvent_name=solvent)
        method = get_hmethod(method_name) if method_name.lower() not in {"xtb", "mopac"} else get_lmethod(method_name)
        rxn.calculate_reaction_profile(method=method)
        dg = str(getattr(rxn, "delta_g", None))
        de = str(getattr(rxn, "delta_e", None))
        return {
            "success": True,
            "result": {"name": name, "method": method_name, "delta_g": dg, "delta_e": de},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="available_methods",
    description="Get availability status for common low/high-level computational methods",
)
def available_methods() -> dict:
    """
    Probe common methods and report availability.

    Returns:
        dict: Standard response dictionary with success/result/error fields.
    """
    try:
        low_level = ["xtb", "mopac"]
        high_level = ["orca", "g09", "g16", "qchem", "nwchem"]
        status = {}

        for m in low_level:
            try:
                method = get_lmethod(m)
                status[m] = bool(getattr(method, "is_available", False))
            except Exception:
                status[m] = False

        for m in high_level:
            try:
                method = get_hmethod(m)
                status[m] = bool(getattr(method, "is_available", False))
            except Exception:
                status[m] = False

        return {"success": True, "result": status, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()