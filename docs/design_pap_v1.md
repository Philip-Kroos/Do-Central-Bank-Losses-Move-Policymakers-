# /design — The Accountant in the Committee
**Pre-Analysis-Plan, Entwurf v1** · Stand 10.09.2026 · Status: **nicht registriert**, wartet auf Korpuszählung und deine Freigabe

Dieses Dokument deckt die Workflow-Schritte 3–5 ab: Design, Power und Datenstruktur. Es enthält keine Ergebnisse. Alle Zahlen stammen entweder aus Quellen (zitiert), aus eigenen Rechnungen auf Quellenzahlen (`[OUR CALC]`) oder aus Simulationen mit Annahmen (`[ASSUMPTION]`).

---

## 0. Was sich seit der letzten Version geändert hat

1. **Zwei meiner eigenen Vorhersagen sind durch den Modell-Audit gefallen.**
   - *„Falke will Verkäufe, Buchhalter lehnt sie ab"* hält nur in 65 von 266 zulässigen Parameterziehungen. Ein verlustaverser Gouverneur senkt den teuren Zins und weicht auf Verkäufe aus, wenn der Verlust pro verkauftem Euro klein ist.
   - *„Höhere Portfolio-Duration → weniger Verkäufe"* hält in 251 von 266 Ziehungen, also nicht robust.

   Beide Vorhersagen sind gestrichen (`model/verify_model.py`, Audit-Log im Docstring).

2. **Die Institutionen sind jetzt an einer Primärquelle geprüft.** Grundlage ist das Bulletin der Banque de France 260/6 (Arrata & Gentil) zusammen mit dem EZB-Beschluss (EU) 2016/2248.
   - Staats- und Agency-Anleihen, die seit 2015 gekauft wurden, sind weder im Risiko noch im Ertrag gepoolt.
   - Einlagen der Banken sind gepoolt. Die nicht gepoolten Anleihen werden aus diesem gepoolten Topf finanziert. Dafür führt jede NZB einen Pool-Nettoaktivposten, der zum Referenzsatz verzinst wird: bis Ende 2024 der Hauptrefinanzierungssatz, seit 1.1.2025 der Einlagensatz.
   - **Folge:** Pro Einheit Kapitalschlüssel variieren die NZB-Ergebnisse vor allem über die Rendite des eigenen Staatsanleiheportfolios. Das bestätigt die Kernannahme; der Mechanismus ist jetzt belegt, die Herleitung stammt von uns.

3. **Der Killer-Angriff „Exposition = Kernland" ist schwächer als befürchtet.** Nettozinsergebnis nach Reallokation pro Prozentpunkt Kapitalschlüssel, gerechnet aus der Tabelle der Banque de France `[OUR CALC]`:

   | | 2023 | 2024 |
   |---|---|---|
   | Deutschland | −0,71 Mrd. € | −0,69 Mrd. € |
   | **Frankreich** | **−0,74 Mrd. €** | **−0,80 Mrd. €** |
   | Spanien | −0,48 Mrd. € | −0,54 Mrd. € |
   | Italien | −0,37 Mrd. € | −0,38 Mrd. € |

   Frankreich verliert pro Schlüsselanteil mehr als Deutschland, Spanien mehr als Italien. Die Rangfolge der Verluste deckt sich nicht mit der Falken-Tauben-Rangfolge. Einschränkung: Das ist Nettozinsergebnis, nicht GuV nach Rückstellungen, und nur für vier NZBs.

4. **Das Direktorium ist kein Null-Placebo.** Auch die EZB selbst schreibt Verluste (2023: −1,3 Mrd. €). Das Direktorium ist daher eine Vergleichsgruppe mit **niedrigem ψ**: kein nationaler Fiskalprinzipal und nicht verlängerbare Amtszeiten. Eine Gruppe ohne Exposition ist es nicht.

5. **Neuer Kontext 2026: ein zweiter Straffungszyklus.** Die EZB erhöhte im Juni 2026 um 25 bp auf einen Einlagensatz von 2,25 %. Für heute (10.09.2026) wird eine weitere Erhöhung auf 2,50 % erwartet; das Ergebnis ist hier noch nicht geprüft. Steigende Sätze bei weiter hohen Beständen verschärfen die NZB-Verluste erneut. Das ist eine **zweite, vorab registrierbare Treatment-Episode**, keine rein historische Replikation.

6. **Power:** Das Design trägt nur, wenn das Thema häufig genug vorkommt; Details in §4.

---

## 1. Frage und Beitrag

**Frage:** Verschiebt die GuV der eigenen Notenbank, welche Instrumente ein Zentralbanker öffentlich befürwortet?

**Ein Satz:** Wenn Gouverneure in die Verlustzone ihrer eigenen NZB geraten, befürworten sie Instrumente, die deren GuV verbessern, bei gleicher Haltung zur Inflation. [OUR CLAIM, zu testen]

**Nächste Papers** (Details in der Literaturkarte):
- Goncharov, Ioannidou, Schmalz (JF 2023): Diskontinuität der Gewinnverteilung bei null, Querschnitt.
- Heinemann & Kemper (2026): LLM-Scores, TWFE mit Staatsschulden, ausdrücklich forensisch und korrelativ.
- Grodecka-Messi, Kliem, Müller (2025): eine einzelne Institution, Makro-Outcome.

---

## 2. Theorie: verifizierte Propositionen

Gouverneur *i* wählt seine befürworteten Einstellungen für Zins *r*, unverzinsten Reserveanteil *q* und aktive Verkäufe *a*. Er minimiert makroökonomische Kosten *C(r,q,a; g)* abzüglich *ω·Π(r,q,a)*.
- *g* = wahrgenommener Inflationsdruck
- *Π* = NZB-Ergebnis pro Einheit Kapitalschlüssel
- *ω = ψ·(1 + ℓ·1{Π + Puffer < 0})*
- *ψ* = Gewicht auf die eigene GuV, *ℓ* = Verlustaversion mit Referenzpunkt null

| Proposition | Aussage | Prüfung |
|---|---|---|
| **P1 Stance-Neutralität** | Bei ω = 0 gilt q* = 0 und ∂q*/∂g = 0; ∂q*/∂ω > 0 | symbolisch ✓ |
| **P2 Offenbarte GuV-Monotonie** | Das GuV-Ergebnis der befürworteten Instrumentenkombination steigt schwach in ω, für jede Kostenfunktion | numerisch 266/266 ✓ (folgt auch aus monotoner Komparativer Statik) |
| **P3 Nicht gepoolte Heterogenität** | Höhere eigene Portfoliorendite *s* → mehr befürwortete Verkäufe (bei ω > 0) | numerisch 266/266 ✓ |
| **P4 Gepooltes Instrument braucht den Knick** | Die Ersparnis aus niedrigerer Reservenverzinsung ist pro Schlüsselanteil für alle NZBs gleich. Unterschiede in q* entstehen daher nur über ψ oder den Eintritt in die Verlustzone | symbolisch ✓ |

