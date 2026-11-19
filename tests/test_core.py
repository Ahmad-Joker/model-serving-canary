import csv
import io
import json
import contextlib
import tempfile
import unittest
from pathlib import Path
from model_serving_canary.core import read_cases,evaluate,DataError,percentile
from model_serving_canary.cli import main

HEADER=['case_id','label','baseline_prediction','candidate_prediction','baseline_latency_ms','candidate_latency_ms']
ROWS=[['a','1','1','1','10','11'],['b','0','0','0','10','11'],['c','1','0','1','10','11'],['d','0','0','0','10','11']]
class CanaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'data.csv';self.write(ROWS)
    def tearDown(self):self.tmp.cleanup()
    def write(self,rows,header=HEADER):
        with self.path.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(header);w.writerows(rows)
    def test_pass(self):self.assertEqual(evaluate(read_cases(self.path))['decision'],'PASS')
    def test_fail_f1(self):self.assertEqual(evaluate(read_cases(self.path),min_candidate_f1=1.0,max_p95_ratio=.5)['decision'],'FAIL')
    def test_fail_accuracy(self):
        r=[x[:] for x in ROWS];r[0][3]='0';r[1][3]='1';self.write(r)
        self.assertFalse(evaluate(read_cases(self.path))['checks']['accuracy_drop']['passed'])
    def test_bad_columns(self):
        self.write(ROWS,HEADER[:-1]);self.assertRaises(DataError,read_cases,self.path)
    def test_empty(self):self.write([]);self.assertRaises(DataError,read_cases,self.path)
    def test_duplicate(self):self.write(ROWS+[ROWS[0]]);self.assertRaises(DataError,read_cases,self.path)
    def test_bad_label(self):
        r=[x[:] for x in ROWS];r[0][1]='2';self.write(r);self.assertRaises(DataError,read_cases,self.path)
    def test_bad_latency(self):
        r=[x[:] for x in ROWS];r[0][4]='nan';self.write(r);self.assertRaises(DataError,read_cases,self.path)
    def test_negative_latency(self):
        r=[x[:] for x in ROWS];r[0][5]='-1';self.write(r);self.assertRaises(DataError,read_cases,self.path)
    def test_zero_baseline_latency(self):
        r=[x[:] for x in ROWS]
        for row in r:row[4]='0'
        self.write(r);self.assertEqual(evaluate(read_cases(self.path))['decision'],'FAIL')
    def test_percentile(self):self.assertEqual(percentile([0,10],.95),9.5)
    def test_cli_pass(self):
        with contextlib.redirect_stdout(io.StringIO()) as o:rc=main([str(self.path)])
        self.assertEqual(rc,0);self.assertEqual(json.loads(o.getvalue())['decision'],'PASS')
    def test_cli_invalid(self):
        with contextlib.redirect_stderr(io.StringIO()):rc=main(['/missing-file.csv'])
        self.assertEqual(rc,2)
    def test_invalid_gate(self):self.assertRaises(DataError,evaluate,read_cases(self.path),max_p95_ratio=0)
    def test_deterministic(self):
        c=read_cases(self.path);self.assertEqual(evaluate(c),evaluate(c))
if __name__=='__main__':unittest.main()
