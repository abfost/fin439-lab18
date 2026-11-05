#!/usr/bin/env python3
"""Fetch five fiscal years of SEC 10-K facts and compute Buffett checks."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Any

import requests


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
)

FLOW_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ],
    "capital_spending": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
}

INSTANT_TAGS = {
    "equity": ["StockholdersEquity"],
    "liabilities": ["Liabilities"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
}

DISPLAY_NAMES = {
    "revenue": "Revenue",
    "net_income": "Net income",
    "operating_cash_flow": "Operating cash flow",
    "capital_spending": "Capital spending",
    "equity": "Equity",
    "liabilities": "Liabilities",
    "roe": "ROE",
    "liabilities_to_equity": "Liabilities / equity",
    "owner_earnings": "Owner earnings",
}


def is_annual_flow(unit: dict[str, Any]) -> bool:
    """Accept annual flows reported in a 10-K."""
    if (
        unit.get("form") != "10-K"
        or not unit.get("start")
        or not unit.get("end")
    ):
        return False

    try:
        days = (
            date.fromisoformat(unit["end"])
            - date.fromisoformat(unit["start"])
        ).days
    except (ValueError, TypeError):
        return False

    # Covers ordinary calendar years and 52/53-week fiscal years.
    return 350 <= days <= 380


def is_10k_instant(unit: dict[str, Any]) -> bool:
    """Accept point-in-time facts reported in a 10-K."""
    return (
        unit.get("form") == "10-K"
        and bool(unit.get("end"))
        and not unit.get("start")
    )


def latest_by_end(
    units: list[dict[str, Any]], predicate
) -> dict[str, dict[str, Any]]:
    """Keep the latest filed eligible fact for each period end."""
    selected: dict[str, dict[str, Any]] = {}

    for unit in units:
        if not predicate(unit):
            continue

        end = unit["end"]
        old = selected.get(end)

        new_key = (
            unit.get("filed", ""),
            unit.get("accn", ""),
        )
        old_key = (
            old.get("filed", ""),
            old.get("accn", ""),
        ) if old is not None else ("", "")

        if old is None or new_key > old_key:
            selected[end] = unit

    return selected


def facts_for_tag(
    facts: dict[str, Any], tag: str
) -> list[dict[str, Any]]:
    """Return USD observations for a US-GAAP XBRL tag."""
    return (
        facts.get("facts", {})
        .get("us-gaap", {})
        .get(tag, {})
        .get("units", {})
        .get("USD", [])
    )


def latest_fiscal_ends(facts: dict[str, Any]) -> list[str]:
    """Find the latest five annual period ends in required flows."""
    ends: set[str] = set()

    for tags in FLOW_TAGS.values():
        for tag in tags:
            annual = latest_by_end(
                facts_for_tag(facts, tag),
                is_annual_flow,
            )
            ends.update(annual)

    return sorted(ends)[-5:]


def field_value(
    facts: dict[str, Any],
    tags: list[str],
    end: str,
    predicate,
) -> tuple[int | float | None, str | None]:
    """Try tags in assignment priority order for the fiscal end."""
    for tag in tags:
        unit = latest_by_end(
            facts_for_tag(facts, tag), predicate
        ).get(end)

        if unit is not None and unit.get("val") is not None:
            return unit["val"], tag

    return None, None


def in_millions(
    value: int | float | None,
) -> int | float | None:
    """Convert dollars to millions without rounding away precision."""
    if value is None:
        return None

    result = value / 1_000_000
    return int(result) if result.is_integer() else result


def build_rows(facts: dict[str, Any]) -> list[dict[str, Any]]:
    """Build annual rows; calculate using original dollar amounts."""
    rows: list[dict[str, Any]] = []

    for end in latest_fiscal_ends(facts):
        row: dict[str, Any] = {
            "fiscal_year_end": end,
            "values": {},
            "tags": {},
            "raw_values": {},
        }
        raw = row["raw_values"]

        # Annual flows: revenue, income, operating cash flow, capex.
        for name, tags in FLOW_TAGS.items():
            value, tag = field_value(
                facts, tags, end, is_annual_flow
            )
            raw[name] = value
            row["values"][name] = in_millions(value)
            row["tags"][name] = tag

        # Balance-sheet values at the same fiscal-year end.
        for name, tags in INSTANT_TAGS.items():
            value, tag = field_value(
                facts, tags, end, is_10k_instant
            )
            raw[name] = value
            row["values"][name] = in_millions(value)
            row["tags"][name] = tag

        net_income = raw["net_income"]
        equity = raw["equity"]
        liabilities = raw["liabilities"]
        capex = raw["capital_spending"]
        operating_cash_flow = raw["operating_cash_flow"]

        # Ratios are unknown when an input is missing or equity <= 0.
        raw["roe"] = (
            100 * net_income / equity
            if net_income is not None
            and equity is not None
            and equity > 0
            else None
        )
        raw["liabilities_to_equity"] = (
            liabilities / equity
            if liabilities is not None
            and equity is not None
            and equity > 0
            else None
        )

        # Missing capex is unknown, never assumed to be zero.
        raw["owner_earnings"] = (
            operating_cash_flow - capex
            if operating_cash_flow is not None
            and capex is not None
            else None
        )

        # Rounded ratios are for display only.
        for name in ("roe", "liabilities_to_equity"):
            row["values"][name] = (
                round(raw[name], 1 if name == "roe" else 2)
                if raw[name] is not None
                else None
            )

        row["values"]["owner_earnings"] = in_millions(
            raw["owner_earnings"]
        )

        row["tags"]["roe"] = (
            "NetIncomeLoss / StockholdersEquity"
        )
        row["tags"]["liabilities_to_equity"] = (
            "Liabilities / StockholdersEquity"
        )

        ocf_tag = row["tags"]["operating_cash_flow"]
        capex_tag = row["tags"]["capital_spending"]
        row["tags"]["owner_earnings"] = (
            f"{ocf_tag} - {capex_tag}"
            if ocf_tag and capex_tag
            else None
        )

        rows.append(row)

    return rows


def checks_for(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Evaluate checks using unrounded values when available."""
    # Real EDGAR rows carry fiscal_year_end. The fallback keeps the function
    # compatible with minimal callers/tests that already provide row order.
    ordered = sorted(rows, key=lambda row: row.get("fiscal_year_end", ""))

    def value(row, name):
        if "raw_values" in row:
            return row["raw_values"].get(name)
        # Supports older reports and test fixtures.
        return row["values"].get(name)

    roe = [value(row, "roe") for row in ordered]
    owner_earnings = [
        value(row, "owner_earnings") for row in ordered
    ]

    def complete(values):
        return len(values) == 5 and all(
            item is not None for item in values
        )

    roe_result = "not known"
    positive_result = "not known"
    growth_result = "not known"

    if complete(roe):
        roe_result = (
            "pass" if all(item >= 15 for item in roe) else "fail"
        )

    if complete(owner_earnings):
        positive_result = (
            "pass"
            if all(item > 0 for item in owner_earnings)
            else "fail"
        )
        growth_result = (
            "pass"
            if owner_earnings[-1] > owner_earnings[0]
            else "fail"
        )

    return {
        "ROE of 15% or more every year": roe_result,
        "Owner earnings positive every year": positive_result,
        "Owner earnings grew, first year to last": growth_result,
    }


