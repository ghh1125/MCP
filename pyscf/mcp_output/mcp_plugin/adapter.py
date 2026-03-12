import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the PySCF repository.

    This adapter is intentionally import-driven and provides:
    - Robust import checks
    - Structured status dictionaries for all operations
    - Graceful fallback guidance when imports fail
    - Thin wrappers around representative high-value PySCF entry modules/functions
    """

    mode = "import"

    def __init__(self) -> None:
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_core_modules()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = {"status": "success", "mode": self.mode}
        if data:
            resp.update(data)
        return resp

    def _fail(self, message: str, hint: Optional[str] = None) -> Dict[str, Any]:
        resp = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            resp["hint"] = hint
        return resp

    def _import_module(self, key: str, import_path: str) -> None:
        try:
            module = __import__(import_path, fromlist=["*"])
            self._modules[key] = module
        except Exception as exc:
            self._import_errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_core_modules(self) -> None:
        targets = {
            "pyscf": "pyscf",
            "gto": "pyscf.gto",
            "scf": "pyscf.scf",
            "dft": "pyscf.dft",
            "mp": "pyscf.mp",
            "cc": "pyscf.cc",
            "fci": "pyscf.fci",
            "mcscf": "pyscf.mcscf",
            "tdscf": "pyscf.tdscf",
            "geomopt": "pyscf.geomopt",
            "solvent": "pyscf.solvent",
            "pbc": "pyscf.pbc",
            "tools": "pyscf.tools",
        }
        for key, path in targets.items():
            self._import_module(key, path)

    def _get(self, key: str) -> Any:
        mod = self._modules.get(key)
        if mod is None:
            raise ImportError(
                f"Module '{key}' is unavailable. "
                f"Check compiled PySCF libs and optional runtime dependencies."
            )
        return mod

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "ready": "pyscf" in self._modules,
            }
        )

    # -------------------------------------------------------------------------
    # Core object factories (class instance methods)
    # -------------------------------------------------------------------------
    def create_mole(
        self,
        atom: str,
        basis: str = "sto-3g",
        charge: int = 0,
        spin: int = 0,
        unit: str = "Angstrom",
        verbose: int = 0,
    ) -> Dict[str, Any]:
        """
        Create and build a molecular object (pyscf.gto.Mole).

        Parameters:
        - atom: Atomic specification string.
        - basis: Basis set name.
        - charge: Total molecular charge.
        - spin: 2S value (n_alpha - n_beta).
        - unit: Geometry unit.
        - verbose: PySCF verbosity level.
        """
        try:
            gto = self._get("gto")
            mol = gto.Mole()
            mol.atom = atom
            mol.basis = basis
            mol.charge = charge
            mol.spin = spin
            mol.unit = unit
            mol.verbose = verbose
            mol.build()
            return self._ok({"object": mol, "nelectron": mol.nelectron, "nao": mol.nao_nr()})
        except Exception as exc:
            return self._fail(
                f"Failed to create molecule: {type(exc).__name__}: {exc}",
                "Verify atom format, basis name, and compiled PySCF backend availability.",
            )

    def create_cell(self, **cell_kwargs: Any) -> Dict[str, Any]:
        """
        Create and build a periodic cell object (pyscf.pbc.gto.Cell).

        Parameters:
        - cell_kwargs: Keyword args for Cell().build(...), e.g., atom, a, basis, pseudo.
        """
        try:
            pbc = self._get("pbc")
            cell = pbc.gto.Cell()
            cell.build(**cell_kwargs)
            return self._ok({"object": cell, "nao": cell.nao_nr()})
        except Exception as exc:
            return self._fail(
                f"Failed to create periodic cell: {type(exc).__name__}: {exc}",
                "Provide valid lattice vectors, atomic coordinates, and periodic basis/pseudo settings.",
            )

    # -------------------------------------------------------------------------
    # SCF / DFT wrappers (function-call methods)
    # -------------------------------------------------------------------------
    def run_rhf(self, mol: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            scf = self._get("scf")
            mf = scf.RHF(mol)
            for k, v in kwargs.items():
                setattr(mf, k, v)
            e = mf.kernel()
            return self._ok({"energy": e, "converged": bool(mf.converged), "object": mf})
        except Exception as exc:
            return self._fail(
                f"RHF run failed: {type(exc).__name__}: {exc}",
                "Check molecule validity and SCF options like max_cycle, conv_tol, and initial guess.",
            )

    def run_uhf(self, mol: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            scf = self._get("scf")
            mf = scf.UHF(mol)
            for k, v in kwargs.items():
                setattr(mf, k, v)
            e = mf.kernel()
            return self._ok({"energy": e, "converged": bool(mf.converged), "object": mf})
        except Exception as exc:
            return self._fail(f"UHF run failed: {type(exc).__name__}: {exc}")

    def run_rks(self, mol: Any, xc: str = "PBE", **kwargs: Any) -> Dict[str, Any]:
        try:
            dft = self._get("dft")
            mf = dft.RKS(mol)
            mf.xc = xc
            for k, v in kwargs.items():
                setattr(mf, k, v)
            e = mf.kernel()
            return self._ok({"energy": e, "xc": xc, "converged": bool(mf.converged), "object": mf})
        except Exception as exc:
            return self._fail(
                f"RKS run failed: {type(exc).__name__}: {exc}",
                "Ensure libxc/xcfun runtime is available for selected XC functional.",
            )

    # -------------------------------------------------------------------------
    # Post-HF wrappers
    # -------------------------------------------------------------------------
    def run_mp2(self, mf: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            mp = self._get("mp")
            solver = mp.MP2(mf)
            for k, v in kwargs.items():
                setattr(solver, k, v)
            e_corr, _ = solver.kernel()
            return self._ok({"e_corr": e_corr, "e_tot": solver.e_tot, "object": solver})
        except Exception as exc:
            return self._fail(f"MP2 run failed: {type(exc).__name__}: {exc}")

    def run_ccsd(self, mf: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            cc = self._get("cc")
            solver = cc.CCSD(mf)
            for k, v in kwargs.items():
                setattr(solver, k, v)
            e_corr, _, _ = solver.kernel()
            return self._ok({"e_corr": e_corr, "e_tot": solver.e_tot, "object": solver})
        except Exception as exc:
            return self._fail(f"CCSD run failed: {type(exc).__name__}: {exc}")

    def run_fci(self, mf: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            fci = self._get("fci")
            cisolver = fci.FCI(mf)
            e, vec = cisolver.kernel(**kwargs)
            return self._ok({"energy": e, "vector": vec, "object": cisolver})
        except Exception as exc:
            return self._fail(f"FCI run failed: {type(exc).__name__}: {exc}")

    def run_casscf(self, mf: Any, ncas: int, nelecas: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            mcscf = self._get("mcscf")
            mc = mcscf.CASSCF(mf, ncas, nelecas)
            for k, v in kwargs.items():
                setattr(mc, k, v)
            e = mc.kernel()[0]
            return self._ok({"energy": e, "object": mc})
        except Exception as exc:
            return self._fail(f"CASSCF run failed: {type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # TD / response wrappers
    # -------------------------------------------------------------------------
    def run_tddft(self, mf: Any, nstates: int = 5, **kwargs: Any) -> Dict[str, Any]:
        try:
            td = mf.TDDFT()
            td.nstates = nstates
            for k, v in kwargs.items():
                setattr(td, k, v)
            e = td.kernel()[0]
            return self._ok({"excitation_energies": e, "object": td})
        except Exception as exc:
            return self._fail(f"TDDFT run failed: {type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # Geometry optimization and solvent wrappers
    # -------------------------------------------------------------------------
    def optimize_geometry(self, method_obj: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            geomopt = self._get("geomopt")
            mol_eq = geomopt.optimize(method_obj, **kwargs)
            return self._ok({"optimized_mol": mol_eq})
        except Exception as exc:
            return self._fail(
                f"Geometry optimization failed: {type(exc).__name__}: {exc}",
                "Install geometric or pyberny and confirm gradient support for the method.",
            )

    def apply_ddcosmo(self, method_obj: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            solvent = self._get("solvent")
            obj = solvent.ddCOSMO(method_obj)
            for k, v in kwargs.items():
                setattr(obj, k, v)
            return self._ok({"object": obj})
        except Exception as exc:
            return self._fail(f"ddCOSMO setup failed: {type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # Tools wrappers
    # -------------------------------------------------------------------------
    def export_fcidump(self, mf: Any, filename: str = "FCIDUMP", **kwargs: Any) -> Dict[str, Any]:
        try:
            tools = self._get("tools")
            tools.fcidump.from_scf(mf, filename, **kwargs)
            return self._ok({"filename": filename})
        except Exception as exc:
            return self._fail(f"FCIDUMP export failed: {type(exc).__name__}: {exc}")

    def export_molden(self, mol: Any, filename: str, mo_coeff: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            tools = self._get("tools")
            tools.molden.from_mo(mol, filename, mo_coeff, **kwargs)
            return self._ok({"filename": filename})
        except Exception as exc:
            return self._fail(f"Molden export failed: {type(exc).__name__}: {exc}")