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
import pypsa

mcp = FastMCP("pypsa_service")


@mcp.tool(
    name="create_network",
    description="Create an empty PyPSA network instance.",
)
def create_network(name: str = "") -> dict[str, Any]:
    """
    Create a new PyPSA Network object.

    Parameters:
        name: Optional name to assign to the network.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network()
        if name:
            network.name = name
        result = {
            "network_name": getattr(network, "name", ""),
            "snapshots_count": int(len(network.snapshots)),
            "buses_count": int(len(network.buses)),
            "lines_count": int(len(network.lines)),
            "generators_count": int(len(network.generators)),
            "loads_count": int(len(network.loads)),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="load_network_from_file",
    description="Load a PyPSA network from a supported file format.",
)
def load_network_from_file(path: str) -> dict[str, Any]:
    """
    Load a network from disk.

    Parameters:
        path: File path to a PyPSA-supported network file (e.g., netcdf/hdf5/csv folder).

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        result = {
            "network_name": getattr(network, "name", ""),
            "snapshots_count": int(len(network.snapshots)),
            "components": list(network.components.keys()),
            "buses_count": int(len(network.buses)),
            "lines_count": int(len(network.lines)),
            "links_count": int(len(network.links)),
            "generators_count": int(len(network.generators)),
            "loads_count": int(len(network.loads)),
            "stores_count": int(len(network.stores)),
            "storage_units_count": int(len(network.storage_units)),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="add_bus",
    description="Add a bus to a PyPSA network file and save it.",
)
def add_bus(path: str, bus_name: str, carrier: str = "") -> dict[str, Any]:
    """
    Add a bus to an existing network and persist changes.

    Parameters:
        path: Path to existing network file.
        bus_name: Name of the bus to add.
        carrier: Optional carrier for the bus.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        kwargs: dict[str, Any] = {}
        if carrier:
            kwargs["carrier"] = carrier
        network.add("Bus", bus_name, **kwargs)
        network.export_to_netcdf(path)
        return {
            "success": True,
            "result": {"bus_name": bus_name, "buses_count": int(len(network.buses))},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="add_generator",
    description="Add a generator to a bus in a PyPSA network file and save it.",
)
def add_generator(
    path: str,
    generator_name: str,
    bus: str,
    p_nom: float,
    marginal_cost: float = 0.0,
    carrier: str = "",
) -> dict[str, Any]:
    """
    Add a generator to an existing network and persist changes.

    Parameters:
        path: Path to existing network file.
        generator_name: Generator name.
        bus: Existing bus name.
        p_nom: Nominal capacity.
        marginal_cost: Marginal generation cost.
        carrier: Optional carrier.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        kwargs: dict[str, Any] = {
            "bus": bus,
            "p_nom": p_nom,
            "marginal_cost": marginal_cost,
        }
        if carrier:
            kwargs["carrier"] = carrier
        network.add("Generator", generator_name, **kwargs)
        network.export_to_netcdf(path)
        return {
            "success": True,
            "result": {
                "generator_name": generator_name,
                "generators_count": int(len(network.generators)),
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="run_linear_optimal_power_flow",
    description="Run network optimization on a PyPSA network file and return objective.",
)
def run_linear_optimal_power_flow(path: str, solver_name: str = "highs") -> dict[str, Any]:
    """
    Execute optimization for the network.

    Parameters:
        path: Path to network file.
        solver_name: Linopy-compatible solver name (e.g., highs, gurobi, cplex, glpk).

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        status, condition = network.optimize(solver_name=solver_name)
        objective = getattr(network.model, "objective", None)
        objective_value = float(objective.value) if objective is not None and hasattr(objective, "value") else None
        return {
            "success": True,
            "result": {
                "status": str(status),
                "condition": str(condition),
                "objective": objective_value,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="run_linear_power_flow",
    description="Run linear power flow for a PyPSA network file.",
)
def run_linear_power_flow(path: str) -> dict[str, Any]:
    """
    Execute linear power flow.

    Parameters:
        path: Path to network file.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        network.lpf()
        return {
            "success": True,
            "result": {
                "snapshots_count": int(len(network.snapshots)),
                "line_flows_rows": int(len(network.lines_t.p0)) if hasattr(network, "lines_t") else 0,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="run_nonlinear_power_flow",
    description="Run nonlinear power flow for a PyPSA network file.",
)
def run_nonlinear_power_flow(path: str) -> dict[str, Any]:
    """
    Execute nonlinear power flow.

    Parameters:
        path: Path to network file.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        network.pf()
        return {
            "success": True,
            "result": {
                "snapshots_count": int(len(network.snapshots)),
                "buses_voltage_rows": int(len(network.buses_t.v_mag_pu)) if hasattr(network, "buses_t") else 0,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="network_statistics",
    description="Compute basic summary statistics from a PyPSA network file.",
)
def network_statistics(path: str) -> dict[str, Any]:
    """
    Return core counts and capacity summaries.

    Parameters:
        path: Path to network file.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        network = pypsa.Network(path)
        total_gen_nom = float(network.generators.p_nom.sum()) if len(network.generators) else 0.0
        total_load_p = float(network.loads.p_set.sum()) if "p_set" in network.loads.columns and len(network.loads) else 0.0
        result = {
            "buses_count": int(len(network.buses)),
            "lines_count": int(len(network.lines)),
            "links_count": int(len(network.links)),
            "generators_count": int(len(network.generators)),
            "loads_count": int(len(network.loads)),
            "stores_count": int(len(network.stores)),
            "storage_units_count": int(len(network.storage_units)),
            "total_generator_p_nom": total_gen_nom,
            "total_load_p_set": total_load_p,
            "snapshots_count": int(len(network.snapshots)),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()