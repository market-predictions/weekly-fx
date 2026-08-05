# Decision — Adopt Two-Role Governance for Weekly FX

## Date

2026-08-05

## Decision

Adopt `CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1` for consequential Weekly FX lab work and any later production-promotion package.

The user continues to issue one instruction. Internally:

- `implementation_operations` prepares the candidate;
- `governance_release_assurance` independently reconstructs and certifies or rejects it.

Implementation cannot certify its own completion. Governance cannot silently modify the candidate it reviews.

## Current maturity

```text
current=LEVEL_1_CHECKLIST
target_lab=LEVEL_3_HARD_CI_GATE
target_production=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
```

## Lab boundary

A passing Weekly FX lab assurance record is not production authority for `daily-fx`. Promotion requires a separate candidate, explicit promotion scope, protected recipient/secret handling, and a new assurance pass.

## Required follow-up

Create `control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md`, machine-readable assurance evidence, and a hard lab gate before optional test delivery. Add LEVEL_4 receiving-system confirmation only to the protected production path.

## Authority boundary

This decision does not authorize report generation, state mutation, workflow dispatch, production promotion, or email delivery.
