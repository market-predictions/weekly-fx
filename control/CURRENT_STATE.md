# FX Review OS — Current State

## Snapshot date
2026-04-27

## What this repository currently is

This repository is now the **non-production lab clone** of the original FX production system.

It contains:
- the mirrored FX production prompt and workflow files from `daily-fx`
- the existing archived outputs and explicit state artifacts in `output/`
- the same technical overlay and mark-to-market portfolio engine concept used by production
- a growing **lab-only analytics and rule-testing layer** for non-destructive QA and tool evaluation

## Current strengths

- Strong determinism and anti-drift framing.
- Clear client-grade presentation contract.
- Explicit state-file awareness already exists.
- Explicit technical-overlay contract already exists.
- Explicit mark-to-market portfolio engine concept already exists.
- Strong fail-loud delivery discipline.
- A safe lab surface now exists for testing tooling without changing `daily-fx` first.
- A first lab-only QuantStats diagnostics layer now exists for portfolio QA.
- A first lab-only vectorbt rule sandbox now exists for portfolio-level overlay exploration.

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

### 2. Lab / production boundaries were previously implicit
Before the clone-and-lab setup, new tooling would have had to compete directly with the production repo.
The weekly lab repos reduce that risk, but they now need to keep their lab role explicit.

### 3. Authority rules need to stay visible
FX already has more explicit state files than ETF, but that only helps if future sessions can quickly see:
- which file is authoritative for implementation facts
- which file is authoritative for strategy intent
- what happens if those disagree

### 4. ChatGPT Project layer still has to be created manually
The repo side can now be structured, but the actual recurring ChatGPT workspace is not created automatically by the repository.

## Target architecture

### ChatGPT side
- One dedicated ChatGPT Project called **FX Review OS**.
- Project instructions that reinforce the operating model.
- Minimal stable bootstrap context in the ChatGPT Project, with GitHub as the live source of truth for changing prompt, script, workflow, output, and state files.

### GitHub side
- GitHub remains the source of truth for prompt, scripts, workflows, outputs, and control docs.
- Existing FX state files remain part of the operating core.
- The control layer reduces restart friction and architecture drift.
- `weekly-fx` is the first experimentation surface for tool integrations before production promotion.

### Delivery side
- Delivery remains in `send_fxreport.py` plus GitHub Actions.
- The prompt keeps decision standards and output requirements, but should gradually stop being the only runbook.
- Lab analytics and sandbox layers must remain separate from production email delivery until explicitly validated.

## Immediate priorities

### Priority A — keep the lab clone role explicit
Completed in this step:
- establish `weekly-fx` as the safe experimentation surface
- preserve the mirrored production files
- begin documenting lab-only additions explicitly in control files

### Priority B — validate the new QuantStats diagnostics layer
Completed in this step:
- add a standalone QuantStats diagnostics script
- add a manual GitHub Actions workflow that generates diagnostics artifacts only
- keep diagnostics separate from the client-facing report and email flow

### Priority C — validate the new vectorbt sandbox layer
Completed in this step:
- add a standalone vectorbt rule sandbox script
- add a manual GitHub Actions workflow that generates sandbox artifacts only
- keep the sandbox separate from production strategy and delivery logic

### Priority D — compare lab outputs against current state and report behavior
Planned next:
- compare QuantStats diagnostics against Section 7 / `fx_valuation_history.csv`
- inspect the vectorbt sandbox results for signal quality, overfitting risk, and practical relevance
- decide which outputs are useful for internal QA only
- avoid leaking lab-only analytics into production presentation before validation

### Priority E — make the FX layer boundaries more explicit
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
- create the ChatGPT Project
- paste project instructions
- upload `control/PROJECT_BOOTSTRAP.md` as the default project context
- set lab-safe GitHub secrets/variables where needed
- decide when a lab change is ready to be promoted to production

### Can be done by assistant
- design the project instructions
- design the GPT spec
- create and update GitHub control files
- refactor prompts
- propose or write repo files
- review and improve scripts/workflows
- strengthen state authority rules
- add lab-only diagnostics and QA tooling
- add lab-only rule-testing sandboxes

## Current status label

**Lab clone established — weekly-fx now mirrors the FX production system and includes both a lab-only QuantStats diagnostics layer and a lab-only vectorbt rule sandbox, while production remains protected in `daily-fx`.**
