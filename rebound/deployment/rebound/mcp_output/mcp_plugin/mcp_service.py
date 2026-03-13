import os
import sys
from typing import Optional, List, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

import rebound


mcp = FastMCP("rebound_service")


@mcp.tool(name="rebound_create_simulation", description="Create a new REBOUND simulation and configure basic parameters.")
def rebound_create_simulation(
    integrator: str = "ias15",
    gravity: str = "basic",
    dt: float = 0.01,
    units_length: Optional[str] = None,
    units_time: Optional[str] = None,
    units_mass: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create and initialize a REBOUND Simulation object.

    Parameters:
        integrator: Integrator name (e.g., ias15, whfast, leapfrog, bs, mercurius).
        gravity: Gravity solver mode.
        dt: Base timestep.
        units_length: Optional length unit.
        units_time: Optional time unit.
        units_mass: Optional mass unit.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        sim = rebound.Simulation()
        sim.integrator = integrator
        sim.gravity = gravity
        sim.dt = dt
        if units_length and units_time and units_mass:
            sim.units = (units_length, units_time, units_mass)
        result = {
            "integrator": sim.integrator,
            "gravity": sim.gravity,
            "dt": sim.dt,
            "N": sim.N,
            "t": sim.t,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="rebound_two_body_orbit", description="Run a two-body simulation and return final state and orbital elements.")
def rebound_two_body_orbit(
    primary_mass: float,
    secondary_mass: float,
    a: float,
    e: float,
    inc: float = 0.0,
    Omega: float = 0.0,
    omega: float = 0.0,
    f: float = 0.0,
    t_end: float = 1.0,
    integrator: str = "ias15",
) -> Dict[str, Any]:
    """
    Simulate a two-body orbit from orbital elements.

    Parameters:
        primary_mass: Mass of central body.
        secondary_mass: Mass of orbiting body.
        a: Semi-major axis.
        e: Eccentricity.
        inc: Inclination (radians).
        Omega: Longitude of ascending node (radians).
        omega: Argument of periapsis (radians).
        f: True anomaly (radians).
        t_end: End time for integration.
        integrator: Integrator name.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        sim = rebound.Simulation()
        sim.integrator = integrator
        sim.add(m=primary_mass)
        sim.add(m=secondary_mass, a=a, e=e, inc=inc, Omega=Omega, omega=omega, f=f)
        sim.move_to_com()
        sim.integrate(t_end)
        p1 = sim.particles[1]
        orb = p1.orbit(primary=sim.particles[0])
        result = {
            "t": sim.t,
            "N": sim.N,
            "particle": {
                "x": p1.x,
                "y": p1.y,
                "z": p1.z,
                "vx": p1.vx,
                "vy": p1.vy,
                "vz": p1.vz,
            },
            "orbit": {
                "a": orb.a,
                "e": orb.e,
                "inc": orb.inc,
                "Omega": orb.Omega,
                "omega": orb.omega,
                "f": orb.f,
                "P": orb.P,
            },
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="rebound_nbody_integrate", description="Integrate an N-body system from Cartesian state vectors.")
def rebound_nbody_integrate(
    particles: List[Dict[str, float]],
    t_end: float,
    dt: float = 0.01,
    integrator: str = "ias15",
    move_to_com: bool = True,
) -> Dict[str, Any]:
    """
    Integrate an N-body system.

    Parameters:
        particles: List of particle dicts with keys m,x,y,z,vx,vy,vz.
        t_end: End time.
        dt: Timestep.
        integrator: Integrator name.
        move_to_com: Whether to shift system to center-of-mass frame.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        sim = rebound.Simulation()
        sim.integrator = integrator
        sim.dt = dt

        for p in particles:
            sim.add(
                m=float(p["m"]),
                x=float(p["x"]),
                y=float(p["y"]),
                z=float(p["z"]),
                vx=float(p["vx"]),
                vy=float(p["vy"]),
                vz=float(p["vz"]),
            )

        if move_to_com:
            sim.move_to_com()

        e0 = sim.energy()
        sim.integrate(t_end)
        e1 = sim.energy()

        final_particles: List[Dict[str, float]] = []
        for i in range(sim.N):
            pi = sim.particles[i]
            final_particles.append(
                {
                    "m": pi.m,
                    "x": pi.x,
                    "y": pi.y,
                    "z": pi.z,
                    "vx": pi.vx,
                    "vy": pi.vy,
                    "vz": pi.vz,
                }
            )

        result = {
            "t": sim.t,
            "N": sim.N,
            "energy_initial": e0,
            "energy_final": e1,
            "energy_delta": e1 - e0,
            "particles": final_particles,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="rebound_orbital_elements", description="Compute orbital elements for each body relative to a selected primary.")
def rebound_orbital_elements(
    particles: List[Dict[str, float]],
    primary_index: int = 0,
) -> Dict[str, Any]:
    """
    Compute orbital elements for particles in a simulation snapshot.

    Parameters:
        particles: List of particle dicts with keys m,x,y,z,vx,vy,vz.
        primary_index: Index of primary body used as orbital reference.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        sim = rebound.Simulation()
        for p in particles:
            sim.add(
                m=float(p["m"]),
                x=float(p["x"]),
                y=float(p["y"]),
                z=float(p["z"]),
                vx=float(p["vx"]),
                vy=float(p["vy"]),
                vz=float(p["vz"]),
            )

        if primary_index < 0 or primary_index >= sim.N:
            return {"success": False, "result": None, "error": "primary_index out of range"}

        primary = sim.particles[primary_index]
        elements: List[Dict[str, float]] = []

        for i in range(sim.N):
            if i == primary_index:
                continue
            orb = sim.particles[i].orbit(primary=primary)
            elements.append(
                {
                    "index": i,
                    "a": orb.a,
                    "e": orb.e,
                    "inc": orb.inc,
                    "Omega": orb.Omega,
                    "omega": orb.omega,
                    "f": orb.f,
                    "P": orb.P,
                }
            )

        return {"success": True, "result": {"N": sim.N, "elements": elements}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="rebound_simulationarchive_run", description="Integrate and write a SimulationArchive file, then report metadata.")
def rebound_simulationarchive_run(
    particles: List[Dict[str, float]],
    archive_path: str,
    t_end: float,
    snapshot_interval: float,
    integrator: str = "ias15",
    dt: float = 0.01,
) -> Dict[str, Any]:
    """
    Run a simulation and persist snapshots to a SimulationArchive file.

    Parameters:
        particles: List of particle dicts with keys m,x,y,z,vx,vy,vz.
        archive_path: Output SimulationArchive path.
        t_end: Integration end time.
        snapshot_interval: Time between saved snapshots.
        integrator: Integrator name.
        dt: Timestep.

    Returns:
        Dictionary with success/result/error fields.
    """
    try:
        sim = rebound.Simulation()
        sim.integrator = integrator
        sim.dt = dt

        for p in particles:
            sim.add(
                m=float(p["m"]),
                x=float(p["x"]),
                y=float(p["y"]),
                z=float(p["z"]),
                vx=float(p["vx"]),
                vy=float(p["vy"]),
                vz=float(p["vz"]),
            )

        sim.save_to_file(archive_path, interval=snapshot_interval)
        sim.integrate(t_end)

        sa = rebound.Simulationarchive(archive_path)
        result = {
            "archive_path": archive_path,
            "num_snapshots": len(sa),
            "t_final": sim.t,
            "N_final": sim.N,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()