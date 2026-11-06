"""Shared Pyomo components for MEC-NOMA resource allocation."""
from __future__ import annotations
import math
from pyomo.environ import ConcreteModel, Constraint, Expression, NonNegativeReals, Param, Reals, Set, Var, exp, log
from mec_fair_allocation.config import MECParameters

def initial_log_powers(params: MECParameters) -> dict[int, float]:
    result = {}
    for user in params.users:
        margin = params.power_threshold[user] - params.circuit_power - params.epsilon * params.f_min[user] ** 3
        result[user] = math.log(max(0.25 * margin / params.zeta, 1e-12))
    return result

def initial_log_offloading_rates(params: MECParameters, log_powers: dict[int, float]) -> dict[int, float]:
    powers = {user: math.exp(log_powers[user]) for user in params.users}
    points = {}
    for user in params.users:
        interference = sum(powers[other] * params.g_squared[other] for other in params.users if params.order[other] < params.order[user])
        sinr = powers[user] * params.g_squared[user] / (interference + params.noise_power)
        points[user] = math.log(max(params.bandwidth * math.log2(1.0 + sinr) * 0.5, 1e-12))
    return points

def attach_common_components(model: ConcreteModel, params: MECParameters) -> None:
    model.N = Set(initialize=params.users, ordered=True)
    for name, value in {"phi_se": params.phi_se, "phi_ee": params.phi_ee, "zeta": params.zeta, "circuit_power": params.circuit_power, "epsilon": params.epsilon, "bandwidth": params.bandwidth, "noise_power": params.noise_power}.items():
        setattr(model, name, Param(initialize=value))
    for name, mapping in {"cn": params.cn, "rate_threshold": params.rate_threshold, "power_threshold": params.power_threshold, "f_min": params.f_min, "f_max": params.f_max, "g_squared": params.g_squared, "sic_order": params.order}.items():
        setattr(model, name, Param(model.N, initialize=mapping))
    powers = initial_log_powers(params)
    model.f = Var(model.N, domain=NonNegativeReals, bounds=lambda m, n: (m.f_min[n], m.f_max[n]), initialize=lambda m, n: m.f_min[n])
    model.rho = Var(model.N, domain=Reals, initialize=lambda m, n: powers[n])
    model.user_power = Expression(model.N, rule=lambda m, n: m.zeta * exp(m.rho[n]) + m.circuit_power + m.epsilon * m.f[n] ** 3)
    model.power_budget = Constraint(model.N, rule=lambda m, n: m.user_power[n] <= m.power_threshold[n])

def noma_rate_expression(model: ConcreteModel, user: int):
    interference = sum(exp(model.rho[other]) * model.g_squared[other] for other in model.N if model.sic_order[other] < model.sic_order[user])
    sinr = exp(model.rho[user]) * model.g_squared[user] / (interference + model.noise_power)
    return model.bandwidth * log(1 + sinr) / log(2)
