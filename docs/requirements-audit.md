# Lab 19 requirements audit

Technical validation completed November 5, 2026. This document records the implementation and written analysis.

| Requirement | Status | Evidence |
|---|---|---|
| Preserve the Lab 18 app and Buffett checks | Verified | Existing chart, facts, saved-memo probe and JPM run remain; Lab 18 regression tests pass. The current COST Buffett memo is regenerated from the shared evidence. |
| Add Graham and Burry from FAskills | Verified | `.agents/skills/graham-edgar/` and `.agents/skills/burry-edgar/` contain attributed instructions and original persona reference pages. Assigned checks are implemented in `panel.py`. |
| Same annual facts and rules for all investors | Verified | One SEC annual extraction creates `report['rows']`; all three screens consume those rows. `validate_lab19.py` rebuilds them from raw companyfacts responses. |
| Liabilities, current assets, current liabilities | Verified | XBRL tags `Liabilities`, `AssetsCurrent`, `LiabilitiesCurrent`. Current ratio divides original current assets by original current liabilities. |
| Graham's three checks | Verified | Latest current ratio >= 2.0; five annual net incomes positive; first-to-last income growth. Tests cover missing inputs, zero denominator and unrounded comparisons. |
| Burry's two checks | Verified | Each year's operating cash flow >= net income; latest liabilities/equity <= 2, with positive equity. Missing ratio stays not known. |
| Separate memos from printed numbers only | Verified | Each memo lists its checks, its verdict and investor-specific annual numerical evidence. Saved memo files exactly match regenerated output. |
| App table, three verdicts, side-by-side memos | Verified | `app.py`; tested for COST and NVDA. Pass counts shown for each investor. |
| Number flag across all memos | Verified | Each of the three app memo editors was separately tested with an unsupported number. Signed and grouped decimal values also tested. This is a numeric membership check; correct year, metric and unit attribution are outside the scope of this membership check. |
| COST known answer | Verified | Buffett 3/3; Graham 2/3; Burry 2/2. Latest current ratio 1.06 fails 2.0. Both complete ratio series match the handout. |
| Threshold changed in Graham's skill | Verified | Changed `.agents/skills/graham-edgar/config.json` to 1.0 and reran COST; saved result in `data/COST_threshold_probe.json`. Restored 2.0, reran COST, and recorded the conservative-liquidity reason under Graham's memo. |
| Fund's largest company | Verified for selected VOO | NVDA, documented by Vanguard's September 30, 2026 fact sheet. Source linked in checkout notes. VOO is the selected fund for this company analysis. |
| Company's table, verdicts and memos | Verified | `data/NVDA_panel.json`, `memos/NVDA_*_memo.md`, app saved-company selector. Buffett 3/3, Graham 3/3, Burry 1/2. |
| Honest gaps | Verified in code and app | Missing facts explicitly show not found, calculated gaps/checks show not known. No estimates or substituted zeroes. COST and NVDA have complete required inputs; injected-gap tests establish behavior rather than inventing company gaps. |
| Bull and bear, two sentences each | Written discussion included | The checkout document presents a two-sentence bull case and a two-sentence bear case grounded in the NVIDIA panel. |
| Conditional trust decision | Included | The decision limits the panel to screening for further research, with failed checks, missing information, valuation and portfolio limits investigated before allocation. |
| Explain the panel and reflect | Written explanation included | Checkout notes explain shared facts/different rules, agreement/split and threshold sensitivity. |
| Graham code explanation | Written explanation included | Checkout notes explain row sorting, raw inputs, current ratio, annual income tests, first-to-last growth, missing inputs and unrounded comparisons in plain language. |

## Validation results

Validation results: all 14 tests pass. Source SHA-256 hashes match; recalculation from both raw responses matches saved rows, checks, verdicts and memos. No future-dated filing facts were found relative to the retrieval date. Exact validation details: `data/lab19_validation.json`.

## Submission links

- Repository: https://github.com/abfost/fin439-lab18
- App: https://github.com/abfost/fin439-lab18/blob/main/app.py
- Checks and memo generation: https://github.com/abfost/fin439-lab18/blob/main/panel.py
- Analysis and decision: https://github.com/abfost/fin439-lab18/blob/main/docs/lab19-checkout.md
- This audit: https://github.com/abfost/fin439-lab18/blob/main/docs/requirements-audit.md
- Reproduction validator: https://github.com/abfost/fin439-lab18/blob/main/validate_lab19.py
- Graham skill: https://github.com/abfost/fin439-lab18/blob/main/.agents/skills/graham-edgar/SKILL.md
- Burry skill: https://github.com/abfost/fin439-lab18/blob/main/.agents/skills/burry-edgar/SKILL.md
