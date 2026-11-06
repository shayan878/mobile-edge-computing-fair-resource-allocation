"""Typed model parameters and validation for the MEC resource-allocation problem."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

_INDEXED_FIELDS = (
    "cn",
    "rate_threshold",
    "power_threshold",
    "f_min",
    "f_max",
    "g_squared",
    "order",
)


@dataclass(frozen=True, slots=True)
class MECParameters:
    """Parameters shared by the alpha=1 and alpha=infinity optimization models.

    Power values are in watts, CPU frequencies in cycles/second, bandwidth in hertz,
    channel gains as squared magnitudes, and noise as power.
    """

    users: tuple[int, ...]
    phi_se: float
    phi_ee: float
    zeta: float
    circuit_power: float
    epsilon: float
    cn: Mapping[int, float]
    bandwidth: float
    noise_power: float
    rate_threshold: Mapping[int, float]
    power_threshold: Mapping[int, float]
    f_min: Mapping[int, float]
    f_max: Mapping[int, float]
    g_squared: Mapping[int, float]
    order: Mapping[int, int]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> MECParameters:
        """Create and validate parameters from a JSON-compatible mapping."""
        users = tuple(int(user) for user in data.get("users", ()))
        converted: dict[str, dict[int, float | int]] = {}
        for name in _INDEXED_FIELDS:
            raw = data[name]
            if not isinstance(raw, Mapping):
                raise ValueError(f"{name} must be an object keyed by user ID")
            converted[name] = {
                int(user): int(value) if name == "order" else float(value)
                for user, value in raw.items()
            }

        params = cls(
            users=users,
            phi_se=float(data["phi_se"]),
            phi_ee=float(data["phi_ee"]),
            zeta=float(data["zeta"]),
            circuit_power=float(data["circuit_power"]),
            epsilon=float(data["epsilon"]),
            cn=converted["cn"],
            bandwidth=float(data["bandwidth"]),
            noise_power=float(data["noise_power"]),
            rate_threshold=converted["rate_threshold"],
            power_threshold=converted["power_threshold"],
            f_min=converted["f_min"],
            f_max=converted["f_max"],
            g_squared=converted["g_squared"],
            order=converted["order"],
        )
        params.validate()
        return params

    @classmethod
    def from_json(cls, path: str | Path) -> MECParameters:
        """Load parameters from a JSON file."""
        with Path(path).open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError("The parameter file must contain a JSON object")
        return cls.from_mapping(data)

    def validate(self) -> None:
        """Raise ValueError when parameters are missing, invalid or inconsistent."""
        if not self.users:
            raise ValueError("users must contain at least one user ID")
        if len(set(self.users)) != len(self.users):
            raise ValueError("users contains duplicate IDs")
        user_set = set(self.users)

        for name in _INDEXED_FIELDS:
            mapping = getattr(self, name)
            if set(mapping) != user_set:
                missing = sorted(user_set - set(mapping))
                extra = sorted(set(mapping) - user_set)
                raise ValueError(
                    f"{name} keys do not match users (missing={missing}, extra={extra})"
                )

        for name, value in {
            "phi_se": self.phi_se,
            "phi_ee": self.phi_ee,
            "zeta": self.zeta,
            "bandwidth": self.bandwidth,
            "noise_power": self.noise_power,
        }.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and greater than zero")

        for name, value in {
            "circuit_power": self.circuit_power,
            "epsilon": self.epsilon,
        }.items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")

        for user in self.users:
            for name, value in {
                "cn": self.cn[user],
                "rate_threshold": self.rate_threshold[user],
                "power_threshold": self.power_threshold[user],
                "f_min": self.f_min[user],
                "g_squared": self.g_squared[user],
            }.items():
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f"{name}[{user}] must be finite and greater than zero")

            if not math.isfinite(self.f_max[user]) or self.f_max[user] < self.f_min[user]:
                raise ValueError(f"f_max[{user}] must be finite and >= f_min[{user}]")

            remaining = (
                self.power_threshold[user]
                - self.circuit_power
                - self.epsilon * self.f_min[user] ** 3
            )
            if remaining <= 0:
                raise ValueError(
                    f"power_threshold[{user}] leaves no positive offloading-power margin "
                    "at f_min"
                )

        if len(set(self.order.values())) != len(self.users):
            raise ValueError("order values must be unique to define an unambiguous SIC order")

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "users": list(self.users),
            "phi_se": self.phi_se,
            "phi_ee": self.phi_ee,
            "zeta": self.zeta,
            "circuit_power": self.circuit_power,
            "epsilon": self.epsilon,
            "cn": {str(k): v for k, v in self.cn.items()},
            "bandwidth": self.bandwidth,
            "noise_power": self.noise_power,
            "rate_threshold": {str(k): v for k, v in self.rate_threshold.items()},
            "power_threshold": {str(k): v for k, v in self.power_threshold.items()},
            "f_min": {str(k): v for k, v in self.f_min.items()},
            "f_max": {str(k): v for k, v in self.f_max.items()},
            "g_squared": {str(k): v for k, v in self.g_squared.items()},
            "order": {str(k): v for k, v in self.order.items()},
        }
