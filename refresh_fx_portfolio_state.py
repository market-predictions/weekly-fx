#!/usr/bin/env python3
"""Refresh Weekly FX model portfolio state from Twelve Data before rendering.

This script is intentionally focused on the portfolio valuation contract:
- load output/fx_portfolio_state.json
- fetch latest available Twelve Data daily close for each implemented FX pair
- revalue existing currency sleeves without rebalancing
- append output/fx_valuation_history.csv
- write output/fx_state_refresh_manifest.json

It does not send email and it does not rewrite the strategic report text. The delivery
workflow consumes the refreshed state during render/send.
"""

from __future__ import annotations

import csv
import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output")
STATE_PATH = OUTPUT_DIR / "fx_portfolio_state.json"
HISTORY_PATH = OUTPUT_DIR / "fx_valuation_history.csv"
MANIFEST_PATH = OUTPUT_DIR / "fx_state_refresh_manifest.json"
TWELVE_DATA_URL = "https://api.twelvedata.com/time_series"
DEFAULT_SLEEP_SECONDS = 8.0


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require_api_key() -> str:
    for name in ("TWELVE_DATA_API_KEY", "TWELVEDATA_API_KEY", "TWELVE_DATA_KEY"):
        value = os.environ.get(name)
        if value:
            return value
    raise RuntimeError(
        "Missing Twelve Data API key. Set TWELVE_DATA_API_KEY, TWELVEDATA_API_KEY, or TWELVE_DATA_KEY in repository secrets."
    )


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required state file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_latest_daily_bar(symbol: str, api_key: str) -> dict[str, Any]:
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": "5",
        "apikey": api_key,
        "format": "JSON",
    }
    url = TWELVE_DATA_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") == "error" or "values" not in payload:
        raise RuntimeError(f"Twelve Data error for {symbol}: {payload}")

    values = payload.get("values") or []
    if not values:
        raise RuntimeError(f"Twelve Data returned no bars for {symbol}")

    latest = values[0]
    close = float(latest["close"])
    return {
        "symbol": symbol,
        "datetime": latest["datetime"],
        "close": close,
        "source": "Twelve Data API",
    }


def ccyusd_price_from_raw_pair(raw_pair: str, close: float, currency: str) -> float:
    pair = raw_pair.replace("/", "").upper()
    if pair == f"{currency}USD":
        return close
    if pair == f"USD{currency}":
        if close == 0:
            raise RuntimeError(f"Cannot invert zero close for {raw_pair}")
        return 1.0 / close
    raise RuntimeError(f"Unsupported pair mapping for currency={currency}, raw_pair={raw_pair}")


def read_last_nav(history_path: Path, fallback_nav: float) -> float:
    if not history_path.exists():
        return fallback_nav
    last_nav = fallback_nav
    with history_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                last_nav = float(row["nav_usd"])
            except Exception:
                continue
    return last_nav


def append_history_row(path: Path, row: dict[str, Any]) -> None:
    headers = [
        "date",
        "nav_usd",
        "cash_usd",
        "gross_exposure_usd",
        "net_exposure_usd",
        "realized_pnl_usd",
        "unrealized_pnl_usd",
        "daily_return_pct",
        "since_inception_return_pct",
        "drawdown_pct",
        "overlay_as_of_utc",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in headers})


