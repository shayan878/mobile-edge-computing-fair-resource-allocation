# Fair Resource Allocation for NOMA-Enabled Mobile Edge Computing

[![CI](https://github.com/shayan878/mobile-edge-computing-fair-resource-allocation/actions/workflows/ci.yml/badge.svg)](https://github.com/shayan878/mobile-edge-computing-fair-resource-allocation/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pyomo](https://img.shields.io/badge/optimization-Pyomo-orange.svg)](https://www.pyomo.org/)

A modular Python implementation of two fairness-oriented resource-allocation formulations for a NOMA-enabled mobile edge computing (MEC) network. The project models proportional fairness (alpha = 1) and max-min fairness (alpha = infinity) using Pyomo and successive convex approximation (SCA).

> **Research implementation, not a certified reproduction.** The included three-user configuration is illustrative and comes from the original scripts. It is not presented as the paper's official simulation configuration. Solver results must be generated and validated in your own environment.

## Research reference

Q. Wang and F. Zhou, “Fair Resource Allocation in an MEC-Enabled Ultra-Dense IoT Network with NOMA,” *2019 IEEE International Conference on Communications Workshops (ICC Workshops)*, 2019, pp. 1–6.

**DOI:** [10.1109/ICCW.2019.8757173](https://doi.org/10.1109/ICCW.2019.8757173)

This work studies resource allocation in ultra-dense IoT networks using mobile edge computing and non-orthogonal multiple access, and proposes an iterative successive-convex-approximation approach to non-convex resource-allocation problems.

## What is implemented?

| Fairness case | Module | Purpose |
|---|---|---|
| alpha = 1 | `models/proportional_fairness.py` | Proportional-fair optimization formulation |
| alpha = infinity | `models/max_min_fairness.py` | Max-min-fair optimization formulation |
| Shared model | `models/common.py` | NOMA rate, power model and initial values |
| SCA execution | `solver.py` | Iterative solve, convergence history and solver checks |
| Metrics | `metrics.py` | Per-user rates, power and feasibility indicators |

## Repository structure

```text
.
├── .github/workflows/       # CI across supported Python versions
├── configs/scenarios/       # Versioned example parameter sets
├── docs/                    # Model notes and reproducibility guide
├── src/mec_fair_allocation/
│   ├── models/
│   │   ├── common.py
│   │   ├── proportional_fairness.py
│   │   └── max_min_fairness.py
│   ├── cli.py
│   ├── config.py
│   ├── metrics.py
│   └── solver.py
├── tests/                   # Unit and model-structure tests
├── CITATION.cff
├── CONTRIBUTING.md
└── pyproject.toml
```

## Quick start

### 1. Install

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

### 2. Install a nonlinear solver

The model uses Pyomo. IPOPT is the default nonlinear solver and must be installed separately. Confirm that the `ipopt` executable is available on your `PATH`.

### 3. Run proportional fairness

```bash
mec-fair-allocation \
  --config configs/scenarios/three-user-example.json \
  --fairness alpha-1 \
  --output results/alpha-1.json
```

### 4. Run max-min fairness

```bash
mec-fair-allocation \
  --config configs/scenarios/three-user-example.json \
  --fairness alpha-infinity \
  --output results/alpha-infinity.json
```

You can also run the CLI without installing the console entry point:

```bash
python -m mec_fair_allocation.cli --help
```

## Configure your own scenario

Copy `configs/scenarios/three-user-example.json` and update the user-indexed values. Every per-user mapping must contain exactly the same user IDs as the `users` list.

The configuration documents the following physical quantities:

- `bandwidth`: Hz
- `noise_power`, `power_threshold`, `circuit_power`: W
- `f_min`, `f_max`: CPU cycles/s
- `g_squared`: squared channel magnitude
- `cn`: CPU cycles per input bit, as used by the source implementation
- `order`: unique SIC ordering index

The parameter validator checks positive physical quantities, matching user keys, CPU bounds, power feasibility at minimum frequency, and unique SIC order.

## Algorithm outline

1. Validate scenario parameters.
2. Build the selected Pyomo model.
3. Initialize log-domain transmit powers and SCA expansion points.
4. Solve the current nonlinear subproblem.
5. Update expansion points and calculate the infinity-norm change.
6. Stop at the configured tolerance or iteration limit.
7. Export decision variables, iteration history, and derived metrics.

The solver checks termination status and fails explicitly if a usable solution is not returned.

## Tests and code quality

```bash
ruff check .
pytest
python -m build
```

The CI workflow runs linting, tests and a package build on Python 3.10, 3.11 and 3.12. Model-construction tests require Pyomo but do not require IPOPT; the end-to-end optimization requires a separately installed solver.

## Mathematical notes and limitations

Read [Model formulation](docs/model-formulation.md) and [Reproducibility](docs/reproducibility.md) before interpreting numerical results.

In particular, the max-min model retains the direction of the rate-threshold constraint from the original script. That direction needs to be checked against the exact equation and variable definitions in the paper before treating it as a conventional QoS lower bound. The implementation deliberately does not silently change the mathematical formulation.

## Citation

If you use this implementation, cite the paper above. Repository metadata is provided in [CITATION.cff](CITATION.cff).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Mathematical changes should identify the source equation, units, and validation evidence.

## License

No license has been added because the repository did not previously specify one. Until a license is selected, reuse and redistribution permissions are not granted by default.
