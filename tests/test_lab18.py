from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from app_support import unsupported_memo_numbers

sys.path.insert(0, str(Path(".agents/skills/buffett-edgar").resolve()))
import buffett_edgar  # noqa: E402


class Lab18Tests(unittest.TestCase):
    def test_cost_matches_assignment_reference_table(self) -> None:
        report = json.loads(Path("data/COST_report.json").read_text(encoding="utf-8"))
        expected = [
            ("2022-08-28", 226954, 5844, 7392, 3891, 20642, 28.3, 3501),
            ("2023-09-03", 242290, 6292, 11068, 4323, 25058, 25.1, 6745),
            ("2024-09-01", 254453, 7367, 11339, 4710, 23622, 31.2, 6629),
            ("2025-08-31", 275235, 8099, 13335, 5498, 29164, 27.8, 7837),
            ("2026-08-30", 303154, 9226, 15817, 6435, 35803, 25.8, 9382),
        ]
        actual = [
            (
                row["fiscal_year_end"], row["values"]["revenue"], row["values"]["net_income"],
                row["values"]["operating_cash_flow"], row["values"]["capital_spending"],
                row["values"]["equity"], row["values"]["roe"], row["values"]["owner_earnings"],
            )
            for row in report["rows"]
        ]
        self.assertEqual(actual, expected)
        self.assertEqual(set(report["checks"].values()), {"pass"})

    def test_number_probe_flags_unprinted_number(self) -> None:
        report = json.loads(Path("data/COST_report.json").read_text(encoding="utf-8"))
        self.assertEqual(unsupported_memo_numbers("ROE was 40.0%.", report), ["40.0%"])

    def test_missing_owner_earnings_makes_checks_not_known(self) -> None:
        rows = [{"values": {"roe": 20.0, "owner_earnings": None}} for _ in range(5)]
        checks = buffett_edgar.checks_for(rows)
        self.assertEqual(checks["Owner earnings positive every year"], "not known")
        self.assertEqual(checks["Owner earnings grew, first year to last"], "not known")


if __name__ == "__main__":
    unittest.main()
