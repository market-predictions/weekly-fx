#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.fx_carry_utils import carry_rows_from_state, load_json, load_policy_config, risk_bucket_snapshot_from_state

DEFAULT_STATE_PATH = Path("output/fx_portfolio_state.json")
DEFAULT_CARRY_PATH = Path("output/fx_carry_snapshot.csv")
DEFAULT_RISK_PATH = Path("output/fx_risk_bucket_snapshot.json")
DEFAULT_CONFIG_PATH = Path("config/fx_policy_rate_proxies.json")

CARRY_HEADERS = [
    "run_date",
    "currency",
    "position_type",
    "policy_rate_proxy_pct",
    "usd_policy_rate_proxy_pct",
    "estimated_carry_vs_usd_pct",
    "current_weight_pct",
    "market_value_usd",
    "estimated_annual_carry_usd",
    "estimated_weekly_carry_usd",
    "estimated_daily_carry_usd",
    "spot_unrealized_pnl_usd",
    "carry_to_abs_spot_pnl_ratio",
    "action_label",
    "carry_status",
    "source",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write FX carry and true risk-bucket snapshots from current portfolio state")
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--carry-output", default=str(DEFAULT_CARRY_PATH))
    parser.add_argument("--risk-output", default=str(DEFAULT_RISK_PATH))
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def write_carry_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CARRY_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in CARRY_HEADERS})


def main() -> None:
    args = parse_args()
    state = load_json(Path(args.state))
    config = load_policy_config(Path(args.config))
    carry_rows = carry_rows_from_state(state, config)
    risk_snapshot = risk_bucket_snapshot_from_state(state, config)

    if args.check_only:
        if not carry_rows:
            raise RuntimeError("FX carry snapshot would be empty")
        if not risk_snapshot.get("buckets"):
            raise RuntimeError("FX risk bucket snapshot would be empty")
        print(
            "FX_CARRY_RISK_SNAPSHOT_DERIVATION_OK | "
            f"carry_rows={len(carry_rows)} | "
            f"risk_buckets={len(risk_snapshot.get('buckets', []))}"
        )
        return

    write_carry_csv(Path(args.carry_output), carry_rows)
    Path(args.risk_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.risk_output).write_text(json.dumps(risk_snapshot, indent=2) + "\n", encoding="utf-8")
    print(
        "FX_CARRY_RISK_SNAPSHOT_OK | "
        f"carry={args.carry_output} | "
        f"risk={args.risk_output} | "
        f"carry_rows={len(carry_rows)}"
    )


if __name__ == "__main__":
    main()
