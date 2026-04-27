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
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import vectorbt as vbt

from fx_technical_overlay import PAIR_MAP, fetch_series

FAST_WINDOWS = [3, 5, 7]
SLOW_WINDOWS = [10, 15, 21]
DD_LIMITS_PCT = [0.50, 0.75]
MIN_ACTIVE_ENTRY_SIGNALS = 1
MIN_ACTIVE_EXPOSURE_PCT = 15.0

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
    active_candidate_rows: int
    inactive_candidate_rows: int
    best_active_overall_sleeve: str
    best_active_overall_strategy: str
    best_active_overall_total_return_pct: float
    best_active_overall_max_drawdown_pct: float
    best_inactive_overall_sleeve: str
    best_inactive_overall_strategy: str
    best_inactive_overall_total_return_pct: float
    activity_threshold_entry_signals: int
    activity_threshold_exposure_pct: float
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


def position_state_from_signals(entries: pd.Series, exits: pd.Series) -> pd.Series:
    entries = entries.fillna(False).astype(bool)
    exits = exits.fillna(False).astype(bool)
    active = False
    states: list[bool] = []
    for idx in entries.index:
        if active and bool(exits.loc[idx]):
            active = False
        if (not active) and bool(entries.loc[idx]):
            active = True
        states.append(active)
    return pd.Series(states, index=entries.index, name="in_position")


def exposure_stats(position_state: pd.Series) -> tuple[float, int, int]:
    daily_state = position_state.groupby(position_state.index.floor("D")).max().astype(bool)
    total_days = int(len(daily_state))
    invested_days = int(daily_state.sum())
    exposure_pct = safe_float((invested_days / total_days) * 100.0 if total_days > 0 else 0.0)
    return exposure_pct, invested_days, total_days


def quality_flag(entry_signal_count: int, exposure_pct: float) -> str:
    if entry_signal_count >= MIN_ACTIVE_ENTRY_SIGNALS and exposure_pct >= MIN_ACTIVE_EXPOSURE_PCT:
        return "active_candidate"
    return "inactive_or_no_trade"


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
    exits: pd.Series,
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
    signal_count = entry_count_from_signals(entries)
    exposure_pct, invested_days, total_days = exposure_stats(position_state_from_signals(entries, exits))
    flag = quality_flag(signal_count, exposure_pct)

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
        "entry_signal_count": signal_count,
        "exposure_pct": exposure_pct,
        "invested_days": invested_days,
        "total_days": total_days,
        "rule_quality_flag": flag,
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
        baseline_exits,
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
                trend_exits,
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
                    combo_exits,
                )
                rows.append(combo_row)
                curves[combo_name] = combo_curve

    return rows, curves


def normalize_date_index_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.groupby(frame.index.floor("D")).last().reset_index()
    first_col = normalized.columns[0]
    normalized = normalized.rename(columns={first_col: "date"})
    normalized["date"] = pd.to_datetime(normalized["date"]).dt.strftime("%Y-%m-%d")
    return normalized


def add_baseline_deltas(grid_df: pd.DataFrame) -> pd.DataFrame:
    baseline = (
        grid_df.loc[grid_df["family"] == "baseline", ["sleeve", "total_return_pct", "max_drawdown_pct"]]
        .rename(columns={
            "total_return_pct": "baseline_total_return_pct",
            "max_drawdown_pct": "baseline_max_drawdown_pct",
        })
        .copy()
    )
    merged = grid_df.merge(baseline, on="sleeve", how="left")
    merged["baseline_return_delta_pct"] = merged["total_return_pct"] - merged["baseline_total_return_pct"]
    merged["baseline_drawdown_delta_pct"] = merged["max_drawdown_pct"] - merged["baseline_max_drawdown_pct"]
    return merged


def best_by_sleeve(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[])
    ranked = df.sort_values(
        ["sleeve", "total_return_pct", "sharpe", "sortino", "baseline_return_delta_pct"],
        ascending=[True, False, False, False, False],
    ).reset_index(drop=True)
    return ranked.groupby("sleeve", as_index=False).first().reset_index(drop=True)


