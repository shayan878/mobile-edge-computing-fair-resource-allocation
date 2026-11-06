from pathlib import Path
import pytest
from mec_fair_allocation.config import MECParameters

@pytest.fixture
def params():
    return MECParameters.from_json(Path(__file__).resolve().parents[1] / "configs/scenarios/three-user-example.json")
