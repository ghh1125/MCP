# TenCirChem MCP (Model Context Protocol) Service README

## 1) Project Introduction

TenCirChem is a quantum chemistry and quantum dynamics library built on top of tensorcircuit, PySCF, and OpenFermion.  
This MCP (Model Context Protocol) service wraps core TenCirChem capabilities so agents and applications can run chemistry workflows through structured tool calls.

Main capabilities exposed by the service:

- Build molecular systems (`Molecule`)
- Run static electronic-structure solvers (UCC/HEA families)
- Construct fermionic/qubit Hamiltonians from integrals
- Run quantum dynamics time evolution and model transforms
- Switch numerical backend (NumPy/JAX-style workflow)

---

## 2) Installation Method

### Requirements

- Python 3.9+ (recommended)
- Core dependencies:
  - numpy
  - scipy
  - tensorcircuit
  - pyscf
  - openfermion
- Optional (recommended for performance/features):
  - jax
  - optax
  - pytest (testing)
  - sphinx (docs)

### Install from PyPI

pip install tencirchem

### Install from source

git clone https://github.com/tencent-quantum-lab/TenCirChem.git  
cd TenCirChem  
pip install -e .

### Install service dependencies (example)

pip install -r requirements.txt

---

## 3) Quick Start

### A. Basic import and backend selection

from tencirchem.utils.backend import set_backend, get_backend  
set_backend("numpy")  
print(get_backend())

### B. Create a molecule and run a static ansatz (example flow)

from tencirchem import Molecule  
from tencirchem.static.uccsd import UCCSD

mol = Molecule(...)  
solver = UCCSD(mol)  
energy = solver.kernel()  
print("Energy:", energy)

### C. Hamiltonian construction from integrals

from tencirchem.static.hamiltonian import get_h_from_integral, get_hop_from_integral

h_fermion = get_h_from_integral(...)  
h_qubit = get_hop_from_integral(...)

### D. Dynamics modules

from tencirchem.dynamic import time_evolution, time_derivative, transform

# Use module functions/classes according to your model and workflow.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints (mapped to TenCirChem modules):

- `backend.set`
  - Set numeric backend (`set_backend`)
- `backend.get`
  - Get current backend (`get_backend`)
- `molecule.create`
  - Build a molecular object (`Molecule`)
- `static.ucc.run`
  - Run generic UCC workflow (`UCC`)
- `static.uccsd.run`
  - Run UCCSD solver (`UCCSD`)
- `static.hea.run`
  - Run hardware-efficient ansatz solver (`HEA`)
- `static.kupccgsd.run`
  - Run k-UpCCGSD workflow (`KUPCCGSD`)
- `static.puccd.run`
  - Run pair-UCCD workflow (`PUCCD`)
- `hamiltonian.from_integral`
  - Build Hamiltonian from molecular integrals (`get_h_from_integral`)
- `hamiltonian.qubit_operator`
  - Build qubit operator from integrals (`get_hop_from_integral`)
- `dynamic.time_evolution.run`
  - Execute time propagation routines
- `dynamic.time_derivative.compute`
  - Evaluate derivative kernels for dynamics
- `dynamic.transform.apply`
  - Apply model/basis transformations
- `dynamic.model.pyrazine.load`
  - Load pyrazine benchmark model utilities
- `dynamic.model.sbm.load`
  - Load spin-boson model utilities

Note: exact endpoint names are implementation choices for your service layer; the list above is a practical mapping recommendation.

---

## 5) Common Issues and Notes

- PySCF build/runtime issues:
  - Ensure compiler toolchain and BLAS/LAPACK are available.
- Backend mismatch:
  - If using JAX, install compatible `jax`/`jaxlib` versions and set backend explicitly.
- Performance:
  - Large active spaces and deep ansatz circuits can be expensive; start with small molecules/bases.
- Numerical stability:
  - Optimizer settings strongly affect convergence (initial parameters, tolerance, max iterations).
- Environment isolation:
  - Use virtual environments/conda to avoid dependency conflicts.
- Testing:
  - Run `pytest` to validate environment and solver behavior before deployment.

---

## 6) Reference Links / Documentation

- GitHub repository: https://github.com/tencent-quantum-lab/TenCirChem
- Project README (English): https://github.com/tencent-quantum-lab/TenCirChem/blob/master/README.md
- Chinese README: https://github.com/tencent-quantum-lab/TenCirChem/blob/master/README_CN.md
- Examples: https://github.com/tencent-quantum-lab/TenCirChem/tree/master/example
- Source package: https://github.com/tencent-quantum-lab/TenCirChem/tree/master/tencirchem
- Tests: https://github.com/tencent-quantum-lab/TenCirChem/tree/master/tests