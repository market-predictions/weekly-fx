#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

REPORT_RE = re.compile(r"weekly_fx_review_(\d{6})(?:_(\d{2}))?\.md$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FX report alpha-discipline requirements before send")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--report", default=None)
    parser.add_argument("--warn-only-risk-bucket", action="store_true", default=True)
    return parser.parse_args()


def latest_report_file(output_dir: Path) -> Path:
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_fx_review_*.md"):
        match = REPORT_RE.fullmatch(path.name)
        if not match:
            continue
        candidates.append((match.group(1), int(match.group(2) or "0"), path))
    if not candidates:
        raise FileNotFoundError("No weekly_fx_review_*.md report found")
    candidates.sort(key=lambda row: (row[0], row[1]))
    return candidates[-1][2]


def section_body(md_text: str, number: int) -> str:
    lines = md_text.splitlines()
    capture: list[str] = []
    in_section = False
    prefix = f"## {number}."
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if stripped.startswith(prefix):
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            capture.append(line)
    return "\n".join(capture).strip()


def parse_markdown_table(table_text: str) -> list[list[str]]:
    rows = []
    for line in table_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    return rows


def first_table(section: str) -> str:
    lines = []
    capture = False
    for line in section.splitlines():
        if line.strip().startswith("|"):
            capture = True
            lines.append(line)
        elif capture:
            break
    return "\n".join(lines)


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def section13_map(md_text: str) -> dict[str, dict[str, str]]:
    rows = parse_markdown_table(first_table(section_body(md_text, 13)))
    if len(rows) < 2:
        return {}
    headers = [h.strip().lower() for h in rows[0]]
    out = {}
    for cells in rows[1:]:
        item = {headers[i]: cells[i] if i < len(cells) else "" for i in range(len(headers))}
        ccy = item.get("currency", "").upper()
        if ccy:
            out[ccy] = item
    return out


def target_weight(row: dict[str, str]) -> float | None:
    for key in ("target weight (%)", "target weight", "target"):
        if key in row:
            try:
                return float(row[key].replace("%", "").strip())
            except Exception:
                return None
    return None


def validate(md_text: str, output_dir: Path, report_path: Path) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    required_phrases = [
        "FX carry dashboard",
        "USD cash contradiction check",
        "Risk-bucket exposure",
        "No-action override table",
    ]
    for phrase in required_phrases:
        if phrase not in md_text:
            errors.append(f"Missing required alpha-discipline block or label: {phrase}")

    carry_rows = csv_rows(output_dir / "fx_carry_snapshot.csv")
    if not carry_rows:
        errors.append("output/fx_carry_snapshot.csv has no rows")

    risk = load_json(output_dir / "fx_risk_bucket_snapshot.json")
    risk_bucket = next((b for b in risk.get("buckets", []) if b.get("bucket") == "risk_on_cyclical_carry_fx"), None)
    if risk_bucket:
        exposure = float(risk_bucket.get("exposure_pct", 0.0))
        if exposure > 60.0:
            warnings.append(f"WARN: risk-on/cyclical/carry FX bucket is above 60% hard-warning threshold: {exposure:.2f}%")
        elif exposure > 55.0:
            warnings.append(f"WARN: risk-on/cyclical/carry FX bucket is above 55% soft cap: {exposure:.2f}%")

    state = load_json(output_dir / "fx_portfolio_state.json")
    cash_pct = 0.0
    if state.get("nav_usd"):
        cash_pct = float(state.get("cash_usd", 0.0)) / float(state.get("nav_usd")) * 100.0

    sec13 = section13_map(md_text)
    usd_row = sec13.get("USD")
    usd_action = ""
    usd_target = None
    if usd_row:
        usd_action = usd_row.get("action", "") or usd_row.get("suggested action", "")
        usd_target = target_weight(usd_row)
    if "reduce" in usd_action.lower() and cash_pct > 10.0:
        contradiction_section = section_body(md_text, 14) + "\n" + section_body(md_text, 16)
        has_override = "USD cash contradiction check" in contradiction_section and "override" in contradiction_section.lower()
        has_target_reduction = usd_target is not None and usd_target < cash_pct
        if not has_override and not has_target_reduction:
            errors.append(
                "USD is labelled Reduce while USD cash is above 10%, but no target reduction or dated no-action override was found."
            )

    section14 = section_body(md_text, 14)
    if "No additional" in section14 and "No-action override table" not in section14:
        errors.append("Section 14 says no rebalance occurred but lacks the required No-action override table.")

    if warnings:
        for warning in warnings:
            print(warning)
    return errors


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    report_path = Path(args.report) if args.report else latest_report_file(output_dir)
    md_text = report_path.read_text(encoding="utf-8")
    errors = validate(md_text, output_dir, report_path)
    if errors:
        for error in errors:
            print(f"FX_ACTION_DISCIPLINE_ERROR | {error}")
        raise SystemExit(1)
    print(f"FX_ACTION_DISCIPLINE_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