**Konsequenz aus P4, der zentrale Punkt der Theorie:** Mit linearen Präferenzen über Gewinne wären sich alle Gouverneure bei der Reservenverzinsung einig. Heterogenität setzt Referenzabhängigkeit bei null voraus. Das Paper testet damit **Verlustaversion von Zentralbankern mit Referenzpunkt Nullgewinn**. Genau diese Präferenzstruktur impliziert die Diskontinuität bei Goncharov et al., die dort nur als Querschnittsfakt gezeigt wird.

---

## 3. Empirisches Design

### 3.1 Einheiten, Zeitraum, Treatment
- **Einheiten:** 20 NZB-Gouverneure (Bulgarien ab 2026 separat), dazu das Direktorium als Niedrig-ψ-Vergleich.
- **Zeitraum:** Halbjahre 2016H1–2027H1.
- **Treatment A (gestaffelt):** D_it = 1 ab dem Halbjahr nach der ersten veröffentlichten Verlust- oder Nullausschüttung der NZB. Das Datum ist die Veröffentlichung des Geschäftsberichts. Beispiel Bundesbank: 2023 Null nur dank Rückstellungen, 2024 Verlust.
- **Treatment B (kontinuierlich):** E_it = (S_i/k_i)·(ref_t − s_i), also der NZB-spezifische Carry-Verlust pro Schlüsselanteil. s_i wird aus den Renditen der Kaufperiode 2015–2022 konstruiert und ist damit vorbestimmt.

### 3.2 Outcomes (Codebuch v0, Passage-Ebene, 5-Satz-Segmente wie bei Heinemann & Kemper)

| Label | Thema | Position (−1 / 0 / +1) |
|---|---|---|
| Y1 | Reservenverzinsung, Mindestreserve (Quote und Verzinsung), Tiering, Gebühren | −1 Verzinsung halten/erhöhen · 0 deskriptiv · **+1 Verzinsung senken / unverzinste Reserven ausweiten** |
| Y2 | Eigene Verluste, Kapital, Rückstellungen, Rekapitalisierung | −1 „Verluste irrelevant/temporär" · +1 „Verluste sind eine Beschränkung/Sorge" |
| Y3 | Bilanzgröße, QT-Tempo, aktive Verkäufe | −1 langsamer/stoppen · +1 schneller/aktiv verkaufen |
| Y4 | Zinsstance | −1 dovish · +1 hawkish |
| Y5 | Begründung, sofern Y1 ≠ 0 | *Effizienz/Implementierung* · *GuV/Fiskalisch* · *Bankengewinne/Fairness* |

**Primäres Outcome:** Y1-Position. **Sekundär:** das GuV-implizierte Befürwortungsindex (P2). Dafür wird jede Y1/Y3/Y4-Position mit dem NZB-spezifischen Grenzeffekt auf Π gewichtet, berechnet aus deiner Bilanzpipeline.

**Mechanismus:** Y5 trennt das GuV-Motiv von allgemeiner Stimmung gegen Bankengewinne (T6).

### 3.3 Hauptspezifikation (vor den Ergebnissen fixiert)

y_it = α_i + γ_t + β·D_it + X_it'δ + ε_it

- **y_it:** gewichteter Mittelwert der Y1-Positionen, Gewichte = Anzahl Passagen.
- **α_i:** Gouverneurs-FE; Robustheit mit NZB-FE.
- **γ_t:** Halbjahres-FE.
- **X_it:** nationaler HICP, 10J-Spread zu Bunds, Schuldenquote. Die Schuldenquote ist Pflicht, weil sie der Kanal von Heinemann & Kemper ist.
- **Schätzer:** Callaway–Sant'Anna mit not-yet-treated als Kontrolle; Sun–Abraham als Robustheit.
- **Sensitivität:** Rambachan–Roth-Bounds für Verletzungen paralleler Trends.
- **Inferenz:** Randomisierungsinferenz durch Permutation der Kohorten über NZBs als primäres p; Wild-Cluster-Bootstrap auf NZB-Ebene als sekundäres p.
- **Mehrere Outcomes:** Romano–Wolf über Y1–Y4.

### 3.4 Identifikationsannahmen (formal)
- **A1 (parallele Trends):** Ohne Eintritt in die Verlustzone hätten sich die Y1-Positionen früher und später betroffener NZBs, bedingt auf α_i, γ_t, X_it, parallel entwickelt.
- **A2 (keine Antizipation):** Keine Verschiebung vor der Veröffentlichung. *Bedrohung:* Verluste waren projiziert (IMF 2023). *Antwort:* alternatives Treatment-Datum „erste projizierte Verlustmeldung" plus Honest DiD.
- **A3 (Timing exogen zu Präferenzen):** Der Zeitpunkt des ersten Verlusts ergibt sich aus s_i und den Rückstellungspuffern, die vor 2022 gebildet wurden. Er ist nicht Ergebnis der Präferenzen des amtierenden Gouverneurs. *Test:* Puffer und s_i regressiert auf Y4-Positionen vor 2022.
- **A4 (Sprecherselektion):** Wer über das Thema spricht, ist nicht selbst Treatment-Folge. *Test:* extensive Marge, also P(Y1 erwähnt), als eigenes Outcome.

### 3.5 Falsifikationstests (vorab festgelegt)

| # | Test | Erwartung unter H0 „nur Nationalität/Präferenz" | Erwartung unter H1 „Verlustaversion" |
|---|---|---|---|
| F1 | Y4 (Zinsstance) als Outcome | Effekt ≈ β bei Y1 | kein bzw. schwächerer Effekt |
| F2 | Themen ohne Bilanzbezug (Klima, Aufsicht) | beliebig | kein Effekt |
| F3 | Pre-Trends 2016–2022 | — | flach |
| F4 | Direktorium (Niedrig-ψ) | gleicher Effekt | kleinerer Effekt |
| F5 | Kernland×Zeit-FE | Effekt verschwindet | Effekt bleibt |
| F6 | Y5 = „Bankengewinne/Fairness" als Outcome | Effekt | kein Effekt |
| F7 | Heterogenität: wiederernennbare Gouverneure; NZBs ohne automatische Rekapitalisierung | kein Unterschied | größerer Effekt |

### 3.6 Out-of-Sample-Test (Episode 2026/27)
1. **Vor Registrierung:** E_i und der Verluststatus werden mit Stand der Geschäftsberichte 2025 fixiert. Daraus folgt eine vorhergesagte Rangfolge der Unterstützung für eine höhere Mindestreserve oder niedrigere Verzinsung.
2. **Nach Registrierung:** Alle Aussagen von Registrierungsdatum bis drei Monate nach der Mindestreserve-Entscheidung werden blind kodiert.
3. **Test:** Spearman-Rangkorrelation von Vorhersage und kodierter Position. Schwelle und Test werden vorab festgelegt.

