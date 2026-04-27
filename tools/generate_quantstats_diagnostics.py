#!/usr/bin/env python3
"""Generate lab-only QuantStats diagnostics for the FX valuation history.

This script is intentionally non-destructive:
- it reads existing repo state from output/
- it does not modify the production report flow
- it writes diagnostics artifacts only to a separate lab output folder

Headline metrics in the summary are intentionally aligned to the authoritative
portfolio engine when that engine state exists. QuantStats remains a supporting
analytics layer, not the source of truth for implementation facts.
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
    returns_rows: int
    inception_date: str
    first_valuation_date: str
    end_date: str
    starting_capital_usd: float
    latest_nav_usd: float
    engine_total_return_pct: float
    engine_since_inception_return_pct: float
    engine_max_drawdown_pct: float
    engine_daily_return_pct: float
    engine_unrealized_pnl_usd: float
    cagr_pct: float
    sharpe: float
    sortino: float
    quantstats_max_drawdown_pct: float
    raw_path_max_drawdown_pct: float
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


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return default


def load_valuation_history(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing valuation history file: {csv_path}")

    df = pd.read_csv(csv_path)
    required = {"date", "nav_usd", "overlay_as_of_utc"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Valuation history is missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav_usd"] = pd.to_numeric(df["nav_usd"], errors="coerce")
    df["overlay_as_of_utc"] = pd.to_datetime(df["overlay_as_of_utc"], errors="coerce", utc=True)
    df["row_order"] = range(len(df))
    df = df.dropna(subset=["date", "nav_usd"]).copy()
    if df.empty:
        raise RuntimeError("Valuation history contains no usable date/nav rows")
    return df


def build_daily_nav(raw_df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        raw_df.sort_values(["date", "row_order"])
        .groupby("date", as_index=False)
        .last()
        .sort_values("date")
        .reset_index(drop=True)
    )
    if len(daily) < 2:
        raise RuntimeError("Need at least 2 daily NAV points to compute returns")
    return daily


def max_drawdown_from_nav(nav_series: pd.Series) -> float:
    series = pd.to_numeric(nav_series, errors="coerce").dropna().astype(float)
    if series.empty:
        return 0.0
    running_peak = series.cummax()
    drawdowns = (series / running_peak) - 1.0
    return safe_float(drawdowns.min() * 100.0)


def compute_cagr_pct(start_value: float, end_value: float, inception_date: str, end_date: str) -> float:
    if start_value <= 0 or end_value <= 0:
        return 0.0

    start_dt = pd.to_datetime(inception_date, errors="coerce")
    end_dt = pd.to_datetime(end_date, errors="coerce")
    if pd.isna(start_dt) or pd.isna(end_dt):
        return 0.0

    day_span = max(int((end_dt - start_dt).days), 1)
    years = day_span / 365.25
    if years <= 0:
        return 0.0
    return safe_float((((end_value / start_value) ** (1.0 / years)) - 1.0) * 100.0)


def compute_calmar(cagr_pct: float, max_drawdown_pct: float) -> float:
    if max_drawdown_pct == 0:
        return 0.0
    return safe_float(cagr_pct / abs(max_drawdown_pct))


def build_summary(
    returns: pd.Series,
    raw_df: pd.DataFrame,
    daily_nav: pd.DataFrame,
    portfolio_state: dict[str, Any],
    manifest: dict[str, Any],
) -> DiagnosticsSummary:
    inception_date = str(portfolio_state.get("inception_date") or daily_nav.iloc[0]["date"].strftime("%Y-%m-%d"))
    first_valuation_date = daily_nav.iloc[0]["date"].strftime("%Y-%m-%d")
    end_date = daily_nav.iloc[-1]["date"].strftime("%Y-%m-%d")

    starting_capital_usd = safe_float(portfolio_state.get("starting_capital_usd"), default=100000.0)
    latest_nav_usd = safe_float(
        portfolio_state.get("last_valuation", {}).get("nav_usd"),
        default=safe_float(daily_nav.iloc[-1]["nav_usd"]),
    )

    engine_total_return_pct = safe_float(((latest_nav_usd / starting_capital_usd) - 1.0) * 100.0)
    engine_since_inception_return_pct = safe_float(
        portfolio_state.get("last_valuation", {}).get("since_inception_return_pct"),
        default=engine_total_return_pct,
    )
    engine_max_drawdown_pct = safe_float(
        portfolio_state.get("max_drawdown_pct"),
        default=max_drawdown_from_nav(raw_df.sort_values(["overlay_as_of_utc", "row_order"])["nav_usd"]),
    )
    engine_daily_return_pct = safe_float(
        portfolio_state.get("last_valuation", {}).get("daily_return_pct"),
        default=safe_float(returns.iloc[-1] * 100.0),
    )
    engine_unrealized_pnl_usd = safe_float(
        portfolio_state.get("last_valuation", {}).get("unrealized_pnl_usd"),
        default=safe_float(portfolio_state.get("unrealized_pnl_usd")),
    )

    cagr_pct = compute_cagr_pct(starting_capital_usd, latest_nav_usd, inception_date, end_date)
    sharpe = safe_float(qs.stats.sharpe(returns))
    sortino = safe_float(qs.stats.sortino(returns))
    quantstats_max_drawdown_pct = safe_float(qs.stats.max_drawdown(returns) * 100.0)
    raw_path_max_drawdown_pct = max_drawdown_from_nav(raw_df.sort_values(["overlay_as_of_utc", "row_order"])["nav_usd"])
    volatility_pct = safe_float(qs.stats.volatility(returns) * 100.0)
    calmar = compute_calmar(cagr_pct, engine_max_drawdown_pct)
    best_day_pct = safe_float(qs.stats.best(returns) * 100.0)
    worst_day_pct = safe_float(qs.stats.worst(returns) * 100.0)
    last_daily_return_pct = safe_float(returns.iloc[-1] * 100.0)

    return DiagnosticsSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        valuation_rows_raw=int(len(raw_df)),
        valuation_rows_daily=int(len(daily_nav)),
        returns_rows=int(len(returns)),
        inception_date=inception_date,
        first_valuation_date=first_valuation_date,
        end_date=end_date,
        starting_capital_usd=starting_capital_usd,
        latest_nav_usd=latest_nav_usd,
        engine_total_return_pct=engine_total_return_pct,
        engine_since_inception_return_pct=engine_since_inception_return_pct,
        engine_max_drawdown_pct=engine_max_drawdown_pct,
        engine_daily_return_pct=engine_daily_return_pct,
        engine_unrealized_pnl_usd=engine_unrealized_pnl_usd,
        cagr_pct=cagr_pct,
        sharpe=sharpe,
        sortino=sortino,
        quantstats_max_drawdown_pct=quantstats_max_drawdown_pct,
        raw_path_max_drawdown_pct=raw_path_max_drawdown_pct,
        volatility_pct=volatility_pct,
        calmar=calmar,
        best_day_pct=best_day_pct,
        worst_day_pct=worst_day_pct,
        last_daily_return_pct=last_daily_return_pct,
        source_report=manifest.get("source_report") or portfolio_state.get("last_rebalance", {}).get("source_report"),
        valuation_source=portfolio_state.get("valuation_source") or manifest.get("valuation_source"),
        overlay_as_of_utc=(manifest.get("overlay_as_of_utc") or portfolio_state.get("last_valuation", {}).get("overlay_as_of_utc")),
    )


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_markdown_summary(path: Path, summary: DiagnosticsSummary) -> None:
    lines = [
        "# Weekly FX lab diagnostics summary",
        "",
        "## Engine-aligned headline metrics",
        "",
        f"- Inception date: **{summary.inception_date}**",
        f"- First valuation date in daily diagnostics: **{summary.first_valuation_date}**",
        f"- Latest valuation date: **{summary.end_date}**",
        f"- Starting capital (USD): **{summary.starting_capital_usd:,.2f}**",
        f"- Latest NAV (USD): **{summary.latest_nav_usd:,.2f}**",
        f"- Since inception return (%): **{summary.engine_since_inception_return_pct:.4f}**",
        f"- Total return from starting capital (%): **{summary.engine_total_return_pct:.4f}**",
        f"- Daily return (%): **{summary.engine_daily_return_pct:.4f}**",
        f"- Max drawdown (%): **{summary.engine_max_drawdown_pct:.4f}**",
        f"- Unrealized P&L (USD): **{summary.engine_unrealized_pnl_usd:,.2f}**",
        "",
        "## Supplemental QuantStats diagnostics",
        "",
        f"- CAGR (%): **{summary.cagr_pct:.4f}**",
        f"- Sharpe: **{summary.sharpe:.4f}**",
        f"- Sortino: **{summary.sortino:.4f}**",
        f"- Volatility (%): **{summary.volatility_pct:.4f}**",
        f"- Calmar: **{summary.calmar:.4f}**",
        f"- Best day (%): **{summary.best_day_pct:.4f}**",
        f"- Worst day (%): **{summary.worst_day_pct:.4f}**",
        f"- Last daily return (%): **{summary.last_daily_return_pct:.4f}**",
        f"- QuantStats max drawdown from collapsed daily series (%): **{summary.quantstats_max_drawdown_pct:.4f}**",
        f"- Raw-path max drawdown from valuation history (%): **{summary.raw_path_max_drawdown_pct:.4f}**",
        "",
        "## Notes",
        "",
        "- Headline return and drawdown fields are anchored to the authoritative portfolio engine when available.",
        "- QuantStats remains a supporting diagnostics layer, not the source of truth for implementation facts.",
        "- Differences between collapsed daily-series drawdown and raw-path drawdown are expected when multiple same-day valuations exist.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    raw_df = load_valuation_history(valuation_path)
    daily_nav = build_daily_nav(raw_df)
    nav_series = daily_nav.set_index("date")["nav_usd"].astype(float)
    returns = nav_series.pct_change().dropna()
    returns.name = "fx_model_portfolio_returns"

    if returns.empty:
        raise RuntimeError("Daily return series is empty after pct_change()")

    daily_nav_export = artifact_dir / "fx_daily_nav_series.csv"
    daily_returns_export = artifact_dir / "fx_daily_returns.csv"
    summary_export = artifact_dir / "fx_quantstats_summary.json"
    summary_md_export = artifact_dir / "fx_quantstats_summary.md"
    manifest_export = artifact_dir / "fx_quantstats_manifest.json"
    html_export = artifact_dir / "fx_quantstats_tearsheet.html"

    daily_nav.assign(date=daily_nav["date"].dt.strftime("%Y-%m-%d")).to_csv(daily_nav_export, index=False)
    returns.to_frame(name="return").assign(date=lambda df: df.index.strftime("%Y-%m-%d")).loc[:, ["date", "return"]].to_csv(
        daily_returns_export,
        index=False,
    )

    summary = build_summary(returns, raw_df, daily_nav, portfolio_state, manifest)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    write_markdown_summary(summary_md_export, summary)

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
                "summary_markdown": str(summary_md_export),
                "quantstats_html": str(html_export),
            },
            "raw_valuation_rows": int(len(raw_df)),
            "daily_valuation_rows": int(len(daily_nav)),
            "returns_rows": int(len(returns)),
            "latest_nav_usd": summary.latest_nav_usd,
            "latest_date": summary.end_date,
            "engine_total_return_pct": summary.engine_total_return_pct,
            "engine_max_drawdown_pct": summary.engine_max_drawdown_pct,
            "quantstats_max_drawdown_pct": summary.quantstats_max_drawdown_pct,
        },
    )

    print(f"QuantStats diagnostics written to: {artifact_dir}")
    print(f"HTML tearsheet: {html_export}")
    print(f"Summary JSON: {summary_export}")
    print(f"Summary Markdown: {summary_md_export}")


if __name__ == "__main__":
    main()
