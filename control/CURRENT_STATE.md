# FX Review OS — Current State

## Snapshot

```text
date=2026-08-07
repository=market-predictions/weekly-fx
role=NON_PRODUCTION_LAB
portfolio_control_mode=VALIDATION
canonical_shared_control=market-predictions/control-plane
shared_controller=portfolio_control
project_governance_maturity=LEVEL_3_LAB_ENFORCED
production_target=market-predictions/daily-fx
production_promotion_from_this_repo=FAIL_CLOSED
```

## What this repository currently is

`weekly-fx` is the **non-production FX lab and validation repository**. It is the safe experimentation surface for report logic, state handling, alpha-discipline, technical overlays, diagnostics and candidate promotion preparation.

It must not be treated as production `daily-fx`, and it cannot certify its own production promotion.

The current cross-project operating architecture is:

```text
principal
  |
  v
portfolio_control
  |-- implementation_operations
  `-- governance_release_assurance
```

For this project, `portfolio_control` reconstructs state, protects scope, routes ordinary technical work and consolidates status. The LEVEL 3 project assurance contract remains independently authoritative for candidate assurance. Production promotion requires a target-repository candidate and target-repository assurance in `daily-fx`.

## Current operating strengths

- Strong deterministic and anti-drift framing.
- Explicit lab-versus-production boundary.
- LEVEL 3 lab release-assurance gate with fail-closed production-promotion semantics.
- Client-grade report presentation contract.
- Explicit state-file and technical-overlay handling.
- Mark-to-market portfolio engine concept.
- Alpha-discipline layer covering carry visibility, USD cash discipline, risk buckets and no-action proof.
- Pre-send alpha-discipline validation in the lab workflow.
- Repo-native state-refresh path and automatic technical-overlay refresh.
- QuantStats/vectorbt experimentation remains separated from client-facing authority.

## Current evidence and live state

Latest observed `main` at this reconciliation:

```text
main_sha=3f25ff6a0cb24187655f3b052f764b0377836ff7
latest_change=Update FX technical overlay [skip ci]
latest_change_time_utc=2026-08-07T07:36:55Z
```

The technical overlay is therefore live operational input that may refresh without implying report completion, release approval or production promotion.

The current governance baseline is later and more authoritative than the May-era narrative previously held in this file:

- `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` points to the canonical private control plane;
- `control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md` defines the LEVEL 3 lab assurance boundary;
- `weekly-fx` cannot issue production-promotion PASS;
- any promotion to `daily-fx` requires independent target-repository assurance there.

## Current weaknesses / open validation work

### 1. Fresh compliant report validation still matters

The alpha-discipline implementation exists, but the lab still needs evidence from a fresh compliant report showing that the required carry, USD-cash, risk-bucket and no-action blocks are correctly produced and validated.

### 2. Carry remains a proxy unless better evidence is supplied

`config/fx_policy_rate_proxies.json` is useful for estimated carry discipline but is not broker rollover, tom-next or forward-point carry. It must not be represented as realized carry.

### 3. Prompt/state/runbook responsibilities remain partly monolithic

The longer-term architecture should keep decision framework, input/state contract, output contract, operational runbook and governance/release assurance distinct. Refactoring is a maturity improvement, not a prerequisite for every lab cycle.

### 4. Lab analytics remain non-production evidence

QuantStats/vectorbt outputs are exploratory diagnostics. They do not acquire client-facing or production authority merely because a lab run succeeds.

## Current controller objective

```text
objective=VALIDATE_LEVEL_3_LAB_REPORT_PATH_WITHOUT_CROSSING_DAILY_FX_PRODUCTION_BOUNDARY
principal_decision_required_now=false
```

The controller should autonomously:

1. keep state and governance records synchronized;
2. generate/validate bounded lab evidence when appropriate;
3. distinguish state-refresh activity from report/release completion;
4. route implementation work below principal level;
5. require independent lab assurance for consequential candidate changes;
6. escalate production promotion only when a concrete `daily-fx` target candidate and target assurance make the decision actionable.

## Authority boundary

The following remain outside routine controller authority unless the applicable project contract explicitly permits them:

- client-facing production delivery from the lab;
- production promotion to `daily-fx`;
- weakening the LEVEL 3 assurance gate;
- representing proxy carry as realized broker carry;
- any irreversible external action reserved to the principal or production repository.

## Recommended session start

The canonical project prompt invocation is sufficient:

```text
Start this assignment by reading and applying the canonical project operating method in `market-predictions/control-plane`.
```

Because `weekly-fx` is enrolled in the reporting-family portfolio-control pilot, the shared control plane supplies portfolio state and controller routing before project-local implementation work begins.

## Current status label

**Weekly FX is a LEVEL 3 non-production validation lab under portfolio control. The immediate work is fresh compliant-report validation and state/architecture hardening; no principal decision or production promotion is currently actionable.**
