import pytest
pyomo = pytest.importorskip("pyomo.environ")
from mec_fair_allocation.models import build_max_min_model, build_proportional_fair_model

def test_both_model_builders_create_expected_components(params):
    proportional = build_proportional_fair_model(params)
    max_min = build_max_min_model(params)
    assert len(proportional.N) == 3
    assert len(proportional.power_budget) == 3
    assert len(proportional.offloading_rate) == 3
    assert proportional.objective.sense == pyomo.maximize
    assert len(max_min.N) == 3
    assert len(max_min.power_budget) == 3
    assert len(max_min.offloading_rate) == 3
    assert max_min.objective.sense == pyomo.maximize

def test_sca_expansion_point_is_mutable(params):
    model = build_proportional_fair_model(params)
    model.xk[1] = float(model.xk[1]) + 0.01
    assert float(model.xk[1]) > 0
