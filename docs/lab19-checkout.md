# Lab 19 — Legend Panel

AI use: ChatGPT/Codex helped extend the app, implement and test the checks, and draft these notes. Educational analysis, not investment advice. Review the proposed decision in your own words.

## Company and fund
VOO; NVIDIA (NVDA), its largest holding in Vanguard's September 30, 2026 fact sheet (8.4%). Source: https://workplace.vanguard.com/assets/corp/fund_communications/pdf_publish/us-products/fact-sheet/F0968.pdf . This fund choice still needs comparison with the Lab 13 mandate before Project 2 portfolio construction.

## Known answer and threshold
COST: Buffett 3/3, Graham 2/3, Burry 2/2. Current ratios: 1.02, 1.07, 0.97, 1.03, 1.06. Liabilities/equity: 2.11, 1.75, 1.96, 1.64, 1.49. These are calculated from SEC facts, not used as data inputs.
Lowering Graham's threshold to 1.0 changes its COST liquidity result to pass. Retain 2.0 to preserve the assigned conservative screen; interpret a failure as a reason to investigate rather than an automatic investment rejection.

## NVIDIA: agreement and split
Buffett passes all three checks; Graham passes all three; Burry passes leverage but fails cash conversion. Operating cash flow is below net income in fiscal years ending 2022, 2024, 2025 and 2026. That does not by itself prove bad accounting.

## How the investors differ
Graham would look at Costco differently from Buffett because he puts more emphasis on liquidity. Costco passes Buffett’s checks, but its current ratio of 1.06 falls below Graham’s requirement of 2.0.

## Bull case on NVIDIA
NVIDIA passes all of Buffett’s and Graham’s checks, showing positive earnings, growth, and positive owner earnings. It also passes Burry’s leverage check, which supports the case that its balance sheet is manageable.

## Bear case on NVIDIA
NVIDIA fails Burry’s requirement that operating cash flow cover net income every year. That makes me want to investigate why cash flow falls below reported earnings before trusting the overall positive results.

## Why the panel disagrees
The investors use the same facts, but they focus on different things. Buffett emphasizes profitability and owner earnings, Graham checks liquidity and earnings stability, and Burry focuses on cash backing up earnings and liabilities compared with equity.

## What the threshold change shows
Changing Graham’s current-ratio requirement from 2.0 to 1.0 makes Costco pass without changing anything about the company. I would keep 2.0 because it preserves the original conservative rule, but I would investigate a failure instead of automatically rejecting the company.

## Proposed decision — review and adopt or revise
I would use the panel to screen companies for further research, provided that I investigate failed checks, missing information, valuation, and portfolio limits before making an allocation.

## Graham code explanation
The `graham_checks` function takes the company’s annual data and checks it against Graham’s three rules.

First, it sorts the rows by fiscal-year end so the years are in order. Then it gets the latest year’s original values, before rounding.

Next, it gets current assets and current liabilities. It divides current assets by current liabilities to calculate the current ratio, but only if both numbers are available and current liabilities are greater than zero. Otherwise, it leaves the ratio unknown.

The function also makes a list of net income for each year. It uses that list to check whether income was positive every year and whether it increased from the first year to the last.

Finally, it returns a result for each check. The current-ratio check passes if the actual ratio meets the threshold. The positive-income check requires five years of available income, and the growth check compares the first and last years within the five-year window.

If an input is missing, the affected check returns “not known.” The code does not guess the missing number or replace it with zero. It also compares the original numbers rather than the rounded display values, so rounding cannot accidentally turn a failure into a pass.

## What is a panel?
These are three persona-inspired skills implemented as deterministic screens, not three independently reasoning autonomous agents. Shared facts can produce different verdicts because the screens test different properties and thresholds. Multiple personas do not provide independent evidence; they reuse the same financial statements.

## Reflection preparation
The panel agrees on NVIDIA's positive income, growing owner earnings and acceptable latest leverage. It splits on earnings quality: Burry's cash-conversion rule fails even while Buffett and Graham pass their screens. Changing the COST liquidity cutoff changes Graham's verdict without changing Costco's facts; a verdict depends on the chosen rules, so retain and disclose the cutoff rather than treating a pass as objective proof of suitability.

## Audit evidence
See `docs/requirements-audit.md` and `data/lab19_validation.json`. Fourteen tests pass, including reproduction from saved raw SEC data, every COST reference ratio, threshold sensitivity, missing data and a separate flag probe in each investor's app memo. The actual skill-setting probe is saved in `data/COST_threshold_probe.json`; the retained threshold is restored to 2.0.
