# Daten-Download für das Expositionsmaß (du lädst herunter, ich rechne)

Die Sandbox erreicht ecb.europa.eu nicht. Alles Folgende ist öffentlich. Speichere die Dateien bitte unverändert und lade sie hoch; das Umformen in die Long-Format-Schemata übernehme ich.

| # | Inhalt | Quelle | Status |
|---|---|---|---|
| 1 | PSPP-Bestände je Jurisdiktion und gewichtete Restlaufzeit (WAM), monatlich | EZB, Datei `PSPP_weighted_average_maturity.xlsx` auf der APP-Seite (ecb.europa.eu → Monetary policy → Asset purchase programmes) | Datei belegt (Suchtreffer); Spaltenlayout `[UNVERIFIED]` |
| 2 | PEPP: jurisdiktionale Zusammensetzung der kumulierten Nettokäufe und WAM, monatlich inkl. Historie | EZB, PEPP-Seite (Downloads) | Veröffentlichung laut EZB-FAQ belegt |
| 3 | Länderrenditen nach Laufzeit (mind. 2J, 5J, 10J), monatlich 2015–2026, für die 20 Länder | ECB Data Portal: langfristige Zinssätze (10J, Konvergenzkriterium) für alle Länder; weitere Laufzeiten, wo vorhanden | Serienschlüssel `[UNVERIFIED]`; ohne weitere Laufzeiten nutzt der Code die 10J-Rendite mit der Steigung der Euroraum-Kurve (Flag im Output) |
| 4 | Euroraum-Zinsstrukturkurve (Spot-Renditen nach Laufzeit), monatlich | EZB, „Euro area yield curves" | Seite existiert (Navigation der EZB-Website) |
| 5 | Kapitalschlüssel mit Gültigkeitszeiträumen | EZB, „Capital subscription" | Seite existiert |
| 6 | Hauptrefinanzierungssatz und Einlagensatz | EZB, „Key ECB interest rates" | Seite existiert |
| optional | ISIN-Listen verleihbarer PSPP-Bestände je NZB (z. B. Banque de France) | NZB-Websites | Liefert Wertpapiere, aber keine Beträge; nur zur Validierung der WAM-Annahme |

**Vorab festgelegte Validierung:** Die Rangfolge des Carry-Maßes pro Schlüsselprozentpunkt wird mit dem Nettozinsergebnis nach Reallokation aus Banque de France Bulletin 260/6 (DE, FR, IT, ES; 2023/24) verglichen. Bekanntes Risiko: Frankreich verliert dort pro Schlüsselanteil *mehr* als Deutschland, obwohl französische Renditen höher lagen. Das Maß kann diese Umkehr möglicherweise nicht reproduzieren, weil andere nicht gepoolte Posten mitspielen. **Stimmen die Rangfolgen nicht überein, bleibt Treatment A (berichtete Ergebnisse) die Hauptspezifikation und das Carry-Maß nur Dosis-Evidenz.**
