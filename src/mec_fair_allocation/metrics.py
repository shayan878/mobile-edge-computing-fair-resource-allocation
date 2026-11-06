"""Post-solve metrics for resource allocations."""
from __future__ import annotations
import math
from typing import Mapping
from mec_fair_allocation.config import MECParameters

def evaluate_allocation(params: MECParameters, cpu_frequency: Mapping[int, float], log_transmit_power: Mapping[int, float]) -> dict[str, object]:
    """Calculate per-user local/offloaded rates, power and feasibility indicators."""
    params.validate()
    expected = set(params.users)
    if set(cpu_frequency) != expected or set(log_transmit_power) != expected:
        raise ValueError("Decision mappings must contain exactly the configured user IDs")
    users, rates, powers = {}, [], []
    for n in params.users:
        frequency, rho = float(cpu_frequency[n]), float(log_transmit_power[n])
        if not math.isfinite(frequency) or not params.f_min[n] <= frequency <= params.f_max[n]:
            raise ValueError(f"cpu_frequency[{n}] is outside configured bounds")
        if not math.isfinite(rho):
            raise ValueError(f"log_transmit_power[{n}] must be finite")
        tx_power = math.exp(rho)
        interference = sum(math.exp(float(log_transmit_power[i])) * params.g_squared[i] for i in params.users if params.order[i] < params.order[n])
        sinr = tx_power * params.g_squared[n] / (interference + params.noise_power)
        offload = params.bandwidth * math.log2(1.0 + sinr)
        local = frequency / params.cn[n]
        total = offload + local
        power = params.zeta * tx_power + params.circuit_power + params.epsilon * frequency**3
        users[str(n)] = {
            "transmit_power_w": tx_power, "cpu_frequency_cycles_per_second": frequency,
            "offloading_rate_bits_per_second": offload, "local_rate_bits_per_second": local,
            "total_rate_bits_per_second": total, "power_w": power,
        }
        rates.append(total)
        powers.append(power)
    return {
        "users": users, "minimum_total_rate_bits_per_second": min(rates),
        "sum_total_rate_bits_per_second": sum(rates), "sum_power_w": sum(powers),
        "minimum_rate_thresholds_met": all(users[str(n)]["total_rate_bits_per_second"] + 1e-8 >= params.rate_threshold[n] for n in params.users),
        "power_budgets_met": all(users[str(n)]["power_w"] <= params.power_threshold[n] + 1e-8 for n in params.users),
    }
