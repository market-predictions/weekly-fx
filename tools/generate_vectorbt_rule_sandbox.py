#!/usr/bin/env python3
"""Generate a lab-only vectorbt rule sandbox for the FX model portfolio NAV path.

This script is intentionally non-destructive:
- it reads existing repo state from output/
- it treats the model portfolio NAV path as a research proxy, not as a tradable asset
- it writes artifacts only to a separate lab output folder
- it does not modify the production report or delivery flow
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


FAST_WINDOWS = [3, 5, 7]
SLOW_WINDOWS = [10, 15, 21]
DD_LIMITS_PCT = [0.50, 0.75]


@dataclass
class SandboxSummary:
    generated_at_utc: str
    starting_capital_usd: float
    proxy_rows: int
    daily_rows: int
    strategy_count: int
    baseline_strategy: str
    baseline_total_return_pct: float
    baseline_max_drawdown_pct: float
    best_strategy: str
    best_family: str
    best_total_return_pct: float
    best_max_drawdown_pct: float
    best_vs_baseline_return_delta_pct: float
    best_vs_baseline_drawdown_delta_pct: float
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate vectorbt sandbox diagnostics from FX valuation history")
    parser.add_argument("--output-dir", default="output", help="Path to repo output/ directory")
    parser.add_argument(
        "--artifact-dir",
        default="lab_outputs/vectorbt",
        help="Directory to write sandbox artifacts into",
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


def load_daily_nav(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing valuation history file: {csv_path}")
    df = pd.read_csv(csv_path)
    required = {"date", "nav_usd"}
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
    if len(daily) < 2:
        raise RuntimeError("Need at least 2 daily NAV points for vectorbt sandbox")
    return daily


def build_proxy_close(daily_nav: pd.DataFrame, portfolio_state: dict[str, Any]) -> pd.Series:
    ts = pd.to_datetime(daily_nav["date"]).dt.tz_localize("UTC") + pd.Timedelta(hours=23, minutes=59)
    close = pd.Series(daily_nav["nav_usd"].astype(float).values, index=ts, name="fx_model_nav_proxy")

    starting_capital = safe_float(portfolio_state.get("starting_capital_usd"), 100000.0)
    first_close = safe_float(close.iloc[0])
    if not math.isclose(first_close, starting_capital, rel_tol=0.0, abs_tol=1e-9):
        synthetic_start_ts = close.index[0] - pd.Timedelta(days=1)
        synthetic = pd.Series([starting_capital], index=[synthetic_start_ts], name=close.name)
        close = pd.concat([synthetic, close]).sort_index()

    return close.astype(float)


def collapse_daily_last(series: pd.Series) -> pd.Series:
    idx = series.index
    if getattr(idx, "tz", None) is not None:
        groups = idx.tz_convert("UTC").floor("D")
    else:
        groups = idx.floor("D")
    return series.groupby(groups).last().astype(float)


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


def metrics_from_portfolio(
    name: str,
    family: str,
    params: dict[str, Any],
    pf: Any,
    entries: pd.Series,
    starting_capital: float,
) -> tuple[dict[str, Any], pd.Series]:
    value = pd.Series(pf.value(), copy=False)
    value.name = name
    daily_value = collapse_daily_last(value)
    daily_returns = daily_value.pct_change().dropna()

    total_return = safe_float(((daily_value.iloc[-1] / starting_capital) - 1.0) * 100.0)
    mdd = max_drawdown_pct(value)
    sharpe = annualized_sharpe(daily_returns)
    sortino = annualized_sortino(daily_returns)
    cagr = cagr_pct(starting_capital, safe_float(daily_value.iloc[-1]), daily_value.index[0], daily_value.index[-1])

    row = {
        "strategy": name,
        "family": family,
        "parameters": json.dumps(params, sort_keys=True),
        "start_date": daily_value.index[0].strftime("%Y-%m-%d"),
        "end_date": daily_value.index[-1].strftime("%Y-%m-%d"),
        "start_value_usd": starting_capital,
        "end_value_usd": safe_float(daily_value.iloc[-1]),
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


def build_baseline(close: pd.Series, starting_capital: float) -> tuple[dict[str, Any], pd.Series]:
    entries = pd.Series(False, index=close.index)
    entries.iloc[0] = True
    exits = pd.Series(False, index=close.index)
    pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=starting_capital, fees=0.0)
    return metrics_from_portfolio("baseline_hold", "baseline", {}, pf, entries, starting_capital)


def build_trend_and_combo_strategies(close: pd.Series, starting_capital: float) -> tuple[list[dict[str, Any]], dict[str, pd.Series]]:
    rows: list[dict[str, Any]] = []
    curves: dict[str, pd.Series] = {}

    close_dd_pct = ((close / close.cummax()) - 1.0) * 100.0

    for fast in FAST_WINDOWS:
        for slow in SLOW_WINDOWS:
            if fast >= slow:
                continue

            fast_ma = vbt.MA.run(close, window=fast).ma
            slow_ma = vbt.MA.run(close, window=slow).ma
            trend_entries = (fast_ma > slow_ma).fillna(False)
            trend_exits = (fast_ma <= slow_ma).fillna(False)

            trend_name = f"trend_ma_{fast}_{slow}"
            trend_pf = vbt.Portfolio.from_signals(close, trend_entries, trend_exits, init_cash=starting_capital, fees=0.0)
            trend_row, trend_curve = metrics_from_portfolio(
                trend_name,
                "trend",
                {"fast_window": fast, "slow_window": slow},
                trend_pf,
                trend_entries,
                starting_capital,
            )
            rows.append(trend_row)
            curves[trend_name] = trend_curve

            for dd_limit in DD_LIMITS_PCT:
                risk_ok = (close_dd_pct > (-dd_limit)).fillna(False)
                combo_entries = (trend_entries & risk_ok).fillna(False)
                combo_exits = (trend_exits | (~risk_ok)).fillna(False)

                combo_name = f"trend_dd_ma_{fast}_{slow}_dd_{str(dd_limit).replace('.', '_')}"
                combo_pf = vbt.Portfolio.from_signals(close, combo_entries, combo_exits, init_cash=starting_capital, fees=0.0)
                combo_row, combo_curve = metrics_from_portfolio(
                    combo_name,
                    "trend_plus_drawdown",
                    {"fast_window": fast, "slow_window": slow, "dd_limit_pct": dd_limit},
                    combo_pf,
                    combo_entries,
                    starting_capital,
                )
                rows.append(combo_row)
                curves[combo_name] = combo_curve

    return rows, curves


def write_markdown_summary(path: Path, summary: SandboxSummary, top_df: pd.DataFrame) -> None:
    lines = [
        "# Weekly FX vectorbt sandbox summary",
        "",
        "## Purpose",
        "",
        "This is a lab-only rule sandbox that treats the FX model portfolio NAV path as a **research proxy**.",
        "It does not replace production strategy logic or execution state.",
        "",
        "## Headline result",
        "",
        f"- Baseline strategy: **{summary.baseline_strategy}**",
        f"- Baseline total return (%): **{summary.baseline_total_return_pct:.4f}**",
        f"- Baseline max drawdown (%): **{summary.baseline_max_drawdown_pct:.4f}**",
        f"- Best sandbox strategy: **{summary.best_strategy}**",
        f"- Best strategy family: **{summary.best_family}**",
        f"- Best total return (%): **{summary.best_total_return_pct:.4f}**",
        f"- Best max drawdown (%): **{summary.best_max_drawdown_pct:.4f}**",
        f"- Return delta vs baseline (%): **{summary.best_vs_baseline_return_delta_pct:.4f}**",
        f"- Drawdown delta vs baseline (%): **{summary.best_vs_baseline_drawdown_delta_pct:.4f}**",
        "",
        "## Interpretation rules",
        "",
        "- Treat this as a **portfolio-level overlay sandbox**, not as a direct FX pair execution model.",
        "- The close series is the tracked model portfolio NAV path used as a proxy for rule testing.",
        "- Better sandbox performance does **not** mean the rule is production-ready.",
        "- The main use is to pressure-test whether simple trend / drawdown filters deserve further investigation.",
        "",
        "## Top strategies",
        "",
    ]

    if top_df.empty:
        lines.append("No strategy rows were generated.")
    else:
        lines.extend([
            "| Strategy | Family | Total return (%) | Max drawdown (%) | Sharpe | Sortino |",
            "|---|---|---:|---:|---:|---:|",
        ])
        for _, row in top_df.iterrows():
            lines.append(
                f"| {row['strategy']} | {row['family']} | {row['total_return_pct']:.4f} | {row['max_drawdown_pct']:.4f} | {row['sharpe']:.4f} | {row['sortino']:.4f} |"
            )

    lines.extend([
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

    valuation_path = output_dir / "fx_valuation_history.csv"
    portfolio_state_path = output_dir / "fx_portfolio_state.json"
    manifest_path = output_dir / "fx_state_refresh_manifest.json"

    portfolio_state = load_json(portfolio_state_path)
    refresh_manifest = load_json(manifest_path)

    daily_nav = load_daily_nav(valuation_path)
    close = build_proxy_close(daily_nav, portfolio_state)
    starting_capital = safe_float(portfolio_state.get("starting_capital_usd"), 100000.0)

    rows: list[dict[str, Any]] = []
    curves: dict[str, pd.Series] = {}

    baseline_row, baseline_curve = build_baseline(close, starting_capital)
    rows.append(baseline_row)
    curves[baseline_row["strategy"]] = baseline_curve

    strategy_rows, strategy_curves = build_trend_and_combo_strategies(close, starting_capital)
    rows.extend(strategy_rows)
    curves.update(strategy_curves)

    grid_df = pd.DataFrame(rows).sort_values(["total_return_pct", "sharpe", "sortino"], ascending=[False, False, False]).reset_index(drop=True)
    top_df = grid_df.head(10).copy()

    baseline = grid_df.loc[grid_df["strategy"] == "baseline_hold"].iloc[0]
    best = grid_df.iloc[0]

    summary = SandboxSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        starting_capital_usd=starting_capital,
        proxy_rows=int(len(close)),
        daily_rows=int(len(daily_nav)),
        strategy_count=int(len(grid_df)),
        baseline_strategy=str(baseline["strategy"]),
        baseline_total_return_pct=safe_float(baseline["total_return_pct"]),
        baseline_max_drawdown_pct=safe_float(baseline["max_drawdown_pct"]),
        best_strategy=str(best["strategy"]),
        best_family=str(best["family"]),
        best_total_return_pct=safe_float(best["total_return_pct"]),
        best_max_drawdown_pct=safe_float(best["max_drawdown_pct"]),
        best_vs_baseline_return_delta_pct=safe_float(best["total_return_pct"] - baseline["total_return_pct"]),
        best_vs_baseline_drawdown_delta_pct=safe_float(best["max_drawdown_pct"] - baseline["max_drawdown_pct"]),
        note="This sandbox tests simple trend and trend-plus-drawdown overlays on the model portfolio NAV path as a research proxy. It is a QA / exploration layer only.",
    )

    grid_export = artifact_dir / "fx_vectorbt_strategy_grid.csv"
    top_export = artifact_dir / "fx_vectorbt_top_strategies.csv"
    summary_export = artifact_dir / "fx_vectorbt_summary.json"
    summary_md_export = artifact_dir / "fx_vectorbt_summary.md"
    curves_export = artifact_dir / "fx_vectorbt_equity_curves.csv"
    manifest_export = artifact_dir / "fx_vectorbt_manifest.json"

    grid_df.to_csv(grid_export, index=False)
    top_df.to_csv(top_export, index=False)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    write_markdown_summary(summary_md_export, summary, top_df)

    top_curve_names = ["baseline_hold"] + [name for name in top_df["strategy"].tolist() if name != "baseline_hold"][:3]
    curve_frame = pd.concat([curves[name].rename(name) for name in top_curve_names], axis=1)
    curve_frame = curve_frame.groupby(curve_frame.index.floor("D")).last().reset_index().rename(columns={"index": "date"})
    curve_frame["date"] = pd.to_datetime(curve_frame["date"]).dt.strftime("%Y-%m-%d")
    curve_frame.to_csv(curves_export, index=False)

    write_manifest(
        manifest_export,
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "input_files": {
                "valuation_history": str(valuation_path),
                "portfolio_state": str(portfolio_state_path),
                "state_refresh_manifest": str(manifest_path),
            },
            "artifact_files": {
                "strategy_grid_csv": str(grid_export),
                "top_strategies_csv": str(top_export),
                "summary_json": str(summary_export),
                "summary_markdown": str(summary_md_export),
                "equity_curves_csv": str(curves_export),
            },
            "refresh_context": {
                "source_report": refresh_manifest.get("source_report"),
                "overlay_as_of_utc": refresh_manifest.get("overlay_as_of_utc"),
                "valuation_source": refresh_manifest.get("valuation_source"),
            },
            "parameter_grid": {
                "fast_windows": FAST_WINDOWS,
                "slow_windows": SLOW_WINDOWS,
                "drawdown_limits_pct": DD_LIMITS_PCT,
            },
            "baseline_strategy": summary.baseline_strategy,
            "best_strategy": summary.best_strategy,
            "strategy_count": summary.strategy_count,
        },
    )

    print(f"vectorbt sandbox artifacts written to: {artifact_dir}")
    print(f"Strategy grid CSV: {grid_export}")
    print(f"Top strategies CSV: {top_export}")
    print(f"Summary Markdown: {summary_md_export}")


if __name__ == "__main__":
    main()
