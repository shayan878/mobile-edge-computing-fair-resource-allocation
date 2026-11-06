import pytest
from mec_fair_allocation.config import MECParameters

def test_example_config_loads(params):
    assert params.users == (1, 2, 3)

def test_round_trip_mapping(params):
    assert MECParameters.from_mapping(params.to_mapping()) == params

def test_missing_user_parameter_is_rejected(params):
    data = params.to_mapping()
    del data["g_squared"]["2"]
    with pytest.raises(ValueError, match="g_squared keys"):
        MECParameters.from_mapping(data)

def test_duplicate_sic_order_is_rejected(params):
    data = params.to_mapping()
    data["order"]["2"] = data["order"]["1"]
    with pytest.raises(ValueError, match="unique"):
        MECParameters.from_mapping(data)

def test_nonpositive_noise_is_rejected(params):
    data = params.to_mapping()
    data["noise_power"] = 0
    with pytest.raises(ValueError, match="noise_power"):
        MECParameters.from_mapping(data)
