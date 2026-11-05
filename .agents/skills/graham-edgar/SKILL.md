---
name: graham-edgar
description: Apply the Lab 19 Graham business checks to shared SEC annual facts and write a memo using printed numbers only.
---

# Graham EDGAR screen

Source: https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/ben_graham.md
Read references/ben_graham.md for the original persona. This lab deliberately implements only the assigned checks, not the source's full valuation framework.

Run `python panel.py TICKER --email EMAIL` from the repository root, using the user's supplied SEC contact email. Alternatively use `--facts PATH` for a saved, unmodified SEC companyfacts response.

Checks: Current ratio at least 2.0 in the latest year; positive net income every year; net income grew from first year to last.
The implementation is `graham_checks` in `panel.py`. Use unrounded inputs for decisions. Keep missing inputs as not known; never infer capital spending or fill a gap. All investors read the same rows.

Write the Graham memo from the printed evidence only. Use the code-produced checks and verdict. Do not add prices, forecasts, or unsupported financial figures. Run the shared memo number flag across every investor memo. A screen is not a valuation or an allocation recommendation.
