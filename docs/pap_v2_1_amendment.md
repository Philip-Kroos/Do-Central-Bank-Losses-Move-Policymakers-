# Pre-Analysis-Plan – Änderung v2.1 (Power-Ergebnis, ergebnisblind)
**Datum:** 11.09.2026, ca. 10:30 UTC · **Grundlage:** PAP v2 §9 (Power-Neuberechnung mit tatsächlichen Zählungen) · **Status:** eingefroren (SHA-256 in `docs/pap_v2_1_amendment.sha256`); **Veto durch Philip möglich bis zum Start der Klassifikation**

## 0. Offenlegung
Grundlage sind nur Passage-**Zählungen** je NZB-Halbjahr, die beobachteten Kohorten und das Carry-Maß (Treatment-Seite). Keine Stance-Position wurde gelesen, kodiert oder geschätzt.

## 1. Power-Ergebnis (`power/power_pap_v2_summary.csv`)
**Annahmen:** Passage-Rauschen sd 0,7 auf der Skala −1 bis +1; Zellschock sd 0,2 (Sensitivität 0,1); Anteil echter Stance-Passagen am Prefilter f ∈ {0,6; 1,0}; 13 NZBs mit belegtem Status.

| Design | Effekt | Power (f = 0,6) | Power (f = 1,0) |
|---|---|---|---|
| H1 binär, bis 2026H1 | −0,20 | 0,24 | 0,25 |
| H1 binär, bis 2026H1 | −0,30 | 0,38 | 0,55 |
| H1 binär, Zellschock 0,1 | −0,30 | 0,65 | — |
| H1 binär, verlängert bis 2027H2 (Zählungen angenommen) | −0,30 | 0,60 | — |
| **H3 Dosis** (Carry, standardisiert, 18 NZBs), studentisierte RI | **−0,20 pro SD** | **0,83** | — |
| H3 Dosis | −0,10 pro SD | 0,36 | — |
| Size-Checks bei β = 0 | — | binär 0,058 (plain RI); Dosis 0,058 (studentisiert); Dosis nicht studentisiert **0,17** | |

**Befund:** Das binäre Ereignisdesign ist mit den vorhandenen Daten unterpowert, der MDE bei 80 % liegt über 0,4 Skalenpunkten. Gründe: nur 6 behandelte NZBs, DE und FR mit nur 2 Nach-Halbjahren, und die Daten konzentrieren sich auf wenige NZBs. Das Dosisdesign erreicht 80 % Power bei etwa 0,2 Skalenpunkten pro SD. Ein **nicht** studentisiertes RI im Dosisdesign ist deutlich zu großzügig, der Grund ist die Präzisionsheterogenität der Einheiten.

## 2. Änderungen
1. **H3 (Dosis) wird primär; H1 (binär) sekundär; H2 (Knick) explorativ.**
2. **Hauptspezifikation H3:**
   - y = α_Gouverneur + γ_Halbjahr + β·E + δ'X, gewichtet mit der Anzahl Passagen.
   - E = demeantes, standardisiertes nicht gepooltes Carry pro Schlüsselpunkt, Konfiguration `net_flow_pepp0.889_mm1`. Die übrigen 11 Konfigurationen sind Robustheit.
   - Stichprobe: alle NZBs mit Carry-Maß (18); Fenster 2016H1–2026H1.
3. **Inferenz H3:** Randomisierungsinferenz durch Permutation ganzer Expositionspfade über NZBs, 999 Ziehungen, Statistik = β / Cluster-SE (CR0 nach NZB). Sekundär: Wild-Cluster-Bootstrap.
4. **Robustheit wie v2 §6**, ergänzt um R9: Kern×Halbjahr-FE im Dosisdesign. Das ist wegen der Korrelation von Portfoliorendite und Peripherie der wichtigste Test.
5. **H1** bleibt mit Spezifikation v2 §5 als sekundäre Evidenz. Die Ergebnisse werden **mit** der Power-Einschränkung berichtet; ein Nullergebnis ist nicht als Evidenz gegen H1 zu lesen.
6. **Datenfenster:** Die Hauptanalyse endet 2026H1. Eine vorab festgelegte Aktualisierung mit Daten bis 2027H2 wird separat berichtet (H6), ohne Neuspezifikation.

## 3. Was H3 widerlegt
β ≥ 0, oder β verschwindet unter R9, oder signifikante Leads in der Event-Study-Version (Dosis × Relativzeit ab 2022H1).
