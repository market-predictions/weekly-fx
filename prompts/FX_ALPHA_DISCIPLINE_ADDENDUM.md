# FX Alpha Discipline Addendum

This file is active runtime authority for `weekly-fx` report generation and validation.

It hardens the existing `fx.txt` framework without replacing the monolithic production prompt.

## Purpose

The FX review must move from macro commentary plus portfolio tracking toward a stricter alpha-generation operating system.

A USD-base spot FX portfolio has only two direct return sources:
1. spot FX movement
2. carry / rollover / rate-differential return

Therefore every report must make carry, cash drag, risk-bucket concentration, and no-action discipline explicit.

## 1. Carry dashboard rule

Every Weekly FX Review must include a compact block labelled exactly:

`FX carry dashboard`

The block must show, at minimum:
- policy-rate proxy or actual rollover source
- USD cash yield proxy
- estimated carry vs USD for each funded sleeve
- estimated annual carry contribution in USD
- estimated weekly carry contribution in USD
- spot unrealized P&L in USD
- whether the sleeve is positive carry, negative carry, or cash-yield proxy

Preferred machine-readable source:
- `output/fx_carry_snapshot.csv`

If broker rollover, tom-next, or forward-point data is not available, use the policy-rate proxy config in:
- `config/fx_policy_rate_proxies.json`

The report must clearly label this as an estimate, not as guaranteed realized carry.

## 2. USD cash contradiction check

Every Weekly FX Review must include a compact block labelled exactly:

`USD cash contradiction check`

Rule:
- USD cash above 10% is not neutral.
- If USD is labelled `Reduce` while USD cash remains above 10%, the report must do one of the following:
  1. reduce USD target weight versus current cash weight
  2. execute a reduction
  3. declare capital-preservation mode
  4. include a dated no-action override with a clear reason and expiry condition

If none of those exists, the report fails alpha discipline.

## 3. Risk-bucket exposure rule

Every Weekly FX Review must include a compact block labelled exactly:

`Risk-bucket exposure`

The report must show true macro exposure buckets, not just currency labels:

| Bucket | Included sleeves |
|---|---|
| USD liquidity | USD cash |
| Defensive FX | CHF, JPY |
| Risk-on / cyclical / carry FX | AUD, CAD, MXN, EUR, GBP, NZD, ZAR |

Preferred machine-readable source:
- `output/fx_risk_bucket_snapshot.json`

Guardrails:
- risk-on / cyclical / carry FX soft cap: 55%
- hard warning threshold: 60%
- above 60% requires explicit justification and stress-test language

## 4. Reduce-signal execution discipline

The label `Reduce` is an execution label, not a sentiment label.

Use these definitions:
- `Reduce` = target weight is lower than current weight, or a trade has been executed
- `Hold / reduce bias` = lower conviction, but no immediate trade
- `Reduce pending trigger` = reduction is conditional on a defined trigger
- `Exit clock` = position must be reviewed for reduction or closure by the next report

A sleeve may not remain labelled `Reduce` for more than one report cycle without either:
- an executed reduction
- a lower target weight
- a dated no-action override

## 5. No-action override table

If Section 14 says no rebalance occurred, it must include a compact table labelled exactly:

`No-action override table`

The table must cover:

| Trigger | Status | Required action or override |
|---|---|---|
| USD cash above ceiling | yes/no | reduce, capital-preservation mode, or dated override |
| Reduce signal unresolved | yes/no | execute, lower target, or dated override |
| Top conviction underweight | yes/no | add or explain why not |
| Risk-on bucket above soft cap | yes/no | justify, hedge, or reduce |
| Carry hurdle failed | yes/no | review or close |

A no-rebalance conclusion without this table is incomplete.

## 6. Carry hurdle rule

Any non-USD sleeve must pass at least one of these tests:
- positive estimated carry vs USD
- credible spot-appreciation thesis
- explicit hedge/diversifier role

If a sleeve is both below entry price and has negative estimated carry vs USD, the report must flag it for immediate review unless it has a clear hedge role.

## 7. Conviction-weight alignment rule

Future reports must show whether target weights align with stated conviction.

Suggested bands:

| Conviction tier | FX target range |
|---|---:|
| Tier 1 | 12-16% |
| Tier 2 | 7-11% |
| Tier 3 | 3-6% |
| Avoid / closed | 0% |
| USD cash normal mode | 5-10% |
| USD cash capital-preservation mode | 15-35% |

If a sleeve is top conviction but below its band, the report must either raise the target or explain why implementation is staged.

## 8. Output placement

Do not add a new large section.

Integrate the new alpha-discipline blocks into existing sections:

| Required block | Preferred report section |
|---|---|
| FX carry dashboard | Section 7 or Section 15 |
| USD cash contradiction check | Section 14 |
| Risk-bucket exposure | Section 8 |
| No-action override table | Section 14 |
| Conviction-weight alignment | Section 13 or Section 15 |

## 9. Machine-readable artifacts

The following files are now part of the FX input/state contract:
- `output/fx_carry_snapshot.csv`
- `output/fx_risk_bucket_snapshot.json`

They are generated by:
- `tools/write_fx_carry_and_risk_snapshots.py`

Carry accrual is applied by:
- `tools/apply_fx_carry_accrual.py`

Pre-send discipline is enforced by:
- `tools/validate_fx_action_discipline.py`

## 10. Delivery gate

The send workflow must fail before render/send if:
- carry snapshot is missing or empty
- FX carry dashboard block is missing from the report
- USD cash contradiction check block is missing from the report
- Risk-bucket exposure block is missing from the report
- Section 14 says no rebalance occurred but no No-action override table exists
- USD is labelled Reduce while USD cash is above 10% and there is no target reduction or dated no-action override

The workflow may warn, but should not automatically fail, when the risk-on bucket is between 55% and 60%.
Above 60%, the report must explicitly justify the concentration.
