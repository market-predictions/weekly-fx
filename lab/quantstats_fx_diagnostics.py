#!/usr/bin/env python3
"""Build non-destructive QuantStats diagnostics for the FX lab repository.

This script reads the authoritative FX valuation history, normalizes it to one row per
calendar date, computes a compact deterministic summary, and generates a QuantStats
HTML tear sheet for lab use.

It is intentionally separate from the production report and delivery flow.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
import quantstats as qs


DEFAULT_INPUT = Path("output/fx_valuation_history.csv")
DEFAULT_OUTPUT_DIR = Path("lab_outputs/fx_quantstats")


def _safe_float(value: Any) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def load_history(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Valuation history not found: {csv_path}")

    df = pd.read_csv(csv_path)
    required = {"date", "nav_usd"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Valuation history missing required columns: {sorted(missing)}")

    if "overlay_as_of_utc" in df.columns:
        df["overlay_as_of_utc"] = pd.to_datetime(df["overlay_as_of_utc"], errors="coerce", utc=True)
    else:
        df["overlay_as_of_utc"] = pd.NaT

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df = df.sort_values(["date", "overlay_as_of_utc", "nav_usd"], kind="stable")

    # Keep the latest marked-to-market entry per calendar date.
    df = df.groupby(df["date"].dt.date, as_index=False).tail(1).copy()
    df = df.sort_values("date", kind="stable").reset_index(drop=True)

    if "daily_return_pct" in df.columns:
        df["daily_return_decimal"] = pd.to_numeric(df["daily_return_pct"], errors="coerce") / 100.0
    else:
        df["daily_return_decimal"] = pd.NA

    nav_returns = pd.to_numeric(df["nav_usd"], errors="coerce").pct_change()
    df["daily_return_decimal"] = df["daily_return_decimal"].fillna(nav_returns)
    df.loc[df.index[0], "daily_return_decimal"] = df.loc[df.index[0], "daily_return_decimal"] if pd.notna(df.loc[df.index[0], "daily_return_decimal"]) else 0.0
    df["daily_return_decimal"] = df["daily_return_decimal"].fillna(0.0)

    return df


def compute_summary(df: pd.DataFrame) -> dict[str, Any]:
    returns = pd.Series(df["daily_return_decimal"].astype(float).values, index=pd.DatetimeIndex(df["date"]), name="fx_lab_returns")
    nav = pd.Series(pd.to_numeric(df["nav_usd"], errors="coerce").astype(float).values, index=pd.DatetimeIndex(df["date"]), name="nav_usd")

    total_return = float(nav.iloc[-1] / nav.iloc[0] - 1.0) if len(nav) > 1 and nav.iloc[0] != 0 else 0.0
    periods = max(len(returns), 1)
    annualized_return = float((1.0 + total_return) ** (252.0 / periods) - 1.0) if periods > 1 and nav.iloc[0] > 0 else total_return
    annualized_vol = float(returns.std(ddof=0) * math.sqrt(252.0)) if periods > 1 else 0.0
    sharpe = float((returns.mean() / returns.std(ddof=0)) * math.sqrt(252.0)) if periods > 1 and returns.std(ddof=0) not in (0.0, float("nan")) else 0.0

    running_max = nav.cummax()
    drawdown = nav / running_max - 1.0
    max_drawdown = float(drawdown.min()) if len(drawdown) else 0.0
    win_rate = float((returns > 0).mean()) if len(returns) else 0.0

    latest = df.iloc[-1]
    summary = {
        "valuation_date": latest["date"].strftime("%Y-%m-%d"),
        "overlay_as_of_utc": latest["overlay_as_of_utc"].isoformat() if pd.notna(latest["overlay_as_of_utc"]) else None,
        "nav_usd": _safe_float(latest.get("nav_usd")),
        "cash_usd": _safe_float(latest.get("cash_usd")),
        "gross_exposure_usd": _safe_float(latest.get("gross_exposure_usd")),
        "unrealized_pnl_usd": _safe_float(latest.get("unrealized_pnl_usd")),
        "daily_return_pct": _safe_float(latest.get("daily_return_pct")),
        "since_inception_return_pct": _safe_float(latest.get("since_inception_return_pct")),
        "observations": int(len(df)),
        "total_return_pct": round(total_return * 100.0, 4),
        "annualized_return_pct": round(annualized_return * 100.0, 4),
        "annualized_vol_pct": round(annualized_vol * 100.0, 4),
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown_pct": round(max_drawdown * 100.0, 4),
        "win_rate_pct": round(win_rate * 100.0, 2),
    }
    return summary


def write_markdown(df: pd.DataFrame, summary: dict[str, Any], output_path: Path) -> None:
    recent = df.tail(10).copy()
    recent["date"] = recent["date"].dt.strftime("%Y-%m-%d")

    lines: list[str] = []
    lines.append("# FX Lab QuantStats Diagnostics")
    lines.append("")
    lines.append("This artifact is lab-only and does not change production report logic, state authority, or delivery behavior.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Valuation date: **{summary['valuation_date']}**")
    lines.append(f"- Overlay timestamp: **{summary['overlay_as_of_utc'] or 'n/a'}**")
    lines.append(f"- NAV (USD): **{summary['nav_usd']:.2f}**" if summary["nav_usd"] is not None else "- NAV (USD): n/a")
    lines.append(f"- Daily return (%): **{summary['daily_return_pct']:.4f}**" if summary["daily_return_pct"] is not None else "- Daily return (%): n/a")
    lines.append(f"- Since inception return (%): **{summary['since_inception_return_pct']:.4f}**" if summary["since_inception_return_pct"] is not None else "- Since inception return (%): n/a")
    lines.append(f"- Annualized return (%): **{summary['annualized_return_pct']:.4f}**")
    lines.append(f"- Annualized volatility (%): **{summary['annualized_vol_pct']:.4f}**")
    lines.append(f"- Sharpe ratio: **{summary['sharpe_ratio']:.4f}**")
    lines.append(f"- Max drawdown (%): **{summary['max_drawdown_pct']:.4f}**")
    lines.append(f"- Win rate (%): **{summary['win_rate_pct']:.2f}**")
    lines.append(f"- Observations after one-row-per-date normalization: **{summary['observations']}**")
    lines.append("")
    lines.append("## Recent valuation history")
    lines.append("")
    lines.append("| Date | NAV (USD) | Daily return (%) | Since inception return (%) | Drawdown (%) |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in recent.iterrows():
        nav = _safe_float(row.get("nav_usd")) or 0.0
        daily = _safe_float(row.get("daily_return_pct"))
        since = _safe_float(row.get("since_inception_return_pct"))
        dd = _safe_float(row.get("drawdown_pct"))
        lines.append(
            f"| {row['date']} | {nav:.2f} | {daily:.4f if daily is not None else 'n/a'} | {since:.4f if since is not None else 'n/a'} | {dd:.4f if dd is not None else 'n/a'} |".replace("ValueError", "n/a")
        )

    # Repair any 'None' text from f-string formatting.
    lines = [line.replace("None", "n/a") for line in lines]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_tearsheet(df: pd.DataFrame, html_path: Path) -> None:
    returns = pd.Series(df["daily_return_decimal"].astype(float).values, index=pd.DatetimeIndex(df["date"]), name="fx_lab_returns")
    qs.extend_pandas()
    qs.reports.html(
        returns,
        output=str(html_path),
        title="FX Lab QuantStats Tear Sheet",
        compounded=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build QuantStats diagnostics for weekly-fx lab use.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to fx_valuation_history.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for diagnostics outputs")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_history(args.input)
    summary = compute_summary(df)

    json_path = output_dir / "fx_quantstats_summary.json"
    md_path = output_dir / "fx_quantstats_summary.md"
    html_path = output_dir / "fx_quantstats_tearsheet.html"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(df, summary, md_path)
    build_tearsheet(df, html_path)

    print(f"Wrote summary JSON to {json_path}")
    print(f"Wrote summary Markdown to {md_path}")
    print(f"Wrote QuantStats HTML tear sheet to {html_path}")


if __name__ == "__main__":
    main()
