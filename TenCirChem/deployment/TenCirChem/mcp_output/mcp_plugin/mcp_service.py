import os
import sys
from typing import List, Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

try:
    import numpy as np
except Exception:
    np = None  # type: ignore

try:
    import tencirchem as tcc
except Exception:
    tcc = None  # type: ignore

try:
    from tencirchem.molecule import molecule as build_molecule
except Exception:
    build_molecule = None  # type: ignore

try:
    from tencirchem.static.uccsd import UCCSD
except Exception:
    UCCSD = None  # type: ignore

try:
    from tencirchem.static.kupccgsd import KUPCCGSD
except Exception:
    KUPCCGSD = None  # type: ignore

try:
    from tencirchem.static.puccd import PUCCD
except Exception:
    PUCCD = None  # type: ignore

try:
    from tencirchem.static.hea import HEA
except Exception:
    HEA = None  # type: ignore

try:
    from tencirchem.dynamic.model.sbm import get_ham_terms as sbm_get_ham_terms
except Exception:
    sbm_get_ham_terms = None  # type: ignore

try:
    from tencirchem.dynamic.model.pyrazine import get_ham_terms as pyrazine_get_ham_terms
except Exception:
    pyrazine_get_ham_terms = None  # type: ignore


mcp = FastMCP("tencirchem_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="health_check", description="Check service and dependency availability.")
def health_check() -> Dict[str, Any]:
    """
    Returns service health information and availability of key dependencies/modules.

    Returns:
        Dictionary with success/result/error fields.
    """
    result = {
        "numpy_available": np is not None,
        "tencirchem_available": tcc is not None,
        "molecule_builder_available": build_molecule is not None,
        "uccsd_available": UCCSD is not None,
        "kupccgsd_available": KUPCCGSD is not None,
        "puccd_available": PUCCD is not None,
        "hea_available": HEA is not None,
        "sbm_model_available": sbm_get_ham_terms is not None,
        "pyrazine_model_available": pyrazine_get_ham_terms is not None,
    }
    return _ok(result)


@mcp.tool(name="get_version", description="Get TenCirChem package version information.")
def get_version() -> Dict[str, Any]:
    """
    Retrieves TenCirChem version metadata if import is available.

    Returns:
        Dictionary with success/result/error fields.
    """
    if tcc is None:
        return _err("tencirchem is not importable in current environment")
    version = getattr(tcc, "__version__", "unknown")
    return _ok({"tencirchem_version": version})


@mcp.tool(name="build_molecule", description="Create a molecular object from atomic geometry.")
def build_molecule_tool(
    geometry: List[List[str]],
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
) -> Dict[str, Any]:
    """
    Builds a molecular object via tencirchem.molecule.molecule.

    Args:
        geometry: Atomic geometry as [[atom_symbol, x, y, z], ...] where coordinates are strings parseable as float.
        basis: Basis set string.
        charge: Molecular charge.
        spin: Spin multiplicity parameter expected by backend.

    Returns:
        Dictionary with success/result/error fields.
    """
    if build_molecule is None:
        return _err("tencirchem.molecule.molecule is unavailable")

    try:
        parsed_geometry = []
        for row in geometry:
            if len(row) != 4:
                return _err("Each geometry row must have 4 elements: symbol, x, y, z")
            atom = str(row[0])
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])
            parsed_geometry.append([atom, (x, y, z)])

        mol = build_molecule(parsed_geometry, basis=basis, charge=charge, spin=spin)
        result = {
            "basis": basis,
            "charge": charge,
            "spin": spin,
            "n_orbitals": getattr(mol, "nao", None),
            "n_electrons": getattr(mol, "nelectron", None),
        }
        return _ok(result)
    except Exception as exc:
        return _err(f"Failed to build molecule: {exc}")


@mcp.tool(name="run_uccsd", description="Run UCCSD VQE for a simple molecular system.")
def run_uccsd(
    geometry: List[List[str]],
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    maxiter: int = 50,
) -> Dict[str, Any]:
    """
    Executes a UCCSD workflow and returns energy estimate when available.

    Args:
        geometry: Atomic geometry as [[atom_symbol, x, y, z], ...].
        basis: Basis set string.
        charge: Molecular charge.
        spin: Spin parameter.
        maxiter: Optimization maximum iterations.

    Returns:
        Dictionary with success/result/error fields.
    """
    if build_molecule is None or UCCSD is None:
        return _err("Required UCCSD components are unavailable")

    try:
        parsed_geometry = []
        for row in geometry:
            atom = str(row[0])
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])
            parsed_geometry.append([atom, (x, y, z)])

        mol = build_molecule(parsed_geometry, basis=basis, charge=charge, spin=spin)
        solver = UCCSD(mol)
        if hasattr(solver, "kernel"):
            energy = solver.kernel(maxiter=maxiter)
        elif hasattr(solver, "run"):
            energy = solver.run(maxiter=maxiter)
        else:
            return _err("UCCSD solver does not expose kernel/run method")
        return _ok({"energy": float(energy) if energy is not None else None})
    except Exception as exc:
        return _err(f"UCCSD execution failed: {exc}")


