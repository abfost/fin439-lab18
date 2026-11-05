"""Lab 19: deterministic persona screens over one shared annual report."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
GRAHAM_CONFIG = ROOT / '.agents/skills/graham-edgar/config.json'
DEFAULT_GRAHAM_THRESHOLD = json.loads(GRAHAM_CONFIG.read_text())['current_ratio_threshold']
spec = importlib.util.spec_from_file_location('buffett_edgar', ROOT/'.agents/skills/buffett-edgar/buffett_edgar.py')
edgar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edgar)


def annual_check(values, predicate):
    # Require the complete five-year window; never fill a gap.
    if len(values) != 5 or any(v is None for v in values):
        return 'not known'
    return 'pass' if all(predicate(v) for v in values) else 'fail'


def growth(values):
    if len(values) != 5 or values[0] is None or values[-1] is None:
        return 'not known'
    return 'pass' if values[-1] > values[0] else 'fail'


def graham_checks(rows, threshold=DEFAULT_GRAHAM_THRESHOLD):
    ordered = sorted(rows, key=lambda r: r['fiscal_year_end'])
    latest = ordered[-1]['raw_values'] if ordered else {}
    assets = latest.get('current_assets')
    liabilities = latest.get('current_liabilities')
    # Missing inputs and nonpositive denominators cannot produce a ratio.
    ratio = assets / liabilities if assets is not None and liabilities is not None and liabilities > 0 else None
    income = [r['raw_values'].get('net_income') for r in ordered]
    return {
        f'Current ratio at least {threshold:.1f}, latest year': 'not known' if ratio is None else ('pass' if ratio >= threshold else 'fail'),
        'Net income positive every year': annual_check(income, lambda v: v > 0),
        'Net income grew, first year to last': growth(income),
    }


def burry_checks(rows):
    ordered = sorted(rows, key=lambda r: r['fiscal_year_end'])
    cash = []
    for r in ordered:
        v = r['raw_values']
        ocf, ni = v.get('operating_cash_flow'), v.get('net_income')
        cash.append(None if ocf is None or ni is None else ocf >= ni)
    latest = ordered[-1]['raw_values'] if ordered else {}
    ratio = latest.get('liabilities_to_equity')
    return {
        'Operating cash flow at least net income every year': annual_check(cash, bool),
        'Liabilities no more than twice equity, latest year': 'not known' if ratio is None else ('pass' if ratio <= 2 else 'fail'),
    }


def verdict(checks):
    if 'fail' in checks.values():
        return 'watch it'
    if 'not known' in checks.values():
        return 'not known'
    return 'own the business'


def build_panel(report, threshold=DEFAULT_GRAHAM_THRESHOLD):
    rows = sorted(report['rows'], key=lambda r: r['fiscal_year_end'])
    checks = {'Buffett': edgar.checks_for(rows), 'Graham': graham_checks(rows, threshold), 'Burry': burry_checks(rows)}
    display = []
    for row in rows:
        raw = row['raw_values']
        ca, cl = raw.get('current_assets'), raw.get('current_liabilities')
        ratio = ca/cl if ca is not None and cl is not None and cl > 0 else None
        display.append({'FY end': row['fiscal_year_end'], **row['values'],
                        'current_ratio': None if ratio is None else round(ratio, 2)})
    result = {'ticker':report['ticker'], 'company_name':report['company_name'], 'threshold':threshold,
              'facts': display, 'checks':checks, 'verdicts':{k:verdict(v) for k,v in checks.items()}}
    result['counts'] = {investor: {'passed': list(items.values()).count('pass'),
                                  'failed': list(items.values()).count('fail'),
                                  'not_known': list(items.values()).count('not known'),
                                  'total': len(items)} for investor, items in checks.items()}
    memos = {}
    for investor, items in checks.items():
        lines = [f"{report['ticker']} — {investor}: {result['verdicts'][investor]}."]
        lines += [f'{label}: {status}.' for label,status in items.items()]
        if investor == 'Buffett':
            for fact in display:
                roe, oe = fact.get('roe'), fact.get('owner_earnings')
                lines.append(f"FY end {fact['FY end']}: ROE " + ('not known' if roe is None else f'{roe:.1f}%')
                             + '; owner earnings ' + ('not known' if oe is None else f'{oe:,}') + ' USD millions.')
        if investor == 'Graham':
            ratio = display[-1]['current_ratio'] if display else None
            lines.append('Latest current ratio: '+('not known' if ratio is None else f'{ratio:.2f}')+'.')
            for fact in display:
                income = fact.get('net_income')
                lines.append(f"FY end {fact['FY end']}: net income " + ('not found' if income is None else f'{income:,}') + ' USD millions.')
            lines.append(f'Threshold retained: {threshold:.1f}; '+('keep the assignment’s conservative liquidity requirement.' if threshold == 2 else 'relaxed liquidity screen; interpret separately from the required validation.'))
        if investor == 'Burry':
            ratio = display[-1].get('liabilities_to_equity') if display else None
            lines.append('Latest liabilities / equity: '+('not known' if ratio is None else f'{ratio:.2f}')+'.')
            for fact in display:
                ocf, income = fact.get('operating_cash_flow'), fact.get('net_income')
                lines.append(f"FY end {fact['FY end']}: operating cash flow " + ('not found' if ocf is None else f'{ocf:,}')
                             + '; net income ' + ('not found' if income is None else f'{income:,}') + ' USD millions.')
        lines.append({'Buffett':'Focus: profitability and cash remaining after capital spending.', 'Graham':'Focus: liquidity and earnings stability.', 'Burry':'Focus: cash backing earnings and balance-sheet obligations.'}[investor])
        lines.append('Business judgment only: this simplified screen does not establish a fair purchase price or justify an allocation. Any failed check means watch it; an incomplete screen without a failure remains not known. A positive business judgment still requires further research. Missing inputs remain not known.')
        memos[investor] = '\n\n'.join(lines)
    result['memos'] = memos
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ticker')
    parser.add_argument('--email')
    parser.add_argument('--facts', help='Local unmodified SEC companyfacts JSON')
    parser.add_argument('--threshold', type=float, default=DEFAULT_GRAHAM_THRESHOLD)
    args = parser.parse_args()
    if args.facts:
        facts = json.loads(Path(args.facts).read_text())
        report = {'ticker':args.ticker.upper(), 'company_name':facts.get('entityName',''), 'cik':str(facts['cik']).zfill(10), 'units':'USD millions; ROE percent; other ratios dimensionless', 'rows':edgar.build_rows(facts)}
        report['checks'] = edgar.checks_for(report['rows'])
    elif args.email:
        report = edgar.fetch_report(args.ticker,args.email)
    else:
        parser.error('Supply --facts or --email')
    panel = build_panel(report,args.threshold)
    # All memo numbers must exist in this printed evidence, excluding memos.
    evidence = {k:v for k,v in panel.items() if k != 'memos'}
    from app_support import unsupported_memo_numbers
    panel['number_flags'] = {k:unsupported_memo_numbers(v,evidence) for k,v in panel['memos'].items()}
    print(json.dumps(panel,indent=2))
    (ROOT/'data'/f'{args.ticker.upper()}_report.json').write_text(json.dumps(report,indent=2))
    (ROOT/'data'/f'{args.ticker.upper()}_panel.json').write_text(json.dumps(panel,indent=2))
    for investor,memo in panel['memos'].items():
        (ROOT/'memos'/f'{args.ticker.upper()}_{investor.lower()}_memo.md').write_text(memo+'\n')

if __name__ == '__main__':
    main()
