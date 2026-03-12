import os
import sys
from typing import Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from chempy.chemistry import Substance
from chempy.electrolytes import ionic_strength
from chempy.electrochemistry.nernst import nernst_potential
from chempy.equilibria import EqSystem
from chempy.kinetics.arrhenius import arrhenius_equation
from chempy.kinetics.integrated import pseudo_irrev
from chempy.properties.water_density_tanaka_2001 import water_density
from chempy.properties.water_viscosity_korson_1969 import water_viscosity
from chempy.reactionsystem import ReactionSystem
from chempy.util.parsing import formula_to_composition
from chempy.util.periodic import atomic_number

mcp = FastMCP("chempy_service")


@mcp.tool(name="parse_formula", description="Parse a chemical formula into elemental composition.")
def parse_formula(formula: str) -> Dict:
    """
    Parse a chemical formula string and return elemental composition.

    Parameters:
        formula: Chemical formula string (e.g., 'H2O', 'Fe2O3', 'NH4+').

    Returns:
        Dictionary with:
            success: True if parsing succeeded, else False.
            result: Composition mapping on success.
            error: Error message on failure, else None.
    """
    try:
        comp = formula_to_composition(formula)
        return {"success": True, "result": dict(comp), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="substance_from_formula", description="Create a chempy Substance from a formula.")
def substance_from_formula(formula: str, name: Optional[str] = None) -> Dict:
    """
    Build a Substance object from a formula.

    Parameters:
        formula: Chemical formula.
        name: Optional display name for the substance.

    Returns:
        Dictionary with:
            success: True if creation succeeded.
            result: Basic serialized substance info.
            error: Error message on failure.
    """
    try:
        sub = Substance.from_formula(formula)
        if name:
            sub.name = name
        result = {
            "name": sub.name,
            "latex_name": getattr(sub, "latex_name", None),
            "unicode_name": getattr(sub, "unicode_name", None),
            "composition": dict(getattr(sub, "composition", {}) or {}),
            "charge": getattr(sub, "charge", None),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="get_atomic_number", description="Get atomic number for an element symbol.")
def get_atomic_number(symbol: str) -> Dict:
    """
    Return periodic-table atomic number for an element symbol.

    Parameters:
        symbol: Element symbol (e.g., 'H', 'Na', 'Fe').

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        z = atomic_number(symbol)
        return {"success": True, "result": int(z), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="calculate_ionic_strength", description="Compute ionic strength from concentrations and charges.")
def calculate_ionic_strength(concentrations: List[float], charges: List[int]) -> Dict:
    """
    Compute ionic strength I = 0.5 * sum(c_i * z_i^2).

    Parameters:
        concentrations: Species concentrations.
        charges: Corresponding integer charges.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        if len(concentrations) != len(charges):
            raise ValueError("concentrations and charges must have equal length")
        i_strength = ionic_strength(concentrations, charges)
        return {"success": True, "result": float(i_strength), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="calculate_nernst_potential", description="Calculate electrode potential using the Nernst equation.")
def calculate_nernst_potential(
    out_conc: float,
    in_conc: float,
    charge: int,
    temperature_kelvin: float = 298.15,
) -> Dict:
    """
    Calculate Nernst potential for a species gradient.

    Parameters:
        out_conc: Outside concentration.
        in_conc: Inside concentration.
        charge: Ionic charge number z.
        temperature_kelvin: Absolute temperature in K.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        e = nernst_potential(out_conc, in_conc, charge, T=temperature_kelvin)
        return {"success": True, "result": float(e), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="arrhenius_rate_constant", description="Compute Arrhenius rate constant k(T).")
def arrhenius_rate_constant(
    temperature_kelvin: float,
    pre_exponential_factor: float,
    activation_energy_j_per_mol: float,
) -> Dict:
    """
    Compute rate constant from Arrhenius equation.

    Parameters:
        temperature_kelvin: Temperature in Kelvin.
        pre_exponential_factor: Arrhenius pre-exponential factor A.
        activation_energy_j_per_mol: Activation energy Ea in J/mol.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        k = arrhenius_equation(
            pre_exponential_factor,
            activation_energy_j_per_mol,
            temperature_kelvin,
        )
        return {"success": True, "result": float(k), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="pseudo_first_order_concentration", description="Evaluate pseudo-first-order irreversible concentration profile.")
def pseudo_first_order_concentration(
    t: float,
    k: float,
    c0: float,
) -> Dict:
    """
    Evaluate concentration for pseudo-first-order irreversible kinetics.

    Parameters:
        t: Time.
        k: Effective first-order rate constant.
        c0: Initial concentration.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        c = pseudo_irrev(t, k, c0)
        return {"success": True, "result": float(c), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="water_density_tanaka_2001", description="Compute pure-water density from Tanaka 2001 model.")
def water_density_tanaka_2001(temperature_celsius: float) -> Dict:
    """
    Compute water density as function of temperature (Tanaka 2001 correlation).

    Parameters:
        temperature_celsius: Temperature in degrees Celsius.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        rho = water_density(temperature_celsius)
        return {"success": True, "result": float(rho), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="water_viscosity_korson_1969", description="Compute water viscosity from Korson 1969 model.")
def water_viscosity_korson_1969(temperature_celsius: float) -> Dict:
    """
    Compute dynamic viscosity of water from temperature.

    Parameters:
        temperature_celsius: Temperature in degrees Celsius.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        mu = water_viscosity(temperature_celsius)
        return {"success": True, "result": float(mu), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="reaction_system_summary", description="Create a basic ReactionSystem summary from reaction strings.")
def reaction_system_summary(
    reaction_strings: List[str],
    substance_keys: List[str],
    checks: bool = False,
) -> Dict:
    """
    Build a ReactionSystem from reaction strings and return summary metadata.

    Parameters:
        reaction_strings: Reactions in chempy string format.
        substance_keys: Substance keys present in system.
        checks: Whether to run internal consistency checks.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        rsys = ReactionSystem.from_string(
            "\n".join(reaction_strings),
            substance_keys=substance_keys,
            checks=checks,
        )
        result = {
            "nr": int(rsys.nr),
            "ns": int(rsys.ns),
            "substances": list(rsys.substances.keys()),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="equilibrium_system_summary", description="Create equilibrium system summary from reaction strings.")
def equilibrium_system_summary(
    equilibrium_strings: List[str],
    substance_keys: List[str],
) -> Dict:
    """
    Build an EqSystem from equilibrium strings and return summary metadata.

    Parameters:
        equilibrium_strings: Equilibrium definitions in chempy format.
        substance_keys: Substance keys for the system.

    Returns:
        Dictionary with standard success/result/error fields.
    """
    try:
        eqsys = EqSystem.from_string(
            "\n".join(equilibrium_strings),
            substance_keys=substance_keys,
        )
        result = {
            "nr": int(eqsys.nr),
            "ns": int(eqsys.ns),
            "substances": list(eqsys.substances.keys()),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()