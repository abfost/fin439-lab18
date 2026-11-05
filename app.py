"""FIN439 Lab 18: reproducible Buffett-style SEC EDGAR review."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from app_support import unsupported_memo_numbers
from panel import build_panel

ROOT = Path(__file__).parent
SCRIPT = ROOT / ".agents" / "skills" / "buffett-edgar" / "buffett_edgar.py"

st.set_page_config(page_title="FIN439 Lab 18", page_icon=":material/account_balance:", layout="wide")
st.title("Legend Panel — Buffett, Graham and Burry")
st.caption("data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")


def saved_report(ticker: str) -> dict | None:
    path = ROOT / "data" / f"{ticker.upper()}_report.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def run_edgar(ticker: str, email: str) -> tuple[dict | None, str | None]:
    """Run the bundled script; the email is passed only to its SEC User-Agent."""
    command = [sys.executable, str(SCRIPT), ticker, "--email", email, "--json"]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=75, check=False)
    if completed.returncode:
        return None, completed.stderr.strip() or completed.stdout.strip()
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError:
        return None, "The EDGAR script returned data that was not valid JSON."


def table_for(report: dict) -> pd.DataFrame:
    labels = {
        "fiscal_year_end": "FY end",
        "revenue": "Revenue",
        "net_income": "Net income",
        "operating_cash_flow": "Operating cash flow",
        "capital_spending": "Capital spending",
        "equity": "Equity",
        "liabilities": "Liabilities",
        "roe": "ROE %",
        "liabilities_to_equity": "Liabilities / equity",
        "owner_earnings": "Owner earnings",
    }
    display_rows = []
    for row in report["rows"]:
        values = row["values"]
        item = {"FY end": row["fiscal_year_end"]}
        for key, label in labels.items():
            if key == "fiscal_year_end":
                continue
            value = values.get(key)
            if value is None:
                item[label] = "not known" if key in {"roe", "liabilities_to_equity"} else "not found"
            elif key == "roe":
                item[label] = f"{value:.1f}%"
            elif key == "liabilities_to_equity":
                item[label] = f"{value:.1f}"
            else:
                item[label] = f"{value:,}"
        display_rows.append(item)
    return pd.DataFrame(display_rows)


with st.sidebar:
    st.header("Run SEC EDGAR data")
    with st.form("edgar_form"):
        ticker = st.text_input("Ticker", value="COST", max_chars=10).upper().strip()
        email = st.text_input("Email for the SEC User-Agent", type="password")
        submitted = st.form_submit_button("Fetch SEC facts", icon=":material/download:", width="stretch")
    st.caption("The email is used only in the request header and is not saved by this app.")

saved_ticker = st.sidebar.selectbox("Saved company", ["COST", "NVDA", "JPM"])
if st.session_state.get("saved_ticker") != saved_ticker:
    st.session_state.saved_ticker = saved_ticker
    st.session_state.report = saved_report(saved_ticker)

if "report" not in st.session_state:
    st.session_state.report = saved_report("COST")

if submitted:
    if not ticker:
        st.error("Enter a ticker before fetching SEC facts.")
    elif "@" not in email:
        st.error("Enter an email address so the SEC User-Agent identifies Aly Foster.")
    else:
        with st.spinner("Getting 10-K company facts from SEC EDGAR..."):
            report, error = run_edgar(ticker, email)
        if error:
            st.error(error)
        else:
            st.session_state.report = report

report = st.session_state.report
if report is None:
    st.info("Enter a ticker and your email in the sidebar, then select Fetch SEC facts.")
    st.stop()

st.subheader(f"{report['ticker']} — {report['company_name']}")
st.caption(f"CIK {report['cik']} · {report['units']} · 10-K annual facts only")

rows = report["rows"]
chart_data = pd.DataFrame(
    [
        {
            "Fiscal year end": row["fiscal_year_end"],
            "Net income": row["values"]["net_income"],
            "Owner earnings": row["values"]["owner_earnings"],
        }
        for row in rows
    ]
).melt("Fiscal year end", var_name="Measure", value_name="USD millions")
chart_data = chart_data.dropna(subset=["USD millions"])
chart = (
    alt.Chart(chart_data)
    .mark_line(point=True)
    .encode(
        x=alt.X("Fiscal year end:N", title="Fiscal year end"),
        y=alt.Y("USD millions:Q", title="USD millions"),
        color=alt.Color("Measure:N", title=None),
        tooltip=["Fiscal year end:N", "Measure:N", alt.Tooltip("USD millions:Q", format=",")],
    )
)
with st.container(border=True):
    st.subheader("Owner earnings and net income")
    st.altair_chart(chart, width="stretch", alt="Owner earnings and net income across the available fiscal years.")

with st.container(border=True):
    st.subheader("Five-year SEC facts and calculations")
    st.dataframe(table_for(report), hide_index=True, alt="Five annual SEC fact rows with calculated ROE and owner earnings.")
    with st.expander("XBRL tags used"):
        for row in rows:
            tags = "; ".join(f"{key}: {value or 'not found'}" for key, value in row["tags"].items())
            st.caption(f"{row['fiscal_year_end']} — {tags}")

with st.container(border=True):
    st.subheader("Buffett checks computed by code")
    checks = pd.DataFrame(
        [{"Check": check, "Result": result} for check, result in report["checks"].items()]
    )
    st.table(checks, border="horizontal", width="stretch")

memo_path = ROOT / "memos" / f"{report['ticker']}_buffett_memo.md"
if memo_path.exists():
    saved_memo = memo_path.read_text(encoding="utf-8")
    if st.session_state.get("memo_ticker") != report["ticker"]:
        st.session_state.memo_ticker = report["ticker"]
        st.session_state.memo_text = saved_memo
    with st.container(border=True):
        st.subheader("Saved Buffett-style memo")
        st.markdown(saved_memo)
        st.divider()
        probe_memo = st.text_area(
            "Memo number probe",
            key="memo_text",
            height=220,
            help="Try adding a number such as 40.0% that the script did not print.",
        )
        unsupported = unsupported_memo_numbers(probe_memo, report)
        if unsupported:
            st.warning(
                "Unsupported numeric value(s): " + ", ".join(unsupported) + ". Remove them or run the script again."
            )
        else:
            st.success("Every numeric value in this memo appears in the script output.")
else:
    st.info("No saved memo exists for this ticker yet. Use the Buffett EDGAR skill after reviewing this script output.")


st.header("Three-investor panel")
threshold = st.select_slider("Graham current-ratio threshold", options=[1.0, 2.0], value=2.0)
panel = build_panel(report, threshold)
evidence = {k:v for k,v in panel.items() if k != "memos"}
st.dataframe(pd.DataFrame(panel["facts"]), hide_index=True)
st.table(pd.DataFrame([{"Investor": investor, "Check": label, "Result": status}
    for investor, checks in panel["checks"].items() for label,status in checks.items()]))
for column, investor in zip(st.columns(3), panel["memos"]):
    with column:
        st.subheader(investor)
        st.write("Verdict: " + panel["verdicts"][investor])
        memo = st.text_area("Memo and number probe", value=panel["memos"][investor],
            height=420, key=f"panel_{report['ticker']}_{investor}_{threshold}")
        flags = unsupported_memo_numbers(memo, evidence)
        if flags:
            st.warning("Unprinted numbers: " + ", ".join(flags))
        else:
            st.success("All memo numbers occur in printed evidence.")
with st.expander("Printed evidence used by all memo number checks"):
    st.json(evidence)
