"""Command-line interface."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from mec_fair_allocation.config import MECParameters
from mec_fair_allocation.metrics import evaluate_allocation
from mec_fair_allocation.solver import SCAOptions, solve_fairness

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mec-fair-allocation", description="Solve MEC-NOMA fair resource allocation.")
    parser.add_argument("--config", required=True, help="JSON model parameter file")
    parser.add_argument("--fairness", choices=("alpha-1", "alpha-infinity"), required=True)
    parser.add_argument("--solver", default="ipopt")
    parser.add_argument("--max-iterations", type=int, default=50)
    parser.add_argument("--tolerance", type=float, default=1e-4)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    return parser

def main() -> int:
    args = build_parser().parse_args()
    params = MECParameters.from_json(args.config)
    result = solve_fairness(params, args.fairness, SCAOptions(solver_name=args.solver, max_iterations=args.max_iterations, tolerance=args.tolerance))
    result["metrics"] = evaluate_allocation(params, result["cpu_frequency"], result["log_transmit_power"])
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
