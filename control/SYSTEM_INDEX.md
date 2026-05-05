# FX Review OS — System Index

This file is the **first entry point** for any serious work on the `weekly-fx` system.

## Purpose
This repository is the **non-production lab clone** of `daily-fx`.

It contains the mirrored FX production execution files plus a growing lab layer used to test tooling, diagnostics, and workflow improvements **without changing the original production repo first**.

Use this file first so you do not start in the wrong place.

## Canonical execution files
Read these after the control files and only when relevant to the task.

- `fx.txt` — current monolithic masterprompt for the Weekly FX Review.
- `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md` — alpha-discipline addendum for carry visibility, USD cash discipline, true risk buckets, reduce-signal execution, and no-action proof.
- `send_fxreport.py` — delivery/rendering script for HTML email, PDF generation, attachments, and manifest logic.
- `.github/workflows/send-weekly-report.yml` — GitHub Actions workflow that runs the report and delivery process.
- `.github/workflows/refresh-fx-state.yml` — canonical technical/state refresh workflow.
- `fx_refresh_all_state.py` — full overlay/state/carry refresh wrapper.
- `refresh_fx_portfolio_state.py` — send-path fresh-price valuation refresh.
- `output/` — archived FX reports and state artifacts.
- `output/fx_portfolio_state.json` — explicit portfolio implementation state when present.
- `output/fx_trade_ledger.csv` — trade/event history for the model portfolio when present.
- `output/fx_valuation_history.csv` — valuation history when present.
- `output/fx_recommendation_scorecard.csv` — recommendation scoring history when present.
- `output/fx_technical_overlay.json` — technical confirmation overlay input.
- `output/fx_carry_snapshot.csv` — estimated carry snapshot.
- `output/fx_risk_bucket_snapshot.json` — true USD / defensive FX / risk-on FX bucket snapshot.
- `config/fx_policy_rate_proxies.json` — policy-rate proxy config for estimated carry.
- `tools/write_fx_carry_and_risk_snapshots.py` — carry and risk-bucket artifact writer.
- `tools/apply_fx_carry_accrual.py` — policy-rate proxy carry-accrual step.
- `tools/validate_fx_action_discipline.py` — pre-send alpha-discipline validator.
- `daily_outputs/latest/` and `mt5_output/latest/` — current supporting artifacts.

### Lab-specific execution files
These files exist only in the lab repo unless explicitly promoted later:
- `tools/generate_quantstats_diagnostics.py`
- `.github/workflows/lab-quantstats-diagnostics.yml`
- `docs/QUANTSTATS_LAB_DIAGNOSTICS.md`
- `tools/generate_vectorbt_rule_sandbox.py`
- `.github/workflows/lab-vectorbt-rule-sandbox.yml`
- `docs/VECTORBT_LAB_RULE_SANDBOX.md`
- `tools/generate_vectorbt_sleeve_sandbox.py`
- `.github/workflows/lab-vectorbt-sleeve-sandbox.yml`
- `docs/VECTORBT_SLEEVE_LAB_SANDBOX.md`

## Canonical control files
These are the control-layer files for recurring sessions.

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- `control/OPTIONAL_CUSTOM_GPT_SPEC.md`

## Operating model
This repository should be read in four layers.

### 1. Decision framework
This is the strategic FX judgment layer:
- macro regime
- policy divergence
- currency ranking
- carry hurdle
- conviction-weight alignment
- portfolio rotation
- opportunity selection

Primary files today:
- `fx.txt`
- `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`

### 2. Input/state contract
This is where the repo decides what facts are authoritative.

The FX system is already more mature here than ETF because it explicitly references:
- state files
- technical overlay files
- valuation history
- trade ledger files
- carry snapshot
- risk-bucket snapshot

Even so, the authority rules should remain explicit and easy to find.

### 3. Output contract
This defines the report shape and premium delivery expectations.

Today much of it still lives inside `fx.txt` and is implemented in `send_fxreport.py`.

The alpha-discipline addendum now also requires compact report blocks for:
- `FX carry dashboard`
- `USD cash contradiction check`
- `Risk-bucket exposure`
- `No-action override table` when no rebalance occurs

### 4. Operational runbook
This defines how the system is actually run.

Today the prompt still carries too much runbook logic. Over time, the scripts and workflow should own more of the true execution layer.

The current workflow layer now also owns:
- carry/risk snapshot generation
- policy-rate proxy carry accrual
- pre-send alpha-discipline validation

## Session start rule
For architecture work, debugging, prompt changes, workflow changes, tool integration, or flow redesign, start in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then open the specific execution file(s) needed for the task

Recommended execution file priority by task:
- macro / logic / structure → `fx.txt` and `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`
- carry / cash discipline / risk buckets → `config/fx_policy_rate_proxies.json`, `output/fx_carry_snapshot.csv`, `output/fx_risk_bucket_snapshot.json`, and `tools/validate_fx_action_discipline.py`
- delivery / email / PDF / manifest → `send_fxreport.py`
- workflow / secrets / scheduling → `.github/workflows/send-weekly-report.yml`
- implementation-state disputes → the relevant file in `output/`
- lab analytics / QA → `tools/generate_quantstats_diagnostics.py` and `.github/workflows/lab-quantstats-diagnostics.yml`
- lab rule-testing / portfolio overlay sandbox → `tools/generate_vectorbt_rule_sandbox.py` and `.github/workflows/lab-vectorbt-rule-sandbox.yml`
- lab rule-testing / sleeve-level sandbox → `tools/generate_vectorbt_sleeve_sandbox.py` and `.github/workflows/lab-vectorbt-sleeve-sandbox.yml`

## Session close rule
At the end of any meaningful architecture or implementation session:

1. write stable decisions into `control/DECISION_LOG.md`
2. update `control/CURRENT_STATE.md` if the architecture changed
3. update `control/NEXT_ACTIONS.md` so the next session can restart without rediscovery

## Non-negotiable discipline
- Do not collapse state, strategy, and delivery logic back into one giant opaque prompt.
- Do not let technical overlay evidence become the only decision engine.
- Do not claim delivery succeeded without a real receipt or manifest.
- Do not treat stale overlay files as if they were fresh without labeling them.
- Do not assume lab-only tools are production-approved.
- Do not let lab workflows send client-facing output unless explicitly validated and promoted.
- Do not treat proxy backtests on the portfolio NAV path as automatic production recommendations.
- Do not treat sleeve-level sandbox winners as automatic production rules without validation.
- Do not call a sleeve a carry opportunity unless the carry estimate is shown.
- Do not call the FX book diversified without showing true risk-bucket exposure.

## Current direction of travel
The target architecture for weekly-fx is:

- **ChatGPT Project** as working memory and recurring workspace
- **GitHub** as explicit state, audit trail, and operational source of truth
- **GitHub Actions + scripts** as execution and delivery layer
- **weekly-fx** as the safe experimentation surface for tooling and QA improvements
- **daily-fx** as the protected production repo until lab changes are validated and intentionally promoted
- **Explicit carry and risk-bucket state** as part of the FX input/state contract
- **Pre-send alpha-discipline validation** before client-facing delivery
- **Optional Custom GPT** only as architect/reviewer, not as the production runner