**Termin:** Die nächsten geldpolitischen Sitzungen sind am 29.10. und 17.12.2026. Operative Beschlüsse können auch außerhalb dieser Sitzungen fallen.

---

## 4. Power (Workflow-Schritt 4)

`power/power_sim.py`; 250 Wiederholungen × 199 Permutationen je Zelle. **Alle Inputs sind `[ASSUMPTION]`.**

| Effekt β (Skala −1 bis +1) | 0,25 | 0,5 | 1 | 2 | 4 |
|---|---|---|---|---|---|
| 0,00 (Size) | 0,04 | 0,04 | 0,04 | 0,06 | 0,06 |
| 0,20 | 0,06 | 0,15 | 0,24 | 0,46 | 0,65 |
| 0,30 | 0,12 | 0,22 | 0,49 | 0,72 | 0,92 |
| 0,45 | 0,21 | 0,46 | **0,83** | 0,99 | 1,00 |
| 0,60 | 0,25 | 0,69 | 0,95 | 1,00 | 1,00 |

Spalten = relevante Passagen pro Gouverneur-Halbjahr.

**Lesart:**
- Mit einer relevanten Passage pro Gouverneur-Halbjahr ist ein Effekt von 0,45 Skalenpunkten erkennbar. Das entspricht grob einem Sprung von „deskriptiv" zu „eher für Kürzung".
- Bei 0,5 Passagen oder weniger ist das Design für plausible Effekte unterpowert.
- Die Simulation ist **optimistisch**: Sie nimmt eine konstante Themenfrequenz an, obwohl das Thema vor 2022 fast fehlt.

**Warnsignal aus den Daten von Heinemann & Kemper:** Ihr BIS-Korpus enthält 2.196 Gouverneursreden über rund 27 Jahre, mit starkem Übergewicht der großen Länder. Das spricht dafür, dass Reden allein **unter** einer Passage pro Halbjahr zur Reservenverzinsung liegen. Diese Einschätzung ist `[UNVERIFIED]`; die Zählung klärt sie.

**Go/No-Go-Regel (vorab, nur auf Basis von Zählungen, ohne Blick auf Positionen):**
1. **Weiter mit Y1 als primärem Outcome,** wenn für 2022H1–2026H1 im Mittel mindestens eine Y1-Passage pro Gouverneur-Halbjahr über alle Quellen vorliegt (BIS, NZB-Websites, Interviews, Anhörungen), bei mindestens 12 NZBs mit Passagen.
2. **Sonst:** Das primäre Outcome wechselt auf den GuV-Index (P2), gepoolt über Y1, Y3 und Y4, und die extensive Marge wird co-primär.
3. **Wenn auch das unter einer Passage bleibt:** Stopp dieses Designs und Rückfall auf ein reines NZB-Aktionsdesign (Rückstellungen, Ausschüttungsentscheidungen, Kommunikation in Geschäftsberichten).

---

## 5. Daten (Workflow-Schritt 5): Variablenverzeichnis v0

| Variable | Ebene | Quelle | Konstruktion | Status |
|---|---|---|---|---|
| `gov_id`, `ncb`, `term_start`, `term_end` | Gouverneur | NZB-Websites | Handkodierung | offen |
| `reappointable` | Gouverneur-Zeit | NZB-Gesetze | 1, wenn verlängerbar | offen |
| `speech_id`, `date`, `source`, `language`, `audience` | Rede | BIS-Extrakt, CBS, NZB-Websites | Parser | wartet auf Daten |
| `passage_id`, `text` | Passage | abgeleitet | 5-Satz-Segmente | Code folgt |
| `y1_topic`, `y1_pos` … `y5_just` | Passage | LLM + Human-Validierung | Codebuch v0 | Codebuch v0 steht |
| `holdings_S` | NZB-Monat | ECB Data Portal (PSPP/PEPP je Jurisdiktion) | Bestand / Kapitalschlüssel | deine Pipeline |
| `own_yield_s` | NZB | ECB-Renditen, Kaufvolumen je Monat | volumengewichtete Rendite der Kaufperiode (Ansatz wie Gebauer et al.) | offen |
| `ref_rate` | Zeit | EZB | Hauptrefinanzierungssatz bis 2024, danach Einlagensatz | öffentlich |
| `nii_after_realloc`, `profit`, `provisions`, `distribution` | NZB-Jahr | Geschäftsberichte | Handextraktion | offen |
| `first_loss_pubdate` | NZB | Geschäftsberichte, Pressemitteilungen | Datum | offen |
| `statute_loss_rule` | NZB | NZB-Gesetze, EZB-Konvergenzberichte | Vortrag / Rekapitalisierung / Reserveauflösung | offen |
| `private_shareholders` | NZB | NZB-Websites | Dummy | `[UNVERIFIED]` |
| `hicp`, `spread10y`, `debt_gdp` | Land-Halbjahr | ECB Data Portal, Eurostat | Halbjahresmittel | öffentlich |

---

## 6. Abweichungen und Offenlegung
- Jede Abweichung vom Plan wird mit Datum und Begründung im Anhang F dokumentiert.
- Berichtet werden alle gerechneten Spezifikationen.
- Die Klassifikation läuft blind, bevor Expositionsdaten gemergt werden.
- **Primärmodell:** Open-Weight-LLM mit gepinnter Version. **Robustheit:** ein API-Modell.
- **Human-Validierung:** 500 Passagen, stratifiziert nach Thema und Sprache; Krippendorffs α wird berichtet.

## 7. Entscheidungen, die du treffen musst (Gates)
1. **Freigabe der Frage und der Propositionen P1–P4**, inklusive der gestrichenen Verkaufs-Vorhersage.
2. **Treatment A oder B als Hauptspezifikation.** Meine Empfehlung: A, weil P4 den Knick bei null verlangt; B dient als Dosis-Wirkungs-Evidenz.
3. **Go/No-Go-Schwellen in §4:** Sind sie für dich akzeptabel, bevor wir zählen?
4. **Registrierung** unter deinem Namen auf OSF, sobald die Zählung vorliegt.

---

## Nachtrag v1.1 (10.09.2026, abends)

### A. Kontext verifiziert
- Die EZB hat heute den Einlagensatz von 2,25 % auf 2,50 % erhöht, die zweite Erhöhung seit Juni 2026. Eine Entscheidung zur Mindestreserve wird in den Meldungen dazu nicht erwähnt. Das ist noch kein Beleg, dass keine gefallen ist; das Protokoll (Accounts) wird geprüft, sobald es erscheint.
- Die EZB selbst schrieb Verluste: 2023 −1,3 Mrd. € (nach Auflösung von 6,6 Mrd. € Rückstellung), 2024 −7,9 Mrd. €, 2025 −1,3 Mrd. €. In allen drei Jahren gab es keine Gewinnausschüttung an die NZBs. Das bestätigt die Umdeutung des Direktoriums zur Niedrig-ψ-Gruppe.

