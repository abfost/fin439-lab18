"""Rebuild both panels from raw SEC responses and validate assignment anchors."""
import hashlib
import json
from pathlib import Path
from panel import ROOT, build_panel, edgar, graham_checks
from app_support import unsupported_memo_numbers


def validate():
    provenance = json.loads((ROOT/'data/provenance.json').read_text())
    results = {}
    for ticker in ('COST', 'NVDA'):
        raw = ROOT/'data/raw'/f'{ticker}_companyfacts.json'
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == provenance[ticker]['sha256'], f'{ticker}: source hash mismatch'
        facts = json.loads(raw.read_text())
        report = json.loads((ROOT/'data'/f'{ticker}_report.json').read_text())
        # Re-extract without reading the saved computed values as inputs.
        rebuilt_rows = edgar.build_rows(facts)
        assert rebuilt_rows == report['rows'], f'{ticker}: saved rows differ from raw extraction'
        rebuilt = build_panel({**report, 'rows':rebuilt_rows})
        saved = json.loads((ROOT/'data'/f'{ticker}_panel.json').read_text())
        assert rebuilt == {k:v for k,v in saved.items() if k != 'number_flags'}, f'{ticker}: panel is stale'
        evidence = {k:v for k,v in rebuilt.items() if k != 'memos'}
        for investor, memo in rebuilt['memos'].items():
            assert (ROOT/'memos'/f'{ticker}_{investor.lower()}_memo.md').read_text().strip() == memo.strip()
            assert not unsupported_memo_numbers(memo, evidence), (ticker, investor, 'unsupported memo numbers')
            assert unsupported_memo_numbers(memo+' invented 987654321.25', evidence) == ['987654321.25']
        results[ticker] = {'counts':rebuilt['counts'], 'verdicts':rebuilt['verdicts'], 'source_hash_verified':True,
                           'raw_rebuild_matches_saved':True,'all_three_memo_flags_verified':True}
        if ticker == 'COST':
            assert [r['current_ratio'] for r in rebuilt['facts']] == [1.02,1.07,.97,1.03,1.06]
            assert [r['liabilities_to_equity'] for r in rebuilt['facts']] == [2.11,1.75,1.96,1.64,1.49]
            assert [c['passed'] for c in rebuilt['counts'].values()] == [3,2,2]
            assert set(graham_checks(rebuilt_rows,1).values()) == {'pass'}
            results[ticker]['threshold_probe'] = {'retained':2.0,'probe':1.0,'probe_graham_passes':3}
    return results

if __name__ == '__main__':
    result = validate()
    output = ROOT/'data/lab19_validation.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
