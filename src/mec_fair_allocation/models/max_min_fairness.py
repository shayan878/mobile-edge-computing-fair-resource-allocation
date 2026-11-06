"""SCA model for alpha=infinity max-min fairness."""
from pyomo.environ import ConcreteModel, Constraint, Objective, Param, Reals, Var, exp, maximize
from mec_fair_allocation.config import MECParameters
from mec_fair_allocation.models.common import attach_common_components, initial_log_offloading_rates, initial_log_powers, noma_rate_expression

def build_max_min_model(params: MECParameters) -> ConcreteModel:
    """Build the max-min SCA subproblem using the source script's threshold form."""
    params.validate()
    model = ConcreteModel(name="MEC-NOMA max-min fairness")
    attach_common_components(model, params)
    rates = initial_log_offloading_rates(params, initial_log_powers(params))
    model.zk = Param(model.N, initialize=rates, mutable=True)
    model.z = Var(model.N, domain=Reals, initialize=rates)
    model.minimum_total_rate = Var(domain=Reals, initialize=max(params.rate_threshold.values()))
    # Retained from the original script. See docs/model-formulation.md before interpreting.
    model.minimum_rate_threshold = Constraint(model.N, rule=lambda m, n: m.minimum_total_rate >= m.rate_threshold[n])
    def total_rate_sca(m, n):
        tangent = exp(m.zk[n]) + exp(m.zk[n]) * (m.z[n] - m.zk[n])
        return m.minimum_total_rate <= tangent + m.f[n] / m.cn[n]
    model.total_rate_sca = Constraint(model.N, rule=total_rate_sca)
    model.offloading_rate = Constraint(model.N, rule=lambda m, n: exp(m.z[n]) <= noma_rate_expression(m, n))
    model.objective = Objective(expr=model.phi_se * model.minimum_total_rate - model.phi_ee * sum(model.user_power[n] for n in model.N), sense=maximize)
    return model
