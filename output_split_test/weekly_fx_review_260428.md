# Weekly FX Review

> *This report is for informational and educational purposes only; please see the disclaimer at the end.*

## 1. Executive summary

This is an **automated state-driven split run** using the latest stored FX report as the strategic carry-forward base, the latest technical overlay in `output/fx_technical_overlay.json`, and the live implementation files in `output/fx_portfolio_state.json`, `output/fx_trade_ledger.csv`, and `output/fx_valuation_history.csv`. Implementation and valuation facts are taken from the state files when they differ from older report text.

The strategic regime remains **selective non-USD accumulation / reduced USD overweight / still geopolitics-aware**. Current live portfolio value is **100,538.00 USD**, with cash at **24,165.26 USD**, gross exposure at **76,372.74 USD**, realized P&L at **-7.87 USD**, unrealized P&L at **545.85 USD**, and the latest portfolio/overlay timestamp at **2026-04-24T21:48:25Z**.

The current ranking still favors **USD** as the core defensive anchor, with the strongest additional uses of capital now concentrated in **AUD**, **MXN**, **EUR**. This automated generator does **not** perform a fresh live macro research pass; strategy-heavy narrative is therefore refreshed from carry-forward state, while technical, valuation, and implementation facts are updated from the repo’s current state files.

## 2. Portfolio action snapshot

| Sleeve | Action | Current read |
|---|---|---|
| USD | Reduce | Strongest defensive anchor; supported by rates, liquidity, and broad overlay strength |
| EUR | Build on weakness | Lower-rate bloc plus strong negative technical confirmation |
| JPY | Reduce | Haven logic intact, but still strongly negative on current technical confirmation |
| CHF | Hold / stage | Clean second-line defensive sleeve despite negative technical confirmation |
| GBP | Hold / stage | Some rate support, but the technical picture remains strongly negative |
| AUD | Buy | RBA stance remains supportive, but AUD is still only mixed technically and remains cyclical |
| CAD | Hold / stage | Oil / terms-of-trade support intact, but weaker domestic growth and negative technical confirmation cap enthusiasm |
| NZD | Hold / stage | Recovery story lacks urgency and the overlay remains negative |
| MXN | Buy | Carry-positive macro story, but technical confirmation has weakened to negative |
| ZAR | Sell / avoid | Wrong exposure for a defensive, oil-shock-aware regime |

## 3. Global macro & FX regime dashboard

- **Global macro regime:** selective non-USD accumulation / reduced USD overweight / still geopolitics-aware (carried forward from the latest stored report; no live macro refresh in this automated generator).
- **Policy divergence:** **USD** remains favored versus lower-rate blocs; **AUD** and **MXN** retain selective support from higher-rate settings, but not enough to override defensive conditions.
- **Risk regime:** Mild risk-off.
- **USD liquidity / funding:** Supportive for **USD**.
- **Commodity impulse:** Supportive for **CAD** in macro terms; selectively constructive for **AUD**; adverse for major energy importers.
- **Technical overlay:** Same-day available; **USD** negative, **EUR** mixed, **GBP** strong positive, **JPY** strong negative, **CHF** strong positive, **AUD** strong positive, **CAD** strong positive, **NZD** positive, **MXN** strong positive, **ZAR** positive.

## 4. Structural currency opportunity radar

| Theme | Status | Current read |
|---|---|---|
| Dollar liquidity premium | active / investable | Elevated uncertainty and defensive funding demand keep **USD** supported. |
| Swiss defensive role with intervention risk | active / investable | **CHF** remains the cleaner second-line defensive sleeve, though intervention risk caps the upside tail. |
| Yen haven asymmetry | active / watch | Haven logic remains intact, but the overlay is still strongly negative, so position size should stay controlled. |
| Commodity FX recovery | active / watch | **CAD** has macro support from oil, while **AUD** benefits from the current rate stance; neither has clean broad confirmation. |
| Europe cyclical repair | fading / under pressure | Lower relative rates and negative technical confirmation keep **EUR** weak. |
| EM carry under controlled volatility | weakening / watch | **MXN** remains carry-interesting, but the overlay has softened to negative. |
| High-beta EM beta | invalidated | **ZAR** remains unattractive into a defensive, oil-shock-aware regime. |

