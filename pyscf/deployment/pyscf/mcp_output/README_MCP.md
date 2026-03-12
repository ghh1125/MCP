# PySCF MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core PySCF capabilities for AI/workflow-driven quantum chemistry tasks.

It is designed for:
- Building molecular and periodic systems
- Running SCF/HF/DFT calculations
- Running post-SCF methods (MP2, CCSD, CASCI/CASSCF)
- Export/import interoperability data (e.g., QCSchema)

Main backend modules include:
- `pyscf.gto`, `pyscf.scf`, `pyscf.dft`
- `pyscf.mp`, `pyscf.cc`, `pyscf.mcscf`
- `pyscf.pbc` (periodic systems)
- `pyscf.tools.qcschema`

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Required: `numpy`, `scipy`, `h5py`
- Optional (feature-dependent): `ase`, `geometric`, `pyberny`, `xcfun`, `mpi4py`, `matplotlib`

### Install
- Install PySCF:
  `pip install pyscf`
- Verify import:
  `python -c "import pyscf; print(pyscf.__version__)"`

If you are deploying this as an MCP (Model Context Protocol) service, add your MCP server runtime dependencies (for example: FastAPI/SDK/runtime used by your platform).

---

## 3) Quick Start

### Minimal flow
1. Create molecule/cell object (`gto.M` or `pbc.gto.Cell`)
2. Run SCF (`RHF/UHF` or `RKS/UKS`)
3. Optionally run post-SCF (`MP2/CCSD/CASSCF`)
4. Return energy, convergence info, and selected properties

### Example usage patterns
- Molecule + RHF: build `Mole` → `scf.RHF(mol).kernel()`
- Molecule + DFT: build `Mole` → `dft.RKS(mol).set(xc="PBE").kernel()`
- Post-HF: from converged SCF object → `mp.MP2(mf).kernel()` or `cc.CCSD(mf).kernel()`
- Periodic: build `Cell` + k-points → `pbc.scf.KRHF(cell, kpts).kernel()`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) services surface (developer-oriented):

- `build_molecule`
  - Create `Mole` from atom/basis/charge/spin options.
- `run_scf`
  - Run RHF/UHF/ROHF (or periodic variants) and return total energy + convergence metadata.
- `run_dft`
  - Run RKS/UKS with configurable XC functional, grids, and SCF controls.
- `run_mp2`
  - Execute MP2 from a converged SCF reference.
- `run_ccsd`
  - Execute CCSD (and optionally perturbative triples where enabled).
- `run_casci` / `run_casscf`
  - Active-space workflows for multireference problems.
- `build_periodic_cell`
  - Create periodic `Cell` with lattice, basis, pseudo/ECP settings.
- `run_periodic_scf`
  - Gamma-point or k-point periodic SCF calculations.
- `qcschema_import` / `qcschema_export`
  - Interoperability with external workflow tools.
- `get_density_matrix` / `analyze_orbitals`
  - Utility endpoints for post-analysis.

Note: the upstream repository is primarily import-driven and does not expose a single stable first-class CLI; MCP (Model Context Protocol) services should map Python APIs directly.

---

## 5) Common Issues and Notes

- Native/compiled components:
  - PySCF includes C/C++ accelerated libraries; use compatible Python/OS toolchains.
- Optional XC/runtime:
  - Some DFT functionals/features may require specific XC backends (`libxc`/`xcfun`) availability.
- Memory/performance:
  - CCSD/CASSCF/periodic k-point jobs can be very expensive; set memory, threading, and scratch/checkpoint strategy.
- Convergence:
  - Difficult systems may need SCF tuning (DIIS, damping, level shift, better initial guess).
- Geometry optimization:
  - External optimizers (`geometric`, `pyberny`, `ase`) are optional and must be installed separately.
- MPI/distributed:
  - Some advanced workflows can use `mpi4py`; ensure runtime MPI compatibility.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pyscf/pyscf
- Main README: https://github.com/pyscf/pyscf/blob/master/README.md
- Examples directory: https://github.com/pyscf/pyscf/tree/master/examples
- API source tree: https://github.com/pyscf/pyscf/tree/master/pyscf
- Contributing: https://github.com/pyscf/pyscf/blob/master/CONTRIBUTING.md