def refresh_state() -> dict[str, Any]:
    api_key = require_api_key()
    sleep_seconds = float(os.environ.get("FX_REFRESH_SLEEP_SECONDS", str(DEFAULT_SLEEP_SECONDS)))
    state = load_json(STATE_PATH)

    positions = state.get("positions") or []
    if not positions:
        raise RuntimeError("Portfolio state has no positions to refresh")

    pair_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for idx, position in enumerate(positions):
        currency = str(position.get("currency") or "").upper()
        raw_pair = str(position.get("raw_pair") or "").upper()
        if not currency or not raw_pair:
            errors.append(f"Position missing currency/raw_pair: {position}")
            continue

        try:
            quote = fetch_latest_daily_bar(raw_pair, api_key)
            ccyusd = ccyusd_price_from_raw_pair(raw_pair, float(quote["close"]), currency)
            units = float(position.get("units_ccy") or 0.0)
            avg_entry = float(position.get("avg_entry_price_ccyusd") or 0.0)
            market_value = units * ccyusd
            unrealized = units * (ccyusd - avg_entry)

            position["current_price_ccyusd"] = round(ccyusd, 8)
            position["market_value_usd"] = round(market_value, 2)
            position["unrealized_pnl_usd"] = round(unrealized, 2)

            pair_rows.append(
                {
                    "currency": currency,
                    "raw_pair": raw_pair,
                    "twelve_data_symbol": quote["symbol"],
                    "selected_date": quote["datetime"],
                    "raw_close": round(float(quote["close"]), 8),
                    "ccyusd_price": round(ccyusd, 8),
                    "market_value_usd": round(market_value, 2),
                    "unrealized_pnl_usd": round(unrealized, 2),
                    "status": "fresh",
                }
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{raw_pair}: {exc}")

        if idx < len(positions) - 1 and sleep_seconds > 0:
            time.sleep(sleep_seconds)

    if errors:
        raise RuntimeError("FX refresh failed for one or more pairs: " + " | ".join(errors))

    cash = float(state.get("cash_usd") or 0.0)
    realized = float(state.get("realized_pnl_usd") or 0.0)
    gross_exposure = round(sum(float(pos.get("market_value_usd") or 0.0) for pos in positions), 2)
    nav = round(cash + gross_exposure, 2)
    unrealized_total = round(sum(float(pos.get("unrealized_pnl_usd") or 0.0) for pos in positions), 2)

    for position in positions:
        position["current_weight_pct"] = round((float(position.get("market_value_usd") or 0.0) / nav) * 100.0, 2) if nav else 0.0

    starting_capital = float(state.get("starting_capital_usd") or 100000.0)
    previous_nav = read_last_nav(HISTORY_PATH, float(state.get("nav_usd") or starting_capital))
    daily_return = round(((nav / previous_nav) - 1.0) * 100.0, 4) if previous_nav else 0.0
    since_inception = round(((nav / starting_capital) - 1.0) * 100.0, 4) if starting_capital else 0.0
    previous_peak = float(state.get("peak_nav_usd") or starting_capital)
    peak_nav = round(max(previous_peak, nav), 2)
    drawdown = round(((nav / peak_nav) - 1.0) * 100.0, 4) if peak_nav else 0.0
    max_drawdown = round(min(float(state.get("max_drawdown_pct") or 0.0), drawdown), 4)

    selected_dates = [row["selected_date"] for row in pair_rows]
    common_date = Counter(selected_dates).most_common(1)[0][0] if selected_dates else ""
    conservative_date = min(selected_dates) if selected_dates else common_date
    timestamp = utc_now()

    state["valuation_source"] = "Twelve Data latest available daily bars"
    state["nav_usd"] = nav
    state["peak_nav_usd"] = peak_nav
    state["max_drawdown_pct"] = max_drawdown
    state["positions"] = positions
    state["last_valuation"] = {
        "date": conservative_date,
        "nav_usd": nav,
        "gross_exposure_usd": gross_exposure,
        "net_exposure_usd": gross_exposure,
        "unrealized_pnl_usd": unrealized_total,
        "since_inception_return_pct": since_inception,
        "daily_return_pct": daily_return,
        "overlay_as_of_utc": timestamp,
    }

    write_json(STATE_PATH, state)
    history_row = {
        "date": conservative_date,
        "nav_usd": nav,
        "cash_usd": round(cash, 2),
        "gross_exposure_usd": gross_exposure,
        "net_exposure_usd": gross_exposure,
        "realized_pnl_usd": round(realized, 2),
        "unrealized_pnl_usd": unrealized_total,
        "daily_return_pct": daily_return,
        "since_inception_return_pct": since_inception,
        "drawdown_pct": drawdown,
        "overlay_as_of_utc": timestamp,
    }
    append_history_row(HISTORY_PATH, history_row)

    manifest = {
        "as_of_utc": timestamp,
        "source": "Twelve Data API",
        "mode": "prep_first_portfolio_state_refresh",
        "valuation_date": conservative_date,
        "most_common_pair_date": common_date,
        "pairs_requested": len(positions),
        "pairs_refreshed": len(pair_rows),
        "nav_usd": nav,
        "cash_usd": round(cash, 2),
        "gross_exposure_usd": gross_exposure,
        "unrealized_pnl_usd": unrealized_total,
        "daily_return_pct": daily_return,
        "since_inception_return_pct": since_inception,
        "pair_rows": pair_rows,
        "state_file": str(STATE_PATH),
        "valuation_history_file": str(HISTORY_PATH),
    }
    write_json(MANIFEST_PATH, manifest)
    return manifest


def main() -> None:
    manifest = refresh_state()
    print(
        "FX_STATE_REFRESH_OK | "
        f"valuation_date={manifest['valuation_date']} | "
        f"pairs={manifest['pairs_refreshed']}/{manifest['pairs_requested']} | "
        f"nav_usd={manifest['nav_usd']:.2f} | "
        f"daily_return_pct={manifest['daily_return_pct']:.4f}"
    )


if __name__ == "__main__":
    main()