## 5. Key risks / invalidators

- A rapid and durable de-escalation in geopolitical risk plus a sharp reversal in oil would reduce the **USD** / **CHF** defensive premium.
- A decisive broadening of non-U.S. growth plus materially easier Fed pricing would weaken the **USD** overweight case.
- A clean reversal in **USDJPY** technical strength would improve the case for rebuilding **JPY** more aggressively.
- A clearer euro-area growth improvement with no renewed energy pressure would improve **EUR**.
- A broad risk-on reset would help **AUD**, **NZD**, and **ZAR** faster than this framework currently assumes.

## 6. Bottom line

The correct portfolio posture remains **defense first, optionality second, high-beta last**. **USD** remains the strongest core anchor. **CHF** remains the cleaner secondary defensive allocation than **JPY** on this run. **CAD**, **AUD**, and **MXN** remain secondary sleeves rather than leadership sleeves. **EUR** and **GBP** stay in reduce territory, while **NZD** and **ZAR** still do not deserve capital.

## 7. Equity curve and portfolio development

Valuation source: **Twelve Data latest completed daily bars / overlay reuse**. Valuation date: **2026-04-24**. Engine overlay timestamp: **2026-04-24T21:48:25Z**.

- Net asset value (USD): **100,538.00**
- Cash (USD): **24,165.26**
- Gross exposure (USD): **76,372.74**
- Net exposure (USD): **76,372.74**
- Realized P&L (USD): **-7.87**
- Unrealized P&L (USD): **545.85**
- Daily return (%): **0.2769**
- Since inception return (%): **0.5380**
- Max drawdown (%): **-0.8519**

The equity curve below is sourced from the live portfolio engine and reflects actual mark-to-market updates stored in `output/fx_valuation_history.csv`.

