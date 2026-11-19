# Model Serving Canary

Offline, zero-service, standard-library Python gate for comparing candidate and baseline binary classifier predictions on paired labeled cases. **Does not deploy models.**

## Run

```bash
python -m pip install -e .
python examples/make_fixture.py
model-serving-canary examples/synthetic_cases.csv
python -m unittest discover -s tests -v
```

JSON output includes baseline/candidate accuracy, precision, recall, F1, mean/p95 latency, and PASS/FAIL checks. Exit code 0=pass, 1=gate failure, 2=invalid input. Options: `--max-accuracy-drop`, `--min-candidate-f1`, `--max-p95-ratio`. CSV columns: `case_id,label,baseline_prediction,candidate_prediction,baseline_latency_ms,candidate_latency_ms`.

All example records are synthetic. No credentials or paid integrations. See `MASTER_PROMPT.md`, `docs/architecture.md`, `docs/research.md`, `docs/ranking.md`, `docs/verification.md`.
