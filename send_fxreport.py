#!/usr/bin/env python3
from __future__ import annotations

"""Guarded Weekly FX lab delivery entrypoint.

Imported callers receive the preserved renderer module. Direct validation keeps
legacy behavior. Direct transport renders the exact assets, independently
reconstructs the lab release candidate, and opens SMTP only after assurance PASS.
"""

import sys

import send_fxreport_legacy as _legacy


if __name__ != "__main__":
    sys.modules[__name__] = _legacy
else:
    import json
    import os
    from datetime import datetime, timezone
    from pathlib import Path

    from tools.fx_release_assurance import build_lab_assurance, validate_lab_assurance

    if "--validate-only" in sys.argv:
        _legacy.main()
    else:
        output_dir = Path("output")
        report = _legacy.latest_report_file(output_dir)
        assets = _legacy.generate_delivery_assets(output_dir, report)

        environment = os.environ.get("FX_DELIVERY_ENVIRONMENT", "").strip()
        repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
        source_sha = os.environ.get("GITHUB_SHA", "").strip()
        run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
        if not environment or not repository or not source_sha:
            raise RuntimeError("FX release assurance requires FX_DELIVERY_ENVIRONMENT, GITHUB_REPOSITORY and GITHUB_SHA.")
        chart = assets.get("chart_path")
        if not chart:
            raise RuntimeError("FX release assurance requires a generated equity-curve PNG.")

        assurance = output_dir / f"{report.stem}_release_assurance.json"
        record = build_lab_assurance(
            source_sha=source_sha,
            github_run_id=run_id,
            repository=repository,
            environment=environment,
            report=report,
            clean_markdown=assets["clean_md_path"],
            delivery_html=assets["html_path"],
            pdf=assets["pdf_path"],
            equity_curve_png=chart,
            output=assurance,
        )
        if record["decision"] != "PASS":
            raise RuntimeError(f"FX lab release assurance failed: {record['blockers']}")
        validate_lab_assurance(assurance, expected_source_sha=source_sha, expected_report=str(report))
        print(f"FX_GOVERNANCE_PASS_PRE_SEND | assurance={assurance}")

        attachments, manifest_path, mail_to = _legacy.send_email_with_attachments(assets)
        receipt = output_dir / f"{report.stem}_transport_receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "status": "LAB_TRANSPORT_SENT_UNVERIFIED",
                    "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "environment": "lab",
                    "report": report.name,
                    "recipient": mail_to,
                    "assurance_path": str(assurance),
                    "delivery_manifest_path": str(manifest_path),
                    "attachments": attachments,
                    "independent_receipt_confirmed": False,
                    "production_promotion_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(
            f"LAB_TRANSPORT_SENT_UNVERIFIED | report={report.name} | recipient={mail_to} | "
            f"manifest={manifest_path.name} | receipt={receipt.name}"
        )