| Date | NAV (USD) | Daily return (%) | Since inception return (%) | Drawdown (%) | Overlay timestamp |
|---|---|---|---|---|---|
| 2026-03-25 | 100,000.00 | 0.0000 | 0.0000 | 0.0000 | 2026-03-25T12:08:31Z |
| 2026-03-25 | 99,947.37 | -0.0000 | -0.0526 | -0.0526 | 2026-03-25T12:21:52Z |
| 2026-03-25 | 99,788.68 | -0.0000 | -0.2113 | -0.2113 | 2026-03-25T19:18:21Z |
| 2026-03-25 | 99,791.54 | -0.0000 | -0.2085 | -0.2113 | 2026-03-25T22:08:27Z |
| 2026-03-25 | 99,791.74 | -0.0000 | -0.2083 | -0.2113 | 2026-03-25T23:34:00Z |
| 2026-03-25 | 99,782.64 | 0.0000 | -0.2174 | -0.2174 | 2026-03-25T23:46:50Z |
| 2026-03-25 | 99,785.42 | -0.0000 | -0.2146 | -0.2174 | 2026-03-25T23:50:51Z |
| 2026-03-26 | 99,765.98 | -0.0000 | -0.2340 | -0.2340 | 2026-03-26T00:46:04Z |
| 2026-03-26 | 99,673.93 | -0.0000 | -0.3261 | -0.3261 | 2026-03-26T11:33:57Z |
| 2026-03-26 | 99,518.16 | -0.0001 | -0.4818 | -0.4818 | 2026-03-26T19:25:44Z |
| 2026-03-26 | 99,472.94 | -0.0000 | -0.5271 | -0.5271 | 2026-03-26T20:13:51Z |
| 2026-03-26 | 99,556.26 | -0.0003 | -0.4437 | -0.5271 | 2026-03-26T23:05:58Z |
| 2026-03-26 | 99,551.58 | -0.0000 | -0.4484 | -0.5271 | 2026-03-26T23:32:25Z |
| 2026-03-26 | 99,559.41 | -0.0000 | -0.4406 | -0.5271 | 2026-03-26T23:42:52Z |
| 2026-03-28 | 99,257.64 | -0.0001 | -0.7424 | -0.7424 | 2026-03-28T08:58:02Z |
| 2026-03-28 | 99,276.67 | -0.0002 | -0.7233 | -0.7424 | 2026-03-28T22:33:56Z |
| 2026-03-28 | 99,273.40 | -0.0000 | -0.7266 | -0.7424 | 2026-03-28T22:45:34Z |
| 2026-03-29 | 99,270.83 | -0.0026 | -0.7292 | -0.7424 | 2026-03-29T00:25:31Z |
| 2026-03-29 | 99,267.15 | -0.0037 | -0.7329 | -0.7424 | 2026-03-29T00:50:29Z |
| 2026-03-29 | 99,274.67 | 0.0076 | -0.7253 | -0.7424 | 2026-03-29T08:35:40Z |
| 2026-03-29 | 99,319.63 | -0.0003 | -0.6804 | -0.7424 | 2026-03-29T12:55:35Z |
| 2026-03-29 | 99,324.70 | 0.0051 | -0.6753 | -0.7424 | 2026-03-29T13:01:01Z |
| 2026-03-29 | 99,352.48 | -0.0003 | -0.6475 | -0.7424 | 2026-03-29T14:24:37Z |
| 2026-03-29 | 99,299.75 | -0.0531 | -0.7003 | -0.7424 | 2026-03-29T20:19:49Z |
| 2026-03-29 | 99,148.10 | -0.1527 | -0.8519 | -0.8519 | 2026-03-29T22:46:54Z |
| 2026-03-30 | 99,333.13 | 0.1866 | -0.6669 | -0.8519 | 2026-03-30T06:19:57Z |
| 2026-03-30 | 99,194.27 | -0.1398 | -0.8057 | -0.8519 | 2026-03-30T16:52:31Z |
| 2026-03-31 | 99,478.38 | 0.2864 | -0.5216 | -0.8519 | 2026-03-31T23:01:03Z |
| 2026-04-01 | 99,560.42 | 0.0825 | -0.4396 | -0.8519 | 2026-04-01T06:11:35Z |
| 2026-04-01 | 99,690.99 | 0.1311 | -0.3090 | -0.8519 | 2026-04-01T07:16:07Z |
| 2026-04-01 | 99,827.25 | 0.1367 | -0.1727 | -0.8519 | 2026-04-01T17:07:23Z |
| 2026-04-01 | 99,724.54 | -0.1029 | -0.2755 | -0.8519 | 2026-04-01T23:06:42Z |
| 2026-04-02 | 99,428.00 | -0.2974 | -0.5720 | -0.8519 | 2026-04-02T22:09:04Z |
| 2026-04-03 | 99,307.74 | -0.1210 | -0.6923 | -0.8519 | 2026-04-03T20:00:24Z |
| 2026-04-03 | 99,326.13 | 0.0185 | -0.6739 | -0.8519 | 2026-04-03T20:25:28Z |
| 2026-04-14 | 100,717.08 | 1.4004 | 0.7171 | -0.8519 | 2026-04-14T20:32:02Z |
| 2026-04-14 | 100,724.36 | 0.0072 | 0.7244 | -0.8519 | 2026-04-14T22:21:34Z |
| 2026-04-14 | 100,713.64 | -0.0106 | 0.7136 | -0.8519 | 2026-04-14T23:14:25Z |
| 2026-04-15 | 100,768.01 | 0.0540 | 0.7680 | -0.8519 | 2026-04-15T18:14:47Z |
| 2026-04-15 | 100,771.02 | 0.0030 | 0.7710 | -0.8519 | 2026-04-15T18:18:38Z |
| 2026-04-15 | 100,773.44 | 0.0024 | 0.7734 | -0.8519 | 2026-04-15T18:22:28Z |
| 2026-04-16 | 100,681.33 | -0.0914 | 0.6813 | -0.8519 | 2026-04-16T16:49:00Z |
| 2026-04-16 | 100,664.43 | -0.0168 | 0.6644 | -0.8519 | 2026-04-16T17:49:57Z |
| 2026-04-16 | 100,701.83 | 0.0372 | 0.7018 | -0.8519 | 2026-04-16T19:03:12Z |
| 2026-04-16 | 100,698.76 | -0.0030 | 0.6988 | -0.8519 | 2026-04-16T21:50:17Z |
| 2026-04-16 | 100,727.17 | 0.0282 | 0.7272 | -0.8519 | 2026-04-16T22:29:58Z |
| 2026-04-17 | 100,728.32 | 0.0011 | 0.7283 | -0.8519 | 2026-04-17T07:58:30Z |
| 2026-04-17 | 101,049.90 | 0.3193 | 1.0499 | -0.8519 | 2026-04-17T14:06:33Z |
| 2026-04-20 | 100,860.23 | -0.1877 | 0.8602 | -0.8519 | 2026-04-20T21:24:32Z |
| 2026-04-21 | 100,734.16 | -0.0066 | 0.7342 | -0.8519 | 2026-04-21T11:02:02Z |
| 2026-04-21 | 100,665.49 | -0.0682 | 0.6655 | -0.8519 | 2026-04-21T21:24:36Z |
| 2026-04-21 | 100,655.14 | 0.0002 | 0.6551 | -0.8519 | 2026-04-21T22:00:38Z |
| 2026-04-22 | 100,581.30 | -0.0734 | 0.5813 | -0.8519 | 2026-04-22T21:28:01Z |
| 2026-04-23 | 100,260.34 | -0.3191 | 0.2603 | -0.8519 | 2026-04-23T17:51:43Z |
| 2026-04-24 | 100,538.00 | 0.2769 | 0.5380 | -0.8519 | 2026-04-24T21:48:25Z |

