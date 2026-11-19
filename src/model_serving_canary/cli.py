import argparse
import json
import sys
from .core import DataError, read_cases, evaluate

def main(argv=None):
    p=argparse.ArgumentParser(description='Offline model candidate promotion gate')
    p.add_argument('csv_path')
    p.add_argument('--max-accuracy-drop',type=float,default=.02)
    p.add_argument('--min-candidate-f1',type=float,default=.7)
    p.add_argument('--max-p95-ratio',type=float,default=1.25)
    args=p.parse_args(argv)
    try:
        report=evaluate(read_cases(args.csv_path),args.max_accuracy_drop,args.min_candidate_f1,args.max_p95_ratio)
    except DataError as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr)
        return 2
    print(json.dumps(report,indent=2,allow_nan=False))
    return 0 if report['decision']=='PASS' else 1
if __name__=='__main__': sys.exit(main())