### B. Treatment-Timing aus handerhobenen Daten (7 NZBs + EZB)
Datei: `data/hand/ncb_results_v0.csv` (jede Zeile mit Quelle). Abgeleitet mit `code/exposure/treatment_dates.py`.

| NZB | Erster Brutto-Verlust (GJ) | Erster Netto-Verlust (GJ) | Treatment „netto" an | Ausstieg | Anmerkung |
|---|---|---|---|---|---|
| NL | 2022 | 2022 | 2023H2 | — | Verluste bis 2025, weitere erwartet |
| BE | 2022 | 2022 | 2023H2 | — | Erster Verlust seit ~70 Jahren; kein variables Dividend |
| AT | 2023 | 2023 | 2024H2 | — | 2024 erstmals negatives Eigenkapital |
| DE | 2023 | 2024 | 2025H2 | — | Netto 2024 **abgeleitet** (−27,8 + 8,6 Mrd. €), prüfen |
| FR | 2023 | 2024 | 2025H2 | GJ 2025 | 2025 Gewinn von 8,1 Mrd. €, Grund noch ungelesen |
| ES | 2023 | nie | — | — | 2023 und 2024 null dank Rückstellungen, 2025 Gewinn |
| IT | 2023 | nie | — | — | Netto positiv über Rückstellungen und Steuergutschrift |

**Befund:** Die Kohorten mischen Falken und Nicht-Falken. DE und FR fallen in dieselbe Kohorte, NL/BE/AT sind früh, IT/ES nie netto betroffen. Der Zeitpunkt folgt sichtbar den Puffern: Die Bundesbank hat große Rückstellungen und kommt deshalb spät. Das stützt Annahme A3.

**Ausstiege (FR) liefern einen symmetrischen Test:** Kehrt die Befürwortung nach dem Rückweg in die Gewinnzone um?

**Offene Punkte:**
- Publikationsdaten fehlen teils; ersatzweise gilt der 31.3. des Folgejahres, markiert.
- DE, ES, IT, NL, EZB sind links-zensiert, weil die Jahre 2021/2022 noch fehlen.
- Die Definition „keine Überweisung an den Staat" ist für DE ungeeignet: Überweisungen gibt es seit GJ 2020 nicht, durch Rückstellungsentscheidung und nicht durch Verluste.
- **13 NZBs fehlen noch.**

### C. Power-Sensitivität mit beobachteter Kohortenstruktur
Die Anteile der sieben erhobenen NZBs wurden auf 20 hochskaliert (`power/power_sim_observed_cohorts.py`, 150 × 199).

| β | 0,5 | 1 | 2 | Passagen/Halbjahr |
|---|---|---|---|---|
| 0,00 | 0,03 | 0,07 | 0,06 | |
| 0,30 | 0,25 | 0,52 | 0,79 | |
| 0,45 | 0,49 | **0,84** | 0,97 | |

Das Ergebnis ist praktisch unverändert gegenüber v1. Der Engpass bleibt die Themenfrequenz, nicht die Kohortenstruktur.

### D. Kostspielige Handlungen als zusätzliche Outcomes (gegen den Cheap-Talk-Einwand)
- **NBB:** Am 27.03.2024 änderte der Regentschaftsrat die Reserve- und Dividendenpolitik; Vorrang hat nun der Wiederaufbau der Reserven. Kurz nach Bekanntgabe des Verlusts 2022 fiel die börsennotierte NBB-Aktie am 21.09.2022 um mehr als 27 %. Das sind datierte, kostspielige Handlungen bzw. Marktreaktionen.
- **Banca d'Italia:** Der Gouverneur betonte bei der Bilanzvorlage 2024, positive Ergebnisse seien für die finanzielle Unabhängigkeit wichtig, obwohl Gewinn kein Ziel sei. Das ist Evidenz für Salienz und wird unter Y2 kodiert.
- **Neue Variable:** `capital_policy_change` (NZB-Jahr), also Änderungen an Rückstellungs- oder Ausschüttungsregeln mit Datum.

### E. Pipeline-Stand
- `run_go_nogo.py` läuft Ende-zu-Ende: Laden (schema-tolerant), Segmentieren, mehrsprachiger Prefilter, Go/No-Go-Bericht. Mit synthetischen Daten getestet; die echten Korpora fehlen noch.
- 10 Unit-Tests grün (`tests/test_pipeline.py`).
- Codebuch v1: `docs/codebook_v1.md`.

---

## Nachtrag v1.2 (10.09.2026, später Abend)

### A. Treatment-Daten: 13 NZBs + EZB
`data/hand/ncb_results_v0.csv`: 43 Zeilen, jede mit Quelle. Neu hinzugekommen sind FI, PT, IE, GR, SK und LV (LV nur teilweise).

| Definition | GJ 2022 | GJ 2023 | GJ 2024 | nie (bisher) |
|---|---|---|---|---|
| **Netto-Verlust** (belastet Eigenkapital oder wird vorgetragen) | NL, BE, SK | AT | DE, FR | ES, FI, IE, IT, PT, GR |
| **Brutto-Verlust** (vor Rückstellungen) | NL, BE, SK | AT, DE, FR, ES, FI, IE, IT, PT | — | GR |

**Befunde:**
1. **Die Netto-Definition teilt das Panel ungefähr hälftig.** Viele NZBs haben Nettoverluste durch Rückstellungen vermieden (ES, FI, PT, IT, IE). Diese Gruppe ist eine natürliche Kontrollgruppe mit derselben Brutto-Belastung. Damit wird der Knick bei null testbar: **gleicher Bruttoverlust, unterschiedliche Nettosalienz**. Das ist der sauberste Vergleich im Design und entspricht Proposition P4.
2. **Griechenland hat keinen Bruttoverlust**, 2024 sogar einen Vorsorgegewinn von 31,9 Mio. €. Das passt zum Mechanismus der eigenen Portfoliorendite (hochverzinste heimische Anleihen) und liefert eine externe Plausibilisierung des Expositionsmaßes.
3. **Portugal 2025:** Der Nettoverlust von −1,4 Mio. € ist rein steuertechnisch (latente Steuern) und wird per Flag `net_loss_technical` aus der Netto-Definition ausgeschlossen.
4. **Slowakei:** Das negative Eigenkapital ist ein Altbestand aus der Zeit vor 2022. Die Salienz-Basislinie ist dort eine andere; das wird als Heterogenitätsdimension markiert.

### B. Power mit Netto-Definition
Hochskaliert auf 20 NZBs, davon 9 behandelt (`power/power_sim_net_definition.py`, 150 × 199):

| β | 1 | 2 | 4 | Passagen/Halbjahr |
|---|---|---|---|---|
| 0,00 | 0,07 | 0,03 | 0,05 | |
| 0,30 | 0,50 | 0,83 | 0,95 | |
| 0,45 | **0,82** | 0,99 | 1,00 | |

Weniger behandelte Einheiten werden durch mehr Kontrollen und frühere Kohorten ausgeglichen. Der Engpass bleibt die Themenfrequenz.

### C. Gouverneursliste (Primärquelle: EZB-Seite zum Rat, Stand 10.06.2026)
- Alle 21 amtierenden Gouverneure sind erfasst, außerdem das Direktorium mit Amtszeiten.
- **Hohe Fluktuation 2024–2026:** Mindestens NL, PT, HR sind datiert. Laut Namensabgleich gibt es neue Amtsinhaber außerdem in FR, ES, AT, SI und EE; die Daten dazu fehlen noch. **Bedrohung T10 steigt:** Neue Gouverneure treten mitten in die Verlustphase ein. Die Hauptspezifikation braucht daher neben Gouverneurs-FE auch NZB-FE als gleichrangige Robustheit.
- **Wechsler zwischen den Ebenen** ermöglichen einen Test innerhalb derselben Person (neuer Falsifikationstest **F8**):
  - *Panetta:* Direktorium bis 31.10.2023, danach Banca d'Italia (NZB mit Bruttoverlust, aber ohne Nettoverlust).
  - *Vujčić:* Gouverneur der kroatischen Nationalbank, seit 01.06.2026 EZB-Vizepräsident.
  - Es sind nur zwei Fälle, also Fallstudie und keine Schätzung. Die Vorhersage ist trotzdem scharf: Die Y1-Position sollte sich mit der institutionellen GuV verschieben, die Y4-Position nicht.

### D. Weitere Salienz-Evidenz
- **Portugal:** Der Gouverneur kündigte 2025 an, der Staat solle wegen des Wiederaufbaus der Puffer nicht so bald mit Dividenden rechnen. Die Bank betonte ihre Unabhängigkeit in Finanz- und Rückstellungspolitik. Das wird unter Y2 kodiert und liefert eine Kandidatin für `capital_policy_change`.

### E. Offen
- NZBs: LT, EE, LU, SI, HR, CY, MT fehlen; LV ist unvollständig.
- Viele Einträge sind links-zensiert (GJ 2021/2022 fehlen).
- Startdaten für 17 Gouverneure fehlen, dazu die Vorgänger in FR, ES, AT, SI, EE, HR, MT, CY.
- Einige Publikationsdaten sind angenommen und markiert.

---

## Nachtrag v1.3 (11.09.2026)

### A. Gouverneursliste: 37 Zeilen, davon 18 mit belegtem Amtsbeginn
Neu belegte Wechsel:

| NZB | Vorgänger (bis) | Nachfolger (ab) | Anmerkung |
|---|---|---|---|
| FR | Villeroy de Galhau (01.06.2026) | Moulin (02.06.2026) | Sechs Jahre; die Finanzausschüsse haben nicht blockiert (52 dafür, 58 dagegen; zum Blockieren waren 3/5 nötig) |
| ES | Hernández de Cos (11.06.2024) → Delgado kommissarisch | Escrivá (06.09.2024) | Sechs Jahre, **nicht verlängerbar**; direkt aus dem Ministeramt |
| AT | Holzmann (31.08.2025) | Kocher (01.09.2025–31.08.2031) | Holzmann galt als Falke und stimmte wiederholt gegen die Mehrheit; Kocher war Minister bis März 2025 |
| SI | Vasle (08.01.2025) → Dolenc kommissarisch, **ohne geldpolitisches Stimmrecht** | Dolenc (01.03.2026–29.02.2032) | Rund 14 Monate ohne stimmberechtigten Gouverneur |
| EE | Müller (spätestens Juni 2026) | Kaasik | Wechseldatum `[UNVERIFIED]` |

### B. Konsequenz für die Identifikation (T10)
Jede NZB mit Nettoverlust (NL, BE, SK, AT, DE, FR) hat mindestens einen Gouverneur, dessen Amtszeit **den Treatment-Beginn überspannt**: Knot, Holzmann, Villeroy und vermutlich Wunsch, Kažimír und Nagel (deren Startdaten sind noch zu belegen). **Das Design mit Gouverneurs-FE ist damit machbar.** Nachfolger, die erst nach dem Treatment-Beginn antreten (Kocher, Sleijpen, Moulin), tragen nur über NZB-FE bei. Sie werden in einer Robustheitsprüfung ausgeschlossen.

### C. Neue Heterogeneitätsvariablen (Mechanismus: politischer Druck, F7)
- `former_minister`: belegt für ES (Escrivá), AT (Kocher), PT (Centeno), GR (Stournaras), SK (Kažimír).
- `reappointable`: ES = 0 (gesetzlich). Andere NZBs sind noch zu kodieren.
- `acting_no_vote`: SI 2025-01 bis 2026-02 (Vertretung ohne Stimmrecht). Das ist ein natürlicher Placebo-Zeitraum: Die Befürwortung kann dort keine Abstimmung beeinflussen.

### D. Treatment-Daten
LU ergänzt: GJ 2023 und 2024 jeweils „ausgeglichenes Ergebnis", netto 0. Es fehlen weiterhin LT, EE, HR, CY, MT sowie die Vorperioden 2021/22 für die großen NZBs.

---

## Nachtrag v1.4 (11.09.2026): Expositionsmaß (Treatment B) implementiert

**Code:** `code/exposure/own_yield.py`, `run_exposure.py`, `run_exposure_grid.sh`. **Tests:** 19 grün, davon 9 neu, inklusive End-to-End-Lauf auf synthetischen Daten.

**Definition:** carry_i,t = S_i,t × (s_i,t − ref_t), in Mio. € p.a. und pro Prozentpunkt Kapitalschlüssel. Zusätzlich gibt es eine querschnittlich demeante Version, weil alles Gemeinsame in den Zeit-FE aufgeht.
- **S** = eigene PSPP- und PEPP-Bestände der NZB.
- **s** = kaufgewichtete Rendite dieser Bestände.
- **ref** = Hauptrefinanzierungssatz bis 31.12.2024, Einlagensatz ab 1.1.2025.

**Datengrundlage (belegt):** Die EZB veröffentlicht die PSPP-Bestände je Jurisdiktion samt WAM monatlich. Für das PEPP gibt es die jurisdiktionale Zusammensetzung und die WAM ebenfalls monatlich mit Historie. Die PSPP-Käufe folgten dem Kapitalschlüssel auf Bestandsbasis. Nettokäufe gab es vom 9.3.2015 bis 19.12.2018, danach bis Oktober 2019 nur Reinvestitionen.

