"""Solver-aware successive convex approximation execution."""
from __future__ import annotations
import math
from dataclasses import asdict, dataclass
from typing import Any
from pyomo.environ import SolverFactory, value
from pyomo.opt import SolverStatus, TerminationCondition
from mec_fair_allocation.config import MECParameters
from mec_fair_allocation.models import build_max_min_model, build_proportional_fair_model

@dataclass(frozen=True, slots=True)
class SCAOptions:
    """Stopping criteria and nonlinear solver settings."""
    max_iterations: int = 50
    tolerance: float = 1e-4
    solver_name: str = "ipopt"
    solver_tolerance: float = 1e-7
    def __post_init__(self):
        if self.max_iterations < 1 or self.tolerance <= 0 or self.solver_tolerance <= 0:
            raise ValueError("Iteration count and tolerances must be positive")

def solve_fairness(params: MECParameters, fairness: str, options: SCAOptions | None = None) -> dict[str, Any]:
    """Solve alpha=1 or alpha=infinity; fail clearly on unusable solver results."""
    options = options or SCAOptions()
    builders = {"alpha-1": build_proportional_fair_model, "alpha-infinity": build_max_min_model}
    if fairness not in builders:
        raise ValueError(f"Unknown fairness '{fairness}'. Choose one of {tuple(builders)}")
    solver = SolverFactory(options.solver_name)
    if not solver.available(exception_flag=False):
        raise RuntimeError(f"Solver '{options.solver_name}' is unavailable; install it and add it to PATH.")
    if options.solver_name == "ipopt":
        solver.options["tol"] = options.solver_tolerance
    model = builders[fairness](params)
    point = model.xk if fairness == "alpha-1" else model.zk
    variable = model.x if fairness == "alpha-1" else model.z
    history = []
    converged = False
    accepted = {TerminationCondition.optimal, TerminationCondition.locallyOptimal, TerminationCondition.feasible}
    for iteration in range(1, options.max_iterations + 1):
        result = solver.solve(model, tee=False)
        if result.solver.status != SolverStatus.ok or result.solver.termination_condition not in accepted:
            raise RuntimeError(f"Solver returned status={result.solver.status}, termination={result.solver.termination_condition}")
        new_values = {n: float(value(variable[n])) for n in params.users}
        delta = max(abs(new_values[n] - float(value(point[n]))) for n in params.users)
        history.append({"iteration": iteration, "objective": float(value(model.objective)), "delta_inf": delta})
        for n in params.users:
            point[n] = new_values[n]
        if delta < options.tolerance:
            converged = True
            break
    frequencies = {n: float(value(model.f[n])) for n in params.users}
    log_powers = {n: float(value(model.rho[n])) for n in params.users}
    result = {
        "fairness": fairness, "converged": converged, "iterations": len(history),
        "objective": float(value(model.objective)), "cpu_frequency": frequencies,
        "log_transmit_power": log_powers,
        "transmit_power": {n: math.exp(v) for n, v in log_powers.items()},
        "history": history, "options": asdict(options),
    }
    if fairness == "alpha-infinity":
        result["minimum_total_rate_variable"] = float(value(model.minimum_total_rate))
    return result
