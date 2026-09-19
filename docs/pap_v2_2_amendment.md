# Pre-Analysis-Plan – Änderung v2.2 (Referee-Pass, ergebnisblind)
**Datum:** 11.09.2026, ca. 11:30 UTC · **Status:** eingefroren (SHA-256 in `docs/pap_v2_2_amendment.sha256`) · **Veto durch Philip möglich bis zum Start der Klassifikation**

## 0. Offenlegung
Grundlage: interner Referee-Pass (`docs/referee_report_internal_v1.md`) und eine Diagnose, die nur Treatment-, Expositions- und Zähldaten nutzt. Keine Stance-Position wurde gelesen oder geschätzt.

## 1. Diagnose: Woher die identifizierende Variation im Dosisdesign kommt
- Nach Gouverneurs- und Halbjahres-FE bleiben **10,4 %** der Varianz der Exposition übrig. Mit Kern×Halbjahr-FE und Vorperioden-Spread×Einlagensatz sind es 8,6 %.
- Diese verbleibende Variation erklärt sich zu **92,5 %** durch die **Abweichung der eigenen Staatsanleihebestände pro Kapitalschlüsselpunkt vom Durchschnitt, multipliziert mit dem Referenzsatz**. Die eigene Portfoliorendite erklärt nur 2 %.
- **Konsequenz:** Identifiziert wird im Kern aus „NZBs mit überdurchschnittlichen eigenen Beständen je Schlüsselpunkt verlieren relativ mehr, wenn die Zinsen steigen". Die Bestände je Schlüsselpunkt reichen von 2,6 Mrd. € (EE) bis 38,1 Mrd. € (IT), 2024H1.
- **Neue Hauptbedrohung:** Hohe Bestände je Schlüsselpunkt entstehen dort, wo der Staatsanleihemarkt groß ist, also tendenziell bei hoher Staatsverschuldung. Gouverneure hochverschuldeter Länder könnten auf Zinserhöhungen aus fiskalischen Gründen dovisher reagieren (Kanal von Heinemann & Kemper), unabhängig von der NZB-GuV.

## 2. Änderungen
1. **Kontrollen in der Hauptspezifikation (H3 und H1):**
   - nationale HICP-Inflation (unverändert);
   - **Spread zu DE im Mittel 2019–2021 × Einlagensatz_t** (ersetzt den laufenden Spread);
   - **Schuldenquote im Mittel 2019–2021 × Einlagensatz_t** (ersetzt die laufende Schuldenquote).
   - **Begründung:** Laufende Spreads und Schuldenquoten reagieren auf dieselben Schocks und die gemeinsame Politik (Bad-Control-Problem). Vorperioden-Niveaus × Zinspfad erfassen die unterschiedliche Rateneinwirkung auf verschuldete bzw. fragmentierungsanfällige Länder, ohne selbst Outcome zu sein.
2. **R10:** laufender Spread und laufende Schuldenquote wie in v2 (Robustheit).
3. **Kollinearitätsregel (vorab, vor jedem Blick auf Outcomes):**
   - Messgröße: Anteil der Expositionsvarianz, der nach FE **und** den Kontrollen aus 1 verbleibt, relativ zum Anteil nach FE allein.
   - **Liegt er unter 25 %:** Die Power wird mit der verbleibenden Variation neu simuliert. Übersteigt der MDE dann 0,3 Skalenpunkte pro SD, wird das Dosisdesign als **nicht in der Lage, NZB-Verlust- und Fiskalkanal zu trennen,** berichtet. Es gibt dann keinen kausalen Anspruch; H1 und deskriptive Evidenz stehen im Vordergrund.
4. **Zusätzlicher Test F6:** Das Dosisdesign mit Schuldenquote 2019–2021 × Einlagensatz *anstelle* der Exposition als „Placebo-Kanal". Berichtet wird, welcher der beiden Terme die Variation trägt, wenn beide enthalten sind.
