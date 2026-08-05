# Weekly FX — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=CANONICAL_ACTIVE
project_repository=market-predictions/weekly-fx
project_risk_class=financial_strategy_lab_with_optional_delivery
adoption_status=enforced
enforcement_maturity=LEVEL_3_HARD_CI_GATE
target_enforcement_maturity=LEVEL_3_HARD_CI_GATE_FOR_LAB_AND_LEVEL_4_FOR_PRODUCTION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=ENFORCED
production_promotion_contract=control/FX_PRODUCTION_PROMOTION_ASSURANCE_CONTRACT_V1.md
production_promotion_contract_status=ENFORCED_FAIL_CLOSED_BOUNDARY
production_action=lab_report_generation_and_optional_test_delivery
post_action_confirmation=lab_manifest_or_test_receipt; production_requires_independent_receipt
```

## User interface

The user gives one FX project instruction and receives one consolidated project status. The user does not separately coordinate implementation and assurance roles.

## Enforced lab gate

The lab delivery entrypoint now renders the exact candidate assets, reconstructs the release from refreshed state, alpha-discipline evidence and artifact hashes, and requires governance `PASS` before SMTP transport.

The gate verifies:

- source SHA, workflow run and exact report identity;
- state-refresh completeness and same-date portfolio consistency;
- trade ledger, valuation history and recommendation scorecard;
- technical overlay, carry snapshot and risk-bucket snapshot;
- all 17 report sections;
- carry, USD-cash contradiction and risk-bucket surfaces;
- no-action proof where applicable;
- cleaned Markdown, delivery HTML, PDF and equity-curve PNG formats and hashes;
- explicit lab-only authority and role separation.

The hard gate is implemented by:

- `control/FX_RELEASE_ASSURANCE_CONTRACT_V1.md`
- `control/FX_PRODUCTION_PROMOTION_ASSURANCE_CONTRACT_V1.md`
- `tools/fx_release_assurance.py`
- `send_fxreport.py`
- `tests/test_fx_release_assurance.py`
- `.github/workflows/validate-fx-release-assurance.yml`
- `.github/workflows/send-weekly-report.yml`

## Lab and production boundary

`weekly-fx` cannot issue production promotion `PASS`. A lab candidate may only return:

```text
INDETERMINATE_REQUIRES_TARGET_REPOSITORY_ASSURANCE
```

for production promotion. A later `daily-fx` package requires explicit authority, source/target hashes, target-repository tests and a fresh independent assurance pass.

## Remaining LEVEL 4 boundary

Lab SMTP success remains `LAB_TRANSPORT_SENT_UNVERIFIED`. Production LEVEL 4 can only be reached in the protected production repository with an independent receiving-system confirmation bound to the same release identity.

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
