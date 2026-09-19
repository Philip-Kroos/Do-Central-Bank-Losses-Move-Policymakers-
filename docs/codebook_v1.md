# Codebuch v1 — Positionen zu Bilanz- und GuV-relevanten Instrumenten
Stand 10.09.2026 · wird mit der OSF-Registrierung eingefroren · Änderungen danach nur mit datiertem Eintrag in Anhang F

## 1. Analyseeinheit
- **Passage:** fünf aufeinanderfolgende Sätze (`code/corpus/segment.py`), in Originalsprache.
- **Kontext für Klassifikator und Kodierer:** Datum, Rolle (Gouverneur/Direktorium) und die vorangehende Passage.
- **Maskierung:** Sprechername, Institution und Land werden durch Platzhalter ersetzt (`[SPEAKER]`, `[INSTITUTION]`, `[COUNTRY]`). So sollen Vorannahmen wie „Bundesbank = Falke" die Kodierung nicht färben. Grenze: Der Inhalt kann das Land trotzdem verraten; das wird berichtet.
- **Nur eigene Positionen zählen.** Referiert der Sprecher fremde Positionen (Kritiker, Marktteilnehmer), wird mit 0 kodiert.

## 2. Themen (Mehrfachlabels möglich)

| Label | Umfasst | Umfasst nicht |
|---|---|---|
| **Y1 Reserven** | Verzinsung von Überschuss- oder Mindestreserven; Höhe der Mindestreservequote; Tiering; Gebühren auf Reserven; Verzinsungsbasis (Einlagensatz vs. andere) | Bankenabgaben oder Übergewinnsteuern des Staates, sofern nicht die Reservenverzinsung selbst Thema ist |
| **Y2 GuV der Zentralbank** | Verluste, Rückstellungen, Eigenkapital, Verlustvortrag, Ausschüttung an den Staat, Rekapitalisierung | Gewinne oder Verluste von Geschäftsbanken |
| **Y3 Bilanz** | QT-Tempo, Wiederanlagen, aktive Verkäufe, Größe und Zusammensetzung der Bilanz, strukturelles Portfolio | Einzelne TLTRO-Konditionen (→ Y1 nur, wenn es um deren Verzinsung geht) |
| **Y4 Zinsstance** | Richtung und Tempo der Leitzinsen, Inflationsrisiken als Begründung | Beschreibende Wiedergabe beschlossener Zinsen ohne Wertung |

## 3. Positionen (−1 / 0 / +1; NA, wenn das Thema fehlt)

**Y1:**
- **+1** = für niedrigere Verzinsung von Reserven oder einen größeren unverzinsten Anteil. Das umfasst höhere unverzinste Mindestreserven, Tiering, Gebühren und die Verteidigung einer bereits beschlossenen Kürzung.
- **−1** = für Beibehaltung oder Erhöhung der Verzinsung, Warnung vor unverzinsten Reserven.
- **0** = rein deskriptiv.

**Y2:**
- **+1** = Verluste als Sorge, Beschränkung oder Problem für Unabhängigkeit bzw. Glaubwürdigkeit.
- **−1** = „Verluste sind für die Politik irrelevant, temporär, kein Problem".
- **0** = deskriptiv.

**Y3:**
- **+1** = schnellerer Bilanzabbau oder aktive Verkäufe.
- **−1** = langsamer, Stopp, Wiederanlagen.
- **0** = deskriptiv.

**Y4:**
- **+1** = hawkish (höhere Sätze, Aufwärtsrisiken betont).
- **−1** = dovish.
- **0** = neutral oder datenabhängig ohne Richtung.

