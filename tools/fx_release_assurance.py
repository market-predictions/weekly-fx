#!/usr/bin/env python3
"""Fail-closed release assurance for the Weekly FX lab delivery path."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROLE = "implementation_operations"
ASSURANCE_ROLE = "governance_release_assurance"
SHA_RE = re.compile(r"[0-9a-f]{40}")
SECTION_RE = re.compile(r"^##\s+(\d+)\.", re.MULTILINE)
REQUIRED_CHECKS = {
    "source_identity_bound",
    "lab_boundary_enforced",
    "required_files_present",
    "control_json_parseable",
    "state_refresh_complete",
    "portfolio_refresh_consistent",
    "report_structure_complete",
    "alpha_discipline_surface_complete",
    "artifact_formats_valid",
    "artifact_hashes_complete",
    "roles_separated",
    "promotion_boundary_enforced",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[dict[str, Any]], blockers: list[str], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
    if not passed:
        blockers.append(check_id)


def valid_format(key: str, path: Path) -> str | None:
    size = path.stat().st_size
    if key == "report" or key == "clean_markdown":
        if size < 512 or "#" not in path.read_text(encoding="utf-8", errors="replace"):
            return f"{key}: invalid markdown"
    elif key == "delivery_html":
        raw = path.read_text(encoding="utf-8", errors="replace").lower()
        if size < 1024 or ("<html" not in raw and "<!doctype" not in raw):
            return "delivery_html: invalid HTML"
    elif key == "pdf":
        if size < 1024 or path.read_bytes()[:5] != b"%PDF-":
            return "pdf: invalid PDF"
    elif key == "equity_curve_png":
        if size < 128 or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            return "equity_curve_png: invalid PNG"
    elif path.suffix.lower() == ".csv" and size < 8:
        return f"{key}: empty CSV"
    return None


def report_token(report: Path) -> str:
    match = re.fullmatch(r"weekly_fx_review_(\d{6})(?:_\d{2})?\.md", report.name)
    if not match:
        raise ValueError(f"Unexpected FX report name: {report.name}")
    return match.group(1)


def build_lab_assurance(
    *,
    source_sha: str,
    github_run_id: str,
    repository: str,
    environment: str,
    report: Path,
    clean_markdown: Path,
    delivery_html: Path,
    pdf: Path,
    equity_curve_png: Path,
    output: Path,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    token = report_token(report)

    identity_ok = bool(SHA_RE.fullmatch(source_sha.lower())) and repository == "market-predictions/weekly-fx" and bool(token)
    add_check(checks, blockers, "source_identity_bound", identity_ok, {"source_sha": source_sha, "github_run_id": github_run_id, "repository": repository, "report_token": token, "report": str(report)})

    lab_ok = environment == "lab" and repository == "market-predictions/weekly-fx"
    add_check(checks, blockers, "lab_boundary_enforced", lab_ok, {"environment": environment, "repository": repository, "client_facing_production_authority": False, "production_promotion_authority": False})

    state_manifest = Path("output/fx_state_refresh_manifest.json")
    portfolio = Path("output/fx_portfolio_state.json")
    ledger = Path("output/fx_trade_ledger.csv")
    valuation = Path("output/fx_valuation_history.csv")
    scorecard = Path("output/fx_recommendation_scorecard.csv")
    overlay = Path("output/fx_technical_overlay.json")
    carry = Path("output/fx_carry_snapshot.csv")
    risk = Path("output/fx_risk_bucket_snapshot.json")
    paths = {
        "state_refresh_manifest": state_manifest,
        "portfolio_state": portfolio,
        "trade_ledger": ledger,
        "valuation_history": valuation,
        "recommendation_scorecard": scorecard,
        "technical_overlay": overlay,
        "carry_snapshot": carry,
        "risk_bucket_snapshot": risk,
        "report": report,
        "clean_markdown": clean_markdown,
        "delivery_html": delivery_html,
        "pdf": pdf,
        "equity_curve_png": equity_curve_png,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    add_check(checks, blockers, "required_files_present", not missing, {"missing": missing})

    parsed: dict[str, Any] = {}
    json_errors: dict[str, str] = {}
    for key in ("state_refresh_manifest", "portfolio_state", "technical_overlay", "risk_bucket_snapshot"):
        path = paths[key]
        if path.is_file():
            try:
                parsed[key] = load_json(path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                json_errors[key] = str(exc)
    add_check(checks, blockers, "control_json_parseable", not json_errors, json_errors)

    manifest = parsed.get("state_refresh_manifest", {})
    pair_rows = manifest.get("pair_rows", []) if isinstance(manifest, dict) else []
    requested = manifest.get("pairs_requested") if isinstance(manifest, dict) else None
    refreshed = manifest.get("pairs_refreshed") if isinstance(manifest, dict) else None
    fresh_rows = len([row for row in pair_rows if isinstance(row, dict) and row.get("status") == "fresh"])
    refresh_ok = bool(pair_rows) and requested == refreshed == fresh_rows and manifest.get("valuation_date") == manifest.get("most_common_pair_date")
    add_check(checks, blockers, "state_refresh_complete", refresh_ok, {"pairs_requested": requested, "pairs_refreshed": refreshed, "fresh_rows": fresh_rows, "valuation_date": manifest.get("valuation_date") if isinstance(manifest, dict) else None, "most_common_pair_date": manifest.get("most_common_pair_date") if isinstance(manifest, dict) else None})

    state = parsed.get("portfolio_state", {})
    state_valuation = state.get("last_valuation", {}) if isinstance(state, dict) else {}
    state_ok = (
        isinstance(manifest, dict)
        and isinstance(state, dict)
        and state_valuation.get("date") == manifest.get("valuation_date")
        and abs(float(state.get("nav_usd", -1)) - float(manifest.get("nav_usd_after_carry_accrual", manifest.get("nav_usd", -2)))) < 0.02
        and abs(float(state.get("cash_usd", -1)) - float(manifest.get("cash_usd_after_carry_accrual", manifest.get("cash_usd", -2)))) < 0.02
    )
    add_check(checks, blockers, "portfolio_refresh_consistent", state_ok, {"state_date": state_valuation.get("date") if isinstance(state_valuation, dict) else None, "manifest_date": manifest.get("valuation_date") if isinstance(manifest, dict) else None, "state_nav": state.get("nav_usd") if isinstance(state, dict) else None, "manifest_nav": manifest.get("nav_usd_after_carry_accrual", manifest.get("nav_usd")) if isinstance(manifest, dict) else None})

    text = clean_markdown.read_text(encoding="utf-8", errors="replace") if clean_markdown.is_file() else ""
    sections = sorted(set(SECTION_RE.findall(text)))
    structure_ok = all(str(number) in sections for number in range(1, 18))
    add_check(checks, blockers, "report_structure_complete", structure_ok, {"sections": sections})

    lower = text.lower()
    required_surfaces = {
        "fx_carry_dashboard": "fx carry dashboard" in lower,
        "usd_cash_contradiction_check": "usd cash contradiction check" in lower,
        "risk_bucket_exposure": "risk-bucket exposure" in lower or "risk bucket exposure" in lower,
    }
    section14 = ""
    match14 = re.search(r"^##\s+14\..*?(?=^##\s+15\.|\Z)", text, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if match14:
        section14 = match14.group(0).lower()
    no_execution = any(phrase in section14 for phrase in ("no trades", "no changes", "none", "geen transacties"))
    no_action_proof = "no-action override" in lower or "no action override" in lower
    alpha_ok = all(required_surfaces.values()) and (not no_execution or no_action_proof)
    add_check(checks, blockers, "alpha_discipline_surface_complete", alpha_ok, {**required_surfaces, "no_execution_detected": no_execution, "no_action_proof": no_action_proof})

    format_errors: list[str] = []
    for key, path in paths.items():
        if path.is_file():
            error = valid_format(key, path)
            if error:
                format_errors.append(error)
    add_check(checks, blockers, "artifact_formats_valid", not format_errors, format_errors)

    hashes: dict[str, dict[str, str]] = {}
    if not missing:
        hashes = {key: {"path": str(path), "sha256": sha256_file(path)} for key, path in paths.items()}
    hashes_ok = len(hashes) == len(paths) and all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in hashes.values())
    add_check(checks, blockers, "artifact_hashes_complete", hashes_ok, hashes)

    add_check(checks, blockers, "roles_separated", IMPLEMENTATION_ROLE != ASSURANCE_ROLE, {"implementation_role": IMPLEMENTATION_ROLE, "assurance_role": ASSURANCE_ROLE, "implementation_may_self_certify": False, "assurance_may_mutate_candidate": False})
    promotion_ok = environment == "lab" and repository == "market-predictions/weekly-fx"
    add_check(checks, blockers, "promotion_boundary_enforced", promotion_ok, {"weekly_fx_may_self_promote": False, "production_target": "market-predictions/daily-fx", "production_decision": "INDETERMINATE_REQUIRES_TARGET_REPOSITORY_ASSURANCE"})

    decision = "PASS" if not blockers else "FAIL"
    record = {
        "schema_version": "1.0.0",
        "contract_id": "FX_RELEASE_ASSURANCE_CONTRACT_V1",
        "product": "weekly_fx_lab",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "environment": environment,
        "implementation_role": IMPLEMENTATION_ROLE,
        "assurance_role": ASSURANCE_ROLE,
        "identity": {"source_sha": source_sha.lower(), "github_run_id": github_run_id, "repository": repository, "report_token": token, "report_path": str(report), "valuation_date": manifest.get("valuation_date") if isinstance(manifest, dict) else None},
        "authority": {"client_facing_production_authority": False, "production_promotion_authority": False, "weekly_fx_may_self_promote": False},
        "checks": checks,
        "artifact_hashes": hashes,
        "blockers": blockers,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def validate_lab_assurance(path: Path, *, expected_source_sha: str | None = None, expected_report: str | None = None) -> dict[str, Any]:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("decision") != "PASS":
        errors.append(f"decision must be PASS, got {payload.get('decision')!r}")
    if payload.get("environment") != "lab":
        errors.append("environment must be lab")
    if payload.get("authority", {}).get("production_promotion_authority") is not False:
        errors.append("production promotion authority must be false")
    if payload.get("blockers"):
        errors.append(f"blockers present: {payload.get('blockers')}")
    checks = {item.get("id"): item for item in payload.get("checks", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_CHECKS - set(checks))
    failed = sorted(key for key, item in checks.items() if item.get("passed") is not True)
    if missing:
        errors.append(f"required checks missing: {missing}")
    if failed:
        errors.append(f"failed checks present: {failed}")
    identity = payload.get("identity", {})
    if expected_source_sha and identity.get("source_sha") != expected_source_sha.lower():
        errors.append("source SHA mismatch")
    if expected_report and identity.get("report_path") != expected_report:
        errors.append("report path mismatch")
    hashes = payload.get("artifact_hashes", {})
    if not hashes or any(not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) for item in hashes.values() if isinstance(item, dict)):
        errors.append("artifact hashes incomplete")
    if errors:
        raise RuntimeError("FX lab release assurance rejected: " + "; ".join(errors))
    return payload


def evaluate_production_promotion_from_lab() -> dict[str, Any]:
    return {
        "contract_id": "FX_PRODUCTION_PROMOTION_ASSURANCE_CONTRACT_V1",
        "source_repository": "market-predictions/weekly-fx",
        "target_repository": "market-predictions/daily-fx",
        "decision": "INDETERMINATE_REQUIRES_TARGET_REPOSITORY_ASSURANCE",
        "production_pass": False,
        "reason": "A lab repository cannot issue production promotion PASS.",
    }
