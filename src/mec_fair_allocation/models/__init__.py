"""Optimization model builders."""
from mec_fair_allocation.models.max_min_fairness import build_max_min_model
from mec_fair_allocation.models.proportional_fairness import build_proportional_fair_model
__all__ = ["build_max_min_model", "build_proportional_fair_model"]
