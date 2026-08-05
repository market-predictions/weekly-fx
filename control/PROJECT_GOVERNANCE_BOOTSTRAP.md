# Weekly FX — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=CANONICAL_ACTIVE
project_repository=market-predictions/weekly-fx
project_risk_class=financial_strategy_lab_with_optional_delivery
adoption_status=documented
enforcement_maturity=LEVEL_1_CHECKLIST
target_enforcement_maturity=LEVEL_3_HARD_CI_GATE_FOR_LAB_AND_LEVEL_4_FOR_PRODUCTION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=PLANNED
production_action=lab_report_generation_and_optional_test_delivery
post_action_confirmation=lab_manifest_or_test_receipt; production_requires_independent_receipt
```

## User interface

The user gives one FX project instruction and receives one consolidated project status. The user does not separately coordinate implementation and assurance roles.

## Lab and production boundary

`weekly-fx` remains a lab-first repository. Governance adoption must preserve that boundary:

- lab evidence does not become `daily-fx` production authority automatically;
- lab delivery must use safe recipients or disabled/test transport;
- production promotion requires a separate governed candidate and assurance pass in the protected production repository.

## Current adoption boundary

This file documents role separation and status semantics. It does not yet claim a machine-generated independent assurance record or hard pre-send gate.

The planned `control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md` should independently verify at least:

- source SHA, requested close, report token, and run identity;
- portfolio state, trade ledger, valuation history, technical overlay, carry snapshot, and risk-bucket freshness;
- strategy intent versus implementation-state consistency;
- no look-ahead or stale-overlay substitution;
- required carry, USD-cash contradiction, risk-bucket, and no-action blocks;
- report and rendered-artifact hashes;
- lab/production recipient and secret boundary;
- manifest or receiving-system evidence appropriate to the environment;
- separate promotion authority before `daily-fx` production use.

## Session read rule

For production promotion, delivery, state mutation, or completion claims, read this file after:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`

Then read the minimum relevant execution and assurance files.

## Prompt invocation

```text
Apply the project's implementation-versus-release-assurance separation. Treat all generated output as a release candidate until independent assurance passes. Do not let implementation certify its own completion. Report action execution separately from independently confirmed outcome.
```