## 8. Currency allocation map

| Currency | Strategic score | Action | Role in portfolio |
|---|---|---|---|
| USD | 6.4 | Reduce | Base, liquidity buffer, defensive anchor |
| EUR | 17.1 | Build on weakness | Lower-rate bloc with energy sensitivity and strong negative technical confirmation |
| JPY | 4.2 | Reduce | Haven sleeve retained, but current technical confirmation is still strongly negative |
| CHF | 13.6 | Hold / stage | Defensive diversifier with cleaner strategic support than JPY |
| GBP | 11.6 | Hold / stage | Some rate support remains, but strong negative technical confirmation weakens the case |
| AUD | 19.6 | Buy | Mixed technical overlay offsets part of the cyclical risk |
| CAD | 13.3 | Hold / stage | Oil / terms-of-trade support with weaker near-term confirmation |
| NZD | 11.4 | Hold / stage | Low-rate recovery story lacks urgency |
| MXN | 19.6 | Buy | Carry-positive macro story, but technical confirmation has weakened to negative |
| ZAR | 1.6 | Sell / avoid | High-beta EM exposure not paid enough in this regime |

## 9. Macro transmission & second-order effects map

| Shock / driver | Likely winners | Likely losers | Transmission logic |
|---|---|---|---|
| Energy-shock / geopolitical stress | USD, CHF, CAD | EUR, NZD, ZAR | Higher fuel costs raise defensive demand, help energy-linked terms of trade, and hurt importers. |
| Fed on hold versus lower-rate blocs | USD | EUR, NZD, CHF cash alternatives | Rate differential and cash carry favor **USD**. |
| BoJ normalization from a still-low base | JPY | Traditional funding trades versus JPY | Incremental tightening reduces the structural drag on **JPY**, though price action is not yet confirming. |
| Hawkish AUD carry without broad risk-on | AUD | Lower-yield cyclical alternatives | **AUD** gets some rate support, but not enough to become a leadership sleeve in mild risk-off. |
| Trade-policy uncertainty | USD, CHF | AUD, NZD, ZAR, cyclical EUR rebound trades | Reduced visibility hurts high-beta currencies and supports liquid defensive anchors. |

## 10. Current currency review

**USD — Reduce**
The current overlay remains positive for the dollar through broad non-USD weakness. **USD** remains the highest-quality base sleeve.

**EUR — Build on weakness**
The current overlay remains explicitly strong negative on **EUR**. Macro carry-forward and technical confirmation continue to align to the downside.

**JPY — Reduce**
The macro haven thesis remains intact, but the current overlay still shows a strong negative **JPY** confirmation through **USDJPY** strength. **JPY** remains in the portfolio, but only as a staged hold rather than a larger haven sleeve.

