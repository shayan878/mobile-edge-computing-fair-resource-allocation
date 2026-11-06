# Model formulation and implementation notes

## Scope

This repository implements the two fairness cases represented in the original code:

- **Alpha = 1:** proportional-fair objective.
- **Alpha = infinity:** max-min-fair objective.

Both models use a NOMA uplink rate expression and successive convex approximation (SCA) expansion points. Model construction is separated from solver execution.

## Shared expressions

For each user n, transmit power is represented in the log domain as rho_n = ln(p_n), CPU frequency is f_n, and the offloading rate is:

R_off,n = B log2(1 + exp(rho_n) |g_n|^2 / (sigma^2 + sum_i exp(rho_i)|g_i|^2)),

where the interference sum follows the configured SIC order (o_i < o_n).

The per-user power expression is:

P_n = zeta exp(rho_n) + P_circuit + epsilon f_n^3.

The local computation-rate term in the supplied implementation is f_n/C_n. The SCA constraints approximate the exponential rate terms around mutable expansion points.

## Alpha = 1

The proportional-fair model maximizes the weighted sum of auxiliary log-rate variables, less the weighted power cost. Its SCA constraint uses the first-order tangent of the exponential at the current expansion point.

## Alpha = infinity

The max-min model maximizes a common minimum-rate variable subject to per-user SCA upper bounds and the rate-threshold constraint retained from the original script.

**Formulation caveat:** the original code uses `minimum_total_rate >= rate_threshold[n]`. This is not the conventional direction for a minimum-rate QoS constraint. It has been retained rather than silently reversed because the exact variable definition and units must be checked against the derivation before changing the mathematics. Consult the [reference paper](https://doi.org/10.1109/ICCW.2019.8757173).

## Numerical interpretation

The values in `configs/scenarios/three-user-example.json` are the illustrative three-user values in the original scripts. They are not claimed to be the paper's official simulation setup or validated reproduction results.

## Solver and convergence

The outer loop stops when the infinity norm of the change in log-rate expansion points is below tolerance, or when the iteration limit is reached. Solver status and termination condition are checked after every subproblem. A successful local NLP solve is not a proof of global optimality for the original non-convex problem.
