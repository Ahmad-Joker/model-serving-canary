# Architecture
CSV (paired synthetic or user-supplied cases) -> strict parser -> confusion-matrix metrics and latency p95 -> configurable gates -> JSON report and process exit code.

`core.py` validates and evaluates; `cli.py` handles arguments/exit codes; `make_fixture.py` produces synthetic cases; `tests/` exercises gates and errors.

Limits: binary classification only, offline labeled predictions, no live serving, no model registry, no drift detector, no statistical confidence intervals. Accuracy and F1 on small samples can mislead. A PASS does not imply production safety or fairness.
