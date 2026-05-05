# FX Review OS — Current State

## Snapshot date
2026-05-05

## What this repository currently is

This repository is the **non-production lab clone** of the original FX production system.

It contains:
- the mirrored FX production prompt and workflow files from `daily-fx`
- the existing archived outputs and explicit state artifacts in `output/`
- the same technical overlay and mark-to-market portfolio engine concept used by production
- a lab-only analytics and rule-testing layer for non-destructive QA and tool evaluation
- a new alpha-discipline layer for carry visibility, USD cash discipline, true risk buckets, and no-action proof

## Current strengths

- Strong determinism and anti-drift framing.
- Clear client-grade presentation contract.
- Explicit state-file awareness already exists.
- Explicit technical-overlay contract already exists.
- Explicit mark-to-market portfolio engine concept already exists.
- Strong fail-loud delivery discipline.
- A safe lab surface exists for testing tooling without changing `daily-fx` first.
- A lab-only QuantStats diagnostics layer exists for portfolio QA.
- A lab-only vectorbt rule sandbox exists for portfolio-level overlay exploration.
- FX carry is now visible via `output/fx_carry_snapshot.csv`.
- True macro concentration is now visible via `output/fx_risk_bucket_snapshot.json`.
- Future reports are hardened by `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`.
- The send workflow now includes pre-send alpha-discipline validation through `tools/validate_fx_action_discipline.py`.

## Current weaknesses

### 1. Prompt monolith still exists
Even though FX is more mature than ETF on explicit state, the prompt still mixes:
- strategy logic
- state authority rules
- technical overlay handling
- valuation logic
- output rules
- workflow orchestration
- delivery completion logic

The new alpha-discipline layer is currently implemented as an addendum rather than a full split of the monolith. That is safer, but the longer-term direction is still to separate the decision framework, input/state contract, output contract, and runbook more cleanly.

### 2. Carry source is still a proxy
The carry layer currently uses policy-rate proxy inputs in `config/fx_policy_rate_proxies.json`.

This is useful for visibility and discipline, but it is not the same as actual broker rollover, tom-next, or forward-point carry. Future work should replace or supplement the proxy with a more direct carry source when available.

### 3. Authority rules need to stay visible
FX now has more explicit state files than before, but that only helps if future sessions can quickly see:
- which file is authoritative for implementation facts
- which file is authoritative for strategy intent
- which files are estimated carry/risk diagnostics
- what happens if these disagree

### 4. Lab / production boundary remains important
`weekly-fx` is still a lab/safe experimentation repo. Changes should not be assumed production-approved for `daily-fx` until tested and intentionally promoted.

## Target architecture

### ChatGPT side
- One dedicated ChatGPT Project called **FX Review OS**.
- Project instructions that reinforce the operating model.
- Minimal stable bootstrap context in the ChatGPT Project, with GitHub as the live source of truth for changing prompt, script, workflow, output, and state files.

### GitHub side
- GitHub remains the source of truth for prompt, scripts, workflows, outputs, and control docs.
- Existing FX state files remain part of the operating core.
- The control layer reduces restart friction and architecture drift.
- `weekly-fx` remains the experimentation surface for tool integrations before production promotion.
- Carry and risk-bucket snapshots are now part of the input/state contract.

### Delivery side
- Delivery remains in `send_fxreport.py` plus GitHub Actions.
- The prompt keeps decision standards and output requirements, while scripts/workflows own more execution discipline.
- The send workflow now gates client-facing delivery on alpha-discipline validation.

## Immediate priorities

### Priority A — validate the alpha-discipline layer
Completed in this step:
- add `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`
- add `config/fx_policy_rate_proxies.json`
- add `output/fx_carry_snapshot.csv`
- add `output/fx_risk_bucket_snapshot.json`
- add `tools/write_fx_carry_and_risk_snapshots.py`
- add `tools/apply_fx_carry_accrual.py`
- add `tools/validate_fx_action_discipline.py`
- update refresh/send workflows to generate and validate the new artifacts

Planned next:
- generate the next FX report with the new required blocks
- verify the send workflow fails loud if the blocks are missing
- verify the send workflow passes once the new report includes the blocks

### Priority B — validate carry quality
Planned next:
- compare policy-rate proxy carry with any available broker rollover, forward points, or tom-next data
- avoid presenting proxy carry as guaranteed realized carry
- decide whether carry should remain a report estimate or become full NAV accrual in production

### Priority C — continue lab analytics validation
Planned next:
- compare QuantStats diagnostics against Section 7 / `fx_valuation_history.csv`
- inspect vectorbt sandbox results for signal quality, overfitting risk, and practical relevance
- keep lab-only analytics out of client-facing delivery unless explicitly promoted

### Priority D — make FX boundaries more explicit
Still planned:
- extract the state/input contract more cleanly from `fx.txt`
- extract the output contract more cleanly from `fx.txt`
- reduce unnecessary runbook logic inside the prompt where scripts are better owners

## Recommended session start sequence

For any future weekly-fx architecture or integration session:
1. read `control/SYSTEM_INDEX.md`
2. read this file
3. read `control/NEXT_ACTIONS.md`
4. only then open the specific execution file relevant to the task

## Current role split

### Manual by user
- keep production `daily-fx` protected until lab changes are validated
- decide when the alpha-discipline layer is ready for production promotion
- provide broker rollover / forward-point data if available

### Can be done by assistant
- update GitHub control files
- refactor prompts
- review and improve scripts/workflows
- strengthen state authority rules
- generate test reports using the new alpha-discipline requirements
- inspect workflow failures and delivery receipts
- prepare promotion PRs from weekly-fx to daily-fx when approved

## Current status label

**FX alpha-discipline layer implemented in weekly-fx — carry visibility, USD cash contradiction checks, risk-bucket exposure, carry-accrual scaffolding, and pre-send validation now exist in the lab repo. Next step is to generate a fresh report that satisfies the new required blocks and verify the workflow gate.**
