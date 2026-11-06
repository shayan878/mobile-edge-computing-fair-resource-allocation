"""SCA model for alpha=1 proportional fairness."""
import math

from pyomo.environ import ConcreteModel, Constraint, Objective, Param, Reals, Var, exp, log, maximize
from mec_fair_allocation.config import MECParameters
from mec_fair_allocation.models.common import attach_common_components, initial_log_offloading_rates, initial_log_powers, noma_rate_expression

def build_proportional_fair_model(params: MECParameters) -> ConcreteModel:
    """Build the proportional-fair SCA subproblem."""
    params.validate()
    model = ConcreteModel(name="MEC-NOMA proportional fairness")
    attach_common_components(model, params)
    rates = initial_log_offloading_rates(params, initial_log_powers(params))
    model.xk = Param(model.N, initialize=rates, mutable=True)
    model.a = Var(model.N, domain=Reals, initialize=lambda m, n: math.log(params.rate_threshold[n]))
    model.x = Var(model.N, domain=Reals, initialize=rates)
    model.minimum_rate = Constraint(model.N, rule=lambda m, n: m.a[n] >= log(m.rate_threshold[n]))
    def computation_rate_sca(m, n):
        tangent = exp(m.xk[n]) + exp(m.xk[n]) * (m.x[n] - m.xk[n])
        return exp(m.a[n]) <= tangent + m.f[n] / m.cn[n]
    model.computation_rate_sca = Constraint(model.N, rule=computation_rate_sca)
    model.offloading_rate = Constraint(model.N, rule=lambda m, n: exp(m.x[n]) <= noma_rate_expression(m, n))
    model.objective = Objective(expr=model.phi_se * sum(model.a[n] for n in model.N) - model.phi_ee * sum(model.user_power[n] for n in model.N), sense=maximize)
    return model
