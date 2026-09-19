"""Masking for blind coding: speaker names, institutions, countries, demonyms, capitals."""
from __future__ import annotations
import re
from code.corpus.bis_affiliation import INSTITUTIONS

COUNTRIES = ["Austria", "Belgium", "Cyprus", "Germany", "Estonia", "Spain", "Finland", "France", "Greece", "Ireland",
             "Italy", "Lithuania", "Luxembourg", "Latvia", "Malta", "Netherlands", "Portugal", "Slovenia", "Slovakia",
             "Croatia", "Bulgaria", "Hellenic Republic"]
DEMONYMS = ["Austrian", "Belgian", "Cypriot", "German", "Germans", "Estonian", "Spanish", "Spaniards", "Finnish", "Finns",
            "French", "Greek", "Greeks", "Irish", "Italian", "Italians", "Lithuanian", "Luxembourgish", "Latvian", "Maltese",
            "Dutch", "Portuguese", "Slovenian", "Slovene", "Slovak", "Slovakian", "Croatian", "Bulgarian"]
CAPITALS = ["Vienna", "Nicosia", "Berlin", "Tallinn", "Madrid", "Helsinki", "Paris", "Athens", "Dublin", "Rome", "Vilnius",
            "Riga", "Valletta", "Amsterdam", "Lisbon", "Ljubljana", "Bratislava", "Zagreb", "Sofia", "Milan", "Barcelona"]
EXTRA_INST = [r"Bundesbank", r"DNB", r"OeNB", r"NBB", r"BCL", r"Banca d.Italia", r"Banco de Espa\w+", r"Banque de France",
              r"Suomen Pankki", r"Bank of Italy", r"Bank of Spain", r"Bank of France", r"Bank of Greece"]


def build_masker(names: list[str]):
    inst = sorted({p for pats in INSTITUTIONS.values() for p in pats if "European Central Bank" not in p} | set(EXTRA_INST), key=len, reverse=True)
    name_tokens = set()
    for n in names:
        for part in str(n).split(";"):
            part = part.strip()
            if len(part) > 3:
                name_tokens.add(re.escape(part))
                last = part.split()[-1]
                if len(last) > 3:
                    name_tokens.add(re.escape(last))
    pats = [
        (re.compile(r"\b(?:" + "|".join(sorted(name_tokens, key=len, reverse=True)) + r")\b"), "[SPEAKER]") if name_tokens else None,
        (re.compile(r"(?:" + "|".join(inst) + r")", re.I), "[INSTITUTION]"),
        (re.compile(r"\b(?:" + "|".join(COUNTRIES) + r")\b"), "[COUNTRY]"),
        (re.compile(r"\b(?:" + "|".join(DEMONYMS) + r")\b"), "[NATIONAL]"),
        (re.compile(r"\b(?:" + "|".join(CAPITALS) + r")\b"), "[CITY]"),
    ]
    pats.insert(0, (re.compile(r"\b(?:Member of the Executive Board|Vice[- ]President|President|Chief Economist|Deputy Governor|Governor|Chairman of the Board|Chair of the Board)\s+of\s+(?:the\s+)?(?:ECB|European Central Bank)\b", re.I), "[ROLE]"))
    pats.append((re.compile(r"\b(?:Deputy Governor|Governor|Deputy President|Vice[- ]President|President|Chairman of the Board|Chair of the Board|Member of the (?:Executive )?Board)\s+of\s+(?:the\s+)?\[INSTITUTION\]", re.I), "[ROLE]"))
    pats = [p for p in pats if p]

    def mask(text: str) -> str:
        for rx, rep in pats:
            text = rx.sub(rep, text)
        return text
    return mask
