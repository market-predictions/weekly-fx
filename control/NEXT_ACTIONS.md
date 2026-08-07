# FX Review OS — Next Actions

## Control mode

```text
date=2026-08-07
portfolio_control_mode=VALIDATION
principal_decision_required_now=false
production_repo=market-predictions/daily-fx
```

The reporting-family `portfolio_control` agent owns routine coordination. The principal should not be asked to direct separate implementation and assurance agents or repeat repository context.

## P1 — validate a fresh compliant lab report

Owner: `portfolio_control -> implementation_operations`, followed by independent `governance_release_assurance` where required.

1. Start from the canonical control-plane invocation and current live state.
2. Generate a fresh **lab** Weekly FX report that obeys `prompts/FX_ALPHA_DISCIPLINE_ADDENDUM.md`.
3. Require the report to include the applicable:
   - FX carry dashboard;
   - USD cash contradiction check;
   - risk-bucket exposure;
   - no-action override table when no rebalance occurs.
4. Validate with `tools/validate_fx_action_discipline.py` and the existing render/report gates.
5. Keep any delivery in the safe lab contract; do not infer client-facing production authority.
6. Record exact evidence and failure reason rather than claiming completion from report generation alone.

Done when a fresh compliant lab candidate has independently interpretable pass/fail evidence.

## P2 — preserve fail-closed lab / production separation

Owner: `portfolio_control` and `governance_release_assurance`.

1. Preserve `weekly-fx` as non-production.
2. Do not let a successful lab run issue production-promotion PASS.
3. If a future promotion is warranted, prepare a concrete `daily-fx` target candidate.
4. Require independent target-repository assurance in `daily-fx` before any promotion can be represented as approved.
5. Escalate to the principal only when the target candidate and evidence make a consequential choice actionable.

## P3 — improve carry evidence without overstating it

Owner: `implementation_operations`.

1. Continue to label policy-rate proxy carry as estimated/proxy carry.
2. Compare with broker rollover, tom-next or forward-point data only when a reliable source is available.
3. Do not block ordinary lab report validation merely because direct broker carry is not yet available, unless the report would otherwise misstate the value.
4. Treat production NAV accrual based on a stronger carry source as a separate promotion decision.

## P4 — continue bounded analytics validation

Owner: `implementation_operations`.

- QuantStats and vectorbt remain lab diagnostics.
- Run them when they answer a defined validation question.
- Separate active strategy improvement from inactivity/no-trade effects.
- Archive weak or noisy findings rather than automatically promoting them into report logic.
- No principal interruption is required for ordinary lab experimentation.

## P5 — architecture hardening when justified by active work

Owner: `portfolio_control`.

Continue separating:

1. decision framework;
2. input/state contract;
3. output contract;
4. operational runbook;
5. governance/release assurance.

Do not create refactoring work merely for architectural neatness. Prefer changes that remove an observed ambiguity, recurrent failure or release risk.

## State-refresh discipline

The automatic technical-overlay refresh on `main` is operational input maintenance only.

A refresh commit does **not** mean:

- a new Weekly FX report exists;
- the report has passed assurance;
- the report has been sent;
- production has been promoted;
- the principal needs to decide anything.

The controller should keep those states separate in every brief.

## Principal escalation rule

Escalate only if all are true:

1. a genuine unresolved choice remains;
2. existing policy, evidence, safe defaults and reversible lab work cannot responsibly resolve it;
3. the consequence is material; and
4. the principal can act on the decision now.

Likely future principal item: production promotion after a concrete `daily-fx` candidate and independent target assurance exist. Until then it is **not** an actionable decision.

## Current next gate

```text
NEXT_GATE=FRESH_COMPLIANT_WEEKLY_FX_LAB_REPORT_VALIDATION
OWNER=PORTFOLIO_CONTROL
PRINCIPAL_ACTION=NONE
```
