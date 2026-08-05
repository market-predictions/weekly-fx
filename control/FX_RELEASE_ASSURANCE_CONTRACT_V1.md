# Weekly FX Lab Release Assurance Contract V1

## Status

```text
contract_id=FX_RELEASE_ASSURANCE_CONTRACT_V1
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
project=market-predictions/weekly-fx
environment=lab
current_maturity=LEVEL_3_HARD_CI_GATE
target_production_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
```

## Purpose

Prevent a Weekly FX lab report from reaching transport without independent reconstruction of the report, refreshed implementation state, alpha-discipline evidence, rendered assets and lab boundary.

This contract does not promote `weekly-fx` changes into `daily-fx`.

## Required evidence

A lab pre-send `PASS` binds:

- source commit SHA and workflow run ID;
- exact report path, report date and token;
- state-refresh manifest;
- portfolio state, trade ledger, valuation history and recommendation scorecard;
- technical overlay, carry snapshot and risk-bucket snapshot;
- cleaned Markdown, delivery HTML, PDF and equity-curve PNG;
- required alpha-discipline report blocks;
- exact SHA-256 identities;
- explicit lab-only authority fields.

## Mandatory checks

1. source and report identities are valid;
2. report date equals refreshed valuation date;
3. all requested pairs were refreshed and marked fresh;
4. portfolio state valuation date and NAV agree with the refresh manifest;
5. technical, carry and risk artifacts are present and non-empty;
6. the report contains all 17 required sections;
7. the report contains `FX carry dashboard`, `USD cash contradiction check`, and `Risk-bucket exposure`;
8. when no trade execution is disclosed, the report contains a no-action override table or equivalent explicit no-action proof;
9. generated Markdown/HTML/PDF/PNG formats are valid;
10. every evidence and client artifact is hashed;
11. `environment=lab`, production authority is false, and target repository is `weekly-fx`;
12. implementation and assurance roles are separate.

## Hard gate

`send_fxreport.py` preserves the established renderer and validation interface. On direct transport execution, it requires the lab assurance builder and validator to return `PASS` before SMTP transport.

The production workflow sets `FX_DELIVERY_ENVIRONMENT=lab`. Any other environment is rejected in this repository.

## Status semantics

```text
LAB_RELEASE_CANDIDATE_READY
GOVERNANCE_FAIL
GOVERNANCE_PASS_PRE_SEND
LAB_TRANSPORT_SENT_UNVERIFIED
LAB_OUTCOME_CONFIRMED
```

## Production boundary

A lab `PASS` is never production promotion authority. Promotion is governed separately by `control/FX_PRODUCTION_PROMOTION_ASSURANCE_CONTRACT_V1.md` and requires a fresh candidate and independent assurance in the protected target repository.
