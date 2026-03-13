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
from qutip import basis, destroy, qeye, sigmax, sigmay, sigmaz, tensor
from qutip.core.expect import expect
from qutip.core.metrics import fidelity, tracedist
from qutip.core.operators import num
from qutip.core.states import coherent, fock_dm
from qutip.entropy import entropy_vn
from qutip.measurement import measure_observable
from qutip.random_objects import rand_dm, rand_ket
from qutip.solver.mesolve import mesolve
from qutip.solver.sesolve import sesolve
from qutip.solver.steadystate import steadystate

mcp = FastMCP("qutip_service")


@mcp.tool(name="create_basis_state", description="Create a basis ket state |n> in dimension N.")
def create_basis_state(dim: int, index: int) -> dict:
    """
    Create a basis ket.

    Parameters:
        dim: Hilbert-space dimension.
        index: Basis index to populate with 1.

    Returns:
        dict with success/result/error where result is a string representation of the state.
    """
    try:
        state = basis(dim, index)
        return {"success": True, "result": str(state), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_destroy_operator", description="Create annihilation operator a for dimension N.")
def create_destroy_operator(dim: int) -> dict:
    """
    Create a destruction operator.

    Parameters:
        dim: Hilbert-space dimension.

    Returns:
        dict with success/result/error where result is a string representation of the operator.
    """
    try:
        op = destroy(dim)
        return {"success": True, "result": str(op), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_number_operator", description="Create number operator for dimension N.")
def create_number_operator(dim: int) -> dict:
    """
    Create number operator n.

    Parameters:
        dim: Hilbert-space dimension.

    Returns:
        dict with success/result/error where result is a string representation of the operator.
    """
    try:
        op = num(dim)
        return {"success": True, "result": str(op), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_coherent_state", description="Create coherent state |alpha> in dimension N.")
def create_coherent_state(dim: int, alpha_real: float, alpha_imag: float = 0.0) -> dict:
    """
    Create a coherent state.

    Parameters:
        dim: Hilbert-space dimension.
        alpha_real: Real part of alpha.
        alpha_imag: Imaginary part of alpha.

    Returns:
        dict with success/result/error where result is a string representation of the state.
    """
    try:
        alpha = complex(alpha_real, alpha_imag)
        state = coherent(dim, alpha)
        return {"success": True, "result": str(state), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_fock_density_matrix", description="Create Fock basis density matrix |n><n|.")
def create_fock_density_matrix(dim: int, index: int) -> dict:
    """
    Create a Fock density matrix.

    Parameters:
        dim: Hilbert-space dimension.
        index: Fock state index.

    Returns:
        dict with success/result/error where result is a string representation of the density matrix.
    """
    try:
        rho = fock_dm(dim, index)
        return {"success": True, "result": str(rho), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="expect_pauli", description="Compute expectation value of a Pauli operator on a qubit state.")
def expect_pauli(state_label: str, pauli: str) -> dict:
    """
    Compute expectation value for a standard qubit basis state and Pauli observable.

    Parameters:
        state_label: One of '0' or '1'.
        pauli: One of 'x', 'y', or 'z'.

    Returns:
        dict with success/result/error where result is a float (or complex as string if needed).
    """
    try:
        if state_label not in ("0", "1"):
            raise ValueError("state_label must be '0' or '1'.")
        ket = basis(2, int(state_label))

        p = pauli.lower()
        if p == "x":
            op = sigmax()
        elif p == "y":
            op = sigmay()
        elif p == "z":
            op = sigmaz()
        else:
            raise ValueError("pauli must be one of 'x', 'y', 'z'.")

        val = expect(op, ket)
        result = float(val.real) if abs(val.imag) < 1e-12 else str(val)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="compute_fidelity_fock", description="Compute fidelity between two Fock states.")
def compute_fidelity_fock(dim: int, n1: int, n2: int) -> dict:
    """
    Compute fidelity between |n1> and |n2>.

    Parameters:
        dim: Hilbert-space dimension.
        n1: First Fock index.
        n2: Second Fock index.

    Returns:
        dict with success/result/error where result is fidelity as float.
    """
    try:
        s1 = basis(dim, n1)
        s2 = basis(dim, n2)
        val = fidelity(s1, s2)
        return {"success": True, "result": float(val), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="compute_trace_distance_random", description="Compute trace distance between two random density matrices.")
def compute_trace_distance_random(dim: int, seed1: Optional[int] = None, seed2: Optional[int] = None) -> dict:
    """
    Compute trace distance between two random density operators.

    Parameters:
        dim: Hilbert-space dimension.
        seed1: Optional random seed for first state.
        seed2: Optional random seed for second state.

    Returns:
        dict with success/result/error where result is trace distance as float.
    """
    try:
        rho1 = rand_dm(dim, seed=seed1)
        rho2 = rand_dm(dim, seed=seed2)
        val = tracedist(rho1, rho2)
        return {"success": True, "result": float(val), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="entropy_von_neumann_fock", description="Compute von Neumann entropy of a Fock density matrix.")
def entropy_von_neumann_fock(dim: int, index: int, base: float = 2.0) -> dict:
    """
    Compute von Neumann entropy for |n><n|.

    Parameters:
        dim: Hilbert-space dimension.
        index: Fock state index.
        base: Log base for entropy.

    Returns:
        dict with success/result/error where result is entropy as float.
    """
    try:
        rho = fock_dm(dim, index)
        ent = entropy_vn(rho, base=base)
        return {"success": True, "result": float(ent), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="measure_pauli_z", description="Projectively measure sigma_z on a qubit state.")
def measure_pauli_z(state_label: str) -> dict:
    """
    Perform a projective measurement of sigma_z on |0> or |1>.

    Parameters:
        state_label: One of '0' or '1'.

    Returns:
        dict with success/result/error where result includes measured eigenvalue and post-state string.
    """
    try:
        if state_label not in ("0", "1"):
            raise ValueError("state_label must be '0' or '1'.")
        ket = basis(2, int(state_label))
        value, post_state = measure_observable(ket, sigmaz())
        result = {"eigenvalue": float(value), "post_state": str(post_state)}
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="solve_schrodinger_qubit", description="Run sesolve for a qubit under sigma_x Hamiltonian.")
def solve_schrodinger_qubit(tlist: List[float]) -> dict:
    """
    Solve a simple closed-system qubit evolution using sesolve.

    Parameters:
        tlist: Time points.

    Returns:
        dict with success/result/error where result contains final state and expectation trajectory of sigma_z.
    """
    try:
        if len(tlist) < 2:
            raise ValueError("tlist must contain at least two time points.")
        h = 0.5 * sigmax()
        psi0 = basis(2, 0)
        res = sesolve(h, psi0, tlist, e_ops=[sigmaz()])
        result = {
            "final_state": str(res.states[-1]),
            "expect_z": [float(v) for v in res.expect[0]],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="solve_master_equation_qubit", description="Run mesolve for a dissipative qubit with relaxation.")
def solve_master_equation_qubit(tlist: List[float], gamma: float) -> dict:
    """
    Solve Lindblad master equation for a decaying qubit.

    Parameters:
        tlist: Time points.
        gamma: Relaxation rate.

    Returns:
        dict with success/result/error where result contains final density matrix and expectation trajectory of sigma_z.
    """
    try:
        if len(tlist) < 2:
            raise ValueError("tlist must contain at least two time points.")
        if gamma < 0:
            raise ValueError("gamma must be non-negative.")
        h = 0.5 * sigmax()
        rho0 = fock_dm(2, 1)
        c_ops = [(gamma ** 0.5) * destroy(2)]
        res = mesolve(h, rho0, tlist, c_ops=c_ops, e_ops=[sigmaz()])
        result = {
            "final_state": str(res.states[-1]),
            "expect_z": [float(v) for v in res.expect[0]],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="compute_steady_state_qubit", description="Compute steady state of a dissipative qubit.")
def compute_steady_state_qubit(gamma: float) -> dict:
    """
    Compute steady-state density matrix for a qubit with relaxation.

    Parameters:
        gamma: Relaxation rate.

    Returns:
        dict with success/result/error where result contains steady state and sigma_z expectation.
    """
    try:
        if gamma < 0:
            raise ValueError("gamma must be non-negative.")
        h = 0.5 * sigmax()
        c_ops = [(gamma ** 0.5) * destroy(2)] if gamma > 0 else []
        rho_ss = steadystate(h, c_ops)
        z = expect(sigmaz(), rho_ss)
        result = {"steady_state": str(rho_ss), "expect_z": float(z.real)}
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp