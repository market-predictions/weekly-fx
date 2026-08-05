# FX Review OS — Project Bootstrap

## Purpose
This is the **one file** you should upload into the ChatGPT Project `FX Review OS` as the stable project bootstrap.

Do **not** treat this file as the operational source of truth.
Its job is to point each session to the correct live files in GitHub.

## Core rule
- **ChatGPT Project** = working memory and workbench
- **GitHub** = live source of truth

That means:
- use this bootstrap file as the fixed starting context inside the ChatGPT Project
- use GitHub to read the current control files, state files, and execution files live
- avoid uploading changing repo files unless there is a specific reason

## First read sequence for meaningful FX work
At the start of any serious FX architecture, debugging, prompt, state, release, promotion, or delivery session:

1. read `control/SYSTEM_INDEX.md` from GitHub
2. read `control/CURRENT_STATE.md` from GitHub
3. read `control/NEXT_ACTIONS.md` from GitHub
4. read `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` for consequential work
5. only then read the minimum relevant execution file(s)

## Separation of duties

The project uses one user-facing coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

The user gives one instruction and receives one consolidated status. The user does not separately coordinate the two roles.

Implementation prepares the candidate. Governance independently reconstructs and certifies or rejects it. Implementation may not certify its own completion. Governance may not silently modify the candidate it reviews. A repaired candidate receives a new assurance pass.

The shared standard, lab boundary, local risk class, adoption maturity, and required evidence are linked from `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`.

## Lab and production boundary

`weekly-fx` remains the lab/safe experimentation repository. `daily-fx` remains protected production.

A passing lab test or assurance record does not automatically grant production authority. Production promotion requires a separate governed candidate, explicit promotion scope, safe recipient/secret handling, and a new assurance pass.

## Which execution files to read by task
### Prompt architecture / report logic / macro decision framework
- `fx.txt`
- `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`

### Explicit state / valuation / overlay / carry questions
- `output/fx_portfolio_state.json`
- `output/fx_trade_ledger.csv`
- `output/fx_valuation_history.csv`
- `output/fx_recommendation_scorecard.csv`
- `output/fx_technical_overlay.json`
- `output/fx_carry_snapshot.csv`
- `output/fx_risk_bucket_snapshot.json`

### Rendering / PDF / email / manifest / delivery
- `send_fxreport.py`

### Workflow / secrets / orchestration
- `.github/workflows/send-weekly-report.yml`

### Historical continuity / prior artifact review
- latest relevant file in `output/`

## Important architecture rule
The project should not silently become overloaded with state snapshots or technical files.

So:
- do **not** upload `fx.txt` as default project context for now
- do **not** upload changing state files as standard project files unless there is a specific task-driven need
- treat these files as **live GitHub sources** and fetch them when needed

## Required distinctions
Always keep these five layers separate in reasoning and recommendations:
1. decision framework
2. input/state contract
3. output contract
4. operational runbook
5. governance and release assurance

## Quality rules
- Preserve the explicit state-file model.
- Treat technical overlay as confirmation, not as the whole decision engine.
- Label stale inputs clearly.
- Prefer minimal, precise, non-destructive changes.
- Treat GitHub as the current truth when project context and repo content differ.
- Treat generated output as a release candidate until the required assurance pass exists.
- Do not claim delivery succeeded without a real receipt or manifest from the delivery layer.
- Report action execution separately from independently confirmed outcome.

## Minimal upload strategy for the ChatGPT Project
Recommended default upload set:
- this file only: `control/PROJECT_BOOTSTRAP.md`

Optional later additions only if there is a real need:
- a compact glossary
- a short naming-conventions file
- a future split-out FX contract file after refactoring

## Session close rule
At the end of a meaningful FX session, check whether GitHub should be updated in:
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- project governance, assurance, and promotion files

## One-line reminder
**Upload this file to the ChatGPT Project; read the rest live from GitHub.**