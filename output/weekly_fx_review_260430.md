# Weekly FX Review 2026-04-30

> *This report is for informational and educational purposes only; please see the disclaimer at the end.*

## 1. Executive summary

This is a fresh prep-first Weekly FX Review trigger. The production workflow must first refresh the model portfolio state from Twelve Data, then validate the HTML/PDF render, and only then send the report.

The strategic regime remains **selective non-USD accumulation with geopolitical caution** unless the refreshed state and overlay evidence indicate otherwise. The report should not be considered final until the workflow has rebuilt the live state artifacts and passed delivery validation.

The funded book remains structured around reduced but still meaningful **USD** liquidity, defensive **CHF**, reduced residual **JPY**, and active non-USD risk in **AUD**, **MXN**, **CAD**, **EUR**, **GBP**, and **NZD**. **ZAR** remains outside the funded model until strategic quality improves.

## 2. Portfolio action snapshot

| Sleeve | Action | Current read |
|---|---|---|
| USD | Reduce | Liquidity anchor, but not the dominant expression |
| CHF | Hold / stage | Defensive diversifier |
| JPY | Reduce | Reduced reserve residual |
| CAD | Hold / stage | Commodity-linked developed-market sleeve |
| MXN | Buy | Satellite carry sleeve |
| AUD | Buy | Highest-conviction developed-market cyclical sleeve |
| GBP | Hold / stage | Improved but event-sensitive |
| EUR | Build on weakness | Staged Europe rebuild sleeve |
| NZD | Hold / stage | Modest recovery sleeve |
| ZAR | Sell / avoid | No current allocation |

## 3. Global macro & FX regime dashboard

- Global macro regime: selective recovery with ongoing geopolitical and energy risk.
- Policy divergence: AUD and MXN remain important expressions.
- Risk regime: selective recovery, not clean risk-on.
- USD liquidity / funding: still relevant but reduced.
- Technical overlay: must be read from the latest available production artifact.

## 4. Structural currency opportunity radar

| Theme | Status | Current read |
|---|---|---|
| Dollar liquidity premium | fading / still relevant | USD remains useful as liquidity, but excess defence should keep falling if confirmation persists |
| Swiss defensive role | active / watch | CHF remains useful ballast |
| Yen haven asymmetry | weak / watch | JPY remains reduced until confirmation improves |
| Commodity FX recovery | active / investable | AUD and CAD remain key developed-market expressions |
| Europe rebuild | active / staged | EUR and GBP remain staged sleeves |
| EM carry | active / investable | MXN remains preferred carry expression |
| High-beta EM beta | unconfirmed | ZAR remains avoided |

## 5. Key risks / invalidators

- Renewed oil or geopolitical shock restores USD and CHF defensive demand.
- Fresh U.S. inflation pressure revives USD strength.
- Global growth weakens enough to hurt AUD, CAD, MXN, GBP, EUR, and NZD.
- BoJ repricing strengthens JPY faster than expected.
- Twelve Data refresh, render validation, PDF generation, or email send fails.

## 6. Bottom line

The report should use a prep-first flow: refresh FX prices and portfolio state first, then render and send. The portfolio stance remains measured rotation away from oversized USD defence into the best-confirmed non-USD sleeves, with AUD, MXN, and CAD still the key expressions unless the refreshed data changes that judgment.

## 7. Equity curve and portfolio development

This section must be interpreted after the production workflow refreshes `output/fx_portfolio_state.json` and `output/fx_valuation_history.csv` from Twelve Data.

`EQUITY_CURVE_CHART_PLACEHOLDER`

## 8. Currency allocation map

| Currency | Strategic read | Action | Role in portfolio |
|---|---|---|---|
| USD | Defensive core, but fading premium | Reduce | Liquidity and optionality |
| AUD | Highest-conviction DM cyclical | Buy | Policy and growth sleeve |
| MXN | Satellite carry | Buy | Carry-plus-confirmation sleeve |
| CAD | Commodity-linked DM | Hold / stage | Oil and North America sleeve |
| CHF | Defensive diversifier | Hold / stage | Ballast |
| EUR | Europe rebuild | Build on weakness | Staged Europe sleeve |
| GBP | Improved but event-sensitive | Hold / stage | Sterling sleeve |
| NZD | Secondary recovery sleeve | Hold / stage | Modest live allocation |
| JPY | Weak reserve residual | Reduce | Reduced optionality |
| ZAR | Unconfirmed | Sell / avoid | No allocation |

## 9. Macro transmission & second-order effects map

| Shock / driver | Likely winners | Likely losers | Transmission logic |
|---|---|---|---|
| Reduced panic demand for the dollar | AUD, CAD, MXN, GBP, NZD, EUR | USD cash overweight | Less one-way haven demand weakens broad USD premium |
| Oil remains elevated | CAD, CHF, selective AUD | JPY, fragile energy importers | Commodity and energy channels matter |
| Stronger cyclical resilience | AUD, CAD, MXN, NZD | Low-conviction low-yield sleeves | Resource-linked and carry-positive sleeves benefit |
| Tighter Europe credit | USD, CHF | EUR-sensitive optimism | Lending weakness caps EUR chasing |
| Sterling technical confirmation | GBP | stale sterling underweights | Better price action can improve GBP ranking |

## 10. Current currency review

**USD — Reduce**  
USD remains important through cash and reserve status, but excess defensive allocation should keep falling if the refreshed data confirms USD de-crowding.

**EUR — Build on weakness**  
EUR remains strategically investable but should be staged rather than chased.

**JPY — Reduce**  
JPY remains a reduced residual until price confirmation improves.

**CHF — Hold / stage**  
CHF remains defensive ballast.

**GBP — Hold / stage**  
GBP remains improved but event-sensitive.

**AUD — Buy**  
AUD remains the leading developed-market cyclical sleeve.

**CAD — Hold / stage**  
CAD remains supported by commodity and North America sensitivity.

**NZD — Hold / stage**  
NZD remains a modest recovery sleeve.

**MXN — Buy**  
MXN remains the preferred carry sleeve.

**ZAR — Sell / avoid**  
ZAR remains outside the model allocation.

## 11. Best new currency opportunities

1. AUD — leading developed-market cyclical sleeve.  
2. MXN — preferred carry sleeve.  
3. CAD — durable commodity-linked sleeve.

## 12. Portfolio rotation plan

| Bucket | Positioning |
|---|---|
| Core liquidity | USD cash |
| Defensive diversification | CHF |
| Reduced haven residual | JPY |
| Commodity / cyclical DM | AUD, CAD, NZD |
| Carry / selective EM | MXN |
| Rebuilding Europe / UK | EUR, GBP |
| Avoid | ZAR |

## 13. Final action table

| Currency | Action | Target weight (%) | Confidence |
|---|---|---:|---|
| USD | Reduce | 24 | Medium-High |
| CHF | Hold / stage | 12 | Medium |
| JPY | Reduce | 5 | Medium |
| CAD | Hold / stage | 11 | Medium-High |
| MXN | Buy | 12 | Medium-High |
| AUD | Buy | 13 | High |
| GBP | Hold / stage | 7 | Medium |
| EUR | Build on weakness | 11 | Medium |
| NZD | Hold / stage | 5 | Low-Medium |
| ZAR | Sell / avoid | 0 | Medium-High |

## 14. Position changes executed this run

No additional model-portfolio rebalance is declared in this trigger scaffold. Any actual implementation change must come from a production rebalance/state artifact.

## 15. Current portfolio holdings and cash

- Starting capital (USD): **100,000.00**
- Invested market value (USD): **TBD after Twelve Data refresh**
- Cash (USD): **TBD after Twelve Data refresh**
- Total portfolio value (USD): **TBD after Twelve Data refresh**
- Since inception return (%): **TBD after Twelve Data refresh**
- Base currency: **USD**

## 16. Carry-forward input for next run

**This section is the canonical default input for the next run unless the user explicitly overrides it.**

- Report type: Weekly FX Review
- Run date: 2026-04-30
- Run filename: weekly_fx_review_260430.md
- Base currency: USD
- Portfolio engine state: refresh required before delivery; workflow should update from Twelve Data before render/send.

## 17. Disclaimer

This report is for informational and educational purposes only and does not constitute investment advice, a solicitation, or a recommendation to transact in any security, derivative, fund, or currency. The model portfolio is a rules-based illustrative framework built for analytical tracking. It does not account for taxes, transaction costs, funding costs, slippage, implementation constraints, legal restrictions, suitability requirements, or investor-specific objectives. Market conditions can change rapidly, including because of central-bank decisions, geopolitical developments, commodity-price shocks, and policy changes. Any use of this report or its model allocations is at the reader’s own risk.
