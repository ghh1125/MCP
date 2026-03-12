import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("pyscf_core_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="pyscf_scf_energy", description="Run SCF energy calculation (RHF/UHF/RKS/UKS).")
def pyscf_scf_energy(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    method: str = "RHF",
    xc: str = "PBE",
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Run a single-point SCF/DFT calculation in PySCF.

    Parameters:
    - atom: Molecular geometry string in PySCF format.
    - basis: Basis set name.
    - charge: Molecular charge.
    - spin: 2S value (number of unpaired electrons).
    - method: One of RHF, UHF, RKS, UKS.
    - xc: Exchange-correlation functional for DFT methods.
    - verbose: PySCF verbosity level.

    Returns:
    - Dictionary with total energy and basic orbital metadata.
    """
    try:
        from pyscf import gto, scf, dft

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        m = method.upper()

        if m == "RHF":
            mf = scf.RHF(mol)
        elif m == "UHF":
            mf = scf.UHF(mol)
        elif m == "RKS":
            mf = dft.RKS(mol)
            mf.xc = xc
        elif m == "UKS":
            mf = dft.UKS(mol)
            mf.xc = xc
        else:
            return _err("Unsupported method. Use RHF, UHF, RKS, or UKS.")

        e_tot = mf.kernel()
        result = {
            "e_tot": float(e_tot),
            "converged": bool(mf.converged),
            "nelectron": int(mol.nelectron),
            "nao": int(mol.nao_nr()),
        }
        return _ok(result)
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_geometry_optimize", description="Run geometry optimization using geomeTRIC if available.")
def pyscf_geometry_optimize(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    maxsteps: int = 50,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Perform RHF geometry optimization.

    Parameters:
    - atom: Initial molecular geometry string.
    - basis: Basis set name.
    - charge: Molecular charge.
    - spin: 2S value.
    - maxsteps: Maximum optimization steps.
    - verbose: PySCF verbosity level.

    Returns:
    - Dictionary containing optimized geometry and final energy.
    """
    try:
        from pyscf import gto, scf, geomopt

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol)
        mf.kernel()

        mol_eq = geomopt.geometric_solver.optimize(mf, maxsteps=maxsteps)
        mf_eq = scf.RHF(mol_eq)
        e_final = mf_eq.kernel()

        coords = []
        for i in range(mol_eq.natm):
            sym = mol_eq.atom_symbol(i)
            x, y, z = mol_eq.atom_coord(i)
            coords.append([sym, float(x), float(y), float(z)])

        return _ok({"e_tot": float(e_final), "optimized_atoms": coords})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_mp2_energy", description="Compute MP2 correlation and total energy from RHF reference.")
def pyscf_mp2_energy(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Run RHF followed by MP2.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin (must be compatible with RHF).
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with HF, MP2 correlation, and MP2 total energies.
    """
    try:
        from pyscf import gto, scf, mp

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol).run()
        pt = mp.MP2(mf).run()

        return _ok(
            {
                "e_hf": float(mf.e_tot),
                "e_corr_mp2": float(pt.e_corr),
                "e_tot_mp2": float(pt.e_tot),
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_ccsd_energy", description="Compute CCSD energy from RHF reference.")
def pyscf_ccsd_energy(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Run RHF followed by CCSD.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin (compatible with RHF).
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with HF, CCSD correlation, and CCSD total energies.
    """
    try:
        from pyscf import gto, scf, cc

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol).run()
        mycc = cc.CCSD(mf).run()

        return _ok(
            {
                "e_hf": float(mf.e_tot),
                "e_corr_ccsd": float(mycc.e_corr),
                "e_tot_ccsd": float(mycc.e_tot),
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_fci_energy", description="Run full CI in current basis from RHF reference.")
def pyscf_fci_energy(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    nroots: int = 1,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Compute FCI energies in molecular orbital basis.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin.
    - nroots: Number of requested roots.
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with FCI root energies.
    """
    try:
        from pyscf import gto, scf, fci

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol).run()
        cisolver = fci.FCI(mol, mf.mo_coeff)
        energies, _ = cisolver.kernel(nroots=nroots)

        if isinstance(energies, (float, int)):
            e_list = [float(energies)]
        else:
            e_list = [float(x) for x in energies]

        return _ok({"fci_energies": e_list})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_tddft_excitations", description="Compute lowest TDDFT excitation energies.")
def pyscf_tddft_excitations(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    xc: str = "PBE",
    nstates: int = 5,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Run RKS then TDDFT for vertical excitations.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin.
    - xc: XC functional.
    - nstates: Number of excited states.
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with excitation energies in Hartree and eV.
    """
    try:
        from pyscf import gto, dft, tdscf

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = dft.RKS(mol)
        mf.xc = xc
        mf.kernel()

        td = tdscf.TDDFT(mf)
        td.nstates = nstates
        e = td.kernel()[0]

        eh = [float(x) for x in e]
        ev = [float(x * 27.211386245988) for x in e]
        return _ok({"excitation_energies_hartree": eh, "excitation_energies_ev": ev})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_nmr_shielding", description="Compute RHF NMR shielding tensors.")
def pyscf_nmr_shielding(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Compute NMR shielding tensors with RHF.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin.
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with shielding tensors as nested lists.
    """
    try:
        from pyscf import gto, scf
        from pyscf.prop.nmr import rhf as nmr_rhf

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol).run()
        nmr_calc = nmr_rhf.NMR(mf)
        shielding = nmr_calc.kernel()

        tensors: List[List[List[float]]] = []
        for t in shielding:
            tensors.append([[float(v) for v in row] for row in t])

        return _ok({"shielding_tensors": tensors})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_cubegen_density", description="Generate electron density cube file from SCF result.")
def pyscf_cubegen_density(
    atom: str,
    basis: str = "sto-3g",
    output_cube: str = "density.cube",
    charge: int = 0,
    spin: int = 0,
    nx: int = 80,
    ny: int = 80,
    nz: int = 80,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Generate a cube file for electron density.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - output_cube: Output cube file path.
    - charge: Molecular charge.
    - spin: Spin.
    - nx, ny, nz: Grid dimensions.
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with output file path and SCF energy.
    """
    try:
        from pyscf import gto, scf, tools

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        mf = scf.RHF(mol).run()
        tools.cubegen.density(mol, output_cube, mf.make_rdm1(), nx=nx, ny=ny, nz=nz)

        return _ok({"output_cube": output_cube, "e_tot": float(mf.e_tot)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="pyscf_basis_info", description="Inspect basis and molecular size information.")
def pyscf_basis_info(
    atom: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    verbose: int = 0,
) -> Dict[str, Any]:
    """
    Return basic molecule/basis metadata.

    Parameters:
    - atom: Molecular geometry.
    - basis: Basis set.
    - charge: Molecular charge.
    - spin: Spin.
    - verbose: PySCF verbosity.

    Returns:
    - Dictionary with atom/electron/orbital counts.
    """
    try:
        from pyscf import gto

        mol = gto.M(atom=atom, basis=basis, charge=charge, spin=spin, verbose=verbose)
        return _ok(
            {
                "natm": int(mol.natm),
                "nelectron": int(mol.nelectron),
                "nao": int(mol.nao_nr()),
                "basis": basis,
                "charge": charge,
                "spin": spin,
            }
        )
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()