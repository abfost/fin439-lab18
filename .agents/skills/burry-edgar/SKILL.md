---
name: burry-edgar
description: Apply the Lab 19 Burry business checks to shared SEC annual facts and write a memo using printed numbers only.
---

# Burry EDGAR screen

Source: https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md
Read references/michael_burry.md for the original persona. This lab deliberately implements only the assigned checks, not the source's full valuation framework.

Run `python panel.py TICKER --email EMAIL` from the repository root, using the user's supplied SEC contact email. Alternatively use `--facts PATH` for a saved, unmodified SEC companyfacts response.

Checks: Operating cash flow at least net income every year; latest liabilities no more than twice positive equity.
The implementation is `burry_checks` in `panel.py`. Use unrounded inputs for decisions. Keep missing inputs as not known; never infer capital spending or fill a gap. All investors read the same rows.

Write the Burry memo from the printed evidence only. Use the code-produced checks and verdict. Do not add prices, forecasts, or unsupported financial figures. Run the shared memo number flag across every investor memo. A screen is not a valuation or an allocation recommendation.