**CHF — Hold / stage**
**CHF** remains one of the cleanest defensive diversifiers. The current overlay is negative, which tempers sizing, but the broader defensive case remains intact.

**GBP — Hold / stage**
**GBP** retains some rate support, but the current technical overlay remains strong negative. That keeps **GBP** in reduce territory rather than leadership status.

**AUD — Buy**
**AUD** is still only mixed on the overlay and remains a cyclical currency in a mild risk-off world. That supports a staged allocation, not aggressive adding.

**CAD — Hold / stage**
**CAD** still has macro support from oil and terms of trade, but the current overlay for **USDCAD** still argues against stronger conviction. That keeps **CAD** in smaller-hold territory.

**NZD — Hold / stage**
The strategic case remains weak and the overlay remains negative. That is not enough to justify a rebuild.

**MXN — Buy**
**MXN** remains carry-positive on macro logic, but the latest overlay has softened to negative and the global backdrop is less friendly to EM carry. That keeps **MXN** in the portfolio, but with a stronger case for disciplined sizing.

**ZAR — Sell / avoid**
**ZAR** remains the wrong kind of exposure for a defensive portfolio with geopolitical and trade-policy awareness. The overlay remains negative and does not rescue the weak strategic case.

## 11. Best new currency opportunities

1. **AUD** — Not a clean technical buy, but still a better cyclical placeholder than the weaker high-beta alternatives because the overlay is mixed rather than outright broken.
2. **MXN** — Carry remains helpful, but the negative overlay argues for disciplined sizing instead of aggressive adding.
3. **EUR** — Remains one of the better available uses of capital in the current state-driven ranking.

## 12. Portfolio rotation plan

| Bucket | Positioning |
|---|---|
| Core defense | USD cash 36%, CHF 13% |
| Defensive optionality | JPY 13% |
| Secondary macro hold | CAD 10% |
| Staged cyclicals / carry | MXN 8%, AUD 8% |
| Reduce / underweight | GBP 7%, EUR 5% |
| Avoid | NZD 0%, ZAR 0% |

No fresh rebalance is assumed in this automated generator run beyond the authoritative implementation state already stored in the repo.

## 13. Final action table

| Currency | Action | Target weight (%) | Confidence |
|---|---|---|---|
| USD | Reduce | 24 | High |
| EUR | Build on weakness | 11 | Medium |
| JPY | Reduce | 5 | Medium-High |
| CHF | Hold / stage | 12 | Medium |
| GBP | Hold / stage | 7 | Medium |
| AUD | Buy | 13 | Medium |
| CAD | Hold / stage | 11 | Medium |
| NZD | Hold / stage | 5 | Medium |
| MXN | Buy | 12 | Medium |
| ZAR | Sell / avoid | 0 | Medium |

## 14. Position changes executed this run

No **additional** position changes are executed inside this automated generator run. However, the authoritative implementation state currently reflects a rebalance sourced from `weekly_fx_review_260421_03.md`, with **8 trades executed** on **2026-04-21**.

Authoritative latest rebalance adjustments already recorded in the trade ledger:

| Currency | Units delta | Execution price (CCYUSD) | Notional USD | Comment |
|---|---|---|---|---|
| CHF | 7.9027 | 1.27990170 | 10.11 | Hold / stage target 12.00% |
| JPY | 361.5961 | 0.00627311 | 2.27 | Reduce target 5.00% |
| CAD | -9.8088 | 0.73190904 | 7.18 | Hold / stage target 11.00% |
| MXN | -154.7560 | 0.05773162 | 8.93 | Buy target 12.00% |
| AUD | 1.7791 | 0.71516000 | 1.27 | Buy target 13.00% |
| GBP | -0.9748 | 1.35014000 | 1.32 | Hold / stage target 7.00% |
| EUR | 8.8053 | 1.17397000 | 10.34 | Build on weakness target 11.00% |
| NZD | 12.5507 | 0.58903000 | 7.39 | Hold / stage target 5.00% |

## 15. Current portfolio holdings and cash

- Starting capital (USD): **100,000.00**
- Invested market value (USD): **76,372.74**
- Cash (USD): **24,165.26**
- Total portfolio value (USD): **100,538.00**
- Since inception return (%): **0.5380**
- Base currency: **USD**