def write_markdown_summary(
    path: Path,
    summary: SleeveSandboxSummary,
    active_best_df: pd.DataFrame,
    inactive_best_df: pd.DataFrame,
) -> None:
    lines = [
        "# Weekly FX sleeve-level vectorbt sandbox summary",
        "",
        "## Purpose",
        "",
        "This is a lab-only sleeve-level sandbox that tests simple vectorbt rules on underlying FX sleeve price paths.",
        "It does not replace production methodology or delivery logic.",
        "",
        "## Activity filter",
        "",
        f"- Minimum entry signals for an active candidate: **{summary.activity_threshold_entry_signals}**",
        f"- Minimum exposure for an active candidate: **{summary.activity_threshold_exposure_pct:.1f}%**",
        "- Rules below the threshold are kept visible, but they are ranked separately as inactive / no-trade outcomes.",
        "",
        "## Headline result",
        "",
        f"- Best active overall sleeve: **{summary.best_active_overall_sleeve}**",
        f"- Best active overall strategy: **{summary.best_active_overall_strategy}**",
        f"- Best active overall total return (%): **{summary.best_active_overall_total_return_pct:.4f}**",
        f"- Best active overall max drawdown (%): **{summary.best_active_overall_max_drawdown_pct:.4f}**",
        f"- Best inactive overall sleeve: **{summary.best_inactive_overall_sleeve}**",
        f"- Best inactive overall strategy: **{summary.best_inactive_overall_strategy}**",
        f"- Best inactive overall total return (%): **{summary.best_inactive_overall_total_return_pct:.4f}**",
        "",
        "## Best active rule per sleeve",
        "",
        "| Sleeve | Overlay status | Strategy | Family | Total return (%) | Baseline delta (%) | Max drawdown (%) | Exposure (%) | Entries |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in active_best_df.iterrows():
        lines.append(
            f"| {row['sleeve']} | {row['overlay_status']} | {row['strategy']} | {row['family']} | {row['total_return_pct']:.4f} | {row['baseline_return_delta_pct']:.4f} | {row['max_drawdown_pct']:.4f} | {row['exposure_pct']:.2f} | {int(row['entry_signal_count'])} |"
        )

    lines.extend([
        "",
        "## Best inactive / no-trade rule per sleeve",
        "",
        "| Sleeve | Overlay status | Strategy | Total return (%) | Exposure (%) | Entries | Quality flag |",
        "|---|---|---|---:|---:|---:|---|",
    ])
    if inactive_best_df.empty:
        lines.append("| - | - | No inactive / no-trade candidates | - | - | - | - |")
    else:
        for _, row in inactive_best_df.iterrows():
            lines.append(
                f"| {row['sleeve']} | {row['overlay_status']} | {row['strategy']} | {row['total_return_pct']:.4f} | {row['exposure_pct']:.2f} | {int(row['entry_signal_count'])} | {row['rule_quality_flag']} |"
            )

    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- Treat active winners and inactive / no-trade outcomes as different categories.",
        "- A flat defensive rule may still be useful, but it is not the same as an active improving rule.",
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

    grid_df = pd.DataFrame(all_rows)
    grid_df = add_baseline_deltas(grid_df)
    grid_df = grid_df.sort_values(
        ["sleeve", "total_return_pct", "sharpe", "sortino", "baseline_return_delta_pct"],
        ascending=[True, False, False, False, False],
    ).reset_index(drop=True)

    active_df = grid_df.loc[grid_df["rule_quality_flag"] == "active_candidate"].copy()
    inactive_df = grid_df.loc[grid_df["rule_quality_flag"] == "inactive_or_no_trade"].copy()

    active_best_by_sleeve = best_by_sleeve(active_df).sort_values("total_return_pct", ascending=False).reset_index(drop=True)
    inactive_best_by_sleeve = best_by_sleeve(inactive_df).sort_values("total_return_pct", ascending=False).reset_index(drop=True)

    best_active = active_best_by_sleeve.iloc[0] if not active_best_by_sleeve.empty else None
    best_inactive = inactive_best_by_sleeve.iloc[0] if not inactive_best_by_sleeve.empty else None

    summary = SleeveSandboxSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        sleeve_count=int(len(SLEEVE_MAP)),
        total_strategy_rows=int(len(grid_df)),
        active_candidate_rows=int(len(active_df)),
        inactive_candidate_rows=int(len(inactive_df)),
        best_active_overall_sleeve=str(best_active["sleeve"]) if best_active is not None else "none",
        best_active_overall_strategy=str(best_active["strategy"]) if best_active is not None else "none",
        best_active_overall_total_return_pct=safe_float(best_active["total_return_pct"]) if best_active is not None else 0.0,
        best_active_overall_max_drawdown_pct=safe_float(best_active["max_drawdown_pct"]) if best_active is not None else 0.0,
        best_inactive_overall_sleeve=str(best_inactive["sleeve"]) if best_inactive is not None else "none",
        best_inactive_overall_strategy=str(best_inactive["strategy"]) if best_inactive is not None else "none",
        best_inactive_overall_total_return_pct=safe_float(best_inactive["total_return_pct"]) if best_inactive is not None else 0.0,
        activity_threshold_entry_signals=MIN_ACTIVE_ENTRY_SIGNALS,
        activity_threshold_exposure_pct=MIN_ACTIVE_EXPOSURE_PCT,
        note="This sleeve-level sandbox uses underlying FX pair histories transformed into sleeve-aligned price paths. Active winners and inactive / no-trade outcomes are now separated so flat defensive rules do not masquerade as active improvements.",
    )

    prices_export = artifact_dir / "fx_sleeve_price_history.csv"
    grid_export = artifact_dir / "fx_sleeve_vectorbt_strategy_grid.csv"
    active_best_export = artifact_dir / "fx_sleeve_vectorbt_best_active_by_sleeve.csv"
    inactive_best_export = artifact_dir / "fx_sleeve_vectorbt_best_inactive_by_sleeve.csv"
    summary_export = artifact_dir / "fx_sleeve_vectorbt_summary.json"
    summary_md_export = artifact_dir / "fx_sleeve_vectorbt_summary.md"
    curves_export = artifact_dir / "fx_sleeve_vectorbt_best_active_equity_curves.csv"
    manifest_export = artifact_dir / "fx_sleeve_vectorbt_manifest.json"

    price_df = pd.concat(price_frame.values(), axis=1)
    price_df.columns = list(price_frame.keys())
    price_df = normalize_date_index_frame(price_df)
    price_df.to_csv(prices_export, index=False)

    grid_df.to_csv(grid_export, index=False)
    active_best_by_sleeve.to_csv(active_best_export, index=False)
    inactive_best_by_sleeve.to_csv(inactive_best_export, index=False)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    write_markdown_summary(summary_md_export, summary, active_best_by_sleeve, inactive_best_by_sleeve)

    if not active_best_by_sleeve.empty:
        best_curve_names = active_best_by_sleeve["strategy"].tolist()
        curve_df = pd.concat([all_curves[name].rename(name) for name in best_curve_names], axis=1)
        curve_df = normalize_date_index_frame(curve_df)
        curve_df.to_csv(curves_export, index=False)
    else:
        pd.DataFrame(columns=["date"]).to_csv(curves_export, index=False)

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
            "activity_filter": {
                "min_entry_signals": MIN_ACTIVE_ENTRY_SIGNALS,
                "min_exposure_pct": MIN_ACTIVE_EXPOSURE_PCT,
            },
            "artifact_files": {
                "price_history_csv": str(prices_export),
                "strategy_grid_csv": str(grid_export),
                "best_active_by_sleeve_csv": str(active_best_export),
                "best_inactive_by_sleeve_csv": str(inactive_best_export),
                "summary_json": str(summary_export),
                "summary_markdown": str(summary_md_export),
                "best_active_equity_curves_csv": str(curves_export),
            },
            "best_active_overall_sleeve": summary.best_active_overall_sleeve,
            "best_active_overall_strategy": summary.best_active_overall_strategy,
            "best_inactive_overall_sleeve": summary.best_inactive_overall_sleeve,
            "best_inactive_overall_strategy": summary.best_inactive_overall_strategy,
            "total_strategy_rows": summary.total_strategy_rows,
            "active_candidate_rows": summary.active_candidate_rows,
            "inactive_candidate_rows": summary.inactive_candidate_rows,
        },
    )

    print(f"Sleeve-level vectorbt sandbox artifacts written to: {artifact_dir}")
    print(f"Price history CSV: {prices_export}")
    print(f"Best active-by-sleeve CSV: {active_best_export}")
    print(f"Best inactive-by-sleeve CSV: {inactive_best_export}")
    print(f"Summary Markdown: {summary_md_export}")


if __name__ == "__main__":
    main()
