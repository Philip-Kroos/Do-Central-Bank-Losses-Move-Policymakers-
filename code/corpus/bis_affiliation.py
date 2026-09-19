"""Speaker affiliation and role from BIS speech descriptions (euro area central banks).

The BIS extract has no institution column. Descriptions follow a stable pattern:
  "<Type> by <Title> <Name>, <Role> of (the) <Institution>[ and <other role>], at <venue>, <place>, <date>."
We isolate the affiliation segment (text between the speaker name and the venue) and match
institution aliases only inside it, so host institutions mentioned in the venue part are ignored.
"""
from __future__ import annotations
import re

INSTITUTIONS = {
    "ECB": [r"European Central Bank"],
    "DE": [r"Deutsche Bundesbank", r"Bundesbank"],
    "FR": [r"Bank of France", r"Banque de France"],
    "IT": [r"Bank of Italy", r"Banca d.Italia"],
    "ES": [r"Bank of Spain", r"Banco de Espa\w+"],
    "NL": [r"Netherlands Bank", r"De Nederlandsche Bank", r"Nederlandsche Bank"],
    "BE": [r"National Bank of Belgium", r"Nationale Bank van Belgi\w+", r"Banque [Nn]ationale de Belgique"],
    "IE": [r"Central Bank of Ireland"],
    "GR": [r"Bank of Greece"],
    "PT": [r"Bank of Portugal", r"Banco de Portugal"],
    "AT": [r"Austrian National Bank", r"Oesterreichische Nationalbank", r"Central Bank of the Republic of Austria"],
    "FI": [r"Bank of Finland", r"Suomen Pankki"],
    "LU": [r"Central Bank of Luxembourg", r"Banque centrale du Luxembourg"],
    "SI": [r"Bank of Slovenia", r"Banka Slovenije"],
    "SK": [r"National Bank of Slovakia", r"N.rodn. banka Slovenska"],
    "EE": [r"Bank of Estonia", r"Eesti Pank"],
    "LV": [r"Bank of Latvia", r"Latvijas Banka"],
    "LT": [r"Bank of Lithuania", r"Lietuvos bankas"],
    "CY": [r"Central Bank of Cyprus"],
    "MT": [r"Central Bank of Malta"],
    "HR": [r"Croatian National Bank", r"Hrvatska narodna banka"],
    "BG": [r"Bulgarian National Bank"],
}
_INST_RE = [(code, re.compile(p, re.I)) for code, pats in INSTITUTIONS.items() for p in pats]
_VENUE_SPLIT = re.compile(r",\s+at\s|\s+at\s+the\s|,\s+in\s|\s+before\s+the\s|\s+to\s+the\s|,\s+on\s+the\s+occasion|,\s+during\s", re.I)
_BY = re.compile(r"\bby\s+(?:(?:Mr|Ms|Mrs|Dr|Prof|Professor|Governor|Sir|Lord)\.?\s+)*", re.I)
_NON_HEAD = re.compile(r"deputy|vice|member of|executive director|director|chief|adviser|advisor|head of|secretary|board member", re.I)
_HEAD = re.compile(r"governor|president|chairman|chair\b|chairwoman", re.I)


def affiliation_segment(description: str) -> str:
    if not isinstance(description, str):
        return ""
    m = _BY.search(description)
    rest = description[m.end():] if m else description
    rest = rest.split(",", 1)[1] if "," in rest else rest       # drop the speaker name
    return _VENUE_SPLIT.split(rest, maxsplit=1)[0]


def parse(description: str) -> dict:
    """Return institution code, role class and the raw role phrase of the FIRST affiliation."""
    seg = affiliation_segment(description)
    hits = sorted(((m.start(), code, m) for code, rx in _INST_RE for m in [rx.search(seg)] if m), key=lambda x: x[0])
    if not hits:
        return dict(inst=None, role_class=None, role_phrase=None)
    start, code, _ = hits[0]
    role_phrase = seg[:start].strip(" ,")
    last_role = re.split(r"\band\b|;", role_phrase)[-1]              # role attached to this institution
    if code == "ECB":
        role_class = "ecb_president" if re.search(r"^\s*president", last_role, re.I) else "ecb_board"
    elif _NON_HEAD.search(last_role):
        role_class = "ncb_other"
    elif _HEAD.search(last_role):
        role_class = "ncb_head"
    else:
        role_class = "ncb_other"
    return dict(inst=code, role_class=role_class, role_phrase=role_phrase[:120])
