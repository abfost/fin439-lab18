# FIN439 Lab 18

This project turns the five-year Buffett checks into repeatable code. It uses
only SEC EDGAR company facts from annual 10-K filings; it does not use FAskills
or paid financial data.

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

## What to inspect

- `.agents/skills/buffett-edgar/SKILL.md` is the project-discoverable Codex
  skill. The script beside it selects annual 10-K facts, records XBRL tags,
  retains the latest filing for duplicate periods, and prints `not found` or
  `not known` instead of estimating.
- `data/COST_report.json` is the saved output from the tested COST script run.
- `memos/COST_buffett_memo.md` is a business-only judgment using its printed
  values. The app's editable number probe flags a value, such as `40.0%`, that
  was not printed by the script.

Your personal trust decision and reflection are intentionally not filled in.
