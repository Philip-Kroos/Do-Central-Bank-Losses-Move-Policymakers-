# Pre-Analysis-Plan – Änderung v2 („Loss-Salience and Rate Advocacy")
**Datum:** 11.09.2026, 10:03 UTC · **Freigabe:** Philip (Chat, 11.09.2026) · **Status:** eingefroren; SHA-256 in `docs/pap_v2_amendment.sha256`

## 0. Anlass und Offenlegung
- **Auslöser:** Die vorab festgelegte Go/No-Go-Regel (v1 §4) war nicht erfüllt, sie beruht nur auf Zählungen (Nachtrag v1.5).
- **Was bis zu diesem Zeitpunkt gelesen wurde:** 18 Passagen mit Y1-Prefilter-Treffern (Präzisionsprüfung, keine Kodierung). **Keine** Passage zur Zinsstance wurde gelesen oder klassifiziert. Bekannt sind nur Zählungen je NZB und Halbjahr.
- **Was diese Änderung ersetzt:** v1 §3.2 (primäres Outcome), §3.3 (Spezifikation), §3.5 (Falsifikation) und §6 (Klassifikator). Alle anderen Teile von v1 gelten weiter.

## 1. Frage und Hypothesen
**Frage:** Plädieren Gouverneure für niedrigere Zinsen, nachdem ihre eigene NZB erstmals einen Nettoverlust ausgewiesen hat?

| # | Hypothese | Status |
|---|---|---|
| **H1** | Nach dem ersten veröffentlichten Nettoverlust wird die Zinsstance des Gouverneurs dovisher (β_N < 0), relativ zu noch nicht und nie behandelten Gouverneuren | **primär** |
| H2 | **Knick bei null:** Der Nettoverlust wirkt stärker als ein durch Rückstellungen vollständig gedeckter Bruttoverlust (β_N − β_G < 0) | sekundär |
| H3 | **Dosis:** Die Stance sinkt im Carry-Maß (Treatment B, demeant) | sekundär |
| H4 | **Druck:** Der Effekt ist größer bei wiederernennbaren Gouverneuren und bei ehemaligen Ministern | sekundär |
| H5 | **Handlungen:** Nach dem ersten Nettoverlust ändern NZBs ihre Rückstellungs- oder Ausschüttungspolitik zugunsten der Puffer | sekundär, deskriptiv |
| H6 | **Out of Sample:** Die Episode ab 2026H2 wird separat vorhergesagt und berichtet | separat |

Theoretische Grundlage: Proposition aus `model/verify_model.py`. dr*/dω < 0 hält in allen zulässigen Ziehungen mit Reserven über dem Banknotenumlauf.

## 2. Stichprobe
- **Sprecher:** Leiter der 20 NZBs (ohne BG), inklusive kommissarischer Leiter. Direktoriumsmitglieder bilden eine separate Gruppe (Placebo, F2).
- **Korpus:** BIS-Extrakt, Reden vom 01.01.2016 bis 30.06.2026. Die Zuordnung erfolgt über `code/corpus/bis_affiliation.py`; nur autorenkonsistente Einträge.
- **Einheit:** Gouverneur × Halbjahr; Zellen ohne stance-relevante Passage entfallen.
- **Übergangshalbjahr:** Das Halbjahr, in dem die Verlustveröffentlichung liegt, wird für die betroffene NZB ausgeschlossen.

## 3. Outcome
**Einheit der Messung:** 5-Satz-Passage, Name, Institution und Land maskiert.
- **Topic Y4 (Zinsstance):** Die Passage äußert eine Präferenz oder Einschätzung zur **Richtung oder zum Tempo der Leitzinsen bzw. zum geldpolitischen Kurs**. Reine Inflationsprognosen ohne Politikbezug zählen nicht.
- **Position:** −1 = für niedrigere Sätze, frühere oder größere Senkungen, langsamere Erhöhungen, Warnung vor Überstraffung · 0 = neutral, datenabhängig ohne Richtung, rein berichtend · +1 = für höhere Sätze, mehr oder schnellere Straffung, Warnung vor zu früher Lockerung.

**Primäres Outcome:** Mittel der Positionen aller Y4-Passagen einer Zelle (inklusive 0).
**Sekundär:** (Anteil +1) − (Anteil −1).

## 4. Treatment
- **N (primär):** 1 in Halbjahren, die nach der ersten offiziellen Veröffentlichung eines Nettoverlusts beginnen. Nettoverlust heißt, der Verlust mindert das Eigenkapital oder wird vorgetragen. Steuertechnische Verluste sind ausgeschlossen (Flag). Innerhalb des Fensters bis 2026H1 wirkt N absorbierend.
- **G (für H2):** 1 in Halbjahren nach der ersten Veröffentlichung eines Bruttoverlusts, der vollständig durch Rückstellungen gedeckt wurde, ohne Nettoverlust.
- **Datenquelle:** `data/hand/ncb_results_v0.csv`.
  - Fehlt ein Veröffentlichungsdatum, gilt der 31.03. des Folgejahres.
  - NZBs, deren Status bis zur Schätzung nicht belegt ist, werden **ausgeschlossen**, nicht als unbehandelt gezählt.

