## 2026-03-28 — ChatGPT Project context model: bootstrap-first, GitHub-live

### Decision
The ChatGPT Project should use a **lean bootstrap-first context model**:
- keep only stable bootstrap context in the Project by default
- treat GitHub as the live source of truth for changing prompt, script, workflow, output, and state files
- only upload additional files to the Project when a specific task clearly benefits from it

### Why
Uploading multiple changing repo files as standard Project context increases the risk of drift between Project memory and actual repo state.
The operating model should keep the ChatGPT Project lean and make GitHub authoritative for live execution context.

### Consequence
- `control/CURRENT_STATE.md` should describe the Project as bootstrap-first, not as a place for a standing set of changing files
- `control/NEXT_ACTIONS.md` should instruct the user to upload `control/PROJECT_BOOTSTRAP.md` as the default Project context
- future FX sessions should read control files first and then open the minimum relevant live repo files from GitHub

---

## 2026-04-27 — weekly-fx is the lab clone for non-destructive FX tooling changes

### Decision
`weekly-fx` should act as the **non-production experimentation surface** for FX tooling, diagnostics, and workflow improvements.

The protected production repo remains `daily-fx` until lab changes are validated and intentionally promoted.

### Why
New tooling such as analytics, optimization, and diagnostics should not be integrated directly into the live production repo before validation.

The clone-first model preserves:
- production stability
- delivery safety
- deterministic comparison against the existing production workflow

### Consequence
- control files in `weekly-fx` must explicitly describe the repo as lab-first
- lab-only additions must not be presented as production-approved by default
- production delivery credentials should not be copied blindly into the lab repo

---

## 2026-04-27 — first lab analytics integration: manual QuantStats diagnostics layer

### Decision
The first lab-only tooling integration in `weekly-fx` is a **manual QuantStats diagnostics layer**.

It consists of:
- `tools/generate_quantstats_diagnostics.py`
- `.github/workflows/lab-quantstats-diagnostics.yml`
- `docs/QUANTSTATS_LAB_DIAGNOSTICS.md`

### Why
QuantStats offers a fast way to generate portfolio tear sheets and diagnostic analytics from the existing valuation history without modifying the client-facing Weekly FX Review flow.

### Consequence
- the new diagnostics workflow is manual and artifact-only
- it does not replace Section 7
- it does not send client email
- it is intended first for QA and internal comparison against `fx_valuation_history.csv`
- only after validation should any insight from this layer be considered for production promotion

---

## 2026-04-27 — second lab analytics integration: manual vectorbt rule sandbox

### Decision
The next lab-only tooling integration in `weekly-fx` is a **manual vectorbt rule sandbox**.

It consists of:
- `tools/generate_vectorbt_rule_sandbox.py`
- `.github/workflows/lab-vectorbt-rule-sandbox.yml`
- `docs/VECTORBT_LAB_RULE_SANDBOX.md`

### Why
The right use is not to replace the FX methodology, but to create a safe sandbox for testing whether simple portfolio-level trend and drawdown overlays would have materially changed the tracked model-portfolio path.

### Consequence
- the vectorbt workflow is manual and artifact-only
- it does not send client email
- it does not replace the production FX decision framework
- it treats the tracked portfolio NAV path as a **research proxy**, not as a tradable production signal source
- any apparent outperformance must be treated first as a hypothesis and checked for short-history noise or overfitting before any production promotion

---

## 2026-05-05 — FX alpha-discipline layer: carry, cash discipline, true risk buckets, and no-action proof

### Decision
`weekly-fx` now adds an explicit **FX alpha-discipline layer** on top of the existing monolithic `fx.txt` prompt.

The layer is implemented through:
- `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`
- `config/fx_policy_rate_proxies.json`
- `output/fx_carry_snapshot.csv`
- `output/fx_risk_bucket_snapshot.json`
- `tools/fx_carry_utils.py`
- `tools/write_fx_carry_and_risk_snapshots.py`
- `tools/apply_fx_carry_accrual.py`
- `tools/validate_fx_action_discipline.py`
- updates to `.github/workflows/send-weekly-report.yml`
- updates to `.github/workflows/refresh-fx-state.yml`
- updates to `fx_refresh_all_state.py`

### Why
A USD-base unlevered spot FX portfolio has two direct return sources: spot price movement and carry. The prior report framework discussed carry and USD de-crowding qualitatively, but did not force visible carry accounting, USD cash contradiction checks, true macro exposure buckets, or proof for non-action.

The new layer is designed to prevent:
- calling a sleeve a carry opportunity without showing estimated carry
- saying `Reduce USD` while leaving excess USD cash unexplained
- mistaking several correlated risk-on currencies for true diversification
- letting `Reduce` remain a sentiment label instead of an execution label
- saying no rebalance occurred without a no-action proof table

### Consequence
Future compliant Weekly FX Reviews must include compact blocks labelled:
- `FX carry dashboard`
- `USD cash contradiction check`
- `Risk-bucket exposure`
- `No-action override table` when no rebalance occurs

The send workflow should now fail before render/send when those requirements are missing.

Carry is currently estimated through policy-rate proxies, not broker rollover or forward points. That distinction must stay visible until a better carry source is connected.

The next validation step is to generate a fresh compliant report and confirm the workflow gate passes only when the new blocks are present.
