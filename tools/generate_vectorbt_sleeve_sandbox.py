#!/usr/bin/env python3
"""Generate a lab-only sleeve-level vectorbt sandbox for FX currencies.

This script is intentionally non-destructive:
- it reads the existing FX technical overlay and state context
- it fetches underlying pair histories using the same Twelve Data pipeline style
- it writes artifacts only to a separate lab output folder
- it does not modify the production report or delivery flow

The sandbox tests non-USD sleeves directly. USD cash is intentionally excluded,
because cash is a reserve allocation rather than a directional FX sleeve.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import vectorbt as vbt

from fx_technical_overlay import PAIR_MAP, fetch_series

FAST_WINDOWS = [3, 5, 7]
SLOW_WINDOWS = [10, 15, 21]
DD_LIMITS_PCT = [0.50, 0.75]

SLEEVE_MAP = {
    "EUR": {"pair": "EURUSD", "symbol": PAIR_MAP["EURUSD"], "invert": False},
    "GBP": {"pair": "GBPUSD", "symbol": PAIR_MAP["GBPUSD"], "invert": False},
    "AUD": {"pair": "AUDUSD", "symbol": PAIR_MAP["AUDUSD"], "invert": False},
    "NZD": {"pair": "NZDUSD", "symbol": PAIR_MAP["NZDUSD"], "invert": False},
    "JPY": {"pair": "USDJPY", "symbol": PAIR_MAP["USDJPY"], "invert": True},
    "CHF": {"pair": "USDCHF", "symbol": PAIR_MAP["USDCHF"], "invert": True},
    "CAD": {"pair": "USDCAD", "symbol": PAIR_MAP["USDCAD"], "invert": True},
    "MXN": {"pair": "USDMXN", "symbol": PAIR_MAP["USDMXN"], "invert": True},
    "ZAR": {"pair": "USDZAR", "symbol": PAIR_MAP["USDZAR"], "invert": True},
}


@dataclass
class SleeveSandboxSummary:
    generated_at_utc: str
    sleeve_count: int
    total_strategy_rows: int
    best_overall_sleeve: str
    best_overall_strategy: str
    best_overall_total_return_pct: float
    best_overall_max_drawdown_pct: float
    worst_overall_sleeve: str
    worst_overall_strategy: str
    worst_overall_total_return_pct: float
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sleeve-level vectorbt sandbox for weekly-fx")
    parser.add_argument("--output-dir", default="output", help="Path to repo output/ directory")
    parser.add_argument(
        "--artifact-dir",
        default="lab_outputs/vectorbt_sleeves",
        help="Directory to write sandbox artifacts into",
    )
    parser.add_argument("--daily-bars", type=int, default=260, help="Daily bars to request per sleeve")
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


def max_drawdown_pct(nav_series: pd.Series) -> float:
    values = pd.to_numeric(nav_series, errors="coerce").dropna().astype(float)
    if values.empty:
        return 0.0
    peak = values.cummax()
    dd = (values / peak) - 1.0
    return safe_float(dd.min() * 100.0)


def annualized_sharpe(daily_returns: pd.Series) -> float:
    if daily_returns.empty:
        return 0.0
    std = daily_returns.std(ddof=0)
    if std == 0 or pd.isna(std):
        return 0.0
    return safe_float((daily_returns.mean() / std) * math.sqrt(252.0))


def annualized_sortino(daily_returns: pd.Series) -> float:
    if daily_returns.empty:
        return 0.0
    downside = daily_returns[daily_returns < 0]
    downside_std = downside.std(ddof=0)
    if downside.empty or downside_std == 0 or pd.isna(downside_std):
        return 0.0
    return safe_float((daily_returns.mean() / downside_std) * math.sqrt(252.0))


def cagr_pct(start_value: float, end_value: float, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> float:
    if start_value <= 0 or end_value <= 0:
        return 0.0
    days = max((end_ts - start_ts).days, 1)
    years = days / 365.25
    if years <= 0:
        return 0.0
    return safe_float((((end_value / start_value) ** (1.0 / years)) - 1.0) * 100.0)


def entry_count_from_signals(entries: pd.Series) -> int:
    entries = entries.fillna(False).astype(bool)
    transitions = entries & (~entries.shift(1, fill_value=False))
    return int(transitions.sum())


def fetch_sleeve_close(symbol: str, invert: bool, outputsize: int) -> pd.Series:
    rows = fetch_series(symbol, "1day", outputsize=outputsize)
    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["datetime", "close"]).copy()
    if df.empty:
        raise RuntimeError(f"No usable rows fetched for symbol {symbol}")
    close = df.set_index("datetime")["close"].astype(float)
    if invert:
        close = 1.0 / close
    close.name = symbol.replace("/", "") + ("_INV" if invert else "")
    return close


def metrics_from_portfolio(
    sleeve: str,
    pair: str,
    overlay_status: str,
    name: str,
    family: str,
    params: dict[str, Any],
    pf: Any,
    entries: pd.Series,
) -> tuple[dict[str, Any], pd.Series]:
    value = pd.Series(pf.value(), copy=False)
    value.name = name
    daily_value = value.groupby(value.index.floor("D")).last().astype(float)
    daily_returns = daily_value.pct_change().dropna()

    total_return = safe_float(((daily_value.iloc[-1] / daily_value.iloc[0]) - 1.0) * 100.0)
    mdd = max_drawdown_pct(value)
    sharpe = annualized_sharpe(daily_returns)
    sortino = annualized_sortino(daily_returns)
    cagr = cagr_pct(safe_float(daily_value.iloc[0]), safe_float(daily_value.iloc[-1]), daily_value.index[0], daily_value.index[-1])

    row = {
        "sleeve": sleeve,
        "pair": pair,
        "overlay_status": overlay_status,
        "strategy": name,
        "family": family,
        "parameters": json.dumps(params, sort_keys=True),
        "start_date": daily_value.index[0].strftime("%Y-%m-%d"),
        "end_date": daily_value.index[-1].strftime("%Y-%m-%d"),
        "start_value": safe_float(daily_value.iloc[0]),
        "end_value": safe_float(daily_value.iloc[-1]),
        "total_return_pct": total_return,
        "cagr_pct": cagr,
        "max_drawdown_pct": mdd,
        "sharpe": sharpe,
        "sortino": sortino,
        "best_day_pct": safe_float(daily_returns.max() * 100.0 if not daily_returns.empty else 0.0),
        "worst_day_pct": safe_float(daily_returns.min() * 100.0 if not daily_returns.empty else 0.0),
        "last_daily_return_pct": safe_float(daily_returns.iloc[-1] * 100.0 if not daily_returns.empty else 0.0),
        "entry_signal_count": entry_count_from_signals(entries),
    }
    return row, daily_value


def build_sleeve_strategy_rows(
    sleeve: str,
    pair: str,
    overlay_status: str,
    close: pd.Series,
) -> tuple[list[dict[str, Any]], dict[str, pd.Series]]:
    rows: list[dict[str, Any]] = []
    curves: dict[str, pd.Series] = {}

    baseline_entries = pd.Series(False, index=close.index)
    baseline_entries.iloc[0] = True
    baseline_exits = pd.Series(False, index=close.index)
    baseline_pf = vbt.Portfolio.from_signals(close, baseline_entries, baseline_exits, init_cash=1.0, fees=0.0)
    baseline_name = f"{sleeve}_baseline_hold"
    baseline_row, baseline_curve = metrics_from_portfolio(
        sleeve,
        pair,
        overlay_status,
        baseline_name,
        "baseline",
        {},
        baseline_pf,
        baseline_entries,
    )
    rows.append(baseline_row)
    curves[baseline_name] = baseline_curve

    close_dd_pct = ((close / close.cummax()) - 1.0) * 100.0

    for fast in FAST_WINDOWS:
        for slow in SLOW_WINDOWS:
            if fast >= slow:
                continue

            fast_ma = vbt.MA.run(close, window=fast).ma
            slow_ma = vbt.MA.run(close, window=slow).ma
            trend_entries = (fast_ma > slow_ma).fillna(False)
            trend_exits = (fast_ma <= slow_ma).fillna(False)

            trend_name = f"{sleeve}_trend_ma_{fast}_{slow}"
            trend_pf = vbt.Portfolio.from_signals(close, trend_entries, trend_exits, init_cash=1.0, fees=0.0)
            trend_row, trend_curve = metrics_from_portfolio(
                sleeve,
                pair,
                overlay_status,
                trend_name,
                "trend",
                {"fast_window": fast, "slow_window": slow},
                trend_pf,
                trend_entries,
            )
            rows.append(trend_row)
            curves[trend_name] = trend_curve

            for dd_limit in DD_LIMITS_PCT:
                risk_ok = (close_dd_pct > (-dd_limit)).fillna(False)
                combo_entries = (trend_entries & risk_ok).fillna(False)
                combo_exits = (trend_exits | (~risk_ok)).fillna(False)
                combo_name = f"{sleeve}_trend_dd_ma_{fast}_{slow}_dd_{str(dd_limit).replace('.', '_')}"
                combo_pf = vbt.Portfolio.from_signals(close, combo_entries, combo_exits, init_cash=1.0, fees=0.0)
                combo_row, combo_curve = metrics_from_portfolio(
                    sleeve,
                    pair,
                    overlay_status,
                    combo_name,
                    "trend_plus_drawdown",
                    {"fast_window": fast, "slow_window": slow, "dd_limit_pct": dd_limit},
                    combo_pf,
                    combo_entries,
                )
                rows.append(combo_row)
                curves[combo_name] = combo_curve

    return rows, curves


def write_markdown_summary(path: Path, summary: SleeveSandboxSummary, best_df: pd.DataFrame) -> None:
    lines = [
        "# Weekly FX sleeve-level vectorbt sandbox summary",
        "",
        "## Purpose",
        "",
        "This is a lab-only sleeve-level sandbox that tests simple vectorbt rules on underlying FX sleeve price paths.",
        "It does not replace production methodology or delivery logic.",
        "",
        "## Headline result",
        "",
        f"- Best overall sleeve: **{summary.best_overall_sleeve}**",
        f"- Best overall strategy: **{summary.best_overall_strategy}**",
        f"- Best overall total return (%): **{summary.best_overall_total_return_pct:.4f}**",
        f"- Best overall max drawdown (%): **{summary.best_overall_max_drawdown_pct:.4f}**",
        f"- Weakest sleeve by best-rule result: **{summary.worst_overall_sleeve}**",
        f"- Weakest sleeve best strategy: **{summary.worst_overall_strategy}**",
        f"- Weakest sleeve best-rule total return (%): **{summary.worst_overall_total_return_pct:.4f}**",
        "",
        "## Best rule per sleeve",
        "",
        "| Sleeve | Overlay status | Strategy | Family | Total return (%) | Max drawdown (%) | Sharpe | Sortino |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for _, row in best_df.iterrows():
        lines.append(
            f"| {row['sleeve']} | {row['overlay_status']} | {row['strategy']} | {row['family']} | {row['total_return_pct']:.4f} | {row['max_drawdown_pct']:.4f} | {row['sharpe']:.4f} | {row['sortino']:.4f} |"
        )
    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- Treat this as sleeve-level exploration, not as automatic production allocation advice.",
        "- A sleeve whose top rule looks good over a short window may still be pure noise.",
        "- Compare these results against the existing technical overlay, not instead of it.",
        "",
        "## Note",
        "",
        summary.note,
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    overlay = load_json(output_dir / "fx_technical_overlay.json")
    overlay_status_map = {
        ccy: payload.get("ta_status", "unknown")
        for ccy, payload in overlay.get("currencies", {}).items()
    }

    all_rows: list[dict[str, Any]] = []
    all_curves: dict[str, pd.Series] = {}
    price_frame: dict[str, pd.Series] = {}

    for sleeve, config in SLEEVE_MAP.items():
        close = fetch_sleeve_close(config["symbol"], config["invert"], args.daily_bars)
        price_frame[sleeve] = close
        sleeve_rows, sleeve_curves = build_sleeve_strategy_rows(
            sleeve=sleeve,
            pair=config["pair"],
            overlay_status=overlay_status_map.get(sleeve, "unknown"),
            close=close,
        )
        all_rows.extend(sleeve_rows)
        all_curves.update(sleeve_curves)

    grid_df = pd.DataFrame(all_rows).sort_values(["sleeve", "total_return_pct", "sharpe", "sortino"], ascending=[True, False, False, False]).reset_index(drop=True)
    best_by_sleeve = grid_df.groupby("sleeve", as_index=False).first().sort_values("total_return_pct", ascending=False).reset_index(drop=True)

    best_overall = best_by_sleeve.iloc[0]
    worst_overall = best_by_sleeve.iloc[-1]

    summary = SleeveSandboxSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        sleeve_count=int(len(SLEEVE_MAP)),
        total_strategy_rows=int(len(grid_df)),
        best_overall_sleeve=str(best_overall["sleeve"]),
        best_overall_strategy=str(best_overall["strategy"]),
        best_overall_total_return_pct=safe_float(best_overall["total_return_pct"]),
        best_overall_max_drawdown_pct=safe_float(best_overall["max_drawdown_pct"]),
        worst_overall_sleeve=str(worst_overall["sleeve"]),
        worst_overall_strategy=str(worst_overall["strategy"]),
        worst_overall_total_return_pct=safe_float(worst_overall["total_return_pct"]),
        note="This sleeve-level sandbox uses underlying FX pair histories transformed into sleeve-aligned price paths. It is a research layer only and must be checked for short-history noise before any promotion.",
    )

    prices_export = artifact_dir / "fx_sleeve_price_history.csv"
    grid_export = artifact_dir / "fx_sleeve_vectorbt_strategy_grid.csv"
    best_export = artifact_dir / "fx_sleeve_vectorbt_best_by_sleeve.csv"
    summary_export = artifact_dir / "fx_sleeve_vectorbt_summary.json"
    summary_md_export = artifact_dir / "fx_sleeve_vectorbt_summary.md"
    curves_export = artifact_dir / "fx_sleeve_vectorbt_best_equity_curves.csv"
    manifest_export = artifact_dir / "fx_sleeve_vectorbt_manifest.json"

    price_df = pd.concat(price_frame.values(), axis=1)
    price_df.columns = list(price_frame.keys())
    price_df = price_df.groupby(price_df.index.floor("D")).last().reset_index().rename(columns={"index": "date"})
    price_df["date"] = pd.to_datetime(price_df["date"]).dt.strftime("%Y-%m-%d")
    price_df.to_csv(prices_export, index=False)

    grid_df.to_csv(grid_export, index=False)
    best_by_sleeve.to_csv(best_export, index=False)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    write_markdown_summary(summary_md_export, summary, best_by_sleeve)

    best_curve_names = best_by_sleeve["strategy"].tolist()
    curve_df = pd.concat([all_curves[name].rename(name) for name in best_curve_names], axis=1)
    curve_df = curve_df.groupby(curve_df.index.floor("D")).last().reset_index().rename(columns={"index": "date"})
    curve_df["date"] = pd.to_datetime(curve_df["date"]).dt.strftime("%Y-%m-%d")
    curve_df.to_csv(curves_export, index=False)

    write_manifest(
        manifest_export,
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "Twelve Data via sleeve-level lab fetch",
            "daily_bars_requested": args.daily_bars,
            "sleeves": list(SLEEVE_MAP.keys()),
            "parameter_grid": {
                "fast_windows": FAST_WINDOWS,
                "slow_windows": SLOW_WINDOWS,
                "drawdown_limits_pct": DD_LIMITS_PCT,
            },
            "artifact_files": {
                "price_history_csv": str(prices_export),
                "strategy_grid_csv": str(grid_export),
                "best_by_sleeve_csv": str(best_export),
                "summary_json": str(summary_export),
                "summary_markdown": str(summary_md_export),
                "best_equity_curves_csv": str(curves_export),
            },
            "best_overall_sleeve": summary.best_overall_sleeve,
            "best_overall_strategy": summary.best_overall_strategy,
            "total_strategy_rows": summary.total_strategy_rows,
        },
    )

    print(f"Sleeve-level vectorbt sandbox artifacts written to: {artifact_dir}")
    print(f"Price history CSV: {prices_export}")
    print(f"Best-by-sleeve CSV: {best_export}")
    print(f"Summary Markdown: {summary_md_export}")


if __name__ == "__main__":
    main()
