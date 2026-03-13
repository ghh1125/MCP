import os
import sys
from typing import Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from pyomo.environ import (
    ConcreteModel,
    Var,
    Objective,
    Constraint,
    NonNegativeReals,
    SolverFactory,
    minimize,
    value,
)
from pyomo.opt import SolverStatus, TerminationCondition
from pyomo.core.base.componentuid import ComponentUID
from pyomo.util.model_size import build_model_size_report
from pyomo.util.infeasible import log_infeasible_constraints

mcp = FastMCP("pyomo_mcp_service")


@mcp.tool(name="create_linear_model", description="Create and solve a small linear optimization model.")
def create_linear_model(
    objective_x: float,
    objective_y: float,
    rhs_constraint_1: float,
    rhs_constraint_2: float,
    solver_name: str = "glpk",
) -> Dict[str, Any]:
    """
    Create and solve a 2-variable linear model.

    Parameters:
        objective_x: Coefficient of x in objective.
        objective_y: Coefficient of y in objective.
        rhs_constraint_1: Right-hand side for x + y >= rhs_constraint_1.
        rhs_constraint_2: Right-hand side for 2x + y >= rhs_constraint_2.
        solver_name: Solver executable/interface name (e.g., glpk, cbc, highs).

    Returns:
        Dictionary with success/result/error:
        - success: True if solver run produced a feasible/optimal style termination.
        - result: Solution details, objective value, and solver status when available.
        - error: Error string when unsuccessful, else None.
    """
    try:
        model = ConcreteModel()
        model.x = Var(domain=NonNegativeReals)
        model.y = Var(domain=NonNegativeReals)

        model.c1 = Constraint(expr=model.x + model.y >= rhs_constraint_1)
        model.c2 = Constraint(expr=2 * model.x + model.y >= rhs_constraint_2)
        model.obj = Objective(expr=objective_x * model.x + objective_y * model.y, sense=minimize)

        solver = SolverFactory(solver_name)
        if solver is None or not solver.available(exception_flag=False):
            return {"success": False, "result": None, "error": f"Solver '{solver_name}' is not available."}

        res = solver.solve(model, tee=False)
        status = str(res.solver.status)
        term = str(res.solver.termination_condition)

        feasible_terms = {
            str(TerminationCondition.optimal),
            str(TerminationCondition.locallyOptimal),
            str(TerminationCondition.feasible),
        }
        ok = (status == str(SolverStatus.ok)) or (term in feasible_terms)

        result = {
            "solver_status": status,
            "termination_condition": term,
            "x": value(model.x),
            "y": value(model.y),
            "objective": value(model.obj),
        }
        return {"success": ok, "result": result, "error": None if ok else "Solver did not report an accepted status."}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="evaluate_expression", description="Evaluate a Pyomo expression given variable values.")
def evaluate_expression(
    expression: str,
    x_value: float,
    y_value: float,
) -> Dict[str, Any]:
    """
    Evaluate an algebraic expression using Pyomo variables x and y.

    Parameters:
        expression: Python-style expression using x and y (e.g., '3*x + 2*y').
        x_value: Numeric value assigned to x.
        y_value: Numeric value assigned to y.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        model = ConcreteModel()
        model.x = Var(initialize=x_value)
        model.y = Var(initialize=y_value)

        safe_locals: Dict[str, Any] = {"x": model.x, "y": model.y}
        pyomo_expr = eval(expression, {"__builtins__": {}}, safe_locals)
        evaluated = value(pyomo_expr)
        return {"success": True, "result": {"value": evaluated}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="model_size_report", description="Generate structural size statistics for a simple generated model.")
def model_size_report(
    num_vars: int,
    include_linking_constraints: bool,
) -> Dict[str, Any]:
    """
    Build a simple model and return size report metrics.

    Parameters:
        num_vars: Number of nonnegative variables to create.
        include_linking_constraints: Whether to add chain constraints v[i] <= v[i+1].

    Returns:
        Dictionary with success/result/error containing size report attributes.
    """
    try:
        if num_vars <= 0:
            return {"success": False, "result": None, "error": "num_vars must be > 0"}

        model = ConcreteModel()
        model.v = Var(range(num_vars), domain=NonNegativeReals)

        model.obj = Objective(expr=sum(model.v[i] for i in range(num_vars)), sense=minimize)

        if include_linking_constraints and num_vars > 1:
            model.link = Constraint(range(num_vars - 1), rule=lambda m, i: m.v[i] <= m.v[i + 1])

        report = build_model_size_report(model)
        result = {
            "activated_variables": int(report.activated.variables),
            "activated_constraints": int(report.activated.constraints),
            "activated_objectives": int(report.activated.objectives),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="component_uid_roundtrip", description="Create and resolve ComponentUID for a named variable.")
def component_uid_roundtrip(
    var_name: str,
    index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Demonstrate ComponentUID creation and lookup.

    Parameters:
        var_name: Variable base name ('x' or 'v').
        index: Optional index for indexed variable v.

    Returns:
        Dictionary with success/result/error containing CUID string and resolved component name.
    """
    try:
        model = ConcreteModel()
        model.x = Var(domain=NonNegativeReals)
        model.v = Var(range(3), domain=NonNegativeReals)

        if var_name == "x":
            comp = model.x
        elif var_name == "v":
            if index is None:
                return {"success": False, "result": None, "error": "index is required when var_name='v'"}
            comp = model.v[index]
        else:
            return {"success": False, "result": None, "error": "var_name must be 'x' or 'v'"}

        cuid = ComponentUID(comp)
        resolved = cuid.find_component_on(model)

        result = {
            "cuid": str(cuid),
            "resolved_name": resolved.name if resolved is not None else None,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="check_infeasibility", description="Create a contradictory model and detect infeasibility through solver output.")
def check_infeasibility(
    solver_name: str = "glpk",
) -> Dict[str, Any]:
    """
    Build an infeasible model and report solver termination.

    Parameters:
        solver_name: Solver to use.

    Returns:
        Dictionary with success/result/error including infeasibility indicators.
    """
    try:
        model = ConcreteModel()
        model.x = Var(domain=NonNegativeReals)
        model.c1 = Constraint(expr=model.x >= 2.0)
        model.c2 = Constraint(expr=model.x <= 1.0)
        model.obj = Objective(expr=model.x, sense=minimize)

        solver = SolverFactory(solver_name)
        if solver is None or not solver.available(exception_flag=False):
            return {"success": False, "result": None, "error": f"Solver '{solver_name}' is not available."}

        res = solver.solve(model, tee=False)
        status = str(res.solver.status)
        term = str(res.solver.termination_condition)

        try:
            log_infeasible_constraints(model)
        except Exception:
            pass

        result = {
            "solver_status": status,
            "termination_condition": term,
            "is_infeasible": term in {
                str(TerminationCondition.infeasible),
                str(TerminationCondition.infeasibleOrUnbounded),
            },
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()