**Annahmen mit vorab festgelegtem Sensitivitätsraster (12 Konfigurationen):**
- **A1:** Eigener NZB-Anteil an den Jurisdiktionsbeständen = 8/9 für PSPP. Für PEPP ist der Anteil offen `[UNVERIFIED]` und wird mit 8/9 und 1,0 gerechnet.
- **A2:** Kauflaufzeit = WAM × {0,75; 1; 1,5}.
- **A3:** Tilgungen entweder über Netto-Flüsse oder über eine gleichmäßige Laufzeitleiter.

**Vorab festgelegte Validierung** gegen das Nettozinsergebnis der Banque de France (4 NZBs × 2 Jahre, deskriptiv). Stimmen die Rangfolgen nicht überein, bleibt Treatment A die Hauptspezifikation. Das bekannte Risiko ist die Umkehr FR/DE; siehe `docs/data_download.md`.

**Benötigte Downloads:** sechs öffentliche EZB-Quellen, aufgelistet in `docs/data_download.md`.

---

## Nachtrag v1.5 (11.09.2026): Erste echte Daten – Go/No-Go-Ergebnis und Weichenstellung

### A. Daten erhalten
BIS-Reden (Extrakt bis Juni 2026, 20.728 Reden), PSPP/PEPP-Historien, 10J-Renditen (IRS), AAA-Kurve (YC), Leitzinsen, Eurosystem-Kapitalschlüssel 2024/2026 (Screenshots).
- **CBS-Datensatz:** nicht hochgeladen, derzeit nicht nötig (siehe D).
- **Kapitalschlüssel vor 2024:** fehlt, der Schlüssel 2024 wird rückwärts verwendet (markiert).

### B. Go/No-Go (vorab festgelegte Regel, nur Zählungen, nur Gouverneure, 2022H1–2026H1, 20 NZBs × 9 Halbjahre)
Sprecherzuordnung per Parser (`code/corpus/bis_affiliation.py`, 12 Tests auf echten Beschreibungen, Autorenkonsistenz 99,7 %).

| Kriterium | Ergebnis (BIS, Prefilter = Obergrenze) | Schwelle | Status |
|---|---|---|---|
| Y1-Passagen pro NZB-Halbjahr | 0,38 | ≥ 1 | **nicht erfüllt** |
| NZBs mit Y1-Passage | 9 | ≥ 12 | **nicht erfüllt** |
| Gepoolt Y1+Y3 pro NZB-Halbjahr | 0,88 | ≥ 1 | **nicht erfüllt** |
| NZBs gepoolt | 13 | ≥ 12 | erfüllt |

**Entscheidung nach Regel:** `stop_speech_design` für die Instrumenten-Befürwortung.
- **Sensitivität** (nicht Teil der Regel): Mit allen NZB-Offiziellen inklusive Vizes wäre gepoolt 1,16 und 15 NZBs erreicht. Das wird berichtet, aber nicht als Entscheidungsgrundlage genutzt.
- **Präzision des Prefilters ist gering:** 46 von 91 Worttreffern sind „excess liquidity" (meist deskriptiv), „tiering" trifft auch Energietarife. Die echte Y1-Rate liegt deutlich unter 0,38.
- **Offenlegung:** Zur Präzisionsprüfung wurden 18 Y1-Prefilter-Passagen gelesen, Positionen nicht kodiert. Y4-Passagen wurden nur gezählt, nicht gelesen.

### C. Verfügbarkeit alternativer Outcomes (nur Zählungen)
- **Zinsstance (Y4):** 6,8 Passagen pro NZB-Halbjahr (Obergrenze), 18 NZBs mit Passagen.
- **Balance:** NZBs mit Nettoverlust 571 Passagen vs. NZBs ohne Nettoverlust 600.
- **Konzentration:** DE 271, ES 205, IT 193, FR 156, NL 104, FI 85, IE 68, GR 43, BE 31; übrige ≤ 16; LU und LV 0.
- **Modell:** Proposition-Check `dr*/dω < 0` hält in allen 266 Ziehungen, in denen die Reserven den Banknotenumlauf übersteigen. Das ist im Euroraum seit 2015 der Fall.

### D. Expositionsmaß mit echten Daten (Treatment B)
- **Parser:** stimmt mit den EZB-Webtabellen überein (PSPP DE 435.323, NL 96.593, IT 282.861 Mio. €; PEPP GR 33.649; WAM IT 7,38). 33 Tests grün.
- **Portfoliorendite Ende 2021:** LU −0,41 %, DE −0,36 %, NL −0,21 %, FI −0,07 % … ES 0,87 %, GR 1,00 %, PT 1,25 %, IT 1,32 %.
- **Validierung gegen Banque de France (Rangfolge):** Spearman 0,79 (Netto-Flüsse) bzw. 0,76 (Leiter). IT > ES stimmt; **DE/FR sind vertauscht**, das Risiko war vorab benannt.
  - **Folge laut Vorab-Regel:** Treatment A (publizierte Verluste) bleibt Hauptspezifikation; Carry dient als Dosis-Evidenz.
- **Beobachtung:** AT, BE und SK (Nettoverlust) haben höhere Portfoliorenditen als LU, FI und EE (kein Nettoverlust). Der Treatment-Zeitpunkt folgt also nicht einfach der Rendite, sondern den Puffern. Das hilft gegen T1.

### E. Weichenstellung (Entscheidung von Philip nötig, vor jedem Blick auf Positionen)
1. **Option 1 – Zinsstance als primäres Outcome:** „Machen eigene Verluste Gouverneure dovisher?" Ausreichend Daten; direkt verbunden mit der Inflationsfrage (Gebauer et al.; Riksbank). Nachteil: Das stance-neutrale Vorzeichenmuster entfällt, die Identifikation ruht auf gestaffeltem Timing und FE, effektiv etwa 9 datenreiche Cluster.
2. **Option 2 – NZB-Aktionsdesign** (vorab festgelegter Rückfall): Rückstellungs-, Ausschüttungs- und Kapitalpolitik, Framing in Geschäftsberichten. Balanciert 20 × 10, aber kleines N und nahe an Goncharov et al.
3. **Option 3 (Empfehlung) – Kombination:** Y4 primär; NZB-Aktionen als kostspielige Outcomes; Y1/Y2 nur deskriptiv. **Erfordert eine datierte Änderung des PAP, bevor Y4-Positionen gelesen oder klassifiziert werden.**

---

## Nachtrag v1.6 (11.09.2026): Messung und Schätzung bis zur Datenfreigabe fertig

**Validierung**
- `code/validation/analyse_validation.py` rechnet Krippendorffs α (Paket `krippendorff`, reproduziert das publizierte Referenzbeispiel mit 0,743 / 0,849 / 0,815), Konfusionsmatrizen und den **populationsgewichteten** Prefilter-Recall.
- Gate und Recall-Regel sind präzisiert (siehe Abweichungsprotokoll).

