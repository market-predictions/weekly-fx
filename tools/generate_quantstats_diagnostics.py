#!/usr/bin/env python3
"""Generate lab-only QuantStats diagnostics for the FX valuation history.

This script is intentionally non-destructive:
- it reads existing repo state from output/
- it does not modify the production report flow
- it writes diagnostics artifacts only to a separate lab output folder
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import quantstats as qs


@dataclass
class DiagnosticsSummary:
    generated_at_utc: str
    valuation_rows_raw: int
    valuation_rows_daily: int
    start_date: str
    end_date: str
    latest_nav_usd: float
    total_return_pct: float
    cagr_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    volatility_pct: float
    calmar: float
    best_day_pct: float
    worst_day_pct: float
    last_daily_return_pct: float
    source_report: str | None
    valuation_source: str | None
    overlay_as_of_utc: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate QuantStats diagnostics from FX valuation history")
    parser.add_argument("--output-dir", default="output", help="Path to repo output/ directory")
    parser.add_argument(
        "--artifact-dir",
        default="lab_outputs/quantstats",
        help="Directory to write diagnostics artifacts into",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_daily_nav_series(csv_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing valuation history file: {csv_path}")

    df = pd.read_csv(csv_path)
    required = {"date", "nav_usd", "overlay_as_of_utc"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Valuation history is missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav_usd"] = pd.to_numeric(df["nav_usd"], errors="coerce")
    df["row_order"] = range(len(df))
    df = df.dropna(subset=["date", "nav_usd"]).copy()
    if df.empty:
        raise RuntimeError("Valuation history contains no usable date/nav rows")

    daily = (
        df.sort_values(["date", "row_order"]) 
          .groupby("date", as_index=False)
          .last()
          .sort_values("date")
          .reset_index(drop=True)
    )

    nav = daily.set_index("date")["nav_usd"].astype(float)
    if len(nav) < 2:
        raise RuntimeError("Need at least 2 daily NAV points to compute returns")
    return daily, nav


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        if pd.isna(value):
            return 0.0
    except Exception:
        pass
    return float(value)


def build_summary(
    returns: pd.Series,
    daily_nav: pd.DataFrame,
    portfolio_state: dict[str, Any],
    manifest: dict[str, Any],
) -> DiagnosticsSummary:
    start_date = daily_nav.iloc[0]["date"].strftime("%Y-%m-%d")
    end_date = daily_nav.iloc[-1]["date"].strftime("%Y-%m-%d")

    return DiagnosticsSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        valuation_rows_raw=int(len(returns) + 1 + max(0, len(daily_nav) - (len(returns) + 1))),
        valuation_rows_daily=int(len(daily_nav)),
        start_date=start_date,
        end_date=end_date,
        latest_nav_usd=safe_float(daily_nav.iloc[-1]["nav_usd"]),
        total_return_pct=safe_float((daily_nav.iloc[-1]["nav_usd"] / daily_nav.iloc[0]["nav_usd"] - 1.0) * 100.0),
        cagr_pct=safe_float(qs.stats.cagr(returns) * 100.0),
        sharpe=safe_float(qs.stats.sharpe(returns)),
        sortino=safe_float(qs.stats.sortino(returns)),
        max_drawdown_pct=safe_float(qs.stats.max_drawdown(returns) * 100.0),
        volatility_pct=safe_float(qs.stats.volatility(returns) * 100.0),
        calmar=safe_float(qs.stats.calmar(returns)),
        best_day_pct=safe_float(qs.stats.best(returns) * 100.0),
        worst_day_pct=safe_float(qs.stats.worst(returns) * 100.0),
        last_daily_return_pct=safe_float(returns.iloc[-1] * 100.0),
        source_report=manifest.get("source_report") or portfolio_state.get("last_rebalance", {}).get("source_report"),
        valuation_source=portfolio_state.get("valuation_source") or manifest.get("valuation_source"),
        overlay_as_of_utc=(manifest.get("overlay_as_of_utc") or portfolio_state.get("last_valuation", {}).get("overlay_as_of_utc")),
    )


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    valuation_path = output_dir / "fx_valuation_history.csv"
    portfolio_state_path = output_dir / "fx_portfolio_state.json"
    manifest_path = output_dir / "fx_state_refresh_manifest.json"

    portfolio_state = load_json(portfolio_state_path)
    manifest = load_json(manifest_path)

    raw_df = pd.read_csv(valuation_path)
    daily_nav, nav_series = load_daily_nav_series(valuation_path)
    returns = nav_series.pct_change().dropna()
    returns.name = "fx_model_portfolio_returns"

    if returns.empty:
        raise RuntimeError("Daily return series is empty after pct_change()")

    daily_nav_export = artifact_dir / "fx_daily_nav_series.csv"
    daily_returns_export = artifact_dir / "fx_daily_returns.csv"
    summary_export = artifact_dir / "fx_quantstats_summary.json"
    manifest_export = artifact_dir / "fx_quantstats_manifest.json"
    html_export = artifact_dir / "fx_quantstats_tearsheet.html"

    daily_nav.assign(date=daily_nav["date"].dt.strftime("%Y-%m-%d")).to_csv(daily_nav_export, index=False)
    returns.to_frame(name="return").assign(date=lambda df: df.index.strftime("%Y-%m-%d")).loc[:, ["date", "return"]].to_csv(
        daily_returns_export,
        index=False,
    )

    summary = build_summary(returns, daily_nav, portfolio_state, manifest)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")

    qs.reports.html(
        returns,
        output=str(html_export),
        title="Weekly FX Lab Diagnostics — QuantStats",
    )

    write_manifest(
        manifest_export,
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "input_files": {
                "valuation_history": str(valuation_path),
                "portfolio_state": str(portfolio_state_path),
                "state_refresh_manifest": str(manifest_path),
            },
            "artifacts": {
                "daily_nav_csv": str(daily_nav_export),
                "daily_returns_csv": str(daily_returns_export),
                "summary_json": str(summary_export),
                "quantstats_html": str(html_export),
            },
            "raw_valuation_rows": int(len(raw_df)),
            "daily_valuation_rows": int(len(daily_nav)),
            "returns_rows": int(len(returns)),
            "latest_nav_usd": safe_float(daily_nav.iloc[-1]["nav_usd"]),
            "latest_date": daily_nav.iloc[-1]["date"].strftime("%Y-%m-%d"),
        },
    )

    print(f"QuantStats diagnostics written to: {artifact_dir}")
    print(f"HTML tearsheet: {html_export}")
    print(f"Summary JSON: {summary_export}")


if __name__ == "__main__":
    main()
