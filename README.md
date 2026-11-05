# FIN439 Labs 18–19 — Legend Panel

This project turns the five-year Buffett checks into repeatable code. It uses
only SEC EDGAR company facts from annual 10-K filings for financial data. Lab 19 adapts the Graham and Burry frameworks from FAskills; no paid financial data is used.

## Run it in PowerShell

```powershell
uv venv .venv --python 3.12
uv pip install -r requirements.txt --python .venv\Scripts\python.exe
.\.venv\Scripts\python.exe .agents\skills\buffett-edgar\buffett_edgar.py COST --email "your-email@example.com"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\streamlit.exe run app.py
```

The third command sends your email only as part of the SEC-required User-Agent
header (`Aly Foster your-email@example.com`). The app asks for the email again
only when you request fresh SEC data; it does not save it.

## Repository contents

- `.agents/skills/buffett-edgar/SKILL.md` is the project-discoverable Codex
  skill. The script beside it selects annual 10-K facts, records XBRL tags,
  retains the latest filing for duplicate periods, and prints `not found` or
  `not known` instead of estimating.
- `data/COST_report.json` is the saved output from the tested COST script run.
- `memos/COST_buffett_memo.md` is a business-only judgment using its printed
  values. The app's editable number probe flags a value, such as `40.0%`, that
  was not printed by the script.

The Lab 19 checkout document contains the company analysis, bull and bear cases, code explanation, reflection and conditional decision.


## Lab 19 — Legend Panel

The original Buffett app remains, with a three-investor panel added below it.
Select COST or NVDA from Saved company; the saved SEC runs need no email.
Use Graham's threshold control to compare 2.0 with 1.0, and edit each memo to
probe the cross-memo number flag. Financial checks use unrounded source amounts.

```sh
python -m pip install -r requirements.txt
python panel.py COST --email YOUR_EMAIL
python panel.py NVDA --email YOUR_EMAIL
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

`panel.py` prints the evidence, checks, verdicts, memos and per-memo number flags,
and saves reproducible reports and memos. The two added project skills are under
`.agents/skills/graham-edgar` and `.agents/skills/burry-edgar`; each credits its
FAskills source. These simplified screens do not claim to reproduce the full
investors' strategies. The results, discussion, code explanation and conditional decision are recorded in `docs/lab19-checkout.md`.

## Offline reproduction and audit

```sh
python panel.py COST --facts data/raw/COST_companyfacts.json
python panel.py NVDA --facts data/raw/NVDA_companyfacts.json
python validate_lab19.py
```

The saved raw responses and SHA-256 hashes in `data/provenance.json` let a grader reproduce the reports without a network request. See `docs/requirements-audit.md` for the requirement-by-requirement implementation evidence. The numeric flag checks value membership, including signs and decimals, not whether the prose assigns the correct unit, year or metric.