### Entscheidungsregeln für Grenzfälle
1. **Mindestreservequote erhöhen.** Bleibt die Verzinsung bei 0 %, ist das ein größerer unverzinster Anteil: Y1 = +1. Werden zusätzliche Mindestreserven zum Einlagensatz verzinst, gilt Y1 = 0, und die Liquiditätswirkung wird unter Y3 bzw. Y4 kodiert.
2. **Ablehnung von Übergewinnsteuern.** Wendet sich der Sprecher gegen staatliche Bankenabgaben, ist das nicht Y1. Ausnahme: Er bezieht sich ausdrücklich auf Reservenverzinsung als Alternative.
3. **„Wir entscheiden unabhängig von unserer GuV".** Y2 = −1. Kodiert wird der Wortlaut, nicht der vermutete Subtext.
4. **Verteidigung eines Beschlusses mit gemischten Elementen.** Jedes Instrument wird separat kodiert.
5. **Konditionale Aussagen** („falls Reserven knapp werden, …"): 0, außer die Präferenz ist eindeutig.

## 4. Begründung (Y5, nur wenn Y1 ≠ 0; Mehrfachlabels möglich)

| Code | Bedeutung |
|---|---|
| EFF | Implementierung, Effizienz, Kontrolle der Geldmarktsätze, Transmission |
| PNL | Finanzen der Zentralbank, Verluste, Kosten für Staat bzw. Steuerzahler über die Zentralbank |
| FAIR | Bankengewinne als unverdient oder unfair, Fairness gegenüber Sparern oder Steuerzahlern |
| OTHER | sonstige Begründung |
| NONE | keine Begründung gegeben |

**Abgrenzung PNL vs. FAIR:** Gerahmt als *Kosten der Zentralbank* → PNL. Gerahmt als *Gewinn der Banken* → FAIR. Beides → beide Codes.

**Warum Y5 zählt:** F6 im Pre-Analysis-Plan testet, ob der Effekt über PNL läuft und nicht über allgemeine Stimmung gegen Banken.

## 5. Kalibrierungsbeispiele
**Diese Beispiele sind konstruiert. Sie sind keine Zitate realer Personen.**

| Konstruierte Passage (gekürzt) | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---|---|---|---|---|
| „Paying the full deposit rate on all reserves is not a law of nature. A larger share of unremunerated requirements would reduce the burden on public finances." | +1 | NA | NA | NA | PNL |
| „Die Verluste der Notenbank sind vorübergehend und beeinflussen unsere geldpolitischen Entscheidungen nicht." | NA | −1 | NA | NA | — |
| „Nous devons poursuivre la réduction du bilan à un rythme prévisible, sans ventes actives." | NA | NA | −1 | NA | — |
| „Unremunerated reserves would act as a tax on banks and could impair transmission." | −1 | NA | NA | NA | EFF |
| „Banks earned billions on reserves they did nothing for; this is hard to explain to savers." | +1 | NA | NA | NA | FAIR |

## 6. Klassifikator
- **Primär:** Open-Weight-Instruktionsmodell mit gepinnter Version und Hash. Greedy Decoding, Temperatur 0.
- **Robustheit:** ein API-Modell.
- **Blindheit:** Die Klassifikation des Gesamtkorpus läuft **vor** dem Merge mit Expositions- und Treatment-Daten.

**Prompt (System):**
> You are coding passages from speeches by euro area central bankers according to a fixed codebook. Code only the speaker's own positions. Names, institutions and countries are masked. Apply the decision rules exactly. Return JSON only.

**Prompt (User):**
> `CODEBOOK:` {Abschnitte 2–4 wörtlich}
> `CONTEXT:` date={date}; role={role}; previous_passage={prev}
> `PASSAGE:` {text}
> Return: `{"Y1":{"topic":bool,"position":-1|0|1|null},"Y2":{...},"Y3":{...},"Y4":{...},"Y5":["EFF"|"PNL"|"FAIR"|"OTHER"|"NONE"],"evidence_span":"<≤25 words from passage>"}`

**Validierung jeder Antwort:**
- Das JSON-Schema wird geprüft.
- `evidence_span` muss wörtlich in der Passage vorkommen; sonst gilt die Antwort als ungültig und wird einmal wiederholt.
- Der Anteil ungültiger Antworten wird berichtet.

## 7. Human-Validierung (dein Entscheidungspunkt)

**Stichprobe:** 500 Passagen, vorab stratifiziert.

| Schicht | Anzahl |
|---|---|
| Prefilter-Treffer Y1 | 200 |
| Prefilter-Treffer Y2 | 100 |
| Prefilter-Treffer Y3 | 100 |
| Zufällige Nicht-Treffer (zur Schätzung des Prefilter-Recalls) | 100 |

Nicht-englische Passagen werden in allen Schichten überproportional gezogen.

**Ablauf:**
1. **Kodierer:** Du kodierst alle 500 Passagen. Ein **zweiter unabhängiger Kodierer** kodiert 100 davon, zufällig gezogen. Wer das sein kann, ist offen.
2. **Reliabilitätsschwelle (vorab):** Krippendorffs α ≥ 0,667 für die Y1-Position zwischen den beiden Menschen. Liegt α darunter, wird das Codebuch überarbeitet und eine neue Stichprobe gezogen, bevor der volle Lauf startet.
3. **Modell vs. Mensch:** Berichtet werden Genauigkeit, Macro-F1 und α je Label, außerdem die Konfusionsmatrix für Y1.
4. **Recall des Prefilters:** Anteil der menschlich als Y1 kodierten Passagen unter den zufälligen Nicht-Treffern. Liegt er über 5 %, wird die Wortliste erweitert und das Korpus neu gefiltert.

**Aufwand:** 500 Passagen zu je etwa 1,5 Minuten ergeben rund 12–13 Stunden.
