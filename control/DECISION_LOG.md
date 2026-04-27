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
QuantStats offers a fast way to generate portfolio tear sheets and diagnostic analytics from the existing valuation history without modifying the client-facing Weekly FX Review flow. Its current package documentation shows support for generating a complete HTML report with `qs.reports.html(...)`, and the current release supports Python 3.10+ environments. citeturn581380search1turn581380search0

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
vectorbt is designed for fast, vectorized strategy research and portfolio backtesting on pandas/NumPy objects, and its current documentation and package metadata position it as a modern backtesting stack for rapid experimentation on Python 3.10+ environments. The right use here is not to replace the FX methodology, but to create a safe sandbox for testing whether simple portfolio-level trend and drawdown overlays would have materially changed the tracked model-portfolio path. ([vectorbt.dev](https://vectorbt.dev/?utm_source=chatgpt.com), [pypi.org](https://pypi.org/project/vectorbt/?utm_source=chatgpt.com))

### Consequence
- the vectorbt workflow is manual and artifact-only
- it does not send client email
- it does not replace the production FX decision framework
- it treats the tracked portfolio NAV path as a **research proxy**, not as a tradable production signal source
- any apparent outperformance must be treated first as a hypothesis and checked for short-history noise or overfitting before any production promotion