@mcp.tool(name="run_kupccgsd", description="Run k-UpCCGSD VQE for a simple molecular system.")
def run_kupccgsd(
    geometry: List[List[str]],
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    k: int = 1,
    maxiter: int = 50,
) -> Dict[str, Any]:
    """
    Executes a k-UpCCGSD workflow and returns energy estimate when available.

    Args:
        geometry: Atomic geometry as [[atom_symbol, x, y, z], ...].
        basis: Basis set string.
        charge: Molecular charge.
        spin: Spin parameter.
        k: Number of repeated UpCCGSD layers.
        maxiter: Optimization maximum iterations.

    Returns:
        Dictionary with success/result/error fields.
    """
    if build_molecule is None or KUPCCGSD is None:
        return _err("Required KUPCCGSD components are unavailable")

    try:
        parsed_geometry = []
        for row in geometry:
            atom = str(row[0])
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])
            parsed_geometry.append([atom, (x, y, z)])

        mol = build_molecule(parsed_geometry, basis=basis, charge=charge, spin=spin)
        solver = KUPCCGSD(mol, k=k)
        if hasattr(solver, "kernel"):
            energy = solver.kernel(maxiter=maxiter)
        elif hasattr(solver, "run"):
            energy = solver.run(maxiter=maxiter)
        else:
            return _err("KUPCCGSD solver does not expose kernel/run method")
        return _ok({"energy": float(energy) if energy is not None else None, "k": k})
    except Exception as exc:
        return _err(f"KUPCCGSD execution failed: {exc}")


@mcp.tool(name="run_puccd", description="Run pUCCD VQE for a simple molecular system.")
def run_puccd(
    geometry: List[List[str]],
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    maxiter: int = 50,
) -> Dict[str, Any]:
    """
    Executes a pUCCD workflow and returns energy estimate when available.

    Args:
        geometry: Atomic geometry as [[atom_symbol, x, y, z], ...].
        basis: Basis set string.
        charge: Molecular charge.
        spin: Spin parameter.
        maxiter: Optimization maximum iterations.

    Returns:
        Dictionary with success/result/error fields.
    """
    if build_molecule is None or PUCCD is None:
        return _err("Required PUCCD components are unavailable")

    try:
        parsed_geometry = []
        for row in geometry:
            atom = str(row[0])
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])
            parsed_geometry.append([atom, (x, y, z)])

        mol = build_molecule(parsed_geometry, basis=basis, charge=charge, spin=spin)
        solver = PUCCD(mol)
        if hasattr(solver, "kernel"):
            energy = solver.kernel(maxiter=maxiter)
        elif hasattr(solver, "run"):
            energy = solver.run(maxiter=maxiter)
        else:
            return _err("PUCCD solver does not expose kernel/run method")
        return _ok({"energy": float(energy) if energy is not None else None})
    except Exception as exc:
        return _err(f"PUCCD execution failed: {exc}")


@mcp.tool(name="get_sbm_hamiltonian_terms", description="Get spin-boson model Hamiltonian terms.")
def get_sbm_hamiltonian_terms(
    epsilon: float,
    delta: float,
    nmode: int,
    omega: List[float],
    g: List[float],
) -> Dict[str, Any]:
    """
    Generates Hamiltonian terms for the spin-boson model.

    Args:
        epsilon: Bias parameter.
        delta: Tunneling parameter.
        nmode: Number of bosonic modes.
        omega: Mode frequencies.
        g: Coupling strengths.

    Returns:
        Dictionary with success/result/error fields.
    """
    if sbm_get_ham_terms is None:
        return _err("SBM Hamiltonian term generator is unavailable")

    try:
        terms = sbm_get_ham_terms(epsilon=epsilon, delta=delta, nmode=nmode, omega=omega, g=g)
        return _ok({"terms_repr": str(terms)})
    except Exception as exc:
        return _err(f"Failed to generate SBM Hamiltonian terms: {exc}")


@mcp.tool(name="get_pyrazine_hamiltonian_terms", description="Get pyrazine model Hamiltonian terms.")
def get_pyrazine_hamiltonian_terms(
    nmode: int = 4,
    use_potential: bool = True,
) -> Dict[str, Any]:
    """
    Generates Hamiltonian terms for the pyrazine model.

    Args:
        nmode: Number of vibrational modes.
        use_potential: Whether to include potential-related terms when supported.

    Returns:
        Dictionary with success/result/error fields.
    """
    if pyrazine_get_ham_terms is None:
        return _err("Pyrazine Hamiltonian term generator is unavailable")

    try:
        try:
            terms = pyrazine_get_ham_terms(nmode=nmode, use_potential=use_potential)
        except TypeError:
            terms = pyrazine_get_ham_terms(nmode=nmode)
        return _ok({"terms_repr": str(terms)})
    except Exception as exc:
        return _err(f"Failed to generate pyrazine Hamiltonian terms: {exc}")


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()