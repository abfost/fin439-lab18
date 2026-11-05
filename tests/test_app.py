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

class PanelAppAuditTests(unittest.TestCase):
    def test_each_panel_memo_flags_and_nvda_runs(self):
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py').run(timeout=15)
        for idx in (1,2,3):
            original = app.text_area[idx].value
            app.text_area[idx].set_value(original+' Invented 987654321.25').run(timeout=15)
            self.assertFalse(app.exception)
            self.assertTrue(any('987654321.25' in w.value for w in app.warning))
            app.text_area[idx].set_value(original).run(timeout=15)
            self.assertFalse(app.warning)
        app.select_slider[0].set_value(1.0).run(timeout=15)
        self.assertFalse(app.exception)
        self.assertTrue(all(app.table[-1].value.query("Investor == 'Graham'")['Result'] == 'pass'))
        app.sidebar.selectbox[0].select('NVDA').run(timeout=15)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_area),4)
        self.assertEqual(app.table[-1].value.query("Investor == 'Burry'")['Result'].tolist(), ['fail','pass'])

    def test_missing_facts_are_explicit(self):
        report=json.loads(Path('data/COST_report.json').read_text())
        report['rows'][-1]['raw_values']['current_assets']=None
        report['rows'][-1]['values']['current_assets']=None
        app=AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py')
        app.session_state['report']=report
        app.session_state['saved_ticker']='COST'
        app.run(timeout=15)
        self.assertFalse(app.exception)
        self.assertEqual(app.dataframe[-1].value.iloc[-1]['current_assets'],'not found')
        self.assertEqual(app.dataframe[-1].value.iloc[-1]['current_ratio'],'not known')