## 5. Schätzung (Hauptspezifikation, fixiert)
1. **Schätzer:** Imputationsschätzer (Borusyak–Jaravel–Spiess).
   - Das Modell y = α_Gouverneur + γ_Halbjahr + δ'X wird auf unbehandelten Beobachtungen geschätzt.
   - ATT = gewichtetes Mittel (Gewicht = Anzahl Passagen) der Differenz beobachtet − imputiert über behandelte Beobachtungen.
2. **Kontrollen X:** nationale HICP-Inflation (Vorjahresrate, Halbjahresmittel), 10J-Spread zu Deutschland, Staatsschuldenquote. Die Schuldenquote ist Pflicht (Kanal von Heinemann & Kemper).
3. **Inferenz:**
   - **Primäres p:** Randomisierungsinferenz. Die Kohortenzuordnungen (inklusive „nie") werden über die NZBs der Stichprobe permutiert, 999 Ziehungen, zweiseitig.
   - **Sekundär:** Cluster-Bootstrap auf NZB-Ebene, 999 Ziehungen.
4. **Event-Study:** Leads −4 bis −1 und Lags 0 bis +4 Halbjahre per Imputation. Pre-Trend-Test als F-Test auf die Leads, zusätzlich Rambachan–Roth-Sensitivität, falls eine verifizierte Implementierung verfügbar ist; sonst als Einschränkung berichtet.
5. **Multiple Tests:** H1 allein primär. H2 bis H4 mit Romano–Wolf-Korrektur.

## 6. Robustheit (vollständig berichtet, keine Auswahl)
- R1: NZB-FE statt Gouverneurs-FE.
- R2: Kern×Halbjahr-FE mit Kern = {AT, BE, DE, FI, FR, LU, NL}.
- R3: ohne Nachfolger, die nach dem Treatment-Beginn angetreten sind.
- R4: ohne Kontrollen.
- R5: sekundäres Outcome (Anteilsdifferenz).
- R6: Treatment G statt N.
- R7: alternatives Klassifikationsmodell bzw. human-only-Stichprobe.
- R8: Callaway–Sant'Anna (not-yet-treated, ohne Kovariaten).

## 7. Falsifikation (vorab)
| # | Test | Erwartung unter H1 |
|---|---|---|
| F1 | Leads −4 bis −1 | gemeinsam null |
| F2 | Direktorium; Treatment = Veröffentlichung EZB-Fehlbetrag GJ 2023 (22.02.2024) | kleiner als β_N oder null |
| F3 | Placebo-Daten: zufällige Ereignisdaten für nie behandelte NZBs (999×) | Verteilung um null |
| F4 | Slowenien 01/2025–02/2026 (kommissarisch ohne Stimmrecht) | deskriptiv berichtet |
| F5 | R2 (Kern×Halbjahr-FE) | Vorzeichen und Größenordnung bleiben |

**Was H1 widerlegt:** ATT ≥ 0 oder ein Effekt, der unter R2 verschwindet, oder signifikante Leads.

## 8. Messprotokoll
- **Klassifikator (Abweichung von v1):** Ein Open-Weight-Modell ist in unserer Umgebung nicht nutzbar (keine Modell-Downloads). **Primär** ist daher ein API-Modell mit fixer Versionsbezeichnung, Temperatur 0 und vollständiger Archivierung von Prompt und Rohantwort je Passage. Robustheit mit einem zweiten Modell, falls möglich.
- **Blindheit:** Alle Passagen des Korpus werden klassifiziert, **bevor** Treatment- oder Kontrolldaten gemergt werden. Die Klassifikationsdatei wird mit Hash eingefroren.
- **Human-Validierung:**
  - Stichprobe: 400 maskierte Passagen, stratifiziert (300 Y4-Prefilter-Treffer von Gouverneuren über NZB-Größengruppen und die Perioden vor/ab 2022; 50 Direktorium; 50 Nicht-Treffer).
  - Doppelkodierung: 100 Passagen durch einen zweiten Kodierer.
  - Schwelle: Krippendorffs α ≥ 0,667 (Mensch–Mensch, Y4-Position). Liegt α darunter, wird das Codebuch überarbeitet **vor** dem Volllauf.
  - Berichtet werden außerdem Mensch–Modell-α und Konfusionsmatrix.

## 9. Power
Die Power wird vor jeder Klassifikation mit den **tatsächlichen** Passage-Zählungen je NZB-Halbjahr und der beobachteten Kohortenstruktur neu simuliert (`power/power_sim_actual_counts.py`). Das Ergebnis wird hier als Nachtrag ergänzt, ohne die Spezifikation zu ändern.

## 10. Abweichungen
Jede Abweichung wird mit Datum, Grund und Vergleich zur ursprünglichen Spezifikation in `docs/deviations.md` festgehalten.