The holdings below are sourced from the live portfolio-state file. The displayed **Current weight (%)** column is derived deterministically as `market_value_usd / NAV`, because the stored `current_weight_pct` values in the state file do not reconcile to the NAV/cash totals.

| Currency sleeve | Implementation pair | Direction | Entry date | Entry price | Current price | Gross exposure (USD) | Unrealized P&L (USD) | Current weight (%) | Stance |
|---|---|---|---|---|---|---|---|---|---|
| EUR | EUR/USD -> EURUSD | Long EUR | 2026-03-25 | 1.16903261 | 1.17202000 | 11,053.65 | 28.17 | 10.99 | Build on weakness |
| JPY | USD/JPY -> JPYUSD | Long JPY | 2026-03-25 | 0.00629622 | 0.00627487 | 5,034.16 | -17.13 | 5.01 | Reduce |
| CHF | USD/CHF -> CHFUSD | Long CHF | 2026-03-25 | 1.26781027 | 1.27369065 | 12,019.98 | 55.49 | 11.96 | Hold / stage |
| GBP | GBP/USD -> GBPUSD | Long GBP | 2026-03-25 | 1.34200897 | 1.35317000 | 7,061.66 | 58.24 | 7.02 | Hold / stage |
| AUD | AUD/USD -> AUDUSD | Long AUD | 2026-03-25 | 0.70375383 | 0.71485000 | 13,079.47 | 203.02 | 13.01 | Buy |
| CAD | USD/CAD -> CADUSD | Long CAD | 2026-03-25 | 0.72560532 | 0.73144863 | 11,065.08 | 88.40 | 11.01 | Hold / stage |
| NZD | NZD/USD | Long NZD | 2026-04-21 | 0.59039799 | 0.58787000 | 5,022.83 | -21.60 | 5.00 | Hold / stage |
| MXN | USD/MXN -> MXNUSD | Long MXN | 2026-03-25 | 0.05680463 | 0.05752760 | 12,035.91 | 151.26 | 11.97 | Buy |
| USD cash | — | Long USD cash | 2026-03-25 | 1.00000000 | 1.00000000 | 24,165.26 | 0.00 | 24.04 | Reduce |

## 16. Carry-forward input for next run

**This section is the canonical default input for the next run unless the user explicitly overrides it.**

- Report type: Weekly FX Review
- Run date: 2026-04-28
- Run version: automated-split
- Base currency: USD
- Starting capital: 100,000.00
- Current total portfolio value: 100,538.00
- Cash: 24,165.26
- Holdings:
  - EUR 10.99%
  - JPY 5.01%
  - CHF 11.96%
  - GBP 7.02%
  - AUD 13.01%
  - CAD 11.01%
  - NZD 5%
  - MXN 11.97%
  - USD cash 24.04%
- Strategic regime: selective non-USD accumulation / reduced USD overweight / still geopolitics-aware
- Technical overlay state: latest available refresh; USD negative, EUR mixed, GBP strong positive, JPY strong negative, CHF strong positive, AUD strong positive, CAD strong positive, NZD positive, MXN strong positive, ZAR positive
- Portfolio engine state: live; last valuation date 2026-04-24 and latest portfolio-state overlay timestamp 2026-04-24T21:48:25Z
- Technical overlay as of: 2026-04-25T13:47:23Z
- Highest-priority adds next run if thesis improves further: AUD, MXN
- First candidates for rebuild if technicals improve: JPY, AUD, CAD
- First candidates for reduction if regime softens: USD, CHF
- First candidates for addition on improved global breadth: AUD, EUR
- Avoid unless regime changes materially: NZD, ZAR

## 17. Disclaimer

This report is for informational and educational purposes only and does not constitute investment advice, a solicitation, or a recommendation to transact in any security, derivative, fund, or currency. The model portfolio is a rules-based illustrative framework built for analytical tracking. It does not account for taxes, transaction costs, funding costs, slippage, implementation constraints, legal restrictions, suitability requirements, or investor-specific objectives. Market conditions can change rapidly, including because of central-bank decisions, geopolitical developments, commodity-price shocks, and policy changes. Any use of this report or its model allocations is at the reader’s own risk.
