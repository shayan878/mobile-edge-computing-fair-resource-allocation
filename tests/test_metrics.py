import math
import pytest
from mec_fair_allocation.metrics import evaluate_allocation

def test_metrics_are_finite_and_power_feasible(params):
    frequencies = {n: params.f_min[n] for n in params.users}
    log_power = {}
    for n in params.users:
        margin = params.power_threshold[n] - params.circuit_power - params.epsilon * frequencies[n] ** 3
        log_power[n] = math.log(0.25 * margin / params.zeta)
    result = evaluate_allocation(params, frequencies, log_power)
    assert result["sum_total_rate_bits_per_second"] > 0
    assert result["power_budgets_met"] is True

def test_wrong_decision_keys_are_rejected(params):
    with pytest.raises(ValueError, match="exactly"):
        evaluate_allocation(params, {1: params.f_min[1]}, {1: 0.0})
