# vectorbt lab rule sandbox

This document describes the **lab-only vectorbt integration** in `weekly-fx`.

## Purpose

The goal is to add a separate **rule-testing sandbox** without changing the existing production-style FX review flow.

This layer is intentionally:
- non-destructive
- manual to run
- separate from `send_fxreport.py`
- separate from the client-facing Weekly FX Review markdown
- separate from email delivery
- explicitly **not** a production signal engine

## What it tests

The sandbox treats the tracked FX model portfolio NAV path as a **research proxy** and compares:
- baseline hold
- simple trend filters
- simple trend-plus-drawdown filters

The purpose is not to claim that the model portfolio NAV itself is a tradable asset.
The purpose is to test whether simple **portfolio-level overlays** would have changed the realized path enough to justify further research.

## Inputs

The workflow reads:
- `output/fx_valuation_history.csv`
- `output/fx_portfolio_state.json`
- `output/fx_state_refresh_manifest.json`

## What it writes

Artifacts are generated into:
- `lab_outputs/vectorbt/`

The workflow currently produces:
- `fx_vectorbt_strategy_grid.csv`
- `fx_vectorbt_top_strategies.csv`
- `fx_vectorbt_summary.json`
- `fx_vectorbt_summary.md`
- `fx_vectorbt_equity_curves.csv`
- `fx_vectorbt_manifest.json`

## Interpretation rules

- Treat this as a **portfolio-level overlay sandbox**, not as a direct FX pair execution model.
- Better sandbox performance does **not** mean the rule is production-ready.
- The main use is to pressure-test whether simple trend / drawdown filters deserve further investigation.
- This layer is for QA, exploration, and comparison only.

## Safety rules

- Do not wire this into the production client email workflow.
- Do not replace the production FX decision framework with the top sandbox strategy.
- Do not treat the best sandbox rule as an automatic portfolio recommendation.
- Do not promote any rule from this layer without explicit review against the production methodology.

## Expected next uses

This layer is intended to support:
- rule-sensitivity checks on the tracked portfolio path
- comparison of simple overlay ideas against baseline hold
- later discussion of whether any portfolio-level filter deserves deeper research
- future comparison against ETF and Index lab integrations
