# FX Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 0 — keep the lab clone role explicit

### 0. Treat `weekly-fx` as lab-first, not production-first
- Owner: `[JOINT]`
- Action:
  - use `weekly-fx` for tool integration, diagnostics, workflow experiments, and alpha-discipline hardening first
  - keep `daily-fx` protected as the production repo until changes are validated
- Done when: lab-only changes are documented and not confused with production behavior.

### 0A. Keep lab delivery settings safe
- Owner: `[USER]`
- Action:
  - do **not** copy production mail recipients and delivery secrets blindly into `weekly-fx`
  - prefer test recipients, disabled send settings, or separate lab mail credentials
- Done when: lab workflows cannot accidentally send client-facing reports.

---

## Phase 1 — establish the working environment

### 1. Create / maintain the ChatGPT Project
- Owner: `[USER]`
- Action: keep the ChatGPT Project named **FX Review OS** available as the recurring workbench.
- Done when: the project exists and future work uses the live GitHub files as source of truth.

### 2. Keep project instructions aligned
- Owner: `[USER]`
- Source file: `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- Action: keep Project settings aligned with the repo operating model.
- Done when: the FX project has its own instructions separate from global custom instructions.

### 3. Use the lean bootstrap upload model
- Owner: `[USER]`
- Primary upload:
  - `control/PROJECT_BOOTSTRAP.md`
- Action:
  - upload only the bootstrap file as the default stable project context
  - do **not** upload changing repo files as standard project context unless there is a specific task-driven need
- Done when: future sessions read the live repo files from GitHub instead of relying on stale uploaded copies.

---

## Phase 2 — make state authority obvious and durable

### 4. Keep using the control layer at the start of each FX session
- Owner: `[JOINT]`
- Action: every meaningful FX architecture, debugging, prompt, state, workflow, or delivery session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer need to rediscover how the system is organized.

### 5. Keep the four-layer model explicit
- Owner: `[ASSISTANT]`
- Action: preserve and reinforce the separation between:
  1. decision framework
  2. input/state contract
  3. output contract
  4. operational runbook
- Done when: future changes and reviews are consistently framed against these four layers.

### 6. Validate stale-data handling
- Owner: `[ASSISTANT]`
- Action: review handling of:
  - stale technical overlay files
  - stale valuation data
  - stale portfolio values
  - stale carry snapshots
  - stale risk-bucket snapshots
  - stale report artifacts
- Done when: stale inputs cannot silently flatten, distort, or misstate the portfolio or report.

### 6A. Keep the repo-native refresh trigger path authoritative
- Owner: `[ASSISTANT]`
- Action:
  - use `control/run_queue/` as the fallback trigger surface when ChatGPT cannot dispatch GitHub Actions directly
  - keep `.github/workflows/prep-from-trigger.yml` as the queue bridge
  - keep `.github/workflows/refresh-fx-state.yml` as the canonical refresh workflow
  - verify that ChatGPT still checks workflow success plus refreshed files on `main` before continuing
- Done when: the prep-first flow works through either direct dispatch or a committed trigger file without changing the verification standard.

---

## Phase 3 — validate the FX alpha-discipline layer

### 7. Generate the next report with required alpha blocks
- Owner: `[ASSISTANT]`
- Action:
  - read `fx.txt`
  - read `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`
  - use `output/fx_carry_snapshot.csv`
  - use `output/fx_risk_bucket_snapshot.json`
  - include the required blocks:
    - `FX carry dashboard`
    - `USD cash contradiction check`
    - `Risk-bucket exposure`
    - `No-action override table` if no rebalance occurs
- Done when: the next report passes `tools/validate_fx_action_discipline.py`.

### 8. Verify the pre-send validator fails loud when blocks are missing
- Owner: `[ASSISTANT]`
- Action:
  - intentionally inspect the latest pre-alpha report or a test report without required blocks
  - confirm `tools/validate_fx_action_discipline.py` rejects it
- Done when: missing carry/cash/risk/no-action blocks cannot pass send validation.

### 9. Verify the send workflow with a compliant report
- Owner: `[JOINT]`
- Action:
  - publish a fresh compliant report
  - inspect the GitHub Actions run
  - verify state refresh, carry accrual, carry/risk snapshot generation, alpha validation, render validation, email send, and artifact persistence
- Done when: a compliant report has a real delivery receipt or failure reason.

### 10. Improve carry quality beyond policy-rate proxy
- Owner: `[JOINT]`
- Action:
  - compare `config/fx_policy_rate_proxies.json` against broker rollover, tom-next, or forward-point data if available
  - decide whether to keep proxy carry as an estimate or replace it with a direct carry source
- Done when: the report clearly distinguishes estimated carry from realized/broker carry.

---

## Phase 4 — continue lab analytics validation

### 11. Run the QuantStats diagnostics workflow
- Owner: `[JOINT]`
- Action:
  - use `.github/workflows/lab-quantstats-diagnostics.yml` manually
  - inspect the generated artifact bundle from `lab_outputs/quantstats/`
  - compare the diagnostics to Section 7 and to `output/fx_valuation_history.csv`
- Done when: the lab diagnostics layer is validated as a useful QA aid.

### 12. Run the vectorbt rule sandbox workflow
- Owner: `[JOINT]`
- Action:
  - use `.github/workflows/lab-vectorbt-rule-sandbox.yml` manually
  - inspect the generated artifact bundle from `lab_outputs/vectorbt/`
  - compare the top sandbox rules against baseline hold
  - assess whether any result is likely short-history noise rather than a durable signal
- Done when: the vectorbt sandbox is validated as useful exploration rather than premature production logic.

### 13. Re-run the sleeve-level vectorbt sandbox with activity separation
- Owner: `[JOINT]`
- Action:
  - use `.github/workflows/lab-vectorbt-sleeve-sandbox.yml` manually
  - inspect `fx_sleeve_vectorbt_best_active_by_sleeve.csv` and `fx_sleeve_vectorbt_best_inactive_by_sleeve.csv`
  - verify that no-trade / low-exposure rules no longer masquerade as active winners
- Done when: sleeve-level results are interpretable without conflating active improvement and defensive inactivity.

---

## Phase 5 — tighten boundaries without changing behavior

### 14. Extract the state/input contract more explicitly from production logic
- Owner: `[ASSISTANT]`
- Action:
  - clarify what is authoritative for implementation facts
  - clarify what is authoritative for strategy intent
  - clarify what is diagnostic/proxy input
  - clarify deterministic conflict resolution between the files
- Done when: the state model can be understood without rereading the whole monolith.

### 15. Review `send_fxreport.py` against the new architecture
- Owner: `[ASSISTANT]`
- Action: identify which responsibilities belong in the script and which should stop living in the prompt.
- Focus areas:
  - manifest/receipt logic
  - HTML/PDF rendering
  - equity-curve handling
  - stale-report detection
  - portfolio-valuation refresh logic
  - carry/risk artifact display support

### 16. Review the GitHub Actions workflow
- Owner: `[ASSISTANT]`
- Action: confirm that workflow responsibilities stay limited to orchestration, secrets, execution, validation, and delivery.
- Done when: workflow logic is clearly operational, not decision-making.

---

## Suggested immediate next move

The best next move after this update is:
1. generate a fresh Weekly FX Review that obeys `FX_ALPHA_DISCIPLINE_ADDENDUM.md`
2. confirm it includes carry, USD-cash contradiction, risk-bucket, and no-action proof blocks
3. let the send workflow validate it
4. only after a clean lab run, decide whether to promote the alpha-discipline layer to `daily-fx`

---

## Current checkpoint

**FX alpha-discipline layer implemented in weekly-fx — carry visibility, USD cash contradiction checks, true risk-bucket exposure, carry-accrual scaffolding, and pre-send validation now exist. Next step is to generate and validate a compliant fresh report.**
