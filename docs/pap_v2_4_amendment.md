# Pre-Analysis-Plan – Änderung v2.4 (Konzentration der Identifikation, ergebnisblind)
**Datum:** 11.09.2026, ca. 21:00 UTC · **Status:** eingefroren (SHA-256 in `docs/pap_v2_4_amendment.sha256`)

## Befund (nur Zähl-, Treatment- und Expositionsdaten)
Leave-one-NCB-out-Zerlegung der identifizierenden Expositionsvarianz nach FE und v2.2-Kontrollen
(`output/leave_one_out_influence.csv`, Gewichte = Prefilter-Zählungen):

| NZB | Anteil an der identifizierenden Variation | Passagen im Klassifikationsuniversum |
|---|---|---|
| GR | 0,66 | 51 |
| IT | 0,41 | 274 |
| ES | 0,15 | 335 |
| MT | 0,07 | 28 |
| DE | 0,06 | 455 |
| alle übrigen | ≤ 0,06 | |

Die Anteile summieren sich auf über 1, weil die Beiträge korreliert sind. **Griechenland allein trägt zwei Drittel.** Das ist konsistent mit dem Mechanismus (GR und IT haben die höchsten eigenen Portfoliorenditen), macht das Ergebnis aber von wenigen Einheiten und im Fall Griechenlands von rund 51 Passagen abhängig.

## Änderungen
1. **R12 (neu, Pflichtausweis):** H3 wird 17-mal geschätzt, jeweils ohne eine NZB. Berichtet werden alle Punktschätzungen und Jackknife-t-Werte, im Paper als Abbildung.
2. **Interpretationsregel (vorab):** Wechselt das Vorzeichen von β beim Weglassen einer einzelnen NZB, oder fällt der Betrag um mehr als die Hälfte, wird das Ergebnis als **von einzelnen NZBs getragen** berichtet. Es gibt dann keinen allgemeinen Anspruch für den Euroraum, sondern nur die Aussage, dass die betroffenen NZBs den Zusammenhang tragen.
3. **Offenlegungspflicht:** Die Tabelle oben erscheint im Paper, nicht nur im Anhang.
4. **Keine Änderung** an H3, den Kontrollen oder der Inferenz.

## Bewertung
Das ist eine echte Schwäche des Designs und kein Messfehler. Sie folgt daraus, dass die nicht gepoolte Carry-Belastung nur dort stark von der Norm abweicht, wo die eigenen Portfolios hoch verzinst sind. Externe Validität für den gesamten Euroraum kann das Paper deshalb nicht beanspruchen.