**Klassifikation**
- Universum: 4.442 maskierte Y4-Prefilter-Passagen (1.991 Gouverneure, 2.451 Direktorium), in zufälliger Reihenfolge mit undurchsichtigen IDs, aufgeteilt auf 5 Dateien plus Validierungsdatei.
- Die Schlüsseldatei (ID → NZB/Datum) bleibt privat.
- `klassifikation_tool.jsx`: Modell `claude-sonnet-4-6`, Prompt `PAPv2-Y4-p1`, Temperatur 0, 5 Passagen je Anfrage, Beleg-Zitat muss wörtlich im Text stehen (sonst ein Einzelversuch, dann ungültig). Rohantworten werden archiviert. Die Validierungslogik ist in Node getestet.

**Schätzung**
- `code/estimate/panel.py` und `run_estimation.py` bauen das Gouverneur×Halbjahr-Panel und schätzen H3 (Dosis, studentisierte RI über NZB-Pfade), R9 (Kern×Halbjahr) und H1 (Imputation, RI über NZB-Kohorten).
- **Echte Läufe verweigert der Code**, solange die Klassifikationsergebnisse nicht per Hash eingefroren sind.
- **Trockenlauf mit Zufallspositionen** (`output/dryrun/report.json`, keine Ergebnisse): 193 Zellen, 37 Gouverneure, 18 NZBs; p-Werte 0,73 / 0,84 / 0,51 wie unter null erwartet.
- **Test mit eingebautem Effekt:** Ein synthetischer negativer Dosiseffekt wird mit dem richtigen Vorzeichen erkannt (p < 0,05); ohne Effekt keine Ablehnung.

**Offen für den echten Lauf**
- HICP: Der alte ICP-Datensatz endet Dezember 2025 und wurde am 04.02.2026 durch einen neuen HICP-Datensatz ersetzt.
- Schuldenquote.
- Validierungskodierungen (A und B).
- Treatment-Status für LT, EE, LV, HR, CY, MT, SI (nur für H1 nötig).

---

## Nachtrag v1.7 (11.09.2026): Eigenständig erledigte Arbeiten und harte Grenzen

**Erledigt**
- **Expositions-Sensitivitätsraster:** Alle 12 Konfigurationen sind mit echten Daten gerechnet. Die Korrelation mit der Basisversion ab 2022 liegt bei ≥ 0,98, der Spearman-Wert gegen Banque de France bei 0,74–0,81 (`output/exposure_grid/grid_summary.csv`).
- **Treatment-Daten:**
  - Litauen: 2023 „nicht profitabel", 2024 Gewinn > 20 Mio. €.
  - Erstes datiertes **Druck-Ereignis:** Der litauische Präsident schlägt am 24.01.2025 eine Gesetzesänderung vor, die die Gewinnabführung zur Verteidigungsfinanzierung erhöht.
  - Zypern: Gouverneur Patsalides seit April 2024.
  - Für CY, MT, HR, SI und EE waren keine belastbaren Ergebnisquellen auffindbar. Sie bleiben laut PAP v2 §4 aus dem Ereignisdesign ausgeschlossen; das Dosisdesign enthält sie über das Carry-Maß.
- **Paperentwurf, Abschnitte 2–4** (`paper/main.tex`, PDF): Institutioneller Hintergrund, Modell, Daten und Messung. Nur verifizierte Fakten; alle ausstehenden Zahlen sind als rote Platzhalter markiert. Bibliografieeinträge mit ungeprüften Titeln sind als `[TITLE UNVERIFIED]` gekennzeichnet.

**Harte Grenzen (nicht delegierbar an mich)**
1. **Human-Validierung:** Ein Modell kann nicht die Messung validieren, die es selbst erzeugt. Das Gate verlangt menschliche Kodierer (A: 400 Passagen, B: 100).
2. **Klassifikationslauf:** Die Sandbox hat keinen API-Schlüssel (HTTP 401). Der Lauf ist nur im Artefakt im Browser möglich.
3. **HICP- und Schuldendaten:** Das ECB-Daten-API ist aus der Sandbox gesperrt (HTTP 403) und muss manuell heruntergeladen werden.

---

## Nachtrag v1.8 (11.09.2026): Referee-Pass und Folgen
- **Interner Referee-Bericht** (`docs/referee_report_internal_v1.md`): In dieser Form wäre das Paper für ein Top-5-Journal abzulehnen; für ein Feldjournal eine Major Revision, falls Einwand 1 hält.
- **Wichtigster neuer Befund (ergebnisblind):** Die identifizierende Variation des Dosisdesigns sind zu 92,5 % die eigenen Bestände je Schlüsselpunkt × Zinspfad. Das ist potenziell ein Schuldenkanal. **PAP v2.2** führt daher Vorperioden-Kontrollen × Einlagensatz, eine Kollinearitätsregel und F6 ein.
- **Schuldenquote-Daten sind damit entscheidend:** Ohne sie gibt es keine gültige Hauptschätzung.
- **Messung:** Die Variable „nur Rückblick" ergänzt das Kodier-Tool und den Klassifikator (Prompt p2); dazu Robustheit R11.
- **Literatur:** Titel von Grodecka-Messi et al., Cecchetti & Hilscher sowie Arrata & Gentil verifiziert. Neu aufgenommen: Bartels et al. (2026), Unabhängigkeit und Risiko; IMF WP 2026/040, politische Gouverneurswechsel. Nicht verifizierte Vornamen sind in der Bibliografie durch Initialen ersetzt.
- **Paperentwurf:** Abschnitt 5 (Empirische Strategie) ist aus dem eingefrorenen PAP geschrieben; der Entwurf umfasst jetzt 7 Seiten.

---

## Nachtrag v1.9 (11.09.2026): Schuldendaten selbst beschafft, Kollinearitätsregel ausgewertet, Inferenz korrigiert
- **Schuldenquoten 2019–2021** für alle 20 Euro-NZB-Länder plus BG aus Eurostat-Release 118/2022 (`data/hand/debt_ratio_eurostat_oct2022.csv`), getestet gegen die Überschriftswerte.
- **Kollinearitätsregel (ergebnisblind): nicht ausgelöst.** Schulden × Einlagensatz lässt 99 % der Expositionsvariation nach FE bestehen; die Korrelation innerhalb der FE beträgt 0,09. Der Schuldeneinwand aus dem Referee-Pass trifft das Design damit nicht.
- **Inferenzfehler gefunden:** CR0-studentisierte RI hat mit Kontrollen 9,3 % Size. PAP v2.3 stellt auf CR3-Jackknife um (Size 5,2 %). Power: MDE bei 80 % etwa 0,27 pro SD.
- **Offen:** HICP (Eurostat-Tabelle nur als Bild verfügbar, nicht extrahierbar), Validierungskodierung, Klassifikationslauf.