def lookup_cik(
    ticker: str, session: requests.Session
) -> tuple[int, str]:
    response = session.get(TICKERS_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()

    for company in payload.values():
        if company["ticker"].upper() == ticker.upper():
            return int(company["cik_str"]), company["title"]

    raise ValueError(
        f"Ticker not found in SEC ticker list: {ticker}"
    )


def fetch_report(ticker: str, email: str) -> dict[str, Any]:
    ticker = ticker.strip().upper()
    email = email.strip()

    if not ticker:
        raise ValueError("Enter a ticker.")

    if not email or "@" not in email:
        raise ValueError(
            "Provide your email before making an SEC request."
        )

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": f"Aly Foster {email}",
            "Accept-Encoding": "gzip, deflate",
        })

        cik, company_name = lookup_cik(ticker, session)

        response = session.get(
            FACTS_URL.format(cik=cik),
            timeout=30,
        )
        response.raise_for_status()
        rows = build_rows(response.json())

    if not rows:
        raise ValueError(
            "No eligible annual 10-K facts were found."
        )

    return {
        "ticker": ticker,
        "company_name": company_name,
        "cik": f"{cik:010d}",
        "units": "USD millions except ROE percent",
        "rows": rows,
        "checks": checks_for(rows),
    }


def display_value(
    value: int | float | None, key: str
) -> str:
    if value is None:
        return (
            "not known"
            if key in {"roe", "liabilities_to_equity"}
            else "not found"
        )

    if key == "roe":
        return f"{value:.1f}%"

    if key == "liabilities_to_equity":
        return f"{value:.1f}"

    return f"{value:,.6f}".rstrip("0").rstrip(".")


def print_report(report: dict[str, Any]) -> None:
    print(
        f"{report['ticker']} — {report['company_name']} "
        f"(CIK {report['cik']})"
    )
    print(report["units"])

    headers = ["FY end", *DISPLAY_NAMES.values()]
    print(" | ".join(headers))

    for row in report["rows"]:
        cells = [row["fiscal_year_end"]]

        for key in DISPLAY_NAMES:
            cells.append(
                display_value(row["values"][key], key)
            )

        print(" | ".join(cells))
        print(
            "Tags: "
            + "; ".join(
                f"{DISPLAY_NAMES[key]}="
                f"{row['tags'].get(key) or 'not found'}"
                for key in DISPLAY_NAMES
            )
        )

    print("Buffett checks:")
    for label, result in report["checks"].items():
        print(f"- {label}: {result}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument(
        "--email",
        required=True,
        help="Your email for the SEC User-Agent",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON",
    )
    args = parser.parse_args()

    try:
        report = fetch_report(args.ticker, args.email)
    except (requests.RequestException, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
