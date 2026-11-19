"""Synthetic paired predictions; no patient or customer data."""
import csv
from pathlib import Path
out=Path(__file__).with_name('synthetic_cases.csv')
with out.open('w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['case_id','label','baseline_prediction','candidate_prediction','baseline_latency_ms','candidate_latency_ms'])
    for i in range(100):
        label=i%2
        baseline=1-label if i%10==0 else label
        candidate=1-label if i%20==0 else label
        w.writerow([f'synthetic-{i:03d}',label,baseline,candidate,10+i%3,11+i%3])
print(out)
