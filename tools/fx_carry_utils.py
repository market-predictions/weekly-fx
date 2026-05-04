from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path("config/fx_policy_rate_proxies.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_policy_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    return load_json(path)


def pct(value: float, denominator: float) -> float:
    return round((float(value) / float(denominator)) * 100.0, 4) if denominator else 0.0


def carry_rows_from_state(portfolio_state: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    rates = config["rates_pct"]
    base = str(config.get("base_currency", "USD")).upper()
    usd_rate = float(rates[base])
    nav = float(portfolio_state.get("nav_usd") or 0.0)
    run_date = str(portfolio_state.get("last_valuation", {}).get("date") or "")
    source = "manual_policy_rate_proxy"
    rows: list[dict[str, Any]] = []

    cash_usd = float(portfolio_state.get("cash_usd") or 0.0)
    annual_cash = cash_usd * usd_rate / 100.0
    rows.append(
        {
            "run_date": run_date,
            "currency": base,
            "position_type": "cash",
            "policy_rate_proxy_pct": round(usd_rate, 4),
            "usd_policy_rate_proxy_pct": round(usd_rate, 4),
            "estimated_carry_vs_usd_pct": 0.0,
            "current_weight_pct": round(pct(cash_usd, nav), 2),
            "market_value_usd": round(cash_usd, 2),
            "estimated_annual_carry_usd": round(annual_cash, 2),
            "estimated_weekly_carry_usd": round(annual_cash / 52.0, 2),
            "estimated_daily_carry_usd": round(annual_cash / 365.0, 2),
            "spot_unrealized_pnl_usd": 0.0,
            "carry_to_abs_spot_pnl_ratio": "",
            "action_label": "Reduce" if pct(cash_usd, nav) > float(config.get("cash_ceiling_pct_normal_mode", 10.0)) else "Hold",
            "carry_status": "cash_yield_proxy",
            "source": source,
        }
    )

    for pos in portfolio_state.get("positions", []):
        currency = str(pos.get("currency") or "").upper()
        if not currency or currency not in rates:
            continue
        market_value = float(pos.get("market_value_usd") or 0.0)
        spot_pnl = float(pos.get("unrealized_pnl_usd") or 0.0)
        foreign_rate = float(rates[currency])
        carry_diff = foreign_rate - usd_rate
        annual = market_value * carry_diff / 100.0
        ratio: str | float = ""
        if abs(spot_pnl) > 1e-9:
            ratio = round(annual / abs(spot_pnl), 2)
        rows.append(
            {
                "run_date": run_date,
                "currency": currency,
                "position_type": "fx_sleeve",
                "policy_rate_proxy_pct": round(foreign_rate, 4),
                "usd_policy_rate_proxy_pct": round(usd_rate, 4),
                "estimated_carry_vs_usd_pct": round(carry_diff, 4),
                "current_weight_pct": round(float(pos.get("current_weight_pct") or pct(market_value, nav)), 2),
                "market_value_usd": round(market_value, 2),
                "estimated_annual_carry_usd": round(annual, 2),
                "estimated_weekly_carry_usd": round(annual / 52.0, 2),
                "estimated_daily_carry_usd": round(annual / 365.0, 2),
                "spot_unrealized_pnl_usd": round(spot_pnl, 2),
                "carry_to_abs_spot_pnl_ratio": ratio,
                "action_label": pos.get("action_label", ""),
                "carry_status": "positive_carry" if annual > 0 else ("negative_carry" if annual < 0 else "neutral_carry"),
                "source": source,
            }
        )
    return rows


def risk_bucket_snapshot_from_state(portfolio_state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    nav = float(portfolio_state.get("nav_usd") or 0.0)
    cash = float(portfolio_state.get("cash_usd") or 0.0)
    defensive = set(config.get("defensive_bucket", ["CHF", "JPY"]))
    risk_on = set(config.get("risk_on_bucket", ["AUD", "CAD", "MXN", "EUR", "GBP", "NZD", "ZAR"]))
    position_by_currency = {str(p.get("currency") or "").upper(): p for p in portfolio_state.get("positions", [])}

    def exposure_for(currencies: set[str]) -> tuple[float, float]:
        exposure = sum(float(position_by_currency.get(c, {}).get("market_value_usd") or 0.0) for c in currencies)
        return round(exposure, 2), round(pct(exposure, nav), 2)

    defensive_usd, defensive_pct = exposure_for(defensive)
    risk_usd, risk_pct = exposure_for(risk_on)
    cash_pct = round(pct(cash, nav), 2)
    cash_ceiling = float(config.get("cash_ceiling_pct_normal_mode", 10.0))
    soft_cap = float(config.get("risk_on_soft_cap_pct", 55.0))
    hard_cap = float(config.get("risk_on_hard_warning_pct", 60.0))

    warnings = []
    warnings.append(
        {
            "rule": "usd_cash_ceiling",
            "status": "breach" if cash_pct > cash_ceiling else "ok",
            "detail": (
                "USD cash is above the normal-mode ceiling; reports must reduce it, declare capital-preservation mode, or include a dated no-action override."
                if cash_pct > cash_ceiling
                else "USD cash is within the normal-mode ceiling."
            ),
        }
    )
    warnings.append(
        {
            "rule": "risk_on_bucket_soft_cap",
            "status": "breach" if risk_pct > soft_cap else "ok",
            "detail": (
                f"Risk-on/cyclical/carry FX exposure is above the {soft_cap:.0f}% soft cap."
                if risk_pct > soft_cap
                else f"Risk-on/cyclical/carry FX exposure is within the {soft_cap:.0f}% soft cap."
            ),
        }
    )
    warnings.append(
        {
            "rule": "risk_on_bucket_hard_warning",
            "status": "breach" if risk_pct > hard_cap else "ok",
            "detail": (
                f"Risk-on/cyclical/carry FX exposure is above the {hard_cap:.0f}% hard-warning threshold."
                if risk_pct > hard_cap
                else f"Risk-on/cyclical/carry FX exposure is below the {hard_cap:.0f}% hard-warning threshold."
            ),
        }
    )

    return {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "run_date": portfolio_state.get("last_valuation", {}).get("date", ""),
        "nav_usd": round(nav, 2),
        "cash_usd": round(cash, 2),
        "policy": {
            "normal_usd_cash_ceiling_pct": cash_ceiling,
            "risk_on_soft_cap_pct": soft_cap,
            "risk_on_hard_warning_pct": hard_cap,
        },
        "buckets": [
            {"bucket": "usd_liquidity", "currencies": ["USD"], "exposure_pct": cash_pct, "exposure_usd": round(cash, 2)},
            {"bucket": "defensive_fx", "currencies": sorted(defensive), "exposure_pct": defensive_pct, "exposure_usd": defensive_usd},
            {"bucket": "risk_on_cyclical_carry_fx", "currencies": sorted(risk_on), "exposure_pct": risk_pct, "exposure_usd": risk_usd},
        ],
        "warnings": warnings,
        "source": "output/fx_portfolio_state.json + config/fx_policy_rate_proxies.json",
    }


def estimate_daily_carry_accrual_usd(portfolio_state: dict[str, Any], config: dict[str, Any]) -> float:
    rows = carry_rows_from_state(portfolio_state, config)
    return round(sum(float(row.get("estimated_daily_carry_usd") or 0.0) for row in rows), 2)
