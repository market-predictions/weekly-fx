from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.fx_release_assurance import (
    build_lab_assurance,
    evaluate_production_promotion_from_lab,
    validate_lab_assurance,
)


class FXReleaseAssuranceTests(unittest.TestCase):
    def _fixture(self, root: Path, *, include_risk_surface: bool = True) -> dict[str, Path]:
        output = root / "output"
        output.mkdir()
        report = output / "weekly_fx_review_260505_03.md"
        sections = []
        for number in range(1, 18):
            body = "Evidence and portfolio discipline. " * 20
            if number == 3:
                body += "\n### FX carry dashboard\nCarry evidence.\n### USD cash contradiction check\nCash evidence.\n"
                if include_risk_surface:
                    body += "### Risk-bucket exposure\nRisk evidence.\n"
            if number == 14:
                body += "\nTrades executed this run: BUY AUD and MXN.\n"
            sections.append(f"## {number}. Section {number}\n{body}")
        report.write_text("# Weekly FX Review 2026-05-05\n\n" + "\n\n".join(sections), encoding="utf-8")
        clean = output / "weekly_fx_review_260505_03_clean.md"
        clean.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
        html = output / "weekly_fx_review_260505_03_delivery.html"
        html.write_text("<!doctype html><html><body>" + ("validated FX delivery " * 100) + "</body></html>", encoding="utf-8")
        pdf = output / "weekly_fx_review_260505_03.pdf"
        pdf.write_bytes(b"%PDF-" + b"0" * 2048)
        png = output / "weekly_fx_review_260505_03_equity_curve.png"
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 256)

        manifest = {
            "valuation_date": "2026-05-05",
            "most_common_pair_date": "2026-05-05",
            "pairs_requested": 2,
            "pairs_refreshed": 2,
            "nav_usd": 100544.34,
            "cash_usd": 24165.26,
            "nav_usd_after_carry_accrual": 100544.34,
            "cash_usd_after_carry_accrual": 24165.26,
            "pair_rows": [
                {"currency": "EUR", "status": "fresh"},
                {"currency": "JPY", "status": "fresh"},
            ],
        }
        (output / "fx_state_refresh_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (output / "fx_portfolio_state.json").write_text(
            json.dumps({"nav_usd": 100544.34, "cash_usd": 24165.26, "last_valuation": {"date": "2026-05-05"}}),
            encoding="utf-8",
        )
        (output / "fx_technical_overlay.json").write_text(json.dumps({"as_of": "2026-05-05"}), encoding="utf-8")
        (output / "fx_risk_bucket_snapshot.json").write_text(json.dumps({"as_of": "2026-05-05"}), encoding="utf-8")
        for name, content in {
            "fx_trade_ledger.csv": "date,currency,action\n2026-05-05,AUD,BUY\n",
            "fx_valuation_history.csv": "date,nav_usd\n2026-05-05,100544.34\n",
            "fx_recommendation_scorecard.csv": "currency,action\nAUD,BUY\n",
            "fx_carry_snapshot.csv": "currency,estimated_carry\nAUD,1.04\n",
        }.items():
            (output / name).write_text(content, encoding="utf-8")
        return {"report": report.relative_to(root), "clean": clean.relative_to(root), "html": html.relative_to(root), "pdf": pdf.relative_to(root), "png": png.relative_to(root), "assurance": Path("output/fx_release_assurance_260505_03.json")}

    def test_valid_lab_candidate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = self._fixture(root)
            old = Path.cwd()
            try:
                os.chdir(root)
                record = build_lab_assurance(
                    source_sha="c" * 40,
                    github_run_id="123",
                    repository="market-predictions/weekly-fx",
                    environment="lab",
                    report=fx["report"],
                    clean_markdown=fx["clean"],
                    delivery_html=fx["html"],
                    pdf=fx["pdf"],
                    equity_curve_png=fx["png"],
                    output=fx["assurance"],
                )
                self.assertEqual(record["decision"], "PASS")
                validate_lab_assurance(fx["assurance"], expected_source_sha="c" * 40, expected_report=str(fx["report"]))
            finally:
                os.chdir(old)

    def test_missing_alpha_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = self._fixture(root, include_risk_surface=False)
            old = Path.cwd()
            try:
                os.chdir(root)
                record = build_lab_assurance(
                    source_sha="c" * 40,
                    github_run_id="123",
                    repository="market-predictions/weekly-fx",
                    environment="lab",
                    report=fx["report"],
                    clean_markdown=fx["clean"],
                    delivery_html=fx["html"],
                    pdf=fx["pdf"],
                    equity_curve_png=fx["png"],
                    output=fx["assurance"],
                )
                self.assertEqual(record["decision"], "FAIL")
                self.assertIn("alpha_discipline_surface_complete", record["blockers"])
            finally:
                os.chdir(old)

    def test_stale_refresh_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fx = self._fixture(root)
            manifest_path = root / "output/fx_state_refresh_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["pairs_refreshed"] = 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            old = Path.cwd()
            try:
                os.chdir(root)
                record = build_lab_assurance(
                    source_sha="c" * 40,
                    github_run_id="123",
                    repository="market-predictions/weekly-fx",
                    environment="lab",
                    report=fx["report"],
                    clean_markdown=fx["clean"],
                    delivery_html=fx["html"],
                    pdf=fx["pdf"],
                    equity_curve_png=fx["png"],
                    output=fx["assurance"],
                )
                self.assertEqual(record["decision"], "FAIL")
                self.assertIn("state_refresh_complete", record["blockers"])
            finally:
                os.chdir(old)

    def test_lab_cannot_issue_production_pass(self) -> None:
        result = evaluate_production_promotion_from_lab()
        self.assertFalse(result["production_pass"])
        self.assertEqual(result["decision"], "INDETERMINATE_REQUIRES_TARGET_REPOSITORY_ASSURANCE")


if __name__ == "__main__":
    unittest.main()
