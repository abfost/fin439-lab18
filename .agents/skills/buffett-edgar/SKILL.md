---
name: buffett-edgar
description: Analyze a public company as a Buffett-style business judgment using reproducible SEC EDGAR 10-K facts; use when asked for the five-year Buffett checks or a business-only memo.
---

# Buffett EDGAR business analysis

Use this skill for a ticker only when the user has supplied an email address for
the SEC EDGAR User-Agent. Never use FAskills or a paid data source.

1. Run `python .agents/skills/buffett-edgar/buffett_edgar.py TICKER --email EMAIL --json`.
2. Treat the script output as the only source for financial numbers. Do not
   estimate a missing item or calculate a new number in the memo.
3. State the three code-produced checks exactly. If a check is `not known`,
   explain that the corresponding judgment cannot be made from the available
   inputs.
4. Write a short Markdown memo to `memos/TICKER_buffett_memo.md`. Make a
   business judgment of **own the business**, **watch it**, or **pass** based
   only on the printed numbers and the checks. Do not mention a share price,
   valuation, price target, margin of safety, or investment recommendation.
5. Before saving, compare every numeric token in the memo against the script's
   printed output. Remove or spell out any number that did not appear there.

The calculation rules are implemented in the bundled script: use its output,
not your memory of a company or another financial-data source.
