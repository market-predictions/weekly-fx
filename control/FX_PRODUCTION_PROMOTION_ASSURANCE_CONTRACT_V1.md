# FX Production Promotion Assurance Contract V1

## Decision

```text
contract_id=FX_PRODUCTION_PROMOTION_ASSURANCE_CONTRACT_V1
source_repository=market-predictions/weekly-fx
target_repository=market-predictions/daily-fx
weekly_fx_may_self_promote=false
lab_pass_is_production_authority=false
```

## Purpose

Make the lab/production separation machine- and operator-visible. A valid Weekly FX lab assurance record proves only that a lab candidate is internally coherent and safe for the configured lab delivery path.

## Promotion prerequisites

A future production promotion package requires:

1. explicit promotion scope and user authority;
2. source and target commit SHAs;
3. an enumerated file manifest with hashes;
4. evidence that lab-only recipients, secrets, workflows and artifacts are not copied as production authority;
5. target-repository tests and project-specific assurance;
6. a new release candidate in `daily-fx`;
7. independent pre-send assurance in `daily-fx`;
8. independent production receiving-system confirmation before completion.

## Fail-closed rule

Any promotion assertion generated only in `weekly-fx` must return:

```text
INDETERMINATE_REQUIRES_TARGET_REPOSITORY_ASSURANCE
```

It may never return production `PASS`.

## Prohibited shortcuts

- do not reinterpret a lab workflow success as production approval;
- do not copy mail secrets or recipients blindly;
- do not promote stale state or carry artifacts;
- do not let the same candidate bypass a new target-repository assurance pass;
- do not report production delivery from a lab manifest or lab inbox receipt.
