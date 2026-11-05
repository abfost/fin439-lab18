# Lab 19 — Legend Panel

AI use: ChatGPT/Codex helped extend the app, implement and test the checks, and draft these notes. Educational analysis, not investment advice. Review the proposed decision in your own words.

## Company and fund
VOO; NVIDIA (NVDA), its largest holding in Vanguard's September 30, 2026 fact sheet (8.4%). Source: https://workplace.vanguard.com/assets/corp/fund_communications/pdf_publish/us-products/fact-sheet/F0968.pdf . This fund choice still needs comparison with the Lab 13 mandate before Project 2 portfolio construction.

## Known answer and threshold
COST: Buffett 3/3, Graham 2/3, Burry 2/2. Current ratios: 1.02, 1.07, 0.97, 1.03, 1.06. Liabilities/equity: 2.11, 1.75, 1.96, 1.64, 1.49. These are calculated from SEC facts, not used as data inputs.
Lowering Graham's threshold to 1.0 changes its COST liquidity result to pass. Retain 2.0 to preserve the assigned conservative screen; interpret a failure as a reason to investigate rather than an automatic investment rejection.

## NVIDIA: agreement and split
Buffett passes all three checks; Graham passes all three; Burry passes leverage but fails cash conversion. Operating cash flow is below net income in fiscal years ending 2022, 2024, 2025 and 2026. That does not by itself prove bad accounting.

## Bull case draft — for your discussion
NVIDIA passes the profitability, owner-earnings and Graham checks, supporting a financially strong business case. Its latest liquidity and leverage results also support resilience.

## Bear case draft — for your discussion
Burry's cash-conversion check fails because operating cash flow does not cover net income in every year. Even a strong business screen leaves valuation and the reasons for the cash-flow gap unexamined.

## Proposed decision — review and adopt or revise
Only with a condition: use the panel to identify companies for further research, and require a review of cash-conversion failures, valuation, missing data and portfolio mandate limits before any allocation.

## Code explanation preparation
Open graham_checks in panel.py. It sorts the same fiscal rows, gets the latest current assets and current liabilities, and divides only when both are present and liabilities are positive. Missing or invalid inputs return not known. annual_check requires five nonmissing years before deciding whether all net incomes are positive. growth compares the first and last income; missing endpoints return not known. Comparisons use unrounded amounts.

## What is a panel?
These are three persona-inspired skills implemented as deterministic screens, not three independently reasoning autonomous agents. Shared facts can produce different verdicts because the screens test different properties and thresholds. Multiple personas do not provide independent evidence; they reuse the same financial statements.

## Activities you must actually complete
- Open Brightspace → Quizzes → Lab 19 at the required time.
- Do the initial no-screen partner explanation.
- Explain Graham's function line by line without AI and answer the missing-input question; swap.
- Discuss the bull and bear cases and swap roles.
- Explain the panel and threshold lesson to your partner.
- Review the proposed decision and submit your individual GitHub links.

These notes do not claim those partner activities have happened.

## Reflection preparation
The panel agrees on NVIDIA's positive income, growing owner earnings and acceptable latest leverage. It splits on earnings quality: Burry's cash-conversion rule fails even while Buffett and Graham pass their screens. Changing the COST liquidity cutoff changes Graham's verdict without changing Costco's facts; a verdict depends on the chosen rules, so retain and disclose the cutoff rather than treating a pass as objective proof of suitability.

## Audit evidence
See `docs/requirements-audit.md` and `data/lab19_validation.json`. Fourteen tests pass, including reproduction from saved raw SEC data, every COST reference ratio, threshold sensitivity, missing data and a separate flag probe in each investor's app memo. The actual skill-setting probe is saved in `data/COST_threshold_probe.json`; the retained threshold is restored to 2.0.
