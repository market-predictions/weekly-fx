# OUTCOME — weekly-fx (wekelijks FX-rapport)

> **Doel bevestigd door de eigenaar op 2026-11-15.** De invulling van "klaar als" volgt bij de herbouw (ronde B).

**Doel:** Elke week een correct FX-rapport over een FX-modelportefeuille bij de lezers. Opbouw zoals `weekly-etf-eu`, maar met wat FX eigen maakt (paren in plaats van fondsen, rente en carry, centrale banken, andere lezersbehoefte).

**Klaar als:**
- Het rapport is op de vaste dag vóór het vaste tijdstip verzonden.
- Elk getal in het rapport komt uit de berekende feiten; de portefeuille-historie sluit op de cent.
- Eén `acceptance.yml` toetst dit (te bouwen).

**Alleen met akkoord van de eigenaar:** ontvangers en live verzenden; beslisregels en benchmark; startportefeuille.

**Status:** laatste run van de wekelijkse workflow (na herbouw).

## Open vragen aan de eigenaar
- Verzenddag en tijdstip?
- Taal: NL en EN, zoals weekly-etf-eu?
- Wat is de portefeuille: posities in valutaparen met een basisvaluta (EUR?), en mag er hefboom in?

## Besluiten
- 2026-11-15 — Overgestapt op het outcome-first model (control-plane). Oudere plan-, status- en controledocumenten in deze repo zijn niet meer leidend.
- 2026-11-15 — Eigen product, los van `daily-fx` (dagelijks). Niet samenvoegen.
- 2026-11-15 — Herbouw volgens het model van `weekly-etf-eu`: vaste pijplijn (data → beslissen → feiten → tekst → rapport → mail), AI rekent nooit, één acceptatietoets.
