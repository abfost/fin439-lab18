import copy
import json
import unittest
from pathlib import Path
from panel import build_panel, graham_checks, burry_checks
from app_support import unsupported_memo_numbers

class PanelTests(unittest.TestCase):
    def test_cost_and_probe(self):
        report=json.loads(Path('data/COST_report.json').read_text())
        panel=build_panel(report)
        self.assertEqual([list(c.values()).count('pass') for c in panel['checks'].values()],[3,2,2])
        self.assertEqual([r['current_ratio'] for r in panel['facts']],[1.02,1.07,.97,1.03,1.06])
        self.assertEqual([r['liabilities_to_equity'] for r in panel['facts']],[2.11,1.75,1.96,1.64,1.49])
        self.assertEqual(set(graham_checks(report['rows'],1).values()),{'pass'})
        evidence={k:v for k,v in panel.items() if k!='memos'}
        for investor,memo in panel['memos'].items():
            self.assertEqual(unsupported_memo_numbers(memo,evidence),[],investor)
            self.assertEqual(unsupported_memo_numbers(memo+' invented 987654321',evidence),['987654321'],investor)
    def test_gaps_and_zero_denominator(self):
        report=json.loads(Path('data/COST_report.json').read_text())
        rows=copy.deepcopy(report['rows'])
        rows[-1]['raw_values']['current_liabilities']=0
        self.assertEqual(next(iter(graham_checks(rows).values())),'not known')
        rows[1]['raw_values']['operating_cash_flow']=None
        self.assertEqual(next(iter(burry_checks(rows).values())),'not known')
    def test_nvda_split(self):
        panel=json.loads(Path('data/NVDA_panel.json').read_text())
        self.assertEqual(list(panel['checks']['Burry'].values()),['fail','pass'])
