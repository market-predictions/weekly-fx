# QuantStats lab diagnostics

This document describes the first **lab-only analytics integration** in `weekly-fx`.

## Purpose

The goal is to add a separate portfolio diagnostics layer without changing the existing production-style report flow.

This layer is intentionally:
- non-destructive
- manual to run
- separate from `send_fxreport.py`
- separate from the client-facing Weekly FX Review markdown
- separate from email delivery

## What it does

The lab diagnostics workflow reads:
- `output/fx_valuation_history.csv`
- `output/fx_portfolio_state.json`
- `output/fx_state_refresh_manifest.json`

It then:
1. collapses valuation history to one daily NAV point per calendar date
2. computes daily portfolio returns from NAV changes
3. generates a QuantStats HTML tearsheet
4. writes a compact summary JSON
5. uploads all artifacts as a GitHub Actions artifact bundle

## Files added

- `tools/generate_quantstats_diagnostics.py`
- `.github/workflows/lab-quantstats-diagnostics.yml`

## Output location

Artifacts are generated into:
- `lab_outputs/quantstats/`

That folder is used only as a workflow artifact staging area in the lab repository.

## Safety rules

- Do not treat this diagnostics layer as production delivery.
- Do not wire it into the client email workflow without explicit validation.
- Do not replace Section 7 numbers with QuantStats output automatically.
- Treat this layer as QA / analytics support first.

## Expected next uses

This layer is intended to support:
- faster Section 7 validation
- drawdown and rolling-risk QA
- portfolio diagnostics comparisons across runs
- later comparison against ETF and Index lab integrations
