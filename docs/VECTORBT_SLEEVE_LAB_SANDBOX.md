# vectorbt sleeve-level lab sandbox

This document describes the **sleeve-level vectorbt integration** in `weekly-fx`.

## Purpose

The goal is to add a separate **sleeve-level rule-testing sandbox** without changing the existing production-style FX review flow.

This layer is intentionally:
- non-destructive
- manual to run
- separate from `send_fxreport.py`
- separate from the client-facing Weekly FX Review markdown
- separate from email delivery
- explicitly **not** a production signal engine

## What it tests

The sandbox fetches underlying daily FX pair histories and transforms them into **sleeve-aligned price paths** for the traded non-USD sleeves:
- EUR
- GBP
- AUD
- NZD
- JPY
- CHF
- CAD
- MXN
- ZAR

For direct `XXX/USD` pairs it uses the close as-is.
For `USD/XXX` pairs it inverts the close to represent the sleeve as `XXXUSD`.

It then compares, per sleeve:
- baseline hold
- simple trend filters
- simple trend-plus-drawdown filters

## Inputs

The workflow reads:
- `output/fx_technical_overlay.json`
- Twelve Data daily histories fetched at run time using `TWELVEDATA_API_KEY`

## What it writes

Artifacts are generated into:
- `lab_outputs/vectorbt_sleeves/`

The workflow currently produces:
- `fx_sleeve_price_history.csv`
- `fx_sleeve_vectorbt_strategy_grid.csv`
- `fx_sleeve_vectorbt_best_by_sleeve.csv`
- `fx_sleeve_vectorbt_summary.json`
- `fx_sleeve_vectorbt_summary.md`
- `fx_sleeve_vectorbt_best_equity_curves.csv`
- `fx_sleeve_vectorbt_manifest.json`

## Interpretation rules

- Treat this as **sleeve-level exploration**, not as automatic production allocation advice.
- A sleeve whose top rule looks good over a short window may still be pure noise.
- Compare these results against the existing technical overlay, not instead of it.
- This layer is for QA, exploration, and hypothesis generation only.

## Safety rules

- Do not wire this into the production client email workflow.
- Do not replace the production FX decision framework with the top sleeve rule.
- Do not treat the best sleeve-level sandbox rule as an automatic portfolio recommendation.
- Do not promote any rule from this layer without explicit review against the production methodology.

## Operational note

This workflow requires a valid `TWELVEDATA_API_KEY` in the lab repo secrets.
Unlike the earlier portfolio-NAV proxy sandbox, this layer depends on underlying pair histories fetched at runtime.
