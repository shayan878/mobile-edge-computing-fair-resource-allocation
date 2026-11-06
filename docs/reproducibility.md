# Reproducibility

## Environment

- Python 3.10+
- Pyomo 6.8+
- IPOPT (or another compatible Pyomo nonlinear solver)

Create an environment and install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Install IPOPT separately using your operating system's package manager or a trusted solver distribution. Verify it is available on `PATH`.

## Run both fairness cases

```bash
mec-fair-allocation --config configs/scenarios/three-user-example.json --fairness alpha-1 --output results/alpha-1.json
mec-fair-allocation --config configs/scenarios/three-user-example.json --fairness alpha-infinity --output results/alpha-infinity.json
```

The included JSON contains an illustrative three-user scenario normalized from the original scripts. Replace it with the parameter values and units for the experiment you intend to reproduce.

## Validation

```bash
ruff check .
pytest
python -m build
```

Automated tests cover parameter consistency, model construction, mutable SCA expansion points, and metric calculations. They do not claim to validate a full IPOPT numerical run or reproduce the paper's plots.