---

## Nachtrag v1.10 (11.09.2026): OSF-fertige Pre-Registrierung, Anhänge, Replikations-README
- **`docs/preregistration_consolidated_EN.md`** (+ PDF, Hash): englische Konsolidierung des Standes v2.3 mit den Hashes aller eingefrorenen Dokumente. Sie enthält das **konkrete Out-of-Sample-Protokoll H6**:
  - Spearman-Korrelation zwischen der Stance-Änderung und der negativen Expositionsänderung von 2026H1 zu 07/2026–12/2027.
  - Einseitiger Permutationstest, p < 0,05.
  - Die Richtung der Vorhersage folgt aus der Theorie, nicht aus dem geschätzten β.
- **Paperentwurf v3 (10 Seiten):** Anhänge A (Modellverifikation), B (Datenkonstruktion, 12 Expositionsvarianten), C (Codebuch), D (Size und Power), E (Replikation).
- **`README_REPLICATION.md`** nach AEA-Vorlage. Lizenzangaben, die nicht geprüft sind, sind als `[UNVERIFIED]` markiert.
- **Integritätscheck:** Alle eingefrorenen PAP-Dokumente stimmen mit ihren Hashes überein.

---

## Nachtrag v1.11 (11.09.2026): Vollständiger Auswertungsbericht implementiert
- **`run_full_report.py` + `code/estimate/full_report.py`:** Alle vorab festgelegten Schätzungen laufen mit **einem gemeinsamen Permutationsschema**, bei dem alle NZB-Treatments gemeinsam permutiert werden. Das liefert RI-p-Werte je Test und Romano–Wolf für die Sekundärfamilie.
  - **Umgesetzt:** H3, R1, R3, R4, R5, R6, R8 (Callaway–Sant'Anna, Punktschätzung), R9, R10, R11, F1 (Lead der Exposition), F2 (Direktorium, deskriptiv), F3 (Placebo-Daten), F4 (Slowenien), F6, H1, H2 (explorativ), H4, alle 12 Expositionsvarianten.
  - **Output:** LaTeX-Tabelle und Spezifikationsgrafik.
- **Synthetischer Test mit eingebautem Effekt (−0,8 latent):** H3 −0,45 (t −3,0, p 0,02); R1, R4 und alle 12 Varianten erkennen den Effekt; F1-Lead nicht signifikant; H1 erkennt ihn nicht (anderes Treatment, geringe Power).
- **Zwei Planfehler beim Testen gefunden und korrigiert (Abweichungsprotokoll):**
  1. R5 war mathematisch identisch mit dem Hauptoutcome.
  2. F6 hätte nur den H3-Koeffizienten wiederholt.
- **Ehrlicher Hinweis:** R9 (Kern×Halbjahr-FE) hat im synthetischen Lauf sehr breite Intervalle. Der wichtigste Robustheitstest ist also schwach und prüft laut PAP nur Vorzeichen und Größenordnung, nicht Signifikanz.
- **Weiter offen:** HICP, vollständige Kodierung der H4-Attribute, R7 (braucht Validierung), H5-Datensatz.

---

## Nachtrag v1.12 (11.09.2026): H4 abgesichert, H5-Datensatz, Gouverneursliste erweitert

**H4 (Heterogenität) ist jetzt gesperrt, statt auf einer verzerrten Teilstichprobe geschätzt zu werden.**
- Die Attribute decken nur 23 % (ehemalige Minister) bzw. 36 % (Wiederernennbarkeit) der Passagen ab.
- Der Code schätzt H4 erst ab 80 % Abdeckung und meldet die Abdeckung sonst offen im Bericht. Ein Test wacht darüber.
- **Grund:** Kodiert waren bisher vor allem aktuelle Amtsinhaber. Eine Schätzung darauf hätte eine Auswahl aus jüngeren, verlustbetroffenen Jahren genutzt.

**Gouverneursliste:** 52 Zeilen. Neu mit Belegen sind Weidmann (DE, 2011–2021) und Visco (IT, 2011–2023; 2017 für eine zweite Amtszeit bestätigt, also belegt wiederernennbar). 12 weitere Amtsträger aus dem Korpus sind als offen markiert. Zu Weidmanns Amtszeit liegt nur eine Sekundärquelle vor `[UNVERIFIED]`.

**H5-Datensatz (`data/hand/ncb_actions.csv`, 8 Handlungen aus 7 NZBs):**
- Alle drei puffersstärkenden Handlungen nach dem ersten Nettoverlust stammen von behandelten NZBs (BE zweimal, DE einmal), keine davor.
- NZBs ohne Nettoverlust nutzten Puffer, statt sie aufzubauen (ES, FI, IE).
- **Das ist mit dem Mechanismus vereinbar, aber mit 8 Ereignissen rein deskriptiv.** Die Zuordnung ist mechanisch: Wer keinen Nettoverlust hat, kann keine Handlung "danach" haben. Im Paper wird das als Illustration geführt, nicht als Test.

---

## Nachtrag v1.13 (11.09.2026): Konzentration der Identifikation und Prefilter-Prüfung

**Wichtigster Befund: Die Identifikation hängt an wenigen NZBs.**
Griechenland trägt 66 % der identifizierenden Variation, Italien 41 %, Spanien 15 %; alle übrigen höchstens 7 %. Griechenland steuert dabei nur rund 51 Passagen bei. **PAP v2.4** ergänzt deshalb R12 (Leave-one-NCB-out, Pflichtausweis) und eine Interpretationsregel: Kippt das Vorzeichen oder halbiert sich der Effekt beim Weglassen einer NZB, wird das Ergebnis als von einzelnen NZBs getragen berichtet. Das steht jetzt auch im Hauptteil des Papers.

**Prefilter geprüft (ergebnisblind, nur Zählungen).**
Eine moderate Erweiterung (Richtungsverben, Neutralzins-Vokabular, Instrumente) hebt die Trefferzahl im Fenster 2022–2026 von 1.218 auf 1.634 und den Schnitt je NZB-Halbjahr von 7,5 auf 10,1. Sehr breite Begriffe („monetary policy", Inflationsziel) würden 5.983 Passagen zusätzlich einschließen und die Präzision zerstören.
**Aber:** Bei den kleinen NZBs ändert sich fast nichts (SK 2, SI 5, EE 6). Der Grund ist nicht der Filter, sondern das Angebot: Estland und die Slowakei haben im ganzen Fenster **je zwei** Reden im BIS-Korpus, Kroatien, Belgien, Malta, Zypern und Slowenien 10 bis 13. **Eine Filtererweiterung löst das Abdeckungsproblem also nicht.** Sie wird erst nach der Recall-Schätzung aus der Validierung entschieden, wie in PAP v2 §8 festgelegt.
