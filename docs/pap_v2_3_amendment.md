# Pre-Analysis-Plan – Änderung v2.3 (Inferenz, ergebnisblind)
**Datum:** 11.09.2026, ca. 12:15 UTC · **Status:** eingefroren (SHA-256 in `docs/pap_v2_3_amendment.sha256`)

## Anlass
Mit den v2.2-Kontrollen (Vorperioden-Spread × Einlagensatz, Vorperioden-Schuldenquote × Einlagensatz) hat die in v2.1 festgelegte studentisierte Randomisierungsinferenz mit CR0-Standardfehler eine **Size von 9,3 %** (400 Simulationen, wahre Nullhypothese). Das ist nicht akzeptabel.

## Änderung
- **Statistik für H3:** β / SE_CR3, wobei SE_CR3 der Leave-one-NCB-out-Jackknife-Standardfehler ist.
- **Simulierte Size:** 3,3 % (300 Läufe) und 5,2 % (600 Läufe).
- **Alles andere unverändert:** Permutation ganzer Expositionspfade, 999 Ziehungen.

## Power mit Kontrollen und CR3 (`power/power_sensitivity.jsonl`)
| β pro SD Exposition | −0,15 | −0,20 | −0,25 | −0,30 |
|---|---|---|---|---|
| Power | 0,38 | 0,55 | 0,74 | 0,88 |

**MDE bei 80 %:** etwa −0,27 Skalenpunkte pro SD. Das liegt unter der 0,3-Schwelle der Kollinearitätsregel.

## Kollinearitätsregel v2.2 (ergebnisblind ausgewertet, Gewichte = Prefilter-Zählungen)
- Schuldenquoten: Eurostat Euro-Indikatoren 118/2022 (Stand Oktober 2022), Jahre 2019–2021.
- Nach FE verbleibender Anteil der Expositionsvarianz: 10,4 %.
- Mit Schuldenquote × Einlagensatz: 99 % davon bleiben erhalten; mit Spread und Schulden 87 %; mit zusätzlich Kern×Halbjahr-FE 74 %.
- Korrelation innerhalb der FE zwischen Exposition und Schuldenquote × Einlagensatz: 0,09.
- **Regel nicht ausgelöst.** Das Dosisdesign kann den NZB-Carry-Kanal vom vorperiodischen Schulden×Zins-Kanal trennen.
