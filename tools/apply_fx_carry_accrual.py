#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fx_carry_utils import estimate_daily_carry_accrual_usd, load_json, load_policy_config

STATE_PATH = Path("output/fx_portfolio_state.json")
HISTORY_PATH = Path("output/fx_valuation_history.csv")
MANIFEST_PATH = Path("output/fx_state_refresh_manifest.json")
CONFIG_PATH = Path("config/fx_policy_rate_proxies.json")


def parse_date(value: str) -> datetime:
    return datetime.strptime(value[:10], "%Y-%m-%d")


def load_history(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_history(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def update_latest_history_row(valuation_date: str, overlay_ts: str, updates: dict[str, object]) -> None:
    headers, rows = load_history(HISTORY_PATH)
    if not rows:
        return
    for header in ["carry_accrual_usd", "cumulative_carry_accrual_usd", "carry_accrual_days"]:
        if header not in headers:
            headers.append(header)
    for row in reversed(rows):
        if row.get("overlay_as_of_utc") == overlay_ts or row.get("date") == valuation_date:
            for key, value in updates.items():
                row[key] = str(value)
            break
    write_history(HISTORY_PATH, headers, rows)


def apply_carry_accrual(check_only: bool = False) -> dict[str, object]:
    state = load_json(STATE_PATH)
    config = load_policy_config(CONFIG_PATH)
    valuation = state.get("last_valuation", {})
    valuation_date = str(valuation.get("date") or "")
    overlay_ts = str(valuation.get("overlay_as_of_utc") or "")
    if not valuation_date:
        raise RuntimeError("Portfolio state has no last_valuation.date")

    daily_carry = estimate_daily_carry_accrual_usd(state, config)
    carry_state = state.get("carry_accrual", {}) or {}
    last_accrual_date = str(carry_state.get("last_accrual_date") or valuation_date)
    try:
        days = max((parse_date(valuation_date) - parse_date(last_accrual_date)).days, 0)
    except Exception:
        days = 0
    accrual = round(daily_carry * days, 2)
    cumulative = round(float(carry_state.get("cumulative_carry_accrual_usd") or 0.0) + accrual, 2)

    result = {
        "valuation_date": valuation_date,
        "last_accrual_date_before": last_accrual_date,
        "carry_accrual_days": days,
        "estimated_daily_carry_accrual_usd": daily_carry,
        "carry_accrual_usd": accrual,
        "cumulative_carry_accrual_usd": cumulative,
    }
    if check_only:
        return result

    state["cash_usd"] = round(float(state.get("cash_usd") or 0.0) + accrual, 2)
    state["nav_usd"] = round(float(state.get("nav_usd") or 0.0) + accrual, 2)
    state["peak_nav_usd"] = round(max(float(state.get("peak_nav_usd") or 0.0), float(state["nav_usd"])), 2)
    starting = float(state.get("starting_capital_usd") or 100000.0)
    state["last_valuation"]["nav_usd"] = state["nav_usd"]
    state["last_valuation"]["cash_usd"] = state["cash_usd"]
    state["last_valuation"]["estimated_daily_carry_accrual_usd"] = daily_carry
    state["last_valuation"]["carry_accrual_usd"] = accrual
    state["last_valuation"]["cumulative_carry_accrual_usd"] = cumulative
    state["last_valuation"]["since_inception_return_pct"] = round(((state["nav_usd"] / starting) - 1.0) * 100.0, 4) if starting else 0.0
    state["carry_accrual"] = {
        "method": "policy_rate_proxy",
        "source_config": str(CONFIG_PATH),
        "last_accrual_date": valuation_date,
        "estimated_daily_carry_accrual_usd": daily_carry,
        "last_accrual_usd": accrual,
        "last_accrual_days": days,
        "cumulative_carry_accrual_usd": cumulative,
        "note": "Carry accrual is based on policy-rate proxy estimates. Replace with broker rollover/tom-next/forward-points when available.",
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    update_latest_history_row(
        valuation_date,
        overlay_ts,
        {
            "nav_usd": state["nav_usd"],
            "cash_usd": state["cash_usd"],
            "since_inception_return_pct": state["last_valuation"]["since_inception_return_pct"],
            "carry_accrual_usd": accrual,
            "cumulative_carry_accrual_usd": cumulative,
            "carry_accrual_days": days,
        },
    )

    if MANIFEST_PATH.exists():
        manifest = load_json(MANIFEST_PATH)
        manifest["carry_accrual"] = result
        manifest["nav_usd_after_carry_accrual"] = state["nav_usd"]
        manifest["cash_usd_after_carry_accrual"] = state["cash_usd"]
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply policy-rate proxy FX carry accrual to portfolio state")
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = apply_carry_accrual(check_only=args.check_only)
    status = "FX_CARRY_ACCRUAL_DERIVATION_OK" if args.check_only else "FX_CARRY_ACCRUAL_OK"
    print(
        status
        + " | valuation_date={valuation_date} | days={carry_accrual_days} | daily={estimated_daily_carry_accrual_usd} | accrual={carry_accrual_usd} | cumulative={cumulative_carry_accrual_usd}".format(**result)
    )


if __name__ == "__main__":
    main()
