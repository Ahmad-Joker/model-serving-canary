import csv
import math
from pathlib import Path

COLUMNS = ('case_id','label','baseline_prediction','candidate_prediction','baseline_latency_ms','candidate_latency_ms')
class DataError(ValueError):
    pass

def read_cases(path):
    try:
        with Path(path).open(newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or set(reader.fieldnames) != set(COLUMNS):
                raise DataError('CSV must contain exactly the six required columns, without duplicates')
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as e:
        raise DataError(f'Cannot read CSV: {e}') from e
    if not rows:
        raise DataError('CSV has no cases')
    ids = set()
    cases=[]
    for i,row in enumerate(rows, start=2):
        if None in row or any(row[k] is None or not row[k].strip() for k in COLUMNS):
            raise DataError(f'Row {i}: missing or extra fields')
        ident = row['case_id'].strip()
        if ident in ids:
            raise DataError(f'Row {i}: duplicate case_id {ident}')
        ids.add(ident)
        vals=[]
        for k in ('label','baseline_prediction','candidate_prediction'):
            if row[k].strip() not in ('0','1'):
                raise DataError(f'Row {i}: {k} must be 0 or 1')
            vals.append(int(row[k]))
        for k in ('baseline_latency_ms','candidate_latency_ms'):
            try: x=float(row[k])
            except ValueError as e: raise DataError(f'Row {i}: invalid {k}') from e
            if not math.isfinite(x) or x < 0:
                raise DataError(f'Row {i}: {k} must be finite and nonnegative')
            vals.append(x)
        cases.append((ident,*vals))
    return cases

def percentile(values, fraction):
    a=sorted(values)
    p=(len(a)-1)*fraction
    lo=math.floor(p); hi=math.ceil(p)
    return a[lo]+(a[hi]-a[lo])*(p-lo)

def metrics(cases, pred_index, latency_index):
    tp=sum(c[1]==1 and c[pred_index]==1 for c in cases)
    tn=sum(c[1]==0 and c[pred_index]==0 for c in cases)
    fp=sum(c[1]==0 and c[pred_index]==1 for c in cases)
    fn=sum(c[1]==1 and c[pred_index]==0 for c in cases)
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    latencies=[c[latency_index] for c in cases]
    return {'n':len(cases),'accuracy':(tp+tn)/len(cases),'precision':precision,'recall':recall,'f1':f1,'p95_latency_ms':percentile(latencies,.95),'mean_latency_ms':sum(latencies)/len(cases),'tp':tp,'tn':tn,'fp':fp,'fn':fn}

def evaluate(cases,max_accuracy_drop=.02,min_candidate_f1=.7,max_p95_ratio=1.25):
    for name,x in [('max_accuracy_drop',max_accuracy_drop),('min_candidate_f1',min_candidate_f1)]:
        if not math.isfinite(x) or x<0 or x>1: raise DataError(f'{name} must be in [0,1]')
    if not math.isfinite(max_p95_ratio) or max_p95_ratio<=0: raise DataError('max_p95_ratio must be positive')
    base=metrics(cases,2,4); cand=metrics(cases,3,5)
    checks={
      'accuracy_drop':{'passed':cand['accuracy'] >= base['accuracy']-max_accuracy_drop-1e-12,'actual':base['accuracy']-cand['accuracy'],'limit':max_accuracy_drop},
      'candidate_f1':{'passed':cand['f1'] >= min_candidate_f1,'actual':cand['f1'],'minimum':min_candidate_f1},
      'p95_latency_ratio':{'passed':cand['p95_latency_ms'] <= base['p95_latency_ms']*max_p95_ratio+1e-12,'actual':None if base['p95_latency_ms']==0 else cand['p95_latency_ms']/base['p95_latency_ms'],'limit':max_p95_ratio}
    }
    return {'decision':'PASS' if all(v['passed'] for v in checks.values()) else 'FAIL','baseline':base,'candidate':cand,'checks':checks,'note':'Offline paired evaluation only; does not measure production drift, fairness, or live serving.'}
