# Contributing

Thanks for considering a contribution.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check .
pytest
```

## Research and numerical integrity

- Do not silently change objective functions, constraint directions, units, or SIC ordering.
- Cite the equation or source used for any mathematical change.
- Distinguish illustrative parameters from values reported in a publication.
- Do not report solver convergence or performance unless the run was performed and its environment is recorded.
- Add tests for parameter validation, model structure, and metric calculations.
- Keep solver-specific dependencies optional where possible.

Pull requests should explain the motivation, mathematical impact, tests performed, and limitations.
