import unittest
import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_cost_dashboard_renders_and_flags_probe(self) -> None:
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=15)
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "Legend Panel — Buffett, Graham and Burry")
        self.assertEqual(len(app.dataframe), 2)
        self.assertEqual(len(app.text_area), 4)
        self.assertTrue(any("Current ratio" in str(item.value) for item in app.table))

        app.text_area[0].set_value("ROE was 40.0%.").run(timeout=15)
        self.assertFalse(app.exception)
        self.assertTrue(app.warning)
        self.assertIn("40.0%", app.warning[0].value)

    def test_jpm_saved_memo_displays_without_number_warning(self) -> None:
        report = json.loads(Path("data/JPM_report.json").read_text(encoding="utf-8"))
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py")
        app.session_state["report"] = report
        app.session_state["saved_ticker"] = "COST"
        app.run(timeout=15)
        self.assertFalse(app.exception)
        self.assertFalse(app.warning)
        self.assertTrue(app.success)
        self.assertTrue(any("JPM Buffett-style business memo" in item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
